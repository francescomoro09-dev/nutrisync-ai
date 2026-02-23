"""
NutriSync AI -- History Page
"""

import streamlit as st
from datetime import date, timedelta

from tools.db_helpers import get_profiles, get_meals_for_date, get_daily_totals, get_date_range_summary
from tools.ui_components import (
    page_header, section_header, styled_metric, styled_progress,
    meal_card_header, render_vega_chart,
)

page_header("History", "Browse past days' nutrition data.")

profiles = get_profiles()
if not profiles:
    st.info("No profiles created yet. Head to the **Profiles** page to get started.")
    st.stop()

col_profile, col_date = st.columns([1, 1])

with col_profile:
    profile_options = {p["id"]: p["name"] for p in profiles}
    active_id = st.session_state.get("active_profile_id", profiles[0]["id"])
    if active_id not in profile_options:
        active_id = profiles[0]["id"]

    selected_id = st.selectbox(
        "Profile",
        options=list(profile_options.keys()),
        format_func=lambda pid: profile_options[pid],
        index=list(profile_options.keys()).index(active_id),
        key="history_profile",
    )

with col_date:
    selected_date = st.date_input(
        "Date",
        value=date.today(),
        max_value=date.today(),
        key="history_date",
    )

profile = next(p for p in profiles if p["id"] == selected_id)
date_str = selected_date.isoformat()

daily = get_daily_totals(selected_id, date_str)
meals = get_meals_for_date(selected_id, date_str)

if daily["meal_count"] == 0:
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    st.info(f"No meals logged on {selected_date.strftime('%B %d, %Y')} for {profile['name']}.")
else:
    section_header(selected_date.strftime("%A, %B %d, %Y"))

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

    section_header("Meals")

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

# 7-Day Trend
section_header("7-Day Trend")

end_date = selected_date
start_date = end_date - timedelta(days=6)
summary = get_date_range_summary(selected_id, start_date.isoformat(), end_date.isoformat())

if not summary:
    st.caption("No data in this 7-day window.")
else:
    bar_values = [
        {"date": row["meal_date"], "Calories": round(row["total_calories"], 0), "Meals": row["meal_count"]}
        for row in summary
    ]

    render_vega_chart({
        "layer": [
            {
                "data": {"values": bar_values},
                "mark": {"type": "bar", "cornerRadiusTopLeft": 6, "cornerRadiusTopRight": 6, "color": "#FACC15", "opacity": 0.8},
                "encoding": {
                    "x": {"field": "date", "type": "temporal", "title": "Date",
                           "axis": {"format": "%b %d"}},
                    "y": {"field": "Calories", "type": "quantitative", "title": "Calories"},
                    "tooltip": [
                        {"field": "date", "type": "temporal", "title": "Date", "format": "%b %d"},
                        {"field": "Calories", "type": "quantitative", "title": "Calories", "format": ".0f"},
                        {"field": "Meals", "type": "quantitative", "title": "Meals"},
                    ],
                },
            },
            {
                "data": {"values": [{"target": profile["target_calories_kcal"]}]},
                "mark": {"type": "rule", "color": "#EF4444", "strokeDash": [6, 4], "strokeWidth": 2},
                "encoding": {
                    "y": {"field": "target", "type": "quantitative"},
                },
            },
        ],
        "width": "container",
        "height": 250,
    }, height=300)
    st.caption(f"Dashed line = daily calorie target ({profile['target_calories_kcal']:.0f} kcal)")
