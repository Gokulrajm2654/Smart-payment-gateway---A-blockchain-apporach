import sqlite3

conn = sqlite3.connect("user.db")
c = conn.cursor()

# Create the user table with the email column included
c.execute("""CREATE TABLE IF NOT EXISTS user (
                username TEXT,
                account_address TEXT,
                private_key TEXT,
                password TEXT,
                email TEXT,
                failed_attempts INTEGER DEFAULT 0
)""")

c.execute("""CREATE TABLE IF NOT EXISTS password_reset_tokens (
                token TEXT PRIMARY KEY,
                email TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

conn.commit()
conn.close()
