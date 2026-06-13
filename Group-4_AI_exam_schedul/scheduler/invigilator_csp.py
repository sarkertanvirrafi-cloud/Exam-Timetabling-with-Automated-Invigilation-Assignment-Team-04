from __future__ import annotations
from collections import defaultdict
import pandas as pd

class InvigilationError(Exception):
    pass
def assign_invigilators(
    room_allocations: pd.DataFrame,
    teachers: pd.DataFrame,
    course_teachers: pd.DataFrame,
    teacher_availability: pd.DataFrame,
    invigilation_rules: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
teacher_ids = list(teachers['teacher_id'])
    max_duties = dict(zip(teachers['teacher_id'], teachers['max_duties']))
    own_courses = course_teachers.groupby('teacher_id')['course_id'].apply(set).to_dict()
    course_teacher_set = course_teachers.groupby('course_id')['teacher_id'].apply(set).to_dict()
    available = {
        (r.teacher_id, r.timeslot_id): int(r.available) == 1
        for r in teacher_availability.itertuples(index=False)
    }
    req = dict(zip(invigilation_rules['room_id'], invigilation_rules['required_invigilators']))

    duties = defaultdict(int)
    busy = set()  # (teacher_id, timeslot_id)
    rows = []
