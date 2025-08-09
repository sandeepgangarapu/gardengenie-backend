import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env for local dev
load_dotenv()

# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- OpenRouter Configuration ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
LLM_MODEL = "google/gemini-2.5-flash"
LLM_TIMEOUT_SECONDS = int(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))

# --- Unsplash Configuration ---
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
UNSPLASH_API_URL = "https://api.unsplash.com/search/photos"
UNSPLASH_TIMEOUT_SECONDS = int(os.getenv("UNSPLASH_TIMEOUT_SECONDS", "7"))
UNSPLASH_MAX_RETRIES = int(os.getenv("UNSPLASH_MAX_RETRIES", "3"))

# --- CORS Configuration ---
APP_ENV = os.getenv("APP_ENV", "development").lower()

if APP_ENV == "production":
    CORS_ORIGINS = [
        "https://gardengenie.lovable.app",
    ]
else:
    CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]

# --- App Configuration ---
APP_TITLE = "Plant Care API"
APP_DESCRIPTION = ("Smart plant care instructions with automatic plant care category classification and AI-powered plant identification from images. "
                  "Houseplants get focused care guidance (no seed starting), while outdoor plants receive complete zone-specific instructions including seed starting and planting. "
                  "Features include: plant identification from uploaded photos, personalized care instructions, and USDA zone-specific guidance. "
                  "Perfect for apartment dwellers and gardeners.")
APP_VERSION = "1.7.0"

# --- Validation ---
def validate_config():
    """Validate that required configuration is present."""
    missing_configs = []
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        missing_configs.append("Supabase URL or Key")
        logger.error("Supabase URL or Key not found in environment variables. Database operations will fail.")
    
    if not OPENROUTER_API_KEY:
        missing_configs.append("OpenRouter API Key")
        logger.warning("OPENROUTER_API_KEY not found in environment variables.")
    
    if not UNSPLASH_ACCESS_KEY:
        missing_configs.append("Unsplash Access Key")
        logger.warning("UNSPLASH_ACCESS_KEY not found in environment variables. Image fetching will be skipped.")
    
    return missing_configs

# Run validation on import
missing_configs = validate_config() 