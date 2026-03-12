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
    user_id = form.getvalue('user_id', '')
    event_id = form.getvalue('event_id', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get participant record
    cursor.execute("""SELECT p.participant_id, p.performance_title, p.status,
                      e.title as event_title, e.judge_weight, e.vote_weight, e.results_announced
                      FROM participants p JOIN events e ON p.event_id=e.event_id
                      WHERE p.user_id=%s AND p.event_id=%s AND p.status='Approved'""", (user_id, event_id))
    participant = cursor.fetchone()

    if not participant:
        print(json.dumps({"status": "error", "message": "No approved application found"}))
        cursor.close()
        conn.close()
        sys.exit()

    # Convert Decimal to float
    for key, value in participant.items():
        if isinstance(value, decimal.Decimal):
            participant[key] = float(value)

    pid = participant['participant_id']

    # Get scores by criteria
    cursor.execute("""SELECT c.criteria_name, c.max_marks, c.description,
                      AVG(s.marks) as avg_marks, COUNT(DISTINCT s.judge_user_id) as judge_count
                      FROM criteria c LEFT JOIN scores s ON c.criteria_id=s.criteria_id AND s.participant_id=%s
                      WHERE c.event_id=%s GROUP BY c.criteria_id""", (pid, event_id))
    scores = cursor.fetchall()

    # Total judge score normalized
    cursor.execute("""SELECT SUM(s.marks) as total, 
                      (SELECT SUM(c2.max_marks) FROM criteria c2 WHERE c2.event_id=%s) as max_possible
                      FROM scores s JOIN criteria c ON s.criteria_id=c.criteria_id
                      WHERE s.participant_id=%s AND c.event_id=%s""", (event_id, pid, event_id))
    total_row = cursor.fetchone()
    judge_score_norm = 0
    if total_row and total_row['total'] and total_row['max_possible']:
        judge_score_norm = round(float(total_row['total']) / float(total_row['max_possible']) * 100, 2)

    # Vote count
    cursor.execute("SELECT COUNT(*) as cnt FROM votes WHERE participant_id=%s", (pid,))
    vote_row = cursor.fetchone()
    vote_count = vote_row['cnt'] if vote_row else 0

    # Get rank from results if announced
    rank = None
    final_score = None
    if participant['results_announced']:
        cursor.execute("SELECT rank, final_score FROM results WHERE participant_id=%s AND event_id=%s", (pid, event_id))
        result_row = cursor.fetchone()
        if result_row:
            rank = result_row['rank']
            final_score = float(result_row['final_score'])

    cursor.close()
    conn.close()

    print(json.dumps({
        "status": "success",
        "participant": participant,
        "scores": [{"criteria_name": s['criteria_name'], "max_marks": s['max_marks'],
                    "avg_marks": float(s['avg_marks']) if s['avg_marks'] else None,
                    "judge_count": s['judge_count']} for s in scores],
        "judge_score_normalized": judge_score_norm,
        "vote_count": vote_count,
        "rank": rank,
        "final_score": final_score
    }))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
