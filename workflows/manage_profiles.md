# Manage Profiles

## Objective
Create, edit, or delete user profiles with calculated nutrition targets.

## Inputs
- Profile form data: name, age, weight_kg, height_cm, gender, activity_level, fitness_goal

## Tool Chain
1. `tools/nutrition_calc.py:calculate_targets()` — Compute BMR, TDEE, and macro targets
2. `tools/db_helpers.py:create_profile()` or `update_profile()` — Save to database

## Constraints
- Maximum 2 profiles (enforced in the UI by hiding the create form at count >= 2)
- All profile fields are required (enforced by form validation + DB CHECK constraints)

## TDEE Calculation
- BMR: Mifflin-St Jeor equation
- TDEE: BMR x activity multiplier
- Goal adjustment: lose = -20%, maintain = 0%, gain = +10%
- Protein: 2.0/1.6/2.2 g/kg by goal
- Fat: 25% of total calories
- Carbs: remainder

## Edge Cases

### Profile edit triggers recalculation
- Always recalculate targets when any field changes
- Never reuse stale values from previous save

### Extreme values
- DB CHECK constraints prevent: age <= 0 or >= 150, weight <= 0, height <= 0
- Form min/max values provide UI-level validation

### Profile deletion
- CASCADE delete removes all associated meals and meal_items
- Confirmation dialog required before deletion
- If the deleted profile was active, sidebar switches to remaining profile
