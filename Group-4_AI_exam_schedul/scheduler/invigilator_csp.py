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
