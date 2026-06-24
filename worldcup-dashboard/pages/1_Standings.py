import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import get_standings

st.set_page_config(page_title="Standings", page_icon="trophy", layout="wide")

st.title("Group Standings")
st.markdown("---")

df = get_standings()

if df.empty:
    st.warning("No standings data found. Run fetcher.py first.")
    st.stop()

# Form badge helper
def form_badges(form_str):
    if not form_str:
        return ""
    colors = {"W": "#D1FAE5", "D": "#FEF3C7", "L": "#FEE2E2"}
    text_colors = {"W": "#065F46", "D": "#92400E", "L": "#991B1B"}
    badges = ""
    for ch in form_str:
        bg  = colors.get(ch, "#F3F4F6")
        txt = text_colors.get(ch, "#374151")
        badges += (
            f"<span style='background:{bg}; color:{txt}; "
            f"padding:2px 7px; border-radius:999px; font-size:12px; "
            f"font-weight:600; margin-right:3px;'>{ch}</span>"
        )
    return badges

groups = sorted(df["group_name"].unique())

# Show two groups per row
for i in range(0, len(groups), 2):
    cols = st.columns(2)
    for j, col in enumerate(cols):
        if i + j >= len(groups):
            break
        group = groups[i + j]
        group_df = df[df["group_name"] == group].reset_index(drop=True)

        with col:
            st.markdown(f"### {group}")
            st.markdown("""
                <div style='background:#F8F9FA; border:1px solid #E5E7EB;
                            border-radius:10px; overflow:hidden; margin-bottom:16px;'>
            """, unsafe_allow_html=True)

            # Header row
            st.markdown("""
                <div style='display:grid; grid-template-columns:30px 1fr 40px 40px 40px 40px 40px 40px 60px 80px;
                            background:#1F4E79; color:white; font-size:12px; font-weight:600;
                            padding:8px 12px; gap:4px;'>
                    <span>#</span><span>Team</span>
                    <span style='text-align:center'>P</span>
                    <span style='text-align:center'>W</span>
                    <span style='text-align:center'>D</span>
                    <span style='text-align:center'>L</span>
                    <span style='text-align:center'>GF</span>
                    <span style='text-align:center'>GA</span>
                    <span style='text-align:center'>GD</span>
                    <span style='text-align:center'>Pts</span>
                </div>
            """, unsafe_allow_html=True)

            for _, row in group_df.iterrows():
                bg = "#FFFFFF" if row["rank"] % 2 == 0 else "#F9FAFB"
                # Highlight top 2 who qualify
                border_left = "4px solid #10B981" if row["rank"] <= 2 else "4px solid transparent"

                st.markdown(f"""
                    <div style='display:grid;
                                grid-template-columns:30px 1fr 40px 40px 40px 40px 40px 40px 60px 80px;
                                background:{bg}; font-size:13px; padding:8px 12px;
                                border-left:{border_left}; gap:4px; align-items:center;'>
                        <span style='color:#6B7280; font-weight:600;'>{row['rank']}</span>
                        <span style='font-weight:500;'>{row['team']}</span>
                        <span style='text-align:center; color:#374151;'>{row['played']}</span>
                        <span style='text-align:center; color:#374151;'>{row['won']}</span>
                        <span style='text-align:center; color:#374151;'>{row['drawn']}</span>
                        <span style='text-align:center; color:#374151;'>{row['lost']}</span>
                        <span style='text-align:center; color:#374151;'>{row['goals_for']}</span>
                        <span style='text-align:center; color:#374151;'>{row['goals_against']}</span>
                        <span style='text-align:center; color:#374151;'>{row['goal_diff']:+d}</span>
                        <span style='text-align:center; font-weight:700; color:#1F4E79;'>{row['points']}</span>
                    </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # Form guide
            if group_df["form"].notna().any():
                st.markdown("**Recent Form**")
                for _, row in group_df.iterrows():
                    badges = form_badges(row["form"])
                    if badges:
                        st.markdown(
                            f"<div style='margin-bottom:4px; font-size:13px;'>"
                            f"<span style='display:inline-block; width:140px; color:#374151;'>{row['team']}</span>"
                            f"{badges}</div>",
                            unsafe_allow_html=True
                        )

# Legend
st.markdown("---")
st.markdown("""
    <div style='font-size:12px; color:#6B7280;'>
        <span style='display:inline-block; width:12px; height:12px; background:#10B981;
                     border-radius:2px; margin-right:6px;'></span>
        Green bar = qualified for Round of 16
    </div>
""", unsafe_allow_html=True)