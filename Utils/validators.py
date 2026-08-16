"""
Utils/validators.py

Simple, reusable input validation functions used during person
registration and admin login, so bad data never reaches the database.
"""

import re


def is_valid_name(name):
    """Name must not be empty and should contain only letters/spaces."""
    if not name or not name.strip():
        return False, "Name cannot be empty."
    if not re.match(r"^[A-Za-z ]+$", name.strip()):
        return False, "Name should contain only letters and spaces."
    return True, ""


def is_valid_roll_no(roll_no):
    """Roll number / employee ID must not be empty and has no spaces."""
    if not roll_no or not roll_no.strip():
        return False, "Roll number / ID cannot be empty."
    if " " in roll_no.strip():
        return False, "Roll number / ID cannot contain spaces."
    return True, ""


def is_valid_email(email):
    """
    Email is optional in our schema, but if provided, must look valid.
    Returns True for an empty string since email is not mandatory.
    """
    if not email or not email.strip():
        return True, ""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.match(pattern, email.strip()):
        return False, "Email format looks invalid (expected e.g. name@example.com)."
    return True, ""


def is_valid_username(username):
    """Admin username must not be empty and at least 4 characters."""
    if not username or len(username.strip()) < 4:
        return False, "Username must be at least 4 characters long."
    return True, ""


def is_valid_password(password):
    """Admin password must be at least 6 characters long."""
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, ""


if __name__ == "__main__":
    # Quick manual tests: python Utils/validators.py
    print(is_valid_name("Hasini Reddy"))     # (True, "")
    print(is_valid_name(""))                  # (False, "Name cannot be empty.")
    print(is_valid_roll_no("21A91A0501"))     # (True, "")
    print(is_valid_email("test@example.com")) # (True, "")
    print(is_valid_email("not-an-email"))     # (False, "...")
    print(is_valid_username("admin"))         # (True, "")
    print(is_valid_password("12345"))         # (False, "...")