import logging
from typing import Optional, Dict, Any

from ..llm_base import make_llm_request, create_payload, validate_and_parse_response
from ...config import LLM_MODEL
# Import all the new separated prompts
from .prompts.houseplants_prompt import (
    HOUSEPLANTS_BASIC_INFO_PROMPT, 
    HOUSEPLANTS_PLANTING_PROMPT, 
    HOUSEPLANTS_CARE_PROMPT
)
from .prompts.edible_plants_prompt import (
    EDIBLE_PLANTS_BASIC_INFO_PROMPT,
    EDIBLE_PLANTS_PLANTING_PROMPT,
    EDIBLE_PLANTS_CARE_PROMPT
)
from .prompts.fruit_trees_prompt import (
    FRUIT_TREES_BASIC_INFO_PROMPT,
    FRUIT_TREES_PLANTING_PROMPT,
    FRUIT_TREES_CARE_PROMPT
)
from .prompts.ornamental_perennials_prompt import (
    ORNAMENTAL_PERENNIALS_BASIC_INFO_PROMPT,
    ORNAMENTAL_PERENNIALS_PLANTING_PROMPT,
    ORNAMENTAL_PERENNIALS_CARE_PROMPT
)
from .prompts.annual_flowers_prompt import (
    ANNUAL_FLOWERS_BASIC_INFO_PROMPT,
    ANNUAL_FLOWERS_PLANTING_PROMPT,
    ANNUAL_FLOWERS_CARE_PROMPT
)
from .prompts.bulbs_prompt import (
    BULBS_BASIC_INFO_PROMPT,
    BULBS_PLANTING_PROMPT,
    BULBS_CARE_PROMPT
)
from .prompts.succulents_prompt import (
    SUCCULENTS_BASIC_INFO_PROMPT,
    SUCCULENTS_PLANTING_PROMPT,
    SUCCULENTS_CARE_PROMPT
)

from .plant_classifier import get_plant_group_and_prompt
from ..image_service import get_unsplash_image
from ...database.supabase_client import store_plant_and_care_instructions, store_plant_image

logger = logging.getLogger(__name__)

HUMAN_FRIENDLY_GROUP = {
    "houseplants": "houseplant",
    "edible_annuals": "edible annual",
    "fruit_trees": "fruit tree",
    "ornamental_perennials": "ornamental perennial",
    "annual_flowers": "annual flower",
    "bulbs": "bulb",
    "succulents": "succulent",
}

def call_basic_info_prompt(group_key: str, plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Call the basic info prompt for a plant group with retry logic for truncated responses."""
    if group_key == "houseplants":
        prompt = HOUSEPLANTS_BASIC_INFO_PROMPT.format(plant_name=plant_name)
    elif group_key == "edible_annuals":
        prompt = EDIBLE_PLANTS_BASIC_INFO_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "fruit_trees":
        prompt = FRUIT_TREES_BASIC_INFO_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "ornamental_perennials":
        prompt = ORNAMENTAL_PERENNIALS_BASIC_INFO_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "annual_flowers":
        prompt = ANNUAL_FLOWERS_BASIC_INFO_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "bulbs":
        prompt = BULBS_BASIC_INFO_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "succulents":
        prompt = SUCCULENTS_BASIC_INFO_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    else:
        logger.error(f"Unknown prompt group: {group_key}")
        return None

    # Use higher max_tokens for basic info prompts to reduce truncation risk
    payload = create_payload(prompt, max_tokens=3500)
    
    # Try up to 3 attempts to mitigate occasional truncation
    for attempt in range(1, 4):
        result = make_llm_request(payload)
        if not result:
            continue

        # Validate response with retry logic
        parsed_result = validate_and_parse_response(result, ['plantName', 'requirements'], HUMAN_FRIENDLY_GROUP.get(group_key, group_key), plant_name)
        
        if parsed_result is not None:
            # Success - return the parsed result
            return parsed_result
        
        # If validation failed, check if it was due to truncation
        content = result.get("content", "") or ""
        content_stripped = content.rstrip()
        if not content_stripped.endswith('}') or not content_stripped.startswith('{'):
            logger.warning(f"Attempt {attempt}: Basic info prompt response appears truncated for {group_key} '{plant_name}'. Content length: {len(content)}. Retrying...")
            continue
        else:
            # Not a truncation issue, some other parsing problem - don't retry
            logger.error(f"Basic info prompt validation failed for non-truncation reason for {group_key} '{plant_name}'. Stopping retries.")
            break
    
    # All attempts failed
    logger.error(f"Failed to generate valid basic info response for {group_key} '{plant_name}' after 3 attempts")
    return None

def call_planting_prompt(group_key: str, plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Call the planting prompt for a plant group with retry logic for truncated responses."""
    if group_key == "houseplants":
        prompt = HOUSEPLANTS_PLANTING_PROMPT.format(plant_name=plant_name)
    elif group_key == "edible_annuals":
        prompt = EDIBLE_PLANTS_PLANTING_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "fruit_trees":
        prompt = FRUIT_TREES_PLANTING_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "ornamental_perennials":
        prompt = ORNAMENTAL_PERENNIALS_PLANTING_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "annual_flowers":
        prompt = ANNUAL_FLOWERS_PLANTING_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "bulbs":
        prompt = BULBS_PLANTING_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "succulents":
        prompt = SUCCULENTS_PLANTING_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    else:
        logger.error(f"Unknown prompt group: {group_key}")
        return None

    # Use higher max_tokens for planting prompts to reduce truncation risk
    payload = create_payload(prompt, max_tokens=4000)
    
    # Try up to 3 attempts to mitigate occasional truncation
    for attempt in range(1, 4):
        result = make_llm_request(payload)
        if not result:
            continue

        # Validate response with retry logic
        parsed_result = validate_and_parse_response(result, ['seedStartingMonth', 'plantingMonth'], HUMAN_FRIENDLY_GROUP.get(group_key, group_key), plant_name)
        
        if parsed_result is not None:
            # Success - return the parsed result
            return parsed_result
        
        # If validation failed, check if it was due to truncation
        content = result.get("content", "") or ""
        content_stripped = content.rstrip()
        if not content_stripped.endswith('}') or not content_stripped.startswith('{'):
            logger.warning(f"Attempt {attempt}: Planting prompt response appears truncated for {group_key} '{plant_name}'. Content length: {len(content)}. Retrying...")
            continue
        else:
            # Not a truncation issue, some other parsing problem - don't retry
            logger.error(f"Planting prompt validation failed for non-truncation reason for {group_key} '{plant_name}'. Stopping retries.")
            break
    
    # All attempts failed
    logger.error(f"Failed to generate valid planting response for {group_key} '{plant_name}' after 3 attempts")
    return None

def call_care_prompt(group_key: str, plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Call the care prompt for a plant group with retry logic for truncated responses."""
    if group_key == "houseplants":
        prompt = HOUSEPLANTS_CARE_PROMPT.format(plant_name=plant_name)
    elif group_key == "edible_annuals":
        prompt = EDIBLE_PLANTS_CARE_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "fruit_trees":
        prompt = FRUIT_TREES_CARE_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "ornamental_perennials":
        prompt = ORNAMENTAL_PERENNIALS_CARE_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "annual_flowers":
        prompt = ANNUAL_FLOWERS_CARE_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "bulbs":
        prompt = BULBS_CARE_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "succulents":
        prompt = SUCCULENTS_CARE_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    else:
        logger.error(f"Unknown prompt group: {group_key}")
        return None

    # Use higher max_tokens for care prompts to reduce truncation risk
    payload = create_payload(prompt, max_tokens=4500)
    
    # Try up to 3 attempts to mitigate occasional truncation
    for attempt in range(1, 4):
        result = make_llm_request(payload)
        if not result:
            continue

        # Validate response with retry logic
        parsed_result = validate_and_parse_response(result, ['care_plan'], HUMAN_FRIENDLY_GROUP.get(group_key, group_key), plant_name)
        
        if parsed_result is not None:
            # Success - return the parsed result
            return parsed_result
        
        # If validation failed, check if it was due to truncation
        content = result.get("content", "") or ""
        content_stripped = content.rstrip()
        if not content_stripped.endswith('}') or not content_stripped.startswith('{'):
            logger.warning(f"Attempt {attempt}: Care prompt response appears truncated for {group_key} '{plant_name}'. Content length: {len(content)}. Retrying...")
            continue
        else:
            # Not a truncation issue, some other parsing problem - don't retry
            logger.error(f"Care prompt validation failed for non-truncation reason for {group_key} '{plant_name}'. Stopping retries.")
            break
    
    # All attempts failed
    logger.error(f"Failed to generate valid care response for {group_key} '{plant_name}' after 3 attempts")
    return None

# --- New 3-Step Plant Care Functions ---

def generate_plant_basic_info(
    plant_name: str,
    user_zone: str,
    persist_to_db: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Generate basic plant information (Step 1 of 3-step process).
    
    Args:
        plant_name: The name of the plant
        user_zone: The user's USDA hardiness zone
        persist_to_db: Whether to store in database
        
    Returns:
        Dictionary containing basic plant info and plant_id, or None if generation fails
    """
    # Step 1: Classify plant and get appropriate prompt function
    classification_result = get_plant_group_and_prompt(plant_name)
    if not classification_result:
        logger.error(f"Failed to classify plant '{plant_name}'")
        return None
    # If the input is not a plant, short-circuit with a sentinel
    if not classification_result.get('is_plant', True):
        return {"__non_plant": True, "message": classification_result.get('message', 'Not a plant.')}
    
    plant_group = classification_result["plant_group"]
    prompt_function = classification_result["prompt_function"]
    
    # Step 2: Call basic info prompt
    basic_info = call_basic_info_prompt(prompt_function, plant_name, user_zone, plant_group)
    if basic_info is None:
        logger.error(f"Failed to generate basic info for '{plant_name}' using group '{prompt_function}'")
        return None

    # Add plant_group to the response
    basic_info["plant_group"] = plant_group
    
    # Step 3: Optionally store results in database
    plant_id = None
    if persist_to_db:
        from ...database.supabase_client import store_plant_basic_info
        plant_id = store_plant_basic_info(
            original_plant_name=plant_name,
            original_user_zone=user_zone,
            basic_info=basic_info,
            plant_group=plant_group
        )
        
        if not plant_id:
            logger.warning(f"Failed to store basic info for '{plant_name}' in database, but continuing...")
    
    basic_info["plant_id"] = plant_id
    return basic_info

def generate_plant_planting_info(
    plant_id: str,
    plant_name: str,
    user_zone: str,
    plant_group: str,
    prompt_function: str,
    persist_to_db: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Generate planting instructions (Step 2 of 3-step process).
    
    Args:
        plant_id: UUID of the plant in database
        plant_name: The name of the plant
        user_zone: The user's USDA hardiness zone
        plant_group: The plant group from classification
        prompt_function: The prompt function to use
        persist_to_db: Whether to store in database
        
    Returns:
        Dictionary containing planting instructions, or None if generation fails
    """
    # Call planting prompt
    planting_info = call_planting_prompt(prompt_function, plant_name, user_zone, plant_group)
    if planting_info is None:
        logger.error(f"Failed to generate planting info for '{plant_name}' using group '{prompt_function}'")
        return None

    planting_info["plant_id"] = plant_id
    
    # Optionally store results in database
    if persist_to_db:
        from ...database.supabase_client import store_plant_planting_info
        storage_success = store_plant_planting_info(plant_id, planting_info)
        
        if not storage_success:
            logger.warning(f"Failed to store planting info for plant_id '{plant_id}' in database, but continuing...")
    
    return planting_info

def generate_plant_care_info(
    plant_id: str,
    plant_name: str,
    user_zone: str,
    plant_group: str,
    prompt_function: str,
    persist_to_db: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Generate care instructions (Step 3 of 3-step process).
    
    Args:
        plant_id: UUID of the plant in database
        plant_name: The name of the plant
        user_zone: The user's USDA hardiness zone
        plant_group: The plant group from classification
        prompt_function: The prompt function to use
        persist_to_db: Whether to store in database
        
    Returns:
        Dictionary containing care instructions, or None if generation fails
    """
    # Call care prompt
    care_info = call_care_prompt(prompt_function, plant_name, user_zone, plant_group)
    if care_info is None:
        logger.error(f"Failed to generate care info for '{plant_name}' using group '{prompt_function}'")
        return None

    care_info["plant_id"] = plant_id
    
    # Optionally store results in database
    if persist_to_db:
        from ...database.supabase_client import store_plant_care_info
        storage_success = store_plant_care_info(plant_id, care_info)
        
        if not storage_success:
            logger.warning(f"Failed to store care info for plant_id '{plant_id}' in database, but continuing...")
    
    return care_info

def generate_plant_care_instructions(
    plant_name: str,
    user_zone: str,
    perform_image_handling: bool = True,
    persist_to_db: bool = True,
) -> Optional[Dict[str, Any]]:
    """
    Generate complete plant care instructions for a given plant and zone.
    
    Args:
        plant_name: The name of the plant
        user_zone: The user's USDA hardiness zone
        
    Returns:
        Dictionary containing plant care instructions, or None if generation fails
    """
    # Step 1: Classify plant and get appropriate prompt function
    classification_result = get_plant_group_and_prompt(plant_name)
    if not classification_result:
        logger.error(f"Failed to classify plant '{plant_name}'")
        return None
    # If the input is not a plant, short-circuit with a sentinel
    if not classification_result.get('is_plant', True):
        return {"__non_plant": True, "message": classification_result.get('message', 'Not a plant.')}
    
    plant_group = classification_result["plant_group"]
    prompt_function = classification_result["prompt_function"]
    
    # Step 2: Call appropriate LLM function based on classification (legacy full prompt)
    # This function maintains backward compatibility by calling all three prompts
    basic_info = call_basic_info_prompt(prompt_function, plant_name, user_zone, plant_group)
    planting_info = call_planting_prompt(prompt_function, plant_name, user_zone, plant_group)
    care_info_part = call_care_prompt(prompt_function, plant_name, user_zone, plant_group)
    
    if basic_info is None or planting_info is None or care_info_part is None:
        logger.error(f"Failed to generate complete care instructions for '{plant_name}' using group '{prompt_function}'")
        return None
    
    # Merge all parts into a single response for backward compatibility
    care_info = {**basic_info, **planting_info, **care_info_part}
    if care_info is None:
        logger.error(f"Failed to generate care instructions for '{plant_name}' using group '{prompt_function}'")
        return None

    # Step 3: Optionally store results in database
    if persist_to_db:
        storage_success = store_plant_and_care_instructions(
            original_plant_name=plant_name,
            original_user_zone=user_zone,
            care_info=care_info,
            plant_group=plant_group
        )
        
        if not storage_success:
            logger.error("Failed to store primary plant/care information in Supabase.")
            # Still return the care_info even if storage fails
            # The API can decide whether to raise an error or not
    
    # Step 4: Optionally fetch and store image (can be moved to background)
    if perform_image_handling:
        try:
            corrected_plant_name = care_info.get('plantName', plant_name)
            image_data = get_unsplash_image(corrected_plant_name)
            if image_data:
                store_plant_image(corrected_plant_name, image_data)
            else:
                logger.info(f"No image data found for '{corrected_plant_name}', skipping image storage.")
        except Exception as e:
            logger.error(f"Error during image handling for '{plant_name}': {e}")
            # Don't let image errors affect the main result
    
    return care_info


def fetch_and_store_image_for_plant(plant_name: str) -> None:
    """Background-friendly helper to fetch Unsplash image data and store it."""
    try:
        image_data = get_unsplash_image(plant_name)
        if image_data:
            store_plant_image(plant_name, image_data)
        else:
            logger.info(f"No image data found for '{plant_name}', skipping image storage.")
    except Exception as e:
        logger.error(f"Background image handling error for '{plant_name}': {e}")