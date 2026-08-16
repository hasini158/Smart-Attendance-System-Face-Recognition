"""
Utils/auth_manager.py

Handles admin account creation and login verification for the
Smart Attendance System. Passwords are never stored in plain text -
bcrypt is used to hash them before saving to the database.
"""

import bcrypt

from Database.db_connection import execute_query, fetch_query
from Utils.logger import get_logger
from Utils.validators import is_valid_username, is_valid_password

logger = get_logger(__name__)


def create_admin(username, password, role="admin"):
    """
    Creates a new admin user with a securely hashed password.

    Returns:
        (True, "Success message") on success
        (False, "Reason it failed") on failure
    """
    valid_username, username_error = is_valid_username(username)
    if not valid_username:
        return False, username_error

    valid_password, password_error = is_valid_password(password)
    if not valid_password:
        return False, password_error

    # Check if username already exists
    existing = fetch_query(
        "SELECT * FROM admin_users WHERE username = ?",
        (username,),
        fetch_one=True,
    )
    if existing:
        return False, f"Username '{username}' already exists."

    # bcrypt.hashpw needs bytes, and returns bytes - we decode to store as text
    password_bytes = password.encode("utf-8")
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt()).decode("utf-8")

    new_id = execute_query(
        "INSERT INTO admin_users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, hashed_password, role),
    )

    if new_id is not None:
        logger.info(f"Admin user created: {username}")
        return True, f"Admin '{username}' created successfully."
    else:
        logger.error(f"Failed to create admin user: {username}")
        return False, "Database error while creating admin user."


def verify_login(username, password):
    """
    Verifies a login attempt against the stored hashed password.

    Returns:
        (True, "Login successful") if credentials match
        (False, "Reason it failed") otherwise
    """
    if not username or not password:
        return False, "Username and password are required."

    user_row = fetch_query(
        "SELECT * FROM admin_users WHERE username = ?",
        (username,),
        fetch_one=True,
    )

    if user_row is None:
        logger.warning(f"Login attempt for non-existent user: {username}")
        return False, "Invalid username or password."

    stored_hash = user_row["password_hash"].encode("utf-8")
    password_bytes = password.encode("utf-8")

    if bcrypt.checkpw(password_bytes, stored_hash):
        logger.info(f"Successful login: {username}")
        return True, "Login successful."
    else:
        logger.warning(f"Failed login attempt for user: {username}")
        return False, "Invalid username or password."


if __name__ == "__main__":
    # Manual test: python Utils/auth_manager.py
    # Creates a default admin (only works once - second run will say
    # "already exists", which confirms the duplicate-check works too).
    success, message = create_admin("admin", "admin123")
    print(message)

    # Test login with correct password
    success, message = verify_login("admin", "admin123")
    print(f"Correct password test -> {success}: {message}")

    # Test login with wrong password
    success, message = verify_login("admin", "wrongpassword")
    print(f"Wrong password test -> {success}: {message}")