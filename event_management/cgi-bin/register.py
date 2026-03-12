#!C:/Python314/python.exe
import cgi
import cgitb
import json
import sys
import os
import hashlib
sys.path.insert(0, os.path.dirname(__file__))
from db_config import get_connection

cgitb.enable()
print("Content-Type: application/json")
print()

try:
    form = cgi.FieldStorage()
    full_name = form.getvalue('full_name', '').strip()
    email = form.getvalue('email', '').strip()
    phone = form.getvalue('phone', '').strip()
    password = form.getvalue('password', '').strip()
    role = form.getvalue('role', 'student').strip()
    bio = form.getvalue('bio', '').strip()

    if not full_name or not email or not password:
        print(json.dumps({"status": "error", "message": "Name, email and password are required"}))
        sys.exit()

    if role not in ('student', 'participant'):
        print(json.dumps({"status": "error", "message": "Invalid role for registration"}))
        sys.exit()

    md5_password = hashlib.md5(password.encode()).hexdigest()

    # Handle photo upload
    photo_path = ""
    if 'photo' in form and form['photo'].filename:
        photo_item = form['photo']
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        safe_name = "".join(c for c in photo_item.filename if c.isalnum() or c in ('.','-','_'))
        import time
        photo_path = f"uploads/{int(time.time())}_{safe_name}"
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), photo_path)
        with open(full_path, 'wb') as f:
            f.write(photo_item.file.read())

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (full_name, email, phone, password, role, photo, bio) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (full_name, email, phone, md5_password, role, photo_path, bio)
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.close()
    conn.close()

    print(json.dumps({"status": "success", "user_id": new_id, "message": "Registration successful"}))

except Exception as e:
    if 'Duplicate entry' in str(e):
        print(json.dumps({"status": "error", "message": "Email already registered"}))
    else:
        print(json.dumps({"status": "error", "message": str(e)}))
