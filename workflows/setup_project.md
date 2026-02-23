# Setup Project

## Objective
Get NutriSync AI running from scratch on a new machine.

## Prerequisites
- Python 3.10+ installed
- pip available

## Steps

1. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```
   - On ARM64 Windows: use `pip install --only-binary :all:` if builds fail
   - If pyarrow fails to install, the app will still work (streamlit uses it optionally)

2. **Get a Gemini API key**
   - Visit https://aistudio.google.com/apikey
   - Sign in with a Google account
   - Click "Create API key"
   - Copy the key

3. **Configure environment**
   - Open `.env` in the project root
   - Add: `GEMINI_API_KEY=your_key_here`
   - Save the file

4. **Initialize the database**
   ```
   python tools/db_init.py
   ```
   - Creates `nutrisync.db` with the schema
   - Safe to run multiple times (idempotent)

5. **(Optional) Seed sample data**
   ```
   python tools/seed_data.py
   ```
   - Creates two profiles and sample meals for testing
   - Only runs if no profiles exist

6. **Launch the app**
   ```
   streamlit run app.py
   ```
   - Opens at http://localhost:8501

## Verification
- App loads in browser with 4 navigation items (Dashboard, Log Meal, Profiles, History)
- If no API key: yellow warning banner appears in sidebar
- If seeded: Dashboard shows meal data; History shows 7-day trends
- Profile creation form accepts data and calculates TDEE targets

## Troubleshooting

| Issue | Fix |
|---|---|
| `ModuleNotFoundError: streamlit` | Run `pip install streamlit` |
| `GEMINI_API_KEY not found` | Check `.env` file exists with the key, restart app |
| `nutrisync.db` permission error | Ensure write access to the project directory |
| Unicode errors on Windows | Use `set PYTHONIOENCODING=utf-8` before running |
| Streamlit version 0.8 installed | Uninstall and reinstall: `pip uninstall streamlit && pip install streamlit>=1.40` |
