"""
NutriSync AI -- Daily Dashboard
"""

import streamlit as st
from datetime import date

from tools.db_helpers import get_profiles, get_meals_for_date, get_daily_totals
from tools.ui_components import (
    page_header, section_header, styled_metric, styled_progress,
    meal_card_header, render_vega_chart,
)

profiles = get_profiles()
if not profiles:
    page_header("Dashboard")
    st.info("No profiles created yet. Head to the **Profiles** page to get started.")
    st.stop()

active_id = st.session_state.get("active_profile_id")
if active_id is None:
    active_id = profiles[0]["id"]

profile = next((p for p in profiles if p["id"] == active_id), profiles[0])

page_header("Dashboard", f"{profile['name']}  \u00B7  {date.today().strftime('%A, %B %d, %Y')}")

today_str = date.today().isoformat()
daily = get_daily_totals(active_id, today_str)
meals = get_meals_for_date(active_id, today_str)

if daily["meal_count"] == 0:
    st.info("No meals logged today. Go to **Log Meal** to start tracking!")
    st.stop()

section_header("Daily Progress")

cal_consumed = daily["total_calories"]
cal_target = profile["target_calories_kcal"]
pro_consumed = daily["total_protein"]
pro_target = profile["target_protein_g"]
fat_consumed = daily["total_fat"]
fat_target = profile["target_fat_g"]
carb_consumed = daily["total_carbs"]
carb_target = profile["target_carbs_g"]

col1, col2, col3, col4 = st.columns(4)

with col1:
    styled_metric("Calories", f"{cal_consumed:.0f}", subtitle=f"of {cal_target:.0f} kcal target")
    styled_progress(cal_consumed, cal_target)

with col2:
    styled_metric("Protein", f"{pro_consumed:.1f}g", subtitle=f"of {pro_target:.0f}g target")
    styled_progress(pro_consumed, pro_target)

with col3:
    styled_metric("Fat", f"{fat_consumed:.1f}g", subtitle=f"of {fat_target:.0f}g target")
    styled_progress(fat_consumed, fat_target)

with col4:
    styled_metric("Carbs", f"{carb_consumed:.1f}g", subtitle=f"of {carb_target:.0f}g target")
    styled_progress(carb_consumed, carb_target)

# Charts
st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    section_header("Intake vs Target")
    render_vega_chart({
        "data": {
            "values": [
                {"Macro": "Calories (kcal)", "Type": "Consumed", "Amount": round(cal_consumed, 1)},
                {"Macro": "Calories (kcal)", "Type": "Target", "Amount": round(cal_target, 1)},
                {"Macro": "Protein (g)", "Type": "Consumed", "Amount": round(pro_consumed, 1)},
                {"Macro": "Protein (g)", "Type": "Target", "Amount": round(pro_target, 1)},
                {"Macro": "Fat (g)", "Type": "Consumed", "Amount": round(fat_consumed, 1)},
                {"Macro": "Fat (g)", "Type": "Target", "Amount": round(fat_target, 1)},
                {"Macro": "Carbs (g)", "Type": "Consumed", "Amount": round(carb_consumed, 1)},
                {"Macro": "Carbs (g)", "Type": "Target", "Amount": round(carb_target, 1)},
            ]
        },
        "mark": {"type": "bar", "cornerRadiusTopLeft": 6, "cornerRadiusTopRight": 6, "opacity": 0.85},
        "encoding": {
            "x": {"field": "Macro", "type": "nominal", "title": None,
                   "sort": ["Calories (kcal)", "Protein (g)", "Fat (g)", "Carbs (g)"]},
            "y": {"field": "Amount", "type": "quantitative", "title": "Amount"},
            "color": {
                "field": "Type", "type": "nominal",
                "scale": {"domain": ["Consumed", "Target"], "range": ["#FACC15", "#1F1F1F"]},
                "legend": {"orient": "top"},
            },
            "xOffset": {"field": "Type", "type": "nominal"},
        },
        "width": "container",
        "height": 300,
    })

with chart_col2:
    section_header("Macro Breakdown")
    total_macros = pro_consumed + fat_consumed + carb_consumed
    if total_macros > 0:
        render_vega_chart({
            "data": {
                "values": [
                    {"Macro": "Protein", "Grams": round(pro_consumed, 1), "Calories": round(pro_consumed * 4, 0)},
                    {"Macro": "Fat", "Grams": round(fat_consumed, 1), "Calories": round(fat_consumed * 9, 0)},
                    {"Macro": "Carbs", "Grams": round(carb_consumed, 1), "Calories": round(carb_consumed * 4, 0)},
                ]
            },
            "mark": {"type": "arc", "innerRadius": 55, "outerRadius": 120, "cornerRadius": 6, "stroke": "#000000", "strokeWidth": 2},
            "encoding": {
                "theta": {"field": "Calories", "type": "quantitative"},
                "color": {
                    "field": "Macro", "type": "nominal",
                    "scale": {"domain": ["Protein", "Fat", "Carbs"], "range": ["#FACC15", "#EAB308", "#A16207"]},
                    "legend": {"orient": "top"},
                },
                "tooltip": [
                    {"field": "Macro", "type": "nominal"},
                    {"field": "Grams", "type": "quantitative", "format": ".1f", "title": "Grams"},
                    {"field": "Calories", "type": "quantitative", "format": ".0f", "title": "Calories"},
                ],
            },
            "width": "container",
            "height": 300,
        })
    else:
        st.caption("No macro data to display yet.")

# Meal Timeline
section_header("Meals Today")

for meal in meals:
    label = meal.get("meal_label") or "Meal"
    time_str = meal.get("meal_time", "")

    with st.container(border=True):
        header_col, stats_col = st.columns([2, 3])

        with header_col:
            meal_card_header(label.capitalize(), time_str, meal["raw_input"])

        with stats_col:
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Cal", f"{meal['total_calories']:.0f}")
            with m2:
                st.metric("Pro", f"{meal['total_protein']:.1f}g")
            with m3:
                st.metric("Fat", f"{meal['total_fat']:.1f}g")
            with m4:
                st.metric("Carb", f"{meal['total_carbs']:.1f}g")

        if meal.get("items"):
            with st.expander(f"View {len(meal['items'])} item(s)"):
                md = "| Food | Weight (g) | Calories | Protein | Fat | Carbs | Conf. |\n"
                md += "|---|---|---|---|---|---|---|\n"
                for item in meal["items"]:
                    md += (
                        f"| {item.get('food_name', '')} "
                        f"| {item.get('estimated_weight_g', 0):.0f} "
                        f"| {item.get('calories', 0):.0f} "
                        f"| {item.get('protein_g', 0):.1f}g "
                        f"| {item.get('fat_g', 0):.1f}g "
                        f"| {item.get('carbs_g', 0):.1f}g "
                        f"| {item.get('confidence', '')} |\n"
                    )
                st.markdown(md)
