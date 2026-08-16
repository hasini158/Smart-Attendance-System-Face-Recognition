"""
Models/attendance_record.py

Represents a single attendance entry as a clean Python object,
mirroring one row of the 'attendance' table.
"""


class AttendanceRecord:
    """
    A simple data container for one row of the 'attendance' table.
    """

    def __init__(self, attendance_id=None, person_id=None, date="",
                 time_in="", status="Present"):
        self.attendance_id = attendance_id
        self.person_id = person_id
        self.date = date
        self.time_in = time_in
        self.status = status

    @classmethod
    def from_db_row(cls, row):
        """
        Builds an AttendanceRecord object from a sqlite3.Row.

        Usage:
            row = fetch_query("SELECT * FROM attendance WHERE attendance_id = ?", (1,), fetch_one=True)
            record = AttendanceRecord.from_db_row(row)
        """
        if row is None:
            return None
        return cls(
            attendance_id=row["attendance_id"],
            person_id=row["person_id"],
            date=row["date"],
            time_in=row["time_in"],
            status=row["status"],
        )

    def __repr__(self):
        return f"<Attendance person_id={self.person_id} {self.date} {self.time_in} {self.status}>"