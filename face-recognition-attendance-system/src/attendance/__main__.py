from __future__ import annotations
import argparse
from pathlib import Path
from .storage import AttendanceStore
from .vision import capture_enrollment, train_model, run_recognition

def main():
    parser = argparse.ArgumentParser(description="Consent-based face attendance prototype")
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    sub = parser.add_subparsers(dest="command", required=True)
    enroll = sub.add_parser("enroll")
    enroll.add_argument("--person-id", required=True)
    enroll.add_argument("--name", required=True)
    enroll.add_argument("--consent", action="store_true")
    enroll.add_argument("--samples", type=int, default=25)
    sub.add_parser("train")
    mark = sub.add_parser("mark")
    mark.add_argument("--threshold", type=float, default=65.0)
    export = sub.add_parser("export")
    export.add_argument("--output", type=Path, default=Path("attendance-export.csv"))
    args = parser.parse_args()
    if args.command == "enroll":
        count = capture_enrollment(args.person_id, args.name, args.data_dir, args.consent, args.samples)
        print(f"Captured {count} samples.")
    elif args.command == "train":
        print(f"Model saved to {train_model(args.data_dir)}")
    elif args.command == "mark":
        run_recognition(args.data_dir, AttendanceStore(args.data_dir / "attendance.csv"), args.threshold)
    elif args.command == "export":
        print(f"Exported {AttendanceStore(args.data_dir / 'attendance.csv').export(args.output)} records.")

if __name__ == "__main__":
    main()
