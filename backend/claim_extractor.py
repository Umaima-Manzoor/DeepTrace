# uses NVIDIA Nemotron Nano (via Nebius Token Factory) to decompose raw, unstructured user text into structured, verifiable atomic claims.

import json                 # Nemotron outputs in raw JSON format, which we parse into Python dictionaries.
from pathlib import Path    # reads prompt text from external file instead of hardcoding in Python
from config.settings import settings
from backend.utils import clean_json_string, get_llm_client  # shared utilities

# system prompt for Nemotron Nano — loaded from external text file so it can be edited without touching Python code
EXTRACTION_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "extraction.txt").read_text(encoding="utf-8")


# builds the user-facing instruction based on whether batch mode is on or off
def _build_user_prompt(raw_text: str, batch_mode: bool) -> str:
    # tailor instruction based on batch toggle
    mode_instruction = (
        "Extract all major distinct factual claims from this full article."
        if batch_mode else
        "Extract the primary core factual claim from this text."
    )
    return f"{mode_instruction}\n\nINPUT TEXT:\n\"\"\"\n{raw_text.strip()}\n\"\"\""      # text to analyze, not instructions


# sends the prompt to the fast model and returns the raw text response
def _call_fast_model(user_prompt: str) -> str:
    client = get_llm_client()

    # Execute cloud inference via configured LLM provider
    response = client.chat.completions.create(
        model=settings.FAST_MODEL,
        temperature=settings.DEFAULT_TEMPERATURE,
        max_tokens=settings.MAX_TOKENS_EXTRACTION,
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )

    # Extract raw text output from the model
    return response.choices[0].message.content.strip()


# parses the raw LLM output string into a Python dictionary
def _parse_extraction_response(raw_output: str) -> dict:
    # Sanitize any accidental markdown code fences (```json ... ```)
    cleaned_json = clean_json_string(raw_output)

    # Parse string into Python dictionary for looping
    parsed_data = json.loads(cleaned_json)
    parsed_data["success"] = True
    parsed_data["is_mock"] = False
    return parsed_data


# core extraction pipeline
def extract_claims(raw_text: str, batch_mode: bool = False) -> dict:
    # raw_text: user's pasted claim or article
    # batch_mode: whether to extract multiple claims from a full article (True) or just the primary claim (False)
    # returns: dictionary with parsed claims, search queries, and status

    if not raw_text or not raw_text.strip():
        return {
            "success": False,
            "error": "Empty input text provided.",
            "total_claims": 0,
            "claims": []
        }

    # Check if a live Nebius API key is configured
    key_status = settings.validate_keys()
    if not key_status["nebius"]:        # simulation in case of missing or invalid Nebius API key
        return _simulate_extraction_fallback(raw_text, batch_mode)

    try:
        user_prompt = _build_user_prompt(raw_text, batch_mode)
        raw_output = _call_fast_model(user_prompt)
        return _parse_extraction_response(raw_output)

    except Exception as e:
        # Graceful error handling: return error dictionary rather than crashing
        return {
            "success": False,
            "error": f"LLM inference error: {str(e)}",
            "total_claims": 0,
            "claims": []
        }


# offline simulator: Generates realistic mock extracted claims when working offline or while Nebius account review is pending.  
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