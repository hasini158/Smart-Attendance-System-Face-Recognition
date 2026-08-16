"""
Utils/ui_helpers.py

Small shared PyQt5 UI helpers used across multiple GUI windows.
"""

from PyQt5.QtGui import QPalette, QColor


def style_placeholder(line_edit):
    """
    Gives placeholder text a darker, more readable gray than PyQt5's
    very light default, improving contrast against a white background.
    """
    palette = line_edit.palette()
    palette.setColor(QPalette.PlaceholderText, QColor("#8B95A1"))
    line_edit.setPalette(palette)