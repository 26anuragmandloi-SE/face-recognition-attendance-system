from datetime import datetime
from attendance.storage import AttendanceStore

def test_prevents_duplicate_same_day(tmp_path):
    store = AttendanceStore(tmp_path / "attendance.csv")
    moment = datetime(2026, 1, 2, 9, 0)
    assert store.mark("E01", "Asha", moment) is True
    assert store.mark("E01", "Asha", moment) is False
    assert len(store.read()) == 1

def test_allows_different_people(tmp_path):
    store = AttendanceStore(tmp_path / "attendance.csv")
    moment = datetime(2026, 1, 2, 9, 0)
    assert store.mark("E01", "Asha", moment)
    assert store.mark("E02", "Ravi", moment)
    assert len(store.read()) == 2
