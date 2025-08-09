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
- MAX_UPLOAD_MB=10

Local development
-----------------
1. Create and activate a virtualenv
2. Install deps: `pip install -r requirements.txt`
3. Run: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
4. Docs: visit `http://127.0.0.1:8000/docs`

SQL migrations
--------------
- Apply `sql/upsert_plant_and_care.sql` in Supabase SQL editor.

Reverse proxy upload limits
---------------------------
If you deploy behind a reverse proxy, set an equivalent request body limit to avoid proxy buffering large uploads:

- Nginx: add `client_max_body_size 10m;`
- Caddy: add `request_body { max_size 10MB }`
- Traefik: set `middlewares.buffering.maxRequestBodyBytes`

Keep this value in sync with `MAX_UPLOAD_MB`.


