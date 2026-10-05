""" Stage 4: Evidence Report & Scorecard Synthesis
Merges outputs from Stage 1 (claims), Stage 2 (sources), and Stage 3 (verdict),
computes aggregate credibility metrics, and produces a unified report dossier.
"""

from datetime import datetime

# synthesizes outputs from Stages 1, 2, and 3 into a clean, comprehensive master report.
# returns a master report dictionary ready for UI rendering and file export.
def generate_verification_report(claim_data: dict, sources_data: dict, verdict_data: dict) -> dict:
    claim_text = claim_data.get("claim_text") or verdict_data.get("claim_text", "Unknown Claim")         # if stage 1 has raw form
    verdict = verdict_data.get("verdict", "UNVERIFIABLE").upper()
    confidence = int(verdict_data.get("confidence_score", 0))
    misinfo_type = verdict_data.get("misinfo_type", "Unclassified")
    reasoning = verdict_data.get("reasoning_summary", "No reasoning summary provided.")
    key_contradiction = verdict_data.get("key_contradiction")

    raw_sources = sources_data.get("sources", [])
    raw_stances = verdict_data.get("source_stances", [])

    enriched_sources = _enrich_sources_with_stances(raw_sources, raw_stances)       # map stances back to sources by matching source_id or domain

    metrics = _compute_aggregate_metrics(enriched_sources)      # compute aggregate credibility & stance distribution metrics

    # map verdict to UI badge class defined in assets/style.css
    badge_map = {
        "VERIFIED": "verdict-verified",
        "DISPUTED": "verdict-disputed",
        "DEBUNKED": "verdict-debunked",
        "UNVERIFIABLE": "verdict-unverifiable"
    }
    verdict_badge_class = badge_map.get(verdict, "verdict-unverifiable")

    is_mock = claim_data.get("is_mock", False) or sources_data.get("is_mock", False) or verdict_data.get("is_mock", False)      # checks if any stage ran in simulation mode
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M PKT")

    report = {
        "success": True,
        "timestamp": timestamp,
        "is_mock": is_mock,
        "claim_text": claim_text,
        "verdict": verdict,
        "verdict_badge_class": verdict_badge_class,
        "confidence_score": confidence,
        "misinfo_type": misinfo_type,
        "reasoning_summary": reasoning,
        "key_contradiction": key_contradiction,
        "metrics": metrics,
        "sources": enriched_sources,
        "export_markdown": ""
    }

    # Generate clean text dossier for export / copy
    report["export_markdown"] = _generate_markdown_dossier(report)
    return report


# pairs each retrieved source from Stage 2 with its stance determination from Stage 3 - left join of sources with stances
def _enrich_sources_with_stances(sources: list, stances: list) -> list:
    # Create lookup map by source_id and domain for fast matching (O(1))
    stance_by_id = {s.get("source_id"): s for s in stances if "source_id" in s}
    stance_by_domain = {s.get("domain", "").lower(): s for s in stances if "domain" in s}

    # Stance color mapping for UI rendering
    stance_color_map = {
        "SUPPORTS": "#22C55E",          # Green
        "CONTRADICTS": "#EF4444",        # Red
        "ORIGIN_OF_CLAIM": "#F59E0B",    # Yellow
        "NEUTRAL": "#94A3B8"             # Slate Grey
    }
    
    enriched = []
    for s in sources:
        sid = s.get("source_id")
        domain = s.get("domain", "").lower()

        # Find matching stance from Stage 3
        matched_stance = stance_by_id.get(sid) or stance_by_domain.get(domain)

        if matched_stance:
            stance_type = matched_stance.get("stance", "NEUTRAL").upper()
            stance_summary = matched_stance.get("one_line_summary", s.get("snippet", ""))
        else:
            stance_type = "NEUTRAL"
            stance_summary = s.get("snippet", "")

        entry = dict(s)
        entry["stance"] = stance_type
        entry["stance_summary"] = stance_summary
        entry["stance_color"] = stance_color_map.get(stance_type, "#94A3B8")
        enriched.append(entry)

    return enriched


# computes summary statistics across all examined sources.
def _compute_aggregate_metrics(enriched_sources: list) -> dict:
    total = len(enriched_sources)
    supports = sum(1 for s in enriched_sources if s.get("stance") == "SUPPORTS")
    contradicts = sum(1 for s in enriched_sources if s.get("stance") == "CONTRADICTS")
    origin = sum(1 for s in enriched_sources if s.get("stance") == "ORIGIN_OF_CLAIM")
    neutral = sum(1 for s in enriched_sources if s.get("stance") == "NEUTRAL")

    tier_1_count = sum(1 for s in enriched_sources if s.get("tier") == 1)
    tier_2_count = sum(1 for s in enriched_sources if s.get("tier") == 2)
    tier_3_count = sum(1 for s in enriched_sources if s.get("tier") == 3)
    tier_4_count = sum(1 for s in enriched_sources if s.get("tier") == 4)

    return {
        "total_sources": total,
        "supports_count": supports,
        "contradicts_count": contradicts,
        "origin_count": origin,
        "neutral_count": neutral,
        "tier_1_count": tier_1_count,
        "tier_2_count": tier_2_count,
        "tier_3_count": tier_3_count,
        "tier_4_count": tier_4_count,
        "high_trust_ratio": f"{round(((tier_1_count + tier_2_count) / max(total, 1)) * 100)}%"
    }


# generates a clean, copy-pasteable Markdown summary report.
def _generate_markdown_dossier(report: dict) -> str:
    md = [
        f"# 🛰️ DeepTrace Fact-Checking Dossier",
        f"**Generated:** {report['timestamp']}",
        f"**Overall Verdict:** {report['verdict']} ({report['confidence_score']}% Confidence)",
        f"**Misinformation Classification:** {report['misinfo_type']}",
        f"\n## 📌 Claim Investigated",
        f"> \"{report['claim_text']}\"",
        f"\n## 🧠 AI Reasoning Analysis",
        f"{report['reasoning_summary']}",
    ]

    if report.get("key_contradiction"):
        md.extend([
            f"\n## ⚠️ Key Contradiction Identified",
            f"{report['key_contradiction']}"
        ])

    md.extend([
        f"\n## 📊 Evidence Breakdown ({report['metrics']['total_sources']} Sources Examined)",
        f"- **Supporting Sources:** {report['metrics']['supports_count']}",
        f"- **Contradicting Sources:** {report['metrics']['contradicts_count']}",
        f"- **Tier 1 (Official/Gov):** {report['metrics']['tier_1_count']}",
        f"- **Tier 2 (Wire Services):** {report['metrics']['tier_2_count']}",
        f"- **High-Trust Source Ratio:** {report['metrics']['high_trust_ratio']}",
        f"\n### Source Citations"
    ])

    for s in report.get("sources", []):
        md.append(f"1. **[{s.get('domain')}]** {s.get('title')} ({s.get('tier_label')}) — *Stance: {s.get('stance')}*\n   {s.get('url')}\n   > \"{s.get('stance_summary')}\"\n")

    md.append("\n---\n*Report generated autonomously by DeepTrace via NVIDIA Nemotron & Tavily AI on Nebius Token Factory.*")
    return "\n".join(md)