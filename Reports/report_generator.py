"""
Reports/report_generator.py

Queries the database to build attendance reports:
- Today's attendance
- Full attendance history for a date range
- Per-person attendance history
"""

from Database.db_connection import fetch_query


def get_attendance_by_date_range(start_date, end_date):
    """
    Returns all attendance records between start_date and end_date
    (inclusive), joined with person details, ordered by date/time.

    Dates must be in 'YYYY-MM-DD' format (matches how they're stored).
    """
    rows = fetch_query(
        """
        SELECT attendance.attendance_id, persons.name, persons.roll_no,
               persons.department, attendance.date, attendance.time_in,
               attendance.status
        FROM attendance
        JOIN persons ON attendance.person_id = persons.person_id
        WHERE attendance.date BETWEEN ? AND ?
        ORDER BY attendance.date DESC, attendance.time_in DESC
        """,
        (start_date, end_date),
    )
    return rows


def get_all_attendance():
    """Returns every attendance record ever recorded, most recent first."""
    rows = fetch_query(
        """
        SELECT attendance.attendance_id, persons.name, persons.roll_no,
               persons.department, attendance.date, attendance.time_in,
               attendance.status
        FROM attendance
        JOIN persons ON attendance.person_id = persons.person_id
        ORDER BY attendance.date DESC, attendance.time_in DESC
        """
    )
    return rows


def get_attendance_for_person(roll_no):
    """Returns full attendance history for a single person by roll number."""
    rows = fetch_query(
        """
        SELECT attendance.attendance_id, persons.name, persons.roll_no,
               attendance.date, attendance.time_in, attendance.status
        FROM attendance
        JOIN persons ON attendance.person_id = persons.person_id
        WHERE persons.roll_no = ?
        ORDER BY attendance.date DESC
        """,
        (roll_no,),
    )
    return rows


if __name__ == "__main__":
    # Manual test: python -m Reports.report_generator
    print("=== All Attendance Records ===")
    for row in get_all_attendance():
        print(dict(row))