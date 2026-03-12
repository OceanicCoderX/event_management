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
    status_filter = form.getvalue('status', 'Approved')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """SELECT p.*, u.full_name, u.photo, u.bio, u.email,
               (SELECT COUNT(*) FROM votes v WHERE v.participant_id=p.participant_id) as vote_count
               FROM participants p JOIN users u ON p.user_id=u.user_id
               WHERE p.event_id=%s"""
    params = [event_id]

    if status_filter and status_filter != 'All':
        query += " AND p.status=%s"
        params.append(status_filter)

    query += " ORDER BY p.registered_at ASC"
    cursor.execute(query, params)
    participants = cursor.fetchall()
    for pt in participants:
        if pt.get('registered_at'):
            pt['registered_at'] = str(pt['registered_at'])

    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "data": participants}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
