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
    judge_user_id = form.getvalue('judge_user_id', '')
    event_id = form.getvalue('event_id', '')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Get event info (scores locked status)
    cursor.execute("SELECT scores_locked, title FROM events WHERE event_id=%s", (event_id,))
    event = cursor.fetchone()

    # Get approved participants
    cursor.execute("""SELECT p.participant_id, p.performance_title, p.category_entry,
                      u.full_name, u.photo, u.bio
                      FROM participants p JOIN users u ON p.user_id=u.user_id
                      WHERE p.event_id=%s AND p.status='Approved'""", (event_id,))
    participants = cursor.fetchall()

    # Get criteria
    cursor.execute("SELECT * FROM criteria WHERE event_id=%s", (event_id,))
    criteria = cursor.fetchall()
    for c in criteria:
        if isinstance(c.get('max_marks'), decimal.Decimal):
            c['max_marks'] = float(c['max_marks'])

    # Get existing scores by this judge
    cursor.execute("""SELECT s.participant_id, s.criteria_id, s.marks
                      FROM scores s JOIN participants p ON s.participant_id=p.participant_id
                      WHERE p.event_id=%s AND s.judge_user_id=%s""", (event_id, judge_user_id))
    existing_scores = cursor.fetchall()
    scores_map = {}
    for s in existing_scores:
        key = f"{s['participant_id']}_{s['criteria_id']}"
        scores_map[key] = float(s['marks'])

    cursor.close()
    conn.close()
    print(json.dumps({
        "status": "success",
        "event": event,
        "participants": participants,
        "criteria": criteria,
        "existing_scores": scores_map
    }))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
