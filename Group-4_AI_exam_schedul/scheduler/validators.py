from __future__ import annotations
from itertools import combinations
import pandas as pd

def validate_all(
    timetable: pd.DataFrame,
    room_allocations: pd.DataFrame,
    invigilation_roster: pd.DataFrame,
    dfs: dict[str, pd.DataFrame],
) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {
        'student_conflicts': [],
        'room_conflicts': [],
        'room_capacity': [],
        'invigilation': [],
    }
    
    slot_by_course = dict(zip(timetable['course_id'], timetable['timeslot_id']))

    for student_id, group in dfs['enrollments'].groupby('student_id'):
        courses = list(group['course_id'])
        seen = {}
        for course in courses:
            slot = slot_by_course.get(course)
            if not slot:
                continue
            if slot in seen:
                errors['student_conflicts'].append(f'{student_id}: {seen[slot]} and {course} both at {slot}')
            else:
                seen[slot] = course


    for (slot, room), group in room_allocations.groupby(['timeslot_id', 'room_id']):
        if len(group) > 1:
            errors['room_conflicts'].append(f'Room {room} used {len(group)} times at {slot}')

    for row in room_allocations.itertuples(index=False):
        if int(row.student_count) > int(row.room_capacity):
            errors['room_capacity'].append(f'{row.course_id}: {row.student_count}>{row.room_capacity}')

    course_teachers = dfs['course_teachers'].groupby('course_id')['teacher_id'].apply(set).to_dict()
    available = {(r.teacher_id, r.timeslot_id): int(r.available) == 1 for r in dfs['teacher_availability'].itertuples(index=False)}
    teacher_max = dict(zip(dfs['teachers']['teacher_id'], dfs['teachers']['max_duties']))
    teacher_busy = set()
    teacher_load = {tid: 0 for tid in teacher_max}

    
    for row in invigilation_roster.itertuples(index=False):
        invigs = [getattr(row, c) for c in ['invigilator_1', 'invigilator_2', 'invigilator_3'] if getattr(row, c, '')]
        if len(invigs) < int(row.required_invigilators):
            errors['invigilation'].append(f'{row.course_id}: missing invigilator(s)')
        for tid in invigs:
            if tid in course_teachers.get(row.course_id, set()):
                errors['invigilation'].append(f'{tid} invigilates own course {row.course_id}')
            if not available.get((tid, row.timeslot_id), False):
                errors['invigilation'].append(f'{tid} unavailable at {row.timeslot_id}')
            if (tid, row.timeslot_id) in teacher_busy:
                errors['invigilation'].append(f'{tid} has duplicate duty at {row.timeslot_id}')
            teacher_busy.add((tid, row.timeslot_id))
            teacher_load[tid] = teacher_load.get(tid, 0) + 1

    
    for tid, load in teacher_load.items():
        if load > int(teacher_max.get(tid, 0)):
            errors['invigilation'].append(f'{tid}: {load}>{teacher_max.get(tid)} duties')
    return errors


def error_count(errors: dict[str, list[str]]) -> int:
    return sum(len(v) for v in errors.values())


