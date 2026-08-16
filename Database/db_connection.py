"""
Database/db_connection.py

Handles all SQLite database connections and schema creation for the
Smart Attendance System Using Face Recognition project.

Responsibilities:
- Create the SQLite database file (if it doesn't exist)
- Create all required tables (persons, attendance, admin_users)
- Provide simple, reusable helper functions for the rest of the app
  to run queries, without any other module needing to know SQL details.
"""

import sqlite3
import os

# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

# Database file is stored inside the Database/ folder itself.
DB_FOLDER = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_FOLDER, "attendance.db")


# ---------------------------------------------------------------------------
# CONNECTION HELPER
# ---------------------------------------------------------------------------

def get_connection():
    """
    Creates and returns a new SQLite connection.

    Using check_same_thread=False so the connection can be safely
    passed around between GUI callbacks and background camera threads
    later on (PyQt runs the camera loop off the main thread).
    """
    connection = sqlite3.connect(DB_PATH, check_same_thread=False)

    # Enforces foreign key constraints (e.g., attendance.person_id must
    # reference an existing persons.person_id). SQLite disables this
    # by default, so we turn it on explicitly for every connection.
    connection.execute("PRAGMA foreign_keys = ON;")

    # Lets us access columns by name (row["name"]) instead of only
    # by numeric index (row[0]) - much more readable in other modules.
    connection.row_factory = sqlite3.Row

    return connection


# ---------------------------------------------------------------------------
# SCHEMA CREATION
# ---------------------------------------------------------------------------

def initialize_database():
    """
    Creates all required tables if they do not already exist.
    Safe to call every time the app starts - CREATE TABLE IF NOT EXISTS
    means it will never wipe existing data.
    """
    connection = get_connection()
    cursor = connection.cursor()

    # --- persons table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            person_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL,
            roll_no        TEXT NOT NULL UNIQUE,
            department     TEXT,
            email          TEXT,
            encoding_path  TEXT,
            registered_on  TEXT DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # --- attendance table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id      INTEGER NOT NULL,
            date           TEXT NOT NULL,
            time_in        TEXT NOT NULL,
            status         TEXT DEFAULT 'Present',
            FOREIGN KEY (person_id) REFERENCES persons (person_id)
                ON DELETE CASCADE
        );
    """)

    # --- admin_users table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (
            admin_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username       TEXT NOT NULL UNIQUE,
            password_hash  TEXT NOT NULL,
            role           TEXT DEFAULT 'admin'
        );
    """)

    connection.commit()
    connection.close()
    print(f"[Database] Initialized successfully at: {DB_PATH}")


# ---------------------------------------------------------------------------
# GENERIC QUERY HELPERS
# ---------------------------------------------------------------------------

def execute_query(query, params=()):
    """
    Runs an INSERT, UPDATE, or DELETE statement.

    Args:
        query (str): SQL statement with '?' placeholders.
        params (tuple): Values to safely substitute into the placeholders.

    Returns:
        int: The id of the last inserted row (useful right after an INSERT).
             Returns None if the query wasn't an insert or on failure.
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        return cursor.lastrowid
    except sqlite3.Error as error:
        print(f"[Database] Error executing query: {error}")
        connection.rollback()
        return None
    finally:
        connection.close()


def fetch_query(query, params=(), fetch_one=False):
    """
    Runs a SELECT statement and returns the results.

    Args:
        query (str): SQL SELECT statement with '?' placeholders.
        params (tuple): Values to safely substitute into the placeholders.
        fetch_one (bool): If True, returns a single row (or None).
                           If False, returns a list of rows (possibly empty).

    Returns:
        sqlite3.Row | list[sqlite3.Row] | None
    """
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        if fetch_one:
            return cursor.fetchone()
        return cursor.fetchall()
    except sqlite3.Error as error:
        print(f"[Database] Error fetching query: {error}")
        return None if fetch_one else []
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# MANUAL TEST (only runs if this file is executed directly)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Running this file directly (python Database/db_connection.py)
    # creates the database and tables, and prints confirmation.
    # This does NOT run when this file is imported from elsewhere.
    initialize_database()

    # Quick sanity check: list all tables that now exist in the db file.
    tables = fetch_query(
        "SELECT name FROM sqlite_master WHERE type='table';"
    )
    print("[Database] Tables found:", [row["name"] for row in tables])
