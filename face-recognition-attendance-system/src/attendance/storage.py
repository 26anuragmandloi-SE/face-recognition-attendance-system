"""CSV-backed attendance storage."""
from __future__ import annotations
import csv
from datetime import datetime, date
from pathlib import Path

FIELDS = ["person_id", "name", "timestamp", "date"]

class AttendanceStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def mark(self, person_id: str, name: str, at: datetime | None = None) -> bool:
        at = at or datetime.now().astimezone()
        rows = self.read()
        if any(r["person_id"] == person_id and r["date"] == at.date().isoformat() for r in rows):
            return False
        new_row = {
            "person_id": person_id,
            "name": name,
            "timestamp": at.isoformat(timespec="seconds"),
            "date": at.date().isoformat(),
        }
        exists = self.path.exists()
        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            if not exists:
                writer.writeheader()
            writer.writerow(new_row)
        return True

    def read(self) -> list[dict[str, str]]:
        if not self.path.exists():
            return []
        with self.path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def export(self, output: Path) -> int:
        rows = self.read()
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        return len(rows)
