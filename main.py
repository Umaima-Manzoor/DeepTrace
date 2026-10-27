"""
main.py - DeepTrace FastAPI Application
Serves the web interface and connects the 4-stage verification pipeline to the HTML frontend via htmx.
"""

from fastapi import FastAPI, Request, Form          # FastAPI: creates web application      Request: object containing all info about the incoming HTTP request - need to pass into Jinja2 to generate correct URLs     Form: extracts the form fields by name
from fastapi.responses import HTMLResponse, PlainTextResponse       
from fastapi.staticfiles import StaticFiles         # for safely loading style.css fron /static - otherwise would get an error on loading
from fastapi.templating import Jinja2Templates      # lets us render HTML files with python variables

from backend.claim_extractor import extract_claims
from backend.source_retriever import retrieve_sources
from backend.cross_referencer import cross_reference_claim
from backend.report_generator import generate_verification_report
from config.settings import settings
from pathlib import Path

app = FastAPI(title="DeepTrace", version="1.0.0")
ROOT = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "templates")          # where to look for the template files

# Returns a minimal UNVERIFIABLE report when a single claim fails mid-pipeline
def _failed_claim_report(claim_text: str, error: str) -> dict:
    return {
        "success": False,
        "is_mock": False,
        "claim_text": claim_text,
        "verdict": "UNVERIFIABLE",
        "verdict_badge_class": "verdict-unverifiable",
        "confidence_score": 0,
        "misinfo_type": "Unclassified",
        "reasoning_summary": f"Analysis failed for this claim: {error}",
        "key_contradiction": None,
        "metrics": {
            "total_sources": 0, "supports_count": 0, "contradicts_count": 0,
            "origin_count": 0, "neutral_count": 0,
            "tier_1_count": 0, "tier_2_count": 0, "tier_3_count": 0, "tier_4_count": 0,
            "high_trust_ratio": "0%"
        },
        "sources": [],
        "export_markdown": ""
    }

@app.get("/", response_class=HTMLResponse)      # run this function when a GET request is sent and this route returns HTML
async def home(request: Request):   #Async: can handle multiple requests simultaneously - renders the home page with the claim input form - Request: HTTP object
    return templates.TemplateResponse(request, "index.html")


@app.post("/verify", response_class=HTMLResponse)       # handles POST requests to /verify
async def verify(request: Request, claim_text: str = Form(...), batch_mode: str | None = Form(None) ):        #claim_text is required or else an error     batch_mode None means optional        Runs the full 4-stage verification pipeline and returns results HTML

    if not claim_text or not claim_text.strip():
        return templates.TemplateResponse(
            request, "partials/error.html",
            {"error_message": "No input detected. Paste a claim or article excerpt."}
        )

    is_batch = batch_mode == "true"

    if len(claim_text) > 8000:
        return templates.TemplateResponse(request, "partials/error.html", {
            "error_message": "Input too long. Please keep claims under 8,000 characters.",
        })

    try:
        # Stage 1: Extract atomic claims
        extraction = extract_claims(claim_text, batch_mode=is_batch)
        if not extraction.get("success"):
            return templates.TemplateResponse(
                request, "partials/error.html",
                {"error_message": "Claim extraction failed. Please try again."}
            )

        # Determine which claims to process - single mode uses first claim only, batch uses all (capped at 5)
        all_claims = extraction.get("claims", [])
        if is_batch:
            claims_to_process = all_claims[:5]      # cap at 5 to prevent excessive API calls and wait times
        else:
            claims_to_process = all_claims[:1]      # single mode: primary claim only

        if not claims_to_process:
            return templates.TemplateResponse(request, "partials/error.html", {
                "error_message": "No verifiable claims were extracted. Try a more specific claim.",
            })

        # Stages 2-4: Retrieve, Cross-Reference, Report - for each claim
        reports = []
        for claim in claims_to_process:
            try:
                sources_data = retrieve_sources(claim["search_query"])
                verdict_data = cross_reference_claim(claim, sources_data)
                report = generate_verification_report(claim, sources_data, verdict_data)
                reports.append(report)
            except Exception as e:
                print(f"[ERROR] Claim failed: {claim.get('claim_text', '')[:80]} — {e}")        # first 80 chars of the claim that failed so that the logs don't get flooded
                reports.append(_failed_claim_report(claim.get("claim_text", "Unknown claim"), "Verification failed. Please try again."))

        # Combine all markdown reports into a single downloadable document
        combined_markdown = "\n\n---\n\n".join(
            r.get("export_markdown", "") for r in reports if r.get("export_markdown")
        )

        return templates.TemplateResponse(
            request, "results.html",
            {"reports": reports, "is_batch": is_batch, "combined_markdown": combined_markdown}
        )

    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        return templates.TemplateResponse(
            request, "partials/error.html",
            {"error_message": "Verification failed. Please try again."}
        )


@app.post("/download")      # POST because the form sends the markdown content as form data
async def download(request: Request, report_markdown: str = Form(...)):         # Returns the verification report as a downloadable markdown file
    return PlainTextResponse(
        content=report_markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=deeptrace_report.md"}     # triggers browser's download dialog otherwise md text will be shown as it is on the page
    )


@app.get("/health")
async def health():     # Health check endpoint for deployment monitoring
    key_status = settings.validate_keys()
    return {
        "status": "ok",
        "llm_key": key_status["llm"],
        "search_key": key_status["search"],
        "environment": settings.APP_ENV
    }