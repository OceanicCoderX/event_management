#!C:/Python314/python.exe
import cgi
import json
import sys
import os
import decimal
sys.path.insert(0, os.path.dirname(__file__))
from db_config import get_connection

print("Content-Type: application/json")
print()

try:
    form = cgi.FieldStorage()
    judge_user_id = form.getvalue('judge_user_id', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""SELECT e.*, c.name as category_name, ja.assigned_at,
                      (SELECT COUNT(*) FROM participants p WHERE p.event_id=e.event_id AND p.status='Approved') as participant_count,
                      (SELECT COUNT(DISTINCT s.participant_id) FROM scores s 
                       JOIN participants p ON s.participant_id=p.participant_id 
                       WHERE p.event_id=e.event_id AND s.judge_user_id=%s) as scored_count
                      FROM judge_assignments ja 
                      JOIN events e ON ja.event_id=e.event_id
                      LEFT JOIN categories c ON e.category_id=c.category_id
                      WHERE ja.judge_user_id=%s ORDER BY e.event_date ASC""", (judge_user_id, judge_user_id))
    events = cursor.fetchall()
    for ev in events:
        if ev.get('event_date'):
            ev['event_date'] = str(ev['event_date'])
        if ev.get('registration_deadline'):
            ev['registration_deadline'] = str(ev['registration_deadline'])
        if ev.get('created_at'):
            ev['created_at'] = str(ev['created_at'])
        if ev.get('assigned_at'):
            ev['assigned_at'] = str(ev['assigned_at'])
        # Convert Decimal to float
        for key, value in ev.items():
            if isinstance(value, decimal.Decimal):
                ev[key] = float(value)

    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "data": events}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
