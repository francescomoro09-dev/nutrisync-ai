"""
Database initialization script for NutriSync AI.

Creates the SQLite schema if it doesn't already exist. Idempotent — safe to run
multiple times. Uses WAL journal mode for better concurrent access on Windows.
"""

import sqlite3
import os

# Default database path (project root)
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "nutrisync.db")

SCHEMA_SQL = """
-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;

-- Enable foreign key enforcement
PRAGMA foreign_keys=ON;

-- Table: profiles
-- Stores user profiles with physical stats, goals, and calculated targets.
-- Max 2 profiles enforced at the application layer.
CREATE TABLE IF NOT EXISTS profiles (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    age             INTEGER NOT NULL CHECK(age > 0 AND age < 150),
    weight_kg       REAL    NOT NULL CHECK(weight_kg > 0),
    height_cm       REAL    NOT NULL CHECK(height_cm > 0),
    gender          TEXT    NOT NULL CHECK(gender IN ('male', 'female')),
    activity_level  TEXT    NOT NULL CHECK(activity_level IN (
                        'sedentary', 'light', 'moderate', 'active', 'very_active')),
    fitness_goal    TEXT    NOT NULL CHECK(fitness_goal IN (
                        'lose_weight', 'maintain', 'gain_muscle')),
    -- Calculated fields (recomputed on every profile save)
    bmr_kcal              REAL,
    tdee_kcal             REAL,
    target_calories_kcal  REAL,
    target_protein_g      REAL,
    target_fat_g          REAL,
    target_carbs_g        REAL,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Table: meals
-- Each row is one meal logging event.
CREATE TABLE IF NOT EXISTS meals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id      INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    meal_date       TEXT    NOT NULL,   -- ISO date: 'YYYY-MM-DD'
    meal_time       TEXT    NOT NULL,   -- ISO time: 'HH:MM'
    meal_label      TEXT,               -- 'breakfast', 'lunch', 'dinner', 'snack', or NULL
    raw_input       TEXT    NOT NULL,   -- Original natural language text
    total_calories  REAL    NOT NULL DEFAULT 0,
    total_protein   REAL    NOT NULL DEFAULT 0,
    total_fat       REAL    NOT NULL DEFAULT 0,
    total_carbs     REAL    NOT NULL DEFAULT 0,
    gemini_model    TEXT,               -- Model name for audit trail
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- Table: meal_items
-- Individual food items extracted by Gemini from a meal.
CREATE TABLE IF NOT EXISTS meal_items (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    meal_id             INTEGER NOT NULL REFERENCES meals(id) ON DELETE CASCADE,
    food_name           TEXT    NOT NULL,
    estimated_weight_g  REAL,
    calories            REAL    NOT NULL DEFAULT 0,
    protein_g           REAL    NOT NULL DEFAULT 0,
    fat_g               REAL    NOT NULL DEFAULT 0,
    carbs_g             REAL    NOT NULL DEFAULT 0,
    confidence          TEXT    CHECK(confidence IN ('high', 'medium', 'low'))
);

-- Index for fast daily lookups
CREATE INDEX IF NOT EXISTS idx_meals_profile_date ON meals(profile_id, meal_date);
"""


def init_database(db_path: str = DEFAULT_DB_PATH) -> str:
    """
    Create the NutriSync database and schema if they don't exist.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        The path to the created/existing database.
    """
    conn = sqlite3.connect(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()

    return db_path


# --- Run directly to initialize the database ---
if __name__ == "__main__":
    path = init_database()
    print(f"[OK] Database initialized at: {path}")

    # Verify tables exist
    conn = sqlite3.connect(path)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    print(f"  Tables: {', '.join(tables)}")
    assert "profiles" in tables, "Missing 'profiles' table"
    assert "meals" in tables, "Missing 'meals' table"
    assert "meal_items" in tables, "Missing 'meal_items' table"
    print("[OK] All tables verified.")
