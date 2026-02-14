# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Hevyer is a Python tool that fetches workout data from the Hevy fitness API, normalizes it, sends it with a coaching prompt to an AI model, and generates a workout report.

## Setup & Commands

```bash
# Install dependencies (use the project venv)
.venv/bin/pip install -r requirements.txt

# Run the full pipeline (requires .env with HEVY_API_TOKEN and OPENAI_API_KEY)
.venv/bin/python main.py

# See all CLI options
.venv/bin/python main.py --help

# Run the Streamlit web UI
.venv/bin/streamlit run app.py
```

There is no formal test framework, linter, or build system configured.

## Architecture

**Pipeline:** Hevy API → raw JSON → normalization → normalized JSON + prompt → AI model → workout report

- **main.py** — CLI entry point and pipeline functions (`fetch_workouts`, `build_report`). Supports `--model`, `--output`, `--save-workouts`, and `--save-normalized` flags.
- **app.py** — Streamlit web UI that calls the pipeline functions and displays the coaching report in structured sections.
- **normalize2.py** — Transforms raw workout data into `NormalizedWorkout` Pydantic models (flattening exercises and sets, computing duration as a timedelta).
- **models/normalized_workout_model.py** — `NormalizedWorkout`, `Exercise`, and `ExerciseSet` Pydantic models.
- **prompt** — A detailed prompt template instructing an AI to analyze normalized workout data as a strength training coach (progression, fatigue, exercise selection).

## Key Libraries

- **pydantic** — All data models use Pydantic v2 (`model_validate_json`, `model_dump_json`, `model_dump`)
- **hevy_api_wrapper** — External package providing `Client`, `Workout`, and `PaginatedWorkouts` models
- **python-dotenv** — Loads API credentials from `.env` file
- **openai** — OpenAI API client for generating coaching reports

## Notes

- API credentials are loaded from a `.env` file via `load_dotenv()` and `Client.from_env()`.
- Logging goes to stderr; the report goes to stdout (or a file with `-o`).
