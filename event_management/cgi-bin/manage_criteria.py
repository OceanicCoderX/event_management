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
    action = form.getvalue('action', 'get')
    event_id = form.getvalue('event_id', '')
    criteria_id = form.getvalue('criteria_id', '')
    criteria_name = form.getvalue('criteria_name', '').strip()
    max_marks = form.getvalue('max_marks', '10')
    description = form.getvalue('description', '').strip()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if action == 'get':
        cursor.execute("SELECT * FROM criteria WHERE event_id=%s ORDER BY criteria_id", (event_id,))
        data = cursor.fetchall()
        print(json.dumps({"status": "success", "data": data}))

    elif action == 'add':
        # Check if scoring has begun
        cursor.execute("""SELECT COUNT(*) as cnt FROM scores s JOIN participants p ON s.participant_id=p.participant_id
                          JOIN criteria c ON s.criteria_id=c.criteria_id WHERE c.event_id=%s""", (event_id,))
        scored = cursor.fetchone()
        if scored and scored['cnt'] > 0:
            print(json.dumps({"status": "error", "message": "Cannot add criteria after scoring has begun"}))
        else:
            cursor.execute("INSERT INTO criteria (event_id, criteria_name, max_marks, description) VALUES (%s,%s,%s,%s)",
                           (event_id, criteria_name, max_marks, description))
            conn.commit()
            print(json.dumps({"status": "success", "message": "Criteria added", "criteria_id": cursor.lastrowid}))

    elif action == 'delete':
        cursor.execute("DELETE FROM criteria WHERE criteria_id=%s", (criteria_id,))
        conn.commit()
        print(json.dumps({"status": "success", "message": "Criteria deleted"}))

    cursor.close()
    conn.close()

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
