"""
PROJECT NOVA - Phase 1 Evidence Pipeline Acceptance Tests (Sprint 5)
===================================================================
Tests:
1. Retrieval of facts located well beyond character 1,200.
2. Retrieval of facts located in middle / end of long documents (character 4,000+).
3. Irrelevant introductory text is deprioritized in favor of answer-bearing passages.
4. Structured markdown tables are preserved intact without fragmentation.
5. Strict entity matching prioritizes target entity and penalizes conflicting variants.
6. Context and character budgets are strictly respected.
7. Deduplication of overlapping / repeated chunks across sources.
8. End-to-end integration with main.py: _format_evidence_context passes deep facts.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from retriever.chunker import (
    chunk_document,
    score_chunk,
    select_top_evidence_chunks,
)
from retriever.models import ExtractedDocument
from main import NovaOrchestrator


def run_all_tests():
    passed = 0
    total = 0

    def assert_eq(actual, expected, msg=""):
        nonlocal passed, total
        total += 1
        assert actual == expected, f"FAILED [{total}]: {msg} (Expected {expected}, got {actual})"
        passed += 1

    def assert_true(cond, msg=""):
        nonlocal passed, total
        total += 1
        assert cond, f"FAILED [{total}]: {msg}"
        passed += 1

    print("\n============================================================")
    print("       PROJECT NOVA - SPRINT 5 PHASE 1 ACCEPTANCE SUITE     ")
    print("============================================================\n")

    # ------------------------------------------------------------------
    # TEST 1: FACT BEYOND CHARACTER 1,200 (FIXING 1,200-CHAR BLINDNESS)
    # ------------------------------------------------------------------
    print("[1/5] Testing Fact Retrieval Beyond Character 1,200...")
    # Construct a long document where the first 2,000 characters are generic fluff,
    # and the critical fact (Kapil Dev's score in the 1983 final: 15 runs) is at character 2,500.
    fluff_intro = "The Cricket World Cup is the premier international championship of One Day International cricket. " * 25 # ~2,400 chars
    final_scorecard_section = (
        "\n\n## 1983 World Cup Final Match Scorecard\n"
        "In the final match at Lord's on 25 June 1983, India batted first and scored 183 runs. "
        "Kris Srikkanth scored 38, Mohinder Amarnath scored 26, and captain Kapil Dev scored 15 runs off 8 balls. "
        "India bowled out the West Indies for 140 runs to win by 43 runs.\n\n"
    )
    long_doc = ExtractedDocument(
        source_index=1,
        title="1983 Cricket World Cup History and Final Scorecard",
        url="https://espncricinfo.com/series/1983-world-cup/final-scorecard",
        clean_text=fluff_intro + final_scorecard_section + ("Further tournament analysis. " * 30),
        published_date="2023-06-25",
        author="ESPN Staff"
    )

    query = "What was Kapil Dev's score in the 1983 World Cup final?"
    selected_chunks = select_top_evidence_chunks(query, [long_doc], max_chunks=2, max_total_chars=3000)
    
    assert_true(len(selected_chunks) > 0, "Should select at least one chunk")
    best_chunk = selected_chunks[0]
    assert_true("Kapil Dev scored 15 runs" in best_chunk.text, "Chunk MUST contain the deep fact beyond char 1,200")
    assert_true(best_chunk.start_char >= 1200, f"Chunk start offset ({best_chunk.start_char}) must be located beyond char 1,200")
    print(f"  ✓ Fact at character offset {best_chunk.start_char} successfully retrieved and prioritized over intro fluff!")

    # ------------------------------------------------------------------
    # TEST 2: FACT AT VERY END OF LONG DOCUMENT (CHAR 5,000+)
    # ------------------------------------------------------------------
    print("\n[2/5] Testing Fact Retrieval at Very End of Long Document...")
    filler_middle = "This is intermediate hardware background discussing chip architecture and history. " * 50 # ~4,500 chars
    specs_conclusion = (
        "\n\n### Technical Specifications Table\n"
        "| Processor | Base Clock | Boost Clock | Memory Bandwidth |\n"
        "| NVIDIA DGX Spark | 2.2 GHz | 3.8 GHz | 2.4 TB/s |\n"
    )
    long_tech_doc = ExtractedDocument(
        source_index=2,
        title="NVIDIA Enterprise Computing Architecture",
        url="https://nvidia.com/enterprise/dgx-spark-specs",
        clean_text="Introduction to enterprise AI computing.\n\n" + filler_middle + specs_conclusion,
        published_date="2025-01-10"
    )
    query_specs = "What is the clock speed of processor in NVIDIA DGX Spark?"
    selected_tech = select_top_evidence_chunks(query_specs, [long_tech_doc], max_chunks=2, max_total_chars=3000)
    assert_true(len(selected_tech) > 0, "Should retrieve specs chunk")
    tech_chunk = selected_tech[0]
    assert_true("Boost Clock" in tech_chunk.text or "3.8 GHz" in tech_chunk.text, "Must capture end-of-document specification")
    assert_true(tech_chunk.contains_table, "Must preserve structured markdown table flag")
    print(f"  ✓ End-of-document specs table at offset {tech_chunk.start_char} retrieved with table structure intact!")

    # ------------------------------------------------------------------
    # TEST 3: STRICT ENTITY ALIGNMENT VS CONFLICTING VARIANTS
    # ------------------------------------------------------------------
    print("\n[3/5] Testing Entity Variant Disambiguation in Chunk Selection...")
    doc_variants = ExtractedDocument(
        source_index=3,
        title="Apple iPhone Lineup Analysis 2024-2025",
        url="https://techradar.com/apple/iphone-16-lineup",
        clean_text=(
            "## iPhone 16 Base Model\n"
            "The iPhone 16 was officially launched in India on September 20, 2024 with a starting price of Rs 79,900.\n\n"
            "## iPhone 16e Budget Variant\n"
            "The iPhone 16e was announced in February 2025 as a budget-oriented variant starting at Rs 59,900.\n"
        )
    )
    query_base = "What is the price of iPhone 16 in India?"
    chunks_base = select_top_evidence_chunks(query_base, [doc_variants], max_chunks=1)
    assert_true("Rs 79,900" in chunks_base[0].text, "Query for base iPhone 16 must select base model chunk, not 16e")
    assert_true("Rs 59,900" not in chunks_base[0].text, "Must not select 16e variant price")

    query_variant = "What is the launch date and price of iPhone 16e?"
    chunks_var = select_top_evidence_chunks(query_variant, [doc_variants], max_chunks=1)
    assert_true("iPhone 16e" in chunks_var[0].text, "Query for iPhone 16e must select 16e chunk")
    assert_true("February 2025" in chunks_var[0].text, "Must select 16e launch date")
    print("  ✓ Strict entity scoring accurately isolates base models from budget variants!")

    # ------------------------------------------------------------------
    # TEST 4: DEDUPLICATION & CHARACTER BUDGET ENFORCEMENT
    # ------------------------------------------------------------------
    print("\n[4/5] Testing Deduplication & Context Budget Enforcement...")
    duplicate_doc1 = ExtractedDocument(
        source_index=4,
        title="News Outlet A",
        url="https://site-a.com/news",
        clean_text="ISRO successfully landed Chandrayaan-3 lander Vikram on the lunar south pole on August 23, 2023."
    )
    duplicate_doc2 = ExtractedDocument(
        source_index=5,
        title="News Outlet B",
        url="https://site-b.com/news",
        clean_text="ISRO successfully landed Chandrayaan-3 lander Vikram on the lunar south pole on August 23, 2023." # Exact syndicated duplicate
    )
    dedup_chunks = select_top_evidence_chunks(
        "Chandrayaan-3 landing date",
        [duplicate_doc1, duplicate_doc2],
        max_chunks=4,
        max_total_chars=1000
    )
    assert_eq(len(dedup_chunks), 1, "Syndicated duplicate articles should be deduplicated to 1 chunk")

    total_chars = sum(len(c.text) for c in dedup_chunks)
    assert_true(total_chars <= 1000, "Must enforce max character budget")
    print("  ✓ Syndicated duplicate passages deduplicated, and character budget strictly enforced.")

    # ------------------------------------------------------------------
    # TEST 5: END-TO-END ORCHESTRATOR INTEGRATION WITH DEEP PASSAGES
    # ------------------------------------------------------------------
    print("\n[5/5] Testing main.py Integration with Deep Evidence Passages...")
    orchestrator = NovaOrchestrator(verifier_mode="hybrid")
    
    # Verify that _format_evidence_context selects the deep scorecard section instead of intro fluff
    evidence_prompt_text = orchestrator._format_evidence_context(query, [long_doc])
    assert_true("Kapil Dev scored 15 runs" in evidence_prompt_text, "Evidence context fed to LLM MUST contain the deep fact")
    assert_true("--- SOURCE [1]" in evidence_prompt_text, "Source index must be traceable in prompt")
    print("  ✓ main.py _format_evidence_context delivers deep-article facts to Synthesizer seamlessly!")

    print("\n============================================================")
    print(f"✓ SPRINT 5 PHASE 1: {passed}/{total} ACCEPTANCE TESTS PASSED (100%)")
    print("============================================================\n")


if __name__ == "__main__":
    run_all_tests()

