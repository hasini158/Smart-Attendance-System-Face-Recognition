"""
GUI/login_window.py

The admin login screen - the first thing shown when the app starts.
On successful login, it opens the MainWindow (dashboard) and closes itself.
"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QApplication
)
from PyQt5.QtCore import Qt

from Utils.auth_manager import verify_login
from Utils.ui_helpers import style_placeholder


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = None  # will hold a reference so it isn't garbage-collected
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Smart Attendance System - Admin Login")
        self.setFixedSize(400, 320)

        title_label = QLabel("Smart Attendance System")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("role", "title")

        subtitle_label = QLabel("ADMIN LOGIN")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setProperty("role", "subtitle")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(38)
        style_placeholder(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(38)
        style_placeholder(self.password_input)
        # Pressing Enter in the password field triggers login too
        self.password_input.returnPressed.connect(self.handle_login)

        login_button = QPushButton("Login")
        login_button.setMinimumHeight(42)
        login_button.clicked.connect(self.handle_login)

        layout = QVBoxLayout()
        layout.addSpacing(10)
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(15)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(6)
        layout.addWidget(login_button)
        layout.setContentsMargins(40, 35, 40, 35)
        layout.setSpacing(14)

        self.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        success, message = verify_login(username, password)

        if success:
            # Import here (not at top of file) to avoid a circular import,
            # since main_window.py will later import things that eventually
            # lead back to this file.
            from GUI.main_window import MainWindow

            self.main_window = MainWindow()
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", message)
            self.password_input.clear()


if __name__ == "__main__":
    # Manual test: python -m GUI.login_window
    import sys
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())