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
    judge_user_id = form.getvalue('judge_user_id', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if action == 'get':
        # Get all events with their assigned judges
        cursor.execute("""SELECT e.event_id, e.title, 
                          GROUP_CONCAT(u.full_name SEPARATOR ', ') as judge_names,
                          COUNT(ja.judge_user_id) as judge_count
                          FROM events e LEFT JOIN judge_assignments ja ON e.event_id=ja.event_id
                          LEFT JOIN users u ON ja.judge_user_id=u.user_id
                          GROUP BY e.event_id ORDER BY e.event_date""")
        events = cursor.fetchall()

        cursor.execute("SELECT user_id, full_name, email FROM users WHERE role='judge' ORDER BY full_name")
        judges = cursor.fetchall()

        print(json.dumps({"status": "success", "events": events, "judges": judges}))

    elif action == 'get_event_judges':
        cursor.execute("""SELECT ja.assignment_id, u.user_id, u.full_name, u.email
                          FROM judge_assignments ja JOIN users u ON ja.judge_user_id=u.user_id
                          WHERE ja.event_id=%s""", (event_id,))
        assigned = cursor.fetchall()
        print(json.dumps({"status": "success", "data": assigned}))

    elif action == 'assign':
        cursor.execute("INSERT INTO judge_assignments (judge_user_id, event_id) VALUES (%s,%s)",
                       (judge_user_id, event_id))
        conn.commit()
        print(json.dumps({"status": "success", "message": "Judge assigned"}))

    elif action == 'remove':
        cursor.execute("DELETE FROM judge_assignments WHERE judge_user_id=%s AND event_id=%s",
                       (judge_user_id, event_id))
        conn.commit()
        print(json.dumps({"status": "success", "message": "Judge removed"}))

    cursor.close()
    conn.close()

except Exception as e:
    if 'Duplicate entry' in str(e):
        print(json.dumps({"status": "error", "message": "Judge already assigned to this event"}))
    else:
        print(json.dumps({"status": "error", "message": str(e)}))
