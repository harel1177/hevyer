from datetime import timedelta
from typing import List, Optional

from pydantic import BaseModel


class ExerciseSet(BaseModel):
    weight_kg: Optional[float] = None
    reps: Optional[int] = None


class Exercise(BaseModel):
    title: str
    sets: List[ExerciseSet]


class NormalizedWorkout(BaseModel):
    title: str
    start_time: str
    timedelta: timedelta
    exercises: List[Exercise]
