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


class Settings:     #Central configuration store for DeepTrace verification pipeline

    # Runtime environment
    APP_ENV: str = os.getenv("APP_ENV", "development").strip()      # fallback if not found
    DEBUG: bool = APP_ENV == "development"

    # Nebius Token Factory Inference API
    NEBIUS_API_KEY: str = os.getenv("NEBIUS_API_KEY", "").strip()     # warning instead of crashing on missing key 
    NEBIUS_BASE_URL: str = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1").strip()

    # NVIDIA Nemotron Models 
    NVIDIA_NANO_MODEL: str = os.getenv("NVIDIA_NANO_MODEL", "nvidia/nemotron-nano").strip()
    NVIDIA_ULTRA_MODEL: str = os.getenv("NVIDIA_ULTRA_MODEL", "nvidia/nemotron-3-ultra").strip()        # for heavy reasoning tasks like cross-referencing and synthesis

    # Tavily AI Search Engine
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "").strip()   # gives Nemotron real-time grounded search results

    # Pipeline Settings & Thresholds
    MAX_SEARCH_RESULTS: int = int(os.getenv("MAX_SEARCH_RESULTS", "8"))     # loads max no. of web pages Tavily should search for each claim
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))  # loads confidence percentage below which a claim is considered unverified/disputed

    # LLM Operational Hyperparameters
    DEFAULT_TEMPERATURE: float = 0.2    # Strict factual reasoning, minimal hallucination, no invention
    MAX_TOKENS_EXTRACTION: int = 1024    # Nano token limit for claim extraction
    MAX_TOKENS_SYNTHESIS: int = 1500    # Ultra token limit for cross-referencing analysis - more because of the need to synthesize multiple sources and provide a detailed explanation

    @classmethod
    def validate_keys(cls) -> dict[str, bool]:
        """Validates whether required API credentials are provided."""
        return {
            "nebius": bool(cls.NEBIUS_API_KEY and not cls.NEBIUS_API_KEY.startswith("your_")),
            "tavily": bool(cls.TAVILY_API_KEY and not cls.TAVILY_API_KEY.startswith("your_")),
        }


# Singleton configuration object ready for import
settings = Settings()