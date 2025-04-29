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
from postgrest import APIError # Added for specific exception handling

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
    version="1.4.0", # Bump version for Unsplash integration
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

# --- Unsplash Configuration ---
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"

if not UNSPLASH_ACCESS_KEY:
    logger.warning("UNSPLASH_ACCESS_KEY not found in environment variables. Image fetching will be skipped.")


# --- Pydantic Models ---
class PlantCareInput(BaseModel):
    plant_name: str = Field(..., min_length=1, description="The user-provided plant name (e.g., tomato, Fiddle Leaf Fig).")
    user_zone: str = Field(..., pattern=r"^\d{1,2}[ab]?$", description="The user's USDA Hardiness Zone (e.g., 7a, 8b, 5).")


# --- Helper Functions ---

# Removed MCP-related helpers: escape_sql_string, escape_sql_array, execute_supabase_sql

def get_unsplash_image(plant_name: str) -> Optional[dict]:
    """Queries the Unsplash API for an image of the given plant name."""
    if not UNSPLASH_ACCESS_KEY:
        logger.info("Unsplash Access Key missing, skipping image fetch.")
        return None

    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}",
        "Accept-Version": "v1"
    }
    params = {
        "query": plant_name,
        "per_page": 1, # We only need the first result
        "orientation": "landscape" # Optional: prefer landscape images
    }

    try:
        response = requests.get(UNSPLASH_API_URL, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        results = data.get("results")
        if not results:
            logger.info(f"No Unsplash image found for query: '{plant_name}'")
            return None

        first_image = results[0]
        image_url = first_image.get("urls", {}).get("regular") # Get a reasonably sized image
        photographer_name = first_image.get("user", {}).get("name")
        photographer_url = first_image.get("user", {}).get("links", {}).get("html")

        if not image_url:
            logger.warning(f"Found Unsplash result for '{plant_name}' but missing image URL.")
            return None

        logger.info(f"Found Unsplash image for '{plant_name}' by {photographer_name}")
        return {
            "unsplash_image_url": image_url,
            "unsplash_photographer_name": photographer_name,
            "unsplash_photographer_url": photographer_url,
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling Unsplash API for '{plant_name}': {e}")
        if hasattr(e, 'response') and e.response is not None:
            logger.error(f"Unsplash Response Status: {e.response.status_code}")
            logger.error(f"Unsplash Response Text: {e.response.text}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Error parsing Unsplash response for '{plant_name}': {e} - Response: {response.text if 'response' in locals() else 'N/A'}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during Unsplash call for '{plant_name}': {e}")
        return None


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
        "priority": "[must do OR good to do OR skip]", // Use 'optional' instead of 'skip'
        "months": "[e.g., April OR May]" // Indicate SINGLE best month for this zone
      }},
      {{
        "step": "[Care step 2 description]",
        "priority": "[must do OR good to do OR optional]", // Use 'optional' instead of 'skip'
        "months": "[e.g., April OR May]" // Indicate SINGLE best month for this zone
      }}
      // ... more steps as relevant, steps ordered as they appear here
    ],
    "summer": [
      {{
        "step": "[Care step 1 description]",
        "priority": "[must do OR good to do OR optional]", // Use 'optional' instead of 'skip'
        "months": "[e.g., June OR July]" // Indicate SINGLE best month for this zone
      }},
      {{
        "step": "[Care step 2 description]",
        "priority": "[must do OR good to do OR optional]", // Use 'optional' instead of 'skip'
        "months": "[e.g., July OR August]" // Indicate SINGLE best month for this zone
      }}
      // ... more steps as relevant
    ],
    "fall": [
      {{
        "step": "[Care step 1 description]",
        "priority": "[must do OR good to do OR optional]", // Use 'optional' instead of 'skip'
        "months": "[e.g., September OR October]" // Indicate SINGLE best month for this zone
      }},
      {{
        "step": "[Care step 2 description]",
        "priority": "[must do OR good to do OR optional]", // Use 'optional' instead of 'skip'
        "months": "[e.g., October OR November]" // Indicate SINGLE best month for this zone
      }}
      // ... more steps as relevant
    ],
    "winter": [
      {{
        "step": "[Care step 1 description]",
        "priority": "[must do OR good to do OR optional]", // Use 'optional' instead of 'skip'
        "months": "[e.g., December OR January]" // Indicate SINGLE best month for this zone
      }},
      {{
        "step": "[Care step 2 description]",
        "priority": "[must do OR good to do OR optional]", // Use 'optional' instead of 'skip'
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
Priority/Season ENUMs: If `priority` or `season` columns in Supabase are ENUMs, ensure the generated strings match valid ENUM values exactly (e.g., 'spring', 'summer', 'fall', 'winter', 'must do', 'good to do', 'optional'). Use 'optional' if something is not critical.
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

def _store_plant_image(plant_name: str, image_data: dict) -> None:
    """Helper to find/insert/update plant image data in Supabase."""
    if not supabase or not image_data or not plant_name:
        logger.warning("Skipping image storage due to missing Supabase client, image data, or plant name.")
        return

    try:
        # Check if image record already exists for this plant name
        find_image_resp: APIResponse = supabase.table('plant_images')\
                                            .select('id')\
                                            .eq('name', plant_name)\
                                            .limit(1)\
                                            .execute()

        if find_image_resp is None:
            logger.error(f"Supabase query execution (find image for '{plant_name}') returned None.")
            return # Don't block main flow

        image_record_data = {
            'name': plant_name,
            'unsplash_image_url': image_data.get('unsplash_image_url'),
            'unsplash_photographer_name': image_data.get('unsplash_photographer_name'),
            'unsplash_photographer_url': image_data.get('unsplash_photographer_url'),
            # 'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat() # Let trigger handle
        }

        if find_image_resp.data:
            # Image record exists, update it
            existing_image_id = find_image_resp.data[0].get('id')
            if existing_image_id:
                logger.info(f"Updating existing image record for '{plant_name}' (ID: {existing_image_id})")
                update_image_resp: APIResponse = supabase.table('plant_images')\
                                                        .update(image_record_data)\
                                                        .eq('id', existing_image_id)\
                                                        .execute()
                if update_image_resp is None:
                     logger.error(f"Supabase image update execution for '{plant_name}' returned None.")
                # No need to check data length on update success typically
            else:
                 logger.error(f"Found image record for '{plant_name}' but missing ID.")

        else:
            # Image record doesn't exist, insert it
            logger.info(f"Inserting new image record for '{plant_name}'")
            insert_image_resp: APIResponse = supabase.table('plant_images')\
                                                .insert(image_record_data)\
                                                .execute()
            if insert_image_resp is None:
                logger.error(f"Supabase image insert execution for '{plant_name}' returned None.")
            elif not insert_image_resp.data:
                logger.error(f"Failed to insert image record for '{plant_name}'. Response: {insert_image_resp!r}")

    except APIError as api_e:
        logger.error(f"Supabase API Error during image storage for '{plant_name}': {api_e.message}", exc_info=False) # Keep log concise
    except Exception as e:
        logger.error(f"An unexpected error occurred during image storage for '{plant_name}': {e}", exc_info=False) # Keep log concise


def store_result(
    original_plant_name: str, # Keep original for logging if needed
    original_user_zone: str, # Keep original for logging if needed
    care_info: dict,
    model_used: str # Keep for logging if needed
) -> bool:
    """
    Stores the generated care instructions and fetches/stores an Unsplash image
    in Supabase using supabase-py client.
    Returns True if plant & care instructions are stored successfully,
    logs warnings for image storage failures.
    """

    if supabase is None:
        logger.error("Supabase client is not initialized. Cannot store result.")
        return False

    if not isinstance(care_info, dict):
        logger.error("Invalid care_info type passed to store_result. Expected dict.")
        return False

    # 1. Extract Data from care_info (using .get for safety)
    plant_name = care_info.get('plantName') # Use the LLM-corrected name
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
    zone_suitability = care_info.get('zoneSuitability') # Extract zone suitability

    # Basic validation for core data needed for insertion
    if not plant_name or not zone:
        logger.error(f"Missing essential plantName or zone in care_info: {care_info}")
        return False

    plant_uuid: Optional[str] = None
    plant_and_care_stored_successfully = False # Track primary goal success

    try:
        # --- SECTION A: Store Plant and Care Instructions ---
        # 2. Find or Insert/Update Plant Record
        logger.debug(f"Checking for plant: {plant_name}, zone: {zone}")
        response: APIResponse = supabase.table('plants')\
                                    .select('plant_id')\
                                    .eq('plant_name', plant_name)\
                                    .eq('zone', zone)\
                                    .execute()

        # --- Add detailed logging ---
        logger.debug(f"Supabase find query response type: {type(response)}")
        logger.debug(f"Supabase find query response value: {response!r}") # Using !r for unambiguous representation
        # --- End detailed logging ---

        # --- Add check for None response ---
        if response is None:
            logger.error("Supabase query execution (find plant) returned None. Check connection/client state/API logs (maybe 406?).")
            return False # Fatal if we can't query
        # --- End added check ---

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
            'zone_suitability': zone_suitability, # Add zone suitability here
            # 'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat() # Let Supabase handle timestamp updates if configured
        }

        # --- Modify logic to handle list response ---
        if response.data and len(response.data) > 0:
            # Plant(s) exist
            if len(response.data) > 1:
                 logger.warning(f"Found multiple ({len(response.data)}) existing plant records for name '{plant_name}' and zone '{zone}'. Updating the first one found.")

            # Get UUID from the first result
            plant_uuid = response.data[0].get('plant_id')
            if not plant_uuid:
                 logger.error(f"Found plant record(s) but missing plant_id in the first result: {response.data[0]}")
                 return False # Fatal if we have inconsistent data

            logger.info(f"Found existing plant with UUID: {plant_uuid}. Updating.")
            update_response: APIResponse = supabase.table('plants')\
                                                .update(plant_data_for_upsert)\
                                                .eq('plant_id', plant_uuid)\
                                                .execute()
            # Check for None before checking attributes
            if update_response is None:
                logger.error("Supabase update execution returned None.")
                return False # Fatal if update fails
            # Note: Supabase update often returns empty data on success, so checking length might not be reliable.

        else:
            # Plant doesn't exist (response.data is empty list or None - handled above), Insert it
            logger.info(f"Inserting new plant: {plant_name}, zone: {zone}")
            insert_response: APIResponse = supabase.table('plants')\
                                                .insert(plant_data_for_upsert)\
                                                .execute()

            # Check for None before accessing data
            if insert_response is None:
                 logger.error("Supabase plant insert execution returned None.")
                 return False # Fatal if insert fails

            if insert_response.data and len(insert_response.data) > 0:
                plant_uuid = insert_response.data[0].get('plant_id')
                if not plant_uuid:
                    logger.error(f"Inserted plant but response missing plant_id: {insert_response.data}")
                    return False # Fatal if insert response is malformed
                logger.info(f"Inserted new plant with UUID: {plant_uuid}")
            else:
                logger.error(f"Failed to insert new plant. Response: {insert_response!r}") # Log response detail
                return False # Fatal if insert fails structurally

        # Ensure we have a plant_uuid
        if not plant_uuid:
             logger.error("Could not obtain plant_uuid after find/insert/update operations.")
             return False # Fatal if UUID logic fails

        # 3. Log the Query (Implementation depends on query_logs table - skipping for now)
        # logger.info("Query logging skipped.")

        # 4. Delete Old Seasonal Care Instructions for this Plant UUID
        logger.debug(f"Deleting old care instructions for plant_id: {plant_uuid}")
        delete_response: APIResponse = supabase.table('care_instructions')\
                                            .delete()\
                                            .eq('plant_id', plant_uuid)\
                                            .execute()
        # Check for None before checking attributes
        if delete_response is None:
            logger.warning("Supabase delete execution returned None. Cannot confirm deletion of old care instructions.")
            # Don't make this fatal, proceed with inserting new ones
        # Deleting 0 rows is not an error here
        elif not hasattr(delete_response, 'data') and not hasattr(delete_response, 'count'): # Heuristic check
             logger.warning(f"Could not confirm deletion of old care instructions. Response: {delete_response!r}") # Log response detail
             # Don't make this fatal

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
            plant_and_care_stored_successfully = True # Plant was saved/updated
        else:
            logger.info(f"Inserting {len(seasonal_instructions_to_insert)} seasonal care instructions for plant_id: {plant_uuid}")
            insert_care_response: APIResponse = supabase.table('care_instructions')\
                                                    .insert(seasonal_instructions_to_insert)\
                                                    .execute()

            # Check for None before accessing data
            if insert_care_response is None:
                logger.error("Supabase care instructions insert execution returned None.")
                return False # Fatal if care instructions fail to insert

            if not insert_care_response.data or len(insert_care_response.data) != len(seasonal_instructions_to_insert):
                logger.error(f"Failed to insert all seasonal care instructions. Response: {insert_care_response!r}") # Log response detail
                # This indicates partial success or total failure of the batch insert
                return False # Fatal if care instructions fail to insert properly
            else:
                logger.info(f"Successfully stored {len(seasonal_instructions_to_insert)} seasonal care instructions.")
                plant_and_care_stored_successfully = True # Mark primary goal as successful

        # --- END SECTION A ---

    except APIError as api_e:
        # Catch specific Supabase/PostgREST API errors during plant/care storage
        logger.error(f"Supabase API Error during plant/care storage: {api_e.message}", exc_info=True)
        return False # Fatal
    except Exception as e:
        # Catch potential exceptions during plant/care storage
        logger.error(f"An unexpected error occurred during Supabase plant/care storage: {e}", exc_info=True)
        return False # Fatal

    # --- SECTION B: Fetch and Store Image ---
    # This runs only if Section A succeeded and we have a plant_name
    if plant_and_care_stored_successfully and plant_name:
        try:
            # 6. Get Unsplash Image
            image_data = get_unsplash_image(plant_name)

            # 7. Store Image Info (if found)
            if image_data:
                _store_plant_image(plant_name, image_data)
            else:
                logger.info(f"No image data found or fetched for '{plant_name}', skipping image storage.")

        except Exception as e:
            # Catch any unexpected errors during image fetch/store phase
            logger.error(f"An unexpected error occurred during image handling for '{plant_name}': {e}", exc_info=True)
            # Do not return False here, as the primary goal (plant/care storage) succeeded.

    # --- END SECTION B ---

    # Return the success status of the primary goal (storing plant & care info)
    return plant_and_care_stored_successfully


# --- API Endpoint ---

@app.post("/plant-care-instructions", response_model=dict)
async def get_plant_care_instructions(payload: PlantCareInput, request: Request):
    """
    Receives a plant name and USDA zone, generates detailed care instructions
    using an LLM via OpenRouter, stores the result (and fetches/stores an image)
    in Supabase using supabase-py, and returns the care instructions as a JSON object.
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
    # Note: store_result now also handles image fetching/storage internally
    storage_success = store_result(
        original_plant_name=plant_name, # Pass the original name if needed for comparison/logging
        original_user_zone=user_zone,
        care_info=care_info,
        model_used=LLM_MODEL
    )
    if not storage_success:
        # Logged within store_result for fatal errors (plant/care storage failure)
        logger.error("Failed to store primary plant/care information in Supabase.")
        # Raise 500 if core storage failure should prevent user response
        raise HTTPException(status_code=500, detail="Failed to store core care instructions.")
    # If storage_success is True, it means plant/care info was stored.
    # Image storage failures are logged as warnings inside store_result but don't cause storage_success to be False.

    # 3. Return result (the dictionary itself)
    return care_info

@app.get("/health", status_code=200)
async def health_check():
    """Simple health check endpoint. Checks Supabase connection."""
    if supabase is None:
        return {"status": "error", "db_connection": "Supabase client not initialized"}
    db_status = "unknown" # Initialize
    try:
        # Simple query to check connection
        response = supabase.table('plants').select('plant_id', count='exact').limit(0).execute()
        # Check if response indicates success (even with 0 rows)
        # Check for None response first
        if response is None:
             db_status = "failed (query returned None)"
        # Check if count is present, indicating a successful query structure
        elif hasattr(response, 'count') and response.count is not None:
             db_status = "successful"
        else:
             # Log the actual response for debugging if it's unexpected
             logger.warning(f"Health check Supabase query response unexpected: {response!r}")
             db_status = "failed (unexpected response format)"

    except APIError as api_e:
        logger.error(f"Health check Supabase API error: {api_e.message}")
        db_status = f"failed (API error: {api_e.code})" # Include error code if available
    except Exception as e:
        logger.error(f"Health check Supabase query failed: {e}", exc_info=False) # Keep log concise
        db_status = "failed (query exception)"

    return {"status": "ok" if db_status == "successful" else "error", "db_connection": db_status}

# --- Local Development Runner ---
if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server for local development...")
    # Render provides the PORT env var; default to 8000 locally if not set
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

