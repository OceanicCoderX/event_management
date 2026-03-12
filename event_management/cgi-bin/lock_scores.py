#!C:/Python314/python.exe
import cgi
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db_config import get_connection

print("Content-Type: application/json")
print()

try:
    form = cgi.FieldStorage()
    event_id = form.getvalue('event_id', '')
    action = form.getvalue('action', '')

    if not event_id or action not in ('lock', 'unlock'):
        print(json.dumps({"status": "error", "message": "event_id and action (lock/unlock) required"}))
        sys.exit()

    new_val = 1 if action == 'lock' else 0

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET scores_locked=%s WHERE event_id=%s", (new_val, event_id))
    conn.commit()
    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "scores_locked": new_val}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
