"""
Face_Recognition/face_encoder.py

Reads the face images captured by face_detector.py, generates a
128-dimensional face encoding for each one using the face_recognition
library, averages them into a single reliable encoding, saves it to
disk as a .pkl file, and registers the person in the 'persons' table.
"""

import os
import pickle

import face_recognition
import numpy as np

from Database.db_connection import execute_query, fetch_query
from Utils.logger import get_logger
from Utils.validators import is_valid_name, is_valid_roll_no, is_valid_email

logger = get_logger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FACES_FOLDER = os.path.join(PROJECT_ROOT, "Dataset", "raw_faces")
ENCODINGS_FOLDER = os.path.join(PROJECT_ROOT, "Dataset", "encodings")
os.makedirs(ENCODINGS_FOLDER, exist_ok=True)


def generate_encoding_from_folder(image_folder_path):
    """
    Reads every image in the given folder, detects the face, and
    generates an encoding for each one. Returns the AVERAGE of all
    valid encodings, which is more reliable than using just one photo.

    Returns:
        (True, numpy_array) on success
        (False, error_message) if no valid face was found in any image
    """
    encodings_found = []

    for filename in sorted(os.listdir(image_folder_path)):
        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        image_path = os.path.join(image_folder_path, filename)
        image = face_recognition.load_image_file(image_path)

        # face_encodings() returns a list (one per face found in the image).
        # We expect exactly one face per registration photo.
        face_locations = face_recognition.face_locations(image)
        if len(face_locations) == 0:
            logger.warning(f"No face found in {filename}, skipping.")
            continue

        encodings = face_recognition.face_encodings(image, known_face_locations=face_locations)
        if encodings:
            encodings_found.append(encodings[0])
            logger.info(f"Encoding generated from {filename}")

    if not encodings_found:
        return False, "No valid face could be encoded from the captured images."

    # Average all encodings into one representative vector for this person
    average_encoding = np.mean(encodings_found, axis=0)
    return True, average_encoding


def is_roll_no_registered(roll_no):
    """
    Quick check for whether a roll number already exists in the database.
    Used by the GUI to reject duplicates BEFORE opening the camera,
    so the user doesn't waste time capturing photos for a registration
    that will be rejected anyway.

    Returns:
        True if the roll number is already registered, False otherwise.
    """
    existing = fetch_query(
        "SELECT * FROM persons WHERE roll_no = ?", (roll_no,), fetch_one=True
    )
    return existing is not None


def register_person(roll_no, name, department, email, image_folder_path):
    """
    Full registration pipeline:
        1. Validate input fields
        2. Generate a face encoding from the captured images
        3. Save the encoding to Dataset/encodings/<roll_no>.pkl
        4. Insert the person's details into the 'persons' table

    Returns:
        (True, "Success message") on success
        (False, "Reason it failed") on failure
    """
    # --- Step 1: Validate inputs ---
    valid, error = is_valid_name(name)
    if not valid:
        return False, error

    valid, error = is_valid_roll_no(roll_no)
    if not valid:
        return False, error

    valid, error = is_valid_email(email)
    if not valid:
        return False, error

    # Check for duplicate roll number before doing any expensive work
    existing = fetch_query(
        "SELECT * FROM persons WHERE roll_no = ?", (roll_no,), fetch_one=True
    )
    if existing:
        return False, f"A person with roll number '{roll_no}' is already registered."

    # --- Step 2: Generate encoding ---
    success, result = generate_encoding_from_folder(image_folder_path)
    if not success:
        return False, result
    face_encoding = result

    # --- Step 3: Save encoding to disk ---
    encoding_filename = f"{roll_no}.pkl"
    encoding_path = os.path.join(ENCODINGS_FOLDER, encoding_filename)
    with open(encoding_path, "wb") as f:
        pickle.dump(face_encoding, f)
    logger.info(f"Encoding saved to {encoding_path}")

    # --- Step 4: Insert into database ---
    new_id = execute_query(
        """
        INSERT INTO persons (name, roll_no, department, email, encoding_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name.strip(), roll_no.strip(), department.strip(), email.strip(), encoding_path),
    )

    if new_id is None:
        return False, "Database error while registering person."

    logger.info(f"Person registered successfully: {name} ({roll_no})")
    return True, f"{name} registered successfully with ID {new_id}."


if __name__ == "__main__":
    # Manual test: python -m Face_Recognition.face_encoder
    # Uses the TEST001_Hasini folder captured in the previous step.
    print("=== Face Encoding + Registration Test ===")

    test_roll_no = input("Enter the roll number used during capture (e.g. TEST001): ").strip()
    test_name = input("Enter the name used during capture (e.g. Hasini): ").strip()
    test_department = input("Enter department (e.g. CSE): ").strip()
    test_email = input("Enter email (optional, press Enter to skip): ").strip()

    safe_name = test_name.replace(" ", "_")
    folder_path = os.path.join(RAW_FACES_FOLDER, f"{test_roll_no}_{safe_name}")

    if not os.path.exists(folder_path):
        print(f"\n❌ Folder not found: {folder_path}")
        print("Make sure you ran face_detector.py first with the same roll number and name.")
    else:
        success, message = register_person(
            test_roll_no, test_name, test_department, test_email, folder_path
        )
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")