"""
GUI/registration_window.py

The registration form, now with the webcam feed embedded directly in
the window (instead of opening a separate OpenCV popup). The person
clicks "Capture Photo" (instead of pressing SPACE) each time they
want to save a frame, with a live counter and preview.
"""

import os

import cv2
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt, QTimer

from Face_Recognition.face_encoder import register_person, is_roll_no_registered
from Utils.camera_utils import cv_frame_to_qpixmap
from Utils.validators import is_valid_name, is_valid_roll_no, is_valid_email
from Utils.ui_helpers import style_placeholder
from Utils.logger import get_logger

logger = get_logger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FACES_FOLDER = os.path.join(PROJECT_ROOT, "Dataset", "raw_faces")

VIDEO_WIDTH = 380
VIDEO_HEIGHT = 300
NUM_IMAGES_TO_CAPTURE = 5


class RegistrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.video_capture = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)

        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self.captured_count = 0
        self.current_person_folder = None
        self.face_currently_visible = False

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Register New Person")
        self.resize(720, 480)

        title_label = QLabel("Register New Person")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setProperty("role", "title")

        # --- Left column: form fields ---
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        style_placeholder(self.name_input)

        self.roll_no_input = QLineEdit()
        self.roll_no_input.setPlaceholderText("Roll Number / Employee ID")
        style_placeholder(self.roll_no_input)

        self.department_input = QLineEdit()
        self.department_input.setPlaceholderText("Department (e.g. CSE)")
        style_placeholder(self.department_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (optional)")
        style_placeholder(self.email_input)

        self.open_camera_button = QPushButton("Open Camera")
        self.open_camera_button.clicked.connect(self.handle_open_camera)

        back_button = QPushButton("Back to Dashboard")
        back_button.setProperty("role", "secondary")
        back_button.clicked.connect(self.handle_close)

        form_column = QVBoxLayout()
        form_column.addWidget(self.name_input)
        form_column.addWidget(self.roll_no_input)
        form_column.addWidget(self.department_input)
        form_column.addWidget(self.email_input)
        form_column.addSpacing(10)
        form_column.addWidget(self.open_camera_button)
        form_column.addStretch()
        form_column.addWidget(back_button)
        form_column.setSpacing(12)

        # --- Right column: camera preview ---
        self.video_label = QLabel()
        self.video_label.setFixedSize(VIDEO_WIDTH, VIDEO_HEIGHT)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Camera preview will appear here")
        self.video_label.setStyleSheet(
            "background-color: #1F2937; border-radius: 10px; color: #9CA3AF; font-size: 12px;"
        )

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setProperty("role", "subtitle")

        self.capture_button = QPushButton("Capture Photo (0/5)")
        self.capture_button.setEnabled(False)
        self.capture_button.clicked.connect(self.handle_capture_photo)

        video_column = QVBoxLayout()
        video_column.addWidget(self.video_label)
        video_column.addWidget(self.progress_label)
        video_column.addWidget(self.capture_button)
        video_column.setSpacing(10)

        content_row = QHBoxLayout()
        content_row.addLayout(form_column)
        content_row.addLayout(video_column)

        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)
        main_layout.addLayout(content_row)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(10)

        self.setLayout(main_layout)

    def handle_open_camera(self):
        name = self.name_input.text().strip()
        roll_no = self.roll_no_input.text().strip()
        department = self.department_input.text().strip()
        email = self.email_input.text().strip()

        valid, error = is_valid_name(name)
        if not valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return

        valid, error = is_valid_roll_no(roll_no)
        if not valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return

        valid, error = is_valid_email(email)
        if not valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return

        # Duplicate check happens BEFORE opening the camera - no point
        # capturing photos for a registration that will be rejected.
        if is_roll_no_registered(roll_no):
            QMessageBox.warning(
                self, "Duplicate Roll Number",
                f"A person with roll number '{roll_no}' is already registered."
            )
            return

        safe_name = name.replace(" ", "_")
        self.current_person_folder = os.path.join(RAW_FACES_FOLDER, f"{roll_no}_{safe_name}")
        os.makedirs(self.current_person_folder, exist_ok=True)

        self.video_capture = cv2.VideoCapture(0)
        if not self.video_capture.isOpened():
            QMessageBox.critical(self, "Camera Error", "Could not open the webcam.")
            return

        self.captured_count = 0
        self.progress_label.setText("Position your face in the frame, then click Capture.")
        self.capture_button.setText(f"Capture Photo (0/{NUM_IMAGES_TO_CAPTURE})")
        self.capture_button.setEnabled(True)
        self.open_camera_button.setEnabled(False)

        # Lock the form fields while capturing so they can't be changed mid-registration
        for field in (self.name_input, self.roll_no_input, self.department_input, self.email_input):
            field.setEnabled(False)

        self.timer.start(30)

    def update_preview(self):
        ret, frame = self.video_capture.read()
        if not ret:
            logger.error("Failed to read frame from webcam during registration preview.")
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        self.face_currently_visible = len(faces) > 0

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Keep a copy of the CLEAN frame (no box drawn) for saving later,
        # since we don't want the green rectangle baked into the saved photo.
        self._latest_clean_frame = frame.copy()

        pixmap = cv_frame_to_qpixmap(frame, VIDEO_WIDTH, VIDEO_HEIGHT)
        self.video_label.setPixmap(pixmap)

    def handle_capture_photo(self):
        if not self.face_currently_visible:
            QMessageBox.information(self, "No Face Detected", "Please position your face in the frame before capturing.")
            return

        self.captured_count += 1
        image_path = os.path.join(self.current_person_folder, f"{self.captured_count}.jpg")
        cv2.imwrite(image_path, self._latest_clean_frame)
        logger.info(f"Captured image {self.captured_count}/{NUM_IMAGES_TO_CAPTURE}: {image_path}")

        self.capture_button.setText(f"Capture Photo ({self.captured_count}/{NUM_IMAGES_TO_CAPTURE})")
        self.progress_label.setText(f"Captured {self.captured_count} of {NUM_IMAGES_TO_CAPTURE} photos.")

        if self.captured_count >= NUM_IMAGES_TO_CAPTURE:
            self.finish_capture()

    def finish_capture(self):
        self.timer.stop()
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None

        self.video_label.clear()
        self.video_label.setText("Processing...")
        self.capture_button.setEnabled(False)

        name = self.name_input.text().strip()
        roll_no = self.roll_no_input.text().strip()
        department = self.department_input.text().strip()
        email = self.email_input.text().strip()

        success, message = register_person(roll_no, name, department, email, self.current_person_folder)

        if success:
            QMessageBox.information(self, "Success", message)
            logger.info(f"Registered via GUI: {name} ({roll_no})")
            self.reset_form()
        else:
            QMessageBox.warning(self, "Registration Failed", message)
            self.reset_form()

    def reset_form(self):
        self.name_input.clear()
        self.roll_no_input.clear()
        self.department_input.clear()
        self.email_input.clear()

        for field in (self.name_input, self.roll_no_input, self.department_input, self.email_input):
            field.setEnabled(True)

        self.video_label.setText("Camera preview will appear here")
        self.progress_label.setText("")
        self.capture_button.setText(f"Capture Photo (0/{NUM_IMAGES_TO_CAPTURE})")
        self.open_camera_button.setEnabled(True)
        self.captured_count = 0

    def handle_close(self):
        self.timer.stop()
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        self.close()

    def closeEvent(self, event):
        self.timer.stop()
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None
        event.accept()


if __name__ == "__main__":
    # Manual test: python -m GUI.registration_window
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = RegistrationWindow()
    window.show()
    sys.exit(app.exec_())