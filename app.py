import json

import streamlit as st
from dotenv import load_dotenv

from main import build_prompt, build_report, fetch_workouts

load_dotenv()

st.set_page_config(page_title="Hevyer", page_icon="\U0001f4aa", layout="wide")
st.title("Hevyer — AI Coaching Report")


def display_report(report: str) -> None:
    """Parse and display a coaching report. Falls back to raw text if not valid JSON."""
    try:
        data = json.loads(report)
    except (json.JSONDecodeError, TypeError):
        data = None

    if data:
        focus = data.get("recent_workout_focus", {})
        if focus:
            st.header("Recent Workout Focus")
            cols = st.columns(3)
            cols[0].metric("Date", focus.get("date", "N/A"))
            cols[1].metric("Split", focus.get("split", "N/A"))
            st.markdown(f"**Overall Evaluation:** {focus.get('overall_evaluation', 'N/A')}")

        insights = data.get("comparative_insights", [])
        if insights:
            st.header("Comparative Insights")
            st.table(insights)

        fatigue = data.get("fatigue_or_plateau_signals", [])
        if fatigue:
            st.header("Fatigue / Plateau Signals")
            for item in fatigue:
                st.markdown(f"- {item}")

        improved = data.get("what_improved_since_last_time", [])
        if improved:
            st.header("What Improved")
            for item in improved:
                st.markdown(f"- {item}")

        adjust = data.get("what_to_adjust_next", [])
        if adjust:
            st.header("What to Adjust Next")
            for item in adjust:
                st.markdown(f"- {item}")
    else:
        st.header("Report")
        st.markdown(report)


# Sidebar controls
with st.sidebar:
    st.header("Settings")
    mode = st.radio("Mode", ["Automatic (OpenAI API)", "Manual (copy/paste)"])
    if mode == "Automatic (OpenAI API)":
        model = st.selectbox("OpenAI Model", ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini"], index=0)
    generate = st.button("Fetch Workouts", type="primary", use_container_width=True)

# --- Automatic mode ---
if mode == "Automatic (OpenAI API)":
    if generate:
        with st.spinner("Fetching workouts from Hevy..."):
            try:
                workouts = fetch_workouts()
            except Exception as exc:
                st.error(f"Failed to fetch workouts: {exc}")
                st.stop()

        with st.spinner(f"Generating report with {model}..."):
            try:
                report, normalized_json = build_report(workouts, model)
            except Exception as exc:
                st.error(f"Failed to generate report: {exc}")
                st.stop()

        display_report(report)

        with st.expander("Normalized Workout Data"):
            st.json(normalized_json)

# --- Manual mode ---
else:
    if generate:
        with st.spinner("Fetching workouts from Hevy..."):
            try:
                workouts = fetch_workouts()
            except Exception as exc:
                st.error(f"Failed to fetch workouts: {exc}")
                st.stop()

            full_prompt, normalized_json = build_prompt(workouts)

        st.session_state["manual_prompt"] = full_prompt
        st.session_state["manual_normalized"] = normalized_json

    if "manual_prompt" in st.session_state:
        st.header("Step 1: Copy the prompt")
        st.info("Copy the prompt below and paste it into any AI model (ChatGPT, Claude, etc.).")
        st.code(st.session_state["manual_prompt"], language=None)

        st.header("Step 2: Paste the AI response")
        st.info("Paste the JSON response you got from the AI model below.")
        pasted = st.text_area("AI response (JSON)", height=300, key="pasted_report")

        if st.button("Display Report", type="primary"):
            if pasted.strip():
                display_report(pasted.strip())
            else:
                st.warning("Paste the AI response above first.")

        with st.expander("Normalized Workout Data"):
            st.json(st.session_state["manual_normalized"])
