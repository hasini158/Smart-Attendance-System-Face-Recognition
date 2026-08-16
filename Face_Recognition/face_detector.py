"""
Face_Recognition/face_detector.py

Opens the webcam, detects a face in the live feed, and captures a
set number of images when the person presses SPACE. Images are saved
under Dataset/raw_faces/<roll_no>_<name>/ for later encoding.

This file only handles CAPTURING images - it does NOT generate
encodings. That happens in face_encoder.py (the next step).
"""

import os
import cv2

from Utils.logger import get_logger

logger = get_logger(__name__)

# Project root is two levels up from this file (Face_Recognition/ -> project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FACES_FOLDER = os.path.join(PROJECT_ROOT, "Dataset", "raw_faces")

# How many good face images to capture per person
NUM_IMAGES_TO_CAPTURE = 5


def capture_faces(roll_no, name, camera_index=0):
    """
    Opens the webcam and captures NUM_IMAGES_TO_CAPTURE face images
    for the given person, saving them to:
        Dataset/raw_faces/<roll_no>_<name>/1.jpg, 2.jpg, ...

    Controls (while the camera window is focused):
        SPACE  -> capture the current frame (only works when a face is detected)
        ESC    -> quit early

    Returns:
        (True, folder_path) on success
        (False, error_message) on failure
    """
    # Build a safe folder name, e.g. "21A91A0501_Hasini"
    safe_name = name.strip().replace(" ", "_")
    person_folder_name = f"{roll_no}_{safe_name}"
    person_folder_path = os.path.join(RAW_FACES_FOLDER, person_folder_name)
    os.makedirs(person_folder_path, exist_ok=True)

    # Haar Cascade is a lightweight, built-in OpenCV face detector - fast
    # enough for live preview. (The actual recognition later uses a much
    # more accurate deep-learning model from face_recognition/dlib; this
    # one is just for showing a live box while capturing.)
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    video_capture = cv2.VideoCapture(camera_index)
    if not video_capture.isOpened():
        logger.error("Could not open webcam.")
        return False, "Could not open webcam. Check if another app is using it."

    captured_count = 0
    logger.info(f"Starting face capture for {person_folder_name}")

    while captured_count < NUM_IMAGES_TO_CAPTURE:
        ret, frame = video_capture.read()
        if not ret:
            logger.error("Failed to read frame from webcam.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
        )

        display_frame = frame.copy()
        face_detected = len(faces) > 0

        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # On-screen instructions
        status_text = "Face detected - press SPACE to capture" if face_detected \
            else "No face detected"
        cv2.putText(display_frame, status_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0) if face_detected else (0, 0, 255), 2)
        cv2.putText(display_frame, f"Captured: {captured_count}/{NUM_IMAGES_TO_CAPTURE}",
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(display_frame, "Press ESC to cancel", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("Face Registration - Smart Attendance System", display_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC key
            logger.warning(f"Face capture cancelled by user for {person_folder_name}")
            video_capture.release()
            cv2.destroyAllWindows()
            return False, "Capture cancelled by user."

        if key == 32 and face_detected:  # SPACE key, only if a face is visible
            captured_count += 1
            image_path = os.path.join(person_folder_path, f"{captured_count}.jpg")
            cv2.imwrite(image_path, frame)
            logger.info(f"Captured image {captured_count}/{NUM_IMAGES_TO_CAPTURE}: {image_path}")

    video_capture.release()
    cv2.destroyAllWindows()

    if captured_count == NUM_IMAGES_TO_CAPTURE:
        logger.info(f"Successfully captured all images for {person_folder_name}")
        return True, person_folder_path
    else:
        return False, "Capture incomplete."


if __name__ == "__main__":
    # Manual test: python -m Face_Recognition.face_detector
    print("=== Face Capture Test ===")
    test_roll_no = input("Enter test roll number (e.g. TEST001): ").strip()
    test_name = input("Enter test name (e.g. Hasini): ").strip()

    success, result = capture_faces(test_roll_no, test_name)
    if success:
        print(f"\n✅ Success! Images saved to: {result}")
    else:
        print(f"\n❌ Failed: {result}")