# uses NVIDIA Nemotron Nano (via Nebius Token Factory) to decompose raw, unstructured user text into structured, verifiable atomic claims.

import json                 # Nemotron outputs in raw JSON format, which we parse into Python dictionaries.
from config.settings import settings
from backend.utils import clean_json_string, get_nebius_client  # shared utilities

# system prompt
EXTRACTION_SYSTEM_PROMPT = """You are DeepTrace's high-precision factual claim extraction engine.
Your task is to analyze user input (rumors, headlines, article excerpts) and decompose it into distinct, verifiable atomic claims.

RULES:
1. Extract 1 to 5 atomic factual claims. An atomic claim is a single proposition that can be proven TRUE or FALSE by evidence.
2. Strip away emotional language, opinions, speculation, and sensationalism.
3. For each claim, generate an optimized, concise web search query for Tavily to find authoritative reporting.
4. Categorize each claim (e.g., Science/Space, Politics, Health, Technology, World News, Satire).
5. Output MUST be valid, raw JSON only. Do NOT include markdown code fences (like ```json), commentary, or extra text.

JSON STRUCTURE:
{
  "total_claims": 1,
  "claims": [
    {
      "claim_id": 1,
      "claim_text": "Exact atomic factual assertion.",
      "search_query": "Optimized web search query",
      "category": "Category Name"
    }
  ]
}
"""

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
        client = get_nebius_client()

        # tailor instruction based on batch toggle
        mode_instruction = (
            "Extract all major distinct factual claims from this full article."
            if batch_mode else
            "Extract the primary core factual claim from this text."
        )

        user_prompt = f"{mode_instruction}\n\nINPUT TEXT:\n\"\"\"\n{raw_text.strip()}\n\"\"\""      # text to analyze, not instructions

        # Execute cloud inference on Nebius Token Factory
        response = client.chat.completions.create(
            model=settings.NVIDIA_NANO_MODEL,
            temperature=settings.DEFAULT_TEMPERATURE,
            max_tokens=settings.MAX_TOKENS_EXTRACTION,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        )

        # Extract raw text output from the model
        raw_output = response.choices[0].message.content.strip()

        # Sanitize any accidental markdown code fences (```json ... ```)
        cleaned_json = clean_json_string(raw_output)

        # Parse string into Python dictionary for looping
        parsed_data = json.loads(cleaned_json)
        parsed_data["success"] = True
        parsed_data["is_mock"] = False
        return parsed_data

    except Exception as e:
        # Graceful error handling: return error dictionary rather than crashing
        return {
            "success": False,
            "error": f"Nemotron Nano inference error: {str(e)}",
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