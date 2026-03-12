#!C:/Python314/python.exe
import cgi
import json
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from db_config import get_connection

print("Content-Type: application/json")
print()

try:
    form = cgi.FieldStorage()
    event_id = form.getvalue('event_id', '')
    announce = form.getvalue('announce', '0')

    if not event_id:
        print(json.dumps({"status": "error", "message": "event_id required"}))
        sys.exit()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get event weights
    cursor.execute("SELECT judge_weight, vote_weight FROM events WHERE event_id=%s", (event_id,))
    event = cursor.fetchone()
    judge_weight = float(event['judge_weight'])
    vote_weight = float(event['vote_weight'])

    # Get approved participants
    cursor.execute("""SELECT p.participant_id, u.full_name, p.performance_title
                      FROM participants p JOIN users u ON p.user_id=u.user_id
                      WHERE p.event_id=%s AND p.status='Approved'""", (event_id,))
    participants = cursor.fetchall()

    if not participants:
        print(json.dumps({"status": "error", "message": "No approved participants found"}))
        cursor.close()
        conn.close()
        sys.exit()

    # Get max votes for normalization
    cursor.execute("""SELECT MAX(vc) as max_votes FROM 
                      (SELECT COUNT(*) as vc FROM votes WHERE event_id=%s GROUP BY participant_id) t""", (event_id,))
    max_v_row = cursor.fetchone()
    max_votes = max_v_row['max_votes'] if max_v_row and max_v_row['max_votes'] else 1

    # Get max possible judge score
    cursor.execute("SELECT SUM(max_marks) as max_score FROM criteria WHERE event_id=%s", (event_id,))
    max_score_row = cursor.fetchone()
    max_judge_score = float(max_score_row['max_score']) if max_score_row and max_score_row['max_score'] else 1

    results = []
    for p in participants:
        pid = p['participant_id']

        # Judge score
        cursor.execute("""SELECT SUM(marks) as total FROM scores WHERE participant_id=%s""", (pid,))
        score_row = cursor.fetchone()
        total_marks = float(score_row['total']) if score_row and score_row['total'] else 0
        judge_score_norm = round(total_marks / max_judge_score * 100, 2)

        # Vote score
        cursor.execute("SELECT COUNT(*) as cnt FROM votes WHERE participant_id=%s", (pid,))
        vote_row = cursor.fetchone()
        vote_count = vote_row['cnt'] if vote_row else 0
        vote_score_norm = round(vote_count / max_votes * 100, 2)

        # Final score
        final_score = round(judge_score_norm * (judge_weight / 100) + vote_score_norm * (vote_weight / 100), 2)

        results.append({
            "participant_id": pid,
            "full_name": p['full_name'],
            "performance_title": p['performance_title'],
            "judge_score": judge_score_norm,
            "vote_score": vote_score_norm,
            "final_score": final_score
        })

    # Sort by final score descending
    results.sort(key=lambda x: x['final_score'], reverse=True)

    # Insert/update results table
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for i, r in enumerate(results):
        r['rank'] = i + 1
        is_winner = 1 if i == 0 else 0
        cursor.execute("""INSERT INTO results (event_id, participant_id, judge_score, vote_score, final_score, rank, is_winner, calculated_at)
                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                          ON DUPLICATE KEY UPDATE judge_score=%s, vote_score=%s, final_score=%s, rank=%s, is_winner=%s, calculated_at=%s""",
                       (event_id, r['participant_id'], r['judge_score'], r['vote_score'], r['final_score'], r['rank'], is_winner, now,
                        r['judge_score'], r['vote_score'], r['final_score'], r['rank'], is_winner, now))

    if announce == '1':
        cursor.execute("UPDATE events SET results_announced=1 WHERE event_id=%s", (event_id,))

    conn.commit()
    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "results": results,
                      "announced": announce == '1',
                      "message": "Results calculated" + (" and announced!" if announce == '1' else " (preview)")}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
