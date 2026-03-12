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
    participant_id = form.getvalue('participant_id', '')
    status = form.getvalue('status', '')
    event_id = form.getvalue('event_id', '')
    bulk = form.getvalue('bulk', '0')

    conn = get_connection()
    cursor = conn.cursor()

    if bulk == '1' and event_id:
        # Bulk approve all pending for an event
        cursor.execute("UPDATE participants SET status='Approved' WHERE event_id=%s AND status='Pending'", (event_id,))
        affected = cursor.rowcount
        conn.commit()
        print(json.dumps({"status": "success", "message": f"{affected} participants approved"}))
    elif participant_id and status in ('Approved', 'Rejected', 'Pending'):
        cursor.execute("UPDATE participants SET status=%s WHERE participant_id=%s", (status, participant_id))
        conn.commit()
        print(json.dumps({"status": "success", "message": f"Status updated to {status}"}))
    else:
        print(json.dumps({"status": "error", "message": "Invalid parameters"}))

    cursor.close()
    conn.close()

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
