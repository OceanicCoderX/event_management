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
    category_id = form.getvalue('category_id', '')
    status = form.getvalue('status', '')
    search = form.getvalue('search', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """SELECT e.*, c.name as category_name, c.icon as category_icon,
               (SELECT COUNT(*) FROM participants p WHERE p.event_id=e.event_id AND p.status='Approved') as participant_count
               FROM events e LEFT JOIN categories c ON e.category_id=c.category_id WHERE 1=1"""
    params = []

    if category_id:
        query += " AND e.category_id=%s"
        params.append(category_id)
    if status:
        query += " AND e.status=%s"
        params.append(status)
    if search:
        query += " AND (e.title LIKE %s OR e.description LIKE %s)"
        params.extend([f'%{search}%', f'%{search}%'])

    query += " ORDER BY e.event_date ASC"
    cursor.execute(query, params)
    events = cursor.fetchall()

    # Convert dates to strings and decimals to floats
    for ev in events:
        if ev.get('event_date'):
            ev['event_date'] = str(ev['event_date'])
        if ev.get('registration_deadline'):
            ev['registration_deadline'] = str(ev['registration_deadline'])
        if ev.get('created_at'):
            ev['created_at'] = str(ev['created_at'])
        # Convert Decimal to float
        for key, value in ev.items():
            if isinstance(value, decimal.Decimal):
                ev[key] = float(value)

    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "data": events}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
