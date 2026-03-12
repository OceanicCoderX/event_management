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

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if not event_id:
        cursor.execute("SELECT event_id, title FROM events ORDER BY event_date DESC")
        events = cursor.fetchall()
        cursor.close()
        conn.close()
        print(json.dumps({"status": "success", "data": events}))
        sys.exit()

    # Stats
    cursor.execute("SELECT COUNT(*) as cnt FROM participants WHERE event_id=%s", (event_id,))
    total_registered = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM participants WHERE event_id=%s AND status='Approved'", (event_id,))
    approved = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM participants WHERE event_id=%s AND status='Rejected'", (event_id,))
    rejected = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM votes WHERE event_id=%s", (event_id,))
    total_votes = cursor.fetchone()['cnt']

    cursor.execute("""SELECT AVG(r.final_score) as avg_score FROM results r WHERE r.event_id=%s""", (event_id,))
    avg_row = cursor.fetchone()
    avg_score = round(float(avg_row['avg_score']), 2) if avg_row and avg_row['avg_score'] else 0

    # Registrations over time
    cursor.execute("""SELECT DATE(registered_at) as reg_date, COUNT(*) as cnt 
                      FROM participants WHERE event_id=%s 
                      GROUP BY DATE(registered_at) ORDER BY reg_date""", (event_id,))
    reg_over_time = cursor.fetchall()
    for r in reg_over_time:
        r['reg_date'] = str(r['reg_date'])

    # Votes per participant
    cursor.execute("""SELECT u.full_name, COUNT(v.vote_id) as vote_count
                      FROM participants p JOIN users u ON p.user_id=u.user_id
                      LEFT JOIN votes v ON v.participant_id=p.participant_id
                      WHERE p.event_id=%s AND p.status='Approved'
                      GROUP BY p.participant_id ORDER BY vote_count DESC""", (event_id,))
    votes_per_participant = cursor.fetchall()

    cursor.close()
    conn.close()
    print(json.dumps({
        "status": "success",
        "total_registered": total_registered,
        "approved": approved,
        "rejected": rejected,
        "total_votes": total_votes,
        "avg_score": avg_score,
        "reg_over_time": reg_over_time,
        "votes_per_participant": votes_per_participant
    }))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
