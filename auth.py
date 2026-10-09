import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "securefile.db")


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_user(username, password):
    username = username.strip()

    if not username or not password:
        return False

    if len(username) < 3 or len(username) > 30:
        return False

    if len(password) < 8:
        return False

    connection = get_connection()

    try:
        connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, generate_password_hash(password))
        )
        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def verify_user(username, password):
    connection = get_connection()

    try:
        user = connection.execute(
            "SELECT id, username, password_hash "
            "FROM users WHERE username = ?",
            (username.strip(),)
        ).fetchone()

        if user and check_password_hash(
            user["password_hash"], password
        ):
            return {
                "id": user["id"],
                "username": user["username"]
            }

        return None

    finally:
        connection.close()


def init_db():
    connection = get_connection()

    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        connection.commit()

    finally:
        connection.close()
id="o1q3dz"
