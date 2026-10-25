"""
config/settings.py — DeepTrace Configuration & Settings Manager
Reads parameters from .env and exposes a clean singleton configuration object.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent   # current file's grandparent folder (in this case, DeepTrace is the root folder so its path is returned: D:\DeepTrace)
ENV_FILE = ROOT_DIR / ".env"

# Load variables from .env into system environment since python can't read .env files natively
if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
else:
    load_dotenv()       # Load from system environment if .env file is not found (e.g., in production)


class Settings:     # Central configuration store for DeepTrace verification pipeline

    # Runtime environment
    APP_ENV: str = os.getenv("APP_ENV", "development").strip()      # fallback if not found
    DEBUG: bool = APP_ENV == "development"

    # LLM Inference API (any OpenAI-compatible provider: Nebius, Groq, OpenAI, etc.)
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "").strip()     # warning instead of crashing on missing key
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "https://api.tokenfactory.nebius.com/v1").strip()

    # LLM Models
    FAST_MODEL: str = os.getenv("FAST_MODEL", "nvidia/nemotron-nano").strip()        # lightweight model for claim extraction
    REASONING_MODEL: str = os.getenv("REASONING_MODEL", "nvidia/nemotron-3-ultra").strip()        # heavy reasoning model for cross-referencing and synthesis

    # Web Search API (Tavily, Serper, Brave, etc.)
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "").strip()   # gives the LLM real-time grounded search results

    # Pipeline Settings & Thresholds
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "8"))     # loads max no. of web pages the search API should return for each claim
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))  # loads confidence percentage below which a claim is considered unverified/disputed

    # LLM Operational Hyperparameters
    DEFAULT_TEMPERATURE: float = 0.2    # Strict factual reasoning, minimal hallucination, no invention
    MAX_TOKENS_EXTRACTION: int = 1024    # Fast model token limit for claim extraction
    MAX_TOKENS_SYNTHESIS: int = 4000    # Reasoning model token limit for cross-referencing analysis - more because of the need to synthesize multiple sources and provide a detailed explanation

    @classmethod
    def validate_keys(cls) -> dict[str, bool]:
        """Validates whether required API credentials are provided."""
        return {
            "llm": bool(cls.LLM_API_KEY and not cls.LLM_API_KEY.startswith("your_")),
            "search": bool(cls.SEARCH_API_KEY and not cls.SEARCH_API_KEY.startswith("your_")),
        }


# Singleton configuration object ready for import
settings = Settings()