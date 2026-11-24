# 🚀 Project NOVA (Neural Orchestrator for Verified Answers)

> **An intelligent, local-first hybrid AI assistant that dynamically orchestrates pretrained model knowledge, real-time web retrieval, noise-free content extraction, and claim-level verification with traceable citations.**

[![Python 3.13](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Runtime-Ollama%20(Local)-orange.svg)](https://ollama.com/)
[![Zero API Keys](https://img.shields.io/badge/Cost-100%25%20Free%20(Zero%20API%20Keys)-green.svg)]()
[![Architecture](https://img.shields.io/badge/Design-Pluggable%20Model%20Socket-purple.svg)]()

---

## 📌 Executive Overview

Standard conversational chatbots suffer from three fundamental flaws:
1. **Hallucination on Current Events**: Relying purely on static parametric training weights past their knowledge cutoff.
2. **Blind Web Searching**: Searching the web on *every single prompt*, causing high latency, API costs, and degraded answers on static math, logic, and coding.
3. **Untraceable Answers**: Stating facts without verifiable, claim-by-claim citations.

**Project NOVA** solves this using an **Intelligent Query Routing (IQR)** engine inspired by state-of-the-art research (**Adaptive-RAG**, **Self-RAG**, and **Corrective RAG (CRAG)**). NOVA evaluates the user's intent, knowledge volatility, and temporal dependency before deciding whether to answer directly from internal model memory, search the live web, or retrieve private local documents.

---

## 🎯 The Core Vision: Future-Proof Proprietary LLM Socket

> **Primary Architectural Principle:**
> NOVA is designed as an outer **Knowledge Orchestration & Verification Shell**. 
> All language model interactions are decoupled through an abstract base class (`core/base_model.py: BaseLLMAdapter`).
>
> * **Today**: Powered locally by open-weight models (`Qwen 2.5 1.5B` & `Qwen 2.5 3B`) via Ollama on local CPU/GPU with **zero paid APIs**.
> * **Tomorrow**: When you train and develop your own proprietary PyTorch transformer LLM, you simply implement `BaseLLMAdapter` in `models/proprietary_adapter.py`. **NOVA's router, search engine, web scraper, and citation verifier will drive your custom LLM with zero code rewrites!**

---

## 🏗️ System Architecture

```
                                  ┌───────────────────────────────┐
                                  │       User Natural Query      │
                                  └───────────────┬───────────────┘
                                                  │
                                                  ▼
                               ┌─────────────────────────────────────┐
                               │   Intelligent Query Router (HMSQR)  │
                               │   • Tier 0: Deterministic (0ms)     │
                               │   • Tier 1: Semantic SLM (120ms)    │
                               │   • Tier 2: Hard Policy Gatekeeper  │
                               └──────────┬───────────────┬──────────┘
                                          │               │
                 [STATIC / CONCEPTUAL]    │               │    [DYNAMIC / TIME-SENSITIVE]
                 Volatility: VERY_LOW     │               │    Volatility: HIGH / EXTREME
                                          │               │
                                          ▼               ▼
                                   ┌──────────────┐ ┌───────────────────────────────────┐
                                   │ Internal LLM │ │ Live Dual-Channel Search (ddgs)   │
                                   │ (Direct Gen) │ │ • News channel (Real-time events) │
                                   └──────────────┘ │ • Web channel (General lookups)   │
                                                    └─────────────────┬─────────────────┘
                                                                      │
                                                                      ▼
                                                    ┌───────────────────────────────────┐
                                                    │ Parallel Noise-Free Extractor     │
                                                    │ (Trafilatura + Boilerplate Strip) │
                                                    └─────────────────┬─────────────────┘
                                                                      │
                                                                      ▼
                                                    ┌───────────────────────────────────┐
                                                    │ Grounded Synthesizer with Citations│
                                                    │ Inline claim mapping: [1], [2]    │
                                                    └─────────────────┬─────────────────┘
                                                                      │
                                                                      ▼
                                                    ┌───────────────────────────────────┐
                                                    │ Verified Grounded Response + URLs │
                                                    └───────────────────────────────────┘
```

---

## ⚡ Key Features

* **3-Tier Cascading Router (HMSQR)**:
  * **Tier 0 (0ms Latency)**: Deterministic regex heuristics for coding syntax, mathematical equations, conversational greetings, and linguistic definitions.
  * **Tier 1 (~120ms SLM Inference)**: Uses `Qwen 2.5 1.5B` to estimate **Knowledge Volatility** (`VERY_LOW` to `EXTREME`), user intent, and generates 1–3 crisp search keywords.
  * **Tier 2 (Policy Gatekeeper)**: Enforces hard policies for breaking news, recent years (`2025-2029`), and leadership roles (`who is new mentor/CEO`).
* **100% Free Live Web Search (Zero API Keys)**:
  * Dual-channel search via `ddgs` (News Channel for live financial prices/cricket/news + Text Channel for general pages).
  * Automatically removes tracking parameters (`utm_*`, `fbclid`) and filters out spam redirect domains.
* **Parallel High-Fidelity Article Extractor**:
  * Uses **Trafilatura** and **BeautifulSoup** to strip ads, cookie banners, navigation bars, and footer junk.
  * Multi-threaded fetching: extracts 3–4 full web articles concurrently in **under 2 seconds**.
* **Grounded Answer Synthesis with Citations**:
  * Strict system prompt ensures every factual claim cites its supporting evidence with bracketed markers (`[1]`, `[2]`).
  * Honest abstention: If retrieved pages lack sufficient evidence, NOVA explicitly communicates uncertainty instead of hallucinating.
* **Autonomous Dataset Logging**:
  * Every routing decision is automatically saved as JSONL in `data/routing_dataset.jsonl` to build a curated training dataset for fine-tuning future models.

---

## 📂 Repository Structure

```text
carrot.webtool/
├── config.py                     # Central Pydantic settings & model configurations
├── requirements.txt              # Core lightweight dependencies
├── .gitignore                    # Git tracking rules (ignores venv, caches, data logs)
├── README.md                     # Comprehensive documentation
├── main.py                       # Interactive CLI orchestrator (REPL)
│
├── core/
│   ├── __init__.py
│   └── base_model.py             # Abstract Base Class (BaseLLMAdapter) - The Custom LLM Socket
│
├── models/
│   ├── __init__.py
│   └── ollama_adapter.py         # Ollama driver (Qwen 2.5 1.5B/3B, Nomic-Embed) with JSON repair
│
├── intelligence/
│   ├── __init__.py
│   ├── schemas.py                # Pydantic schemas (RouteType, Volatility, RoutingDecision)
│   ├── signals.py                # Tier 0 Deterministic Heuristics (Code, Math, Greetings, Time)
│   └── router.py                 # Multi-Tier Intelligent Query Router (HMSQR Engine)
│
├── retriever/
│   ├── __init__.py
│   ├── models.py                 # SearchResult and ExtractedDocument schemas
│   ├── web_search.py             # Dual-channel live search engine (ddgs)
│   └── extractor.py              # Parallel Trafilatura article scraper & cleaner
│
├── tests/
│   ├── __init__.py
│   ├── test_model_adapter.py     # Verifies OllamaAdapter generation, JSON schema & embeddings
│   ├── test_router.py            # 8/8 Automated Benchmark Suite for Query Routing (100% Pass)
│   └── test_retrieval.py         # Live DuckDuckGo search & parallel extraction benchmark
│
└── data/
    ├── .gitkeep
    └── routing_dataset.jsonl     # Automatically logged routing traces for future model training
```

---

## 🛠️ Technology Stack

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Language** | **Python 3.13+** | Native async support, typing, and modern AI libraries. |
| **Local Runtime** | **Ollama (0.40+)** | C++ based local inference engine (Zero API cost, CPU-optimized). |
| **Router SLM** | **Qwen 2.5 (1.5B)** | Ultra-fast (~120ms) CPU structured JSON classification. |
| **Synthesizer LLM** | **Qwen 2.5 (3B)** | High-quality reasoning, adherence to citation rules, low RAM footprint (~3GB). |
| **Vector Embeddings** | **Nomic-Embed-Text** | 768-dimensional local dense embeddings for semantic search. |
| **Search Engine** | **ddgs (DuckDuckGo)** | Zero-cost, zero API key live internet search gateway. |
| **Content Extractor**| **Trafilatura + BeautifulSoup** | Gold standard for boilerplate stripping and clean article text extraction. |
| **Schema Validation**| **Pydantic v2** | Strict data contracts and JSON schema enforcement. |

---

## 🚀 Quickstart Guide

### 1. Prerequisites
1. **Ollama**: Download and install from [ollama.com](https://ollama.com/download).
2. Pull the required local models:
   ```powershell
   ollama pull qwen2.5:1.5b
   ollama pull qwen2.5:3b
   ollama pull nomic-embed-text
   ```

### 2. Setup Environment
Clone the repository and set up a Python virtual environment:
```powershell
git clone https://github.com/harsh3011dev-oops/carrot.webtool.git
cd carrot.webtool

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💻 How to Run Project NOVA

### Launch the Interactive Chat Assistant
```powershell
python main.py
```

#### Example 1: Static Concept (Zero Search Call, ~1s Latency)
```text
Ask NOVA >> give me code for palindrome in python

[ROUTER DECISION]
  • Primary Route   : INTERNAL_LLM
  • Tier Decision   : TIER_0_RULES (0.00s)
  • Volatility      : LOW
  • Time Sensitive  : False

[INTERNAL GENERATION] (Zero search cost)
NOVA Response:
def is_palindrome(s):
    s = ''.join(char.lower() for char in s if char.isalnum())
    return s == s[::-1]
```

#### Example 2: Live Breaking Event (Live Web Retrieval + Citations)
```text
Ask NOVA >> who is new mentor of chennai super kings?

[ROUTER DECISION]
  • Primary Route   : WEB_SEARCH
  • Tier Decision   : TIER_2_POLICY_OVERRIDE
  • Volatility      : MEDIUM
  • Time Sensitive  : True

[LIVE WEB SEARCH] -> Searching keywords: ['Chennai Super Kings new mentor']
  • Found 3 relevant sources. Extracting clean content...
  • Extracted 3 web pages in 1.46s

NOVA Grounded Response (With Citations):
Mahendra Singh Dhoni has been appointed as the new mentor of Chennai Super Kings. [1] [2] [3]
According to the sources, Mahendra Singh Dhoni, who has ended his 19-year IPL career, will be joining Chennai Super Kings as their team mentor for the 2027 season. [2] [3] 

Verified Sources:
  [1] Chennai Super Kings Official Announcement on X
  [2] MS Dhoni ends IPL career, joins CSK as mentor | Cricinfo
  [3] MS Dhoni retires from IPL, becomes Chennai Super Kings mentor | India Today
```

---

## 🧪 Running the Automated Benchmarks

Verify system components independently with the included test suites:

1. **Test Model Socket & Structured JSON Output**:
   ```powershell
   python tests/test_model_adapter.py
   ```
2. **Test Intelligent Query Routing (8/8 Test Benchmark)**:
   ```powershell
   python tests/test_router.py
   ```
3. **Test Live Web Search & Parallel Article Extraction**:
   ```powershell
   python tests/test_retrieval.py
   ```

---

## 📅 Development Roadmap (3-Day Fast Track)

* [x] **Day 1: Foundation, Pluggable Model Socket, Query Router & Live Web Engine**
  * Local Ollama integration (`qwen2.5:1.5b` & `3b`).
  * `BaseLLMAdapter` abstract socket for your future custom model.
  * Cascading Intelligent Query Router (HMSQR) with 100% benchmark score.
  * Free Live Web Search (`ddgs`) & Parallel Trafilatura extractor.
  * Interactive CLI orchestrator (`main.py`).
* [ ] **Day 2: Grounding, Local RAG & Verification Engine**
  * FAISS local vector store + Nomic-Embed text ingestion.
  * Cross-Encoder Reranker (`FlashRank` on local CPU).
  * Claim-level Fact Verification & Contradiction Detection (The "V" in NOVA).
* [ ] **Day 3: Interactive UI & Custom Model Socket Testing**
  * Streamlit web interface with live thought traces & citation sidebars.
  * Custom PyTorch Model Plug-and-Play demo script.
  * FastAPI REST API endpoints.

---

## 📜 License & Citation
Project NOVA is developed as an open-source, local-first research initiative for verified AI assistance.
Developed with ❤️ by Harsh.

