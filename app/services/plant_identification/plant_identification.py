import base64
import json
import logging
from typing import Optional, Dict, Any

from ..llm_base import make_llm_request, create_payload
from .plant_identification_prompt import PLANT_IDENTIFICATION_PROMPT

logger = logging.getLogger(__name__)

def identify_plant_from_uploaded_image(image_data: bytes) -> Optional[Dict[str, Any]]:
    """
    Identify a plant from uploaded image data.
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Dictionary containing identification results, or None if identification fails
    """
    if not image_data:
        logger.error("No image data provided for plant identification")
        return None
    
    if len(image_data) == 0:
        logger.error("Empty image data provided for plant identification")
        return None
    
    # Analyze the image using the LLM service
    identification_result = identify_plant_from_image(image_data)
    
    if identification_result is None:
        logger.error("Failed to identify plant from image")
        return None
    
    logger.info(f"Plant identification completed: is_plant={identification_result.get('is_plant')}, name={identification_result.get('common_name')}")
    return identification_result

def identify_plant_from_image(image_data: bytes) -> Optional[Dict[str, Any]]:
    """Analyzes an uploaded image to determine if it contains a plant and identify it."""
    # Convert image bytes to base64
    try:
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding image to base64: {e}")
        return None

    prompt = PLANT_IDENTIFICATION_PROMPT

    payload = {
        "model": create_payload("", max_tokens=300, temperature=0.2)["model"],
        "messages": [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300,
        "temperature": 0.2
    }

    result = make_llm_request(payload)
    if not result:
        return None

    try:
        identification = json.loads(result["content"])
        # Validate required fields
        if not all(k in identification for k in ['is_plant', 'message']):
            logger.error(f"LLM JSON missing essential keys for plant identification: {identification}")
            return None
        
        logger.info(f"Plant identification completed: is_plant={identification.get('is_plant')}, name={identification.get('common_name')}")
        return identification
    except json.JSONDecodeError as json_e:
        logger.error(f"Failed to decode JSON response from LLM for plant identification: {json_e}")
        logger.error(f"LLM Raw Content: {result['content']}")
        return None

def validate_image_data(image_data: bytes, max_size_mb: int = 10) -> Dict[str, Any]:
    """
    Validate uploaded image data.
    
    Args:
        image_data: Raw image bytes
        max_size_mb: Maximum allowed file size in megabytes
        
    Returns:
        Dict with 'valid' boolean and optional 'error' message
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if not image_data:
        return {"valid": False, "error": "No image data provided"}
    
    if len(image_data) == 0:
        return {"valid": False, "error": "Uploaded file is empty"}
    
    if len(image_data) > max_size_bytes:
        return {"valid": False, "error": f"Image file too large. Maximum size is {max_size_mb}MB"}
    
    return {"valid": True}