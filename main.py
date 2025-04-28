import os
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
# import psycopg2 # Use psycopg2 for PostgreSQL # Removed psycopg2
# from psycopg2.extras import RealDictCursor # Not strictly needed now # Removed psycopg2
from dotenv import load_dotenv
import datetime
import logging
import time
import json # Added for JSON parsing
from fastapi.middleware.cors import CORSMiddleware # Added for CORS
from typing import Optional, Any, List

# Supabase imports
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from postgrest import APIResponse # To check response types

# --- Configuration & Initialization ---

load_dotenv() # Load environment variables from .env for local dev

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Supabase Client Initialization ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Supabase URL or Key not found in environment variables. Database operations will fail.")
    supabase: Optional[Client] = None
else:
    try:
        # Use ClientOptions for potential future configurations (e.g., schema)
        options: ClientOptions = ClientOptions()
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY, options)
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase: Optional[Client] = None


app = FastAPI(
    title="Plant Care API",
    description="Provides detailed plant care instructions (seed starting, planting, seasonal care) tailored to a USDA zone, using Gemini via OpenRouter and storing results in Supabase.",
    version="1.3.0", # Bump version for supabase-py integration
)

# --- CORS Middleware ---
# Define the origins allowed to access your API
origins = [
    "https://gardengenie.lovable.app", # Your frontend origin
    "http://localhost", # Allow local development if needed
    "http://localhost:8000", # Allow local development if needed (common port)
    "http://localhost:3000", # Common frontend dev port
    # Add any other origins you need to allow
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # List of allowed origins
    allow_credentials=True, # Allows cookies to be included in requests
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Supabase Configuration ---
# Project ID no longer needed directly in code
# SUPABASE_PROJECT_ID = "bwbefczdqtwwujgcsklu"

# --- Database Connection ---
# Removed old get_db_connection function

# --- OpenRouter Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "google/gemini-2.5-flash-preview"

if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY not found in environment variables.")

# --- Pydantic Models ---
class PlantCareInput(BaseModel):
    plant_name: str = Field(..., min_length=1, description="The user-provided plant name (e.g., tomato, Fiddle Leaf Fig).")
    user_zone: str = Field(..., pattern=r"^\d{1,2}[ab]?$", description="The user's USDA Hardiness Zone (e.g., 7a, 8b, 5).")


# --- Helper Functions ---

# Removed MCP-related helpers: escape_sql_string, escape_sql_array, execute_supabase_sql


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

    # Updated prompt requesting JSON output (ensure it reflects schema)
    prompt = f"""
Please provide detailed seed starting, planting, and care instructions for the following plant, tailored to the user's zone. **Generate the output strictly as a JSON object following the schema specified below.**

**Input Information:**

*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}

**Required Output Format (JSON Schema matching Supabase tables):**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief, general description of the plant]",
  "type": "[Annual OR Perennial]",
  "zone": "[User USDA Hardiness Zone]",
  "zoneSuitability": "[match OR close OR far]", // Not directly stored in plants, used for logging if needed
  "sun": "[Full Sun OR Partial Shade OR Full Shade]", // Will be mapped to 'sun_requirements'
  "seedStartingMonth": "[e.g., February OR March OR null]", // Single best month or null
  "seedStartingInstructions": [
    "[Seed starting step 1 description - e.g., Container/soil choice]",
    "[Seed starting step 2 description - e.g., Sowing depth/spacing]",
    "[Seed starting step 3 description - e.g., Watering/moisture]",
    "[Seed starting step 4 description - e.g., Light/temperature needs]",
    "[Seed starting step 5 description - e.g., Hardening off]"
    // ... add more steps as relevant. If not typically grown from seed, this can be an empty array [].
  ],
  "plantingMonth": "[e.g., April OR May]", // Single best month to plant seedlings/nursery stock outdoors for this zone or null
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
      // ... more steps as relevant, steps ordered as they appear here
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

Output MUST be a valid JSON object.
Match Schema: Adhere strictly to the keys and expected data types (string, array of strings, nested objects/arrays) shown above.
Correct Name: Use the standard common name for "plantName".
Plant/Seed Months: Provide the single best month string or null if not applicable.
Instructions: Provide seed/planting instructions as arrays of strings. Empty array `[]` if not applicable.
Sun: Provide the sun preference string (e.g., "Full Sun").
Care Section: Structure seasonal care exactly as shown. For each step, include `step`, `priority`, and `months`.
Priority/Season ENUMs: If `priority` or `season` columns in Supabase are ENUMs, ensure the generated strings match valid ENUM values exactly (e.g., 'spring', 'summer', 'fall', 'winter', 'must do', 'good to do', 'skip if you don\'t have time').
Completeness: Fill all fields. Use `null` for optional month fields if not applicable. Use empty arrays `[]` for instruction lists or seasonal care lists if empty.
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
            # Basic validation: check for essential keys
            if not all(k in care_info for k in ['plantName', 'zone', 'care']):
                logger.error(f"LLM JSON missing essential keys: {care_info}")
                return None
            logger.info(f"LLM ({LLM_MODEL}) returned valid JSON for '{plant_name}' in zone '{user_zone}'")
            return care_info
        except json.JSONDecodeError as json_e:
            logger.error(f"Failed to decode JSON response from LLM: {json_e}")
            logger.error(f"LLM Raw Content: {llm_content}")
            return None # Return None if JSON parsing fails

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling OpenRouter API: {e}")
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


def store_result(
    original_plant_name: str, # Keep original for logging if needed
    original_user_zone: str, # Keep original for logging if needed
    care_info: dict,
    model_used: str # Keep for logging if needed
) -> bool:
    """Stores the generated care instructions JSON in Supabase using supabase-py client."""

    if supabase is None:
        logger.error("Supabase client is not initialized. Cannot store result.")
        return False

    if not isinstance(care_info, dict):
        logger.error("Invalid care_info type passed to store_result. Expected dict.")
        return False

    # 1. Extract Data from care_info (using .get for safety)
    plant_name = care_info.get('plantName')
    zone = care_info.get('zone')
    description = care_info.get('description')
    plant_type = care_info.get('type')
    sun_requirements = care_info.get('sun') # Map LLM 'sun'
    seed_start_month = care_info.get('seedStartingMonth')
    plant_month = care_info.get('plantingMonth')
    # Ensure these are lists, even if empty from LLM
    seed_instructions = care_info.get('seedStartingInstructions') or []
    plant_instructions = care_info.get('plantingInstructions') or []
    care_details = care_info.get('care', {})

    # Basic validation for core data needed for insertion
    if not plant_name or not zone:
        logger.error(f"Missing essential plantName or zone in care_info: {care_info}")
        return False

    plant_uuid: Optional[str] = None

    try:
        # 2. Find or Insert/Update Plant Record
        logger.debug(f"Checking for plant: {plant_name}, zone: {zone}")
        response: APIResponse = supabase.table('plants')\
                                    .select('plant_id')\
                                    .eq('plant_name', plant_name)\
                                    .eq('zone', zone)\
                                    .maybe_single()\
                                    .execute()

        plant_data_for_upsert = {
            'plant_name': plant_name,
            'zone': zone,
            'description': description,
            'type': plant_type,
            'sun_requirements': sun_requirements,
            'seed_starting_month': seed_start_month,
            'planting_month': plant_month,
            'seed_starting_instructions': seed_instructions,
            'planting_instructions': plant_instructions,
            # 'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat() # Let Supabase handle timestamp updates if configured
        }

        if response.data:
            # Plant exists, Update it
            plant_uuid = response.data.get('plant_id')
            if not plant_uuid:
                 logger.error(f"Found plant record but missing plant_id: {response.data}")
                 return False

            logger.info(f"Found existing plant with UUID: {plant_uuid}. Updating.")
            update_response: APIResponse = supabase.table('plants')\
                                                .update(plant_data_for_upsert)\
                                                .eq('plant_id', plant_uuid)\
                                                .execute()
            # Check for update errors (supabase-py might raise exceptions on failure too)
            if not hasattr(update_response, 'data'): # Basic check if response looks OK
                 logger.error(f"Failed to update plant record. Response: {update_response}")
                 return False

        else:
            # Plant doesn't exist, Insert it
            logger.info(f"Inserting new plant: {plant_name}, zone: {zone}")
            insert_response: APIResponse = supabase.table('plants')\
                                                .insert(plant_data_for_upsert)\
                                                .execute()

            if insert_response.data and len(insert_response.data) > 0:
                plant_uuid = insert_response.data[0].get('plant_id')
                if not plant_uuid:
                    logger.error(f"Inserted plant but response missing plant_id: {insert_response.data}")
                    return False
                logger.info(f"Inserted new plant with UUID: {plant_uuid}")
            else:
                logger.error(f"Failed to insert new plant. Response: {insert_response}")
                return False

        # Ensure we have a plant_uuid
        if not plant_uuid:
             logger.error("Could not obtain plant_uuid after find/insert/update operations.")
             return False

        # 3. Log the Query (Implementation depends on query_logs table - skipping for now)
        # logger.info("Query logging skipped.")

        # 4. Delete Old Seasonal Care Instructions for this Plant UUID
        logger.debug(f"Deleting old care instructions for plant_id: {plant_uuid}")
        delete_response: APIResponse = supabase.table('care_instructions')\
                                            .delete()\
                                            .eq('plant_id', plant_uuid)\
                                            .execute()
        # Deleting 0 rows is not an error here
        # Check if the response indicates a failure other than 0 rows deleted
        if not hasattr(delete_response, 'data') and not hasattr(delete_response, 'count'): # Heuristic check
             logger.warning(f"Could not confirm deletion of old care instructions. Response: {delete_response}")
             # Decide if this is fatal - potentially allows duplicates if insert succeeds
             # return False # Optional: make it fatal

        # 5. Prepare and Insert New Seasonal Care Instructions
        seasonal_instructions_to_insert = []
        for season, steps in care_details.items():
             if isinstance(steps, list):
                 for i, step_detail in enumerate(steps):
                     if isinstance(step_detail, dict):
                         # Prepare dict for insertion matching table columns
                         instruction_row = {
                             'plant_id': plant_uuid, # Link to the plant
                             'season': season, # Assuming string matches ENUM
                             'months': step_detail.get('months'),
                             'step_description': step_detail.get('step'),
                             'priority': step_detail.get('priority'), # Assuming string matches ENUM
                             'order_within_season': i + 1 # Order based on list index
                         }
                         seasonal_instructions_to_insert.append(instruction_row)

        if not seasonal_instructions_to_insert:
            logger.info("No seasonal care instructions generated by LLM to insert.")
            return True # Plant saved/updated successfully

        logger.info(f"Inserting {len(seasonal_instructions_to_insert)} seasonal care instructions for plant_id: {plant_uuid}")
        insert_care_response: APIResponse = supabase.table('care_instructions')\
                                                .insert(seasonal_instructions_to_insert)\
                                                .execute()

        if not insert_care_response.data or len(insert_care_response.data) != len(seasonal_instructions_to_insert):
            logger.error(f"Failed to insert all seasonal care instructions. Response: {insert_care_response}")
            # This indicates partial success or total failure of the batch insert
            return False

        logger.info(f"Successfully stored {len(seasonal_instructions_to_insert)} seasonal care instructions.")
        return True

    except Exception as e:
        # Catch potential exceptions from supabase-py client calls or other logic
        logger.error(f"An unexpected error occurred during Supabase storage: {e}", exc_info=True)
        # Log the specific Supabase error if available (depends on supabase-py version/error handling)
        if hasattr(e, 'message'): logger.error(f"Supabase Error Message: {e.message}")
        if hasattr(e, 'details'): logger.error(f"Supabase Error Details: {e.details}")
        if hasattr(e, 'hint'): logger.error(f"Supabase Error Hint: {e.hint}")
        return False


# --- API Endpoint ---

@app.post("/plant-care-instructions", response_model=dict)
async def get_plant_care_instructions(payload: PlantCareInput, request: Request):
    """
    Receives a plant name and USDA zone, generates detailed care instructions
    using an LLM via OpenRouter, stores the result in Supabase using supabase-py,
    and returns the care instructions as a JSON object.
    """
    if supabase is None:
         raise HTTPException(status_code=503, detail="Database client is not initialized. Cannot process request.")

    plant_name = payload.plant_name
    user_zone = payload.user_zone
    logger.info(f"Received request for plant care: '{plant_name}' in zone '{user_zone}'")

    # 1. Call LLM
    care_info = call_openrouter_llm(plant_name, user_zone)

    if care_info is None:
        # Logged in call_openrouter_llm
        raise HTTPException(status_code=503, detail="Error communicating with the LLM service or parsing its response.")

    # 2. Store result in Supabase using supabase-py
    storage_success = store_result(
        original_plant_name=plant_name,
        original_user_zone=user_zone,
        care_info=care_info,
        model_used=LLM_MODEL
        # project_id no longer needed here
    )
    if not storage_success:
        # Logged within store_result
        logger.warning("Failed to store result in Supabase, but returning care instructions to user.")
        # Optional: Raise 500 if storage failure should prevent user response
        # raise HTTPException(status_code=500, detail="Failed to store care instructions.")

    # 3. Return result (the dictionary itself)
    return care_info

@app.get("/health", status_code=200)
async def health_check():
    """Simple health check endpoint. Checks Supabase connection."""
    if supabase is None:
        return {"status": "error", "db_connection": "Supabase client not initialized"}
    try:
        # Simple query to check connection
        response = supabase.table('plants').select('plant_id', count='exact').limit(0).execute()
        # Check if response indicates success (even with 0 rows)
        if hasattr(response, 'count'):
            db_status = "successful"
        else:
             db_status = "failed (unexpected response)"
    except Exception as e:
        logger.error(f"Health check Supabase query failed: {e}")
        db_status = "failed (query error)"

    return {"status": "ok" if db_status == "successful" else "error", "db_connection": db_status}

# --- Local Development Runner ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server for local development...")
    # Render provides the PORT env var; default to 8000 locally if not set
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

