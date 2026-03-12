#!C:/Python314/python.exe
import cgi
import cgitb
import json
import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))
from db_config import get_connection

cgitb.enable()
print("Content-Type: application/json")
print()

try:
    form = cgi.FieldStorage()
    user_id = form.getvalue('user_id', '')
    event_id = form.getvalue('event_id', '')
    performance_title = form.getvalue('performance_title', '').strip()
    category_entry = form.getvalue('category_entry', '').strip()
    bio = form.getvalue('bio', '').strip()

    if not user_id or not event_id or not performance_title:
        print(json.dumps({"status": "error", "message": "user_id, event_id and performance_title are required"}))
        sys.exit()

    # Handle photo upload
    photo_path = ""
    if 'photo' in form and hasattr(form['photo'], 'filename') and form['photo'].filename:
        photo_item = form['photo']
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        safe_name = "".join(c for c in photo_item.filename if c.isalnum() or c in ('.','-','_'))
        photo_path = f"uploads/{int(time.time())}_{safe_name}"
        full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), photo_path)
        with open(full_path, 'wb') as f:
            f.write(photo_item.file.read())

    conn = get_connection()
    cursor = conn.cursor()

    # Check if already applied
    cursor.execute("SELECT participant_id FROM participants WHERE user_id=%s AND event_id=%s", (user_id, event_id))
    existing = cursor.fetchone()
    if existing:
        print(json.dumps({"status": "error", "message": "You have already applied for this event"}))
        cursor.close()
        conn.close()
        sys.exit()

    cursor.execute(
        "INSERT INTO participants (user_id, event_id, performance_title, category_entry) VALUES (%s,%s,%s,%s)",
        (user_id, event_id, performance_title, category_entry)
    )
    conn.commit()
    pid = cursor.lastrowid

    # Update user bio and photo if provided
    if bio or photo_path:
        updates = []
        vals = []
        if bio:
            updates.append("bio=%s")
            vals.append(bio)
        if photo_path:
            updates.append("photo=%s")
            vals.append(photo_path)
        vals.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE user_id=%s", vals)
        conn.commit()

    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "participant_id": pid, "message": "Application submitted"}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
