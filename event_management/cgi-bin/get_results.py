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

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if event_id:
        cursor.execute("""SELECT e.event_id, e.title, e.results_announced, e.status
                          FROM events e WHERE e.event_id=%s AND e.results_announced=1""", (event_id,))
        event = cursor.fetchone()
        if not event:
            print(json.dumps({"status": "error", "message": "Results not announced for this event"}))
            cursor.close()
            conn.close()
            sys.exit()

        cursor.execute("""SELECT r.*, p.performance_title, u.full_name, u.photo, u.bio
                          FROM results r 
                          JOIN participants p ON r.participant_id=p.participant_id
                          JOIN users u ON p.user_id=u.user_id
                          WHERE r.event_id=%s ORDER BY r.rank ASC""", (event_id,))
        results = cursor.fetchall()
        for r in results:
            if r.get('calculated_at'):
                r['calculated_at'] = str(r['calculated_at'])
            # Convert Decimal to float
            for key, value in r.items():
                if isinstance(value, decimal.Decimal):
                    r[key] = float(value)

        cursor.close()
        conn.close()
        print(json.dumps({"status": "success", "event": event, "data": results}))
    else:
        # Return all events with announced results
        cursor.execute("SELECT event_id, title FROM events WHERE results_announced=1 ORDER BY event_date DESC")
        events = cursor.fetchall()
        cursor.close()
        conn.close()
        print(json.dumps({"status": "success", "data": events}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
