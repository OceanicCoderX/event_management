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
    event_id = form.getvalue('event_id', '')

    if not event_id:
        print(json.dumps({"status": "error", "message": "event_id required"}))
        sys.exit()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""SELECT e.*, c.name as category_name, c.icon as category_icon
                      FROM events e LEFT JOIN categories c ON e.category_id=c.category_id
                      WHERE e.event_id=%s""", (event_id,))
    event = cursor.fetchone()

    if not event:
        print(json.dumps({"status": "error", "message": "Event not found"}))
        sys.exit()

    if event.get('event_date'):
        event['event_date'] = str(event['event_date'])
    if event.get('registration_deadline'):
        event['registration_deadline'] = str(event['registration_deadline'])
    if event.get('created_at'):
        event['created_at'] = str(event['created_at'])

    # Convert Decimal to float
    for key, value in event.items():
        if isinstance(value, decimal.Decimal):
            event[key] = float(value)

    # Get approved participants with vote counts
    cursor.execute("""SELECT p.*, u.full_name, u.photo, u.bio,
                      (SELECT COUNT(*) FROM votes v WHERE v.participant_id=p.participant_id) as vote_count
                      FROM participants p JOIN users u ON p.user_id=u.user_id
                      WHERE p.event_id=%s AND p.status='Approved'
                      ORDER BY p.registered_at ASC""", (event_id,))
    participants = cursor.fetchall()
    for pt in participants:
        if pt.get('registered_at'):
            pt['registered_at'] = str(pt['registered_at'])

    # Get criteria
    cursor.execute("SELECT * FROM criteria WHERE event_id=%s", (event_id,))
    criteria = cursor.fetchall()
    for c in criteria:
        if isinstance(c.get('max_marks'), decimal.Decimal):
            c['max_marks'] = float(c['max_marks'])

    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "event": event, "participants": participants, "criteria": criteria}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
