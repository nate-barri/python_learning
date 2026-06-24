import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import get_fixtures, get_rounds

st.set_page_config(page_title="Schedule", page_icon="📅", layout="wide")

st.title("Match Schedule")
st.markdown("---")


def format_date(dt):
    try:
        if hasattr(dt, 'strftime'):
            return dt.strftime("%d %b %Y  %H:%M")
        return str(dt)[:16]
    except:
        return str(dt)


def status_label(status, elapsed):
    if status == "FT":
        return "FT"
    elif status in ("1H", "2H", "ET", "P", "BT"):
        return f"LIVE {elapsed}'"
    elif status == "HT":
        return "HT"
    else:
        return "Upcoming"


def status_color(status):
    if status == "FT":
        return "#059669"
    elif status in ("1H", "2H", "ET", "P", "BT", "HT"):
        return "#DC2626"
    else:
        return "#6B7280"


# Correct round order
ROUND_ORDER = [
    "Group Stage - 1",
    "Group Stage - 2",
    "Group Stage - 3",
    "Round of 16",
    "Quarter-finals",
    "Semi-finals",
    "3rd Place Final",
    "Final"
]

# Load rounds and sort them correctly
all_rounds = get_rounds()
if not all_rounds:
    st.warning("No fixture data found. Run fetcher.py first.")
    st.stop()

# Sort rounds by the defined order, put any unknown rounds at the end
sorted_rounds = sorted(all_rounds, key=lambda r: ROUND_ORDER.index(r) if r in ROUND_ORDER else 99)

# Round filter at the top
st.markdown("#### Select Round")
selected_round = st.radio(
    label="round_selector",
    options=["All"] + sorted_rounds,
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# Load fixtures
df = get_fixtures() if selected_round == "All" else get_fixtures(round_name=selected_round)

if df.empty:
    st.warning("No fixtures found for this round.")
    st.stop()

# Summary metrics
total    = len(df)
played   = len(df[df["status"] == "FT"])
upcoming = len(df[df["status"] == "NS"])
live     = len(df[df["status"].isin(["1H", "2H", "HT", "ET", "P", "BT"])])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Matches", total)
c2.metric("Played", played)
c3.metric("Upcoming", upcoming)
c4.metric("Live Now", live)

st.markdown("---")


def match_card(row):
    """Render a single match card using native Streamlit columns."""
    if row["status"] == "NS" or row["home_goals"] is None:
        score_text = "vs"
    else:
        score_text = f"{int(row['home_goals'])} - {int(row['away_goals'])}"

    status_text = status_label(row["status"], row["elapsed"])
    s_color     = status_color(row["status"])
    date_str    = format_date(row["date"])

    st.markdown(
        f"""
        <div style='border:1px solid #E5E7EB; border-radius:10px; padding:14px 16px;
                    background:#FAFAFA; margin-bottom:4px;'>
            <div style='display:flex; justify-content:space-between; align-items:center;'>
                <span style='font-size:14px; font-weight:600; flex:1; text-align:right;
                             color:#111827;'>{row['home_team']}</span>
                <span style='font-size:18px; font-weight:700; color:#1F4E79;
                             flex:0 0 90px; text-align:center;'>{score_text}</span>
                <span style='font-size:14px; font-weight:600; flex:1; text-align:left;
                             color:#111827;'>{row['away_team']}</span>
            </div>
            <div style='text-align:center; margin-top:6px;'>
                <span style='font-size:11px; font-weight:600; color:{s_color};'>{status_text}</span>
                <span style='font-size:11px; color:#9CA3AF;'> &nbsp;|&nbsp; {date_str}</span>
                <span style='font-size:11px; color:#9CA3AF;'> &nbsp;|&nbsp; {row['venue']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Display matches — 2 per row for group stages, 1 per row for knockouts
if selected_round == "All":
    # Sort round groups in correct order
    for round_name in sorted_rounds:
        group = df[df["round"] == round_name]
        if group.empty:
            continue

        st.markdown(f"### {round_name}")
        rows = group.reset_index(drop=True)

        # Group stages: 2 cards per row
        if "Group Stage" in round_name:
            for i in range(0, len(rows), 2):
                col1, col2 = st.columns(2)
                with col1:
                    match_card(rows.iloc[i])
                with col2:
                    if i + 1 < len(rows):
                        match_card(rows.iloc[i + 1])
        else:
            # Knockouts: 1 card per row, centred
            _, center, _ = st.columns([1, 2, 1])
            for _, row in rows.iterrows():
                with center:
                    match_card(row)

        st.markdown("<br>", unsafe_allow_html=True)

else:
    rows = df.reset_index(drop=True)

    if "Group Stage" in selected_round:
        for i in range(0, len(rows), 2):
            col1, col2 = st.columns(2)
            with col1:
                match_card(rows.iloc[i])
            with col2:
                if i + 1 < len(rows):
                    match_card(rows.iloc[i + 1])
    else:
        _, center, _ = st.columns([1, 2, 1])
        for _, row in rows.iterrows():
            with center:
                match_card(row)