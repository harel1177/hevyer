# Hevyer

Fetch your workout data from the [Hevy](https://hevy.com) fitness API, normalize it, and generate an AI-powered coaching report using OpenAI.

## Prerequisites

- Python 3.12+
- A [Hevy](https://hevy.com) account and API token
- An [OpenAI](https://platform.openai.com) API key

## Installation

```bash
git clone https://github.com/your-username/hevyer.git
cd hevyer
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
HEVY_API_TOKEN=your_hevy_api_token
OPENAI_API_KEY=your_openai_api_key
```

## Usage

```bash
# Generate a coaching report (prints to stdout)
.venv/bin/python main.py

# Use a different OpenAI model
.venv/bin/python main.py --model gpt-4o-mini

# Save the report to a file
.venv/bin/python main.py -o report.json

# Save raw and normalized workout data for inspection
.venv/bin/python main.py --save-workouts raw.json --save-normalized normalized.json
```

Run `.venv/bin/python main.py --help` for all options.

### Web UI (Streamlit)

```bash
.venv/bin/streamlit run app.py
```

This opens a browser with a sidebar to select the OpenAI model and a button to generate the report. The report is displayed in structured sections.

## Architecture

```
Hevy API → raw JSON → normalization → normalized JSON + prompt → OpenAI → coaching report
```

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point — orchestrates the full pipeline |
| `normalize2.py` | Transforms raw Hevy workout data into flat Pydantic models |
| `models/normalized_workout_model.py` | `NormalizedWorkout`, `Exercise`, and `ExerciseSet` Pydantic models |
| `app.py` | Streamlit web UI for generating and viewing reports |
| `prompt` | Prompt template for the AI coaching analysis |

## License

MIT
