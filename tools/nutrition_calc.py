"""
TDEE and macronutrient target calculator using the Mifflin-St Jeor equation.

Pure deterministic math — no AI, no external APIs.
"""

# Activity multipliers for TDEE calculation
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,       # Little or no exercise
    "light": 1.375,         # Light exercise 1-3 days/week
    "moderate": 1.55,       # Moderate exercise 3-5 days/week
    "active": 1.725,        # Hard exercise 6-7 days/week
    "very_active": 1.9,     # Very hard exercise, physical job
}

# Goal-based calorie adjustments
GOAL_CALORIE_MULTIPLIERS = {
    "lose_weight": 0.80,    # 20% deficit
    "maintain": 1.00,       # No adjustment
    "gain_muscle": 1.10,    # 10% surplus
}

# Goal-based protein targets (grams per kg bodyweight)
GOAL_PROTEIN_PER_KG = {
    "lose_weight": 2.0,     # Higher protein preserves muscle in deficit
    "maintain": 1.6,        # Standard active adult
    "gain_muscle": 2.2,     # Higher protein supports muscle synthesis
}

# Macronutrient calorie density (kcal per gram)
KCAL_PER_GRAM_PROTEIN = 4
KCAL_PER_GRAM_FAT = 9
KCAL_PER_GRAM_CARBS = 4

# Fat is set to 25% of total calories for all goals
FAT_CALORIE_FRACTION = 0.25


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor equation.

    Args:
        weight_kg: Body weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: 'male' or 'female'

    Returns:
        BMR in kcal/day
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender == "male":
        return base + 5
    else:
        return base - 161


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure.

    Args:
        bmr: Basal Metabolic Rate in kcal/day
        activity_level: One of 'sedentary', 'light', 'moderate', 'active', 'very_active'

    Returns:
        TDEE in kcal/day
    """
    multiplier = ACTIVITY_MULTIPLIERS[activity_level]
    return bmr * multiplier


def calculate_targets(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    fitness_goal: str,
) -> dict:
    """
    Calculate all nutritional targets for a profile.

    Args:
        weight_kg: Body weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: 'male' or 'female'
        activity_level: One of 'sedentary', 'light', 'moderate', 'active', 'very_active'
        fitness_goal: One of 'lose_weight', 'maintain', 'gain_muscle'

    Returns:
        Dictionary with keys: bmr_kcal, tdee_kcal, target_calories_kcal,
        target_protein_g, target_fat_g, target_carbs_g
    """
    # Step 1: BMR
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)

    # Step 2: TDEE
    tdee = calculate_tdee(bmr, activity_level)

    # Step 3: Goal-adjusted calories
    target_calories = tdee * GOAL_CALORIE_MULTIPLIERS[fitness_goal]

    # Step 4: Macros
    # Protein: set by goal and bodyweight
    protein_g = weight_kg * GOAL_PROTEIN_PER_KG[fitness_goal]

    # Fat: 25% of total calories
    fat_calories = target_calories * FAT_CALORIE_FRACTION
    fat_g = fat_calories / KCAL_PER_GRAM_FAT

    # Carbs: whatever remains after protein and fat
    protein_calories = protein_g * KCAL_PER_GRAM_PROTEIN
    remaining_calories = target_calories - protein_calories - fat_calories
    carbs_g = max(remaining_calories / KCAL_PER_GRAM_CARBS, 0)  # Floor at 0

    return {
        "bmr_kcal": round(bmr, 1),
        "tdee_kcal": round(tdee, 1),
        "target_calories_kcal": round(target_calories, 1),
        "target_protein_g": round(protein_g, 1),
        "target_fat_g": round(fat_g, 1),
        "target_carbs_g": round(carbs_g, 1),
    }


# --- Quick self-test when run directly ---
if __name__ == "__main__":
    # Test case: 30-year-old male, 80kg, 180cm, moderate activity, maintain
    result = calculate_targets(80, 180, 30, "male", "moderate", "maintain")
    print("Test: 30M, 80kg, 180cm, moderate, maintain")
    for k, v in result.items():
        print(f"  {k}: {v}")

    # Expected BMR = (10*80) + (6.25*180) - (5*30) + 5 = 800 + 1125 - 150 + 5 = 1780
    assert abs(result["bmr_kcal"] - 1780.0) < 1, f"BMR expected 1780, got {result['bmr_kcal']}"

    # Expected TDEE = 1780 * 1.55 = 2759
    assert abs(result["tdee_kcal"] - 2759.0) < 1, f"TDEE expected 2759, got {result['tdee_kcal']}"

    print("\n[OK] All assertions passed.")
