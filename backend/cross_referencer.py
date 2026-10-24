""" Stage 3: Deep Logical Cross-Referencing
Uses NVIDIA Nemotron 3 Ultra (via Nebius Token Factory) to analyze live
web evidence from Tavily, detect contradictions, categorize misinformation type,
and synthesize a grounded factual verdict.
"""

import json             # Ultra returns raw JSON - need to convert to Python dict
import re               # regex fallback for extracting JSON from noisy LLM output
from pathlib import Path    # NEW: reads prompt text from external file instead of hardcoding in Python
from config.settings import settings
from backend.utils import get_nebius_client, clean_json_string      # shared utilities


# system prompt for Nemotron 3 Ultra - instructs the model to act as an investigative cross-examiner
# loaded from external text file so it can be edited without touching Python code
CROSS_REFERENCE_SYSTEM_PROMPT = (Path(__file__).parent / "prompts" / "cross_reference.txt").read_text(encoding="utf-8")


# Attempts multiple strategies to extract valid JSON from LLM output.
# LLMs sometimes wrap JSON in markdown fences, add preamble text, or truncate mid-object.
def _robust_json_parse(raw_output: str) -> dict:
    # Strategy 1: Use the shared clean_json_string utility (handles most common cases)
    try:
        cleaned = clean_json_string(raw_output)
        return json.loads(cleaned)
    except (json.JSONDecodeError, Exception):
        pass

    # Strategy 2: Extract JSON block from markdown code fences (```json ... ```)
    fence_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', raw_output, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find the outermost { ... } block in the raw text
    brace_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass

    # Strategy 4: Repair truncated JSON by closing at the last complete object.
    # When the model hits max_tokens mid-JSON, the output starts with { but has no
    # closing }. We find the last } (end of the last complete stance entry), truncate
    # there, and append ]} to close the source_stances array and root object.
    stripped = raw_output.strip()
    if stripped.startswith('{'):            # no need to repair if not in json - prose/garbage
        last_brace = stripped.rfind('}')
        if last_brace > 50:       # only if we have a substantial amount of valid JSON
            repaired = stripped[:last_brace + 1] + ']}'     # ] for source_stances      } root object
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass            # if failed then fall through to the final error

    # All strategies exhausted — raise so the caller's except block handles it
    raise json.JSONDecodeError("Could not extract valid JSON from LLM response", raw_output, 0)


# raw sources -> numbered list - used in cross_reference_claim()
def _format_evidence_dossier(sources: list) -> str:
    if not sources:
        return "No external sources were retrieved."

    dossier_lines = []
    for s in sources:
        snippet = s.get("snippet", "No snippet available.")
        # NOTE: retriever already truncates snippets to 200 words, so no redundant truncation here

        dossier_lines.append(
            f"--- SOURCE #{s.get('source_id', '?')} ---\n"
            f"Title: {s.get('title', 'Unknown')}\n"
            f"Domain: {s.get('domain', 'Unknown')} ({s.get('tier_label', 'Tier 4')})\n"
            f"URL: {s.get('url', '')}\n"
            f"Snippet: {snippet}\n"
        )
    return "\n".join(dossier_lines)     # LLMs process structured text more accurately than raw JSON format


# builds the full user prompt by combining the claim text with formatted source evidence
def _build_cross_reference_prompt(claim_text: str, sources: list) -> str:
    evidence_text = _format_evidence_dossier(sources)       # formats sources into numbered list for LLM prompt (for Nemotron 3 Ultra)

    return f"""CLAIM TO VERIFY:
\"\"\"{claim_text}\"\"\"

RETRIEVED LIVE EVIDENCE DOSSIER ({len(sources)} sources examined):
{evidence_text}

Perform deep logical cross-referencing and return the required JSON evaluation."""


# sends the prompt to Nemotron 3 Ultra and returns the raw text response
def _call_ultra(user_content: str) -> str:
    client = get_nebius_client()

    # Execute high-reasoning cloud inference on Nebius Token Factory
    response = client.chat.completions.create(
        model=settings.NVIDIA_ULTRA_MODEL,
        temperature=settings.DEFAULT_TEMPERATURE,
        max_tokens=settings.MAX_TOKENS_SYNTHESIS,
        messages=[
            {"role": "system", "content": CROSS_REFERENCE_SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]
    )

    return response.choices[0].message.content.strip()


# core cross-referencing pipeline
# claim: dict per claim from stage 1 (claim_extractor)
# sources_data: dict from stage 2 (source_retriever)
# returns: dict with verdict, confidence, reasoning, and per-source stances
def cross_reference_claim(claim: dict, sources_data: dict) -> dict:

    claim_text = claim.get("claim_text", "")
    sources = sources_data.get("sources", [])

    if not claim_text.strip():
        return {
            "success": False,
            "error": "No claim text provided for cross-referencing.",
            "verdict": "UNVERIFIABLE",      # default fallback - prevents crashing
            "confidence_score": 0
        }

    # Check if a live Nebius API key is configured
    key_status = settings.validate_keys()
    if not key_status["nebius"]:
        # Seamless fallback simulation while Nebius account review is pending
        return _simulate_cross_reference_fallback(claim_text, sources)

    try:
        user_content = _build_cross_reference_prompt(claim_text, sources)
        raw_output = _call_ultra(user_content)
        parsed_data = _robust_json_parse(raw_output)        # multi-strategy JSON extraction replaces single json.loads call

        parsed_data["success"] = True
        parsed_data["is_mock"] = False
        parsed_data["claim_text"] = claim_text      # for UI display
        return parsed_data

    except Exception as e:
        return {
            "success": False,
            "error": f"Nemotron 3 Ultra cross-referencing error: {str(e)}",
            "verdict": "UNVERIFIABLE",
            "confidence_score": 0,
            "claim_text": claim_text,
            "reasoning_summary": "Analysis could not be completed. The AI model's response was truncated due to the complexity or length of this claim. Try submitting a shorter, more specific claim for better results.",
            "misinfo_type": "Unclassified"
        }


# generates fake but realistic verdict data when running without a live Nebius key
def _simulate_cross_reference_fallback(claim_text: str, sources: list) -> dict:

    # Context-aware mock: if 'alien' or 'conspiracy' in text, simulate a debunked verdict
    lower_claim = claim_text.lower()
    is_debunked = any(w in lower_claim for w in ["alien", "spacecraft", "antarctic", "secret", "leak", "coverup"])

    if is_debunked:
        return {
            "success": True,
            "is_mock": True,
            "claim_text": claim_text,
            "verdict": "DEBUNKED",
            "confidence_score": 94,
            "misinfo_type": "Fabricated Data",
            "reasoning_summary": (
                "No credible news agency (AP, Reuters, BBC, NASA.gov) has reported any discovery "
                "of alien spacecraft beneath Antarctic ice. The claim originates from "
                "unverified tabloid and satirical blogs. NASA's official mission archives contain "
                "zero matching records for the cited event."
            ),
            "key_contradiction": "NASA official portal shows no active extraterrestrial recovery missions vs. tabloid blog claiming confirmed whistleblower leaks.",
            "source_stances": [
                {
                    "source_id": 1,
                    "domain": "nasa.gov",
                    "stance": "CONTRADICTS",
                    "one_line_summary": "Official archives confirm no records of alien discoveries in Antarctica."
                },
                {
                    "source_id": 2,
                    "domain": "reuters.com",
                    "stance": "CONTRADICTS",
                    "one_line_summary": "Wire service fact-check found zero corroborating evidence from international agencies."
                },
                {
                    "source_id": 3,
                    "domain": "dailygalaxy.com",
                    "stance": "ORIGIN_OF_CLAIM",
                    "one_line_summary": "Identified as the primary unverified tabloid origin of the viral post."
                }
            ]
        }

    # Default verified mock for standard factual queries
    return {
        "success": True,
        "is_mock": True,
        "claim_text": claim_text,
        "verdict": "VERIFIED",
        "confidence_score": 88,
        "misinfo_type": "Legitimate",
        "reasoning_summary": (
            "The claim is supported by high-consensus reporting across multiple Tier 1 and Tier 2 "
            "independent sources. Official press releases and international wire services corroborate "
            "the core factual assertions with matching dates and details."
        ),
        "key_contradiction": None,
        "source_stances": [
            {
                "source_id": 1,
                "domain": "nasa.gov",
                "stance": "SUPPORTS",
                "one_line_summary": "Official press release confirms mission milestones."
            },
            {
                "source_id": 2,
                "domain": "reuters.com",
                "stance": "SUPPORTS",
                "one_line_summary": "Wire report corroborates timeline and official statements."
            }
        ]
    }