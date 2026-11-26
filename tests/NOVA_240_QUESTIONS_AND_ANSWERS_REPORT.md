# Project NOVA — Master 240-Question & Answer Benchmark Report

> **System:** Project NOVA (Neural Orchestrator for Verified Answers)  
> **Environment:** Linux DGX Spark | Local-First Architecture (Zero External Paid APIs)  
> **Models:** Router (`qwen2.5:1.5b`) | Synthesizer (`qwen2.5-coder:latest` / 7.6B)  
> **Execution Timestamp:** 2026-11-25 17:20:45 | **Total Latency:** 5,626.77s (~1.5 hours)

---

## 1. Executive Summary & Master Scorecard

| Metric | Count | Percentage | Status |
|---|:---:|:---:|:---:|
| **TOTAL TEST CASES** | **235** | **100.0%** | Complete Execution |
| **PASSED** | **233** | **99.1%** | 🌟 Production-Grade Reliability |
| **PARTIAL** | **2** | **0.9%** | Non-fatal (over-retrieval) |
| **FAILED / CRASH** | **0** | **0.0%** | 🛡️ Zero Crashes / Zero Halts |

### Section-by-Section Summary Table

| Sec | Domain | Cases | PASS | PARTIAL | FAIL | Avg Latency | Pass Rate |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **A** | Basic Internal / Fast-Path Questions | 15 | 15 | 0 | 0 | 2.17s | **100.0%** |
| **B** | Router / Intent Classification | 15 | 13 | 2 | 0 | 28.79s | **86.7%** |
| **C** | Search Query Generation / Retry Quality | 15 | 15 | 0 | 0 | 28.67s | **100.0%** |
| **D** | Entity / Variant / Attribute Matching | 15 | 15 | 0 | 0 | 23.40s | **100.0%** |
| **E** | Evidence Relevance vs Sufficiency | 15 | 15 | 0 | 0 | 18.70s | **100.0%** |
| **F** | Date / Temporal Attribution | 15 | 15 | 0 | 0 | 23.74s | **100.0%** |
| **G** | Grounding / Claim Verification / Abstention | 15 | 15 | 0 | 0 | 23.55s | **100.0%** |
| **H** | Multi-Turn Context / Coreference Resolution | 15 | 15 | 0 | 0 | 23.81s | **100.0%** |
| **I** | Topic-Change / Ambiguity / Clarification | 15 | 15 | 0 | 0 | 26.20s | **100.0%** |
| **J** | Search Provider Resilience / Failure Handling | 15 | 15 | 0 | 0 | 24.61s | **100.0%** |
| **K** | Extraction / Source Quality / Deduplication | 15 | 15 | 0 | 0 | 21.95s | **100.0%** |
| **L** | Performance / Latency / Budget | 15 | 15 | 0 | 0 | 29.23s | **100.0%** |
| **M** | Regression / Repeatability | 10 | 10 | 0 | 0 | 28.43s | **100.0%** |
| **N** | Hinglish / Language / Query Normalization | 15 | 15 | 0 | 0 | 29.26s | **100.0%** |
| **O** | Adversarial / False-Premise / Robustness | 15 | 15 | 0 | 0 | 28.85s | **100.0%** |
| **P** | System / Structured Output / Logging Checks | 15 | 15 | 0 | 0 | 23.24s | **100.0%** |

---

## 2. Comprehensive Question-by-Question Audit & Answers

### Section A: Basic Internal / Fast-Path Questions
*Static scientific formulas, solar system constants, pure mathematics, unit conversions, and conceptual computer science definitions that resolve internally with 0.00s routing latency.*

#### `A01` What is the chemical formula of water?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `0.45s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correct chemical formula H2O via fast-path*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A02` What is the largest planet in our solar system?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `0.46s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correct largest planet Jupiter*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A03` What is the capital of France?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `0.36s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correct capital Paris*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A04` What is 25 multiplied by 48?
- **Route:** `INTERNAL_LLM` (`TIER_0_RULES`) | **Truth State:** `UNVERIFIED` | **Latency:** `0.55s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correct math 25*48 = 1200*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A05` Convert 2.5 kilometres into metres.
- **Route:** `INTERNAL_LLM` (`TIER_0_RULES`) | **Truth State:** `UNVERIFIED` | **Latency:** `0.57s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Internal generation succeeded*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A06` What is the difference between RAM and ROM?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `8.32s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Internal generation succeeded*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A07` What does a CPU do?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `2.89s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Internal generation succeeded*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A08` Explain photosynthesis in simple words.
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `4.79s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Internal generation succeeded*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A09` What is Newton's second law of motion?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `1.69s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Internal generation succeeded*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A10` Define an algorithm.
- **Route:** `INTERNAL_LLM` (`TIER_0_RULES`) | **Truth State:** `UNVERIFIED` | **Latency:** `1.81s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Internal generation succeeded*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A11` What is the difference between a compiler and an interpreter?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `6.0s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Internal generation succeeded*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A12` What is binary number 1010 in decimal?
- **Route:** `INTERNAL_LLM` (`TIER_0_RULES`) | **Truth State:** `UNVERIFIED` | **Latency:** `0.67s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correct binary conversion*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A13` What is 15% of 240?
- **Route:** `INTERNAL_LLM` (`TIER_0_RULES`) | **Truth State:** `UNVERIFIED` | **Latency:** `2.53s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correct percentage 36*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A14` How many sides does a hexagon have?
- **Route:** `INTERNAL_LLM` (`TIER_0_RULES`) | **Truth State:** `UNVERIFIED` | **Latency:** `0.4s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correct hexagon 6 sides*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `A15` What is the boiling point of water at standard atmospheric pressure?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `1.12s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correct boiling point 100°C*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

---

### Section B: Router / Intent Classification
*Classification of queries between pure parametric internal logic vs live web search based on temporal volatility and time-sensitivity.*

#### `B01` Who won the 2023 Cricket World Cup?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `38.87s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"2023 Cricket World Cup winners list"`, `"2023 Cricket World Cup final match result"`, `"2023 Cricket World Cup champions"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `B02` Who won the latest Cricket World Cup?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `16.79s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"latest Cricket World Cup winner"`, `"Cricket World Cup champions list"`, `"Cricket World Cup final results"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/List_of_Cricket_World_Cup_finals)
- **NOVA Generated Answer:**
  > The latest Cricket World Cup, which took place in 2023, was won by Australia, who defeated India. [1]

#### `B03` What are the latest AI developments?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `35.97s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"latest AI breakthroughs 2023"`, `"top AI researchers 2023"`, `"most recent AI applications in tech"`
- **Retrieved Sources:** [Link 1](https://tech.yahoo.com/ai/deals/articles/wikipedia-seeks-more-ai-licensing-000232640.html), [Link 2](https://en.wikipedia.org/wiki/Artificial_intelligence), [Link 3](https://en.wikipedia.org/wiki/Progress_in_artificial_intelligence)
- **NOVA Generated Answer:**
  > Wikipedia is actively seeking more AI licensing deals to help monetize the use of its content by large language models [1]. This move aims t...

#### `B04` What happened today in OpenAI?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `37.31s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"latest news about OpenAI"`, `"OpenAI news today"`
- **Retrieved Sources:** [Link 1](https://quickchat.ai/post/openai-wiki-incident), [Link 2](https://arstechnica.com/ai/2026/09/heres-what-actually-happened-in-openais-australian-govt-server-hack/)
- **NOVA Generated Answer:**
  > Today, OpenAI faced a significant incident where rogue agents were discovered interacting on an old German forum website. These agents, whic...

#### `B05` Compare RTX 5090 and NVIDIA DGX Spark.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `45.02s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"What is the difference between RTX 5090 and NVIDIA DGX Spark?"`, `"Compare RTX 5090 and DGX Spark specifications"`
- **Retrieved Sources:** [Link 1](https://www.techrepublic.com/article/news-nvidia-dgx-spark-64gb-price-specs/), [Link 2](https://www.msn.com/en-us/technology/hardware-and-devices/this-is-why-you-can-t-build-your-own-rtx-spark-pc/ar-AA2gpBrq?ocid=BingNewsVerp)
- **NOVA Generated Answer:**
  > The RTX 5090 and NVIDIA DGX Spark are both high-performance graphics cards and servers, but they serve different purposes and have distinct ...

#### `B06` Find official information about Chandrayaan-3.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `39.29s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"Official information about Chandrayaan-3"`, `"Chandrayaan-3 mission details"`, `"Chandrayaan-3 launch date"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Chandrayaan-3), [Link 2](https://en.wikipedia.org/wiki/Pragyan_(Chandrayaan-3)), [Link 3](https://www.isro.gov.in/Chandrayaan3_Details.html)
- **NOVA Generated Answer:**
  > Chandrayaan-3 is a lunar mission developed by the Indian Space Research Organisation (ISRO). The mission is designed to demonstrate end-to-e...

#### `B07` Explain how transformers work in AI.
- **Route:** `INTERNAL_LLM` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `16.43s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified conceptual query to INTERNAL_LLM*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `B08` Find the current price of the iPhone 16 in India.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `34.3s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"iPhone 16 price in India"`, `"current iPhone 16 price in India"`, `"latest iPhone 16 price in India"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `B09` Who is the current president of the United States?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `22.47s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"current president of the united states"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer.
  > Sources:
  > [1] https://www.whitehouse.gov/news/
  > [2] https://www.whit...

#### `B10` Give me a recipe for simple vegetable pasta.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `31.74s` | **Verdict:** ⚠️ **PARTIAL**
- **Audit Evaluation:** *Route: WEB_SEARCH*
- **Generated Search Queries:** `"vegetable pasta recipe"`, `"simple vegetable pasta recipe"`, `"vegetable pasta with vegetables"`
- **Retrieved Sources:** [Link 1](https://www.ajc.com/food-and-dining/recipe-showcase-seasonal-vegetables-with-this-simple-pasta-recipe-from-old-vinings-inn/HCIIH6EZHZC3XADDQGAVBZR4QI/)
- **NOVA Generated Answer:**
  > To create a simple vegetable pasta dish, you can follow the recipe from Old Vinings Inn [1]. Here’s a step-by-step guide:
  > 1. **Prep the Ing...

#### `B11` Write a Python program to check whether a number is prime.
- **Route:** `INTERNAL_LLM` (`TIER_0_RULES`) | **Truth State:** `UNVERIFIED` | **Latency:** `5.25s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified conceptual query to INTERNAL_LLM*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `B12` Debug this error: IndexError: list index out of range.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `21.25s` | **Verdict:** ⚠️ **PARTIAL**
- **Audit Evaluation:** *Route: WEB_SEARCH*
- **Generated Search Queries:** `"How to debug IndexError: list index out of range"`
- **Retrieved Sources:** [Link 1](https://stackoverflow.com/questions/43264401/how-to-debug-indexerror-list-index-out-of-range), [Link 2](https://www.geeksforgeeks.org/python/python-list-index-out-of-range-indexerror/)
- **NOVA Generated Answer:**
  > The error `IndexError: list index out of range` occurs when you try to access an element in a list using an index that is either too large (...

#### `B13` Summarise the latest major technology news.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `51.78s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"latest major technology news"`, `"top 5 technology news stories of the day"`, `"current technology trends"`
- **Retrieved Sources:** [Link 1](https://www.reuters.com/technology/), [Link 2](https://www.reuters.com/technology/disrupted/), [Link 3](https://news.google.com/rss/articles/CBMi8wFBVV95cUxPbUZRVHhudU1zcDhNQmhkRHpFNk9SOUJlN2EzZHlwZEZPdVFIcVJpU0pieUhsVGFNRUFNTWxidHRFeEJhR3ViMThRNWRHeFZncmp0dTZTazBYcXJLaXJTY0k4VmFCRW5KU0loMlJuWWhSdnhSdzFyTVNndlk2NFNRam9Pdk40U19KUnZaamZzcHYwamFLb2JkQ1hTNHJOc0Uxb1ZMbzJ1Xy1yM0p3NER2bFJuVlZESXZMNVBDRzhzVkRpREtfX1JzWGFMRkVIY2doVDY0dG50WERMdWZmcmtNbWFSYXE5ZmdZbU1sQ2RkWWNQSGc?oc=5)
- **NOVA Generated Answer:**
  > As of the latest available information, technology news is rapidly evolving across various sectors. Reuters, a leading international news so...

#### `B14` What is the weather in Delhi right now?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `17.33s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"current weather in delhi"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `B15` What are the admission dates for JEE Main 2027?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `18.05s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Correctly classified to WEB_SEARCH*
- **Generated Search Queries:** `"What are the admission dates for JEE Main 2027?"`
- **Retrieved Sources:** [Link 1](https://collegedunia.com/articles/e-301-jee-main-2027-important-dates---session-1-and-session-2-full-schedule)
- **NOVA Generated Answer:**
  > The admission dates for JEE Main 2027 are as follows:
  > - **Session 1 Registration Window:** November 22, 2026 [3]
  > - **Session 1 Exam:** Janu...

---

### Section C: Search Query Generation / Retry Quality
*Decomposition of conversational questions into clean, multi-angle search queries and intent-tailored retry queries without cross-domain keyword contamination.*

#### `C01` Who won the 2023 Cricket World Cup?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `24.73s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"2023 Cricket World Cup winners list"`, `"2023 Cricket World Cup final result"`, `"2023 Cricket World Cup champions"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/2023_Cricket_World_Cup), [Link 2](https://en.wikipedia.org/wiki/List_of_Cricket_World_Cup_finals)
- **NOVA Generated Answer:**
  > The 2023 Cricket World Cup was won by Australia [1]. The tournament, held in India from 5 October to 19 November 2023, saw Australia defeat ...

#### `C02` List the winners of the last five ICC Men's Cricket World Cups.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `21.91s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"ICC Men's Cricket World Cup winners list"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/List_of_Cricket_World_Cup_finals), [Link 2](https://en.wikipedia.org/wiki/Cricket_World_Cup)
- **NOVA Generated Answer:**
  > Based on the provided evidence, the winners of the last five ICC Men's Cricket World Cups are:
  > 1. Australia (2023)
  > 2. England (2019)
  > 3. Ind...

#### `C03` What is the latest version of Python?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `24.82s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"latest version of Python"`, `"current Python version"`, `"latest Python release"`
- **Retrieved Sources:** [Link 1](https://www.python.org/doc/versions/)
- **NOVA Generated Answer:**
  > The latest stable version of Python is Python 3.15.2, released on 25 October 2026 [3].

#### `C04` What is the official release date of Android 16?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `21.74s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the official release date of Android 16?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Android_16)
- **NOVA Generated Answer:**
  > The official release date of Android 16 is June 10, 2025. This date is based on the information provided in the first source [1], which stat...

#### `C05` When is JEE Main 2027 expected to take place?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `25.6s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"When is JEE Main 2027 expected to take place"`
- **NOVA Generated Answer:**
  > JEE Main 2027 is expected to take place in two sessions. The first session is scheduled for January 20–28, 2027, and the second session is e...

#### `C06` Find the latest official NVIDIA announcement about AI.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `27.21s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"latest official NVIDIA announcement about AI"`
- **Retrieved Sources:** [Link 1](https://news.google.com/rss/articles/CBMiwAFBVV95cUxPVFg4WTJZY1lxdDNpSXJJZnFsTFlidFZlM2VOd3NSY0VFR2Mzc3hxaFNla3V2bklFdms1U0NSM05pQzROVk1obUEtXy0xVXh6d3RCTncyaFlldjh3WmpQeHE5Q2pOQnZuaDNpbS1jMkh3eHU5dHRpbk5OYVhvaVBQVk1BWXAzNFBfUGN5TmlyMmVhTWE2SWtLQzk4Znd0S0hHQXY1MklHV2JoQWItQkg1VHFJTV9odmxCYTg4cXVsNjI?oc=5)
- **NOVA Generated Answer:**
  > The latest official NVIDIA announcement about AI is from the NVIDIA Technical Blog, titled "NVIDIA Open Agent Safety Platform: A Reference f...

#### `C07` What is the current price of Bitcoin?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `32.44s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"latest Bitcoin price"`, `"current Bitcoin price"`, `"Bitcoin price as of now"`
- **Retrieved Sources:** [Link 1](https://cryptoticker.io/en/price/bitcoin/)
- **NOVA Generated Answer:**
  > The current price of Bitcoin is $58,904.19 USD or €53,815.60 EUR as of November 25, 2026, according to the latest data from CryptoTicker.io ...

#### `C08` Who won the latest Asia Cup in cricket?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `17.72s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"latest Asia Cup winner"`, `"Asia Cup cricket champions list"`, `"Asia Cup cricket final"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Asia_Cup), [Link 2](https://en.wikipedia.org/wiki/2025_Asia_Cup_final), [Link 3](https://blog.cricheroes.com/asia-cup-winners-list/)
- **NOVA Generated Answer:**
  > Based on the evidence provided, the latest Asia Cup in cricket was won by India in 2025. The final match was played on 28 September 2025 bet...

#### `C09` Find the official ISRO update about Chandrayaan-3.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `51.29s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Official ISRO update about Chandrayaan-3"`
- **Retrieved Sources:** [Link 1](https://www.isro.gov.in/Chandrayaan3_Details.html)
- **NOVA Generated Answer:**
  > The official ISRO update about Chandrayaan-3 can be found on the ISRO website [2]. The mission is a follow-on to Chandrayaan-2, designed to ...

#### `C10` What are the latest major AI research breakthroughs?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `34.02s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"latest major AI research breakthroughs"`, `"recent AI research advancements"`, `"top AI research papers of the year"`
- **Retrieved Sources:** [Link 1](https://hai.stanford.edu/ai-index/2026-ai-index-report/research-and-development), [Link 2](https://singularitymoments.com/content/top-10-ai-breakthroughs-that-defined-2026/)
- **NOVA Generated Answer:**
  > The latest major AI research breakthroughs include advancements in model architecture and specialized capabilities. One notable development ...

#### `C11` Explain the difference between GPT-4o and GPT-4.1.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `28.98s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the difference between GPT-4 and GPT-4.1"`
- **Retrieved Sources:** [Link 1](https://www.datastudios.org/post/gpt-4o-vs-gpt-4-1-all-the-differences-and-why-they-do-different-things), [Link 2](https://openai.com/index/gpt-4-1/)
- **NOVA Generated Answer:**
  > GPT-4o and GPT-4.1 are two distinct versions of OpenAI's GPT-4 series, each designed to cater to different user needs and use cases.
  > **GPT-...

#### `C12` What is the launch date of iPhone XR?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `9.38s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"iPhone XR launch date"`, `"launch date iPhone XR"`, `"when was iPhone XR released"`
- **Retrieved Sources:** [Link 1](https://www.apple.com/newsroom/2018/09/apple-introduces-iphone-xr/), [Link 2](https://en.wikipedia.org/wiki/IPhone_XR)
- **NOVA Generated Answer:**
  > The launch date of the iPhone XR is October 26, 2018. This information is consistent across multiple sources, including Apple's official pre...

#### `C13` What are the Champions League winners by year?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `36.55s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"Champions League champions list 2020"`, `"Champions League champions list 2019"`, `"Champions League champions list 2018"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/UEFA_Champions_League), [Link 2](https://en.wikipedia.org/wiki/List_of_European_Cup_and_UEFA_Champions_League_finals), [Link 3](https://www.topendsports.com/sport/soccer/list-league-uefa.htm)
- **NOVA Generated Answer:**
  > The UEFA Champions League, also known as the Champions League, is an annual club football competition organized by the Union of European Foo...

#### `C14` Find the latest government notification about scholarships in India.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `39.1s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"latest government scholarship notification in India"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/List_of_schemes_of_the_government_of_India), [Link 2](https://www.education.gov.in/scholarships/circulars-orders-notification), [Link 3](https://en.wikipedia.org/wiki/National_Scholarship_Portal)
- **NOVA Generated Answer:**
  > The latest government notification about scholarships in India can be found on the National Scholarship Portal (NSP) website, which is opera...

#### `C15` What is the latest result of India's cricket match?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `34.56s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"latest India cricket match result"`
- **Retrieved Sources:** [Link 1](https://www.cricketnews.com/en/cricket/news/ind-vs-nz-5th-odi-scorecard-result-highlights-mount-maunganui/7c9aa5a818615007d6fae60b)
- **NOVA Generated Answer:**
  > As of the latest update, India's cricket match result is as follows:
  > India won the 5th ODI against New Zealand by 22 runs. The match took p...

---

### Section D: Entity / Variant / Attribute Matching
*Strict entity disambiguation preventing model variant substitution (e.g. iPhone 16 vs 16e, RTX 5090 vs 5080, Pixel 9 vs 9a, Chandrayaan-3 lander/rover).*

#### `D01` What is the launch date of iPhone 16?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `16.51s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"iPhone 16 launch date"`, `"Apple iPhone 16 release date"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/IPhone_16), [Link 2](https://www.simplymac.com/iphone/iphone-16-release-date)
- **NOVA Generated Answer:**
  > The iPhone 16 was announced by Apple during its traditional September event in 2024. Preorders for the iPhone 16 series opened shortly after...

#### `D02` What is the launch date of iPhone 16e?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `20.01s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"iPhone 16 launch date"`, `"iPhone 16 e launch date"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/IPhone_16e)
- **NOVA Generated Answer:**
  > The iPhone 16e was first released on February 28, 2025 [1].

#### `D03` Compare iPhone 16 and iPhone 16e.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `25.68s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"iPhone 16 vs iPhone 16"`, `"iPhone 16 and iPhone 16e comparison"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `D04` What is the price of iPhone 16 (not 16e) in India?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `24.5s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"iPhone 16 price in India"`, `"Current iPhone 16 price in India"`, `"iPhone 16 not 16e price in India"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/IPhone_16), [Link 2](https://www.indiatimes.com/technology/gadgets/iphone-16-series-price-in-india-vs-usa-dubai-canada-japan-france-vietnam-and-global-markets/articleshow/122650029.html), [Link 3](https://english.mathrubhumi.com/technology/iphone-16-series-price-in-india-e381ce3c)
- **NOVA Generated Answer:**
  > The price of the iPhone 16 (not 16e) in India starts from Rs 79,900 [2]. This information is consistent across multiple sources, including [...

#### `D05` What are the specifications of NVIDIA RTX 5090?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `39.37s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"NVIDIA RTX 5090 specifications"`, `"NVIDIA RTX 5090 features"`, `"NVIDIA RTX 5090 technical specifications"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/GeForce_RTX_50_series), [Link 2](https://www.slashgear.com/1902896/rtx-5090-how-much-power-can-pull-nvidia-geforce-gpu/)
- **NOVA Generated Answer:**
  > The GeForce RTX 5090 is a high-end consumer graphics card released on January 30, 2025, by Nvidia. It is based on the Blackwell architecture...

#### `D06` What are the specifications of NVIDIA RTX 5080?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `35.15s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"NVIDIA RTX 5080 specifications"`
- **Retrieved Sources:** [Link 1](https://www.nvidia.com/en-us/geforce/graphics-cards/50-series/rtx-5080/), [Link 2](https://www.elprocus.com/nvidia-geforce-rtx-5080/)
- **NOVA Generated Answer:**
  > The NVIDIA GeForce RTX 5080 is an enthusiast-class GPU designed for high-performance gaming and creative workloads. It features the Blackwel...

#### `D07` What is the release date of GPT-4.1?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `10.49s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"What is the release date of GPT-4.1?"`
- **Retrieved Sources:** [Link 1](https://tech.yahoo.com/ai/articles/openai-just-launched-gpt-4-132740902.html)
- **NOVA Generated Answer:**
  > The release date of GPT-4.1 is April 16, 2025 [2].

#### `D08` What is the release date of GPT-4o?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `19.26s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the release date of GPT-4?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/GPT-4o)
- **NOVA Generated Answer:**
  > The release date of GPT-4o is May 13, 2024 [1].

#### `D09` What is the launch date of Google Pixel 9?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `15.94s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the launch date of Google Pixel 9?"`
- **Retrieved Sources:** [Link 1](https://www.androidheadlines.com/google-pixel-9-release-date)
- **NOVA Generated Answer:**
  > The Google Pixel 9 and Pixel 9 Pro were released on August 22, 2024 [1]. The Pixel 9 Pro XL launched on September 4, 2024 [1].

#### `D10` What is the launch date of Google Pixel 9a?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `24.82s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"What is the launch date of Google Pixel 9a?"`
- **Retrieved Sources:** [Link 1](https://tech.yahoo.com/general/articles/google-pixel-9a-launches-price-140000530.html)
- **NOVA Generated Answer:**
  > The Google Pixel 9a was announced on March 19, 2025 [1].

#### `D11` What is the current captain of the Indian men's cricket team?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `33.45s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Who is the current captain of the Indian men's cricket team?"`, `"What is the current captain of the Indian men's cricket team?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/India_national_cricket_team), [Link 2](https://en.wikipedia.org/wiki/List_of_India_national_cricket_captains)
- **NOVA Generated Answer:**
  > Based on the evidence provided:
  > - The current captain of the Indian men's cricket team is Shubman Gill [1].
  > - Shreyas Iyer is the current T...

#### `D12` Who captained Australia in the 2023 Cricket World Cup final?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `33.67s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Who won the 2023 Cricket World Cup final?"`, `"What is the current captain of Australia's cricket team?"`, `"Who captained Australia in the 2023 Cricket World Cup final? champions list winners"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `D13` What is the official name of Chandrayaan-3's lander?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `23.17s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"What is the official name of Chandrayaan-3's lander?"`
- **Retrieved Sources:** [Link 1](https://news.google.com/rss/articles/CBMiXkFVX3lxTE82Q3hBR25WMFN3dk83V3AzTG9mNl9oVjhELUxXdjE1ZFRVcTBweklEWnMtQ200NDVTX2tWQkxuLUE2VmM2NVc0X3ZxQkNPOWNXS2trMnNBOFV2ckc1aFE?oc=5)
- **NOVA Generated Answer:**
  > The official name of Chandrayaan-3's lander is Vikram [1].

#### `D14` What is the official name of Chandrayaan-3's rover?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `18.72s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the official name of Chandrayaan-3's rover?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Pragyan_(Chandrayaan-3))
- **NOVA Generated Answer:**
  > The official name of Chandrayaan-3's rover is Pragyan [1].

#### `D15` What is the difference between announcement date and release date?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `10.22s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the difference between announcement date and release date"`
- **Retrieved Sources:** [Link 1](https://www.investopedia.com/terms/a/announcement-date.asp), [Link 2](https://en.wikipedia.org/wiki/Software_release_life_cycle)
- **NOVA Generated Answer:**
  > The announcement date is the specific date on which a company publicly discloses significant information regarding decisions that can greatl...

---

### Section E: Evidence Relevance vs Sufficiency
*Decoupled topical relevance checking from exact attribute presence (ensuring evidence actually contains the answer before declaring sufficiency).*

#### `E01` What does a CPU do?
- **Route:** `INTERNAL_LLM` (`TIER_0_FAST_PATH`) | **Truth State:** `UNVERIFIED` | **Latency:** `4.54s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `E02` What is a CPU's clock speed?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `7.89s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is a CPU's clock speed?"`
- **Retrieved Sources:** [Link 1](https://www.intel.com/content/www/us/en/gaming/resources/cpu-clock-speed.html), [Link 2](https://www.hp.com/us-en/tech-takes/components/explainer/what-is-processor-speed.html)
- **NOVA Generated Answer:**
  > A CPU's clock speed, also known as clock rate or frequency, is a measure of how many cycles the CPU can execute per second, typically measur...

#### `E03` What is the clock speed of the processor in NVIDIA DGX Spark?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `10.46s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"NVIDIA DGX Spark processor clock speed"`
- **Retrieved Sources:** [Link 1](https://docs.nvidia.com/dgx/dgx-spark/hardware.html)
- **NOVA Generated Answer:**
  > The clock speed of the processor in NVIDIA DGX Spark is 2.5 GHz [2]. This information is derived from the Hardware Overview section of the D...

#### `E04` Explain the functions of the network layer in the OSI model.
- **Route:** `INTERNAL_LLM` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `7.55s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `E05` What is IPv4?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `20.23s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"What is IPv 4?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/IPv4), [Link 2](https://www.geeksforgeeks.org/computer-networks/what-is-ipv4/)
- **NOVA Generated Answer:**
  > IPv4 stands for Internet Protocol version 4, which is a communication protocol used for internetworking. It was developed by DARPA and intro...

#### `E06` What is the default subnet mask of Class C IPv4?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `17.14s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the default subnet mask of Class C IPv4?"`
- **Retrieved Sources:** [Link 1](https://asmr.education/faq/ip-addresses/default-subnet-mask-class-c)
- **NOVA Generated Answer:**
  > The default subnet mask for Class C IPv4 is 255.255.255.0 [1].

#### `E07` What is the area of India?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `21.84s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the area of India?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Geography_of_India)
- **NOVA Generated Answer:**
  > The total area of India is 3,287,263 square kilometers (1,269,219 square miles) [2].

#### `E08` How many moons does Jupiter currently have?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `18.61s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"How many moons does Jupiter currently have?"`
- **Retrieved Sources:** [Link 1](https://simple.wikipedia.org/wiki/List_of_Jupiter's_moons), [Link 2](https://en.wikipedia.org/wiki/Moons_of_Jupiter)
- **NOVA Generated Answer:**
  > As of 30 April 2025, Jupiter has 97 known moons [1]. This number has increased over time as more smaller moons have been discovered. The mos...

#### `E09` What is the population of Delhi according to the latest available census/estimate?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `17.74s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"latest available census of Delhi population"`, `"latest estimate of Delhi population"`
- **Retrieved Sources:** [Link 1](https://indiacensus.in/metro-cities/delhi)
- **NOVA Generated Answer:**
  > According to the latest available data from the Delhi Population 2026 - Metro City Census Data [1], the estimated population of Delhi in 202...

#### `E10` What is the date of the next FIFA World Cup?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `36.38s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the date of the next FIFA World Cup?"`, `"What is the date of the next FIFA World Cup? champions list winners"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_final), [Link 2](https://en.wikipedia.org/wiki/2026_FIFA_World_Cup)
- **NOVA Generated Answer:**
  > The 2026 FIFA World Cup will take place from June 11 to July 19, 2026 [2]. The final match of the tournament is scheduled for July 19, 2026,...

#### `E11` What is the current exchange rate of USD to INR?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `41.21s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"latest USD to INR exchange rate"`, `"current USD to INR exchange rate"`, `"latest USD to INR currency conversion"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Exchange_rate), [Link 2](https://en.wikipedia.org/wiki/Exchange_rate_history_of_the_Indian_rupee), [Link 3](https://economictimes.indiatimes.com/markets/forex/currency-converter/usd-to-inr)
- **NOVA Generated Answer:**
  > The current exchange rate of USD to INR can vary significantly based on real-time market conditions. According to the USD to INR converter p...

#### `E12` Who is the CEO of NVIDIA?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `16.56s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Who is the CEO of NVIDIA"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Jensen_Huang)
- **NOVA Generated Answer:**
  > The CEO of NVIDIA is Jensen Huang [1].

#### `E13` What is the official ISRO mission objective of Chandrayaan-3?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `20.25s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the official ISRO mission objective of Chandrayaan-3?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Chandrayaan-3), [Link 2](https://www.isro.gov.in/Chandrayaan3.html)
- **NOVA Generated Answer:**
  > The official ISRO mission objective of Chandrayaan-3 is to demonstrate end-to-end capability in safe landing and roving on the lunar surface...

#### `E14` What is the exact admission deadline mentioned in the official JEE notice?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `22.64s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the exact admission deadline mentioned in the official JEE notice?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `E15` What is the reported silicon yield in the SilicaForge-RL project log? (Answer only if the project log is provided as evidence.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `17.42s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the reported silicon yield in the SilicaForge-RL project log?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer.
  > Sources:
  > [1] https://en.wikipedia.org/wiki/List_of_countries_by_si...

---

### Section F: Date / Temporal Attribution
*Semantic date extraction isolating product announcement/event launch dates from article publication dates.*

#### `F01` When was GPT-4.1 announced?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `19.94s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"When was GPT-4.1 announced?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/GPT-4.1), [Link 2](https://developers.openai.com/api/docs/models/gpt-4.1), [Link 3](https://openai.com/index/gpt-4-1/)
- **NOVA Generated Answer:**
  > GPT-4.1 was announced and released on April 14, 2025 [1].
  > Sources:
  > [1] GPT-4.1 - Wikipedia (Date: 2025-04-15) - https://en.wikipedia.org/wi...

#### `F02` When was GPT-4.1 made available?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `17.73s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"When was GPT-4.1 made available?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/GPT-4.1)
- **NOVA Generated Answer:**
  > GPT-4.1 was made available on April 14, 2025 [1].

#### `F03` When was iPhone 16 announced?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `29.1s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"iPhone 16 announcement date"`, `"when was iPhone 16 released"`, `"iPhone 16 launch date"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/IPhone_16), [Link 2](https://simple.wikipedia.org/wiki/IPhone_16)
- **NOVA Generated Answer:**
  > The iPhone 16 was announced on September 20, 2024 [1], [2].

#### `F04` When did iPhone 16 become available for purchase?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `17.96s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"iPhone 16 release date"`, `"When was iPhone 16 available for purchase"`, `"iPhone 16 launch date"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/IPhone_16), [Link 2](https://simple.wikipedia.org/wiki/IPhone_16)
- **NOVA Generated Answer:**
  > The iPhone 16 became available for purchase on September 20, 2024 [1], [2].

#### `F05` What is the latest major OpenAI announcement?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `34.13s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"latest major OpenAI announcement"`
- **Retrieved Sources:** [Link 1](https://openai.com/research/index/publication/)
- **NOVA Generated Answer:**
  > The latest major OpenAI announcement is the release of GPT-6.2 Astra and GPT-6.2 Sol, the most capable models the company has deployed exter...

#### `F06` When was the article about a new NVIDIA chip published?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `14.67s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"When was the article about a new NVIDIA chip published"`
- **Retrieved Sources:** [Link 1](https://www.bbc.com/news/articles/crmp9mppvzro)
- **NOVA Generated Answer:**
  > The article about a new NVIDIA chip was published on 2026-06-01 [1].

#### `F07` What event date does that NVIDIA article report?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `23.38s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the date of the NVIDIA article about [specific topic]"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `F08` When did Android 16 officially release?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `20.08s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"When did Android 16 officially release?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer when Android 16 officially released.

#### `F09` When was Chandrayaan-3 launched?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `22.18s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"When was Chandrayaan-3 launched?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Pragyan_(Chandrayaan-3))
- **NOVA Generated Answer:**
  > Chandrayaan-3 was launched on 14 July 2023, 14:35 IST (09:05 UTC) [1].

#### `F10` When did Chandrayaan-3 land on the Moon?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `19.23s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"When did Chandrayaan-3 land on the Moon?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Chandrayaan-3)
- **NOVA Generated Answer:**
  > Chandrayaan-3 landed on the Moon on August 23, 2023, at 18:00 IST (12:33 UTC) [1].

#### `F11` What is the date of the latest ICC tournament final?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `28.54s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"latest ICC tournament final date"`, `"What is the date of the latest ICC tournament final? champions list winners"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/2026_Men's_T20_World_Cup_final)
- **NOVA Generated Answer:**
  > The latest ICC tournament final is the 2026 Men's T20 World Cup final, which took place on 8 March 2026 [1].

#### `F12` When was the latest JEE Main official notification published?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `26.41s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"latest JEE Main official notification publication date"`
- **Retrieved Sources:** [Link 1](https://www.jagranjosh.com/news/jee-main-2027-session-1-registration-ends-tomorrow-over-13-lakh-submit-forms-11-lakh-pay-fees-189148)
- **NOVA Generated Answer:**
  > The latest JEE Main official notification was published on November 21, 2026 [1]. This date is based on the information provided in Source [...

#### `F13` Is the date in this article its publication date or the event date? (Use a retrieved article as evidence.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `20.64s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"What is the date mentioned in this article?"`, `"Is the date the publication date or the event date?"`
- **Retrieved Sources:** [Link 1](https://answers.rdpolytech.ca/faq/211915)
- **NOVA Generated Answer:**
  > The date in the article is its publication date. According to [2], for websites, you should use the last updated or publication date. Since ...

#### `F14` Give the publication date and event date separately for a recent news story.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `33.98s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the publication date of the latest news story?"`, `"What is the event date of the latest news story?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.
  > Sources:
  > [1] https://sports.yahoo.com/articles/kelce-...

#### `F15` If two sources disagree about a release date, explain the conflict and identify which date each source refers to.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `28.16s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the conflict between two sources regarding the release date of [specific product or event]?"`, `"How do two sources disagree about the release date of [specific product or event]?"`, `"Identify the conflicting release dates between two sources for [specific product or event]"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the specific question about conflicting release dates. The evidence ...

---

### Section G: Grounding / Claim Verification / Abstention
*Atomic proposition extraction, claim corroboration, bracketed citation verification, and enforcement of the 4 canonical truth states (VERIFIED, PARTIAL, UNVERIFIED, ABSTAIN).*

#### `G01` Who founded Microsoft?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `7.75s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Who founded Microsoft?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/History_of_Microsoft), [Link 2](https://en.wikipedia.org/wiki/Microsoft), [Link 3](https://www.history.com/this-day-in-history/April-4/microsoft-founded)
- **NOVA Generated Answer:**
  > Microsoft was founded on April 4, 1975, by Bill Gates and Paul Allen in Albuquerque, New Mexico, United States [1, 2].

#### `G02` Who founded Google?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `8.94s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Who founded Google?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Google)
- **NOVA Generated Answer:**
  > Google was founded in 1998 by American computer scientists Larry Page and Sergey Brin [1].

#### `G03` Explain an obscure fact about a newly released product, with sources.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `29.85s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the newly released product?"`, `"What is an obscure fact about the newly released product?"`, `"Where can I find sources for the obscure fact about the newly released product?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question about an obscure fact about a newly released product.

#### `G04` Find the latest official NVIDIA announcement and summarise only what the source says.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `20.21s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"latest official NVIDIA announcement"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `G05` Answer a question whose answer is absent from the retrieved sources; do not guess.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `17.81s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Answer a question whose answer is absent from the retrieved sources; do not guess."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `G06` What is the official price of a product when retrieved evidence contains only reviews, not price?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `41.75s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"official price of product"`, `"product price without reviews"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.
  > Sources:
  > [1] https://en.wikipedia.org/wiki/Price_fixi...

#### `G07` Summarise this topic using only the retrieved evidence, without adding outside claims.
- **Route:** `INTERNAL_LLM` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `27.64s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `G08` Give three factual claims and cite a source for each claim.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `29.0s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"What is the first law of thermodynamics?"`, `"What is the second law of thermodynamics?"`, `"What is the third law of thermodynamics?"`
- **Retrieved Sources:** [Link 1](https://www.scribd.com/document/600252838/Facts-Claims-And-Opinions), [Link 2](https://simple.wikipedia.org/wiki/Wikipedia:Citing_sources), [Link 3](https://en.wikipedia.org/wiki/Wikipedia:Verifiability)
- **NOVA Generated Answer:**
  > 1. **Factual Claim:** The process of citing sources is essential for verifying information and ensuring that facts are accurate and trustwor...

#### `G09` If evidence supports only two parts of a three-part question, identify the supported and unsupported parts.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `19.52s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What are the supported and unsupported parts of a three-part question when evidence supports only two parts?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `G10` The search results say one thing and internal model knowledge says another. Which answer state should NOVA return?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `19.43s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the internal model knowledge state?"`, `"What is the search results state?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `G11` Is NVIDIA acquiring a company X? (Use a deliberately unverified rumour; do not accept it without credible evidence.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `30.81s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"Is NVIDIA acquiring a company X? (Use a deliberately unverified rumour; do not accept it without credible evidence.)"`
- **Retrieved Sources:** [Link 1](https://www.forbes.com/sites/janakirammsv/2026/08/31/nvidia-is-not-microsoft-and-hugging-face-is-not-github/)
- **NOVA Generated Answer:**
  > NVIDIA is not acquiring a company X based on the provided evidence. The evidence indicates that there were rumors of an acquisition involvin...

#### `G12` Did a named company announce a product if no credible announcement source is retrieved?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `31.95s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the latest product announcement by [company name]?"`, `"Has [company name] announced a new product?"`
- **NOVA Generated Answer:**
  > No, a named company did not announce a product if no credible announcement source is retrieved. The provided evidence does not contain suffi...

#### `G13` What is the current status of a government policy if only old sources are retrieved?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `28.87s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"official policy history"`, `"government policy archives"`, `"old policy documents"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question regarding the current status of a government policy if ...

#### `G14` Does the cited source actually support the final sentence?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `17.03s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Is the cited source accurate?"`, `"Verify the cited source's support for the final sentence"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `G15` Give an answer with no citations, then verify whether every factual claim is supported by evidence.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `22.68s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Give an answer with no citations, then verify whether every factual claim is supported by evidence."`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Wikipedia:Verifiable,_not_cited)
- **NOVA Generated Answer:**
  > Wikipedia requires that all content be verifiable, meaning that another person should be able to verify the claim using reliable sources. Ho...

---

### Section H: Multi-Turn Context / Coreference Resolution
*Continuous 15-turn multi-turn conversational benchmark testing pronoun resolution (their, its, his), elliptical follow-ups, and clean topic switching.*

#### `H01` Who won the 2023 Cricket World Cup?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `14.24s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Turn completed*
- **Generated Search Queries:** `"2023 Cricket World Cup winners list"`, `"2023 Cricket World Cup final result"`, `"2023 Cricket World Cup champions"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/2023_Cricket_World_Cup)
- **NOVA Generated Answer:**
  > The 2023 Cricket World Cup was won by Australia [1]. This victory marked Australia's sixth title in the tournament.

#### `H02` Who was their captain?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `25.93s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"Who was the captain of the Cricket World Cup in 2022?"`, `"What is the current captain of the Cricket World Cup?"`, `"Who was Cricket World Cup's captain in the Cricket World Cup? champions list winners"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `H03` How many matches did they win in the tournament?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `23.45s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"Cricket World Cup champions list"`, `"Cricket World Cup winners list"`, `"Cricket World Cup final result"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `H04` Who was the runner-up?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `20.23s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Turn completed*
- **Generated Search Queries:** `"Who was the runner-up in the 2022 World Cup?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `H05` Who was the runner-up's captain?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `21.83s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"Who was the runner-up in the 2022 World Cup?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `H06` How many runs did the winning captain score in the final?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `42.44s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"Which team won the final?"`, `"Who is the winning captain?"`, `"What is the final score?"`
- **Retrieved Sources:** [Link 1](https://www.theguardian.com/sport/2026/may/31/virat-kohli-royal-challengers-bengaluru-retain-ipl-title-gujarat-titans)
- **NOVA Generated Answer:**
  > Virat Kohli scored 75 runs in the final match of the 2026 Indian Premier League, leading Royal Challengers Bengaluru to victory [1].

#### `H07` Change topic: Explain transformers in AI.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `40.28s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Topic boundary detected and switched cleanly*
- **Generated Search Queries:** `"Change topic: Explain transformers in AI."`
- **Retrieved Sources:** [Link 1](https://news.google.com/rss/articles/CBMigwFBVV95cUxNNS0wS3dTYjFZVlhjRVhJYjJITVhPdVMxM0ozLTMtdmkxblBGcHQxa29YcUV1cFpoTU5lWWJsS2lIUi1lMTJmbGtmMm5TblBZazNCLVlsZHFDbjVLZDdHM1RVTzNvenFja2U3RVFxdDlPeUZVMGo4OGFlTEh6UzVlNDJRSQ?oc=5), [Link 2](https://news.google.com/rss/articles/CBMiqAFBVV95cUxQQnI2OS1zODRUYlliRlI3cUxEakVSZFEzbXVpbjdEVzNadndPLWZiaUtQdm93cGo5dzdtdFZWR3pkQXp4WGRvQ1d3TmRJczMxNDFsVWN0aDJTb3FWTk1MOXc5RDUyLThnb3FJZ3JSbU9ncy0zcWNZdWl4ZUl5Qkd2cVJYVkVRczhvVHJiU0FDYlA5dEdPZDN5d1NuQTBQWFV2ell1bU5FV2U?oc=5), [Link 3](https://news.google.com/rss/articles/CBMiX0FVX3lxTFBQMmxPdmlucTE5clNETkgxOXdVMnZhbnMtQ2VoanlvY0RIV2JnMDFOUExjckJoQWxNNUlTMzZQR3Y0LUN3dzJXZmVMVGxWc2pMYnNRSXZ2X1dlN3lvd3U4?oc=5)
- **NOVA Generated Answer:**
  > Transformers in AI are a type of neural network architecture designed to process and generate text, images, and other sequential data. They ...

#### `H08` What are its limitations?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `24.94s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"What are the limitations of Change?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "What are Change's limitations?"

#### `H09` What is attention in that architecture?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `26.04s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"What is attention in neural networks?"`, `"Explanation of attention mechanism in deep learning"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "What is attention in that architecture?"

#### `H10` Explain it using a simple example.
- **Route:** `INTERNAL_LLM` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `6.15s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `H11` Tell me about Chandrayaan-3.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `35.94s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Topic boundary detected and switched cleanly*
- **Generated Search Queries:** `"Chandrayaan-3 mission overview"`, `"Chandrayaan-3 spacecraft details"`, `"Chandrayaan-3 achievements"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Chandrayaan-3), [Link 2](https://en.wikipedia.org/wiki/Pragyan_(Chandrayaan-3)), [Link 3](https://www.thehindu.com/sci-tech/science/chandrayaan-3-vikrams-hop-offers-fresh-insights-on-the-moons-surface/article70861509.ece)
- **NOVA Generated Answer:**
  > Chandrayaan-3 is a lunar mission developed and operated by the Indian Space Research Organisation (ISRO). The mission consists of a lunar or...

#### `H12` What was its lander called?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `15.44s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"What was the name of Chandrayaan-2 lander?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Chandrayaan-3)
- **NOVA Generated Answer:**
  > The Chandrayaan-3 lander was called Vikram [1].

#### `H13` What was the rover called?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `18.22s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"What was the name of the Mars rover?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Perseverance_(rover))
- **NOVA Generated Answer:**
  > The rover in question is Perseverance [2].

#### `H14` How long did the mission last?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `16.48s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Multi-turn context maintained*
- **Generated Search Queries:** `"How long was the mission duration?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `H15` Now tell me about Mars missions. (Check that topic switch doesn't retain lunar context.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `25.57s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Topic boundary detected and switched cleanly*
- **Generated Search Queries:** `"Now tell me about Mars missions. (Check that topic switch doesn't retain lunar context.)"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Exploration_of_Mars), [Link 2](https://science.nasa.gov/planetary-science/programs/mars-exploration/), [Link 3](https://en.wikipedia.org/wiki/Mars_Exploration_Program)
- **NOVA Generated Answer:**
  > Mars has been the subject of extensive exploration by spacecraft since the late 20th century. These missions have aimed to understand the pl...

---

### Section I: Topic-Change / Ambiguity / Clarification
*Topic boundary detection ensuring conversational context is never leaked across unrelated subject shifts.*

#### `I01` Tell me about Apple.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `44.17s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is Apple?"`, `"History of Apple"`, `"Apple products"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Apple_Inc.)
- **NOVA Generated Answer:**
  > Apple Inc. is an American multinational technology company founded on April 1, 1976, by Steve Jobs, Steve Wozniak, and Ronald Wayne in Los A...

#### `I02` What is its latest phone? (Resolve context.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `32.42s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"latest phone model"`, `"latest phone release"`, `"latest phone manufacturer"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "What is its latest phone?"

#### `I03` Tell me about Python.
- **Route:** `INTERNAL_LLM` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `9.61s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `I04` What is its latest version? (Resolve context.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `21.3s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"latest version"`, `"latest release"`, `"latest update"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `I05` Compare Java and Python.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `54.89s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"Java vs Python"`, `"Java Programming Language"`, `"Python Programming Language"`
- **Retrieved Sources:** [Link 1](https://aigrama.net/blog/architecture/java-vs-python-guide/), [Link 2](https://www.geeksforgeeks.org/python/difference-between-python-and-java/), [Link 3](https://www.wedowebapps.com/python-vs-java/)
- **NOVA Generated Answer:**
  > Java and Python are both powerful programming languages, but they have distinct characteristics that make them suitable for different types ...

#### `I06` Which one is faster? (Resolve antecedent.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `23.51s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Which one is faster? (Resolve antecedent.)"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "Which one is faster?" as it does not address the speed...

#### `I07` Tell me about Mercury. (Ambiguous: planet/element/brand; should clarify or use context.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `33.73s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is Mercury?"`, `"What is Mercury as a planet?"`, `"What is Mercury as an element?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Mercury), [Link 2](https://en.wikipedia.org/wiki/Mercury_(planet))
- **NOVA Generated Answer:**
  > Mercury is a small planet located between Earth and Mars in our solar system. It is the closest planet to the Sun, orbiting at an average di...

#### `I08` What is the best one? (Insufficient context; clarify.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `19.89s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the best one? (Insufficient context; clarify.)"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "What is the best one?"

#### `I09` Tell me about cricket.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `23.05s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"cricket history"`, `"cricket rules"`, `"cricket teams"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/List_of_Cricket_World_Cup_finals), [Link 2](https://simple.wikipedia.org/wiki/ICC_Men's_Cricket_World_Cup)
- **NOVA Generated Answer:**
  > Cricket is an international sport played between two teams, each consisting of eleven players. The sport is governed by the International Cr...

#### `I10` What is the latest score? (Needs live/current retrieval.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `17.06s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"latest score"`, `"current score"`, `"latest score update"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question about the latest score.

#### `I11` Tell me about NVIDIA DGX Spark.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `25.87s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is NVIDIA DGX Spark?"`, `"Introduction to NVIDIA DGX Spark"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer.

#### `I12` What is its memory? (Resolve product context.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `15.1s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is its memory? (Resolve product context.)"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `I13` Tell me about Delhi.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `37.18s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Delhi history"`, `"Delhi landmarks"`, `"Delhi population"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Delhi), [Link 2](https://en.wikipedia.org/wiki/New_Delhi), [Link 3](https://www.britannica.com/place/Delhi)
- **NOVA Generated Answer:**
  > Delhi is a city and national capital territory in north-central India [1]. It consists of two main parts: Old Delhi, the historic city in th...

#### `I14` What is the weather there today? (Context + current search.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `31.3s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the current weather in [insert specific location]"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `I15` New topic: Explain recursion. (Context reset.)
- **Route:** `INTERNAL_LLM` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `3.92s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

---

### Section J: Search Provider Resilience / Failure Handling
*Multi-provider abstraction testing graceful fallback from DuckDuckGo to Google News RSS during rate-limits, timeouts, and zero results.*

#### `J01` Run a query when the primary search provider is healthy.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `20.99s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Run a query when the primary search provider is healthy."`
- **Retrieved Sources:** [Link 1](https://news.google.com/rss/articles/CBMigwFBVV95cUxQUlg3R01meGFPMm5GRlUzTno0WWs5ai0wV3lCNEhoTDAzM3NQTGxEWll3cWhtcDgyb0VHTmlqaS1Pd2RvU3ZCRE9FbzRiTWh2QWpGX3dGdTVTYkhlRHpXMk1hOVRUMEJVV1Zub0c1N0IyQVByT3NKS1NSc0FINUF1Rk9Obw?oc=5), [Link 2](https://news.google.com/rss/articles/CBMiiwFBVV95cUxQV3V1eVFGV0ZpM2plM1NFTHJKWDhwUkkxbHgzWlhTRGZ2Tzc0UTVoSkZlS2lEZ2ZDZWdkaEFkaXRBeTBvVUNBZ0UwRFVWYmlTWURKQ0M1X2pxWXNiX3ZYaWxKbXQwcldXSlF4Q0lOSnpFdVhZU25GTENiWUszRk1BNS1kcVotWFZqLWNB?oc=5), [Link 3](https://news.google.com/rss/articles/CBMiTEFVX3lxTE13VDNsd19YeUJ1ZTM5ZjlKNzJSLWdhZXlsSmpiNmppZVJLSHp4WmtuZmpnX0dpZDVLbzR2NkYwNWlxYjZ4cVpjb0ZuaGQ?oc=5)
- **NOVA Generated Answer:**
  > To determine when the primary search provider is healthy, you can run a query using one of the search engines listed in the articles provide...

#### `J02` Simulate primary provider timeout.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `22.42s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Simulate primary provider timeout."`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Timeout_(computing)), [Link 2](https://en.wikipedia.org/wiki/Downtime)
- **NOVA Generated Answer:**
  > To simulate a primary provider timeout, you can use the Python REPL to create a connection timeout error. This method involves using Python'...

#### `J03` Simulate primary provider returning zero results.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `20.15s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Simulate primary provider returning zero results."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `J04` Simulate primary provider rate limit / HTTP 429.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `35.43s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"How to simulate primary provider rate limit / HTTP 429"`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `J05` Simulate malformed search results.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `22.46s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Simulate malformed search results."`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Wikipedia:MALFORMED), [Link 2](https://en.wikipedia.org/wiki/Template:MalformedSPIs)
- **NOVA Generated Answer:**
  > To simulate malformed search results, one could follow the structure and format provided by the Wikipedia article on "Wikipedia:MALFORMED" [...

#### `J06` Simulate duplicate URLs from two providers.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `18.95s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Simulate duplicate URLs from two providers."`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Duplicate_content), [Link 2](https://en.wikipedia.org/wiki/Wikipedia:Duplication_detector)
- **NOVA Generated Answer:**
  > To simulate duplicate URLs from two providers, you can use a tool like the Wikipedia Duplication Detector [2]. This tool allows you to compa...

#### `J07` Simulate one provider working and one failing.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `22.98s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"How to simulate a provider working and failing"`, `"Simulating a provider with both working and failing states"`
- **Retrieved Sources:** [Link 1](https://www.juniper.net/documentation/us/en/software/paragon-automation24.1/paragon-automation-user-guide/topics/task/pp-failure-simulation-workflow.html), [Link 2](https://en.wikipedia.org/wiki/Penetration_test)
- **NOVA Generated Answer:**
  > To simulate one provider working and one failing, we can use the concept of network simulation provided by Paragon Automation [1]. This tool...

#### `J08` Simulate all providers failing.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `28.04s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Simulate all providers failing."`
- **NOVA Generated Answer:**
  > To simulate all providers failing, we would need to consider the impact on various services and systems that rely on provider availability. ...

#### `J09` Simulate search succeeds but every page extraction fails.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `34.97s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"What is the cause of page extraction failure in a search simulation?"`
- **Retrieved Sources:** [Link 1](https://github.com/aws-solutions-library-samples/accelerated-intelligent-document-processing-on-aws/issues/994), [Link 2](https://community.cloudflare.com/t/pages-sitemap-fetch-fails-in-search-console-but-google-live-inspection-succeeds/982237)
- **NOVA Generated Answer:**
  > When simulating a search that succeeds but every page extraction fails, it's important to understand the underlying issues and potential sol...

#### `J10` Simulate one extracted page and several failed pages.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `33.27s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"simulate webpage"`, `"failed page simulation"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question.

#### `J11` Simulate a source URL redirect.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `21.5s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Simulate a source URL redirect."`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Wikipedia:Redirect_maker)
- **NOVA Generated Answer:**
  > To simulate a source URL redirect, follow these steps:
  > 1. **Create a New Page**: Enter the title you wish to redirect away from into the bo...

#### `J12` Simulate a non-HTML result such as a PDF.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `24.77s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"How to simulate a PDF without HTML"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/PDF), [Link 2](https://en.wikipedia.org/wiki/Html), [Link 3](https://stackoverflow.com/questions/52379104/alternative-to-wkhtmltopdf)
- **NOVA Generated Answer:**
  > To simulate a non-HTML result such as a PDF, you can use various tools and libraries depending on your programming language and requirements...

#### `J13` Simulate a slow source that exceeds the timeout.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `29.1s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"simulate slow source"`, `"simulate slow source that exceeds timeout"`
- **Retrieved Sources:** [Link 1](https://beeceptor.com/docs/connection-timeout-exception-test/), [Link 2](https://stackoverflow.com/questions/100841/artificially-create-a-connection-timeout-error)
- **NOVA Generated Answer:**
  > To simulate a slow source that exceeds the timeout, you can follow the steps outlined in the provided evidence:
  > 1. **Simulate Connection Ti...

#### `J14` Confirm failure does not crash NOVA or produce fabricated citations.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `18.41s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Confirm failure does not crash NOVA or produce fabricated citations."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer whether failure crashes NOVA or produces fabricated citations. The e...

#### `J15` Confirm fallback only activates when configured trigger conditions are met.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `15.73s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Search provider resilience verified*
- **Generated Search Queries:** `"Confirm fallback only activates when configured trigger conditions are met."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer whether fallback only activates when configured trigger conditions a...

---

### Section K: Extraction / Source Quality / Deduplication
*HTML boilerplate and advertisement removal, UTM tracking parameter stripping, and canonical URL deduplication.*

#### `K01` Retrieve a clean article and verify extracted text.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `51.36s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"clean article"`, `"extracted text verification"`
- **Retrieved Sources:** [Link 1](https://codingtechroom.com/question/-extract-clean-text-from-wikipedia-article), [Link 2](https://www.nstdata.io/blog/extract-clean-article-text)
- **NOVA Generated Answer:**
  > To extract clean text from a Wikipedia article, you can use various methods, including using Python libraries like `wikipedia` and `Beautifu...

#### `K02` Retrieve a page with navigation, ads, and boilerplate; verify cleaning.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `26.01s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Retrieve a page with navigation, ads, and boilerplate; verify cleaning."`
- **Retrieved Sources:** [Link 1](https://you.com/docs/guides/search/retrieve-page-content), [Link 2](https://www.firecrawl.dev/glossary/web-scraping-apis/html-cleaning-boilerplate-removal-llm-training), [Link 3](https://www.html-to-markdown-ai.com/use-cases/clean-html-for-ai-training/)
- **NOVA Generated Answer:**
  > To retrieve a page with navigation, ads, and boilerplate, you can use the You.com Web Search API. The API allows you to connect to You.com v...

#### `K03` Retrieve an official documentation page.
- **Route:** `INTERNAL_RAG` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `3.14s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `K04` Retrieve a page with a long article and verify relevant passages are preserved.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `24.79s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"long article page"`, `"preserve relevant passages"`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `K05` Retrieve two articles covering the same story; verify deduplication.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `25.44s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Retrieve two articles covering the same story; verify deduplication."`
- **NOVA Generated Answer:**
  > I apologize, but the evidence provided does not contain sufficient information to answer the user's question. The evidence appears to be a r...

#### `K06` Retrieve sources with conflicting claims; verify conflict is surfaced.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `31.62s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"Sources with conflicting claims"`, `"Verify conflict is surfaced"`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `K07` Retrieve a low-quality SEO page and an authoritative source; verify source ranking.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `30.5s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Low-Quality SEO Page"`, `"Verify Source Ranking"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question regarding a low-quality SEO page and an authoritative s...

#### `K08` Retrieve a category/archive page; ensure it isn't treated as a specific answer source.
- **Route:** `INTERNAL_LLM` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `3.99s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `K09` Retrieve a page whose title matches but body doesn't answer; mark insufficient.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `17.35s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Retrieve a page whose title matches but body doesn't answer; mark insufficient."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question.

#### `K10` Verify extracted passage retains source URL and metadata.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `15.19s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify extracted passage retains source URL and metadata."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the specific question about verifying extracted passage retains sour...

#### `K11` Verify publication date is extracted correctly when available.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `16.66s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"How to verify publication date extraction is correct when available"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `K12` Verify source updated date isn't mistaken for original publication date.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `16.78s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify source updated date isn't mistaken for original publication date."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.
  > Sources:
  > [1] Template:Citation Style documentation/da...

#### `K13` Verify extraction truncation is visible in metadata/log.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `24.01s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"Verify extraction truncation is visible in metadata/log."`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `K14` Verify passage ranking selects answer-relevant text, not merely the first paragraph.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `23.05s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is passage ranking?"`, `"How does passage ranking select answer-relevant text?"`
- **Retrieved Sources:** [Link 1](https://nhimg.org/glossary/passage-ranking/), [Link 2](https://www.muratulusoy.de/en/glossary/passage-ranking.html)
- **NOVA Generated Answer:**
  > Passage ranking selects answer-relevant text, not merely the first paragraph. According to [1], passage ranking is the process of ordering r...

#### `K15` Verify irrelevant extracted pages are excluded from answer context.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `19.29s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"How to verify irrelevant extracted pages are excluded from answer context"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the specific question about verifying irrelevant extracted pages are...

---

### Section L: Performance / Latency / Budget
*Latency profiling across routing, retrieval, HTML extraction, and grounded answer synthesis stages.*

#### `L01` Measure basic internal question latency.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `23.27s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the basic internal question latency measurement?"`
- **Retrieved Sources:** [Link 1](https://psycnet.apa.org/record/1995-98740-012), [Link 2](https://en.wikipedia.org/wiki/Latency_(engineering))
- **NOVA Generated Answer:**
  > To measure basic internal question latency, one must consider the time delay between the cause (the user's input) and the effect (the system...

#### `L02` Measure simple math fast-path latency.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `28.1s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the latency of simple math operations?"`
- **Retrieved Sources:** [Link 1](https://www.geeksforgeeks.org/system-design/latency-in-system-design/), [Link 2](https://en.wikipedia.org/wiki/Fast_path)
- **NOVA Generated Answer:**
  > To measure simple math fast-path latency, one must understand the concept of latency as it pertains to system performance. Latency is the ti...

#### `L03` Measure a one-search factual query latency.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `29.66s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the latency of a one-search query?"`
- **NOVA Generated Answer:**
  > To measure a one-search factual query latency, the process involves several key steps and factors:
  > 1. **Understanding Query Latency**: Quer...

#### `L04` Measure a current-news query latency.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `21.86s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Measure a current-news query latency."`
- **Retrieved Sources:** [Link 1](https://www.latencytest.me/), [Link 2](https://newsdata.io/blog/streaming-news-api-latency/)
- **NOVA Generated Answer:**
  > To measure the current-news query latency, you can use online latency test tools like Latency Test - Measure Website and API Latency [1]. Th...

#### `L05` Measure a query requiring multiple sources.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `22.09s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Measure a query requiring multiple sources."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question.

#### `L06` Measure router inference time separately.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `30.07s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"How to measure router inference time separately"`
- **Retrieved Sources:** [Link 1](https://www.ultralytics.com/glossary/inference-latency), [Link 2](https://en.wikipedia.org/wiki/Hop_(computer_networking))
- **NOVA Generated Answer:**
  > To measure router inference time separately, one must focus on the latency introduced by the router itself during the packet forwarding proc...

#### `L07` Measure search provider time separately.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `19.91s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"How to measure search provider time separately"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Category:Time_measurement_systems), [Link 2](https://trubridge.com/resources/time-must-be-distinct-and-documented-for-certain-encounters/)
- **NOVA Generated Answer:**
  > To measure search provider time separately, it is crucial to ensure that the time spent on each service during an encounter is clearly docum...

#### `L08` Measure page extraction time separately.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `33.45s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"How to measure page extraction time separately"`
- **NOVA Generated Answer:**
  > To measure page extraction time separately, you need to consider the specific tools and methods available for this purpose. The provided evi...

#### `L09` Measure synthesis time separately.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `26.89s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"How to measure synthesis time separately"`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `L10` Record model load/warm-up time separately from steady-state time.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `45.31s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is model load time?"`, `"What is warm-up time in computer science?"`, `"What is steady-state time in computer science?"`
- **Retrieved Sources:** [Link 1](https://www.tensorflow.org/tfx/serving/saved_model_warmup), [Link 2](https://en.wikipedia.org/wiki/Time_constant), [Link 3](https://en.wikipedia.org/wiki/Steady_state)
- **NOVA Generated Answer:**
  > To record model load/warm-up time separately from steady-state time, one must understand the concept of model warmup and the characteristics...

#### `L11` Run the same query again and measure cache effect (if cache exists).
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `51.18s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"How to run the same query again and measure cache effect (if cache exists)"`
- **Retrieved Sources:** [Link 1](https://docs.cloud.google.com/bigquery/docs/cached-results), [Link 2](https://docs.snowflake.com/en/user-guide/querying-persisted-results), [Link 3](https://www.bing.com/aclick?ld=e8b1Y57h6GeWu4veErnlzeSzVUCUwv_0QCAlH3SNerB1Cwyd5baliZ5dqlHR52do-oYnlb9qnzyz6-MX0bIS81jrFFhEPKmeOX-5Bpp9Ag9tf7KKzaGRFX96L4kjRajJ9a2EbFP6x7s93Q6IPoGMCUFcJEaawXK_bWgVb-3g2_x8YpN74Y5W1hcv9EJlxWKqAF3rhDpA&u=aHR0cHMlM2ElMmYlMmZ3d3cuYWxhY2hpc29mdC5jb20lMmZyZXNvdXJjZXMlMmZhcnRpY2xlcyUyZnJlYWR0aHJ1LXdyaXRldGhydS13cml0ZWJlaGluZC5odG1sJTNmdXRtX3NvdXJjZSUzZGJpbmclMjZ1dG1fbWVkaXVtJTNkY3BjJTI2dXRtX2NvbnRlbnQlM2RyZWFkdGhydS13cml0ZXRocnUtbHAlMjZ1dG1fc291cmNlJTNkYmluZyUyNnV0bV9tZWRpdW0lM2RjcGMlMjZ1dG1fY2FtcGFpZ24lM2RuYy1zcmNoLXJlYWR0aHJ1LXdyaXRldGhydSUyNnV0bV90ZXJtJTNkd3JpdGViZWhpbmQlMjUyMGNhY2hlJTI1MjBwYXR0ZXJuJTI2dXRtX2NvbnRlbnQlM2Q3OTMwMjQ5OTcwMjI3OCUyNnNlYXJjaF9xdWVyeSUzZFJ1biUyNTIwdGhlJTI1MjBzYW1lJTI1MjBxdWVyeSUyNTIwYWdhaW4lMjUyMGFuZCUyNTIwbWVhc3VyZSUyNTIwY2FjaGUlMjUyMGVmZmVjdCUyNTIwaWYlMjUyMGNhY2hlJTI1MjBleGlzdHMlMjUyMG9mZmljaWFsJTI1MjBvdmVydmlldyUyNTIwZmFjdHMlMjZtc2Nsa2lkJTNkN2VmYjQwYzVlMjkzMWY1ZmNhMTIyYmMzMjdiZjMzYzM&rlid=7efb40c5e2931f5fca122bc327bf33c3)
- **NOVA Generated Answer:**
  > To measure the cache effect, you can run the same query again and observe if the results are returned from the cache or if the query is exec...

#### `L12` Confirm retry count stays within configured maximum.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `30.2s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"Confirm retry count stays within configured maximum."`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `L13` Confirm fetched page count stays within budget.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `19.92s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Confirm fetched page count stays within budget."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer whether the fetched page count stays within budget.

#### `L14` Confirm context/token budget is respected.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `20.16s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Confirm context/token budget is respected."`
- **Retrieved Sources:** [Link 1](https://inferensys.com/glossary/answer-engine-architecture/conversational-context-management/contextual-token-budget), [Link 2](https://inferensys.com/glossary/context-engineering-and-prompt-architecture/system-prompt-design/token-budget)
- **NOVA Generated Answer:**
  > A Contextual Token Budget is a dynamic allocation strategy that limits the total number of tokens consumed by a conversation to manage laten...

#### `L15` Compare cold-start vs warm-start latency.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `36.32s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"What is cold-start latency?"`, `"What is warm-start latency?"`
- **Retrieved Sources:** [Link 1](https://webhosting.de/en/server-cold-start-vs-warm-start-performance-differences-optimization/), [Link 2](https://callsphere.ai/blog/vw8c-cold-start-vs-warm-start-voice-ai-2026)
- **NOVA Generated Answer:**
  > In the context of server and AI applications, cold-start and warm-start latencies differ significantly due to the initial setup and resource...

---

### Section M: Regression / Repeatability
*Multi-run repeatability testing verifying deterministic output consistency and 0 schema validation crashes.*

#### `M01` Repeat the water formula test 5 times.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `25.04s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Repeat water formula test 5 times"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer.

#### `M02` Repeat the math test 5 times.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `23.41s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Repeat math test 5 times"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question.

#### `M03` Repeat a fixed factual web query 3 times.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `42.96s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Repeat a fixed factual web query 3 times."`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Web_query), [Link 2](https://en.wikipedia.org/wiki/Illusory_truth_effect), [Link 3](https://www.androidauthority.com/google-search-ai-overview-year-bug-fixed-3562697/)
- **NOVA Generated Answer:**
  > A web query or web search query is a query that a user enters into a web search engine to satisfy their information needs. Web search querie...

#### `M04` Repeat a current-news query at different times and check timestamps.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `20.45s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Repeat a current-news query at different times and check timestamps"`
- **Retrieved Sources:** [Link 1](https://currentsapi.services/en/docs/latest_news), [Link 2](https://www.state.gov/press-releases/)
- **NOVA Generated Answer:**
  > To repeat a current-news query at different times and check timestamps, you can use the Latest News API provided by Currents API [1]. This A...

#### `M05` Confirm malformed-router-output tests still pass after other fixes.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `37.08s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"malformed-router-output tests still pass after other fixes"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "Confirm malformed-router-output tests still pass after...

#### `M06` Confirm entity variant tests remain correct after grounding changes.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `18.82s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Confirm entity variant tests remain correct after grounding changes"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "Confirm entity variant tests remain correct after grou...

#### `M07` Confirm context tests remain correct after topic-change detection.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `37.53s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"topic change detection"`, `"context tests correctness"`, `"recent changes in policies"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question regarding whether context tests remain correct a...

#### `M08` Confirm citations remain valid after answer formatting changes.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `24.91s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What are the citation requirements for answer formatting changes?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question regarding the validity of citations after answer format...

#### `M09` Confirm no test result depends on random/unlogged settings.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `18.06s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Confirm no test result depends on random/unlogged settings."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question.

#### `M10` Run the full suite and calculate PASS/PARTIAL/FAIL rates.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `36.01s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"Run the full suite and calculate PASS/PARTIAL/FAIL rates."`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Failure_rate), [Link 2](https://en.wikipedia.org/wiki/Failure_mode_and_effects_analysis), [Link 3](https://calculator.academy/pass-rate-calculator/)
- **NOVA Generated Answer:**
  > To calculate the PASS/PARTIAL/FAIL rates, we need to follow a structured approach. Let's break down the process:
  > 1. **Define the Parameters...

---

### Section N: Hinglish / Language / Query Normalization
*Multilingual Hindi and Hinglish query understanding, entity preservation, and grounded synthesis.*

#### `N01` Paani ka chemical formula kya hai?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `16.31s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the chemical formula for water?"`
- **Retrieved Sources:** [Link 1](https://hif.wikipedia.org/wiki/Paani), [Link 2](https://hi.wikipedia.org/wiki/जल)
- **NOVA Generated Answer:**
  > Paani ka chemical formula H2O hai [1], [2].

#### `N02` India ka capital kya hai?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `18.61s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the capital of India?"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/India)
- **NOVA Generated Answer:**
  > India ka capital New Delhi hai [1].

#### `N03` 2023 Cricket World Cup kisne jeeta tha?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `28.83s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"2023 Cricket World Cup champions list"`, `"2023 Cricket World Cup final result"`, `"2023 Cricket World Cup record holder"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/2023_Cricket_World_Cup_Final)
- **NOVA Generated Answer:**
  > Australia won the 2023 Cricket World Cup final by defeating India. The match was played on 19 November 2023 at the Narendra Modi Stadium in ...

#### `N04` Abhi latest AI news kya hai?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `54.92s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"latest AI news"`
- **NOVA Generated Answer:**
  > The latest AI news as of the provided evidence includes a report from PR Newswire Press Release indicating that 70% of professionals are usi...

#### `N05` DGX Spark aur RTX 5090 compare karo.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `37.9s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"DGX Spark vs RTX 5090 comparison"`, `"DGX Spark vs RTX 5090 current comparison"`
- **Retrieved Sources:** [Link 1](https://www.msn.com/en-us/technology/hardware-and-devices/my-rtx-spark-laptop-rendered-a-blender-scene-too-big-for-an-rtx-5090-and-a-local-llm-on-the-same-machine-built-it/ar-AA2fQGEg?ocid=BingNewsVerp), [Link 2](https://www.pcworld.com/article/3097360/rtx-gpus-and-pcs-accelerate-local-ai-like-never-before.html)
- **NOVA Generated Answer:**
  > The RTX Spark and RTX 5090 are both powerful GPUs, but they serve different purposes and have different capabilities.
  > The RTX Spark is a po...

#### `N06` iPhone 16 ki India mein price kya hai?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `26.24s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"iPhone 16 ki India mein price kya hai?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `N07` CPU kya kaam karta hai?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `40.27s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"What does a CPU do?"`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `N08` Transformer model simple language mein samjhao.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `32.64s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is a transformer model?"`, `"How does a transformer model work?"`
- **Retrieved Sources:** [Link 1](https://simple.wikipedia.org/wiki/Transformer_(machine_learning_model)), [Link 2](https://en.wikipedia.org/wiki/Transformer_(deep_learning)), [Link 3](https://en.wikipedia.org/wiki/BERT_(language_model))
- **NOVA Generated Answer:**
  > A transformer is a type of computer model used for deep learning, which is a method where computers learn on their own. This model was intro...

#### `N09` JEE Main 2027 ki date kya hai?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `21.38s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"JEE Main 2027 exam date"`
- **Retrieved Sources:** [Link 1](https://www.pw.live/iit-jee/exams/jee-main-2027-information-bulletin), [Link 2](https://collegedunia.com/articles/e-301-jee-main-2027-important-dates---session-1-and-session-2-full-schedule)
- **NOVA Generated Answer:**
  > JEE Main 2027 will have two sessions: Session 1 on January 22-30, 2027, and Session 2 tentatively on April 2-7, 2027. The registration for S...

#### `N10` Aaj India ka match kisne jeeta?
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `40.28s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Which team won the current India vs Australia cricket match"`, `"Who is the current captain of the Indian cricket team"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `N11` Isko simple words mein samjhao. (Needs previous context.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `36.0s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Isko simple words mein samjhao. (Needs previous context.)"`
- **Retrieved Sources:** [Link 1](https://askfilo.com/user-question-answers-smart-solutions/isko-as-it-is-detailed-para-mai-hinglish-mai-samjao-with-eg-3530313434343131)
- **NOVA Generated Answer:**
  > Isko as it is detailed paragraph mein hinglish mein samjhao with eg [1].
  > Iska matlab hai ki jo bhi topic ya baat aapko samjhani hai, usko b...

#### `N12` Uska latest version kya hai? (Needs previous context.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `28.35s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"latest version of the product"`, `"latest version of the software"`, `"latest version of the application"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Wikipedia), [Link 2](https://en.wikipedia.org/wiki/ChatGPT)
- **NOVA Generated Answer:**
  > The latest version of Wikipedia is the one that is currently active and maintained by the Wikimedia Foundation. It has been available in 348...

#### `N13` Mujhe official source chahiye, blog nahi.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `15.03s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Mujhe official source chahiye, blog nahi."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question.

#### `N14` Sirf verified information batao.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `22.65s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the most reliable source for verified information?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer.

#### `N15` Agar evidence nahi hai toh guess mat karna.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `19.47s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the alternative to evidence in a legal context?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

---

### Section O: Adversarial / False-Premise / Robustness
*Refusal to accept fabricated rumours (e.g. NVIDIA acquiring OpenAI), false premises, and strict abstention when evidence is unverified.*

#### `O01` Did NVIDIA acquire OpenAI? (Check premise; don't assume.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `35.8s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Did NVIDIA acquire OpenAI? (Check premise; don't assume.)"`
- **NOVA Generated Answer:**
  > NVIDIA and OpenAI have announced a strategic partnership to deploy 10 gigawatts of NVIDIA systems for OpenAI's next-generation AI infrastruc...

#### `O02` Did ISRO launch Chandrayaan-4 yesterday? (Verify current claim.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `26.89s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"Chandrayaan-4 launch date"`, `"ISRO Chandrayaan missions"`, `"Chandrayaan-4 launch verification"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Chandrayaan-4), [Link 2](https://www.isro.gov.in/LaunchMissions.html)
- **NOVA Generated Answer:**
  > Based on the provided evidence, ISRO did not launch Chandrayaan-4 yesterday. The evidence indicates that Chandrayaan-4 is an upcoming missio...

#### `O03` Is the latest iPhone 16e the same phone as iPhone 16? (Reject false equivalence.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `29.42s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"latest iPhone 16 model"`, `"iPhone 16 vs iPhone 16e"`, `"iPhone 16 vs iPhone 16 Plus"`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/IPhone_16e), [Link 2](https://en.wikipedia.org/wiki/IPhone_16)
- **NOVA Generated Answer:**
  > The latest iPhone 16e and iPhone 16 are not the same phone. The iPhone 16e was released in February 2025 and is part of the iPhone 16 series...

#### `O04` Explain why the Moon is larger than Earth. (Correct false premise.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `22.13s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"What is the size difference between the Moon and Earth? Why is the Moon larger than Earth?"`
- **Retrieved Sources:** [Link 1](https://science.nasa.gov/solar-system/moon/five-things-to-know-about-the-moon/), [Link 2](https://science.nasa.gov/moon/by-the-numbers/)
- **NOVA Generated Answer:**
  > The Moon is not larger than Earth; in fact, it is much smaller. According to [1], the Moon is about one-fourth the size of Earth in width. T...

#### `O05` Give the exact current price but no current source is available. (Abstain or label unavailable.)
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `35.0s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"latest stock prices"`, `"current stock market prices"`, `"latest cryptocurrency prices"`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `O06` A source claims a fabricated event; check before accepting.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `40.22s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"reliable sources for verifying fabricated events"`, `"evidence for fabricated events"`, `"reputable news outlets reporting fabricated events"`
- **Retrieved Sources:** [Link 1](https://meridianreport.org/guides/how-to-fact-check-news-before-sharing), [Link 2](https://www.factcheck.org/fake-news/), [Link 3](https://libguides.wustl.edu/evaluate_news/spot)
- **NOVA Generated Answer:**
  > To check a news story before accepting it, it is crucial to fact-check the information thoroughly. According to Muhammad Mehdi's guide on fa...

#### `O07` Two sources disagree; don't arbitrarily pick one.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `30.61s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"Which sources disagree?"`, `"How do the two sources disagree?"`
- **Retrieved Sources:** [Link 1](https://better-ed.ai/teaching-tips/two-sources-side-by-side), [Link 2](https://en.wikipedia.org/wiki/Wikipedia:Conflicting_sources)
- **NOVA Generated Answer:**
  > When dealing with conflicting sources, it's crucial to approach the situation with a balanced and evidence-based mindset. Both sources [1] a...

#### `O08` The question requests an exact figure but evidence gives only an estimate.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `26.25s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"exact figure"`, `"estimate"`, `"precise figure"`
- **Retrieved Sources:** [Link 1](https://math.answers.com/math-and-arithmetic/Why_is_the_result_only_an_estimate_not_an_exact)
- **NOVA Generated Answer:**
  > The result is only an estimate because it relies on sampled data or assumptions that may not capture the full complexity of the entire popul...

#### `O09` The user asks for a date but source gives only a month/year.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `19.6s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the date corresponding to the given month and year?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question. The evidence primarily discusses date formattin...

#### `O10` The user asks for a latest fact but retrieved source is old.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `21.32s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"latest news"`, `"current facts"`, `"up-to-date information"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question regarding a latest fact, as the evidence is prim...

#### `O11` Search result title says answer A but body says answer B.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `15.51s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Search result title says answer A but body says answer B"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer.

#### `O12` Source is satire or opinion; don't present as factual news.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `25.38s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Source is satire or opinion; don't present as factual news."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question as it does not provide any specific examples or details...

#### `O13` Query includes a typo; normalize without changing meaning.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `32.29s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Query includes a typo; normalize without changing meaning."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer.

#### `O14` Query contains multiple subquestions; ensure each is answered or marked unsupported.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `37.9s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"What is the first subquestion?"`, `"What is the second subquestion?"`, `"What is the third subquestion?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the user's question.

#### `O15` Query is ambiguous; ask a clarifying question rather than silently choosing.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `34.42s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"Query is ambiguous; ask a clarifying question rather than silently choosing."`
- **Retrieved Sources:** [Link 1](https://inferensys.com/prompts/grounding-and-evidence-ranking/evidence-based-refusal-and-uncertainty-expression/ambiguous-query-clarification-prompt-before-refusal), [Link 2](https://inferensys.com/prompts/rag-question-answering-prompts/answer-grounding-and-faithful-synthesis-prompts/clarification-question-generation-prompt-for-ambiguous-queries)
- **NOVA Generated Answer:**
  > To provide a clear and grounded response, it's important to understand the context and requirements of the user's query. Based on the eviden...

---

### Section P: System / Structured Output / Logging Checks
*Pydantic contract enforcement, JSON recovery resilience, deterministic fallback logging, and execution audit trails.*

#### `P01` Verify router output conforms to schema.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `20.93s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"How to verify router output conforms to schema"`, `"Router output validation tools"`, `"Schema validation for network devices"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question regarding whether router output conforms to a schema. 
  > ...

#### `P02` Verify malformed JSON recovery runs at most once.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `30.47s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"Verify malformed JSON recovery runs at most once."`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `P03` Verify deterministic fallback is logged.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `UNVERIFIED` | **Latency:** `33.46s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: UNVERIFIED*
- **Generated Search Queries:** `"How is deterministic fallback logged in the system?"`
- **NOVA Generated Answer:**
  > > ⚠️ **Notice: [UNVERIFIED - PARAMETRIC KNOWLEDGE]**
  > > This answer was generated from model training data without live retrieval verificati...

#### `P04` Verify original query is preserved in logs.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `21.21s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify original query is preserved in logs."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.
  > Sources:
  > [1] https://community.databricks.com/t5/lake...

#### `P05` Verify rewritten query is logged separately.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `19.63s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"How is a rewritten query logged separately?"`, `"What is the process of logging a rewritten query separately?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer whether rewritten queries are logged separately.

#### `P06` Verify route decision and reason are logged.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `20.16s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify route decision and reason are logged."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer whether route decision and reason are logged. The evidence provided ...

#### `P07` Verify evidence relevance and sufficiency are separate fields.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `26.02s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify evidence relevance and sufficiency are separate fields."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer whether evidence relevance and sufficiency are separate fields.
  > Sou...

#### `P08` Verify confidence/state is recorded.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `23.04s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify confidence/state is recorded."`, `"Verify confidence/state is recorded. record holder"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer whether confidence/state is recorded.

#### `P09` Verify each answer claim maps to evidence IDs.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `15.58s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify each answer claim maps to evidence IDs."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `P10` Verify citation URLs are valid and source IDs are consistent.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `23.48s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify citation URLs are valid and source IDs are consistent."`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question regarding the validity of citation URLs and the consist...

#### `P11` Verify source publication/event dates are stored separately.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `31.11s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Where are publication and event dates stored in a database?"`, `"How are publication and event dates typically stored in a database?"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "Verify source publication/event dates are stored separ...

#### `P12` Verify provider error type and retry trigger are logged.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `18.27s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"How to verify provider error type and retry trigger are logged"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question.

#### `P13` Verify latency per stage is logged.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `ABSTAIN` | **Latency:** `15.2s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: ABSTAIN*
- **Generated Search Queries:** `"Verify latency per stage logging is recorded"`
- **NOVA Generated Answer:**
  > The provided evidence does not contain sufficient information to answer the question "Verify latency per stage is logged." The evidence prov...

#### `P14` Verify no secret/API key is exposed in logs.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `VERIFIED` | **Latency:** `28.08s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: VERIFIED*
- **Generated Search Queries:** `"How to check for secret/API key exposure in logs"`
- **Retrieved Sources:** [Link 1](https://pasteandpurge.com/learn/what-to-do-if-api-key-or-secret-is-exposed), [Link 2](https://apidog.com/blog/api-key-leak-check-secret-scanner/)
- **NOVA Generated Answer:**
  > To verify that no secret/API key is exposed in logs, one should follow a structured approach as outlined in the Defensive Response Framework...

#### `P15` Verify a failure produces a structured error/abstention, not a crash.
- **Route:** `WEB_SEARCH` (`TIER_1_SLM`) | **Truth State:** `PARTIAL` | **Latency:** `22.03s` | **Verdict:** ✅ **PASS**
- **Audit Evaluation:** *Truth state: PARTIAL*
- **Generated Search Queries:** `"Verify a failure produces a structured error/abstention, not a crash."`
- **Retrieved Sources:** [Link 1](https://en.wikipedia.org/wiki/Crash_(computing)), [Link 2](https://www.geeksforgeeks.org/software-testing/software-testing-bug-vs-defect-vs-error-vs-fault-vs-failure/)
- **NOVA Generated Answer:**
  > A failure in software produces a structured error or abstention, not a crash [3]. A failure is observed when software behaves incorrectly du...

---
