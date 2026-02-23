"""
NutriSync AI -- Profile Management Page
"""

import streamlit as st
from tools.db_helpers import (
    get_profiles,
    get_profile_count,
    create_profile,
    update_profile,
    delete_profile,
)
from tools.nutrition_calc import calculate_targets
from tools.ui_components import page_header, section_header, styled_metric

ACTIVITY_LABELS = {
    "sedentary": "Sedentary (little or no exercise)",
    "light": "Light (1-3 days/week)",
    "moderate": "Moderate (3-5 days/week)",
    "active": "Active (6-7 days/week)",
    "very_active": "Very Active (hard exercise, physical job)",
}

GOAL_LABELS = {
    "lose_weight": "Lose Weight (-20% calories)",
    "maintain": "Maintain Weight",
    "gain_muscle": "Gain Muscle (+10% calories)",
}

GENDER_LABELS = {"male": "Male", "female": "Female"}


def _build_profile_data(name, age, weight, height, gender, activity, goal):
    targets = calculate_targets(weight, height, age, gender, activity, goal)
    return {
        "name": name,
        "age": age,
        "weight_kg": weight,
        "height_cm": height,
        "gender": gender,
        "activity_level": activity,
        "fitness_goal": goal,
        **targets,
    }


def _render_profile_card(profile, index):
    with st.container(border=True):
        col_info, col_targets = st.columns([1, 1])

        with col_info:
            st.markdown(f"""
            <div style="
                font-size:1.3rem;font-weight:700;color:#F5F5F5;margin-bottom:0.5rem;
                display:flex;align-items:center;gap:0.5rem;
            ">
                <span style="width:8px;height:8px;border-radius:50%;background:#FACC15;display:inline-block;"></span>
                {profile['name']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown(
                f"**Age:** {profile['age']} | "
                f"**Weight:** {profile['weight_kg']} kg | "
                f"**Height:** {profile['height_cm']} cm | "
                f"**Gender:** {GENDER_LABELS.get(profile['gender'], profile['gender'])}"
            )
            st.markdown(
                f"**Activity:** {ACTIVITY_LABELS.get(profile['activity_level'], profile['activity_level'])}"
            )
            st.markdown(
                f"**Goal:** {GOAL_LABELS.get(profile['fitness_goal'], profile['fitness_goal'])}"
            )

        with col_targets:
            st.markdown("""
            <div style="color:#737373;font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">
                Daily Targets
            </div>
            """, unsafe_allow_html=True)
            tcol1, tcol2 = st.columns(2)
            with tcol1:
                styled_metric("BMR", f"{profile['bmr_kcal']:.0f} kcal")
                styled_metric("Calories", f"{profile['target_calories_kcal']:.0f} kcal")
            with tcol2:
                styled_metric("TDEE", f"{profile['tdee_kcal']:.0f} kcal")
                styled_metric("Macros", f"P:{profile['target_protein_g']:.0f} F:{profile['target_fat_g']:.0f} C:{profile['target_carbs_g']:.0f}")

        btn_col1, btn_col2, btn_spacer = st.columns([1, 1, 4])
        with btn_col1:
            if st.button("Edit", key=f"edit_{profile['id']}"):
                st.session_state[f"editing_profile_{profile['id']}"] = True
                st.rerun()
        with btn_col2:
            if st.button("Delete", key=f"delete_{profile['id']}", type="secondary"):
                st.session_state[f"confirm_delete_{profile['id']}"] = True
                st.rerun()

        if st.session_state.get(f"confirm_delete_{profile['id']}"):
            st.warning(f"Are you sure you want to delete **{profile['name']}**? All their meal data will also be deleted.")
            cdel1, cdel2, cdel_spacer = st.columns([1, 1, 4])
            with cdel1:
                if st.button("Yes, delete", key=f"confirm_yes_{profile['id']}", type="primary"):
                    delete_profile(profile["id"])
                    st.session_state.pop(f"confirm_delete_{profile['id']}", None)
                    st.success(f"Profile '{profile['name']}' deleted.")
                    st.rerun()
            with cdel2:
                if st.button("Cancel", key=f"confirm_no_{profile['id']}"):
                    st.session_state.pop(f"confirm_delete_{profile['id']}", None)
                    st.rerun()

        if st.session_state.get(f"editing_profile_{profile['id']}"):
            _render_edit_form(profile)


def _render_edit_form(profile):
    st.divider()
    section_header("Edit Profile")

    with st.form(f"edit_form_{profile['id']}"):
        name = st.text_input("Name", value=profile["name"])

        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=profile["age"])
            gender = st.selectbox(
                "Gender",
                options=list(GENDER_LABELS.keys()),
                format_func=lambda g: GENDER_LABELS[g],
                index=list(GENDER_LABELS.keys()).index(profile["gender"]),
            )
        with col2:
            weight = st.number_input(
                "Weight (kg)", min_value=20.0, max_value=300.0,
                value=float(profile["weight_kg"]), step=0.5,
            )
            activity = st.selectbox(
                "Activity Level",
                options=list(ACTIVITY_LABELS.keys()),
                format_func=lambda a: ACTIVITY_LABELS[a],
                index=list(ACTIVITY_LABELS.keys()).index(profile["activity_level"]),
            )
        with col3:
            height = st.number_input(
                "Height (cm)", min_value=50.0, max_value=260.0,
                value=float(profile["height_cm"]), step=0.5,
            )
            goal = st.selectbox(
                "Fitness Goal",
                options=list(GOAL_LABELS.keys()),
                format_func=lambda g: GOAL_LABELS[g],
                index=list(GOAL_LABELS.keys()).index(profile["fitness_goal"]),
            )

        sub_col1, sub_col2, sub_spacer = st.columns([1, 1, 4])
        with sub_col1:
            submitted = st.form_submit_button("Save Changes", type="primary")
        with sub_col2:
            cancelled = st.form_submit_button("Cancel")

        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                data = _build_profile_data(name.strip(), age, weight, height, gender, activity, goal)
                update_profile(profile["id"], data)
                st.session_state.pop(f"editing_profile_{profile['id']}", None)
                st.success(f"Profile '{name}' updated!")
                st.rerun()

        if cancelled:
            st.session_state.pop(f"editing_profile_{profile['id']}", None)
            st.rerun()


def _render_create_form():
    section_header("Create New Profile")

    with st.form("create_profile_form"):
        name = st.text_input("Name")

        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("Age", min_value=1, max_value=120, value=30)
            gender = st.selectbox(
                "Gender",
                options=list(GENDER_LABELS.keys()),
                format_func=lambda g: GENDER_LABELS[g],
            )
        with col2:
            weight = st.number_input(
                "Weight (kg)", min_value=20.0, max_value=300.0, value=70.0, step=0.5,
            )
            activity = st.selectbox(
                "Activity Level",
                options=list(ACTIVITY_LABELS.keys()),
                format_func=lambda a: ACTIVITY_LABELS[a],
                index=2,
            )
        with col3:
            height = st.number_input(
                "Height (cm)", min_value=50.0, max_value=260.0, value=170.0, step=0.5,
            )
            goal = st.selectbox(
                "Fitness Goal",
                options=list(GOAL_LABELS.keys()),
                format_func=lambda g: GOAL_LABELS[g],
                index=1,
            )

        submitted = st.form_submit_button("Create Profile", type="primary")

        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                data = _build_profile_data(name.strip(), age, weight, height, gender, activity, goal)
                profile_id = create_profile(data)
                st.success(f"Profile '{name}' created! (ID: {profile_id})")
                st.rerun()


# ============================================================
# PAGE LAYOUT
# ============================================================

page_header("Profiles", "Manage individual profiles with unique metrics and fitness goals.")

profiles = get_profiles()
profile_count = len(profiles)

if profiles:
    for idx, profile in enumerate(profiles):
        _render_profile_card(profile, idx)
else:
    st.info("No profiles created yet. Add your first profile below.")

st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
if profile_count < 2:
    _render_create_form()
else:
    st.caption("Maximum of 2 profiles reached. Delete an existing profile to create a new one.")
