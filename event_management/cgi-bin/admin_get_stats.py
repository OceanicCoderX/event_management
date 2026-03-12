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
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) as cnt FROM events")
    total_events = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM participants")
    total_participants = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role='judge'")
    active_judges = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM votes")
    total_votes = cursor.fetchone()['cnt']

    # Participants per event (last 5 events)
    cursor.execute("""SELECT e.title, COUNT(p.participant_id) as count
                      FROM events e LEFT JOIN participants p ON e.event_id=p.event_id
                      GROUP BY e.event_id ORDER BY e.event_id DESC LIMIT 5""")
    participants_per_event = cursor.fetchall()

    # Application status breakdown
    cursor.execute("""SELECT status, COUNT(*) as cnt FROM participants GROUP BY status""")
    status_rows = cursor.fetchall()
    application_status = {"Pending": 0, "Approved": 0, "Rejected": 0}
    for row in status_rows:
        application_status[row['status']] = row['cnt']

    # Recent applications
    cursor.execute("""SELECT u.full_name as name, e.title as event_name, p.status, p.registered_at as date
                      FROM participants p JOIN users u ON p.user_id=u.user_id
                      JOIN events e ON p.event_id=e.event_id
                      ORDER BY p.registered_at DESC LIMIT 5""")
    recent_apps = cursor.fetchall()
    for r in recent_apps:
        if r.get('date'):
            r['date'] = str(r['date'])

    cursor.close()
    conn.close()
    print(json.dumps({
        "status": "success",
        "total_events": total_events,
        "total_participants": total_participants,
        "active_judges": active_judges,
        "total_votes": total_votes,
        "participants_per_event": participants_per_event,
        "application_status": application_status,
        "recent_applications": recent_apps
    }))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
