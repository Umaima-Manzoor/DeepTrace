"""
config/settings.py — DeepTrace Configuration & Settings Manager
Reads parameters from .env and exposes a clean singleton configuration object.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent  # project root directory
ENV_FILE = ROOT_DIR / ".env"

# Load variables from .env into system environment since Python can't read .env files natively
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()  # load from system environment if .env file is not found (e.g., in production)


class Settings:  # central configuration store for the verification pipeline

    # Runtime environment
    APP_ENV: str = os.getenv("APP_ENV", "development").strip()

    # LLM Inference API (any OpenAI-compatible provider)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "").strip()  # empty string triggers warning instead of crashing
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.tokenfactory.nebius.com/v1").strip()

    # LLM Models
    FAST_MODEL: str = os.getenv("FAST_MODEL", "nvidia/nemotron-nano").strip()  # lightweight model for claim extraction
    REASONING_MODEL: str = os.getenv("REASONING_MODEL", "nvidia/nemotron-3-ultra").strip()  # heavy reasoning model for cross-referencing

    # Web Search API
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "").strip()  # provides real-time grounded search results

    # Pipeline Settings & Thresholds
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "8"))  # max web pages the search API returns per claim
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))  # below this, claim is considered unverified

    # LLM Operational Hyperparameters
    DEFAULT_TEMPERATURE: float = 0.2  # strict factual reasoning, minimal hallucination
    MAX_TOKENS_EXTRACTION: int = 1024  # fast model token limit for claim extraction
    MAX_TOKENS_SYNTHESIS: int = 4000  # reasoning model token limit — higher to synthesize multiple sources

    @classmethod
    def validate_keys(cls) -> dict[str, bool]:
        """Validates whether required API credentials are provided."""
        return {
            "llm": bool(cls.LLM_API_KEY and not cls.LLM_API_KEY.startswith("your_")),
            "search": bool(cls.SEARCH_API_KEY and not cls.SEARCH_API_KEY.startswith("your_")),
        }


# Singleton configuration object ready for import
settings = Settings()