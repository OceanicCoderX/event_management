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
    voter_user_id = form.getvalue('voter_user_id', '')
    participant_id = form.getvalue('participant_id', '')
    event_id = form.getvalue('event_id', '')

    if not voter_user_id or not participant_id or not event_id:
        print(json.dumps({"status": "error", "message": "voter_user_id, participant_id and event_id are required"}))
        sys.exit()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check if voting is open
    cursor.execute("SELECT voting_open FROM events WHERE event_id=%s", (event_id,))
    event = cursor.fetchone()
    if not event or not event['voting_open']:
        print(json.dumps({"status": "error", "message": "Voting is not open for this event"}))
        cursor.close()
        conn.close()
        sys.exit()

    # Insert vote
    cursor.execute(
        "INSERT INTO votes (voter_user_id, participant_id, event_id) VALUES (%s,%s,%s)",
        (voter_user_id, participant_id, event_id)
    )
    conn.commit()

    # Get new vote count for this participant
    cursor.execute("SELECT COUNT(*) as cnt FROM votes WHERE participant_id=%s", (participant_id,))
    count_row = cursor.fetchone()
    new_vote_count = count_row['cnt'] if count_row else 0

    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "new_vote_count": new_vote_count}))

except Exception as e:
    if 'Duplicate entry' in str(e) or '1062' in str(e):
        print(json.dumps({"status": "error", "message": "You have already voted in this event"}))
    else:
        print(json.dumps({"status": "error", "message": str(e)}))
