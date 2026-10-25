"""
backend/source_retriever.py — Stage 2: Live Multi-Source Retrieval
Queries Search API AI Search API for live grounding evidence and assigns
domain credibility tiers (Tier 1 to Tier 4) to each retrieved source.
"""

import re               # regex for stripping markdown noise from Search API snippets
from urllib.parse import urlparse       # root domain and subdomain extraction
from tavily import TavilyClient
from config.settings import settings


# Tier ranking
# Tier 1: Official Government, International Bodies, Peer-Reviewed Science
TIER_1_DOMAINS = {
    "nasa.gov", "who.int", "cdc.gov", "nih.gov", "un.org",
    "nature.com", "science.org", "sciencedirect.com", "arxiv.org",
    "gov.uk", "europa.eu", "whitehouse.gov", "state.gov",
    "esa.int", "home.cern", "iopscience.iop.org", "eso.org",
    "pmc.ncbi.nlm.nih.gov"
}

# Tier 2: Primary Global News Wire Agencies & Authoritative Reference Works
TIER_2_DOMAINS = {
    "reuters.com", "apnews.com", "afp.com", "bloomberg.com",
    "upi.com", "prnewswire.com", "businesswire.com",
    "britannica.com", "ebsco.com", "cerncourier.com", "ncse.ngo"
}

# Tier 3: Established Mainstream Media, Science Journalism & Curated Encyclopedias
TIER_3_DOMAINS = {
    "bbc.com", "bbc.co.uk", "nytimes.com", "washingtonpost.com",
    "theguardian.com", "wsj.com", "ft.com", "aljazeera.com",
    "cnn.com", "nbcnews.com", "cbsnews.com", "abcnews.go.com",
    "time.com", "economist.com", "theatlantic.com", "forbes.com",
    "scientificamerican.com", "nationalgeographic.com", "space.com",
    "en.wikipedia.org", "simple.wikipedia.org",
    "sciencefocus.com", "skyatnightmagazine.com", "planetary.org"
}


# Strips markdown formatting, file references, and navigation noise from Search API snippets.
# Search API's advanced search sometimes pulls entire page structures including download
# links, image captions, and social media buttons — none of which are useful evidence.
def _clean_snippet(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r'#{1,6}\s*', '', text)           # Remove markdown headers (###### Movies -> Movies)
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)            # Remove markdown links [text](url) - keep just the text
    text = re.sub(r'\[[\w\-_.]+\.(?:mp4|webm|mp3|jpg|png|gif|srt|vtt|pdf|zip)\s*[^\]]*\]', '', text, flags=re.IGNORECASE)           # Remove file references like [filename.mp4 (1920x1080) [145.6 MB]]
    text = re.sub(r'\[(?:edit|\d+|\d+\.\d+\s*\w+)\]', '', text, flags=re.IGNORECASE)            # Remove bracketed metadata like [edit], [1], [145.6 MB], [84 bytes]
    text = re.sub(r'\b(?:Facebook|Twitter|Reddit|Pinterest|Flipboard|Subscribe|Follow|Log in|Reply)\b', '', text)       # Remove common navigation and social media noise words
    text = re.sub(r'\s+', ' ', text).strip()        # Collapse multiple spaces and newlines into single space
    return text


# Truncates a text snippet to a maximum word count, preserving sentence boundaries.
# Prevents LLM context overflow when Search API returns full-page content dumps.
def _truncate_snippet(text: str, max_words: int = 200) -> str:
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text
    truncated = " ".join(words[:max_words])
    last_period = truncated.rfind(".")        # try to cut at a sentence boundary
    if last_period > max_words * 3:           # only if the period is past ~60% of the limit
        return truncated[:last_period + 1]
    return truncated + "..."                  # hard cut with ellipsis if no clean boundary found


# Initializes and returns an authenticated search client - returns None if the key is missing or invalid.
def get_search_client() -> TavilyClient | None:
    if not settings.SEARCH_API_KEY or settings.SEARCH_API_KEY.startswith("your_"):
        return None
    return TavilyClient(api_key=settings.SEARCH_API_KEY)



# takes a full URL, extracts its root domain, and classifies its credibility tier.
# dict: {"tier": int, "label": str, "badge_class": str, "domain": str}
def classify_domain_tier(url: str) -> dict:
    try:
        parsed_url = urlparse(url)      # Extract domain (e.g., 'www.nasa.gov') and strip 'www.' and make it lowercase
        domain = parsed_url.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]

        # Rule 1: Any official government or academic top-level domain
        if domain.endswith(".gov") or domain.endswith(".edu") or domain.endswith(".mil"):
            return {
                "tier": 1,
                "label": "TIER 1 — Official / Gov / Edu",
                "badge_class": "tier-1",
                "domain": domain
            }

        # Rule 2: Explicit Tier 1 scientific/official domain matches
        if any(domain == d or domain.endswith("." + d) for d in TIER_1_DOMAINS):
            return {
                "tier": 1,
                "label": "TIER 1 — Official / Academic",
                "badge_class": "tier-1",
                "domain": domain
            }

        # Rule 3: Tier 2 Wire Services
        if any(domain == d or domain.endswith("." + d) for d in TIER_2_DOMAINS):
            return {
                "tier": 2,
                "label": "TIER 2 — Wire Service",
                "badge_class": "tier-2",
                "domain": domain
            }

        # Rule 4: Tier 3 Established Media
        if any(domain == d or domain.endswith("." + d) for d in TIER_3_DOMAINS):
            return {
                "tier": 3,
                "label": "TIER 3 — Established Media",
                "badge_class": "tier-3",
                "domain": domain
            }

        # Rule 5: Fallback — Tier 4 General Web / Blog
        return {
            "tier": 4,
            "label": "TIER 4 — General Web / Blog",
            "badge_class": "tier-4",
            "domain": domain
        }

    except Exception:
        return {
            "tier": 4,
            "label": "TIER 4 — Unverified Domain",
            "badge_class": "tier-4",
            "domain": "unknown"
        }


# performs the live web search and returns the raw results list
def _search_web(query: str, limit: int) -> list:
    client = get_search_client()
    if not client:
        return None         # signals caller to use simulation fallback

    # Perform live search via configured search AI
    search_response = client.search(
        query=query.strip(),
        search_depth="advanced",         # search_depth=advanced extracts clean paragraph content from each page, filters out ads, navigation menus, cookie banners, and other noise.
        max_results=limit,
        include_answer=False,            # don't want Search API's opinion
        include_raw_content=False        # don't want full page HTML, just clean text snippets
    )

    return search_response.get("results", [])    # extracting results list from search API's JSON response - empty list if no results found


# processes raw Search API results: cleans snippets, truncates, classifies tiers, assigns IDs
def _process_results(raw_results: list) -> list:
    structured_sources = []

    for index, item in enumerate(raw_results, start=1):     # source IDs start at 1 for display purposes
        url = item.get("url", "")
        tier_info = classify_domain_tier(url)

        raw_content = item.get("content", "").strip()
        clean_content = _clean_snippet(raw_content)         # strip markdown noise first
        short_content = _truncate_snippet(clean_content)     # then truncate to ~200 words

        source_entry = {
            "source_id": index,
            "title": item.get("title", "Untitled Source"),
            "url": url,
            "snippet": short_content,
            "score": round(item.get("score", 0.0), 3),      # 3 dp
            "domain": tier_info["domain"],
            "tier": tier_info["tier"],
            "tier_label": tier_info["label"],
            "badge_class": tier_info["badge_class"]
        }
        structured_sources.append(source_entry)

    # Sort sources: highest credibility first (Tier 1 -> Tier 4), then by Search API relevance score
    structured_sources.sort(key=lambda x: (x["tier"], -x["score"]))     # ascending tier (1 is best), descending score
    return structured_sources


# Queries the configured search AI Search API for live grounding evidence across the web.
# dict: {"success": bool, "query": str, "total_found": int, "sources": list}
def retrieve_sources(query: str, max_results: int | None = None) -> dict:
    if not query or not query.strip():
        return {
            "success": False,
            "error": "Empty search query provided.",
            "query": "",
            "total_found": 0,
            "sources": []
        }

    limit = max_results or settings.MAX_SEARCH_RESULTS      # reducing sources per claim in batch mode

    try:
        raw_results = _search_web(query, limit)

        # If Search API key is missing, use offline mock simulator
        if raw_results is None:
            return _simulate_sources_fallback(query, limit)

        structured_sources = _process_results(raw_results)

        return {
            "success": True,
            "query": query,
            "total_found": len(structured_sources),
            "sources": structured_sources,
            "is_mock": False
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Search API error: {str(e)}",
            "query": query,
            "total_found": 0,
            "sources": []
        }


# Mock source generator for offline development.
def _simulate_sources_fallback(query: str, limit: int) -> dict:
    mock_sources = [
        {
            "source_id": 1,
            "title": "NASA Official Press Releases & Mission Archive",
            "url": "https://www.nasa.gov/news/archive",
            "snippet": "Official NASA portal shows no press releases, missions, or scientific findings regarding artificial extraterrestrial structures under Antarctic ice.",
            "score": 0.95,
            "domain": "nasa.gov",
            "tier": 1,
            "tier_label": "TIER 1 — Official / Gov / Edu",
            "badge_class": "tier-1"
        },
        {
            "source_id": 2,
            "title": "Reuters Fact Check: Antarctic Spacecraft Claims",
            "url": "https://www.reuters.com/fact-check",
            "snippet": "Archive search reveals zero credible reporting confirming the viral social media post. Similar claims have circulated repeatedly since 2018.",
            "score": 0.88,
            "domain": "reuters.com",
            "tier": 2,
            "tier_label": "TIER 2 — Wire Service",
            "badge_class": "tier-2"
        },
        {
            "source_id": 3,
            "title": "The Daily Galaxy: Unverified Antarctic Anomaly",
            "url": "https://dailygalaxy.com/viral-antarctic-post",
            "snippet": "Sensational blog post citing unnamed whistleblowers and unverified satellite radar imagery alleging covered-up structures.",
            "score": 0.72,
            "domain": "dailygalaxy.com",
            "tier": 4,
            "tier_label": "TIER 4 — General Web / Blog",
            "badge_class": "tier-4"
        }
    ]

    return {
        "success": True,
        "query": query,
        "total_found": min(len(mock_sources), limit),
        "sources": mock_sources[:limit],
        "is_mock": True
    }