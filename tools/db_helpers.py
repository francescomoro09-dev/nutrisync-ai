"""
Database CRUD operations for NutriSync AI.

All functions take an explicit db_path parameter for testability.
Returns dictionaries (not raw tuples) using sqlite3.Row.
All write operations use explicit transactions.
"""

import sqlite3
import os
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nutrisync.db")


def _get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create a connection with row factory and foreign keys enabled."""
    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


# ============================================================
# PROFILES
# ============================================================

def get_profile_count(db_path: str = DEFAULT_DB_PATH) -> int:
    """Return the number of existing profiles."""
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute("SELECT COUNT(*) FROM profiles")
        return cursor.fetchone()[0]
    finally:
        conn.close()


def get_profiles(db_path: str = DEFAULT_DB_PATH) -> list[dict]:
    """Return all profiles as a list of dictionaries."""
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM profiles ORDER BY id")
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_profile(profile_id: int, db_path: str = DEFAULT_DB_PATH) -> dict | None:
    """Return a single profile by ID, or None if not found."""
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_profile(data: dict, db_path: str = DEFAULT_DB_PATH) -> int:
    """
    Insert a new profile and return its ID.

    Args:
        data: Dictionary with keys: name, age, weight_kg, height_cm, gender,
              activity_level, fitness_goal, bmr_kcal, tdee_kcal,
              target_calories_kcal, target_protein_g, target_fat_g, target_carbs_g

    Returns:
        The new profile's ID.
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            INSERT INTO profiles (
                name, age, weight_kg, height_cm, gender,
                activity_level, fitness_goal,
                bmr_kcal, tdee_kcal, target_calories_kcal,
                target_protein_g, target_fat_g, target_carbs_g
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"], data["age"], data["weight_kg"], data["height_cm"],
                data["gender"], data["activity_level"], data["fitness_goal"],
                data["bmr_kcal"], data["tdee_kcal"], data["target_calories_kcal"],
                data["target_protein_g"], data["target_fat_g"], data["target_carbs_g"],
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_profile(profile_id: int, data: dict, db_path: str = DEFAULT_DB_PATH) -> None:
    """
    Update an existing profile's fields and recalculated targets.

    Args:
        profile_id: The profile to update.
        data: Dictionary with the same keys as create_profile.
    """
    conn = _get_connection(db_path)
    try:
        conn.execute(
            """
            UPDATE profiles SET
                name = ?, age = ?, weight_kg = ?, height_cm = ?, gender = ?,
                activity_level = ?, fitness_goal = ?,
                bmr_kcal = ?, tdee_kcal = ?, target_calories_kcal = ?,
                target_protein_g = ?, target_fat_g = ?, target_carbs_g = ?,
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (
                data["name"], data["age"], data["weight_kg"], data["height_cm"],
                data["gender"], data["activity_level"], data["fitness_goal"],
                data["bmr_kcal"], data["tdee_kcal"], data["target_calories_kcal"],
                data["target_protein_g"], data["target_fat_g"], data["target_carbs_g"],
                profile_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def delete_profile(profile_id: int, db_path: str = DEFAULT_DB_PATH) -> None:
    """Delete a profile and all its associated meals (CASCADE)."""
    conn = _get_connection(db_path)
    try:
        conn.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        conn.commit()
    finally:
        conn.close()


# ============================================================
# MEALS
# ============================================================

def create_meal(
    profile_id: int,
    meal_date: str,
    meal_time: str,
    meal_label: str | None,
    raw_input: str,
    parsed_items: list[dict],
    model_name: str | None = None,
    db_path: str = DEFAULT_DB_PATH,
) -> int:
    """
    Insert a meal and all its parsed items in a single transaction.
    Computes totals from the items.

    Args:
        profile_id: Which profile logged this meal.
        meal_date: ISO date string 'YYYY-MM-DD'.
        meal_time: ISO time string 'HH:MM'.
        meal_label: Optional label ('breakfast', 'lunch', 'dinner', 'snack').
        raw_input: The original natural language text.
        parsed_items: List of dicts, each with keys: food_name, estimated_weight_g,
                      calories, protein_g, fat_g, carbs_g, confidence.
        model_name: Gemini model used for parsing.

    Returns:
        The new meal's ID.
    """
    # Compute totals from items
    total_calories = sum(item.get("calories", 0) for item in parsed_items)
    total_protein = sum(item.get("protein_g", 0) for item in parsed_items)
    total_fat = sum(item.get("fat_g", 0) for item in parsed_items)
    total_carbs = sum(item.get("carbs_g", 0) for item in parsed_items)

    conn = _get_connection(db_path)
    try:
        # Insert meal
        cursor = conn.execute(
            """
            INSERT INTO meals (
                profile_id, meal_date, meal_time, meal_label, raw_input,
                total_calories, total_protein, total_fat, total_carbs, gemini_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id, meal_date, meal_time, meal_label, raw_input,
                round(total_calories, 1), round(total_protein, 1),
                round(total_fat, 1), round(total_carbs, 1), model_name,
            ),
        )
        meal_id = cursor.lastrowid

        # Insert all meal items
        for item in parsed_items:
            conn.execute(
                """
                INSERT INTO meal_items (
                    meal_id, food_name, estimated_weight_g,
                    calories, protein_g, fat_g, carbs_g, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    meal_id,
                    item["food_name"],
                    item.get("estimated_weight_g"),
                    item.get("calories", 0),
                    item.get("protein_g", 0),
                    item.get("fat_g", 0),
                    item.get("carbs_g", 0),
                    item.get("confidence"),
                ),
            )

        conn.commit()
        return meal_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_meals_for_date(
    profile_id: int, date_str: str, db_path: str = DEFAULT_DB_PATH
) -> list[dict]:
    """
    Return all meals for a profile on a given date, with nested items.

    Args:
        profile_id: The profile to query.
        date_str: ISO date string 'YYYY-MM-DD'.

    Returns:
        List of meal dicts, each with an 'items' key containing the meal_items.
    """
    conn = _get_connection(db_path)
    try:
        # Get meals
        meals_cursor = conn.execute(
            """
            SELECT * FROM meals
            WHERE profile_id = ? AND meal_date = ?
            ORDER BY meal_time
            """,
            (profile_id, date_str),
        )
        meals = [dict(row) for row in meals_cursor.fetchall()]

        # Get items for each meal
        for meal in meals:
            items_cursor = conn.execute(
                "SELECT * FROM meal_items WHERE meal_id = ? ORDER BY id",
                (meal["id"],),
            )
            meal["items"] = [dict(row) for row in items_cursor.fetchall()]

        return meals
    finally:
        conn.close()


def get_daily_totals(
    profile_id: int, date_str: str, db_path: str = DEFAULT_DB_PATH
) -> dict:
    """
    Return summed nutritional totals for a profile on a given date.

    Returns:
        Dict with keys: total_calories, total_protein, total_fat, total_carbs, meal_count
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT
                COALESCE(SUM(total_calories), 0) as total_calories,
                COALESCE(SUM(total_protein), 0) as total_protein,
                COALESCE(SUM(total_fat), 0) as total_fat,
                COALESCE(SUM(total_carbs), 0) as total_carbs,
                COUNT(*) as meal_count
            FROM meals
            WHERE profile_id = ? AND meal_date = ?
            """,
            (profile_id, date_str),
        )
        row = cursor.fetchone()
        return dict(row)
    finally:
        conn.close()


def get_date_range_summary(
    profile_id: int, start_date: str, end_date: str, db_path: str = DEFAULT_DB_PATH
) -> list[dict]:
    """
    Return daily totals for a date range (inclusive).

    Returns:
        List of dicts with keys: meal_date, total_calories, total_protein,
        total_fat, total_carbs, meal_count
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            SELECT
                meal_date,
                SUM(total_calories) as total_calories,
                SUM(total_protein) as total_protein,
                SUM(total_fat) as total_fat,
                SUM(total_carbs) as total_carbs,
                COUNT(*) as meal_count
            FROM meals
            WHERE profile_id = ? AND meal_date BETWEEN ? AND ?
            GROUP BY meal_date
            ORDER BY meal_date
            """,
            (profile_id, start_date, end_date),
        )
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def delete_meal(meal_id: int, db_path: str = DEFAULT_DB_PATH) -> None:
    """Delete a meal and its items (CASCADE)."""
    conn = _get_connection(db_path)
    try:
        conn.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
        conn.commit()
    finally:
        conn.close()
