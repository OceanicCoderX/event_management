#!C:/Python314/python.exe
import cgi
import json
import sys
import os
import hashlib
sys.path.insert(0, os.path.dirname(__file__))
from db_config import get_connection

print("Content-Type: application/json")
print()

try:
    form = cgi.FieldStorage()
    action = form.getvalue('action', 'get')
    judge_id = form.getvalue('judge_id', '')
    full_name = form.getvalue('full_name', '').strip()
    email = form.getvalue('email', '').strip()
    phone = form.getvalue('phone', '').strip()
    password = form.getvalue('password', '').strip()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if action == 'get':
        cursor.execute("""SELECT u.user_id, u.full_name, u.email, u.phone, u.created_at,
                          (SELECT COUNT(*) FROM judge_assignments ja WHERE ja.judge_user_id=u.user_id) as assigned_events
                          FROM users u WHERE u.role='judge' ORDER BY u.created_at DESC""")
        judges = cursor.fetchall()
        for j in judges:
            if j.get('created_at'):
                j['created_at'] = str(j['created_at'])
        print(json.dumps({"status": "success", "data": judges}))

    elif action == 'add':
        if not full_name or not email or not password:
            print(json.dumps({"status": "error", "message": "Name, email and password required"}))
        else:
            md5_pw = hashlib.md5(password.encode()).hexdigest()
            cursor.execute("INSERT INTO users (full_name, email, phone, password, role) VALUES (%s,%s,%s,%s,'judge')",
                           (full_name, email, phone, md5_pw))
            conn.commit()
            print(json.dumps({"status": "success", "message": "Judge added", "judge_id": cursor.lastrowid}))

    elif action == 'delete':
        cursor.execute("DELETE FROM users WHERE user_id=%s AND role='judge'", (judge_id,))
        conn.commit()
        print(json.dumps({"status": "success", "message": "Judge removed"}))

    cursor.close()
    conn.close()

except Exception as e:
    if 'Duplicate entry' in str(e):
        print(json.dumps({"status": "error", "message": "Email already exists"}))
    else:
        print(json.dumps({"status": "error", "message": str(e)}))
