"""
Attendance/attendance_manager.py

Contains the business logic for marking attendance:
- Prevents marking the same person twice on the same day
- Inserts a new attendance record with the current date/time
"""

from datetime import datetime

from Database.db_connection import execute_query, fetch_query
from Utils.logger import get_logger

logger = get_logger(__name__)


def is_already_marked_today(person_id):
    """
    Checks whether the given person already has an attendance record
    for today's date.

    Returns:
        True if already marked today, False otherwise.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    row = fetch_query(
        "SELECT * FROM attendance WHERE person_id = ? AND date = ?",
        (person_id, today),
        fetch_one=True,
    )
    return row is not None


def mark_attendance(person_id, status="Present"):
    """
    Marks attendance for the given person_id at the current date/time,
    UNLESS they have already been marked today.

    Returns:
        (True, "message") if a new attendance record was created
        (False, "message") if skipped (already marked) or failed
    """
    if is_already_marked_today(person_id):
        return False, "Already marked today."

    today = datetime.now().strftime("%Y-%m-%d")
    time_now = datetime.now().strftime("%H:%M:%S")

    new_id = execute_query(
        "INSERT INTO attendance (person_id, date, time_in, status) VALUES (?, ?, ?, ?)",
        (person_id, today, time_now, status),
    )

    if new_id is not None:
        logger.info(f"Attendance marked for person_id={person_id} at {time_now}")
        return True, f"Attendance marked at {time_now}."
    else:
        logger.error(f"Failed to mark attendance for person_id={person_id}")
        return False, "Database error while marking attendance."


def get_todays_attendance():
    """
    Returns all attendance records for today, joined with person names,
    ordered by most recent first. Useful for the live recognition screen
    and for a quick 'who's present today' report.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    rows = fetch_query(
        """
        SELECT attendance.attendance_id, persons.name, persons.roll_no,
               attendance.date, attendance.time_in, attendance.status
        FROM attendance
        JOIN persons ON attendance.person_id = persons.person_id
        WHERE attendance.date = ?
        ORDER BY attendance.time_in DESC
        """,
        (today,),
    )
    return rows


if __name__ == "__main__":
    # Manual test: python -m Attendance.attendance_manager
    # Assumes person_id=1 exists (Hasini, registered in Phase 2).
    print("=== Attendance Manager Test ===")

    success, message = mark_attendance(1)
    print(f"First attempt -> {success}: {message}")

    success, message = mark_attendance(1)
    print(f"Second attempt (same day) -> {success}: {message}")

    print("\nToday's attendance:")
    for row in get_todays_attendance():
        print(dict(row))