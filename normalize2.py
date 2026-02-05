import json

from hevy_api_wrapper.models import Workout, PaginatedWorkouts
from datetime import datetime, timedelta
from pathlib import Path
from models.normalaized_workout_model import Exercise, ExerciseSet, NormalizedWorkout
from typing import List


# get sample data
data = PaginatedWorkouts.model_validate_json(Path('workouts.json').read_text())

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

test_workout = normalize_workouts(data)
test_workout_json = [w.model_dump_json() for w in test_workout]
# with open('normalized_workout.json', 'w') as f:
#     json.dump(test_workout_json, f)
# Path('normalized_workout.json').write_text(json.dump(test_workout, f))
print(test_workout)
print(test_workout_json)