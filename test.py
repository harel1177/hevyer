from dotenv import load_dotenv
import os
from normalize2 import normalize_workouts
from hevy_api_wrapper.models import Workout, PaginatedWorkouts
import json
from hevy_api_wrapper import Client
from  pathlib import Path

load_dotenv()  # Load variables from .env into the environment
with Client.from_env() as client:
    workouts: PaginatedWorkouts = client.workouts.get_workouts()
    Path('workouts').write_text(workouts.model_dump_json())
    workout: Workout = workouts.workouts[0]
    print(workouts)
    print(workout)
    print(len(workouts.workouts))
    print('test.py')

# normalized_workouts = normalize_workouts(workouts.workouts)
# print(normalized_workouts)
#
# with open('workouts', 'r') as f:
#     print('opened')
#     data = json.loads(f)
#     print(type(data))