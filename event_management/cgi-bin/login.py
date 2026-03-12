#!C:/Python314/python.exe
import cgi
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from db_config import get_connection
import hashlib

print("Content-Type: application/json")
print()

try:
    form = cgi.FieldStorage()
    email = form.getvalue('email', '').strip()
    password = form.getvalue('password', '').strip()
    role = form.getvalue('role', '').strip()

    if not email or not password or not role:
        print(json.dumps({"status": "error", "message": "Email, password and role are required"}))
        sys.exit()

    md5_password = hashlib.md5(password.encode()).hexdigest()

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_id, full_name, email, role, photo, bio FROM users WHERE email=%s AND password=%s AND role=%s",
        (email, md5_password, role)
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        print(json.dumps({"status": "success", "user_id": user['user_id'],
                          "full_name": user['full_name'], "email": user['email'],
                          "role": user['role'], "photo": user['photo'] or "", "bio": user['bio'] or ""}))
    else:
        print(json.dumps({"status": "error", "message": "Invalid email, password or role"}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
