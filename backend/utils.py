# Shared Utilities for DeepTrace

from openai import OpenAI
from config.settings import settings

# initializes an OpenAI-compatible client pointed at Nebius Token Factory.
# loads credentials and base URL from config/settings.py.
def get_nebius_client() -> OpenAI:
    return OpenAI(
        base_url=settings.NEBIUS_BASE_URL,
        api_key=settings.NEBIUS_API_KEY or "dummy_key_for_testing"
    )


# strips markdown code fences (```json) from LLM output if present.
def clean_json_string(raw_str: str) -> str:
    cleaned = raw_str.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()