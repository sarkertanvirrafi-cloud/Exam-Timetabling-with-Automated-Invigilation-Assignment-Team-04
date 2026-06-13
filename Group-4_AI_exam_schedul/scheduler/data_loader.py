from __future__ import annotations
from pathlib import Path
import pandas as pd

REQUIRED_FILES = {
    'students': 'students.csv',
    'courses': 'courses.csv',
    'enrollments': 'enrollments.csv',
    'teachers': 'teachers.csv',
    'course_teachers': 'course_teachers.csv',
    'rooms': 'rooms.csv',
    'timeslots': 'timeslots.csv',
    'teacher_availability': 'teacher_availability.csv',
    'invigilation_rules': 'invigilation_rules.csv',
}
class DatasetError(Exception):
    pass

def load_dataset(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    data_dir = Path(data_dir)
    dfs: dict[str, pd.DataFrame] = {}
    missing = []
    for key, filename in REQUIRED_FILES.items():
        path = data_dir / filename
        if not path.exists():
            missing.append(filename)
        else:
            dfs[key] = pd.read_csv(path).fillna('')
    if missing:
        raise DatasetError(f"Missing required CSV files: {', '.join(missing)}")
    _normalize(dfs)
    return dfs

