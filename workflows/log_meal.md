# Log Meal

## Objective
Log a meal from natural language input and store structured nutritional data.

## Inputs
- Profile ID (selected in the UI)
- Meal text (natural language description)
- Date and time (defaults to now)
- Optional meal label (breakfast/lunch/dinner/snack)

## Tool Chain
1. `tools/gemini_meal_parser.py` — Parse natural language via Gemini API
2. User reviews and optionally edits parsed items in the data editor
3. `tools/db_helpers.py:create_meal()` — Save to database

## Expected Output
- `meals` row with aggregated totals
- `meal_items` rows for each parsed food item
- Running daily totals displayed to user

## Edge Cases

### Gemini returns empty items
- Input was not food (e.g., "I went for a walk")
- Show warning: "No food items detected"
- Do NOT save to database

### Gemini returns unreasonable values
- Any single item > 2000 kcal: show warning banner
- Total meal > 4000 kcal: show warning banner
- User can edit values before saving via the data editor

### API failure
- Network error, rate limit, or service outage
- Retry 3x with exponential backoff (1s, 2s, 4s)
- On final failure: show error message with details
- Preserve the user's input text (don't clear the text area)
- Log error to `.tmp/gemini_errors.log`

### User edits parsed data
- The edited values (from st.data_editor) are what gets stored
- Original Gemini output is not preserved after editing
- The original raw_input text is always preserved

### Authentication error
- Invalid API key: show clear error, don't retry
- Direct user to check .env file

## Notes
- Model: gemini-2.0-flash (configurable in gemini_meal_parser.py)
- Temperature: 0.1 for consistency
- Structured output via Pydantic schema ensures valid JSON
