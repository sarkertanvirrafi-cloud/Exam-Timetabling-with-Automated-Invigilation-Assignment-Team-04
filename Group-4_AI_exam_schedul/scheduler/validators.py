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


    
