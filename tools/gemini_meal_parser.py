"""
Gemini-powered natural language meal parser for NutriSync AI.

Sends meal descriptions to Google Gemini and returns structured
nutritional data using Pydantic-validated JSON output.
"""

import os
import json
import time
import logging
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

logger = logging.getLogger(__name__)

# Ensure .tmp/ exists for error logging
TMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".tmp")
os.makedirs(TMP_DIR, exist_ok=True)

# ============================================================
# Response Schema (Pydantic)
# ============================================================

class FoodItem(BaseModel):
    food_name: str = Field(description="Name of the food item, e.g. 'pesto pasta'")
    estimated_weight_g: float = Field(description="Estimated weight in grams")
    calories: float = Field(description="Estimated calories (kcal)")
    protein_g: float = Field(description="Estimated protein in grams")
    fat_g: float = Field(description="Estimated fat in grams")
    carbs_g: float = Field(description="Estimated carbohydrates in grams")
    confidence: str = Field(description="Confidence level: 'high', 'medium', or 'low'")


class MealParseResult(BaseModel):
    items: list[FoodItem]
    notes: str = Field(description="Any assumptions made about portions, preparation, or ambiguous items")


# ============================================================
# System Prompt
# ============================================================

SYSTEM_PROMPT = """You are a nutrition analysis assistant. Your task is to parse a natural language meal description and return structured nutritional data for each individual food item.

RULES:
1. Separate the input into individual food items. A meal like "pasta with pesto and a side of Greek yogurt" becomes two items: "pasta with pesto" and "Greek yogurt".
2. For each item, estimate a reasonable portion size in grams based on context clues:
   - "large bowl" = ~400g for pasta/rice/soup, ~300g for salad
   - "small bowl" = ~200g for pasta/rice/soup, ~150g for salad
   - "a plate of" = ~300g
   - "a piece of" = one standard serving of that food
   - "a glass of" = ~250ml
   - If no portion clue is given, use a standard adult serving size
3. Provide calorie and macronutrient estimates per the estimated portion size.
4. Use common nutritional databases as your reference (USDA, standard food composition tables).
5. Set "confidence" to "high" if the food and portion are unambiguous, "medium" if you had to make reasonable assumptions about the portion or preparation, and "low" if the description is very vague.
6. In the "notes" field, explain any assumptions you made (e.g., "Assumed regular pasta, not whole wheat" or "Assumed full-fat Greek yogurt").
7. All numerical values must be non-negative numbers. Round to one decimal place.
8. If the input does not appear to describe food at all, return an empty items list and explain in notes."""


# ============================================================
# Model fallback chain
# ============================================================

# Primary model first, then fallback with separate quota pool
MODEL_CHAIN = ["gemini-2.0-flash", "gemini-2.0-flash-lite"]

# Longer delays for 429 quota errors (free tier needs time to reset)
RATE_LIMIT_DELAYS = [5, 15, 30]  # seconds


# ============================================================
# Core parsing function
# ============================================================

def parse_meal(
    meal_text: str,
    max_retries: int = 3,
) -> dict:
    """
    Parse a natural language meal description using Google Gemini.

    Uses a model fallback chain: tries gemini-2.0-flash first,
    then falls back to gemini-2.0-flash-lite on quota exhaustion.

    Args:
        meal_text: The user's meal description (e.g., "a large bowl of pasta with pesto").
        max_retries: Number of retries per model on transient failures.

    Returns:
        Dict with keys:
            - success (bool): Whether parsing succeeded.
            - items (list[dict]): Parsed food items.
            - notes (str): Gemini's assumptions/notes.
            - model (str): Model used.
            - error (str, optional): Error message if success is False.
            - rate_limited (bool, optional): True if failure was due to quota.
    """
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "items": [],
            "notes": "",
            "model": MODEL_CHAIN[0],
            "error": (
                "GEMINI_API_KEY not found. "
                "Get a free key at https://aistudio.google.com/apikey "
                "and add it to your .env file."
            ),
        }

    # Validate input
    if not meal_text or not meal_text.strip():
        return {
            "success": False,
            "items": [],
            "notes": "",
            "model": MODEL_CHAIN[0],
            "error": "No meal description provided.",
        }

    # Import Gemini SDK (deferred to avoid import errors when key is missing)
    try:
        from google import genai
    except ImportError:
        return {
            "success": False,
            "items": [],
            "notes": "",
            "model": MODEL_CHAIN[0],
            "error": "google-genai package not installed. Run: pip install google-genai",
        }

    client = genai.Client(api_key=api_key)

    # Try each model in the fallback chain
    last_error = None
    was_rate_limited = False

    for model in MODEL_CHAIN:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=f"Parse this meal: {meal_text}",
                    config={
                        "system_instruction": SYSTEM_PROMPT,
                        "response_mime_type": "application/json",
                        "response_schema": MealParseResult,
                        "temperature": 0.1,
                    },
                )

                # Parse and validate with Pydantic
                result = MealParseResult.model_validate_json(response.text)

                return {
                    "success": True,
                    "items": [item.model_dump() for item in result.items],
                    "notes": result.notes,
                    "model": model,
                }

            except Exception as e:
                last_error = e
                error_str = str(e)

                # Log the error
                logger.warning(f"Gemini [{model}] attempt {attempt + 1}/{max_retries} failed: {error_str}")

                # Check for rate limiting FIRST — before auth check to avoid
                # false positives (e.g. retryDelay "56.480401658s" contains "401")
                is_rate_limited = "RESOURCE_EXHAUSTED" in error_str
                if not is_rate_limited and "429" in error_str and "quota" in error_str.lower():
                    is_rate_limited = True

                if is_rate_limited:
                    was_rate_limited = True
                    if attempt < max_retries - 1:
                        wait_time = RATE_LIMIT_DELAYS[min(attempt, len(RATE_LIMIT_DELAYS) - 1)]
                        logger.info(f"Rate limited on {model}. Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        # Exhausted retries on this model — break to try next model
                        logger.info(f"Rate limit retries exhausted on {model}, trying next model...")
                        break

                # Check for authentication errors (don't retry, don't fallback)
                # Use gRPC status strings — avoids false positives from numeric substrings
                if "UNAUTHENTICATED" in error_str or "PERMISSION_DENIED" in error_str or "API_KEY_INVALID" in error_str:
                    _log_error(meal_text, error_str)
                    return {
                        "success": False,
                        "items": [],
                        "notes": "",
                        "model": model,
                        "error": f"Authentication error: {error_str}. Check your GEMINI_API_KEY.",
                    }

                # For other errors, retry with short backoff
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s for transient errors
                    time.sleep(wait_time)
                    continue

    # All models and retries exhausted
    if was_rate_limited:
        error_msg = (
            "API quota exceeded on all available models. "
            "The free tier has limited requests per minute. "
            "Please wait about 60 seconds and try again."
        )
    else:
        error_msg = f"Failed after trying all models. Last error: {last_error}"

    _log_error(meal_text, error_msg)
    return {
        "success": False,
        "items": [],
        "notes": "",
        "model": MODEL_CHAIN[-1],
        "error": error_msg,
        "rate_limited": was_rate_limited,
    }


def _log_error(meal_text: str, error: str) -> None:
    """Log parsing errors to .tmp/gemini_errors.log for debugging."""
    try:
        log_path = os.path.join(TMP_DIR, "gemini_errors.log")
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n[{timestamp}]\n")
            f.write(f"Input: {meal_text}\n")
            f.write(f"Error: {error}\n")
            f.write("-" * 60 + "\n")
    except Exception:
        pass  # Don't fail on logging errors


# --- Quick test when run directly ---
if __name__ == "__main__":
    result = parse_meal("two scrambled eggs and a slice of toast with butter")
    print(json.dumps(result, indent=2))
