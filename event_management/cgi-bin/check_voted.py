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
    voter_user_id = form.getvalue('voter_user_id', '')
    event_id = form.getvalue('event_id', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT participant_id FROM votes WHERE voter_user_id=%s AND event_id=%s",
        (voter_user_id, event_id)
    )
    vote = cursor.fetchone()
    cursor.close()
    conn.close()

    if vote:
        print(json.dumps({"status": "success", "has_voted": True, "participant_id": vote['participant_id']}))
    else:
        print(json.dumps({"status": "success", "has_voted": False, "participant_id": None}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
