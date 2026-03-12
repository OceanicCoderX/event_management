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
    judge_user_id = form.getvalue('judge_user_id', '')
    event_id = form.getvalue('event_id', '')
    scores_json = form.getvalue('scores', '[]')

    scores = json.loads(scores_json)

    if not judge_user_id or not event_id:
        print(json.dumps({"status": "error", "message": "judge_user_id and event_id required"}))
        sys.exit()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if scores are locked
    cursor.execute("SELECT scores_locked FROM events WHERE event_id=%s", (event_id,))
    event = cursor.fetchone()
    if event and event['scores_locked']:
        print(json.dumps({"status": "error", "message": "Scores are locked for this event"}))
        cursor.close()
        conn.close()
        sys.exit()

    for score in scores:
        participant_id = score.get('participant_id')
        criteria_id = score.get('criteria_id')
        marks = score.get('marks')

        if participant_id is None or criteria_id is None or marks is None:
            continue

        # Validate max_marks
        cursor.execute("SELECT max_marks FROM criteria WHERE criteria_id=%s", (criteria_id,))
        crit = cursor.fetchone()
        if crit and float(marks) > float(crit['max_marks']):
            marks = crit['max_marks']

        cursor.execute("""INSERT INTO scores (judge_user_id, participant_id, criteria_id, marks)
                          VALUES (%s,%s,%s,%s)
                          ON DUPLICATE KEY UPDATE marks=%s, scored_at=NOW()""",
                       (judge_user_id, participant_id, criteria_id, marks, marks))

    conn.commit()
    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "message": "Scores saved successfully"}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
