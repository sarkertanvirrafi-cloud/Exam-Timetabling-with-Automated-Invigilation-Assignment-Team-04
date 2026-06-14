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

for course_id, slot_id in sorted(schedule.items()):
        student_count = int(counts.get(course_id, 0))
        exam_type = str(course_meta.get(course_id, {}).get('exam_type', '')).lower()
        candidates = []
for room in room_rows:
            room_id = room['room_id']
            if (slot_id, room_id) in used:
                continue
            if int(room['capacity']) < student_count:
                continue
            # If practical/lab appears, prefer lab-like rooms, otherwise allow all rooms.
            room_type = str(room.get('room_type', '')).lower()
            if 'lab' in exam_type and 'lab' not in room_type:
                continue
            candidates.append(room)
        if not candidates:
         raise ValueError(f'No available room for {course_id} at {slot_id} with {student_count} students.')
        chosen = candidates[0]
        used.add((slot_id, chosen['room_id']))
        allocations.append({
            'course_id': course_id,
            'timeslot_id': slot_id,
            'room_id': chosen['room_id'],
            'room_name': chosen['room_name'],
            'student_count': student_count,
            'room_capacity': int(chosen['capacity']),
       })
  return pd.DataFrame(allocations)
