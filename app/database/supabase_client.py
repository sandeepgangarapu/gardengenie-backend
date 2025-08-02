import logging
import datetime
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions
from postgrest import APIResponse, APIError

from ..config import SUPABASE_URL, SUPABASE_KEY

logger = logging.getLogger(__name__)

# --- Supabase Client Initialization ---
supabase: Optional[Client] = None

def initialize_supabase() -> Optional[Client]:
    """Initialize the Supabase client."""
    global supabase
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("Supabase URL or Key not found in environment variables. Database operations will fail.")
        return None
    
    try:
        # Use ClientOptions for potential future configurations (e.g., schema)
        options: ClientOptions = ClientOptions()
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options)
        logger.info("Supabase client initialized successfully.")
        return supabase
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        return None

def get_supabase_client() -> Optional[Client]:
    """Get the Supabase client, initializing if necessary."""
    global supabase
    if supabase is None:
        supabase = initialize_supabase()
    return supabase

def validate_care_structure(care_details: Any, plant_name: str = "Unknown") -> Dict[str, Any]:
    """
    Validate the care instructions structure from LLM response.
    
    Args:
        care_details: The care section from LLM response
        plant_name: Plant name for logging context
        
    Returns:
        Dict with validation results: {'valid': bool, 'errors': list, 'warnings': list}
    """
    validation_result = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    # Check if care_details is a dictionary
    if not isinstance(care_details, dict):
        validation_result['valid'] = False
        validation_result['errors'].append(f"Care details must be a dictionary, got {type(care_details).__name__}")
        return validation_result
    
    # Check if care_details is empty
    if not care_details:
        validation_result['warnings'].append("Care details dictionary is empty")
        return validation_result
    
    valid_priorities = ['must do', 'good to do', 'optional']
    total_instructions = 0
    
    # Validate each care phase/section
    for care_phase, steps in care_details.items():
        if not isinstance(steps, list):
            validation_result['valid'] = False
            validation_result['errors'].append(f"Care phase '{care_phase}' must contain a list of steps, got {type(steps).__name__}")
            continue
            
        if not steps:
            validation_result['warnings'].append(f"Care phase '{care_phase}' has no care instructions")
            continue
            
        # Validate each step in the care phase
        for i, step_detail in enumerate(steps):
            step_context = f"Care phase '{care_phase}', step {i+1}"
            
            if not isinstance(step_detail, dict):
                validation_result['valid'] = False
                validation_result['errors'].append(f"{step_context}: Step must be a dictionary, got {type(step_detail).__name__}")
                continue
            
            # Check required fields
            step_description = step_detail.get('step')
            if not step_description or not isinstance(step_description, str) or not step_description.strip():
                validation_result['valid'] = False
                validation_result['errors'].append(f"{step_context}: Missing or empty 'step' description")
            
            # Validate priority if present
            priority = step_detail.get('priority')
            if priority and priority not in valid_priorities:
                validation_result['warnings'].append(f"{step_context}: Invalid priority '{priority}'. Expected one of {valid_priorities}")
            
            # Check for timing information (months or timing fields)
            months = step_detail.get('months')
            timing = step_detail.get('timing')
            if not months and not timing:
                validation_result['warnings'].append(f"{step_context}: No timing information (months or timing) provided")
            
            total_instructions += 1
    
    # Final validation checks
    if total_instructions == 0:
        validation_result['valid'] = False
        validation_result['errors'].append("No valid care instructions found in any care phase")
    
    logger.debug(f"Care validation for '{plant_name}': {validation_result}")
    return validation_result

def store_plant_image(plant_name: str, image_data: dict) -> None:
    """Helper to find/insert/update plant image data in Supabase."""
    client = get_supabase_client()
    if not client or not image_data or not plant_name:
        logger.warning("Skipping image storage due to missing Supabase client, image data, or plant name.")
        return

    try:
        # Check if image record already exists for this plant name
        find_image_resp: APIResponse = client.table('plant_images')\
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
        }

        if find_image_resp.data:
            # Image record exists, update it
            existing_image_id = find_image_resp.data[0].get('id')
            if existing_image_id:
                logger.info(f"Updating existing image record for '{plant_name}' (ID: {existing_image_id})")
                update_image_resp: APIResponse = client.table('plant_images')\
                                                        .update(image_record_data)\
                                                        .eq('id', existing_image_id)\
                                                        .execute()
                if update_image_resp is None:
                     logger.error(f"Supabase image update execution for '{plant_name}' returned None.")
            else:
                 logger.error(f"Found image record for '{plant_name}' but missing ID.")

        else:
            # Image record doesn't exist, insert it
            logger.info(f"Inserting new image record for '{plant_name}'")
            insert_image_resp: APIResponse = client.table('plant_images')\
                                                .insert(image_record_data)\
                                                .execute()
            if insert_image_resp is None:
                logger.error(f"Supabase image insert execution for '{plant_name}' returned None.")
            elif not insert_image_resp.data:
                logger.error(f"Failed to insert image record for '{plant_name}'. Response: {insert_image_resp!r}")

    except APIError as api_e:
        logger.error(f"Supabase API Error during image storage for '{plant_name}': {api_e.message}", exc_info=False)
    except Exception as e:
        logger.error(f"An unexpected error occurred during image storage for '{plant_name}': {e}", exc_info=False)

def store_plant_and_care_instructions(
    original_plant_name: str,
    original_user_zone: str,
    care_info: dict,
    model_used: str,
    plant_group: str = None
) -> bool:
    """
    Stores the generated care instructions in Supabase using supabase-py client.
    Returns True if plant & care instructions are stored successfully.
    """
    client = get_supabase_client()
    if client is None:
        logger.error("Supabase client is not initialized. Cannot store result.")
        return False

    if not isinstance(care_info, dict):
        logger.error("Invalid care_info type passed to store_result. Expected dict.")
        return False

    # Extract Data from care_info (using .get for safety)
    plant_name = care_info.get('plantName')  # Use the LLM-corrected name
    zone = original_user_zone  # Use the original zone passed from the user
    description = care_info.get('description')
    plant_type = care_info.get('type')
    sun_requirements = care_info.get('sun')
    seed_start_month = care_info.get('seedStartingMonth')
    plant_month = care_info.get('plantingMonth')
    seed_instructions = care_info.get('seedStartingInstructions') or []
    plant_instructions = care_info.get('plantingInstructions') or []
    care_details = care_info.get('care', {})
    zone_suitability = care_info.get('zoneSuitability')
    seasonality = care_info.get('seasonality')
    final_plant_group = plant_group or care_info.get('plant_group')

    # Basic validation for core data needed for insertion
    if not plant_name or (not zone and final_plant_group not in ['Houseplants', 'Succulents']):
        logger.error(f"Missing essential plantName or zone in care_info: {care_info}")
        return False

    # Validate care structure before proceeding with database operations
    care_validation = validate_care_structure(care_details, plant_name)
    
    if not care_validation['valid']:
        logger.error(f"Invalid care structure for '{plant_name}': {care_validation['errors']}")
        return False
    
    if care_validation['warnings']:
        logger.warning(f"Care structure warnings for '{plant_name}': {care_validation['warnings']}")

    plant_uuid: Optional[str] = None

    try:
        # Find or Insert/Update Plant Record
        logger.debug(f"Checking for plant: {plant_name}, zone: {zone}, plant_group: {final_plant_group}")
        
        # Use different query logic for houseplants vs outdoor plants based on plant group
        if final_plant_group in ['Houseplants', 'Succulents']:
            # For houseplants/succulents, search by name and plant group (zone should be null)
            response: APIResponse = client.table('plants')\
                                        .select('plant_id')\
                                        .eq('plant_name', plant_name)\
                                        .eq('plant_group', final_plant_group)\
                                        .is_('zone', 'null')\
                                        .execute()
        else:
            # For outdoor plants, search by name and zone
            response: APIResponse = client.table('plants')\
                                        .select('plant_id')\
                                        .eq('plant_name', plant_name)\
                                        .eq('zone', zone)\
                                        .execute()

        logger.debug(f"Supabase find query response type: {type(response)}")
        logger.debug(f"Supabase find query response value: {response!r}")

        if response is None:
            logger.error("Supabase query execution (find plant) returned None. Check connection/client state/API logs (maybe 406?).")
            return False

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
            'zone_suitability': zone_suitability,
            'seasonality': seasonality,
            'plant_group': final_plant_group,
        }

        if response.data and len(response.data) > 0:
            # Plant(s) exist
            if len(response.data) > 1:
                 logger.warning(f"Found multiple ({len(response.data)}) existing plant records for name '{plant_name}' and zone '{zone}'. Updating the first one found.")

            # Get UUID from the first result
            plant_uuid = response.data[0].get('plant_id')
            if not plant_uuid:
                 logger.error(f"Found plant record(s) but missing plant_id in the first result: {response.data[0]}")
                 return False

            logger.info(f"Found existing plant with UUID: {plant_uuid}. Updating.")
            update_response: APIResponse = client.table('plants')\
                                                .update(plant_data_for_upsert)\
                                                .eq('plant_id', plant_uuid)\
                                                .execute()
            if update_response is None:
                logger.error("Supabase update execution returned None.")
                return False

        else:
            # Plant doesn't exist, Insert it
            logger.info(f"Inserting new plant: {plant_name}, zone: {zone}")
            insert_response: APIResponse = client.table('plants')\
                                                .insert(plant_data_for_upsert)\
                                                .execute()

            if insert_response is None:
                 logger.error("Supabase plant insert execution returned None.")
                 return False

            if insert_response.data and len(insert_response.data) > 0:
                plant_uuid = insert_response.data[0].get('plant_id')
                if not plant_uuid:
                    logger.error(f"Inserted plant but response missing plant_id: {insert_response.data}")
                    return False
                logger.info(f"Inserted new plant with UUID: {plant_uuid}")
            else:
                logger.error(f"Failed to insert new plant. Response: {insert_response!r}")
                return False

        # Ensure we have a plant_uuid
        if not plant_uuid:
             logger.error("Could not obtain plant_uuid after find/insert/update operations.")
             return False

        # Delete Old Care Instructions for this Plant UUID
        logger.debug(f"Deleting old care instructions for plant_id: {plant_uuid}")
        delete_response: APIResponse = client.table('care_instructions')\
                                            .delete()\
                                            .eq('plant_id', plant_uuid)\
                                            .execute()
        if delete_response is None:
            logger.warning("Supabase delete execution returned None. Cannot confirm deletion of old care instructions.")

        # Prepare and Insert New Care Phase Instructions with enhanced validation
        care_instructions_to_insert = []
        skipped_instructions = 0
        
        for care_phase, steps in care_details.items():
            if not isinstance(steps, list):
                logger.error(f"Invalid care phase data for '{care_phase}': expected list, got {type(steps).__name__}. Skipping care phase.")
                skipped_instructions += 1
                continue
                
            for i, step_detail in enumerate(steps):
                if not isinstance(step_detail, dict):
                    logger.error(f"Invalid step data in care phase '{care_phase}', position {i+1}: expected dict, got {type(step_detail).__name__}. Skipping step.")
                    skipped_instructions += 1
                    continue
                
                # Validate required fields
                step_description = step_detail.get('step')
                if not step_description or not isinstance(step_description, str) or not step_description.strip():
                    logger.error(f"Missing or invalid step description in care phase '{care_phase}', position {i+1}. Skipping step.")
                    skipped_instructions += 1
                    continue
                
                # Create instruction row with validated data
                instruction_row = {
                    'plant_id': plant_uuid,
                    'care_phase': care_phase,
                    'months': step_detail.get('months'),
                    'step_description': step_description.strip(),
                    'priority': step_detail.get('priority'),
                    'order_within_season': i + 1
                }
                care_instructions_to_insert.append(instruction_row)
        
        # Log any skipped instructions
        if skipped_instructions > 0:
            logger.warning(f"Skipped {skipped_instructions} invalid care instructions for '{plant_name}'")

        if not care_instructions_to_insert:
            if skipped_instructions > 0:
                logger.error(f"All care instructions were invalid for '{plant_name}'. No instructions to insert.")
                return False
            else:
                logger.info("No care instructions generated by LLM to insert.")
                return True
        else:
            logger.info(f"Inserting {len(care_instructions_to_insert)} care instructions for plant_id: {plant_uuid}")
            insert_care_response: APIResponse = client.table('care_instructions')\
                                                    .insert(care_instructions_to_insert)\
                                                    .execute()

            if insert_care_response is None:
                logger.error("Supabase care instructions insert execution returned None.")
                return False

            if not insert_care_response.data or len(insert_care_response.data) != len(care_instructions_to_insert):
                logger.error(f"Failed to insert all care instructions. Response: {insert_care_response!r}")
                return False
            else:
                logger.info(f"Successfully stored {len(care_instructions_to_insert)} care instructions.")
                return True

    except APIError as api_e:
        logger.error(f"Supabase API Error during plant/care storage: {api_e.message}", exc_info=True)
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during Supabase plant/care storage: {e}", exc_info=True)
        return False

def health_check() -> Dict[str, Any]:
    """Check Supabase connection health."""
    client = get_supabase_client()
    if client is None:
        return {"status": "error", "db_connection": "Supabase client not initialized"}
    
    db_status = "unknown"
    try:
        # Simple query to check connection
        response = client.table('plants').select('plant_id', count='exact').limit(0).execute()
        
        if response is None:
             db_status = "failed (query returned None)"
        elif hasattr(response, 'count') and response.count is not None:
             db_status = "successful"
        else:
             logger.warning(f"Health check Supabase query response unexpected: {response!r}")
             db_status = "failed (unexpected response format)"

    except APIError as api_e:
        logger.error(f"Health check Supabase API error: {api_e.message}")
        db_status = f"failed (API error: {api_e.code})"
    except Exception as e:
        logger.error(f"Health check Supabase query failed: {e}", exc_info=False)
        db_status = "failed (query exception)"

    return {"status": "ok" if db_status == "successful" else "error", "db_connection": db_status}

# Initialize the client when the module is imported
initialize_supabase() 