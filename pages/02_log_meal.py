"""
NutriSync AI -- Meal Logging Page
"""

import streamlit as st
from datetime import datetime, date, time as dt_time

from tools.groq_meal_parser import parse_meal
from tools.db_helpers import create_meal, get_daily_totals, get_profiles
from tools.ui_components import page_header, section_header, styled_metric, confidence_badge

page_header("Log Meal", "Describe your meal in natural language and let AI extract the nutritional data.")

import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

if not os.getenv("GROQ_API_KEY"):
    st.error(
        "**Groq API key required for meal logging.**\n\n"
        "Add `GROQ_API_KEY=your_key` to the `.env` file and restart the app.\n\n"
        "Get a free key at [console.groq.com/keys](https://console.groq.com/keys)."
    )
    st.stop()

profiles = get_profiles()
if not profiles:
    st.warning("Create a profile first in the **Profiles** page before logging meals.")
    st.stop()

section_header("What did you eat?")

profile_options = {p["id"]: p["name"] for p in profiles}
active_id = st.session_state.get("active_profile_id", profiles[0]["id"])
if active_id not in profile_options:
    active_id = profiles[0]["id"]

col_profile, col_date, col_time, col_label = st.columns([2, 1.5, 1, 1.5])

with col_profile:
    selected_profile_id = st.selectbox(
        "Profile",
        options=list(profile_options.keys()),
        format_func=lambda pid: profile_options[pid],
        index=list(profile_options.keys()).index(active_id),
        key="meal_profile_select",
    )

with col_date:
    meal_date = st.date_input("Date", value=date.today(), key="meal_date_input")

with col_time:
    meal_time = st.time_input("Time", value=datetime.now().time(), key="meal_time_input")

with col_label:
    meal_label = st.selectbox(
        "Meal Type",
        options=[None, "breakfast", "lunch", "dinner", "snack"],
        format_func=lambda x: x.capitalize() if x else "-- Select --",
        key="meal_label_select",
    )

meal_text = st.text_area(
    "Describe your meal",
    placeholder="e.g., A large bowl of pasta with pesto, parmesan cheese, and a side of Greek yogurt with honey",
    height=100,
    key="meal_text_area",
)

if st.button("Analyze Meal", type="primary", disabled=not meal_text.strip()):
    with st.spinner("Analyzing with Groq AI..."):
        result = parse_meal(meal_text.strip())

    if result["success"]:
        st.session_state["parsed_meal"] = result
        st.session_state["parsed_meal_text"] = meal_text.strip()
    else:
        if result.get("rate_limited"):
            st.warning(
                "**Rate limit temporarily hit.**\n\n"
                "Groq allows 30 requests per minute on the free tier. "
                "Wait a moment and click **Analyze Meal** again."
            )
        else:
            st.error(f"**Parsing failed:** {result.get('error', 'Unknown error')}")
        st.session_state.pop("parsed_meal", None)

if "parsed_meal" in st.session_state:
    result = st.session_state["parsed_meal"]
    items = result["items"]

    if not items:
        st.warning("No food items detected. The input may not describe a meal.")
        if result.get("notes"):
            st.info(f"**AI Notes:** {result['notes']}")
    else:
        section_header("Parsed Results")

        if result.get("notes"):
            st.info(f"**AI Notes:** {result['notes']}")

        total_cal = sum(item.get("calories", 0) for item in items)
        high_cal = [i for i in items if i.get("calories", 0) > 2000]
        if high_cal:
            st.warning("Some items have unusually high calorie estimates (>2000 kcal). Please review before saving.")
        elif total_cal > 4000:
            st.warning(f"Total meal calories ({total_cal:.0f} kcal) seem high. Please review before saving.")

        if "edited_items" not in st.session_state:
            st.session_state["edited_items"] = items.copy()

        edited_items = []
        for i, item in enumerate(st.session_state["edited_items"]):
            with st.container(border=True):
                row_header, row_conf = st.columns([5, 1])
                with row_header:
                    food_name = st.text_input("Food", value=item["food_name"], key=f"food_{i}", label_visibility="collapsed")
                with row_conf:
                    confidence_badge(item.get("confidence", "n/a"))

                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    weight = st.number_input("Weight (g)", value=float(item.get("estimated_weight_g", 0)), min_value=0.0, step=10.0, key=f"wt_{i}")
                with c2:
                    cals = st.number_input("Calories", value=float(item.get("calories", 0)), min_value=0.0, step=10.0, key=f"cal_{i}")
                with c3:
                    prot = st.number_input("Protein (g)", value=float(item.get("protein_g", 0)), min_value=0.0, step=1.0, key=f"pro_{i}")
                with c4:
                    fat = st.number_input("Fat (g)", value=float(item.get("fat_g", 0)), min_value=0.0, step=1.0, key=f"fat_{i}")
                with c5:
                    carbs = st.number_input("Carbs (g)", value=float(item.get("carbs_g", 0)), min_value=0.0, step=1.0, key=f"carb_{i}")

            edited_items.append({
                "food_name": food_name,
                "estimated_weight_g": weight,
                "calories": cals,
                "protein_g": prot,
                "fat_g": fat,
                "carbs_g": carbs,
                "confidence": item.get("confidence", "medium"),
            })

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        tcol1, tcol2, tcol3, tcol4 = st.columns(4)
        with tcol1:
            styled_metric("Total Calories", f"{sum(i['calories'] for i in edited_items):.0f} kcal")
        with tcol2:
            styled_metric("Total Protein", f"{sum(i['protein_g'] for i in edited_items):.1f}g")
        with tcol3:
            styled_metric("Total Fat", f"{sum(i['fat_g'] for i in edited_items):.1f}g")
        with tcol4:
            styled_metric("Total Carbs", f"{sum(i['carbs_g'] for i in edited_items):.1f}g")

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
        if st.button("Save Meal", type="primary"):
            save_items = edited_items

            meal_id = create_meal(
                profile_id=selected_profile_id,
                meal_date=meal_date.isoformat(),
                meal_time=meal_time.strftime("%H:%M"),
                meal_label=meal_label,
                raw_input=st.session_state.get("parsed_meal_text", meal_text),
                parsed_items=save_items,
                model_name=result.get("model"),
            )

            st.success(f"Meal saved! (ID: {meal_id})")

            daily = get_daily_totals(selected_profile_id, meal_date.isoformat())
            profile = next(p for p in profiles if p["id"] == selected_profile_id)

            section_header("Today's Running Totals")
            dcol1, dcol2, dcol3, dcol4 = st.columns(4)
            with dcol1:
                styled_metric("Calories", f"{daily['total_calories']:.0f}", subtitle=f"of {profile['target_calories_kcal']:.0f} target")
            with dcol2:
                styled_metric("Protein", f"{daily['total_protein']:.1f}g", subtitle=f"of {profile['target_protein_g']:.0f}g target")
            with dcol3:
                styled_metric("Fat", f"{daily['total_fat']:.1f}g", subtitle=f"of {profile['target_fat_g']:.0f}g target")
            with dcol4:
                styled_metric("Carbs", f"{daily['total_carbs']:.1f}g", subtitle=f"of {profile['target_carbs_g']:.0f}g target")

            st.session_state.pop("parsed_meal", None)
            st.session_state.pop("parsed_meal_text", None)
            st.session_state.pop("edited_items", None)
