import json

import streamlit as st
from dotenv import load_dotenv

from main import build_report, fetch_workouts

load_dotenv()

st.set_page_config(page_title="Hevyer", page_icon="\U0001f4aa", layout="wide")
st.title("Hevyer — AI Coaching Report")

# Sidebar controls
with st.sidebar:
    st.header("Settings")
    model = st.selectbox("OpenAI Model", ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini"], index=0)
    generate = st.button("Generate Report", type="primary", use_container_width=True)

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

    # Try to parse the report as JSON for structured display
    try:
        data = json.loads(report)
    except (json.JSONDecodeError, TypeError):
        data = None

    if data:
        # Recent Workout Focus
        focus = data.get("recent_workout_focus", {})
        if focus:
            st.header("Recent Workout Focus")
            cols = st.columns(3)
            cols[0].metric("Date", focus.get("date", "N/A"))
            cols[1].metric("Split", focus.get("split", "N/A"))
            st.markdown(f"**Overall Evaluation:** {focus.get('overall_evaluation', 'N/A')}")

        # Comparative Insights
        insights = data.get("comparative_insights", [])
        if insights:
            st.header("Comparative Insights")
            st.table(insights)

        # Fatigue / Plateau Signals
        fatigue = data.get("fatigue_or_plateau_signals", [])
        if fatigue:
            st.header("Fatigue / Plateau Signals")
            for item in fatigue:
                st.markdown(f"- {item}")

        # What Improved
        improved = data.get("what_improved_since_last_time", [])
        if improved:
            st.header("What Improved")
            for item in improved:
                st.markdown(f"- {item}")

        # What to Adjust Next
        adjust = data.get("what_to_adjust_next", [])
        if adjust:
            st.header("What to Adjust Next")
            for item in adjust:
                st.markdown(f"- {item}")
    else:
        st.header("Report")
        st.markdown(report)

    # Expandable normalized workout data
    with st.expander("Normalized Workout Data"):
        st.json(normalized_json)
