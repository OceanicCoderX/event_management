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
    action = form.getvalue('action', 'get')
    category_id = form.getvalue('category_id', '')
    name = form.getvalue('name', '').strip()
    description = form.getvalue('description', '').strip()
    icon = form.getvalue('icon', 'bi-star').strip()

    image_path = ''
    if 'image' in form and getattr(form['image'], 'filename', None):
        import time
        fileitem = form['image']
        filename = os.path.basename(fileitem.filename)
        safe_name = f"{int(time.time())}_{filename.replace(' ', '_')}"
        filepath = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'categories', safe_name)
        with open(filepath, 'wb') as f:
            f.write(fileitem.file.read())
        image_path = f"uploads/categories/{safe_name}"

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if action == 'get':
        cursor.execute("""SELECT c.*, (SELECT COUNT(*) FROM events e WHERE e.category_id=c.category_id) as event_count
                          FROM categories c ORDER BY c.category_id""")
        cats = cursor.fetchall()
        print(json.dumps({"status": "success", "data": cats}))

    elif action == 'add':
        if not image_path:
            image_path = "uploads/categories/default_category.jpg"
        cursor.execute("INSERT INTO categories (name, description, icon, image) VALUES (%s,%s,%s,%s)", (name, description, icon, image_path))
        conn.commit()
        print(json.dumps({"status": "success", "message": "Category added", "category_id": cursor.lastrowid}))

    elif action == 'edit':
        if image_path:
            cursor.execute("UPDATE categories SET name=%s, description=%s, icon=%s, image=%s WHERE category_id=%s",
                           (name, description, icon, image_path, category_id))
        else:
            cursor.execute("UPDATE categories SET name=%s, description=%s, icon=%s WHERE category_id=%s",
                           (name, description, icon, category_id))
        conn.commit()
        print(json.dumps({"status": "success", "message": "Category updated"}))

    elif action == 'delete':
        cursor.execute("DELETE FROM categories WHERE category_id=%s", (category_id,))
        conn.commit()
        print(json.dumps({"status": "success", "message": "Category deleted"}))

    cursor.close()
    conn.close()

except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
