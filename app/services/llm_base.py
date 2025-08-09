from openai import OpenAI
import json
import logging
import re
from typing import Optional, Dict, Any

from ..config import OPENROUTER_API_KEY, LLM_MODEL

logger = logging.getLogger(__name__)

def extract_json_from_response(content: str) -> str:
    """Extract JSON from markdown code blocks or raw text."""
    # Remove markdown code blocks if present
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, content, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    else:
        return content.strip()

def make_llm_request(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Helper function to make requests to OpenRouter API using OpenAI client."""
    if not OPENROUTER_API_KEY:
        logger.error("OpenRouter API Key is missing.")
        return None

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )

    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost",
                "X-Title": "Plant Care API",
            },
            model=payload.get("model", LLM_MODEL),
            messages=payload.get("messages", []),
            max_tokens=payload.get("max_tokens", 3000),
            temperature=payload.get("temperature", 0.2)
        )
        
        raw_content = completion.choices[0].message.content.strip()
        # Extract JSON from markdown blocks if present
        clean_content = extract_json_from_response(raw_content)
        if not clean_content:
            logger.warning("Received empty content from LLM.")
            return None

        # Include both the clean JSON content and the full raw response object
        return {"content": clean_content, "raw_response": completion.model_dump(), "raw_text": raw_content}
    
    except Exception as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        return None

def validate_and_parse_response(result: Dict[str, Any], required_keys: list, plant_type: str, plant_name: str) -> Optional[Dict[str, Any]]:
    """Common validation logic for LLM responses."""
    if not result:
        return None

    # Check if JSON response appears to be truncated
    if not result["content"].rstrip().endswith('}'):
        logger.warning(f"LLM response appears to be truncated for {plant_type}. Content length: {len(result['content'])}")
        return None

    try:
        care_info = json.loads(result["content"])
        if not all(k in care_info for k in required_keys):
            logger.error(f"LLM JSON missing essential keys for {plant_type}: {care_info}")
            return None
        # Attach raw payload for downstream persistence
        try:
            care_info["__raw_llm_response"] = result.get("raw_response")
            care_info["__raw_llm_text"] = result.get("raw_text") or result.get("content")
        except Exception:
            # Non-fatal; continue without raw attachment
            pass
        logger.info(f"LLM ({LLM_MODEL}) returned valid JSON for {plant_type} '{plant_name}'")
        return care_info
    except json.JSONDecodeError as json_e:
        logger.error(f"Failed to decode JSON response from LLM for {plant_type}: {json_e}")
        logger.error(f"LLM Raw Content: {result['content']}")
        return None

def create_payload(prompt: str, max_tokens: int = 3000, temperature: float = 0.2) -> Dict[str, Any]:
    """Create standard payload for LLM requests."""
    return {
        "model": LLM_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }