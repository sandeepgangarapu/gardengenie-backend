import logging
from typing import Optional, Dict, Any

from ..llm_base import make_llm_request, create_payload, validate_and_parse_response
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

def call_openrouter_llm_indoor(plant_name: str) -> Optional[Dict[str, Any]]:
    """Calls the OpenRouter API to get indoor plant care instructions as JSON."""
    prompt = HOUSEPLANTS_PROMPT.format(plant_name=plant_name)
    payload = create_payload(prompt)
    result = make_llm_request(payload)
    return validate_and_parse_response(result, ['plantName', 'care_plan', 'requirements'], 'houseplant', plant_name)

def call_openrouter_llm_edible_annuals(plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Calls the OpenRouter API to get edible annual care instructions as JSON."""
    prompt = EDIBLE_PLANTS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    payload = create_payload(prompt)
    result = make_llm_request(payload)
    return validate_and_parse_response(result, ['plantName', 'care_plan', 'requirements'], 'edible annual', plant_name)

def call_openrouter_llm_fruit_trees(plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Calls the OpenRouter API to get fruit tree care instructions as JSON."""
    prompt = FRUIT_TREES_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    payload = create_payload(prompt)
    result = make_llm_request(payload)
    return validate_and_parse_response(result, ['plantName', 'care_plan', 'requirements'], 'fruit tree', plant_name)

def call_openrouter_llm_ornamental_perennials(plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Calls the OpenRouter API to get ornamental perennial care instructions as JSON."""
    prompt = ORNAMENTAL_PERENNIALS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    payload = create_payload(prompt)
    result = make_llm_request(payload)
    return validate_and_parse_response(result, ['plantName', 'care_plan', 'requirements'], 'ornamental perennial', plant_name)

def call_openrouter_llm_annual_flowers(plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Calls the OpenRouter API to get annual flower care instructions as JSON."""
    prompt = ANNUAL_FLOWERS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    payload = create_payload(prompt)
    result = make_llm_request(payload)
    return validate_and_parse_response(result, ['plantName', 'care_plan', 'requirements'], 'annual flower', plant_name)

def call_openrouter_llm_bulbs(plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Calls the OpenRouter API to get bulb care instructions as JSON."""
    prompt = BULBS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    payload = create_payload(prompt)
    result = make_llm_request(payload)
    return validate_and_parse_response(result, ['plantName', 'care_plan', 'requirements'], 'bulb', plant_name)

def call_openrouter_llm_succulents(plant_name: str, user_zone: str, plant_group: str) -> Optional[Dict[str, Any]]:
    """Calls the OpenRouter API to get succulent care instructions as JSON."""
    prompt = SUCCULENTS_PROMPT.format(plant_name=plant_name, user_zone=user_zone, plant_group=plant_group)
    payload = create_payload(prompt)
    result = make_llm_request(payload)
    return validate_and_parse_response(result, ['plantName', 'care_plan', 'requirements'], 'succulent', plant_name)

def generate_plant_care_instructions(plant_name: str, user_zone: str) -> Optional[Dict[str, Any]]:
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
    
    plant_group = classification_result["plant_group"]
    prompt_function = classification_result["prompt_function"]
    
    # Step 2: Call appropriate LLM function based on classification
    care_info = None
    
    if prompt_function == "houseplants":
        care_info = call_openrouter_llm_indoor(plant_name)
    elif prompt_function == "edible_annuals":
        care_info = call_openrouter_llm_edible_annuals(plant_name, user_zone, plant_group)
    elif prompt_function == "fruit_trees":
        care_info = call_openrouter_llm_fruit_trees(plant_name, user_zone, plant_group)
    elif prompt_function == "ornamental_perennials":
        care_info = call_openrouter_llm_ornamental_perennials(plant_name, user_zone, plant_group)
    elif prompt_function == "annual_flowers":
        care_info = call_openrouter_llm_annual_flowers(plant_name, user_zone, plant_group)
    elif prompt_function == "bulbs":
        care_info = call_openrouter_llm_bulbs(plant_name, user_zone, plant_group)
    elif prompt_function == "succulents":
        care_info = call_openrouter_llm_succulents(plant_name, user_zone, plant_group)
    else:
        logger.error(f"Unknown prompt function: {prompt_function}")
        return None

    if care_info is None:
        logger.error(f"Failed to generate care instructions for '{plant_name}'")
        return None

    # Step 3: Store results in database
    storage_success = store_plant_and_care_instructions(
        original_plant_name=plant_name,
        original_user_zone=user_zone,
        care_info=care_info,
        model_used="google/gemini-2.5-flash-preview",  # Could be moved to config
        plant_group=plant_group
    )
    
    if not storage_success:
        logger.error("Failed to store primary plant/care information in Supabase.")
        # Still return the care_info even if storage fails
        # The API can decide whether to raise an error or not
    
    # Step 4: Fetch and store image (optional, doesn't affect main functionality)
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