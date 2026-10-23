"""
main.py - DeepTrace FastAPI Application
Serves the web interface and connects the 4-stage verification pipeline to the HTML frontend via htmx.
"""

from fastapi import FastAPI, Request, Form          # FastAPI: creates web application      Request: object containing all info about the incomming HTTP requestion - need to pass into Jinja2 to generate correct URLs     Form: extracts the form fields by name
from fastapi.responses import HTMLResponse, PlainTextResponse       
from fastapi.staticfiles import StaticFiles         # for safely loading style.css fron /static - otherwise would get an error on loading
from fastapi.templating import Jinja2Templates      # lets us render HTML files with python variables

from backend.claim_extractor import extract_claims
from backend.source_retriever import retrieve_sources
from backend.cross_referencer import cross_reference_claim
from backend.report_generator import generate_verification_report
from config.settings import settings

app = FastAPI(title="DeepTrace", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")          # where to look for the template files


@app.get("/", response_class=HTMLResponse)      # run this function when a GET request is sent and this route returns HTML
async def home(request: Request):   #Async: can handle multiple requests simultaneously - renders the home page with the claim input form - Request: HTTP object
    return templates.TemplateResponse(request, "index.html")


@app.post("/verify", response_class=HTMLResponse)       # handles POST requests to /verify
async def verify(request: Request, claim_text: str = Form(...), batch_mode: str = Form(None) ):        #claim_text is required or else an error     bactch_mode None means optional        Runs the full 4-stage verification pipeline and returns results HTML

    if not claim_text or not claim_text.strip():
        return templates.TemplateResponse(
            request, "partials/error.html",
            {"error_message": "No input detected. Paste a claim or article excerpt."}
        )

    is_batch = batch_mode == "true"

    try:
        # Stage 1: Extract atomic claims
        extraction = extract_claims(claim_text, batch_mode=is_batch)
        if not extraction.get("success"):
            return templates.TemplateResponse(
                request, "partials/error.html",
                {"error_message": extraction.get("error", "Claim extraction failed.")}
            )

        # Determine which claims to process - single mode uses first claim only, batch uses all (capped at 5)
        all_claims = extraction.get("claims", [])
        if is_batch:
            claims_to_process = all_claims[:5]      # cap at 5 to prevent excessive API calls and wait times
        else:
            claims_to_process = all_claims[:1]      # single mode: primary claim only

        # Stages 2-4: Retrieve, Cross-Reference, Report - for each claim
        reports = []
        for claim in claims_to_process:
            try:
                sources_data = retrieve_sources(claim["search_query"])
                verdict_data = cross_reference_claim(claim, sources_data)
                report = generate_verification_report(claim, sources_data, verdict_data)
                reports.append(report)
            except Exception as e:
                # Per-claim error handling: one failed claim doesn't kill the entire batch
                reports.append({
                    "success": False,
                    "is_mock": False,
                    "claim_text": claim.get("claim_text", "Unknown claim"),
                    "verdict": "UNVERIFIABLE",
                    "verdict_badge_class": "verdict-unverifiable",
                    "confidence_score": 0,
                    "misinfo_type": "Unclassified",
                    "reasoning_summary": f"Analysis failed for this claim: {str(e)}",
                    "key_contradiction": None,
                    "metrics": {
                        "total_sources": 0,
                        "supports_count": 0,
                        "contradicts_count": 0,
                        "origin_count": 0,
                        "neutral_count": 0,
                        "tier_1_count": 0,
                        "tier_2_count": 0,
                        "tier_3_count": 0,
                        "tier_4_count": 0,
                        "high_trust_ratio": "0%"
                    },
                    "sources": [],
                    "export_markdown": ""
                })

        # Combine all markdown reports into a single downloadable document
        combined_markdown = "\n\n---\n\n".join(
            r.get("export_markdown", "") for r in reports if r.get("export_markdown")
        )

        return templates.TemplateResponse(
            request, "results.html",
            {"reports": reports, "is_batch": is_batch, "combined_markdown": combined_markdown}
        )

    except Exception as e:
        return templates.TemplateResponse(
            request, "partials/error.html",
            {"error_message": f"Verification failed: {str(e)}"}
        )


@app.post("/download")      # POST because the form sends the markdown content as form data
async def download(request: Request, report_markdown: str = Form(...)):         # Returns the verification report as a downloadable markdown file
    return PlainTextResponse(
        content=report_markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=deeptrace_report.md"}     # triggers browser's download dialog otherwise md text will be shown as it is on the page
    )


@app.get("/health")
async def health():
    """Health check endpoint for deployment monitoring."""
    key_status = settings.validate_keys()
    return {
        "status": "ok",
        "nebius_key": key_status["nebius"],
        "tavily_key": key_status["tavily"],
        "environment": settings.APP_ENV
    }