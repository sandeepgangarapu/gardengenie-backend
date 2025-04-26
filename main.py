import os
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import psycopg2 # Use psycopg2 for PostgreSQL
# from psycopg2.extras import RealDictCursor # Not strictly needed now
from dotenv import load_dotenv
import datetime
import logging
import time
import json # Added for JSON parsing

# --- Configuration & Initialization ---

load_dotenv() # Load environment variables from .env for local dev

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Plant Care API",
    description="Provides detailed plant care instructions (seed starting, planting, seasonal care) tailored to a USDA zone, using Gemini via OpenRouter and storing results in PostgreSQL.",
    version="1.1.0", # Bump version
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
LLM_MODEL = "google/gemini-flash-1.5" # Or consider a more powerful model for complex JSON generation if needed

if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY not found in environment variables.")

# --- Pydantic Models ---
class PlantCareInput(BaseModel):
    plant_name: str = Field(..., min_length=1, description="The user-provided plant name (e.g., tomato, Fiddle Leaf Fig).")
    user_zone: str = Field(..., pattern=r"^\d{1,2}[ab]?$", description="The user's USDA Hardiness Zone (e.g., 7a, 8b, 5).")

# Output model is now implicitly a dictionary via the endpoint's response_model=dict
# We could define a detailed Pydantic model matching the JSON schema,
# but returning dict is simpler and more flexible if LLM output varies slightly.

# --- Helper Functions ---

def call_openrouter_llm(plant_name: str, user_zone: str) -> dict | None:
    """Calls the OpenRouter API to get plant care instructions as JSON."""
    if not OPENROUTER_API_KEY:
        logger.error("OpenRouter API Key is missing.")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost", # Example referrer, replace if needed
        "X-Title": "Plant Care API", # Example title, replace if needed
    }

    # Updated prompt requesting JSON output
    prompt = f"""
Please provide detailed seed starting, planting, and care instructions for the following plant, tailored to the user's zone. **Generate the output strictly as a JSON object following the schema specified below.**

**Input Information:**

*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}

**Required Output Format (JSON Schema):**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief, general description of the plant]",
  "type": "[Annual OR Perennial]",
  "zone": "[User USDA Hardiness Zone]",
  "sun": "[Full Sun OR Partial Shade OR Full Shade]",
  "seedStartingMonth": "[e.g., February OR March]", // Single best month to start seeds (often indoors) for this zone
  "seedStartingInstructions": [
    "[Seed starting step 1 description - e.g., Container/soil choice]",
    "[Seed starting step 2 description - e.g., Sowing depth/spacing]",
    "[Seed starting step 3 description - e.g., Watering/moisture]",
    "[Seed starting step 4 description - e.g., Light/temperature needs]",
    "[Seed starting step 5 description - e.g., Hardening off]"
    // ... add more steps as relevant. If not typically grown from seed, this can be an empty array [].
  ],
  "plantingMonth": "[e.g., April OR May]", // Single best month to plant seedlings/nursery stock outdoors for this zone
  "plantingInstructions": [
    "[Planting step 1 description - e.g., Site selection/preparation]",
    "[Planting step 2 description - e.g., Digging the hole]",
    "[Planting step 3 description - e.g., Handling the seedling/root ball]",
    "[Planting step 4 description - e.g., Placing the plant & backfilling]",
    "[Planting step 5 description - e.g., Initial watering/mulching]"
    // ... add more steps as relevant. Focus on planting seedlings or nursery stock outdoors.
  ],
  "care": {{
    "spring": [
      {{
        "step": "[Care step 1 description]",
        "priority": "[must do OR good to do OR skip if you don't have time]", // General priority level
        "months": "[e.g., April OR May]" // Indicate SINGLE best month for this zone
      }},
      {{
        "step": "[Care step 2 description]",
        "priority": "[must do OR good to do OR skip if you don't have time]", // General priority level
        "months": "[e.g., April OR May]" // Indicate SINGLE best month for this zone
      }}
      // ... more steps as relevant
    ],
    "summer": [
      {{
        "step": "[Care step 1 description]",
        "priority": "[must do OR good to do OR skip if you don't have time]", // General priority level
        "months": "[e.g., June OR July]" // Indicate SINGLE best month for this zone
      }},
      {{
        "step": "[Care step 2 description]",
        "priority": "[must do OR good to do OR skip if you don't have time]", // General priority level
        "months": "[e.g., July OR August]" // Indicate SINGLE best month for this zone
      }}
      // ... more steps as relevant
    ],
    "fall": [
      {{
        "step": "[Care step 1 description]",
        "priority": "[must do OR good to do OR skip if you don't have time]", // General priority level
        "months": "[e.g., September OR October]" // Indicate SINGLE best month for this zone
      }},
      {{
        "step": "[Care step 2 description]",
        "priority": "[must do OR good to do OR skip if you don't have time]", // General priority level
        "months": "[e.g., October OR November]" // Indicate SINGLE best month for this zone
      }}
      // ... more steps as relevant
    ],
    "winter": [
      {{
        "step": "[Care step 1 description]",
        "priority": "[must do OR good to do OR skip if you don't have time]", // General priority level
        "months": "[e.g., December OR January]" // Indicate SINGLE best month for this zone
      }},
      {{
        "step": "[Care step 2 description]",
        "priority": "[must do OR good to do OR skip if you don't have time]", // General priority level
        "months": "[e.g., February OR January]" // Indicate SINGLE best month for this zone
      }}
      // ... more steps as relevant, if applicable
      // If no winter care needed, this can be an empty array: []
    ]
  }}
}}
```
Important Instructions for Generation:

Output MUST be a valid JSON object. Ensure correct syntax (quotes around keys and string values, commas between elements, correct brackets [] for arrays and braces {{}} for objects).
Correct Name: Provide the standard common name. If the input name is a misspelling or variation, use the corrected version for the "plantName" value.
No Botanical Name: Do not include the botanical name.
Seed Starting:
Determine the single best month to start seeds (usually indoors) based on the plant type and User USDA Hardiness Zone, and place it in the "seedStartingMonth" field.
Provide step-by-step instructions for starting the plant from seed in the "seedStartingInstructions" array. If the plant is not typically or easily grown from seed (e.g., many woody shrubs), provide an empty array [].
Planting:
Determine the single best month to plant seedlings or nursery stock outdoors, considering the last frost date for the User USDA Hardiness Zone, and place it in the "plantingMonth" field.
Provide step-by-step instructions for planting seedlings or nursery stock outdoors in the "plantingInstructions" array.
Ongoing Care Focus: The steps within the "care" section (spring, summer, fall, winter) should focus on ongoing maintenance after the plant is established in the ground. Do not repeat planting or seed starting steps here.
Priority Annotation: For each care step object within the seasonal arrays, use the "priority" key with exactly one of the following string values: "must do", "good to do", or "skip if you don't have time". Assign a general priority level appropriate for the task's importance to the plant's health or primary goal (e.g., fruiting).
Care Month Annotation: For each care step object within the seasonal arrays, use the "months" key to specify the single most appropriate month (e.g., "April", "July", "October") to perform the task, considering the User USDA Hardiness Zone. If a task is relevant over multiple months, choose the peak or most critical month for it. Do not use month ranges.
Clarity: Provide clear and concise descriptions for all instruction steps, suitable for a general audience.
Completeness: Fill in all specified fields in the JSON structure. If a season has no specific care steps, provide an empty array [] for that season's key. Include the user's zone in the "zone" field.
Please generate only the JSON object based on these requirements. Do not include any introductory text or explanations outside the JSON structure itself.
"""
    payload = {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1500, # Increased max_tokens for longer JSON output
        "temperature": 0.2, # Kept temperature low for consistency
        "response_format": {"type": "json_object"} # Request JSON output
    }
    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60) # Increased timeout
        response.raise_for_status()
        result = response.json()
        llm_content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        if not llm_content:
             logger.warning("Received empty content from LLM.")
             return None # Treat empty response as an error

        # Attempt to parse the JSON content
        try:
            care_info = json.loads(llm_content)
            logger.info(f"LLM ({LLM_MODEL}) returned valid JSON for '{plant_name}' in zone '{user_zone}'")
            return care_info
        except json.JSONDecodeError as json_e:
            logger.error(f"Failed to decode JSON response from LLM: {json_e}")
            logger.error(f"LLM Raw Content: {llm_content}")
            return None # Return None if JSON parsing fails

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        # Log response text if available for debugging
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"OpenRouter Response Status: {e.response.status_code}")
            logger.error(f"OpenRouter Response Text: {e.response.text}")
        return None
    except (KeyError, IndexError) as e:
         logger.error(f"Error parsing OpenRouter response structure: {e} - Response: {response.text}")
         return None
    except Exception as e:
         logger.error(f"An unexpected error occurred during LLM call: {e}")
         return None


def store_result(plant_name: str, user_zone: str, care_info: dict, model_used: str):
    """Stores the input and the generated care instructions JSON in PostgreSQL."""
    conn = None
    cursor = None
    # Ensure care_info is a valid dict before proceeding
    if not isinstance(care_info, dict):
        logger.error("Invalid care_info type passed to store_result. Expected dict.")
        return False

    try:
        conn = get_db_connection()
        if conn is None:
            return False # Logged in get_db_connection

        cursor = conn.cursor()
        # Assumes a table 'plant_care_logs' with columns:
        # plant_name TEXT, user_zone TEXT, care_instructions JSONB, model_used TEXT, timestamp TIMESTAMPTZ
        # You MUST create this table in your PostgreSQL database.
        # Example CREATE TABLE statement:
        # CREATE TABLE plant_care_logs (
        #     id SERIAL PRIMARY KEY,
        #     plant_name TEXT NOT NULL,
        #     user_zone TEXT NOT NULL,
        #     care_instructions JSONB,
        #     model_used TEXT,
        #     timestamp TIMESTAMPTZ DEFAULT timezone('utc', now())
        # );
        insert_query = """
        INSERT INTO plant_care_logs (plant_name, user_zone, care_instructions, model_used, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc)
        # Convert dict to JSON string for storage, psycopg2 handles JSONB correctly
        care_info_json = json.dumps(care_info)

        cursor.execute(insert_query, (plant_name, user_zone, care_info_json, model_used, timestamp))
        conn.commit()
        logger.info(f"Stored care instructions in PostgreSQL for '{plant_name}' in zone '{user_zone}'")
        return True
    except psycopg2.Error as db_err: # Catch specific psycopg2 errors
        logger.error(f"Database error storing data: {db_err}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error storing data in PostgreSQL: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
        logger.debug("Database connection closed.")

# --- API Endpoint ---

# Renamed endpoint and updated response model
@app.post("/plant-care-instructions", response_model=dict)
async def get_plant_care_instructions(payload: PlantCareInput, request: Request):
    """
    Receives a plant name and USDA zone, generates detailed care instructions
    using an LLM via OpenRouter, stores the result in PostgreSQL,
    and returns the care instructions as a JSON object.
    """
    plant_name = payload.plant_name
    user_zone = payload.user_zone
    logger.info(f"Received request for plant care: '{plant_name}' in zone '{user_zone}'")

    # 1. Call LLM
    care_info = call_openrouter_llm(plant_name, user_zone)

    if care_info is None:
        # Logged in call_openrouter_llm
        raise HTTPException(status_code=503, detail="Error communicating with the LLM service or parsing its response.")

    # 2. Store result (care_info is now a dictionary)
    storage_success = store_result(
        plant_name=plant_name,
        user_zone=user_zone,
        care_info=care_info, # Pass the dict
        model_used=LLM_MODEL
    )
    if not storage_success:
        # Log the error, but still return the result to the user
        logger.warning("Failed to store result in PostgreSQL, but returning care instructions.")

    # 3. Return result (the dictionary itself)
    return care_info

@app.get("/health", status_code=200)
async def health_check():
    """Simple health check endpoint."""
    # Optional: Add DB ping
    # conn = None
    # try:
    #     conn = get_db_connection()
    #     if conn:
    #         return {"status": "ok", "db_connection": "successful"}
    #     else:
    #         return {"status": "ok", "db_connection": "failed"}
    # finally:
    #     if conn:
    #         conn.close()
    return {"status": "ok"}

# --- Local Development Runner ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server for local development...")
    # Render provides the PORT env var; default to 8000 locally if not set
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

