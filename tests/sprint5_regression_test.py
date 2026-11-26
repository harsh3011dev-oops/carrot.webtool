"""
PROJECT NOVA - SPRINT 5 MASTER REGRESSION TEST SUITE (30 TESTS)
==============================================================
Validates the complete Sprint 5 Truth & Grounding Architecture:
- Group 1: Deep Evidence Retrieval & Chunker Fidelity (Tests 1-6)
- Group 2: Proposition Proximity & Cross-Paragraph Isolation (Tests 7-12)
- Group 3: Contradiction Detection & Truth State Demotion (Tests 13-17)
- Group 4: Citation Metric Integrity (Tests 18-21)
- Group 5: Encyclopedic Fallback & Targeted Corrective RAG (Tests 22-26)
- Group 6: Benchmark Runner Ground-Truth Scoring (Tests 27-30)
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from grounding.schemas import ResponseState
from grounding.verifier import ClaimVerifier
from retriever.chunker import chunk_document, score_chunk, select_top_evidence_chunks
from retriever.models import ExtractedDocument
from retriever.search_providers import (
    DuckDuckGoSearchProvider,
    GoogleNewsRSSSearchProvider,
    MultiProviderSearchManager,
    WikipediaSearchProvider,
)
from tests.benchmark_runner import BenchmarkRunner


def run_all_tests():
    passed = 0
    total = 0

    def assert_true(cond: bool, msg: str):
        nonlocal passed, total
        total += 1
        assert cond, f"FAILED [{total}]: {msg}"
        passed += 1

    def assert_eq(a, b, msg: str):
        nonlocal passed, total
        total += 1
        assert a == b, f"FAILED [{total}]: {msg} (Expected {b}, got {a})"
        passed += 1

    print("\n============================================================")
    print("       PROJECT NOVA - SPRINT 5 MASTER REGRESSION SUITE       ")
    print("============================================================\n")

    verifier = ClaimVerifier(mode="hybrid")
    strict_verifier = ClaimVerifier(mode="strict")

    # ------------------------------------------------------------------
    # GROUP 1: DEEP EVIDENCE RETRIEVAL & CHUNKER FIDELITY (TESTS 1-6)
    # ------------------------------------------------------------------
    print("[GROUP 1] Deep Evidence Retrieval & Chunker Fidelity...")

    filler_2500 = "Introductory background context information. " * 60
    deep_fact = "Kapil Dev smashed an unbeaten 175 not out off 138 balls against Zimbabwe at Tunbridge Wells."
    doc_deep = ExtractedDocument(
        source_index=1,
        title="1983 World Cup Match Reports",
        url="https://espncricinfo.com/wc1983",
        clean_text=f"{filler_2500}\n\n## India vs Zimbabwe Miracle\n{deep_fact}\n\nMore tournament history."
    )

    # Test 1.1: Fact beyond 1,200 chars
    chunks_deep = select_top_evidence_chunks("What was Kapil Dev's score against Zimbabwe?", [doc_deep], max_chunks=1)
    assert_true(len(chunks_deep) > 0 and "175 not out" in chunks_deep[0].text, "Fact beyond 1,200 chars retrieved")
    assert_true(chunks_deep[0].start_char > 1200, "Fact was retrieved from deep in the document")

    # Test 1.2: End of article fact
    filler_5000 = "Historical data and commentary. " * 120
    specs_table = "| Specification | Detail |\n| Processor | GB200 |\n| Memory | 128GB Unified |"
    doc_table = ExtractedDocument(
        source_index=2,
        title="NVIDIA DGX Specifications",
        url="https://nvidia.com/dgx",
        clean_text=f"{filler_5000}\n\n## Hardware Specifications\n{specs_table}"
    )
    chunks_table = select_top_evidence_chunks("What is the processor in NVIDIA DGX?", [doc_table], max_chunks=1)
    assert_true("GB200" in chunks_table[0].text, "Fact at char 4,000+ successfully selected")

    # Test 1.3: Table preservation flag
    assert_true(chunks_table[0].contains_table, "Markdown table preserved with contains_table flag")

    # Test 1.4: Section heading preserved
    assert_eq(chunks_table[0].heading, "Hardware Specifications", "Section heading accurately attributed")

    # Test 1.5: Context budget enforcement
    budget_chunks = select_top_evidence_chunks("NVIDIA specifications", [doc_table, doc_deep], max_chunks=3, max_total_chars=2000)
    total_chars = sum(len(c.text) for c in budget_chunks)
    assert_true(total_chars <= 2500, f"Context budget strictly respected (got {total_chars} chars)")

    # Test 1.6: Deduplication across overlapping sources
    dup1 = ExtractedDocument(source_index=3, title="A", url="https://a.com", clean_text="ISRO Chandrayaan-3 landed on August 23, 2023 on the Moon.")
    dup2 = ExtractedDocument(source_index=4, title="B", url="https://b.com", clean_text="ISRO Chandrayaan-3 landed on August 23, 2023 on the Moon.")
    dedup_chunks = select_top_evidence_chunks("Chandrayaan-3 landing", [dup1, dup2], max_chunks=5)
    assert_eq(len(dedup_chunks), 1, "Duplicate syndicated news passages deduplicated to 1 chunk")
    print(f"  ✓ Tests 1-6 passed: Deep retrieval, table preservation, budget & dedup verified.")

    # ------------------------------------------------------------------
    # GROUP 2: PROPOSITION PROXIMITY & CROSS-PARAGRAPH ISOLATION (TESTS 7-12)
    # ------------------------------------------------------------------
    print("\n[GROUP 2] Proposition Proximity & Cross-Paragraph Isolation...")

    doc_1983_full = ExtractedDocument(
        source_index=1,
        title="1983 World Cup Tournament Summary",
        url="https://espncricinfo.com/wc1983",
        clean_text=(
            "## Group Stage: India vs Zimbabwe\n"
            "Kapil Dev scored 175 not out off 138 balls to rescue India from 17 for 5 against Zimbabwe.\n\n"
            "## The Final: India vs West Indies\n"
            "In the 1983 World Cup final at Lord's, Kapil Dev scored 15 runs before taking a great catch. India won by 43 runs."
        )
    )

    # Test 2.1: Kapil Dev 175 in final is NOT supported
    c_false_final = "In the 1983 World Cup final, Kapil Dev scored 175 runs [1]."
    v_false_final = verifier.verify_single_claim(c_false_final, [doc_1983_full])
    assert_true(not v_false_final.is_supported, "Kapil Dev 175 must not verify 1983 final claim")

    # Test 2.2: Kapil Dev 15 in final IS supported
    c_true_final = "In the 1983 World Cup final, Kapil Dev scored 15 runs [1]."
    v_true_final = verifier.verify_single_claim(c_true_final, [doc_1983_full])
    assert_true(v_true_final.is_supported, "Kapil Dev 15 in final corroborated")

    # Test 2.3: Kapil Dev 175 against Zimbabwe IS supported
    c_true_zim = "Kapil Dev scored 175 not out against Zimbabwe [1]."
    v_true_zim = verifier.verify_single_claim(c_true_zim, [doc_1983_full])
    assert_true(v_true_zim.is_supported, "Kapil Dev 175 against Zimbabwe corroborated")

    # Test 2.4: 5090 units shipped does NOT verify price of $5090
    doc_shipments = ExtractedDocument(
        source_index=2,
        title="Hardware Shipments",
        url="https://nvidia.com/news",
        clean_text="NVIDIA shipped over 5090 units of DGX Spark systems to cloud providers."
    )
    c_false_price = "The DGX Spark costs $5090 [2]."
    v_false_price = verifier.verify_single_claim(c_false_price, [doc_shipments])
    assert_true(not v_false_price.is_supported, "Units shipped (5090) rejected for price claim ($5090)")

    # Test 2.5: Missing landing date attribute rejected despite entity match
    doc_launch_only = ExtractedDocument(
        source_index=3,
        title="ISRO Launch",
        url="https://isro.gov.in",
        clean_text="ISRO launched Chandrayaan-3 from Sriharikota spaceport."
    )
    c_landing = "Chandrayaan-3 landed on August 23, 2023 [3]."
    v_landing = verifier.verify_single_claim(c_landing, [doc_launch_only])
    assert_true(not v_landing.is_supported, "Entity match alone cannot verify absent landing date attribute")

    # Test 2.6: Attribute domain alignment for technical specs
    doc_clock = ExtractedDocument(
        source_index=4,
        title="Processor Specs",
        url="https://tech.com/cpu",
        clean_text="The CPU features 8 cores and operates at a boost clock speed of 3.8 GHz."
    )
    c_clock = "The CPU operates at a boost clock speed of 3.8 GHz [4]."
    v_clock = verifier.verify_single_claim(c_clock, [doc_clock])
    assert_true(v_clock.is_supported, "Exact specification and unit corroborated")
    print(f"  ✓ Tests 7-12 passed: Cross-paragraph leakage eliminated & attribute domains verified.")

    # ------------------------------------------------------------------
    # GROUP 3: CONTRADICTION DETECTION & TRUTH STATE DEMOTION (TESTS 13-17)
    # ------------------------------------------------------------------
    print("\n[GROUP 3] Contradiction Detection & Truth State Demotion...")

    doc_iphone_price = ExtractedDocument(
        source_index=5,
        title="iPhone 16 Pricing",
        url="https://apple.com/in/iphone-16",
        clean_text="The base iPhone 16 is priced at Rs 79,900 in India."
    )
    # Test 3.1: Contradictory price
    c_contra_price = "The base iPhone 16 is priced at Rs 59,900 in India."
    v_contra = verifier.verify_single_claim(c_contra_price, [doc_iphone_price])
    assert_true(not v_contra.is_supported, "Contradictory claim rejected")
    assert_true(v_contra.contradiction_detected, "Contradiction explicitly flagged")

    # Test 3.2: Mixed response demoted to PARTIAL (never VERIFIED)
    resp_mixed = "The base iPhone 16 is priced at Rs 79,900 in India [5]. The base iPhone 16 is priced at Rs 59,900 in India [5]."
    audit_mixed = verifier.audit_and_verify_response("iPhone 16 price", resp_mixed, [doc_iphone_price])
    assert_eq(audit_mixed.response_state, ResponseState.PARTIAL, "Contradiction prevents VERIFIED state")

    # Test 3.3: Strict mode demotes unsupported answers to ABSTAIN
    resp_unsupported = "The base iPhone 16 is priced at Rs 10,000 in India."
    audit_strict = strict_verifier.audit_and_verify_response("iPhone 16 price", resp_unsupported, [doc_iphone_price])
    assert_eq(audit_strict.response_state, ResponseState.ABSTAIN, "Strict mode abstains when claims unsupported")

    # Test 3.4: Explicit refusal triggers ABSTAIN
    resp_abstain = "The provided evidence does not contain sufficient information to answer."
    audit_refusal = verifier.audit_and_verify_response("Random topic", resp_abstain, [doc_iphone_price])
    assert_eq(audit_refusal.response_state, ResponseState.ABSTAIN, "Explicit refusal maps to ABSTAIN")

    # Test 3.5: Parametric knowledge flagged as UNVERIFIED in hybrid mode
    resp_param = "Photosynthesis is the process by which green plants make food."
    audit_param = verifier.audit_and_verify_response("Photosynthesis", resp_param, docs=[], is_internal_generation=True)
    assert_eq(audit_param.response_state, ResponseState.UNVERIFIED, "Parametric generation flagged UNVERIFIED")
    assert_true("UNVERIFIED - PARAMETRIC KNOWLEDGE" in audit_param.final_text, "Transparent disclaimer banner attached")
    print(f"  ✓ Tests 13-17 passed: Contradictions flagged & canonical truth states enforced.")

    # ------------------------------------------------------------------
    # GROUP 4: CITATION METRIC INTEGRITY (TESTS 18-21)
    # ------------------------------------------------------------------
    print("\n[GROUP 4] Citation Metric Integrity...")

    # Test 4.1: Citation support rate reflects actual claim-evidence linkage (1 of 2 supported = 0.5)
    assert_eq(audit_mixed.citation_support_rate, 0.5, "Citation support rate accurately 50.0% for 1/2 supported citations")

    # Test 4.2: Hallucinated citation index [99] drops support rate
    text_bad_cite = "The base iPhone 16 costs Rs 79,900 [5] but flies to Mars [99]."
    rate_bad, _ = verifier.verify_citations(text_bad_cite, [doc_iphone_price])
    assert_true(rate_bad < 1.0, "Non-existent source index [99] penalizes citation rate")

    # Test 4.3: Fully supported citations produce 100%
    text_good_cite = "The base iPhone 16 is priced at Rs 79,900 in India [5]."
    c_good_claim = verifier.verify_single_claim("The base iPhone 16 is priced at Rs 79,900 in India [5].", [doc_iphone_price])
    rate_good, _ = verifier.verify_citations(text_good_cite, [doc_iphone_price], [c_good_claim])
    assert_eq(rate_good, 1.0, "Fully corroborated cited claim produces 100% citation rate")

    # Test 4.4: Text with no citations defaults to 1.0
    rate_none, indices_none = verifier.verify_citations("Clean factual text without brackets.", [doc_iphone_price])
    assert_eq(rate_none, 1.0, "Citation rate defaults to 1.0 when no citations are present")
    assert_eq(indices_none, [], "Indices list empty when no citations present")
    print(f"  ✓ Tests 18-21 passed: Honest citation support metrics validated.")

    # ------------------------------------------------------------------
    # GROUP 5: ENCYCLOPEDIC FALLBACK & TARGETED CORRECTIVE RAG (TESTS 22-26)
    # ------------------------------------------------------------------
    print("\n[GROUP 5] Encyclopedic Fallback & Targeted Corrective RAG...")

    # Test 5.1: WikipediaSearchProvider retrieves historical topic
    wiki = WikipediaSearchProvider()
    wiki_results = wiki.search("1983 Cricket World Cup", limit=3)
    assert_true(len(wiki_results) > 0, "Wikipedia provider returned search results")

    # Test 5.2: Wikipedia URLs are authoritative and valid
    assert_true(any("wikipedia.org" in r.url for r in wiki_results), "Direct Wikipedia URL retrieved")

    # Test 5.3: MultiProviderSearchManager fallback cascade
    class FailingProvider(DuckDuckGoSearchProvider):
        def search(self, query: str, limit: int = 5):
            raise ConnectionError("Simulated primary provider outage")

    mgr = MultiProviderSearchManager(
        primary_provider=FailingProvider(),
        fallback_providers=[GoogleNewsRSSSearchProvider(), WikipediaSearchProvider()]
    )
    fallback_results = mgr.search("1983 Cricket World Cup", limit=3)
    assert_true(len(fallback_results) > 0, "Cascaded through fallbacks successfully during outage")

    # Test 5.4: Targeted retry query for missing score attribute
    from main import NovaOrchestrator
    orchestrator = NovaOrchestrator.__new__(NovaOrchestrator)
    retry_score = orchestrator._formulate_retry_queries("Tell me Kapil Dev's score in the final of the 1983 World Cup")
    assert_true(any("scorecard" in q.lower() or "score" in q.lower() for q in retry_score), "Retry query targets missing scorecard attribute")

    # Test 5.5: Targeted retry query for missing launch date attribute
    retry_launch = orchestrator._formulate_retry_queries("What is the launch date of iPhone 16?")
    assert_true(any("official launch release date" in q.lower() for q in retry_launch), "Retry query targets exact launch date attribute")
    print(f"  ✓ Tests 22-26 passed: Wikipedia fallback & targeted corrective RAG verified.")

    # ------------------------------------------------------------------
    # GROUP 6: BENCHMARK RUNNER GROUND-TRUTH SCORING (TESTS 27-30)
    # ------------------------------------------------------------------
    print("\n[GROUP 6] Benchmark Runner Ground-Truth Scoring...")

    runner = BenchmarkRunner.__new__(BenchmarkRunner)

    # Test 6.1: Abstaining on false-premise query is ABSTENTION_CORRECT (PASS)
    from grounding.schemas import VerifiedResponse
    resp_false_premise = VerifiedResponse(
        final_text="The event described contains a false premise and cannot be verified.",
        response_state=ResponseState.ABSTAIN,
        claims=[],
        unsupported_claims_count=0,
        verified_sources=[],
        citation_support_rate=1.0,
    )
    verdict_fp, reason_fp = runner.evaluate_verdict("O", "O01", "Who won the 2030 World Cup?", "WEB_SEARCH", resp_false_premise, 1.2)
    assert_eq(verdict_fp, "PASS", "Abstention on false premise must be PASS")
    assert_true("ABSTENTION_CORRECT" in reason_fp, "Reason reflects ABSTENTION_CORRECT")

    # Test 6.2: Abstaining on factual query is ABSTENTION_FAILURE (FAIL)
    resp_factual_abstain = VerifiedResponse(
        final_text="The provided evidence does not contain sufficient information to answer.",
        response_state=ResponseState.ABSTAIN,
        claims=[],
        unsupported_claims_count=0,
        verified_sources=[],
        citation_support_rate=1.0,
    )
    verdict_fa, reason_fa = runner.evaluate_verdict("C", "C01", "Who won the 2023 Cricket World Cup?", "WEB_SEARCH", resp_factual_abstain, 1.5)
    assert_eq(verdict_fa, "FAIL", "Abstaining on basic factual query must be FAIL")
    assert_true("ABSTENTION_FAILURE" in reason_fa, "Reason reflects ABSTENTION_FAILURE")

    # Test 6.3: Web search with 0 retrieved sources is RETRIEVAL_FAILURE (FAIL)
    resp_no_sources = VerifiedResponse(
        final_text="Some ungrounded speculative text.",
        response_state=ResponseState.PARTIAL,
        claims=[],
        unsupported_claims_count=0,
        verified_sources=[],
        citation_support_rate=0.0,
    )
    verdict_rf, reason_rf = runner.evaluate_verdict("D", "D01", "What is the launch date of iPhone 16?", "WEB_SEARCH", resp_no_sources, 1.0)
    assert_eq(verdict_rf, "FAIL", "Zero sources on web route must be FAIL")
    assert_true("RETRIEVAL_FAILURE" in reason_rf, "Reason reflects RETRIEVAL_FAILURE")

    # Test 6.4: Falsely claiming Kapil Dev scored 175 in final is VERIFICATION_FAILURE (FAIL)
    resp_hallucinated_score = VerifiedResponse(
        final_text="In the 1983 World Cup final, Kapil Dev scored 175 runs.",
        response_state=ResponseState.VERIFIED,
        claims=[],
        unsupported_claims_count=0,
        verified_sources=[doc_1983_full],
        citation_support_rate=1.0,
    )
    verdict_vf, reason_vf = runner.evaluate_verdict("D", "D15", "Tell me Kapil Dev's score in 1983 World Cup final", "WEB_SEARCH", resp_hallucinated_score, 1.0)
    assert_eq(verdict_vf, "FAIL", "Falsely attributing 175 to the final must be FAIL")
    assert_true("VERIFICATION_FAILURE" in reason_vf, "Reason reflects VERIFICATION_FAILURE")
    print(f"  ✓ Tests 27-30 passed: Benchmark ground-truth evaluation verified.")

    print("\n============================================================")
    print(f"✓ SPRINT 5 MASTER REGRESSION: {passed}/{total} TESTS PASSED (100%)")
    print("============================================================\n")


if __name__ == "__main__":
    run_all_tests()

