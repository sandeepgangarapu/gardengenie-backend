import requests
import logging
from typing import Optional, Dict

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ..config import UNSPLASH_ACCESS_KEY, UNSPLASH_API_URL, UNSPLASH_TIMEOUT_SECONDS, UNSPLASH_MAX_RETRIES

logger = logging.getLogger(__name__)

@retry(
    reraise=True,
    stop=stop_after_attempt(UNSPLASH_MAX_RETRIES),
    wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
)
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
        "per_page": 1,  # We only need the first result
        "orientation": "landscape"  # Optional: prefer landscape images
    }

    try:
        response = requests.get(UNSPLASH_API_URL, headers=headers, params=params, timeout=UNSPLASH_TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()

        results = data.get("results")
        if not results:
            logger.info(f"No Unsplash image found for query: '{plant_name}'")
            return None

        first_image = results[0]
        image_url = first_image.get("urls", {}).get("regular")  # Get a reasonably sized image
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