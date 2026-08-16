"""
GUI/main_window.py

The main dashboard shown after a successful login. Provides buttons
to navigate to Registration, Take Attendance, and Reports.

Note: registration_window.py and reports_window.py are built in the
next steps of Phase 4 - for now, their buttons are wired up but the
windows themselves are added as we go.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt

from Utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.registration_window = None
        self.attendance_window = None
        self.reports_window = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart Attendance System - Dashboard")
        self.resize(520, 480)
        self.setMinimumSize(460, 440)

        title_label = QLabel("Smart Attendance System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("role", "title")

        subtitle_label = QLabel("Admin Dashboard")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setProperty("role", "subtitle")

        register_button = QPushButton("  📋   Register New Person\n        Add a new face to the system")
        register_button.setProperty("role", "card")
        register_button.setMinimumHeight(82)
        register_button.clicked.connect(self.open_registration)

        attendance_button = QPushButton("  📷   Take Attendance\n        Start live face recognition")
        attendance_button.setProperty("role", "card")
        attendance_button.setMinimumHeight(82)
        attendance_button.clicked.connect(self.open_attendance)

        reports_button = QPushButton("  📊   View Reports\n        See and export attendance data")
        reports_button.setProperty("role", "card")
        reports_button.setMinimumHeight(82)
        reports_button.clicked.connect(self.open_reports)

        logout_button = QPushButton("Logout")
        logout_button.setProperty("role", "danger")
        logout_button.setMinimumHeight(40)
        logout_button.clicked.connect(self.handle_logout)

        layout = QVBoxLayout()
        layout.addSpacing(10)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(26)
        layout.addWidget(register_button)
        layout.addWidget(attendance_button)
        layout.addWidget(reports_button)
        layout.addStretch()
        layout.addWidget(logout_button)
        layout.setContentsMargins(45, 35, 45, 35)
        layout.setSpacing(16)

        self.setLayout(layout)

    def open_registration(self):
        try:
            from GUI.registration_window import RegistrationWindow
            self.registration_window = RegistrationWindow()
            self.registration_window.show()
        except ImportError:
            QMessageBox.information(
                self, "Coming Soon",
                "Registration window will be built in the next step."
            )

    def open_attendance(self):
        try:
            from GUI.attendance_window import AttendanceWindow
            self.attendance_window = AttendanceWindow()
            self.attendance_window.show()
        except ImportError:
            QMessageBox.information(
                self, "Coming Soon",
                "Attendance window will be built in the next step."
            )

    def open_reports(self):
        try:
            from GUI.reports_window import ReportsWindow
            self.reports_window = ReportsWindow()
            self.reports_window.show()
        except ImportError:
            QMessageBox.information(
                self, "Coming Soon",
                "Reports window will be built in the next step."
            )

    def handle_logout(self):
        logger.info("Admin logged out.")
        from GUI.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    # Manual test: python -m GUI.main_window
    # (Skips login, opens dashboard directly - for layout testing only)
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())