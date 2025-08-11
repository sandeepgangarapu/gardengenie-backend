import logging
from typing import Optional, Dict, Any

from ..llm_base import make_llm_request, create_payload, validate_and_parse_response
from ...config import LLM_MODEL
from .prompts.houseplants_prompt import HOUSEPLANTS_PROMPT
from .prompts.edible_plants_prompt import EDIBLE_PLANTS_PROMPT
from .prompts.fruit_trees_prompt import FRUIT_TREES_PROMPT
from .prompts.ornamental_perennials_prompt import ORNAMENTAL_PERENNIALS_PROMPT
from .prompts.annual_flowers_prompt import ANNUAL_FLOWERS_PROMPT
from .prompts.bulbs_prompt import BULBS_PROMPT
from .prompts.succulents_prompt import SUCCULENTS_PROMPT

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

def call_openrouter_llm_dispatch(group_key: str, plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Dispatch to the correct prompt and call LLM in a DRY way."""
    if group_key == "houseplants":
        prompt = HOUSEPLANTS_PROMPT.format(plant_name=plant_name)
    elif group_key == "edible_annuals":
        prompt = EDIBLE_PLANTS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "fruit_trees":
        prompt = FRUIT_TREES_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "ornamental_perennials":
        prompt = ORNAMENTAL_PERENNIALS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "annual_flowers":
        prompt = ANNUAL_FLOWERS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "bulbs":
        prompt = BULBS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    elif group_key == "succulents":
        prompt = SUCCULENTS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    else:
        logger.error(f"Unknown prompt group: {group_key}")
        return None

    payload = create_payload(prompt)
    result = make_llm_request(payload)
    return validate_and_parse_response(result, ['plantName', 'care_plan', 'requirements'], HUMAN_FRIENDLY_GROUP.get(group_key, group_key), plant_name)

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
    
    # Step 2: Call appropriate LLM function based on classification
    care_info = call_openrouter_llm_dispatch(prompt_function, plant_name, user_zone, plant_group)
    if care_info is None:
        logger.error(f"Failed to generate care instructions for '{plant_name}' using group '{prompt_function}'")
        return None

    # Step 3: Optionally store results in database
    if persist_to_db:
        raw_llm_response = care_info.get('__raw_llm_response') if isinstance(care_info, dict) else None
        resolved_model_used = (
            raw_llm_response.get('model') if isinstance(raw_llm_response, dict) and raw_llm_response.get('model') else LLM_MODEL
        )

        storage_success = store_plant_and_care_instructions(
            original_plant_name=plant_name,
            original_user_zone=user_zone,
            care_info=care_info,
            model_used=resolved_model_used,
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