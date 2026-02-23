# Daily Dashboard

## Objective
Render the daily nutrition dashboard showing intake vs targets for the active profile.

## Inputs
- Active profile ID (from sidebar session state)
- Date (defaults to today on Dashboard page; selectable on History page)

## Tool Chain
1. `tools/db_helpers.py:get_daily_totals()` — Summed calories/protein/fat/carbs
2. `tools/db_helpers.py:get_meals_for_date()` — Individual meals with nested items
3. Profile targets from `st.session_state["active_profile"]`

## Output
- 4 metric cards with progress bars (Calories, Protein, Fat, Carbs)
- Grouped bar chart: Consumed vs Target for each macro
- Donut chart: Macro breakdown by calorie contribution
- Meal timeline: chronological list of meals with expandable item details

## Edge Cases

### No meals logged
- Show friendly message: "No meals logged today"
- Hide charts and meal timeline (use st.stop())

### No profile created
- Show redirect message to Profiles page
- Use st.stop() to prevent errors from missing profile data

### Intake exceeds target
- Progress bars cap at 100% (use min() to avoid overflow)
- Delta color changes to indicate over-target
- Charts still show full values for transparency

### History page variant
- Same layout but with date picker and profile selector
- Also includes 7-day trend bar chart with target line overlay
