import streamlit as st
from pathlib import Path
import time

# python colour constants - mirrors :root variables in assets/style.css
COLORS = {
    "red": "#EF4444",
    "yellow": "#F59E0B",
    "green": "#22C55E",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8"
}

st.set_page_config(     # needs to be at the top, before anything else
    page_title="DeepTrace - Misinformation Radar",
    page_icon="🛰️",
    layout="wide",          # column to entire screen width
    initial_sidebar_state="expanded"
)


def load_css(file_path: str):       # injecting style.css into Streamlit app
    css_file = Path(file_path)
    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:        # utf-8 for emojis and special characters
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)       # reads the file into a <style> tag (single string) - Streamlit escapes raw HTML/CSS by default - without it style tags would be displayed as text
    else:
        st.warning(f"⚠️ Style file not found at {file_path}")

def html(content: str):     # shorthand helper to render html with less code bloat
    st.markdown(content, unsafe_allow_html=True)

load_css("assets/style.css")



# Displays model and API health status
with st.sidebar:
    html("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:3rem;">🛰️</div>
        <div style="font-size:1.3rem; font-weight:800; color:#F1F5F9;">DeepTrace</div>
        <div style="font-size:0.75rem; color:#64748B; letter-spacing:2px; text-transform:uppercase;"> Misinformation Radar </div>
    </div>
    """)

    st.divider()

    st.markdown("### ⚙️ Infrastructure Status")        # h4t
    html("""
    <div style="display:flex; flex-direction:column; gap:10px; margin-top:0.5rem;">
        <div class="infra-row">
            <span><span class="status-dot"></span><span class="infra-label">Nebius Token Factory</span></span>
            <span class="infra-role">Inference Host</span>
        </div>
        <div class="infra-row">
            <span><span class="status-dot"></span><span class="infra-label">Nemotron 3 Ultra</span></span>
            <span class="infra-role">Deep Reasoning</span>
        </div>
        <div class="infra-row">
            <span><span class="status-dot"></span><span class="infra-label">Nemotron Nano</span></span>
            <span class="infra-role">Fast Extraction</span>
        </div>
        <div class="infra-row">
            <span><span class="status-dot"></span><span class="infra-label">Tavily Search API</span></span>
            <span class="infra-role">Live Grounding</span>
        </div>
    </div>
    """)

    st.divider()

    st.markdown("### 🔬 Verification Pipeline")
    html("""
    <div style="display:flex; flex-wrap:wrap; gap:4px; justify-content:center;">
        <span class="stage-pill">🧬 Extract </span>
        <span class="stage-pill">🌐 Search </span>
        <span class="stage-pill">⚖️ Analyze </span>
        <span class="stage-pill">📊 Score </span>
    </div>
    """)


# HERO SECTION
html('<div class="hero-title">🛰️ DeepTrace</div>')
html("""
<div class="hero-subtitle">
    Paste any claim. Get a real-time, multi-source confidence scorecard in seconds.
</div>
""")

# USER INPUT AREA
user_claim = st.text_area(
    label="Claim Input",
    placeholder="Example: \"NASA scientists have confirmed the discovery of an ancient alien spacecraft buried beneath Antarctic ice sheet...\"",
    height = 175,
    label_visibility="collapsed"
)

# symmetrical column layout - centers buttons horizontally
col_spacer_l, col_btn, col_batch, col_spacer_r = st.columns([3.5, 2.2, 2.2, 3.5])

with col_btn:       # verify_clicked: boolean to see whether it has been clicked or not
    verify_clicked = st.button("🔍  Run Verification", type="primary", use_container_width=True)       # forcing to use full width of col

with col_batch:
    batch_mode = st.checkbox(
        "📰 Batch Article Mode",
        help="Decomposes a full article into multiple atomic claims and verifies each independently."
    )
 

# verification pipeline simulation - manages the progress bar and stage indicators
if verify_clicked:
    if not user_claim.strip():      # empty after removing whitespace
        html(f"""
        <div class="glass-card" style="border-color: rgba(var(--yellow-rgb), 0.4); margin-top:1rem;">
            <span style="font-size:1.2rem;">⚠️</span>
            <span style="color:{COLORS['yellow']}; font-weight:600; margin-left:8px;">
                No input detected. Please paste a claim or article excerpt above.
            </span>
        </div>
        """)
    else:
        html("<br>")

        # stage progress bar and indicator pills
        stage_container = st.empty()
        progress_bar = st.progress(0, text="Initializing verification pipeline...")

        # Stage 1: Extraction
        stage_container.markdown("""
        <div style="display:flex; gap:6px; margin-bottom:1rem; justify-content:center;">
            <span class="stage-pill active">🧬 Extracting Claims...</span>
            <span class="stage-pill">🌐 Search</span>
            <span class="stage-pill">⚖️ Analyze</span>
            <span class="stage-pill">📊 Score</span>
        </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(25, text="Stage 1/4 — Extracting atomic claims via NVIDIA Nemotron Nano...")
        time.sleep(0.7)

        # Stage 2: Retrieval
        stage_container.markdown("""
        <div style="display:flex; gap:6px; margin-bottom:1rem; justify-content:center;">
            <span class="stage-pill done">✅ Extracted</span>
            <span class="stage-pill active">🌐 Searching Sources...</span>
            <span class="stage-pill">⚖️ Analyze</span>
            <span class="stage-pill">📊 Score</span>
        </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(50, text="Stage 2/4 — Querying 8 live sources via Tavily AI...")
        time.sleep(0.7)

        # Stage 3: Cross-Referencing
        stage_container.markdown("""
        <div style="display:flex; gap:6px; margin-bottom:1rem; justify-content:center;">
            <span class="stage-pill done">✅ Extracted</span>
            <span class="stage-pill done">✅ 8 Sources Found</span>
            <span class="stage-pill active">⚖️ Cross-Referencing...</span>
            <span class="stage-pill">📊 Score</span>
        </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(75, text="Stage 3/4 — Cross-referencing evidence via NVIDIA Nemotron 3 Ultra...")
        time.sleep(0.7)

        # Stage 4: Verdict
        stage_container.markdown("""
        <div style="display:flex; gap:6px; margin-bottom:1rem; justify-content:center;">
            <span class="stage-pill done">✅ Extracted</span>
            <span class="stage-pill done">✅ 8 Sources Found</span>
            <span class="stage-pill done">✅ Analyzed</span>
            <span class="stage-pill active">📊 Scoring...</span>
        </div>
        """, unsafe_allow_html=True)
        progress_bar.progress(100, text="Stage 4/4 — Synthesizing scorecard...")
        time.sleep(0.3)

        # Pipeline complete state
        stage_container.markdown("""
        <div style="display:flex; gap:6px; margin-bottom:1rem; justify-content:center;">
            <span class="stage-pill done">✅ Extracted</span>
            <span class="stage-pill done">✅ 8 Sources Found</span>
            <span class="stage-pill done">✅ Analyzed</span>
            <span class="stage-pill done">✅ Scored</span>
        </div>
        """, unsafe_allow_html=True)

        # Results Summary Section
        st.divider()
        st.markdown("## 📋 Verification Results")

        m1, m2, m3, m4 = st.columns(4)      # equal widths
        with m1:
            st.metric("Overall Verdict", "🔴 DEBUNKED")
        with m2:
            st.metric("Confidence", "94%")
        with m3:
            st.metric("Sources Examined", "8")
        with m4:
            st.metric("Misinfo Type", "Fabricated")

        html("<br>")

        html("""
        <div style="text-align:center; margin:1.5rem 0;">
            <span class="verdict-debunked">🔴 DEBUNKED — HIGH CONFIDENCE</span>
        </div>
        """)

        # Reasoning Summary Card
        html(f"""
        <div class="glass-card">
            <h3 style="color:{COLORS['text_primary']}; margin-top:0;">🧠 AI Reasoning Summary</h3>
            <p style="color:{COLORS['text_secondary']}; line-height:1.7;">
                No credible news agency (AP, Reuters, BBC, NASA.gov) has reported any discovery 
                of alien spacecraft beneath Antarctic ice. The claim originates from 
                <em>The Daily Galaxy</em>, a known satirical/fabrication outlet. 
                NASA's official archive contains zero matching records.
            </p>
        </div>
        """)

        html("<br>")

        # Source Evidence Breakdown
        st.markdown("## 🔗 Source-by-Source Evidence")

        html(f"""
        <div class="source-card">
            <h4>📰 Reuters <span class="source-tier tier-2">TIER 2 — Wire Service</span></h4>
            <p><strong>Stance:</strong> <span style="color:{COLORS['green']};">No supporting evidence found.</span> 
            Reuters archive search returned 0 matching results for the claimed date.</p>
        </div>
        """)

        html(f"""
        <div class="source-card">
            <h4>🏛️ NASA.gov <span class="source-tier tier-1">TIER 1 — Official/Gov</span></h4>
            <p><strong>Stance:</strong> <span style="color:{COLORS['red']};">Directly contradicts claim.</span> 
            NASA official portal has no records of any extraterrestrial artifact missions.</p>
        </div>
        """)

        html(f"""
        <div class="source-card">
            <h4>🌐 The Daily Galaxy <span class="source-tier tier-4">TIER 4 — Unreliable</span></h4>
            <p><strong>Stance:</strong> <span style="color:{COLORS['yellow']};">Origin of claim.</span> 
            Primary source identified as an unverified tabloid blog lacking editorial oversight.</p>
        </div>
        """)