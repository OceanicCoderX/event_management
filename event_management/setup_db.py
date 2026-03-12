import subprocess
with open(r"database\event_management.sql", "r", encoding="utf-8") as f:
    sql = f.read()
subprocess.run([r"C:\xampp\mysql\bin\mysql.exe", "-u", "root"], input=sql.encode('utf-8'))
print("Database setup complete.")
