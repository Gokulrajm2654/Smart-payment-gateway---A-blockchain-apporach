import sqlite3

def connect_db():
    """Establish a connection to the SQLite database."""
    return sqlite3.connect("user.db")

def login(userid, password):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM user WHERE username = ? AND password = ?", (userid, password))
        num = c.fetchall()
    except Exception as e:
        print(f"Error during login: {e}")
        num = []
    finally:
        conn.close()
    return num

def signup(userid, acc_addr, priv_key, password, email):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO user (username, account_address, private_key, password, email) VALUES (?, ?, ?, ?, ?)", 
                  (userid, acc_addr, priv_key, password, email))
        conn.commit()
    except Exception as e:
        print(f"Error during signup: {e}")
        return 0
    finally:
        conn.close()
    return 1
import sqlite3

def get_user_by_username(username):
    conn = sqlite3.connect("user.db")  # Connect to your database
    c = conn.cursor()
    
    # Query to select user details by username
    c.execute("SELECT * FROM user WHERE username = ?", (username,))
    user = c.fetchone()  # Fetch the first matching record
    
    conn.close()
    
    return user  # Return the user details or None if not found


def getPrivateKey(userid):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("SELECT private_key FROM user WHERE username=?", (userid,))
        privateKey = c.fetchone()
        return privateKey[0] if privateKey else None
    except Exception as e:
        print(f"Error retrieving private key: {e}")
        return None
    finally:
        conn.close()

def getAccountAddress(userid):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("SELECT account_address FROM user WHERE username=?", (userid,))
        addr = c.fetchone()
        return addr[0] if addr else None
    except Exception as e:
        print(f"Error retrieving account address: {e}")
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("SELECT * FROM user WHERE email = ?", (email,))
        user = c.fetchone()
        return user
    except Exception as e:
        print(f"Error retrieving user by email: {e}")
        return None
    finally:
        conn.close()

def update_password_by_email(email, new_password):
    conn = connect_db()
    c = conn.cursor()
    try:
        c.execute("UPDATE user SET password = ? WHERE email = ?", (new_password, email))
        conn.commit()
    except Exception as e:
        print(f"Error updating password: {e}")
    finally:
        conn.close()

def get_email_by_token(token):
    conn = sqlite3.connect("user.db")
    c = conn.cursor()
    c.execute("SELECT email FROM password_reset_tokens WHERE token = ?", (token,))
    email = c.fetchone()
    conn.close()
    return email[0] if email else None

def save_reset_token(email, token, expiration_time):
    """Save the reset token and expiration time to the database."""
    conn = sqlite3.connect("user.db")
    c = conn.cursor()
    c.execute("INSERT INTO password_reset_tokens (token, email, created_at) VALUES (?, ?, ?)", 
              (token, email, expiration_time))
    conn.commit()
    conn.close()

def delete_token(token):
    """Delete the used token from the database."""
    conn = sqlite3.connect("user.db")
    c = conn.cursor()
    c.execute("DELETE FROM password_reset_tokens WHERE token = ?", (token,))
    conn.commit()
    conn.close()

def update_failed_attempts(username, failed_attempts):
    conn = sqlite3.connect("user.db")
    c = conn.cursor()
    c.execute("UPDATE user SET failed_attempts = ? WHERE username = ?", (failed_attempts, username))
    conn.commit()
    conn.close()

def get_failed_attempts(username):
    conn = sqlite3.connect("user.db")
    c = conn.cursor()
    c.execute("SELECT failed_attempts FROM user WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_email(username):
    conn = sqlite3.connect("user.db")
    c = conn.cursor()
    c.execute("SELECT email FROM user WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None


