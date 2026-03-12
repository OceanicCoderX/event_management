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

    cursor.execute("""SELECT p.participant_id, u.full_name, p.performance_title,
                      c.criteria_name, c.max_marks, s.marks, s.criteria_id
                      FROM participants p 
                      JOIN users u ON p.user_id=u.user_id
                      JOIN criteria c ON c.event_id=p.event_id
                      LEFT JOIN scores s ON s.participant_id=p.participant_id AND s.criteria_id=c.criteria_id AND s.judge_user_id=%s
                      WHERE p.event_id=%s AND p.status='Approved'
                      ORDER BY p.participant_id, c.criteria_id""", (judge_user_id, event_id))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    # Convert Decimal to float
    for r in rows:
        for key, value in r.items():
            if isinstance(value, decimal.Decimal):
                r[key] = float(value)
    print(json.dumps({"status": "success", "data": [
        {**r, "marks": float(r['marks']) if r['marks'] is not None else None} for r in rows
    ]}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
