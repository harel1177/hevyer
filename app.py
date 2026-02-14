import json

import streamlit as st
from dotenv import load_dotenv

from main import build_prompt, build_report, fetch_workouts

load_dotenv()

st.set_page_config(page_title="Hevyer", page_icon="\U0001f4aa", layout="wide")
st.title("\U0001f4aa Hevyer — AI Coaching Report")


def display_report(report: str) -> None:
    """Parse and display a coaching report. Falls back to raw text if not valid JSON."""
    try:
        data = json.loads(report)
    except (json.JSONDecodeError, TypeError):
        data = None

    if not data:
        st.header("Report")
        st.markdown(report)
        return

    # Recent Workout Focus
    focus = data.get("recent_workout_focus", {})
    if focus:
        st.markdown("---")
        st.subheader("\U0001f3af Recent Workout Focus")
        cols = st.columns(3)
        cols[0].markdown(
            f"""<div style="background:#1e293b;padding:1rem;border-radius:0.5rem;text-align:center">
            <div style="color:#94a3b8;font-size:0.85rem">Date</div>
            <div style="color:#f8fafc;font-size:1.25rem;font-weight:600">{focus.get('date', 'N/A')}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        cols[1].markdown(
            f"""<div style="background:#1e293b;padding:1rem;border-radius:0.5rem;text-align:center">
            <div style="color:#94a3b8;font-size:0.85rem">Split</div>
            <div style="color:#f8fafc;font-size:1.25rem;font-weight:600">{focus.get('split', 'N/A')}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        cols[2].markdown(
            f"""<div style="background:#1e293b;padding:1rem;border-radius:0.5rem;text-align:center">
            <div style="color:#94a3b8;font-size:0.85rem">Evaluation</div>
            <div style="color:#60a5fa;font-size:1rem;font-weight:500">{focus.get('overall_evaluation', 'N/A')}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    # Comparative Insights
    insights = data.get("comparative_insights", [])
    if insights:
        st.markdown("---")
        st.subheader("\U0001f4ca Comparative Insights")
        for item in insights:
            exercise = item.get("exercise", "")
            comparison = item.get("comparison", "")
            st.markdown(
                f"""<div style="background:#1e293b;padding:0.75rem 1rem;border-left:4px solid #3b82f6;
                border-radius:0 0.5rem 0.5rem 0;margin-bottom:0.5rem">
                <span style="color:#60a5fa;font-weight:600">{exercise}</span>
                <span style="color:#94a3b8"> — </span>
                <span style="color:#e2e8f0">{comparison}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    # Fatigue / Plateau Signals
    fatigue = data.get("fatigue_or_plateau_signals", [])
    if fatigue:
        st.markdown("---")
        st.subheader("\u26a0\ufe0f Fatigue / Plateau Signals")
        for item in fatigue:
            st.markdown(
                f"""<div style="background:#451a03;padding:0.6rem 1rem;border-radius:0.5rem;
                margin-bottom:0.4rem;color:#fbbf24">\u2022 {item}</div>""",
                unsafe_allow_html=True,
            )

    # What Improved
    improved = data.get("what_improved_since_last_time", [])
    if improved:
        st.markdown("---")
        st.subheader("\u2705 What Improved")
        for item in improved:
            st.markdown(
                f"""<div style="background:#052e16;padding:0.6rem 1rem;border-radius:0.5rem;
                margin-bottom:0.4rem;color:#4ade80">\u2022 {item}</div>""",
                unsafe_allow_html=True,
            )

    # What to Adjust Next
    adjust = data.get("what_to_adjust_next", [])
    if adjust:
        st.markdown("---")
        st.subheader("\U0001f527 What to Adjust Next")
        for item in adjust:
            st.markdown(
                f"""<div style="background:#1e1b4b;padding:0.6rem 1rem;border-radius:0.5rem;
                margin-bottom:0.4rem;color:#a78bfa">\u2022 {item}</div>""",
                unsafe_allow_html=True,
            )


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
        st.subheader("\U0001f4cb Step 1: Copy the prompt")
        st.info("Copy the prompt below and paste it into any AI model (ChatGPT, Claude, etc.).")
        with st.expander("Show full prompt", expanded=False):
            st.code(st.session_state["manual_prompt"], language=None)

        st.subheader("\U0001f4e5 Step 2: Paste the AI response")
        st.info("Paste the JSON response you got from the AI model below.")
        pasted = st.text_area("AI response (JSON)", height=300, key="pasted_report")

        if st.button("Display Report", type="primary"):
            if pasted.strip():
                display_report(pasted.strip())
            else:
                st.warning("Paste the AI response above first.")

        with st.expander("Normalized Workout Data"):
            st.json(st.session_state["manual_normalized"])
