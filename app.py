"""
app.py — DeepTrace Fact-Checking Dashboard
Nebius x NVIDIA Global AI Hackathon (Track 2: Best Apps and Agents)
"""

import streamlit as st
import datetime

# ---------------------------------------------------------
# Page Configuration (Dark Theme, Wide Layout)
# ---------------------------------------------------------
st.set_page_config(
    page_title="DeepTrace — Autonomous Fact-Checking Radar",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom CSS Styling for a sleek, modern investigative look
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Gradient Header Title */
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #76B900, #00C7B7, #8A2BE2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #A0AEC0;
        margin-bottom: 1.5rem;
    }
    /* Metric Card Styling */
    .metric-box {
        background-color: #1A202C;
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar: System Status & Model Information
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.shields.io/badge/Nebius-Token%20Factory-8A2BE2?style=for-the-badge", use_container_width=True)
    st.image("https://img.shields.io/badge/NVIDIA-Nemotron-76B900?style=for-the-badge", use_container_width=True)
    st.image("https://img.shields.io/badge/Tavily-AI%20Search-00C7B7?style=for-the-badge", use_container_width=True)
    
    st.divider()
    st.subheader("⚙️ Active Infrastructure")
    st.markdown("""
    - **Reasoning LLM:** `Nemotron 3 Ultra`
    - **Extraction LLM:** `Nemotron Nano`
    - **Inference Host:** `Nebius AI Cloud`
    - **Grounding Engine:** `Tavily Search API`
    """)
    
    st.divider()
    st.caption("Built for Nebius x NVIDIA Hackathon 2026")
    st.caption(f"System Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M PKT')}")

# ---------------------------------------------------------
# Main Cockpit
# ---------------------------------------------------------
st.markdown('<div class="main-title">🛰️ DeepTrace: Autonomous Misinformation Radar</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Multi-agent fact verification powered by NVIDIA Nemotron & Tavily Search on Nebius Token Factory.</div>', unsafe_allow_html=True)

# Input Area for the user's claim or article
user_claim = st.text_area(
    "Enter a claim, viral headline, or news excerpt to verify:",
    placeholder="e.g., NASA confirms discovery of ancient alien structure under Antarctic ice sheet...",
    height=120
)

# Columns for Action Buttons and Verification Settings
col_btn1, col_btn2, col_spacer = st.columns([1.5, 1.5, 5])

with col_btn1:
    verify_clicked = st.button("🔍 Verify Claim", type="primary", use_container_width=True)

with col_btn2:
    batch_mode = st.checkbox("Batch Article Mode", help="Extracts and verifies multiple sub-claims automatically")

# ---------------------------------------------------------
# Verification Execution (Placeholder for Stages 1-4)
# ---------------------------------------------------------
if verify_clicked:
    if not user_claim.strip():
        st.warning("⚠️ Please enter a claim or news excerpt before running verification.")
    else:
        st.info("🚀 Verification pipeline initialized...")
        
        # Simulated Progress Bar showing our 4-stage pipeline
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Stage 1: Extraction
        status_text.text("⚡ Stage 1/4: Extracting atomic claims via NVIDIA Nemotron Nano...")
        progress_bar.progress(25)
        
        # Stage 2: Retrieval
        status_text.text("🌐 Stage 2/4: Querying live authoritative sources via Tavily AI...")
        progress_bar.progress(50)
        
        # Stage 3: Cross-Referencing
        status_text.text("⚖️ Stage 3/4: Cross-referencing evidence via NVIDIA Nemotron 3 Ultra...")
        progress_bar.progress(75)
        
        # Stage 4: Verdict
        status_text.text("📊 Stage 4/4: Synthesizing confidence scorecard...")
        progress_bar.progress(100)
        
        st.success("✅ Verification Complete! (Pipeline skeleton active — connecting live models next)")
        
        # Temporary Preview Cards
        col_res1, col_res2, col_res3 = st.columns(3)
        with col_res1:
            st.metric(label="Verdict", value="🔴 DEBUNKED", delta="High Confidence")
        with col_res2:
            st.metric(label="Confidence Score", value="94%")
        with col_res3:
            st.metric(label="Sources Cross-Examined", value="8 Live Sources")