import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import get_fixtures, get_rounds, get_match_detail

st.set_page_config(page_title="Match Detail", page_icon="🔍", layout="wide")

st.title("Match Detail")
st.markdown("---")

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

# Event type icons
EVENT_ICONS = {
    "Goal":  "⚽",
    "Card":  {"Yellow Card": "🟨", "Red Card": "🟥"},
    "subst": "🔄",
}

def get_event_icon(event_type, detail):
    if event_type == "Goal":
        if detail == "Own Goal":
            return "⚽ (OG)"
        elif detail == "Missed Penalty":
            return "❌"
        return "⚽"
    elif event_type == "Card":
        return EVENT_ICONS["Card"].get(detail, "📋")
    elif event_type == "subst":
        return "🔄"
    return "•"


def format_date(dt):
    try:
        if hasattr(dt, 'strftime'):
            return dt.strftime("%d %b %Y  %H:%M")
        return str(dt)[:16]
    except:
        return str(dt)


# --- Step 1: Pick a round ---
all_rounds = get_rounds()
sorted_rounds = sorted(
    all_rounds,
    key=lambda r: ROUND_ORDER.index(r) if r in ROUND_ORDER else 99
)

col_r, col_m = st.columns([1, 2])

with col_r:
    selected_round = st.selectbox("Select Round", sorted_rounds)

# --- Step 2: Pick a match from that round ---
fixtures_df = get_fixtures(round_name=selected_round)

if fixtures_df.empty:
    st.warning("No fixtures found for this round.")
    st.stop()

# Build match label: "Home Team vs Away Team (score)"
def match_label(row):
    if row["status"] == "FT" and row["home_goals"] is not None:
        return f"{row['home_team']} {int(row['home_goals'])} - {int(row['away_goals'])} {row['away_team']}"
    else:
        return f"{row['home_team']} vs {row['away_team']}"

fixture_options = {match_label(row): row["fixture_id"] for _, row in fixtures_df.iterrows()}

with col_m:
    selected_label  = st.selectbox("Select Match", list(fixture_options.keys()))

selected_fixture_id = fixture_options[selected_label]

st.markdown("---")

# --- Load match detail ---
match_df, events_df = get_match_detail(selected_fixture_id)

if match_df.empty:
    st.warning("Match data not found.")
    st.stop()

match = match_df.iloc[0]

# --- Score header ---
home_goals = int(match["home_goals"]) if match["home_goals"] is not None else "-"
away_goals = int(match["away_goals"]) if match["away_goals"] is not None else "-"

col_home, col_score, col_away = st.columns([3, 2, 3])

with col_home:
    st.markdown(
        f"<h2 style='text-align:right; color:#111827;'>{match['home_team']}</h2>",
        unsafe_allow_html=True
    )

with col_score:
    st.markdown(
        f"<div style='text-align:center; background:#F1F5F9; border-radius:12px; padding:20px;'>"
        f"<p style='font-size:48px; font-weight:800; color:#1F4E79; margin:0; letter-spacing:4px;'>"
        f"{home_goals} - {away_goals}</p>"
        f"<p style='font-size:13px; color:#6B7280; margin:4px 0 0 0;'>{match['status']} &nbsp;|&nbsp; {match['round']}</p>"
        f"<p style='font-size:12px; color:#9CA3AF; margin:4px 0 0 0;'>{format_date(match['date'])}</p>"
        f"<p style='font-size:12px; color:#9CA3AF; margin:2px 0 0 0;'>{match['venue']}, {match['city']}</p>"
        f"</div>",
        unsafe_allow_html=True
    )

with col_away:
    st.markdown(
        f"<h2 style='text-align:left; color:#111827;'>{match['away_team']}</h2>",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- Events timeline ---
if events_df.empty:
    st.info("No events recorded for this match yet.")
else:
    st.markdown("### Match Events")

    # Separate events by team
    home_team = match["home_team"]
    away_team = match["away_team"]

    col_home_ev, col_mid, col_away_ev = st.columns([5, 1, 5])

    with col_home_ev:
        st.markdown(f"**{home_team}**")

    with col_mid:
        st.markdown("&nbsp;", unsafe_allow_html=True)

    with col_away_ev:
        st.markdown(f"**{away_team}**")

    st.markdown("<hr style='margin:6px 0;'>", unsafe_allow_html=True)

    # Sort events by minute
    events_sorted = events_df.sort_values("minute").reset_index(drop=True)

    for _, ev in events_sorted.iterrows():
        minute = f"{int(ev['minute'])}'"
        if ev["extra_minute"] and ev["extra_minute"] > 0:
            minute = f"{int(ev['minute'])}+{int(ev['extra_minute'])}'"

        icon        = get_event_icon(ev["event_type"], ev["detail"])
        player      = ev["player_name"] or ""
        assist      = f" ↳ {ev['assist_name']}" if ev["assist_name"] else ""
        is_home     = ev["team"] == home_team

        col_home_ev, col_mid, col_away_ev = st.columns([5, 1, 5])

        with col_home_ev:
            if is_home:
                st.markdown(
                    f"<div style='text-align:right; padding:4px 0; font-size:14px;'>"
                    f"{icon} &nbsp;<strong>{player}</strong>{assist} &nbsp;"
                    f"<span style='color:#9CA3AF;'>{minute}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        with col_mid:
            st.markdown(
                "<div style='border-left:2px solid #E5E7EB; height:28px; margin:auto;'></div>",
                unsafe_allow_html=True
            )

        with col_away_ev:
            if not is_home:
                st.markdown(
                    f"<div style='text-align:left; padding:4px 0; font-size:14px;'>"
                    f"<span style='color:#9CA3AF;'>{minute}</span> &nbsp;"
                    f"{icon} &nbsp;<strong>{player}</strong>{assist}"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # --- Event summary ---
    st.markdown("---")
    st.markdown("### Summary")

    s1, s2, s3 = st.columns(3)

    goals   = events_df[events_df["event_type"] == "Goal"]
    cards   = events_df[events_df["event_type"] == "Card"]
    subs    = events_df[events_df["event_type"] == "subst"]

    with s1:
        st.metric("Goals", len(goals[goals["detail"] != "Missed Penalty"]))
    with s2:
        st.metric("Cards", len(cards))
    with s3:
        st.metric("Substitutions", len(subs))