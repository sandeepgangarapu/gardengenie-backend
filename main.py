import os
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import psycopg2 # Use psycopg2 for PostgreSQL
from psycopg2.extras import RealDictCursor # Optional: To get results as dictionaries
from dotenv import load_dotenv
import datetime
import logging
import time

# --- Configuration & Initialization ---

load_dotenv() # Load environment variables from .env for local dev

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Plant Name Cleaner API",
    description="Cleans plant names using Gemini via OpenRouter and stores results in PostgreSQL.",
    version="1.0.0",
)

# --- Database Connection ---
# Render provides this automatically in the deployed environment
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    """Establishes a connection to the PostgreSQL database with retries."""
    conn = None
    retries = 5
    delay = 1
    while retries > 0:
        try:
            if not DATABASE_URL:
                # This will be true locally unless you set up local Postgres
                # and add DATABASE_URL to your .env file
                logger.error("DATABASE_URL environment variable not set.")
                return None
            conn = psycopg2.connect(DATABASE_URL)
            logger.info("Database connection established.")
            return conn
        except psycopg2.OperationalError as e:
            # Handles cases like DB not ready yet during startup
            logger.warning(f"Database connection failed: {e}. Retrying in {delay}s... ({retries} retries left)")
            retries -= 1
            time.sleep(delay)
            delay *= 2 # Exponential backoff
        except Exception as e:
             logger.error(f"An unexpected error occurred during DB connection: {e}")
             return None # Fail fast on other errors
    logger.error("Could not establish database connection after multiple retries.")
    return None

# --- OpenRouter Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Verify this model name on OpenRouter documentation
LLM_MODEL = "google/gemini-flash-1.5"

if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY not found in environment variables.")

# --- Pydantic Models ---
class PlantNameInput(BaseModel):
    raw_name: str = Field(..., min_length=1, description="The user-provided plant name.")

class PlantNameOutput(BaseModel):
    original_name: str
    cleaned_name: str
    model_used: str

# --- Helper Functions ---

def call_openrouter_llm(plant_name: str) -> str | None:
    """Calls the OpenRouter API to clean the plant name."""
    if not OPENROUTER_API_KEY:
        logger.error("OpenRouter API Key is missing.")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    # Simple prompt - refine for better results
    prompt = f"""
    Given the following user input, which is potentially a messy or common name for a plant, provide the most likely standardized botanical name (Genus species) or a widely accepted, clean common name if the botanical name is ambiguous or not applicable. If the input is clearly not a plant name, respond with 'N/A'.

    Input: "{plant_name}"

    Cleaned Name:
    """
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0.2,
    }
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        cleaned_name = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if not cleaned_name or len(cleaned_name) > 100:
             logger.warning(f"Received unusual response from LLM: {cleaned_name}")
             return "Error: Invalid response from LLM"
        if "N/A" in cleaned_name:
             return "N/A"

        logger.info(f"LLM ({LLM_MODEL}) returned: '{cleaned_name}' for input '{plant_name}'")
        return cleaned_name
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        return None
    except (KeyError, IndexError) as e:
         logger.error(f"Error parsing OpenRouter response: {e} - Response: {response.text}")
         return None

def store_result(original_name: str, cleaned_name: str, model_used: str):
    """Stores the input and output in PostgreSQL."""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            # Logged in get_db_connection, just return False
            return False

        cursor = conn.cursor()
        # The table 'plant_name_logs' needs to be created in the database later
        insert_query = """
        INSERT INTO plant_name_logs (original_name, cleaned_name, model_used, timestamp)
        VALUES (%s, %s, %s, %s)
        """
        # Use UTC time for consistency
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        # Use parameterized query to prevent SQL injection
        cursor.execute(insert_query, (original_name, cleaned_name, model_used, timestamp))
        conn.commit() # Commit the transaction
        logger.info(f"Stored result in PostgreSQL for '{original_name}'")
        return True
    except Exception as e:
        logger.error(f"Error storing data in PostgreSQL: {e}")
        if conn:
            conn.rollback() # Rollback on error
        return False
    finally:
        # Ensure cursor and connection are closed even if errors occur
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.debug("Database connection closed.")

# --- API Endpoint ---

@app.post("/clean-plant-name", response_model=PlantNameOutput)
async def clean_plant_name(payload: PlantNameInput, request: Request):
    """
    Receives a raw plant name, cleans it using an LLM via OpenRouter,
    stores the result in PostgreSQL, and returns the cleaned name.
    """
    raw_name = payload.raw_name
    logger.info(f"Received request to clean plant name: '{raw_name}'")

    # 1. Call LLM
    cleaned_name = call_openrouter_llm(raw_name)

    if cleaned_name is None:
        raise HTTPException(status_code=503, detail="Error communicating with the LLM service.")
    if "Error:" in cleaned_name:
         raise HTTPException(status_code=500, detail=cleaned_name)

    # 2. Store result
    storage_success = store_result(
        original_name=raw_name,
        cleaned_name=cleaned_name,
        model_used=LLM_MODEL
    )
    if not storage_success:
        # Log the error, but still return the result to the user
        logger.warning("Failed to store result in PostgreSQL, but returning cleaned name.")

    # 3. Return result
    return PlantNameOutput(
        original_name=raw_name,
        cleaned_name=cleaned_name,
        model_used=LLM_MODEL
    )

@app.get("/health", status_code=200)
async def health_check():
    """Simple health check endpoint."""
    # You could add a quick DB ping here if desired
    return {"status": "ok"}

# --- Local Development Runner ---
# This part runs when you execute `python main.py` locally.
# It requires a local PostgreSQL instance and DATABASE_URL in .env.
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server for local development...")
    # Render provides the PORT env var; default to 8000 locally if not set
    port = int(os.getenv("PORT", 8000))
    # Host 0.0.0.0 makes it accessible on your local network
    uvicorn.run(app, host="0.0.0.0", port=port)

