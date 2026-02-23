"""
NutriSync AI -- Streamlit Entrypoint
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from tools.db_init import init_database
from tools.db_helpers import get_profiles
from tools.ui_components import CUSTOM_CSS, sidebar_brand

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

st.set_page_config(
    page_title="NutriSync AI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

init_database()

dashboard = st.Page("pages/01_dashboard.py", title="Dashboard", default=True)
log_meal = st.Page("pages/02_log_meal.py", title="Log Meal")
profiles = st.Page("pages/03_profiles.py", title="Profiles")
history = st.Page("pages/04_history.py", title="History")

pg = st.navigation([dashboard, log_meal, profiles, history])

sidebar_brand()

groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    st.sidebar.warning(
        "**Groq API key not set.**\n\n"
        "Meal logging requires a Groq API key.\n\n"
        "1. Visit [console.groq.com/keys](https://console.groq.com/keys)\n"
        "2. Create a free API key\n"
        "3. Add `GROQ_API_KEY=your_key` to the `.env` file\n"
        "4. Restart the app",
    )

all_profiles = get_profiles()

if all_profiles:
    profile_options = {p["id"]: p["name"] for p in all_profiles}

    if "active_profile_id" not in st.session_state:
        st.session_state["active_profile_id"] = all_profiles[0]["id"]

    if st.session_state["active_profile_id"] not in profile_options:
        st.session_state["active_profile_id"] = all_profiles[0]["id"]

    selected_id = st.sidebar.selectbox(
        "Active Profile",
        options=list(profile_options.keys()),
        format_func=lambda pid: profile_options[pid],
        key="profile_switcher",
        index=list(profile_options.keys()).index(st.session_state["active_profile_id"]),
    )
    st.session_state["active_profile_id"] = selected_id

    st.session_state["active_profile"] = next(
        p for p in all_profiles if p["id"] == selected_id
    )

    profile = st.session_state["active_profile"]
    st.sidebar.markdown(f"""
    <div style="
        background:#141414;
        border-radius:8px;
        padding:0.6rem 0.75rem;
        margin-top:0.5rem;
        border:1px solid #1F1F1F;
    ">
        <div style="color:#525252;font-size:0.65rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.4rem;">Daily Targets</div>
        <div style="display:flex;justify-content:space-between;gap:0.3rem;">
            <div style="text-align:center;">
                <div style="color:#FACC15;font-size:0.9rem;font-weight:700;">{profile['target_calories_kcal']:.0f}</div>
                <div style="color:#525252;font-size:0.58rem;font-weight:600;">KCAL</div>
            </div>
            <div style="text-align:center;">
                <div style="color:#FACC15;font-size:0.9rem;font-weight:700;">{profile['target_protein_g']:.0f}g</div>
                <div style="color:#525252;font-size:0.58rem;font-weight:600;">PROT</div>
            </div>
            <div style="text-align:center;">
                <div style="color:#FACC15;font-size:0.9rem;font-weight:700;">{profile['target_fat_g']:.0f}g</div>
                <div style="color:#525252;font-size:0.58rem;font-weight:600;">FAT</div>
            </div>
            <div style="text-align:center;">
                <div style="color:#FACC15;font-size:0.9rem;font-weight:700;">{profile['target_carbs_g']:.0f}g</div>
                <div style="color:#525252;font-size:0.58rem;font-weight:600;">CARB</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.info("No profiles yet. Create one in the **Profiles** page to get started.")
    st.session_state.pop("active_profile_id", None)
    st.session_state.pop("active_profile", None)

pg.run()
