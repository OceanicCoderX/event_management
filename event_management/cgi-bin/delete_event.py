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

    if not event_id:
        print(json.dumps({"status": "error", "message": "event_id required"}))
        sys.exit()

    conn = get_connection()
    cursor = conn.cursor()

    # Delete in order due to foreign keys
    cursor.execute("DELETE FROM results WHERE event_id=%s", (event_id,))
    cursor.execute("DELETE FROM votes WHERE event_id=%s", (event_id,))
    # Get participant ids for this event
    cursor.execute("SELECT participant_id FROM participants WHERE event_id=%s", (event_id,))
    pids = [row[0] for row in cursor.fetchall()]
    for pid in pids:
        cursor.execute("DELETE FROM scores WHERE participant_id=%s", (pid,))
    cursor.execute("DELETE FROM participants WHERE event_id=%s", (event_id,))
    cursor.execute("DELETE FROM criteria WHERE event_id=%s", (event_id,))
    cursor.execute("DELETE FROM judge_assignments WHERE event_id=%s", (event_id,))
    cursor.execute("DELETE FROM events WHERE event_id=%s", (event_id,))
    conn.commit()
    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "message": "Event deleted successfully"}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
