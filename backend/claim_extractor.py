# Uses LLM API to decompose raw, unstructured user text into structured, verifiable atomic claims.

import json                 # LLM API outputs in raw JSON format, which we parse into Python dictionaries.
from pathlib import Path    # reads prompt text from external file instead of hardcoding in Python
from config.settings import settings
from backend.utils import clean_json_string, get_llm_client  # shared utilities

# System prompt for LLM - loaded from external text file so it can be edited without touching Python code
EXTRACTION_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "extraction.txt").read_text(encoding="utf-8")

# Builds the user-facing instruction based on whether batch mode is on or off
def _build_user_prompt(raw_text: str, batch_mode: bool) -> str:
    mode_instruction = (
        "Extract all major distinct factual claims from this full article."
        if batch_mode else
        "Extract the primary core factual claim from this text."
    )
    return f"{mode_instruction}\n\nINPUT TEXT:\n\"\"\"\n{raw_text.strip()}\n\"\"\""


# Sends the prompt to the fast model and returns the raw text response
def _call_fast_model(user_prompt: str) -> str:
    client = get_llm_client()

    response = client.chat.completions.create(
        model=settings.FAST_MODEL,
        temperature=settings.DEFAULT_TEMPERATURE,
        max_tokens=settings.MAX_TOKENS_EXTRACTION,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    return response.choices[0].message.content.strip()


# Parses the raw LLM output string into a Python dictionary
def _parse_extraction_response(raw_output: str) -> dict:
    cleaned_json = clean_json_string(raw_output)  # strip accidental markdown code fences

    parsed_data = json.loads(cleaned_json)
    parsed_data["success"] = True
    parsed_data["is_mock"] = False
    return parsed_data


# Core extraction pipeline
def extract_claims(raw_text: str, batch_mode: bool = False) -> dict:
    # raw_text: user's pasted claim or article
    # batch_mode: extract multiple claims (True) or just the primary claim (False)
    # returns: dictionary with parsed claims, search queries, and status

    if not raw_text or not raw_text.strip():
        return {
            "success": False,
            "error": "Empty input text provided.",
            "total_claims": 0,
            "claims": []
        }

    key_status = settings.validate_keys()
    if not key_status["llm"]:  # simulation fallback when LLM API key is missing or invalid
        return _simulate_extraction_fallback(raw_text, batch_mode)

    try:
        user_prompt = _build_user_prompt(raw_text, batch_mode)
        raw_output = _call_fast_model(user_prompt)
        return _parse_extraction_response(raw_output)

    except Exception as e:
        return {
            "success": False,
            "error": f"LLM inference error: {str(e)}",
            "total_claims": 0,
            "claims": []
        }


# Offline simulator: generates realistic mock extracted claims when LLM API key is not available
def _simulate_extraction_fallback(raw_text: str, batch_mode: bool) -> dict:
    clean_snippet = raw_text.strip()[:100]
    if batch_mode:
        return {
            "success": True,
            "is_mock": True,
            "total_claims": 2,
            "claims": [
                {
                    "claim_id": 1,
                    "claim_text": f"{clean_snippet} (Primary claim)",
                    "search_query": f"{clean_snippet} official records fact check",
                    "category": "General News"
                },
                {
                    "claim_id": 2,
                    "claim_text": "Government agencies were involved in coordinating public statements.",
                    "search_query": "Government official statements timeline",
                    "category": "Politics"
                }
            ]
        }

    return {
        "success": True,
        "is_mock": True,
        "total_claims": 1,
        "claims": [
            {
                "claim_id": 1,
                "claim_text": f"{clean_snippet}...",
                "search_query": f"{clean_snippet} fact check evidence",
                "category": "General News"
            }
        ]
    }