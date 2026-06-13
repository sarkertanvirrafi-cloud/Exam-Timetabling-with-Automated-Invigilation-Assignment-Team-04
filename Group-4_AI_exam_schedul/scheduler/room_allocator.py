from __future__ import annotations
import pandas as pd

def allocate_rooms(
    schedule: dict[str, str],
    courses: pd.DataFrame,
    enrollments: pd.DataFrame,
    rooms: pd.DataFrame,
) -> pd.DataFrame:
    counts = enrollments.groupby('course_id')['student_id'].nunique().to_dict()
    course_meta = courses.set_index('course_id').to_dict('index')
    used: set[tuple[str, str]] = set()
    room_rows = rooms.sort_values(['capacity', 'room_id']).to_dict('records')
    allocations = []
