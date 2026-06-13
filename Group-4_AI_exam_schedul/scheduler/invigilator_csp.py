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

exams = room_allocations.copy()
    exams['required_invigilators'] = exams['room_id'].map(req).fillna(1).astype(int)
    exams = exams.sort_values(['required_invigilators', 'student_count'], ascending=[False, False])

    for exam in exams.to_dict('records'):
        course_id = exam['course_id']
        slot_id = exam['timeslot_id']
        required = int(exam['required_invigilators'])
        assigned: list[str] = []

        candidates = []
        for tid in teacher_ids:
            if tid in course_teacher_set.get(course_id, set()):
                continue
            if course_id in own_courses.get(tid, set()):
                continue
            if not available.get((tid, slot_id), False):
                continue
            if (tid, slot_id) in busy:
                continue
            if duties[tid] >= int(max_duties.get(tid, 0)):
                continue
            candidates.append(tid)

candidates.sort(key=lambda t: (duties[t], t))
        assigned = candidates[:required]
        if len(assigned) < required:
            raise InvigilationError(
                f'Could not assign {required} invigilators for {course_id} at {slot_id}. Found {len(assigned)}.'
            )

        for tid in assigned:
            busy.add((tid, slot_id))
            duties[tid] += 1
rows.append({
            'course_id': course_id,
            'timeslot_id': slot_id,
            'room_id': exam['room_id'],
            'required_invigilators': required,
            'invigilator_1': assigned[0] if len(assigned) > 0 else '',
            'invigilator_2': assigned[1] if len(assigned) > 1 else '',
            'invigilator_3': assigned[2] if len(assigned) > 2 else '',
        })
roster = pd.DataFrame(rows).sort_values(['timeslot_id', 'course_id'])
    load = teachers[['teacher_id', 'teacher_name', 'dept_code', 'max_duties']].copy()
    load['total_duties'] = load['teacher_id'].map(duties).fillna(0).astype(int)
    load = load[['teacher_id', 'teacher_name', 'dept_code', 'total_duties', 'max_duties']]
    return roster, load
