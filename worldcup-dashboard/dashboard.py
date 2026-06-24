import streamlit as st

st.set_page_config(
    page_title="World Cup 2022 Dashboard",
    page_icon="soccer",
    layout="wide"
)

# Global light theme styles
st.markdown("""
    <style>
        /* Main background */
        .stApp { background-color: #FFFFFF; }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #F8F9FA;
            border-right: 1px solid #E5E7EB;
        }

        /* Cards */
        .card {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        }

        /* Score header */
        .score-box {
            background: #F1F5F9;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
        }

        /* Badge colors */
        .badge-win  { background:#D1FAE5; color:#065F46; padding:2px 10px; border-radius:999px; font-size:13px; font-weight:600; }
        .badge-draw { background:#FEF3C7; color:#92400E; padding:2px 10px; border-radius:999px; font-size:13px; font-weight:600; }
        .badge-loss { background:#FEE2E2; color:#991B1B; padding:2px 10px; border-radius:999px; font-size:13px; font-weight:600; }

        /* Event icons row */
        .event-row { padding: 6px 0; border-bottom: 1px solid #F3F4F6; font-size: 14px; }

        /* Hide default Streamlit menu */
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# Home page content
st.title("World Cup 2022 Dashboard")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class='card'>
            <h3 style='margin:0; color:#1F4E79;'>32</h3>
            <p style='margin:0; color:#6B7280;'>Teams</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class='card'>
            <h3 style='margin:0; color:#1F4E79;'>64</h3>
            <p style='margin:0; color:#6B7280;'>Matches</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class='card'>
            <h3 style='margin:0; color:#1F4E79;'>8</h3>
            <p style='margin:0; color:#6B7280;'>Groups</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class='card'>
            <h3 style='margin:0; color:#1F4E79;'>Qatar</h3>
            <p style='margin:0; color:#6B7280;'>Host Country</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("### Navigate using the sidebar")
st.markdown("""
Use the pages in the sidebar to explore:
- **Standings** — All 8 group tables
- **Schedule** — Full fixture list by round
- **Match Detail** — Goals, cards, and events for any match
- **Teams** — Team profiles and match history
- **Player Stats** — Top scorers, assists, and cards
- **Live Scores** — Real-time match updates
""")