import logging
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    app_title: str = "Plant Care API"
    app_description: str = (
        "Smart plant care instructions with automatic plant care category classification and AI-powered plant identification from images. "
        "Houseplants get focused care guidance (no seed starting), while outdoor plants receive complete zone-specific instructions including seed starting and planting. "
        "Features include: plant identification from uploaded photos, personalized care instructions, and USDA zone-specific guidance. "
        "Perfect for apartment dwellers and gardeners."
    )
    app_version: str = "1.7.0"

    # Upload limits
    max_upload_mb: int = 10

    # Supabase
    supabase_url: str | None = None
    supabase_key: str | None = None

    # OpenRouter / LLM
    openrouter_api_key: str | None = None
    llm_model: str = "openai/gpt-5-mini"
    llm_timeout_seconds: int = 30
    llm_max_retries: int = 3
    llm_use_structured_outputs: bool = True
    # Vision
    vision_llm_model: str = "google/gemini-2.5-flash"

    # Unsplash
    unsplash_access_key: str | None = None
    unsplash_api_url: str = "https://api.unsplash.com/search/photos"
    unsplash_timeout_seconds: int = 7
    unsplash_max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        """
        Return CORS origins based on environment.
        In production, prioritize production URLs but also allow localhost for testing.
        In development, allow both localhost and production URLs for flexibility.
        """
        env = (self.app_env or "development").lower()
        
        # Base origins that are always allowed
        base_origins = [
            "https://gardengenie.lovable.app",  # Production frontend
            "http://localhost",                 # Local development
            "http://localhost:8000",           # Local backend
            "http://localhost:3000",           # Local frontend (common React port)
            "http://127.0.0.1:8000",          # Alternative localhost
            "http://127.0.0.1:3000",          # Alternative localhost
        ]
        
        if env == "production":
            logger.info("CORS configured for production environment")
            return base_origins
        else:
            logger.info("CORS configured for development environment")
            return base_origins


def _validate_on_startup(settings: Settings) -> None:
    fatal_errors: List[str] = []

    if not settings.supabase_url or not settings.supabase_key:
        fatal_errors.append("Supabase URL or Key is missing")
        logger.error("Supabase URL or Key not found in environment variables. Database operations will fail.")

    if not settings.openrouter_api_key:
        logger.warning("OPENROUTER_API_KEY not found in environment variables.")

    if not settings.unsplash_access_key:
        logger.warning("UNSPLASH_ACCESS_KEY not found in environment variables. Image fetching will be skipped.")

    if settings.app_env.lower() == "production" and fatal_errors:
        # In production, fail fast on critical missing config
        raise RuntimeError("; ".join(fatal_errors))


# Instantiate settings once and expose backwards-compatible constants
settings = Settings()
_validate_on_startup(settings)

# Back-compat module-level constants for existing imports
APP_ENV = settings.app_env
APP_TITLE = settings.app_title
APP_DESCRIPTION = settings.app_description
APP_VERSION = settings.app_version
CORS_ORIGINS = settings.cors_origins
MAX_UPLOAD_MB = settings.max_upload_mb

SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_key

OPENROUTER_API_KEY = settings.openrouter_api_key
LLM_MODEL = settings.llm_model
LLM_TIMEOUT_SECONDS = settings.llm_timeout_seconds
LLM_MAX_RETRIES = settings.llm_max_retries
USE_STRUCTURED_OUTPUTS = settings.llm_use_structured_outputs
VISION_LLM_MODEL = settings.vision_llm_model

UNSPLASH_ACCESS_KEY = settings.unsplash_access_key
UNSPLASH_API_URL = settings.unsplash_api_url
UNSPLASH_TIMEOUT_SECONDS = settings.unsplash_timeout_seconds
UNSPLASH_MAX_RETRIES = settings.unsplash_max_retries