""" Stage 3: Deep Logical Cross-Referencing
Uses NVIDIA Nemotron 3 Ultra (via Nebius Token Factory) to analyze live
web evidence from Tavily, detect contradictions, categorize misinformation type,
and synthesize a grounded factual verdict.
"""

import json             # Ultra returns raw JSON - need to convert to Python dict
from config.settings import settings
from backend.utils import get_nebius_client, clean_json_string      # shared utilities


# system prompt for Nemotron 3 Ultra - instructs the model to act as an investigative cross-examiner
CROSS_REFERENCE_SYSTEM_PROMPT = """You are DeepTrace's master investigative fact-verification and logical cross-referencing engine.
Your task is to critically analyze an atomic factual claim against a pool of live retrieved web sources and determine the objective truth.

OPERATIONAL PRINCIPLES:
1. STANCE CLASSIFICATION: For every source provided, classify its stance toward the claim:
   - "SUPPORTS": Source explicitly verifies the claim with credible evidence.
   - "CONTRADICTS": Source directly refutes, debunks, or provides evidence proving the claim false.
   - "NEUTRAL": Source discusses the subject but provides no conclusive confirmation or denial.
   - "ORIGIN_OF_CLAIM": Source is the unverified tabloid/social post where the rumor originated.

2. DOMAIN WEIGHTING:
   - Prioritize Tier 1 (Official Govt/Academic) and Tier 2 (Wire Services: Reuters, AP).
   - A claim contradicted by Tier 1/2 sources MUST be classified as DEBUNKED.
   - If sources directly contradict each other with no Tier 1 resolution, classify as DISPUTED.

3. MISINFORMATION TAXONOMY:
   If the claim is not fully verified, categorize the deception type:
   - "Fabricated Data": Completely invented figures, events, or discoveries.
   - "False Attribution": Real quote/action falsely credited to a person or agency (e.g. NASA).
   - "Cherry-Picking": True data taken selectively to create a misleading conclusion.
   - "Out of Context": Genuine historical event or quote applied to the wrong situation.
   - "Satire / Parody": Satirical content mistaken for real news.
   - "Synthetic Media": Linguistic patterns suggesting AI-generated hallucination.
   - "Legitimate": Verified factual report.

4. OVERALL VERDICT:
   - "VERIFIED" (🟢): High consensus among Tier 1/2 sources.
   - "DISPUTED" (🟡): Conflicting reports among reputable outlets.
   - "DEBUNKED" (🔴): Multiple authoritative sources directly contradict or disprove the claim.
   - "UNVERIFIABLE" (⚪): Insufficient evidence to confirm or deny.

5. OUTPUT FORMAT: Output MUST be valid, raw JSON only. Do NOT include markdown code fences (like ```json), commentary, or extra text.

JSON OUTPUT STRUCTURE:
{
  "verdict": "DEBUNKED",
  "confidence_score": 94,
  "misinfo_type": "Fabricated Data",
  "reasoning_summary": "Cohesive 3-4 sentence plain-English explanation of why this verdict was reached, citing specific findings.",
  "key_contradiction": "Specific conflicting statements identified across sources (or null if none)",
  "source_stances": [
    {
      "source_id": 1,
      "domain": "nasa.gov",
      "stance": "CONTRADICTS",
      "one_line_summary": "Official NASA archives show zero records of any such discovery."
    }
  ]
}
"""


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
            "verdict": "UNVERIFIABLE",      # default fallback - prevents crahsing
            "confidence_score": 0
        }

    # Check if a live Nebius API key is configured
    key_status = settings.validate_keys()
    if not key_status["nebius"]:
        # Seamless fallback simulation while Nebius account review is pending
        return _simulate_cross_reference_fallback(claim_text, sources)

    try:
        client = get_nebius_client()
        evidence_text = _format_evidence_dossier(sources)       # formats sources into numbered list for LLM prompt (for Nemotron 3 Ultra)

        user_content = f"""CLAIM TO VERIFY:
\"\"\"{claim_text}\"\"\"

RETRIEVED LIVE EVIDENCE DOSSIER ({len(sources)} sources examined):
{evidence_text}

Perform deep logical cross-referencing and return the required JSON evaluation."""

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

        raw_output = response.choices[0].message.content.strip()
        cleaned_json = clean_json_string(raw_output)

        parsed_data = json.loads(cleaned_json)
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
            "claim_text": claim_text
        }


# raw sources -> numbered list - used in cross_reference_claim()
def _format_evidence_dossier(sources: list) -> str:
    if not sources:
        return "No external sources were retrieved."

    dossier_lines = []
    for s in sources:
        dossier_lines.append(
            f"--- SOURCE #{s.get('source_id', '?')} ---\n"
            f"Title: {s.get('title', 'Unknown')}\n"
            f"Domain: {s.get('domain', 'Unknown')} ({s.get('tier_label', 'Tier 4')})\n"
            f"URL: {s.get('url', '')}\n"
            f"Snippet: {s.get('snippet', 'No snippet available.')}\n"
        )
    return "\n".join(dossier_lines)     # LLMs process structured text more accurately than raw JSON format


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