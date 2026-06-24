import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import (
    get_top_scorers, get_top_assists, get_top_cards,
    get_tournament_player_stats, get_player_deep_dive,
    get_all_player_names, get_teams, get_standings
)

st.set_page_config(page_title="Player Stats", page_icon="📊", layout="wide")

st.title("Player Stats")
st.markdown("---")

# ── Main tabs ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Top Scorers & Assists",
    "Tournament Stats",
    "By Team / Group",
    "Player Deep Dive"
])


# ── Helper: horizontal bar ─────────────────────────────────────────────────
def bar(value, max_value, color="#1F4E79"):
    pct = int((value / max_value) * 100) if max_value > 0 else 0
    return (
        f"<div style='background:#E5E7EB; border-radius:999px; height:8px; margin-top:16px;'>"
        f"<div style='background:{color}; width:{pct}%; height:8px; border-radius:999px;'></div>"
        f"</div>"
    )


def medal(rank):
    if rank == 1: return "🥇"
    if rank == 2: return "🥈"
    if rank == 3: return "🥉"
    return f"<span style='color:#6B7280; font-size:13px;'>{rank}</span>"


# ══════════════════════════════════════════════════════════════════════════
# TAB 1 — Top Scorers, Assists, Cards
# ══════════════════════════════════════════════════════════════════════════
with tab1:
    sub1, sub2, sub3 = st.tabs(["Top Scorers", "Top Assists", "Disciplinary"])

    with sub1:
        st.markdown("### Top Scorers")
        df = get_top_scorers()
        if df.empty:
            st.info("No goal data yet. Run fetch_all_events() first.")
        else:
            for i, row in df.iterrows():
                c1, c2, c3, c4, c5 = st.columns([1, 3, 3, 1, 4])
                c1.markdown(f"<p style='margin:8px 0; font-size:18px;'>{medal(i+1)}</p>", unsafe_allow_html=True)
                c2.markdown(f"<p style='margin:8px 0; font-weight:600;'>{row['player_name']}</p>", unsafe_allow_html=True)
                c3.markdown(f"<p style='margin:8px 0; color:#6B7280;'>{row['team']}</p>", unsafe_allow_html=True)
                c4.markdown(f"<p style='margin:8px 0; font-weight:700; color:#1F4E79; font-size:16px;'>{row['goals']}</p>", unsafe_allow_html=True)
                c5.markdown(bar(row['goals'], df['goals'].max()), unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0; border:none; border-top:1px solid #F9FAFB;'>", unsafe_allow_html=True)

    with sub2:
        st.markdown("### Top Assists")
        df = get_top_assists()
        if df.empty:
            st.info("No assist data yet. Run fetch_all_events() first.")
        else:
            for i, row in df.iterrows():
                c1, c2, c3, c4, c5 = st.columns([1, 3, 3, 1, 4])
                c1.markdown(f"<p style='margin:8px 0; font-size:18px;'>{medal(i+1)}</p>", unsafe_allow_html=True)
                c2.markdown(f"<p style='margin:8px 0; font-weight:600;'>{row['player_name']}</p>", unsafe_allow_html=True)
                c3.markdown(f"<p style='margin:8px 0; color:#6B7280;'>{row['team']}</p>", unsafe_allow_html=True)
                c4.markdown(f"<p style='margin:8px 0; font-weight:700; color:#2E75B6; font-size:16px;'>{row['assists']}</p>", unsafe_allow_html=True)
                c5.markdown(bar(row['assists'], df['assists'].max(), "#2E75B6"), unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0; border:none; border-top:1px solid #F9FAFB;'>", unsafe_allow_html=True)

    with sub3:
        st.markdown("### Disciplinary")
        df = get_top_cards()
        if df.empty:
            st.info("No card data yet. Run fetch_all_events() first.")
        else:
            c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 3, 2, 2, 2])
            for col, label in zip([c1,c2,c3,c4,c5,c6], ["#","Player","Team","🟨","🟥","Total"]):
                col.markdown(f"**{label}**")
            st.markdown("<hr style='margin:4px 0; border:none; border-top:2px solid #E5E7EB;'>", unsafe_allow_html=True)
            for i, row in df.iterrows():
                total = int(row["yellow_cards"]) + int(row["red_cards"])
                c1, c2, c3, c4, c5, c6 = st.columns([1, 3, 3, 2, 2, 2])
                c1.markdown(f"<p style='margin:8px 0; color:#6B7280;'>{i+1}</p>", unsafe_allow_html=True)
                c2.markdown(f"<p style='margin:8px 0; font-weight:600;'>{row['player_name']}</p>", unsafe_allow_html=True)
                c3.markdown(f"<p style='margin:8px 0; color:#6B7280;'>{row['team']}</p>", unsafe_allow_html=True)
                c4.markdown(f"<p style='margin:8px 0; font-weight:600; color:#92400E;'>{int(row['yellow_cards'])}</p>", unsafe_allow_html=True)
                c5.markdown(f"<p style='margin:8px 0; font-weight:600; color:#991B1B;'>{int(row['red_cards'])}</p>", unsafe_allow_html=True)
                c6.markdown(f"<p style='margin:8px 0; font-weight:700; color:#1F4E79;'>{total}</p>", unsafe_allow_html=True)
                st.markdown("<hr style='margin:2px 0; border:none; border-top:1px solid #F9FAFB;'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
# TAB 2 — Full Tournament Stats Table
# ══════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("### Full Tournament Player Stats")
    df = get_tournament_player_stats()

    if df.empty:
        st.info("No player stats yet. Run fetch_player_stats() in fetcher.py first.")
    else:
        # Stat category selector
        category = st.radio(
            "View",
            ["Attacking", "Passing", "Defending", "Discipline", "Per 90"],
            horizontal=True
        )

        if category == "Attacking":
            cols = ["player", "team", "matches", "minutes", "goals", "assists",
                    "goal_involvements", "shots", "shots_on_target",
                    "shot_accuracy", "conversion_rate", "avg_rating"]
        elif category == "Passing":
            cols = ["player", "team", "matches", "minutes", "passes", "key_passes", "avg_rating"]
        elif category == "Defending":
            cols = ["player", "team", "matches", "minutes", "tackles", "avg_rating"]
        elif category == "Discipline":
            cols = ["player", "team", "matches", "yellow_cards", "red_cards"]
        else:  # Per 90
            cols = ["player", "team", "matches", "minutes",
                    "goals_per_90", "assists_per_90", "avg_rating"]

        display_df = df[cols].copy()
        st.dataframe(display_df, use_container_width=True, height=500)


# ══════════════════════════════════════════════════════════════════════════
# TAB 3 — Filter by Team or Group
# ══════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("### Stats by Team or Group")

    filter_type = st.radio("Filter by", ["Team", "Group"], horizontal=True)

    if filter_type == "Team":
        teams_df = get_teams()
        team_names = sorted(teams_df["name"].tolist())
        selected_team = st.selectbox("Select Team", team_names)
        df = get_tournament_player_stats(team_name=selected_team)
        st.markdown(f"#### {selected_team} — Player Stats")
    else:
        GROUPS = ["Group A","Group B","Group C","Group D",
                  "Group E","Group F","Group G","Group H"]
        selected_group = st.selectbox("Select Group", GROUPS)
        df = get_tournament_player_stats(group_name=selected_group)
        st.markdown(f"#### {selected_group} — Player Stats")

    if df.empty:
        st.info("No player stats yet. Run fetch_player_stats() in fetcher.py first.")
    else:
        category = st.radio(
            "Stat category",
            ["Attacking", "Passing", "Defending", "Per 90"],
            horizontal=True,
            key="tab3_cat"
        )

        if category == "Attacking":
            cols = ["player", "team", "matches", "goals", "assists",
                    "goal_involvements", "shots", "shot_accuracy",
                    "conversion_rate", "avg_rating"]
        elif category == "Passing":
            cols = ["player", "team", "matches", "passes", "key_passes", "avg_rating"]
        elif category == "Defending":
            cols = ["player", "team", "matches", "tackles", "avg_rating"]
        else:
            cols = ["player", "team", "matches", "minutes",
                    "goals_per_90", "assists_per_90", "avg_rating"]

        st.dataframe(df[cols], use_container_width=True, height=400)


# ══════════════════════════════════════════════════════════════════════════
# TAB 4 — Player Deep Dive
# ══════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("### Player Deep Dive")

    player_names = get_all_player_names()

    if not player_names:
        st.info("No player stats yet. Run fetch_player_stats() in fetcher.py first.")
    else:
        selected_player = st.selectbox("Select Player", player_names)
        df = get_player_deep_dive(selected_player)

        if df.empty:
            st.info("No match data for this player.")
        else:
            # ── Summary metrics ──────────────────────────────────────────
            st.markdown("#### Overview")
            total_min   = int(df["minutes_played"].sum())
            total_goals = int(df["goals"].sum())
            total_ast   = int(df["assists"].sum())
            avg_rating  = round(df["rating"].mean(), 2)
            shots_tot   = int(df["shots_total"].sum())
            shots_on    = int(df["shots_on"].sum())
            passes_tot  = int(df["passes_total"].sum())
            key_passes  = int(df["passes_key"].sum())
            tackles_tot = int(df["tackles"].sum())
            yellows     = int(df["yellow_cards"].sum())
            reds        = int(df["red_cards"].sum())

            shot_acc    = round(shots_on / shots_tot * 100, 1) if shots_tot > 0 else 0
            conv_rate   = round(total_goals / shots_tot * 100, 1) if shots_tot > 0 else 0
            goals_p90   = round(total_goals / total_min * 90, 2) if total_min > 0 else 0
            assists_p90 = round(total_ast / total_min * 90, 2) if total_min > 0 else 0

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Matches",  len(df))
            c2.metric("Minutes",  total_min)
            c3.metric("Goals",    total_goals)
            c4.metric("Assists",  total_ast)
            c5.metric("Avg Rating", avg_rating)

            st.markdown("---")

            # ── Stat sections ────────────────────────────────────────────
            col_att, col_pass, col_def, col_disc = st.columns(4)

            with col_att:
                st.markdown("**Attacking**")
                st.markdown(f"Shots: **{shots_tot}**")
                st.markdown(f"On Target: **{shots_on}**")
                st.markdown(f"Shot Accuracy: **{shot_acc}%**")
                st.markdown(f"Conversion Rate: **{conv_rate}%**")
                st.markdown(f"Goals per 90: **{goals_p90}**")

            with col_pass:
                st.markdown("**Passing**")
                st.markdown(f"Total Passes: **{passes_tot}**")
                st.markdown(f"Key Passes: **{key_passes}**")
                st.markdown(f"Assists per 90: **{assists_p90}**")

            with col_def:
                st.markdown("**Defending**")
                st.markdown(f"Tackles: **{tackles_tot}**")

            with col_disc:
                st.markdown("**Discipline**")
                st.markdown(f"🟨 Yellow: **{yellows}**")
                st.markdown(f"🟥 Red: **{reds}**")

            st.markdown("---")

            # ── Per match breakdown ──────────────────────────────────────
            st.markdown("#### Match by Match")

            def fmt_date(dt):
                try:
                    return dt.strftime("%d %b") if hasattr(dt, 'strftime') else str(dt)[:10]
                except:
                    return str(dt)

            for _, row in df.iterrows():
                match_label = f"{row['home_team']} {int(row['home_goals'])} - {int(row['away_goals'])} {row['away_team']}"
                date_str    = fmt_date(row["date"])
                rating_color = "#059669" if row["rating"] >= 7 else "#D97706" if row["rating"] >= 6 else "#DC2626"

                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([2, 3, 1, 1, 1, 1, 1, 1])
                c1.markdown(f"<p style='font-size:12px; color:#9CA3AF; margin:8px 0;'>{date_str} | {row['round']}</p>", unsafe_allow_html=True)
                c2.markdown(f"<p style='font-size:13px; margin:8px 0;'>{match_label}</p>", unsafe_allow_html=True)
                c3.markdown(f"<p style='font-size:13px; margin:8px 0;'>{int(row['minutes_played'])}'</p>", unsafe_allow_html=True)
                c4.markdown(f"<p style='font-size:13px; font-weight:600; color:#1F4E79; margin:8px 0;'>{int(row['goals'])}G</p>", unsafe_allow_html=True)
                c5.markdown(f"<p style='font-size:13px; font-weight:600; color:#2E75B6; margin:8px 0;'>{int(row['assists'])}A</p>", unsafe_allow_html=True)
                c6.markdown(f"<p style='font-size:13px; margin:8px 0;'>{int(row['shots_total'])} shots</p>", unsafe_allow_html=True)
                c7.markdown(f"<p style='font-size:13px; margin:8px 0;'>{int(row['tackles'])} tkl</p>", unsafe_allow_html=True)
                c8.markdown(f"<p style='font-size:14px; font-weight:700; color:{rating_color}; margin:8px 0;'>{row['rating']}</p>", unsafe_allow_html=True)

                st.markdown("<hr style='margin:2px 0; border:none; border-top:1px solid #F9FAFB;'>", unsafe_allow_html=True)