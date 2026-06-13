from __future__ import annotations
from itertools import combinations
import pandas as pd

def validate_all(
    timetable: pd.DataFrame,
    room_allocations: pd.DataFrame,
    invigilation_roster: pd.DataFrame,
    dfs: dict[str, pd.DataFrame],
