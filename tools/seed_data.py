"""
Seed data script for NutriSync AI.

Creates two sample profiles and several days of meal data for testing
the dashboard and history views without needing a Gemini API key.

Only runs if the database has zero profiles.
"""

import os
from datetime import date, timedelta

from tools.db_init import init_database
from tools.db_helpers import get_profile_count, create_profile, create_meal
from tools.nutrition_calc import calculate_targets

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nutrisync.db")

# Sample meal data (pre-parsed, no Gemini needed)
SAMPLE_MEALS = [
    {
        "label": "breakfast",
        "time": "08:30",
        "raw_input": "Two scrambled eggs with toast and butter",
        "items": [
            {"food_name": "Scrambled eggs (2 large)", "estimated_weight_g": 120, "calories": 182, "protein_g": 12.6, "fat_g": 13.4, "carbs_g": 1.6, "confidence": "high"},
            {"food_name": "Toast with butter", "estimated_weight_g": 45, "calories": 165, "protein_g": 3.2, "fat_g": 7.8, "carbs_g": 20.5, "confidence": "high"},
        ],
    },
    {
        "label": "lunch",
        "time": "12:30",
        "raw_input": "Grilled chicken salad with olive oil dressing",
        "items": [
            {"food_name": "Grilled chicken breast", "estimated_weight_g": 150, "calories": 248, "protein_g": 46.5, "fat_g": 5.4, "carbs_g": 0, "confidence": "high"},
            {"food_name": "Mixed green salad", "estimated_weight_g": 200, "calories": 35, "protein_g": 2.5, "fat_g": 0.5, "carbs_g": 6.0, "confidence": "medium"},
            {"food_name": "Olive oil dressing", "estimated_weight_g": 30, "calories": 240, "protein_g": 0, "fat_g": 27.0, "carbs_g": 0.5, "confidence": "medium"},
        ],
    },
    {
        "label": "snack",
        "time": "15:00",
        "raw_input": "Apple and a handful of almonds",
        "items": [
            {"food_name": "Apple (medium)", "estimated_weight_g": 180, "calories": 95, "protein_g": 0.5, "fat_g": 0.3, "carbs_g": 25.0, "confidence": "high"},
            {"food_name": "Almonds (handful)", "estimated_weight_g": 28, "calories": 164, "protein_g": 6.0, "fat_g": 14.1, "carbs_g": 6.1, "confidence": "medium"},
        ],
    },
    {
        "label": "dinner",
        "time": "19:00",
        "raw_input": "Salmon fillet with brown rice and steamed broccoli",
        "items": [
            {"food_name": "Salmon fillet", "estimated_weight_g": 180, "calories": 367, "protein_g": 36.2, "fat_g": 22.1, "carbs_g": 0, "confidence": "high"},
            {"food_name": "Brown rice", "estimated_weight_g": 200, "calories": 248, "protein_g": 5.5, "fat_g": 2.0, "carbs_g": 51.7, "confidence": "high"},
            {"food_name": "Steamed broccoli", "estimated_weight_g": 150, "calories": 52, "protein_g": 4.3, "fat_g": 0.6, "carbs_g": 10.2, "confidence": "high"},
        ],
    },
    {
        "label": "breakfast",
        "time": "09:00",
        "raw_input": "Greek yogurt with honey and granola",
        "items": [
            {"food_name": "Greek yogurt", "estimated_weight_g": 200, "calories": 146, "protein_g": 20.0, "fat_g": 3.8, "carbs_g": 8.0, "confidence": "high"},
            {"food_name": "Honey", "estimated_weight_g": 20, "calories": 64, "protein_g": 0.1, "fat_g": 0, "carbs_g": 17.3, "confidence": "high"},
            {"food_name": "Granola", "estimated_weight_g": 50, "calories": 225, "protein_g": 5.5, "fat_g": 8.5, "carbs_g": 33.0, "confidence": "medium"},
        ],
    },
    {
        "label": "lunch",
        "time": "13:00",
        "raw_input": "Turkey sandwich with cheese and a banana",
        "items": [
            {"food_name": "Turkey sandwich with cheese", "estimated_weight_g": 250, "calories": 380, "protein_g": 28.0, "fat_g": 14.0, "carbs_g": 36.0, "confidence": "medium"},
            {"food_name": "Banana", "estimated_weight_g": 120, "calories": 105, "protein_g": 1.3, "fat_g": 0.4, "carbs_g": 27.0, "confidence": "high"},
        ],
    },
    {
        "label": "dinner",
        "time": "19:30",
        "raw_input": "Pasta with pesto and parmesan",
        "items": [
            {"food_name": "Pasta (cooked)", "estimated_weight_g": 250, "calories": 315, "protein_g": 11.0, "fat_g": 1.8, "carbs_g": 62.0, "confidence": "high"},
            {"food_name": "Pesto sauce", "estimated_weight_g": 40, "calories": 108, "protein_g": 3.2, "fat_g": 9.6, "carbs_g": 2.4, "confidence": "medium"},
            {"food_name": "Parmesan cheese", "estimated_weight_g": 20, "calories": 84, "protein_g": 7.6, "fat_g": 5.6, "carbs_g": 0.8, "confidence": "high"},
        ],
    },
]


def seed(db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Seed the database with sample profiles and meals.
    Only runs if no profiles exist.
    """
    init_database(db_path)

    if get_profile_count(db_path) > 0:
        print("Database already has profiles. Skipping seed.")
        return

    # --- Create two profiles ---
    profile1_data = {
        "name": "Alex",
        "age": 28,
        "weight_kg": 75.0,
        "height_cm": 178.0,
        "gender": "male",
        "activity_level": "moderate",
        "fitness_goal": "maintain",
    }
    targets1 = calculate_targets(**{k: v for k, v in profile1_data.items() if k != "name"})
    profile1_id = create_profile({**profile1_data, **targets1}, db_path)
    print(f"Created profile: {profile1_data['name']} (ID: {profile1_id})")

    profile2_data = {
        "name": "Jordan",
        "age": 26,
        "weight_kg": 62.0,
        "height_cm": 165.0,
        "gender": "female",
        "activity_level": "active",
        "fitness_goal": "lose_weight",
    }
    targets2 = calculate_targets(**{k: v for k, v in profile2_data.items() if k != "name"})
    profile2_id = create_profile({**profile2_data, **targets2}, db_path)
    print(f"Created profile: {profile2_data['name']} (ID: {profile2_id})")

    # --- Seed meals for the past 5 days ---
    today = date.today()
    meal_idx = 0

    for days_ago in range(5, -1, -1):
        meal_date = (today - timedelta(days=days_ago)).isoformat()

        # Give each day 2-3 meals, alternating between profiles
        num_meals = 3 if days_ago % 2 == 0 else 2
        target_profile = profile1_id if days_ago % 2 == 0 else profile2_id

        for _ in range(num_meals):
            meal = SAMPLE_MEALS[meal_idx % len(SAMPLE_MEALS)]
            create_meal(
                profile_id=target_profile,
                meal_date=meal_date,
                meal_time=meal["time"],
                meal_label=meal["label"],
                raw_input=meal["raw_input"],
                parsed_items=meal["items"],
                model_name="seed_data",
                db_path=db_path,
            )
            meal_idx += 1

        profile_name = profile1_data["name"] if target_profile == profile1_id else profile2_data["name"]
        print(f"  {meal_date}: {num_meals} meals for {profile_name}")

    print(f"\n[OK] Seeded {meal_idx} meals across 6 days.")


if __name__ == "__main__":
    seed()
