"""
Utils/logger.py

Provides one shared logger for the entire application, so every module
(Database, Face_Recognition, Attendance, GUI, etc.) writes to the same
log file in a consistent format, instead of each using scattered
print() statements.
"""

import logging
import os

# logs/ folder lives at the project root, one level up from Utils/
LOGS_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs"
)
os.makedirs(LOGS_FOLDER, exist_ok=True)
LOG_FILE = os.path.join(LOGS_FOLDER, "app.log")


def get_logger(name):
    """
    Returns a configured logger instance.

    Usage in any other file:
        from Utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
        logger.error("Something went wrong")
    """
    logger = logging.getLogger(name)

    # Prevents adding duplicate handlers if get_logger() is called
    # multiple times for the same module (common when modules are
    # re-imported during development).
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Writes to logs/app.log
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Also prints to the terminal, so you see logs live while developing
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    # Quick manual test: python Utils/logger.py
    test_logger = get_logger("test")
    test_logger.info("Logger is working correctly.")
    test_logger.warning("This is a sample warning.")
    test_logger.error("This is a sample error.")
    print(f"\nCheck the log file at: {LOG_FILE}")