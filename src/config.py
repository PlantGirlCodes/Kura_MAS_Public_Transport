"""Configuration settings for the Transport Multi-Agent System."""
import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

    # Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR = Path("logs")

    # Rate Limits
    MAX_REQUESTS_PER_MINUTE = 60
    MAX_ERRORS_BEFORE_FALLBACK = 3

    # LLM Settings
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "500"))

    @classmethod
    def validate_required_keys(cls) -> Dict[str, bool]:
        """Validate that required API keys are present."""
        required_keys = [
            "OPENAI_API_KEY",
            "GOOGLE_MAPS_API_KEY",
            "WEATHER_API_KEY"
        ]

        validation = {}
        for key in required_keys:
            value = getattr(cls, key)
            validation[key] = value is not None and value != ""

        return validation

    @classmethod
    def get_missing_keys(cls) -> list:
        """Get list of missing required API keys."""
        validation = cls.validate_required_keys()
        return [key for key, is_valid in validation.items() if not is_valid]