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

    # Structured output schema for classification
    classification_schema = {
        "type": "json_schema",
        "json_schema": {
            "name": "PlantGroupClassification",
            "strict": True,
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "plant_group": {
                        "type": "string",
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
                        ],
                    }
                },
                "required": ["plant_group"],
            },
        },
    }

    payload = create_payload(prompt, max_tokens=100, temperature=0.1, response_format=classification_schema)
    result = make_llm_request(payload)
    
    if not result:
        return None

    try:
        classification = json.loads(result["content"])
        # Validate required fields
        required_fields = ['plant_group']
        if not all(k in classification for k in required_fields):
            logger.error(f"LLM JSON missing required fields for plant group classification: {classification}")
            return None
        
        # Validate values
        valid_plant_groups = ['Vegetables', 'Herbs', 'Fruit Trees', 'Flowering Shrubs', 'Perennial Flowers', 'Annual Flowers', 'Ornamental Trees', 'Houseplants', 'Succulents', 'Bulbs', 'Native Plants']
        
        if classification['plant_group'] not in valid_plant_groups:
            logger.error(f"Invalid classification values: {classification}")
            return None
        
        logger.info(f"Plant '{plant_name}' classified as: {classification}")
        return classification
        
    except json.JSONDecodeError as json_e:
        logger.error(f"Failed to decode JSON response from LLM for plant care classification: {json_e}")
        logger.error(f"LLM Raw Content: {result['content']}")
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

    plant_group = plant_classification["plant_group"]
    
    # Step 2: Map group to prompt function
    prompt_function = CATEGORY_TO_PROMPT.get(plant_group)
    if not prompt_function:
        logger.error(f"No prompt function mapped for plant group: {plant_group}")
        return None
    
    logger.info(f"Plant '{plant_name}' classified as {plant_group} using {prompt_function} prompt")
    
    return {
        "plant_group": plant_group,
        "prompt_function": prompt_function
    } 