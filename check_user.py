import sqlite3
import os

DB_PATH = os.path.expanduser("~/.wolfclaw/wolfclaw_local.db")
email = "pravinved613@gmail.com"

if not os.path.exists(DB_PATH):
    print(f"DB not found at {DB_PATH}")
    exit(1)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT * FROM users WHERE email = ?", (email,))
row = c.fetchone()
if row:
    print(f"User found: {dict(row)}")
else:
    print(f"User {email} NOT found")
    c.execute("SELECT email FROM users")
    print("All users:", [r['email'] for r in c.fetchall()])

conn.close()
