"""
Utils/camera_utils.py

Small shared helper for converting an OpenCV (BGR, numpy array) video
frame into a QPixmap that can be displayed inside a QLabel. Used by
any GUI window that embeds a live camera preview (Registration and
Attendance windows).
"""

import cv2
from PyQt5.QtGui import QImage, QPixmap


def cv_frame_to_qpixmap(frame, target_width=None, target_height=None):
    """
    Converts a BGR OpenCV frame into a QPixmap, optionally scaled to
    fit within the given target size while preserving aspect ratio.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb_frame.shape
    bytes_per_line = channels * width

    qimage = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(qimage)

    if target_width and target_height:
        pixmap = pixmap.scaled(target_width, target_height, aspectRatioMode=1)  # Qt.KeepAspectRatio

    return pixmap