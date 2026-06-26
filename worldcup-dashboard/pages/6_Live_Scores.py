import streamlit as st
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import get_live_matches, get_match_detail, get_fixtures

st.set_page_config(page_title="Live Scores", page_icon="🔴", layout="wide")

st.title("Live Scores")
st.markdown("---")

# Auto-refresh every 15 seconds when there are live matches
def format_elapsed(elapsed):
    if elapsed is None:
        return ""
    return f"{int(elapsed)}'"

def status_display(status, elapsed):
    if status == "1H":
        return f"🟢 1st Half — {format_elapsed(elapsed)}", "#059669"
    elif status == "HT":
        return "🟡 Half Time", "#D97706"
    elif status == "2H":
        return f"🟢 2nd Half — {format_elapsed(elapsed)}", "#059669"
    elif status == "ET":
        return f"🟠 Extra Time — {format_elapsed(elapsed)}", "#EA580C"
    elif status == "P":
        return "🔵 Penalties", "#2563EB"
    elif status == "BT":
        return "🟠 Break Time", "#EA580C"
    else:
        return status, "#6B7280"

# ── Live matches ──────────────────────────────────────────────────────────
live_df = get_live_matches()

if live_df.empty:
    # No live matches — show a friendly message and recent results instead
    st.markdown("""
        <div style='text-align:center; padding:60px 0;'>
            <p style='font-size:48px; margin:0;'>⏸️</p>
            <h3 style='color:#374151; margin:16px 0 8px 0;'>No matches live right now</h3>
            <p style='color:#6B7280; font-size:15px;'>
                This page updates automatically when a match kicks off.<br>
                Check the schedule for upcoming fixtures.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Recent Results")

    # Show last 8 finished matches
    recent_df = get_fixtures()
    finished  = recent_df[recent_df["status"] == "FT"].tail(8).iloc[::-1]

    for _, row in finished.iterrows():
        col_home, col_score, col_away = st.columns([3, 2, 3])

        with col_home:
            st.markdown(
                f"<p style='text-align:right; font-size:16px; font-weight:600; margin:8px 0;'>"
                f"{row['home_team']}</p>",
                unsafe_allow_html=True
            )
        with col_score:
            st.markdown(
                f"<div style='text-align:center;'>"
                f"<p style='font-size:22px; font-weight:700; color:#1F4E79; margin:0;'>"
                f"{int(row['home_goals'])} - {int(row['away_goals'])}</p>"
                f"<p style='font-size:11px; color:#6B7280; margin:2px 0;'>FT</p>"
                f"<p style='font-size:11px; color:#9CA3AF; margin:0;'>{row['round']}</p>"
                f"</div>",
                unsafe_allow_html=True
            )
        with col_away:
            st.markdown(
                f"<p style='text-align:left; font-size:16px; font-weight:600; margin:8px 0;'>"
                f"{row['away_team']}</p>",
                unsafe_allow_html=True
            )

        st.markdown(
            "<hr style='margin:4px 0; border:none; border-top:1px solid #F3F4F6;'>",
            unsafe_allow_html=True
        )

else:
    # Live matches found
    st.markdown(f"### {len(live_df)} Match{'es' if len(live_df) > 1 else ''} Live Now")
    st.caption("Page refreshes every 15 seconds automatically.")

    # Auto refresh
    st.markdown(
        "<meta http-equiv='refresh' content='15'>",
        unsafe_allow_html=True
    )

    for _, row in live_df.iterrows():
        status_text, status_color = status_display(row["status"], row["elapsed"])

        st.markdown(
            f"<div style='border:2px solid {status_color}; border-radius:12px; "
            f"padding:20px 24px; margin-bottom:16px; background:#FAFAFA;'>"
            f"<div style='text-align:center; margin-bottom:12px;'>"
            f"<span style='font-size:13px; font-weight:600; color:{status_color};'>"
            f"{status_text}</span>"
            f"</div>"
            f"<div style='display:flex; justify-content:space-between; align-items:center;'>"
            f"<span style='font-size:20px; font-weight:700; flex:1; text-align:right;'>"
            f"{row['home_team']}</span>"
            f"<span style='font-size:36px; font-weight:800; color:#1F4E79; "
            f"flex:0 0 120px; text-align:center;'>"
            f"{int(row['home_goals'])} - {int(row['away_goals'])}</span>"
            f"<span style='font-size:20px; font-weight:700; flex:1; text-align:left;'>"
            f"{row['away_team']}</span>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True
        )

        # Show live events for this match
        match_df, events_df = get_match_detail(int(row["fixture_id"]))

        if not events_df.empty:
            goals = events_df[
                (events_df["event_type"] == "Goal") &
                (events_df["detail"] != "Missed Penalty")
            ].sort_values("minute")

            cards = events_df[
                events_df["event_type"] == "Card"
            ].sort_values("minute")

            if not goals.empty:
                st.markdown("**Goals**")
                for _, ev in goals.iterrows():
                    minute = f"{int(ev['minute'])}'"
                    if ev["extra_minute"] and ev["extra_minute"] > 0:
                        minute = f"{int(ev['minute'])}+{int(ev['extra_minute'])}'"
                    icon = "⚽ (OG)" if ev["detail"] == "Own Goal" else "⚽"
                    assist = f" ↳ {ev['assist_name']}" if ev["assist_name"] else ""
                    col_l, col_r = st.columns(2)
                    if ev["team"] == row["home_team"]:
                        col_l.markdown(f"<p style='text-align:right; font-size:13px; margin:2px 0;'>{icon} {ev['player_name']}{assist} {minute}</p>", unsafe_allow_html=True)
                    else:
                        col_r.markdown(f"<p style='text-align:left; font-size:13px; margin:2px 0;'>{minute} {icon} {ev['player_name']}{assist}</p>", unsafe_allow_html=True)

            if not cards.empty:
                st.markdown("**Cards**")
                for _, ev in cards.iterrows():
                    minute = f"{int(ev['minute'])}'"
                    icon = "🟨" if ev["detail"] == "Yellow Card" else "🟥"
                    col_l, col_r = st.columns(2)
                    if ev["team"] == row["home_team"]:
                        col_l.markdown(f"<p style='text-align:right; font-size:13px; margin:2px 0;'>{icon} {ev['player_name']} {minute}</p>", unsafe_allow_html=True)
                    else:
                        col_r.markdown(f"<p style='text-align:left; font-size:13px; margin:2px 0;'>{minute} {icon} {ev['player_name']}</p>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)