from hevy_api_wrapper.models import Workout, PaginatedWorkouts
from datetime import datetime
from models.normalized_workout_model import Exercise, ExerciseSet, NormalizedWorkout
from typing import List


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))

def normalize_workout(workout: Workout) -> NormalizedWorkout:
    workout_timedelta =  parse_iso(workout.end_time) - parse_iso(workout.start_time)

    exercises = []
    for i in range(len(workout.exercises)):
        exercise: Exercise = Exercise(**{
            'title': workout.exercises[i].title,
            'sets': [ExerciseSet(**workout.exercises[i].sets[l].model_dump()) for l in range(len(workout.exercises[i].sets))]
        })
        exercises.append(exercise)
    normalized_workout = {
        'title': workout.title,
        'start_time': workout.start_time,
        'timedelta': workout_timedelta,
        'exercises': exercises
    }
    return NormalizedWorkout(**normalized_workout)

def normalize_workouts(workouts: PaginatedWorkouts) -> List[NormalizedWorkout]:
    return [normalize_workout(workout) for workout in workouts.workouts]

