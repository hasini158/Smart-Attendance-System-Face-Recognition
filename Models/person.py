"""
Models/person.py

Represents a single registered person (student/employee) as a clean
Python object, instead of passing raw database tuples/dicts around
the rest of the application.
"""


class Person:
    """
    A simple data container for one row of the 'persons' table.

    This class does NOT talk to the database itself - it's just a
    structured way to hold and pass person data between modules
    (e.g., from Database -> GUI, or GUI -> Registration module).
    """

    def __init__(self, person_id=None, name="", roll_no="", department="",
                 email="", encoding_path="", registered_on=None):
        self.person_id = person_id
        self.name = name
        self.roll_no = roll_no
        self.department = department
        self.email = email
        self.encoding_path = encoding_path
        self.registered_on = registered_on

    @classmethod
    def from_db_row(cls, row):
        """
        Builds a Person object from a sqlite3.Row returned by
        Database/db_connection.py's fetch_query().

        Usage:
            row = fetch_query("SELECT * FROM persons WHERE person_id = ?", (1,), fetch_one=True)
            person = Person.from_db_row(row)
        """
        if row is None:
            return None
        return cls(
            person_id=row["person_id"],
            name=row["name"],
            roll_no=row["roll_no"],
            department=row["department"],
            email=row["email"],
            encoding_path=row["encoding_path"],
            registered_on=row["registered_on"],
        )

    def __repr__(self):
        return f"<Person {self.roll_no} - {self.name}>"