import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import get_teams, get_team_detail, get_standings

st.set_page_config(page_title="Teams", page_icon="🏳️", layout="wide")

st.title("Teams")
st.markdown("---")

# Load all teams
teams_df = get_teams()
if teams_df.empty:
    st.warning("No team data found. Run fetcher.py first.")
    st.stop()

# Load standings for group info
standings_df = get_standings()

# Build a lookup: team_id -> group, rank, points
standings_lookup = {}
if not standings_df.empty:
    for _, row in standings_df.iterrows():
        standings_lookup[row["team"]] = {
            "group": row["group_name"],
            "rank":  row["rank"],
            "points": row["points"],
            "played": row["played"],
            "won":    row["won"],
            "drawn":  row["drawn"],
            "lost":   row["lost"],
            "gf":     row["goals_for"],
            "ga":     row["goals_against"],
            "gd":     row["goal_diff"],
            "form":   row["form"]
        }

# --- Sidebar: pick a team ---
st.sidebar.markdown("### Select Team")

# Group teams by their group
group_map = {}
for _, row in teams_df.iterrows():
    s = standings_lookup.get(row["name"], {})
    grp = s.get("group", "Unknown")
    group_map.setdefault(grp, []).append(row["name"])

# Sort groups
ROUND_ORDER = [
    "Group A", "Group B", "Group C", "Group D",
    "Group E", "Group F", "Group G", "Group H"
]
sorted_groups = sorted(group_map.keys(), key=lambda g: ROUND_ORDER.index(g) if g in ROUND_ORDER else 99)

# Flat sorted team list grouped by letter
all_team_names = []
for grp in sorted_groups:
    all_team_names.extend(sorted(group_map[grp]))

selected_team_name = st.sidebar.selectbox("Team", all_team_names)

# Get team row
team_row = teams_df[teams_df["name"] == selected_team_name].iloc[0]
team_id  = team_row["team_id"]
s        = standings_lookup.get(selected_team_name, {})

# --- Team header ---
col_info, col_stats = st.columns([2, 3])

with col_info:
    st.markdown(f"## {team_row['name']}")
    st.markdown(f"**Country:** {team_row['country']}")
    if s:
        st.markdown(f"**Group:** {s.get('group', 'N/A')}  &nbsp;|&nbsp;  **Rank:** {s.get('rank', 'N/A')}")

with col_stats:
    if s:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Points", s.get("points", 0))
        c2.metric("Won",    s.get("won", 0))
        c3.metric("Drawn",  s.get("drawn", 0))
        c4.metric("Lost",   s.get("lost", 0))
        c5.metric("GD",     s.get("gd", 0))

st.markdown("---")

# --- Match history ---
st.markdown("### Match History")

matches_df = get_team_detail(team_id)

if matches_df.empty:
    st.info("No completed matches found for this team.")
else:
    def result_badge(result):
        if result == "W":
            return "<span style='background:#D1FAE5; color:#065F46; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:700;'>W</span>"
        elif result == "D":
            return "<span style='background:#FEF3C7; color:#92400E; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:700;'>D</span>"
        else:
            return "<span style='background:#FEE2E2; color:#991B1B; padding:2px 10px; border-radius:999px; font-size:12px; font-weight:700;'>L</span>"

    def format_date(dt):
        try:
            if hasattr(dt, 'strftime'):
                return dt.strftime("%d %b %Y")
            return str(dt)[:10]
        except:
            return str(dt)

    for _, row in matches_df.iterrows():
        badge    = result_badge(row["result"])
        score    = f"{int(row['home_goals'])} - {int(row['away_goals'])}"
        date_str = format_date(row["date"])

        # Bold the selected team
        home_bold = f"<strong>{row['home_team']}</strong>" if row["home_team"] == selected_team_name else row["home_team"]
        away_bold = f"<strong>{row['away_team']}</strong>" if row["away_team"] == selected_team_name else row["away_team"]

        col_date, col_round, col_match, col_result = st.columns([2, 2, 5, 1])

        with col_date:
            st.markdown(
                f"<p style='font-size:13px; color:#6B7280; margin:8px 0;'>{date_str}</p>",
                unsafe_allow_html=True
            )
        with col_round:
            st.markdown(
                f"<p style='font-size:13px; color:#9CA3AF; margin:8px 0;'>{row['round']}</p>",
                unsafe_allow_html=True
            )
        with col_match:
            st.markdown(
                f"<p style='font-size:14px; margin:8px 0;'>"
                f"{home_bold} &nbsp; {score} &nbsp; {away_bold}"
                f"</p>",
                unsafe_allow_html=True
            )
        with col_result:
            st.markdown(
                f"<p style='margin:8px 0;'>{badge}</p>",
                unsafe_allow_html=True
            )

        st.markdown(
            "<hr style='margin:2px 0; border:none; border-top:1px solid #F3F4F6;'>",
            unsafe_allow_html=True
        )

    # Win/draw/loss summary
    st.markdown("<br>", unsafe_allow_html=True)
    total   = len(matches_df)
    wins    = len(matches_df[matches_df["result"] == "W"])
    draws   = len(matches_df[matches_df["result"] == "D"])
    losses  = len(matches_df[matches_df["result"] == "L"])
    gf      = matches_df["home_goals"].where(matches_df["home_team"] == selected_team_name, matches_df["away_goals"]).sum()
    ga      = matches_df["away_goals"].where(matches_df["home_team"] == selected_team_name, matches_df["home_goals"]).sum()

    st.markdown("### Tournament Summary")
    s1, s2, s3, s4, s5, s6 = st.columns(6)
    s1.metric("Played",         total)
    s2.metric("Wins",           int(wins))
    s3.metric("Draws",          int(draws))
    s4.metric("Losses",         int(losses))
    s5.metric("Goals Scored",   int(gf))
    s6.metric("Goals Conceded", int(ga))