
import sqlite3
from pathlib import Path
from config import Config


def get_database_connection():

    connection = sqlite3.connect(
        Config.DATABASE_PATH,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():

    Path(Config.DATABASE_PATH).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = get_database_connection()

    try:

        connection.executescript("""

            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            );


            CREATE TABLE IF NOT EXISTS files (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                original_filename TEXT NOT NULL,
                stored_filename TEXT NOT NULL UNIQUE,
                file_size INTEGER NOT NULL CHECK(file_size >= 0),
                integrity_hash TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE

            );


            CREATE INDEX IF NOT EXISTS idx_files_user_uploaded

            ON files(user_id, uploaded_at DESC);

        """)

        connection.commit()

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


def create_user(username, email, password_hash):

    connection = get_database_connection()

    try:

        cursor = connection.execute(

            """
            INSERT INTO users
            (username, email, password_hash)
            VALUES (?, ?, ?)
            """,

            (username, email, password_hash)

        )

        connection.commit()

        return cursor.lastrowid

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


def get_user_by_email(email):

    connection = get_database_connection()

    try:

        return connection.execute(

            "SELECT * FROM users WHERE email = ?",
            (email,)

        ).fetchone()

    finally:

        connection.close()


def get_user_by_id(user_id):

    connection = get_database_connection()

    try:

        return connection.execute(

            "SELECT * FROM users WHERE id = ?",
            (user_id,)

        ).fetchone()

    finally:

        connection.close()


def create_file_record(
    user_id,
    original_filename,
    stored_filename,
    file_size,
    integrity_hash
):

    connection = get_database_connection()

    try:

        cursor = connection.execute(

            """
            INSERT INTO files (
                user_id,
                original_filename,
                stored_filename,
                file_size,
                integrity_hash
            )
            VALUES (?, ?, ?, ?, ?)
            """,

            (
                user_id,
                original_filename,
                stored_filename,
                file_size,
                integrity_hash
            )

        )

        connection.commit()

        return cursor.lastrowid

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


def get_file_by_id_and_user(file_id, user_id):

    connection = get_database_connection()

    try:

        return connection.execute(

            """
            SELECT *
            FROM files
            WHERE id = ? AND user_id = ?
            """,

            (file_id, user_id)

        ).fetchone()

    finally:

        connection.close()


def get_files_by_user(user_id):

    connection = get_database_connection()

    try:

        return connection.execute(

            """
            SELECT
                id,
                original_filename,
                file_size,
                uploaded_at
            FROM files
            WHERE user_id = ?
            ORDER BY uploaded_at DESC
            """,

            (user_id,)

        ).fetchall()

    finally:

        connection.close()
