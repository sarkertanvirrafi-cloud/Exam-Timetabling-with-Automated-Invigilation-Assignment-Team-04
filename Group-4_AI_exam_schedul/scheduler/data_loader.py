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

def _normalize(dfs: dict[str, pd.DataFrame]) -> None:
    for df in dfs.values():
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].astype(str).str.strip()
                

    for col in ['year_level', 'credit', 'exam_duration_hours']:
        if col in dfs['courses'].columns:
            dfs['courses'][col] = pd.to_numeric(dfs['courses'][col], errors='coerce').fillna(0).astype(int)
    dfs['rooms']['capacity'] = pd.to_numeric(dfs['rooms']['capacity'], errors='coerce').fillna(0).astype(int)
    dfs['teachers']['max_duties'] = pd.to_numeric(dfs['teachers']['max_duties'], errors='coerce').fillna(0).astype(int)
    dfs['teacher_availability']['available'] = pd.to_numeric(dfs['teacher_availability']['available'], errors='coerce').fillna(0).astype(int)
    dfs['invigilation_rules']['required_invigilators'] = pd.to_numeric(
        dfs['invigilation_rules']['required_invigilators'], errors='coerce'
    ).fillna(1).astype(int)

