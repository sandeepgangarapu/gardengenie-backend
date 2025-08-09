GardenGenie Backend
===================

FastAPI backend for plant care guidance and plant identification.

Environment variables
---------------------
Create a `.env` file with:

- APP_ENV=development
- SUPABASE_URL=...
- SUPABASE_KEY=...
- OPENROUTER_API_KEY=...
- LLM_TIMEOUT_SECONDS=30
- LLM_MAX_RETRIES=3
- UNSPLASH_ACCESS_KEY=... (optional)
- UNSPLASH_TIMEOUT_SECONDS=7
- UNSPLASH_MAX_RETRIES=3

Local development
-----------------
1. Create and activate a virtualenv
2. Install deps: `pip install -r requirements.txt`
3. Run: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
4. Docs: visit `http://127.0.0.1:8000/docs`

SQL migrations
--------------
- Apply `sql/upsert_plant_and_care.sql` in Supabase SQL editor.


