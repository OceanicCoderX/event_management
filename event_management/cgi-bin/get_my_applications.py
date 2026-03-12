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
    user_id = form.getvalue('user_id', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""SELECT p.*, e.title as event_title, e.event_date, e.status as event_status,
                      e.results_announced, c.name as category_name
                      FROM participants p 
                      JOIN events e ON p.event_id=e.event_id
                      LEFT JOIN categories c ON e.category_id=c.category_id
                      WHERE p.user_id=%s ORDER BY p.registered_at DESC""", (user_id,))
    apps = cursor.fetchall()
    for a in apps:
        if a.get('registered_at'):
            a['registered_at'] = str(a['registered_at'])
        if a.get('event_date'):
            a['event_date'] = str(a['event_date'])

    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "data": apps}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
