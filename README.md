# AI-Based Smart Attendance Management System Using Facial Recognition

![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.9-5C3EE8?logo=opencv&logoColor=white)
![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41CD52?logo=qt&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?logo=sqlite&logoColor=white)

A desktop application that marks attendance automatically by recognizing faces through a webcam. It replaces manual roll calls and proxy attendance with a quick, contactless check-in, and gives administrators a secure dashboard to register people, run live attendance sessions and export reports.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [First-Time Setup](#first-time-setup)
- [Usage](#usage)
- [Configuration](#configuration)
- [Limitations](#limitations)
- [Future Enhancements](#future-enhancements)
- [Privacy Note](#privacy-note)
- [Author](#author)

---

## Features

- **Secure admin login**: passwords are hashed with bcrypt and never stored in plain text.
- **Face registration**: captures 5 photos per person and averages them into one 128-dimensional encoding for more reliable matching.
- **Live attendance**: real-time face detection and recognition with the camera feed embedded in the application window.
- **Duplicate prevention**: attendance is marked only once per person per day.
- **Reports**: view attendance records inside the app and export them to **Excel (.xlsx)** or **PDF**.
- **Input validation**: name, roll number, email and credentials are validated before reaching the database.
- **Logging**: application events and failed login attempts are written to `logs/app.log`.
- **Polished UI**: custom QSS theme, splash screen and app icon.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10 |
| Face detection and recognition | OpenCV, `face_recognition` (dlib, 128-D face encodings) |
| GUI | PyQt5 with a custom QSS stylesheet |
| Database | SQLite |
| Security | bcrypt |
| Reports | openpyxl (Excel), ReportLab (PDF) |
| Numerical processing | NumPy |

## How It Works

**1. Registration**

```
Webcam -> capture 5 face images -> 128-D encoding per image -> average -> save as .pkl
                                                                  |
                                      person details -> SQLite (persons table)
```

**2. Taking attendance**

```
Webcam frame -> detect faces -> encode -> compare with stored encodings (Euclidean distance)
        -> distance <= 0.6 ? identified : "Unknown"
        -> already marked today? skip : insert record into attendance table
```

A face is accepted as a match when its Euclidean distance to the closest stored encoding is **at most 0.6**, the standard threshold for the dlib face model.

## Project Structure

```
smart_attendance_system/
├── main.py                    # Entry point: splash screen, DB init, launches login
├── requirements.txt
├── Assets/
│   ├── icons/                 # Application icon
│   └── style/style.qss        # Global Qt stylesheet
├── GUI/
│   ├── login_window.py        # Admin login
│   ├── main_window.py         # Dashboard
│   ├── registration_window.py # Register a new person (webcam capture)
│   ├── attendance_window.py   # Live recognition and attendance marking
│   └── reports_window.py      # View and export reports
├── Face_Recognition/
│   ├── face_detector.py       # Webcam capture of face images
│   ├── face_encoder.py        # Builds and saves 128-D encodings
│   └── face_matcher.py        # Loads encodings and matches faces
├── Attendance/
│   └── attendance_manager.py  # Mark attendance, once-per-day check
├── Database/
│   └── db_connection.py       # SQLite connection, table creation, query helpers
├── Models/
│   ├── person.py
│   └── attendance_record.py
├── Reports/
│   ├── report_generator.py    # Queries for date-range / full reports
│   └── export_utils.py        # Excel and PDF export
├── Utils/
│   ├── auth_manager.py        # bcrypt hashing, admin creation, login check
│   ├── validators.py          # Input validation
│   ├── logger.py              # Central logging setup
│   ├── camera_utils.py
│   └── ui_helpers.py
├── Dataset/                   # Created at runtime
│   ├── raw_faces/             # Captured images, one folder per person
│   ├── encodings/             # Saved .pkl encodings
│   └── attendance_logs/       # Exported reports
└── logs/                      # Application log files
```

## Database Schema

SQLite database stored at `Database/attendance.db`, created automatically on first run.

| Table | Columns |
|---|---|
| `persons` | `person_id` (PK), `name`, `roll_no` (unique), `department`, `email`, `encoding_path`, `registered_on` |
| `attendance` | `attendance_id` (PK), `person_id` (FK), `date`, `time_in`, `status` |
| `admin_users` | `admin_id` (PK), `username` (unique), `password_hash`, `role` |

## Installation

### Prerequisites

- **Python 3.10** (the version this project was developed and tested on)
- A working **webcam**
- Windows is recommended. `dlib-bin` provides a prebuilt dlib, so no C++ compiler is needed.

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/hasini158/<your-repo-name>.git
cd <your-repo-name>

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt
```

> If pip reports an encoding error while reading `requirements.txt`, re-save the file as UTF-8 and run the command again.

## First-Time Setup

The application needs at least one admin account before you can log in. Create the default one with:

```bash
python Utils/auth_manager.py
```

This creates the admin account **`admin`** with the password **`admin123`**.

> **Change this password** before using the system anywhere other than on your own machine.

## Usage

```bash
python main.py
```

1. **Log in** with your admin credentials.
2. **Register New Person**: enter name, roll number, department and email, then capture 5 photos with the webcam (face the camera in good light, with slight changes of angle between shots).
3. **Take Attendance**: start the live session. Registered people are recognized automatically and marked present once per day.
4. **View Reports**: browse attendance records, then use **Export to Excel** or **Export to PDF**. Exported files are saved in `Dataset/attendance_logs/`.

### Input rules

| Field | Rule |
|---|---|
| Name | Letters and spaces only |
| Roll number / ID | Required, no spaces, must be unique |
| Email | Optional, must be a valid format if given |
| Admin username | At least 4 characters |
| Admin password | At least 6 characters |

## Configuration

| Setting | Location | Default |
|---|---|---|
| Match threshold (lower is stricter) | `MATCH_THRESHOLD` in `Face_Recognition/face_matcher.py` | `0.6` |
| Photos captured per person | `NUM_IMAGES_TO_CAPTURE` in `GUI/registration_window.py` and `Face_Recognition/face_detector.py` | `5` |
| Theme | `Assets/style/style.qss` | Custom dark-blue theme |

## Limitations

- **No liveness detection**: a printed photo or a screen may fool the system.
- Accuracy drops in **poor lighting**.
- Recognition is **less reliable when many faces appear at once**.
- **Single-machine only**: the database and encodings are stored locally.

## Future Enhancements

- Liveness / anti-spoofing detection (blink or depth checks)
- Multi-camera and multi-face optimization
- Cloud or networked database for multi-device use
- Role-based access, such as teacher and admin roles
- Email or SMS notifications for absentees
- Analytics dashboard with attendance trends

## Privacy Note

Face images and encodings are biometric data. Keep `Dataset/raw_faces/`, `Dataset/encodings/` and `Database/attendance.db` out of version control, and register only people who have given their consent.

## Author

**Gottimukula Hasini**
B.Tech, Computer Science and Engineering (Data Science)
Geethanjali College of Engineering and Technology

[GitHub](https://github.com/hasini158) | [LinkedIn](https://www.linkedin.com/in/hasini-gottimukula)

---

*Developed as a B.Tech mini project.*
