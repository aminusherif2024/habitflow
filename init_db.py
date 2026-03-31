import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Users Table

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email text UNIQUE NOT NULL,
    password text NOT NULL
)
""")

# Habits Table

cursor.execute("""
        CREATE TABLE IF NOT EXISTS habits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        done INTEGER DEFAULT 0,
        user_id INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

cursor.execute("""
        ALTER TABLE habits ADD COLUMN date text
""")
conn.commit()
conn.close()
print("Database Initialized!")