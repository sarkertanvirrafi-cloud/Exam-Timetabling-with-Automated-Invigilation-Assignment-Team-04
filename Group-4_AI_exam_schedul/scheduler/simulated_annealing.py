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


