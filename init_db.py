import sqlite3
import os

DB_PATH = "database.db"

# Remove old DB if exists (fresh start)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
    print("Old database removed.")

conn = sqlite3.connect(DB_PATH)
cur  = conn.cursor()

with open("schema.sql") as f:
    cur.executescript(f.read())

conn.commit()
conn.close()
print("✅ Database created successfully!")
print()
print("Default login credentials:")
print("  Admin    : admin@university.edu  / admin123")
print("  Instructor: smith@university.edu / pass123")
print("  Student  : john@university.edu  / pass123")
