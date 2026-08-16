"""
Face_Recognition/face_matcher.py

The core recognition engine:
1. Loads all known face encodings from the database at startup
2. Opens the webcam and continuously detects + encodes live faces
3. Compares each live face against known encodings
4. Draws a labeled bounding box (green = recognized, red = unknown)
5. Automatically marks attendance for recognized faces (once per day)
"""

import pickle

import cv2
import face_recognition
import numpy as np

from Database.db_connection import fetch_query
from Attendance.attendance_manager import mark_attendance
from Utils.logger import get_logger

logger = get_logger(__name__)

# Faces further apart than this distance are considered "not a match".
# Lower = stricter (fewer false matches, but might reject the real person
# in bad lighting). 0.6 is the widely-used default for this model.
MATCH_THRESHOLD = 0.6


def load_known_encodings():
    """
    Loads every registered person's encoding from the database into
    memory. This runs ONCE at startup - not per frame - because
    reading from disk/db on every single frame would be far too slow
    for real-time video.

    Returns:
        known_encodings (list of numpy arrays)
        known_names (list of str)
        known_person_ids (list of int)
    """
    rows = fetch_query("SELECT person_id, name, encoding_path FROM persons")

    known_encodings = []
    known_names = []
    known_person_ids = []

    for row in rows:
        try:
            with open(row["encoding_path"], "rb") as f:
                encoding = pickle.load(f)
            known_encodings.append(encoding)
            known_names.append(row["name"])
            known_person_ids.append(row["person_id"])
        except FileNotFoundError:
            logger.warning(f"Encoding file missing for {row['name']}, skipping.")

    logger.info(f"Loaded {len(known_encodings)} known face encoding(s).")
    return known_encodings, known_names, known_person_ids


def run_recognition(camera_index=0):
    """
    Opens the webcam and runs live face recognition + attendance marking
    until the user presses ESC.
    """
    known_encodings, known_names, known_person_ids = load_known_encodings()

    if not known_encodings:
        print("⚠️  No registered faces found. Please register at least one person first.")
        return

    video_capture = cv2.VideoCapture(camera_index)
    if not video_capture.isOpened():
        print("❌ Could not open webcam.")
        return

    # Keeps track of who we've already shown an "Attendance marked" message
    # for during THIS session, so we don't spam attempts every single frame.
    already_greeted_this_session = set()

    print("Starting recognition. Press ESC in the camera window to quit.")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            logger.error("Failed to read frame from webcam.")
            break

        # Resize frame to 1/4 size for faster face detection, then scale
        # coordinates back up later when drawing on the full-size frame.
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Scale coordinates back up to the original frame size
            top, right, bottom, left = top * 4, right * 4, bottom * 4, left * 4

            name_to_display = "Unknown"
            box_color = (0, 0, 255)  # red (BGR format)

            if known_encodings:
                distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_index = np.argmin(distances)

                if distances[best_match_index] <= MATCH_THRESHOLD:
                    name_to_display = known_names[best_match_index]
                    person_id = known_person_ids[best_match_index]
                    box_color = (0, 255, 0)  # green

                    marked, message = mark_attendance(person_id)

                    # Only print/log the first time we recognize this
                    # person in this session, to avoid flooding output.
                    if person_id not in already_greeted_this_session:
                        already_greeted_this_session.add(person_id)
                        if marked:
                            print(f"✅ {name_to_display}: {message}")
                            logger.info(f"{name_to_display}: {message}")
                        else:
                            print(f"ℹ️  {name_to_display}: {message}")

            # Draw the bounding box and name label
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
            cv2.rectangle(frame, (left, bottom - 25), (right, bottom), box_color, cv2.FILLED)
            cv2.putText(frame, name_to_display, (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

        cv2.putText(frame, "Press ESC to quit", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Smart Attendance System - Live Recognition", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break

    video_capture.release()
    cv2.destroyAllWindows()
    logger.info("Recognition session ended.")


if __name__ == "__main__":
    # Manual test: python -m Face_Recognition.face_matcher
    run_recognition()