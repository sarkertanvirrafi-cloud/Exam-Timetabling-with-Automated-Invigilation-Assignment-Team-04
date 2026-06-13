from __future__ import annotations
import math
import random
import pandas as pd


class AnnealingResult(dict):
    pass
    
def _score(schedule: dict[str, str], graph: dict[str, set[str]], enrollments: pd.DataFrame, timeslots: pd.DataFrame) -> int:
    # Hard conflict penalty: very high
    penalty = 0
    for c, neighbors in graph.items():
        for n in neighbors:
            if c < n and schedule.get(c) == schedule.get(n):
                penalty += 1_000_000
                
    slot_day = dict(zip(timeslots['timeslot_id'], timeslots['date']))
    slot_name = dict(zip(timeslots['timeslot_id'], timeslots['slot_name']))

    # Soft penalty: a student having multiple exams on same date is allowed but discouraged.
    for _, group in enrollments.groupby('student_id'):
        by_day: dict[str, int] = {}
        for c in group['course_id']:
            slot = schedule.get(c)
            if slot:
                by_day[slot_day.get(slot, '')] = by_day.get(slot_day.get(slot, ''), 0) + 1
        for count in by_day.values():
            if count > 1:
                penalty += (count - 1) * 10

    # Soft penalty: too many morning exams.
    for slot in schedule.values():
        if str(slot_name.get(slot, '')).lower() == 'morning':
            penalty += 1
    return penalty
    
def optimize_schedule(
    initial_schedule: dict[str, str],
    graph: dict[str, set[str]],
    enrollments: pd.DataFrame,
    timeslots: pd.DataFrame,
    iterations: int = 8000,
    initial_temp: float = 100.0,
    cooling_rate: float = 0.995,
    seed: int = 42,
) -> dict[str, str]:
    """Improve DSATUR output without breaking hard conflicts."""
    random.seed(seed)
    slots = list(timeslots['timeslot_id'])
    current = dict(initial_schedule)
    current_score = _score(current, graph, enrollments, timeslots)
    best = dict(current)
    best_score = current_score
    courses = list(current.keys())
    temp = initial_temp
    
for _ in range(iterations):
        course = random.choice(courses)
        old_slot = current[course]
        new_slot = random.choice(slots)
        if new_slot == old_slot:
            continue
            
 # Keep hard conflict feasibility as much as possible.
        if any(current.get(n) == new_slot for n in graph.get(course, [])):
            continue
            
        current[course] = new_slot
        new_score = _score(current, graph, enrollments, timeslots)
        delta = new_score - current_score
        if delta <= 0 or random.random() < math.exp(-delta / max(temp, 1e-9)):
            current_score = new_score
            if new_score < best_score:
                best = dict(current)
                best_score = new_score
