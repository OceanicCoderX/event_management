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
    event_id = form.getvalue('event_id', '')
    title = form.getvalue('title', '').strip()
    category_id = form.getvalue('category_id', '')
    description = form.getvalue('description', '').strip()
    venue = form.getvalue('venue', '').strip()
    event_date = form.getvalue('event_date', '')
    registration_deadline = form.getvalue('registration_deadline', '')
    status = form.getvalue('status', 'Upcoming')
    judge_weight = form.getvalue('judge_weight', '60')
    vote_weight = form.getvalue('vote_weight', '40')

    poster_image = ''
    if 'poster_image' in form and getattr(form['poster_image'], 'filename', None):
        import time
        fileitem = form['poster_image']
        filename = os.path.basename(fileitem.filename)
        safe_name = f"{int(time.time())}_{filename.replace(' ', '_')}"
        filepath = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'events', safe_name)
        with open(filepath, 'wb') as f:
            f.write(fileitem.file.read())
        poster_image = f"uploads/events/{safe_name}"

    if not title or not event_date:
        print(json.dumps({"status": "error", "message": "Title and event date are required"}))
        sys.exit()

    conn = get_connection()
    cursor = conn.cursor()

    if event_id:
        if poster_image:
            cursor.execute("""UPDATE events SET title=%s, category_id=%s, description=%s, venue=%s,
                              event_date=%s, registration_deadline=%s, status=%s,
                              judge_weight=%s, vote_weight=%s, poster_image=%s WHERE event_id=%s""",
                           (title, category_id or None, description, venue, event_date,
                            registration_deadline or None, status, judge_weight, vote_weight, poster_image, event_id))
        else:
            cursor.execute("""UPDATE events SET title=%s, category_id=%s, description=%s, venue=%s,
                              event_date=%s, registration_deadline=%s, status=%s,
                              judge_weight=%s, vote_weight=%s WHERE event_id=%s""",
                           (title, category_id or None, description, venue, event_date,
                            registration_deadline or None, status, judge_weight, vote_weight, event_id))
        msg = "Event updated successfully"
    else:
        if not poster_image:
            poster_image = "uploads/events/default_poster.jpg"
        cursor.execute("""INSERT INTO events (title, category_id, description, venue, event_date,
                          registration_deadline, status, judge_weight, vote_weight, poster_image)
                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                       (title, category_id or None, description, venue, event_date,
                        registration_deadline or None, status, judge_weight, vote_weight, poster_image))
        event_id = cursor.lastrowid
        msg = "Event created successfully"

    conn.commit()
    cursor.close()
    conn.close()
    print(json.dumps({"status": "success", "message": msg, "event_id": int(event_id)}))

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
