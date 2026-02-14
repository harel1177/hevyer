import argparse
import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from hevy_api_wrapper import Client
from openai import OpenAI

from normalize2 import normalize_workouts

log = logging.getLogger("hevyer")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch workouts from Hevy, normalize them, and generate an AI coaching report.",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o",
        help="OpenAI model to use (default: gpt-4o)",
    )
    parser.add_argument(
        "-o", "--output",
        help="Write the report to a file instead of stdout",
    )
    parser.add_argument(
        "--save-workouts",
        help="Save raw workout JSON to a file",
    )
    parser.add_argument(
        "--save-normalized",
        help="Save normalized workout JSON to a file",
    )
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    args = parse_args()
    load_dotenv()

    # Check required env vars early
    missing = [v for v in ("HEVY_API_TOKEN", "OPENAI_API_KEY") if not os.getenv(v)]
    if missing:
        log.error("Missing required environment variables: %s", ", ".join(missing))
        log.error("Set them in a .env file or export them in your shell.")
        sys.exit(1)

    # Fetch workouts from Hevy API
    log.info("Fetching workouts from Hevy API...")
    try:
        with Client.from_env() as client:
            workouts = client.workouts.get_workouts()
    except Exception as exc:
        log.error("Failed to fetch workouts from Hevy API: %s", exc)
        sys.exit(1)

    if args.save_workouts:
        Path(args.save_workouts).write_text(workouts.model_dump_json(indent=2))
        log.info("Raw workouts saved to %s", args.save_workouts)

    # Normalize workouts
    log.info("Normalizing %d workouts...", len(workouts.workouts))
    normalized = normalize_workouts(workouts)
    normalized_json = json.dumps([w.model_dump(mode="json") for w in normalized], indent=2)

    if args.save_normalized:
        Path(args.save_normalized).write_text(normalized_json)
        log.info("Normalized workouts saved to %s", args.save_normalized)

    # Build prompt
    prompt_template = Path("prompt").read_text()
    full_prompt = prompt_template + normalized_json

    # Send to OpenAI
    log.info("Sending to OpenAI (%s)...", args.model)
    try:
        openai_client = OpenAI()
        response = openai_client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": full_prompt}],
        )
    except Exception as exc:
        log.error("OpenAI API call failed: %s", exc)
        sys.exit(1)

    report = response.choices[0].message.content

    if args.output:
        Path(args.output).write_text(report)
        log.info("Report written to %s", args.output)
    else:
        print(report)

    log.info("Done.")


if __name__ == "__main__":
    main()
