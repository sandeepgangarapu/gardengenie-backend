import json
import logging
from typing import Optional, Dict

from ..llm_base import make_llm_request, create_payload
from .prompts.plant_classification_prompt import PLANT_CLASSIFICATION_PROMPT

logger = logging.getLogger(__name__)

# Map detailed care categories to prompt functions
CATEGORY_TO_PROMPT = {
    "Vegetables": "edible_annuals",
    "Herbs": "edible_annuals",
    "Fruit Trees": "fruit_trees",
    "Flowering Shrubs": "ornamental_perennials",
    "Perennial Flowers": "ornamental_perennials", 
    "Ornamental Trees": "ornamental_perennials",
    "Annual Flowers": "annual_flowers",
    "Houseplants": "houseplants",
    "Succulents": "succulents",
    "Bulbs": "bulbs",
    "Native Plants": "ornamental_perennials"  # Native plants use ornamental perennial structure
}

def classify_plant_group(plant_name: str) -> Optional[Dict[str, str]]:
    """
    Classify plant to determine which care prompt to use.
    Returns dict with plant_group.
    """
    prompt = PLANT_CLASSIFICATION_PROMPT.format(plant_name=plant_name)

    # Structured output schema for classification with is_plant failsafe
    classification_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "PlantGroupClassification",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "is_plant": {"type": "boolean"},
                    "plant_group": {
                        "type": ["string", "null"],
                        "enum": [
                            "Vegetables",
                            "Herbs",
                            "Fruit Trees",
                            "Flowering Shrubs",
                            "Perennial Flowers",
                            "Annual Flowers",
                            "Ornamental Trees",
                            "Houseplants",
                            "Succulents",
                            "Bulbs",
                            "Native Plants",
                            None,
                        ],
                    },
                },
                "required": ["is_plant", "plant_group"],
            },
        },
    }

    payload = create_payload(prompt, max_tokens=128, temperature=0.0, response_format=classification_schema)
    
    # Try up to 3 attempts to mitigate occasional truncation
    for attempt in range(1, 4):
        result = make_llm_request(payload)
        if not result:
            continue

        content = result.get("content", "") or ""
        # If content appears truncated, retry
        if not content.rstrip().endswith('}'):
            logger.warning(f"Attempt {attempt}: classification JSON appears truncated. Retrying...")
            continue

        try:
            classification = json.loads(content)
        except json.JSONDecodeError as json_e:
            logger.warning(f"Attempt {attempt}: failed to decode classification JSON: {json_e}. Retrying...")
            continue

        # Basic shape validation
        if "is_plant" not in classification or "plant_group" not in classification:
            logger.warning(f"Attempt {attempt}: LLM JSON missing required fields: {classification}. Retrying...")
            continue

        is_plant = bool(classification.get("is_plant"))
        plant_group = classification.get("plant_group")

        valid_plant_groups = [
            'Vegetables', 'Herbs', 'Fruit Trees', 'Flowering Shrubs', 'Perennial Flowers',
            'Annual Flowers', 'Ornamental Trees', 'Houseplants', 'Succulents', 'Bulbs', 'Native Plants'
        ]

        if not is_plant:
            # For non-plant, expect plant_group to be None/null
            if plant_group is not None:
                logger.warning(f"Attempt {attempt}: Non-plant must have plant_group=null. Got: {classification}. Retrying...")
                continue
            logger.info(f"Input '{plant_name}' determined to be non-plant.")
            return {"is_plant": False}

        # is_plant is True: validate group
        if plant_group not in valid_plant_groups:
            logger.warning(f"Attempt {attempt}: Invalid plant_group '{plant_group}'. Retrying...")
            continue

        logger.info(f"Plant '{plant_name}' classified as: {classification}")
        return {"is_plant": True, "plant_group": plant_group}

    logger.error(f"Could not classify plant group for '{plant_name}' after retries")
    return None

def get_plant_group_and_prompt(plant_name: str) -> Optional[Dict[str, str]]:
    """
    Classify a plant and return both the plant group and the appropriate prompt function.
    
    Returns:
        Dict with 'plant_group' and 'prompt_function' keys, or None if classification fails
    """
    # Step 1: Classify plant group
    plant_classification = classify_plant_group(plant_name)
    
    if plant_classification is None:
        logger.error(f"Could not classify plant group for '{plant_name}'")
        return None

    # If not a plant, bubble up this information
    if not plant_classification.get("is_plant", True):
        return {"is_plant": False}

    plant_group = plant_classification["plant_group"]
    
    # Step 2: Map group to prompt function
    prompt_function = CATEGORY_TO_PROMPT.get(plant_group)
    if not prompt_function:
        logger.error(f"No prompt function mapped for plant group: {plant_group}")
        return None
    
    logger.info(f"Plant '{plant_name}' classified as {plant_group} using {prompt_function} prompt")
    
    return {
        "is_plant": True,
        "plant_group": plant_group,
        "prompt_function": prompt_function
    }