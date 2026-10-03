import streamlit as st
from pathlib import Path
import time

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

load_css("assets/style.css")



# Displays model and API health status
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; margin-bottom:1.5rem;">
        <div style="font-size:3rem;">🛰️</div>
        <div style="font-size:1.3rem; font-weight:800; color:#F1F5F9;">DeepTrace</div>
        <div style="font-size:0.75rem; color:#64748B; letter-spacing:2px; text-transform:uppercase;"> Misinformation Radar </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### ⚙️ Infrastructure Status")        # h4t
    st.markdown("""
    <div style="display:flex; flex-direction:column; gap:10px; margin-top:0.5rem;">
        <div>
            <span class="status-dot"></span>
            <span style="color:#F1F5F9; font-weight:600;">Nebius Token Factory</span>
            <span style="color:#64748B; font-size:0.8rem; float:right;">Inference Host</span>
        </div>
        <div>
            <span class="status-dot"></span>
            <span style="color:#F1F5F9; font-weight:600;">Nemotron 3 Ultra</span>
            <span style="color:#64748B; font-size:0.8rem; float:right;">Deep Reasoning</span>
        </div>
        <div>
            <span class="status-dot"></span>
            <span style="color:#F1F5F9; font-weight:600;">Nemotron Nano</span>
            <span style="color:#64748B; font-size:0.8rem; float:right;">Fast Extraction</span>
        </div>
        <div>
            <span class="status-dot"></span>
            <span style="color:#F1F5F9; font-weight:600;">Tavily Search API</span>
            <span style="color:#64748B; font-size:0.8rem; float:right;">Live Grounding</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### 🔬 Verification Pipeline")
    st.markdown("""
    <div style="display:flex; flex-wrap:wrap; gap:4px;">
        <span class="stage-pill">🧬 Extract </span>
        <span class="stage-pill">🌐 Search </span>
        <span class="stage-pill">⚖️ Analyze </span>
        <span class="stage-pill">📊 Score </span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("""
    <div style="text-align:center; color:#64748B; font-size:0.75rem; margin-top:1rem;">
        Built for the<br>
        <span style="color:#8B5CF6; font-weight:700;">Nebius × NVIDIA</span> Global AI Hackathon<br>
        Track 2: Best Apps & Agents<br><br>
        <span style="color:#475569;">v2.0 • Solo Entry • 2026</span>
    </div>
    """, unsafe_allow_html=True)


# HERO SECTION
st.markdown('<div class="hero-title">🛰️ DeepTrace</div>', unsafe_allow_html=True)
st.markdown("""
<div class="hero-subtitle">
    Autonomous multi-source fact-verification engine. Paste any claim, 
    viral headline, or news excerpt - get a real-time confidence scorecard 
    powered by NVIDIA Nemotron reasoning models and Tavily live search.
</div>
""", unsafe_allow_html=True)

# USER INPUT AREA
user_claim = st.text_area(
    label="Claim Input",
    placeholder="Example: \"NASA scientists have confirmed the discovery of an ancient alien spacecraft buried beneath Antarctic ice sheet...\"",
    height = 175,
    label_visibility="collapsed"
)

col_btn, col_batch, col_spacer = st.columns([2, 2, 6])

with col_btn:       # verify_clicked: boolean to see whether it has been clicked or not
    verify_clicked = st.button("🔍  Run Full Verification", type="primary", use_container_width=True)       # forcing to use full width of col

with col_batch:
    batch_mode = st.checkbox(
        "📰 Batch Article Mode",
        help="Decomposes a full article into multiple atomic claims and verifies each independently."
    )
 

# verification pipeline simulation - manages the progress bar and stage indicators
if verify_clicked:
    if not user_claim.strip():      # empty after removing whitespace
        st.markdown("""
        <div class="glass-card" style="border-color: rgba(245,158,11,0.4); margin-top:1rem;">
            <span style="font-size:1.2rem;">⚠️</span>
            <span style="color:#F59E0B; font-weight:600; margin-left:8px;">
                No input detected. Please paste a claim or article excerpt above.
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<br>", unsafe_allow_html=True)

        # stage progress bar and indicator pills
        stage_container = st.empty()
        progress_bar = st.progress(0, text="Initializing verification pipeline...")

        # Stage 1: Extraction
        stage_container.markdown("""
        <div style="display:flex; gap:6px; margin-bottom:1rem;">
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
        <div style="display:flex; gap:6px; margin-bottom:1rem;">
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
        <div style="display:flex; gap:6px; margin-bottom:1rem;">
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
        <div style="display:flex; gap:6px; margin-bottom:1rem;">
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
        <div style="display:flex; gap:6px; margin-bottom:1rem;">
            <span class="stage-pill done">✅ Extracted</span>
            <span class="stage-pill done">✅ 8 Sources Found</span>
            <span class="stage-pill done">✅ Analyzed</span>
            <span class="stage-pill done">✅ Scored</span>
        </div>
        """, unsafe_allow_html=True)

        # Results Summary Section
        st.markdown("---")
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

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; margin:1.5rem 0;">
            <span class="verdict-debunked">🔴 DEBUNKED — HIGH CONFIDENCE</span>
        </div>
        """, unsafe_allow_html=True)

        # Reasoning Summary Card
        st.markdown("""
        <div class="glass-card">
            <h3 style="color:#F1F5F9; margin-top:0;">🧠 AI Reasoning Summary</h3>
            <p style="color:#94A3B8; line-height:1.7;">
                No credible news agency (AP, Reuters, BBC, NASA.gov) has reported any discovery 
                of alien spacecraft beneath Antarctic ice. The claim originates from 
                <em>The Daily Galaxy</em>, a known satirical/fabrication outlet. 
                NASA's official archive contains zero matching records.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Source Evidence Breakdown
        st.markdown("### 🔗 Source-by-Source Evidence")

        st.markdown("""
        <div class="source-card">
            <h4>📰 Reuters <span class="source-tier tier-2">TIER 2 — Wire Service</span></h4>
            <p><strong>Stance:</strong> <span style="color:#22C55E;">No supporting evidence found.</span> 
            Reuters archive search returned 0 matching results for the claimed date.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="source-card">
            <h4>🏛️ NASA.gov <span class="source-tier tier-1">TIER 1 — Official/Gov</span></h4>
            <p><strong>Stance:</strong> <span style="color:#EF4444;">Directly contradicts claim.</span> 
            NASA official portal has no records of any extraterrestrial artifact missions.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="source-card">
            <h4>🌐 The Daily Galaxy <span class="source-tier tier-4">TIER 4 — Unreliable</span></h4>
            <p><strong>Stance:</strong> <span style="color:#F59E0B;">Origin of claim.</span> 
            Primary source identified as an unverified tabloid blog lacking editorial oversight.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#475569; font-size:0.8rem; padding:1rem;">
            Powered by <span style="color:#76B900;">NVIDIA Nemotron</span> on 
            <span style="color:#8B5CF6;">Nebius Token Factory</span> • 
            Live search by <span style="color:#06B6D4;">Tavily AI</span>
        </div>
        """, unsafe_allow_html=True)