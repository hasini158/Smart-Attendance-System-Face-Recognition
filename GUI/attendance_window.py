"""
GUI/attendance_window.py

Live attendance recognition, fully embedded inside the app window
(no separate OpenCV popup). Shows the camera feed directly in a
QLabel, updated ~30 times per second via QTimer, with face detection/
recognition running on each frame. A live-updating list on the right
shows everyone marked present in this session, as it happens.
"""

import cv2
import face_recognition
import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor

from Face_Recognition.face_matcher import load_known_encodings, MATCH_THRESHOLD
from Attendance.attendance_manager import mark_attendance
from Utils.camera_utils import cv_frame_to_qpixmap
from Utils.logger import get_logger

logger = get_logger(__name__)

VIDEO_WIDTH = 480
VIDEO_HEIGHT = 360


class AttendanceWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.video_capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)

        self.known_encodings = []
        self.known_names = []
        self.known_person_ids = []

        # Tracks who has been greeted with a list entry THIS session,
        # so we don't spam the list every frame for the same person.
        self.session_marked_ids = set()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Take Attendance")
        self.resize(760, 460)

        title_label = QLabel("Live Attendance Recognition")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("role", "title")

        # --- Left side: camera preview ---
        self.video_label = QLabel()
        self.video_label.setFixedSize(VIDEO_WIDTH, VIDEO_HEIGHT)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Camera preview will appear here")
        self.video_label.setStyleSheet(
            "background-color: #1F2937; border-radius: 10px; color: #9CA3AF; font-size: 12px;"
        )

        self.status_label = QLabel("Camera stopped.")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setProperty("role", "subtitle")

        self.start_button = QPushButton("Start Recognition")
        self.start_button.clicked.connect(self.start_recognition)

        self.stop_button = QPushButton("Stop")
        self.stop_button.setProperty("role", "danger")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_recognition)

        button_row = QHBoxLayout()
        button_row.addWidget(self.start_button)
        button_row.addWidget(self.stop_button)

        left_column = QVBoxLayout()
        left_column.addWidget(self.video_label)
        left_column.addWidget(self.status_label)
        left_column.addLayout(button_row)
        left_column.setSpacing(10)

        # --- Right side: live attendance list for this session ---
        list_label = QLabel("Marked Present (This Session)")
        list_label.setProperty("role", "subtitle")

        self.attendance_list = QListWidget()
        self.attendance_list.setFixedWidth(220)

        right_column = QVBoxLayout()
        right_column.addWidget(list_label)
        right_column.addWidget(self.attendance_list)

        content_row = QHBoxLayout()
        content_row.addLayout(left_column)
        content_row.addLayout(right_column)

        back_button = QPushButton("Back to Dashboard")
        back_button.setProperty("role", "secondary")
        back_button.clicked.connect(self.handle_close)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)
        main_layout.addLayout(content_row)
        main_layout.addSpacing(10)
        main_layout.addWidget(back_button)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)

    def start_recognition(self):
        self.known_encodings, self.known_names, self.known_person_ids = load_known_encodings()

        if not self.known_encodings:
            QMessageBox.warning(
                self, "No Registered Faces",
                "No registered faces were found. Please register at least one person first."
            )
            return

        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            QMessageBox.critical(self, "Camera Error", "Could not open the webcam.")
            return

        self.session_marked_ids.clear()
        self.attendance_list.clear()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.status_label.setText("Recognition running...")

        logger.info("Embedded recognition session started.")
        self.timer.start(30)  # ~33 frames per second

    def process_frame(self):
        ret, frame = self.video_capture.read()
        if not ret:
            logger.error("Failed to read frame from webcam during embedded recognition.")
            return

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

            name_to_display = "Unknown"
            box_color = (0, 0, 255)  # red (BGR)

            if self.known_encodings:
                distances = face_recognition.face_distance(self.known_encodings, face_encoding)
                best_match_index = np.argmin(distances)

                if distances[best_match_index] <= MATCH_THRESHOLD:
                    name_to_display = self.known_names[best_match_index]
                    person_id = self.known_person_ids[best_match_index]
                    box_color = (0, 255, 0)  # green

                    marked, message = mark_attendance(person_id)

                    if person_id not in self.session_marked_ids:
                        self.session_marked_ids.add(person_id)
                        self.add_to_session_list(name_to_display, marked)

            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.rectangle(frame, (left, bottom - 25), (right, bottom), box_color, cv2.FILLED)
            cv2.putText(frame, name_to_display, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        pixmap = cv_frame_to_qpixmap(frame, VIDEO_WIDTH, VIDEO_HEIGHT)
        self.video_label.setPixmap(pixmap)

    def add_to_session_list(self, name, newly_marked):
        item_text = f"✓ {name}" if newly_marked else f"• {name} (already marked)"
        item = QListWidgetItem(item_text)
        if newly_marked:
            item.setForeground(QColor("#27AE60"))
        else:
            item.setForeground(QColor("#6B7280"))
        self.attendance_list.addItem(item)

    def stop_recognition(self):
        self.timer.stop()
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None

        self.video_label.clear()
        self.video_label.setText("Camera preview will appear here")
        self.status_label.setText("Camera stopped.")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        logger.info("Embedded recognition session stopped.")

    def handle_close(self):
        self.stop_recognition()
        self.close()

    def closeEvent(self, event):
        # Safety net: if the window is closed via the X button while
        # the camera is still running, release it properly first.
        self.stop_recognition()
        event.accept()


if __name__ == "__main__":
    # Manual test: python -m GUI.attendance_window
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = AttendanceWindow()
    window.show()
    sys.exit(app.exec_())