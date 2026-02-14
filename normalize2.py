from datetime import datetime

from hevy_api_wrapper.models import PaginatedWorkouts, Workout

from models.normalized_workout_model import Exercise, ExerciseSet, NormalizedWorkout


def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def normalize_workout(workout: Workout) -> NormalizedWorkout:
    workout_timedelta = parse_iso(workout.end_time) - parse_iso(workout.start_time)

    exercises = [
        Exercise(
            title=exercise.title,
            sets=[ExerciseSet(**s.model_dump()) for s in exercise.sets],
        )
        for exercise in workout.exercises
    ]

    return NormalizedWorkout(
        title=workout.title,
        start_time=workout.start_time,
        timedelta=workout_timedelta,
        exercises=exercises,
    )


def normalize_workouts(workouts: PaginatedWorkouts) -> list[NormalizedWorkout]:
    return [normalize_workout(workout) for workout in workouts.workouts]
