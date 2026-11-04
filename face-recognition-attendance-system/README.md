# Face Recognition Attendance System

A privacy-conscious, local-first attendance prototype using OpenCV's LBPH face recognizer. It supports consent-based enrollment, camera-based recognition, duplicate check-in prevention, and CSV attendance export.

## Features
- Enroll a person from a set of face images with an explicit consent confirmation.
- Train an LBPH recognizer from the local enrollment dataset.
- Mark attendance from a webcam with a configurable confidence threshold.
- Prevent duplicate attendance entries for the same person on the same day.
- Export attendance as CSV.
- Keep biometric images and model files local; they are excluded from Git.

## Architecture
- `src/attendance/` — enrollment, recognition, persistence, and CLI.
- `data/` — local biometric data and generated model (gitignored).
- `tests/` — unit tests for attendance persistence.

## Quick start
Use Python 3.10–3.12.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Install `opencv-contrib-python` (included in requirements), because LBPH is in the contrib modules.

Enroll (collect images from a webcam):
```bash
python -m attendance enroll --person-id EMP001 --name "Alex" --consent
```

Train:
```bash
python -m attendance train
```

Run attendance:
```bash
python -m attendance mark
```

Export:
```bash
python -m attendance export --output attendance-export.csv
```

Run from the project directory with:
```bash
# Windows PowerShell
$env:PYTHONPATH="src"
# macOS/Linux
export PYTHONPATH=src
```

## Privacy and responsible use
- Obtain informed, documented consent before collecting or processing face images.
- Do not enroll people without their knowledge or use this for covert surveillance.
- Store biometric data securely, restrict access, define retention/deletion periods, and follow applicable privacy and employment laws.
- This prototype uses classical face recognition and is not a liveness/anti-spoofing system. A printed photo or replay attack may fool it.
- Recognition can be inaccurate across lighting, camera quality, pose, and demographic groups. Always provide a non-biometric attendance alternative and human review.
- Do not use this prototype for consequential decisions such as pay, discipline, or access denial without independent validation and appropriate safeguards.

## Limitations
This is a portfolio MVP, not a production attendance platform. It does not include liveness detection, encrypted biometric storage, role-based access control, or a web dashboard.

## License
MIT. See `LICENSE`.
