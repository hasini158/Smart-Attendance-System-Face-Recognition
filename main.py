"""
main.py

Single entry point for the Smart Attendance System.
Run this file to start the entire application:

    python main.py

What it does, in order:
1. Shows a branded splash screen
2. Ensures the database and all tables exist (safe to run every time)
3. Loads the global stylesheet and app icon
4. Launches the PyQt application, starting with the Login window
"""

import os
import sys

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt, QTimer

from Database.db_connection import initialize_database
from GUI.login_window import LoginWindow
from Utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STYLESHEET_PATH = os.path.join(PROJECT_ROOT, "Assets", "style", "style.qss")
ICON_PATH = os.path.join(PROJECT_ROOT, "Assets", "icons", "app_icon.ico")


def load_stylesheet(app):
    """Loads the global QSS stylesheet, if it exists. Fails silently
    (with a log warning) rather than crashing the app, since styling
    is cosmetic and should never block the app from running."""
    try:
        with open(STYLESHEET_PATH, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
        logger.info("Stylesheet loaded successfully.")
    except FileNotFoundError:
        logger.warning(f"Stylesheet not found at {STYLESHEET_PATH}, using default look.")


def build_splash_pixmap():
    """Draws a simple branded splash screen entirely in code, so no
    extra image asset is required."""
    width, height = 420, 260
    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#1F3B57"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    painter.setPen(QColor("#FFFFFF"))
    title_font = QFont("Segoe UI", 18, QFont.Bold)
    painter.setFont(title_font)
    painter.drawText(pixmap.rect().adjusted(0, -20, 0, 0), Qt.AlignCenter, "Smart Attendance\nSystem")

    painter.setPen(QColor("#9FB4C7"))
    subtitle_font = QFont("Segoe UI", 10)
    painter.setFont(subtitle_font)
    painter.drawText(pixmap.rect().adjusted(0, 60, 0, 0), Qt.AlignCenter, "Loading, please wait...")

    painter.end()
    return pixmap


def main():
    logger.info("Application starting...")

    app = QApplication(sys.argv)

    load_stylesheet(app)

    if os.path.exists(ICON_PATH):
        app.setWindowIcon(QIcon(ICON_PATH))

    splash = QSplashScreen(build_splash_pixmap())
    splash.show()
    app.processEvents()

    # Safe to call every time - only creates tables if they don't exist yet
    initialize_database()

    window = LoginWindow()

    # Keep the splash visible briefly so it doesn't just flash instantly,
    # then show the login window and close the splash.
    def show_login():
        window.show()
        splash.finish(window)

    QTimer.singleShot(900, show_login)

    exit_code = app.exec_()
    logger.info("Application closed.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()