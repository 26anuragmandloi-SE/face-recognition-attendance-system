"""OpenCV enrollment and LBPH recognition."""
from __future__ import annotations
import cv2
import numpy as np
from pathlib import Path
import json

FACE_SIZE = (200, 200)

def _face_detector():
    path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(path)
    if detector.empty():
        raise RuntimeError("OpenCV face detector could not be loaded.")
    return detector

def capture_enrollment(person_id: str, name: str, data_dir: Path, consent: bool,
                       samples: int = 25) -> int:
    if not consent:
        raise ValueError("Explicit consent is required before face enrollment.")
    if not person_id.strip() or not name.strip():
        raise ValueError("Person ID and name are required.")
    root = Path(data_dir) / "faces" / person_id
    root.mkdir(parents=True, exist_ok=True)
    (root / "profile.json").write_text(
        json.dumps({"person_id": person_id, "name": name}, indent=2), encoding="utf-8"
    )
    detector = _face_detector()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Webcam could not be opened.")
    saved = 0
    try:
        print("Look at the camera. Press q to stop early.")
        while saved < samples:
            ok, frame = camera.read()
            if not ok:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.2, 5, minSize=(80, 80))
            for (x, y, w, h) in faces[:1]:
                face = cv2.resize(gray[y:y+h, x:x+w], FACE_SIZE)
                cv2.imwrite(str(root / f"{saved:03d}.png"), face)
                saved += 1
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 220, 0), 2)
                cv2.putText(frame, f"Captured {saved}/{samples}", (x, y-10),
                            cv2.FONT_HERSHEY_SIMPLEX, .6, (0, 220, 0), 2)
            cv2.imshow("Consent-based enrollment", frame)
            if cv2.waitKey(150) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
    return saved

def train_model(data_dir: Path) -> Path:
    data_dir = Path(data_dir)
    images, labels, label_map = [], [], {}
    for idx, folder in enumerate(sorted((data_dir / "faces").glob("*"))):
        if not folder.is_dir():
            continue
        profile = folder / "profile.json"
        if not profile.exists():
            continue
        meta = json.loads(profile.read_text(encoding="utf-8"))
        files = sorted(folder.glob("*.png"))
        for file in files:
            image = cv2.imread(str(file), cv2.IMREAD_GRAYSCALE)
            if image is not None:
                images.append(cv2.resize(image, FACE_SIZE))
                labels.append(idx)
        if files:
            label_map[str(idx)] = {"person_id": meta["person_id"], "name": meta["name"]}
    if len(set(labels)) < 2:
        raise RuntimeError("Enroll at least two people before training the LBPH model.")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels, dtype=np.int32))
    model_dir = data_dir / "models"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "attendance.yml"
    recognizer.write(str(model_path))
    (model_dir / "labels.json").write_text(json.dumps(label_map, indent=2), encoding="utf-8")
    return model_path

def run_recognition(data_dir: Path, store, threshold: float = 65.0) -> None:
    data_dir = Path(data_dir)
    model_path = data_dir / "models" / "attendance.yml"
    labels_path = data_dir / "models" / "labels.json"
    if not model_path.exists() or not labels_path.exists():
        raise RuntimeError("Train the model first: python -m attendance train")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(model_path))
    labels = json.loads(labels_path.read_text(encoding="utf-8"))
    detector = _face_detector()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        raise RuntimeError("Webcam could not be opened.")
    print("Press q to quit. Recognition is advisory; verify attendance manually.")
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            for (x, y, w, h) in detector.detectMultiScale(gray, 1.2, 5, minSize=(80, 80)):
                face = cv2.resize(gray[y:y+h, x:x+w], FACE_SIZE)
                label, confidence = recognizer.predict(face)
                match = labels.get(str(label)) if confidence <= threshold else None
                if match:
                    added = store.mark(match["person_id"], match["name"])
                    status = "Marked" if added else "Already marked"
                    text = f'{match["name"]}: {status} ({confidence:.1f})'
                    color = (0, 200, 0)
                else:
                    text, color = f"Unknown ({confidence:.1f})", (0, 0, 220)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, .55, color, 2)
            cv2.imshow("Attendance - press q to quit", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
