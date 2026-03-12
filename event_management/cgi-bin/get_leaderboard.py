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

    if not event_id:
        print(json.dumps({"status": "error", "message": "event_id required"}))
        sys.exit()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get event weights
    cursor.execute("SELECT judge_weight, vote_weight, status FROM events WHERE event_id=%s", (event_id,))
    event = cursor.fetchone()
    if not event:
        print(json.dumps({"status": "error", "message": "Event not found"}))
        cursor.close()
        conn.close()
        sys.exit()

    judge_weight = float(event['judge_weight'])
    vote_weight = float(event['vote_weight'])

    # Get participants with vote counts and judge scores
    cursor.execute("""SELECT p.participant_id, u.full_name, u.photo, p.performance_title,
                      (SELECT COUNT(*) FROM votes v WHERE v.participant_id=p.participant_id) as vote_count
                      FROM participants p JOIN users u ON p.user_id=u.user_id
                      WHERE p.event_id=%s AND p.status='Approved'""", (event_id,))
    participants = cursor.fetchall()

    # Get max votes to normalize
    max_votes = max((p['vote_count'] for p in participants), default=1)
    if max_votes == 0:
        max_votes = 1

    results = []
    for p in participants:
        # Get judge scores
        cursor.execute("""SELECT SUM(s.marks) as total_marks, 
                          (SELECT SUM(c.max_marks) FROM criteria c WHERE c.event_id=%s) as max_possible
                          FROM scores s JOIN criteria c ON s.criteria_id=c.criteria_id
                          WHERE s.participant_id=%s AND c.event_id=%s""",
                       (event_id, p['participant_id'], event_id))
        score_row = cursor.fetchone()

        judge_score_norm = 0
        if score_row and score_row['total_marks'] and score_row['max_possible']:
            judge_score_norm = round(float(score_row['total_marks']) / float(score_row['max_possible']) * 100, 2)

        vote_count = p['vote_count']
        vote_score_norm = round(vote_count / max_votes * 100, 2)
        final_score = round(judge_score_norm * (judge_weight / 100) + vote_score_norm * (vote_weight / 100), 2)

        results.append({
            "participant_id": p['participant_id'],
            "full_name": p['full_name'],
            "photo": p['photo'] or "",
            "performance_title": p['performance_title'],
            "vote_count": vote_count,
            "judge_score": judge_score_norm,
            "vote_score": vote_score_norm,
            "final_score": final_score
        })

    results.sort(key=lambda x: x['final_score'], reverse=True)
    for i, r in enumerate(results):
        r['rank'] = i + 1

    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "data": results, "event_status": event['status']}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
