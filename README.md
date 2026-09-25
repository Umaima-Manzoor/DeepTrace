<div align="center">

# 🛰️ DeepTrace
### Autonomous Fact-Checking & Misinformation Radar

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Nebius Token Factory](https://img.shields.io/badge/Inference-Nebius%20Token%20Factory-8A2BE2.svg)](https://nebius.com)
[![NVIDIA Nemotron](https://img.shields.io/badge/LLM-NVIDIA%20Nemotron-76B900.svg)](https://www.nvidia.com)
[![Tavily AI](https://img.shields.io/badge/Search-Tavily%20AI-00C7B7.svg)](https://tavily.com)

**Built for the Nebius x NVIDIA Global AI Hackathon (Track 2: Best Apps and Agents)**

[🚀 Live Demo (Coming Soon)](#) • [📹 Video Presentation (Coming Soon)](#) • [🏗️ System Architecture](#-system-architecture) • [⚡ Quick Start](#-quick-start)

</div>

---

## 📌 Problem & Vision

In 2026, AI-generated synthetic content, hallucinations, and out-of-context claims travel across the web in seconds. Human fact-checking takes hours or days, creating a critical information gap where false narratives anchor before they are debunked.

**DeepTrace** is an autonomous verification agent designed to close this gap in real time. It accepts any raw claim or news article, decomposes it into atomic factual propositions, searches live authoritative sources across the web via **Tavily**, and performs deep logical cross-referencing and stance analysis powered by **NVIDIA Nemotron 3 Ultra** on **Nebius Token Factory**.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    A[User Input: Raw Claim / Article] --> B[Stage 1: Claim Decomposition]
    B -->|NVIDIA Nemotron Nano| C[Structured Atomic Claims]
    C --> D[Stage 2: Live Multi-Angle Retrieval]
    D -->|Tavily AI Search API| E[Tier-Ranked Live Web Evidence]
    E --> F[Stage 3: Deep Cross-Referencing & Stance Analysis]
    F -->|NVIDIA Nemotron 3 Ultra via Nebius| G[Contradiction & Consensus Synthesis]
```
    G --> H[Stage 4: Confidence Scorecard & Evidence Breakdown]
## ✨ Core Features

 - 🎯 **Atomic Claim Decomposition:** Extracts verifiable factual assertions from complex text using NVIDIA Nemotron Nano to ensure focused, high-precision searches.
 - 🌐 **Authoritative Live Retrieval:** Uses Tavily Search API to query 8–10 independent, live web sources filtered for domain authority.
 - ⚖️ **Logical Stance & Contradiction Detection:** Leverages NVIDIA Nemotron 3 Ultra hosted on Nebius Token Factory to evaluate supporting vs. contradicting evidence.
 - 🏷️ **Misinformation Taxonomy:** Classifies debunked claims by deceit type (Cherry-Picking, Out of Context, Fabricated Data, False Attribution).
 - 📊 **Explainable Scorecard:** Generates transparent, color-coded confidence verdicts (🟢 Verified | 🟡 Disputed | 🔴 Debunked | ⚪ Unverifiable) with source attribution.
Bash
## 🛠️ Tech Stack & Infrastructure

| Layer | Component | Description |
|---|---|---|
| Cloud Inference | Nebius Token Factory | High-performance hosted endpoint for Nemotron LLMs |
| Deep Reasoning | NVIDIA Nemotron 3 Ultra | Complex cross-referencing, nuance detection, and verdict synthesis |
| Fast Preprocessing | NVIDIA Nemotron Nano | Fast claim extraction and lightweight query parsing |
| Search Engine | Tavily AI | Agentic web search engine optimized for AI grounding |
| Dashboard UI | Streamlit | Responsive, dark-themed fact-checking dashboard |
| Core Runtime | Python 3.10+ | Modular agentic verification pipeline |

## ⚡ Quick Start

### 1. Clone the repository

```bash

git clone https://github.com/Umaima-Manzoor/DeepTrace.git
```

### 2. Create and activate a virtual environment
Bash
```bash

```
python -m venv venv
Activate it in PowerShell:

```powershell
# Windows (PowerShell):
```
.\venv\Scripts\Activate.ps1
Or in Command Prompt:

```bat
# Windows (Command Prompt):
```

### 3. Install dependencies
Bash
```bash

```

### 4. Configure environment variables

Copy `.env.example` to `.env` and add your Nebius and Tavily API keys:
Copy .env.example to .env and fill in your Nebius and Tavily API keys:
```powershell
Bash
```

### 5. Launch the dashboard
5. Launch the Dashboard
```bash
Bash
```

## 🏆 Hackathon Alignment & Judging Criteria

- **Technological Implementation:** Dual-model architecture utilizing high-reasoning NVIDIA Nemotron 3 Ultra and lightweight Nemotron Nano hosted on Nebius Token Factory.
- **Design & Experience:** Interactive Streamlit cockpit providing real-time verification progress, side-by-side evidence analysis, and transparent citations.
- **Potential Impact:** Direct countermeasure against viral AI hallucinations and digital misinformation with zero user friction.
- **Bonus Award Eligibility:** Deeply integrated with Tavily AI Search API for grounding dynamic research loops.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

<div align="center">

Built with 💚 by <b>Umaima Manzoor</b> for the 2026 Nebius x NVIDIA Global AI Hackathon.

</div>

<div align="center"> Built with 💚 by <b>Umaima Manzoor</b> for the 2026 Nebius x NVIDIA Global AI Hackathon. </div> ```