"""
PROJECT NOVA - Sprint 3 Grounding & Truth Engine Comprehensive Regression Suite
================================================================================
Tests:
1. Atomic claim extraction and decomposition.
2. Individual claim verification against evidence (numbers, entities, dates).
3. Citation validation and citation support rate auditing ([1], [2], invalid [99]).
4. 4 Canonical Response States: VERIFIED, PARTIAL, UNVERIFIED, ABSTAIN.
5. Strict RAG Mode vs Hybrid Knowledge Policy.
6. End-to-end integration with NovaOrchestrator.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from grounding.schemas import ClaimVerification, ResponseState, VerifiedResponse
from grounding.verifier import ClaimVerifier
from retriever.models import ExtractedDocument
from main import NovaOrchestrator


def run_all_tests():
    verifier = ClaimVerifier(mode="hybrid")
    strict_verifier = ClaimVerifier(mode="strict")
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
    print("       PROJECT NOVA - SPRINT 3 REGRESSION TEST SUITE         ")
    print("============================================================\n")

    # ------------------------------------------------------------------
    # TEST SUITE 1: ATOMIC CLAIM EXTRACTION
    # ------------------------------------------------------------------
    print("[1/5] Testing Atomic Claim Extraction...")
    sample_answer = (
        "### Overview\n"
        "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]. "
        "The final match was played at Narendra Modi Stadium in Ahmedabad on November 19, 2023 [2]. "
        "Travis Head scored a match-winning 137 runs off 120 balls [1]. "
        "Based on the provided evidence, this was Australia's sixth World Cup title [2].\n\n"
        "Sources:\n[1] https://espncricinfo.com/match/1\n[2] https://icc-cricket.com"
    )
    claims = verifier.extract_claims(sample_answer)
    assert_eq(len(claims), 4, "Should extract exactly 4 atomic factual claims")
    assert_true("Australia won the 2023 ICC Men's Cricket World Cup" in claims[0], "Claim 1 matches winner")
    assert_true("Narendra Modi Stadium in Ahmedabad" in claims[1], "Claim 2 matches venue")
    assert_true("Travis Head scored a match-winning 137 runs" in claims[2], "Claim 3 matches player score")
    assert_true("sixth World Cup title" in claims[3], "Claim 4 matches title count")
    print(f"  ✓ Extracted {len(claims)} clean atomic claims without headers/sources.")

    # ------------------------------------------------------------------
    # TEST SUITE 2: INDIVIDUAL CLAIM VERIFICATION
    # ------------------------------------------------------------------
    print("\n[2/5] Testing Atomic Claim Corroboration...")
    mock_docs = [
        ExtractedDocument(
            url="https://cricinfo.com/wc2023",
            title="Australia claim sixth World Cup title with six-wicket victory over India",
            clean_text="Australia won the 2023 ICC Men's Cricket World Cup on November 19, 2023. Travis Head smashed 137 off 120 balls to lead Australia to victory by 6 wickets at Narendra Modi Stadium in Ahmedabad against India.",
            source_index=1,
            author="ESPNCricinfo",
            published_date="2023-11-19"
        ),
        ExtractedDocument(
            url="https://apple.com/iphone-16",
            title="Apple unveils iPhone 16 and iPhone 16 Plus",
            clean_text="Apple announced iPhone 16 on September 9, 2024, powered by the A18 Bionic chip. Pre-orders began September 13, and availability started September 20, 2024. Starting price is $799.",
            source_index=2,
            author="Apple PR",
            published_date="2024-09-09"
        )
    ]

    # Valid supported claim
    c1 = "Australia won the 2023 ICC Cricket World Cup by 6 wickets [1]."
    v1 = verifier.verify_single_claim(c1, mock_docs)
    assert_true(v1.is_supported, "True claim should be supported")
    assert_eq(v1.supporting_source_indices, [1], "Should be corroborated by Source 1")

    # Claim with hallucinated date/numbers
    c2 = "Australia won the World Cup on December 25, 2023 with 99 wickets [1]."
    v2 = verifier.verify_single_claim(c2, mock_docs)
    assert_true(not v2.is_supported, "Claim with conflicting numbers/dates must fail")

    # Claim about entity not in evidence
    c3 = "Samsung Galaxy S24 Ultra was released in January 2024 with Snapdragon 8 Gen 3 [1]."
    v3 = verifier.verify_single_claim(c3, mock_docs)
    assert_true(not v3.is_supported, "Unrelated entity must not be corroborated")
    print("  ✓ Verified supported vs unsupported atomic claims.")

    # ------------------------------------------------------------------
    # TEST SUITE 3: CITATION AUDITING
    # ------------------------------------------------------------------
    print("\n[3/5] Testing Bracketed Citation Auditing...")
    text_valid_citations = "Australia won the World Cup [1] and iPhone 16 was released in September 2024 [2]."
    rate, indices = verifier.verify_citations(text_valid_citations, mock_docs)
    assert_eq(rate, 1.0, "All citations valid")
    assert_eq(sorted(indices), [1, 2], "Indices [1, 2] verified")

    text_invalid_citations = "Australia won [1] but iPhone 16 was announced on Mars [99] and Jupiter [50]."
    rate_bad, indices_bad = verifier.verify_citations(text_invalid_citations, mock_docs)
    assert_true(rate_bad < 0.5, "Hallucinated citations [99], [50] must drop support rate")
    print("  ✓ Citation support rate accurately tracked.")

    # ------------------------------------------------------------------
    # TEST SUITE 4: 4 CANONICAL RESPONSE STATES & STRICT/HYBRID POLICIES
    # ------------------------------------------------------------------
    print("\n[4/5] Testing 4 Canonical Response States...")

    # State 1: VERIFIED
    good_resp = (
        "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]. "
        "Travis Head scored 137 runs to lead the team to victory [1]."
    )
    v_verified = verifier.audit_and_verify_response("Who won 2023 World Cup?", good_resp, mock_docs)
    assert_eq(v_verified.response_state, ResponseState.VERIFIED, "Fully corroborated answer must be VERIFIED")
    assert_eq(v_verified.unsupported_claims_count, 0, "No unsupported claims in verified answer")

    # State 2: PARTIAL
    mixed_resp = (
        "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]. "
        "The team also won a total cash prize of $500 million dollars and flew to the Moon afterwards."
    )
    v_partial = verifier.audit_and_verify_response("Who won 2023 World Cup?", mixed_resp, mock_docs)
    assert_eq(v_partial.response_state, ResponseState.PARTIAL, "Mixed supported/unsupported must be PARTIAL")
    assert_true(v_partial.unsupported_claims_count > 0, "Should flag unsupported claims")
    assert_true("Note: Some statements in this response could not be fully verified" in v_partial.final_text, "Partial warning appended")

    # State 3: UNVERIFIED (Hybrid Mode with zero docs)
    internal_resp = "Photosynthesis is the process by which green plants use sunlight to synthesize nutrients."
    v_unverified = verifier.audit_and_verify_response("What is photosynthesis?", internal_resp, docs=[], is_internal_generation=True)
    assert_eq(v_unverified.response_state, ResponseState.UNVERIFIED, "Parametric generation in hybrid mode is UNVERIFIED")
    assert_true("UNVERIFIED - PARAMETRIC KNOWLEDGE" in v_unverified.final_text, "Banner must disclose unverified status")

    # Strict Mode on zero docs must ABSTAIN
    v_strict_zero = strict_verifier.audit_and_verify_response("What is photosynthesis?", internal_resp, docs=[], is_internal_generation=True)
    assert_eq(v_strict_zero.response_state, ResponseState.ABSTAIN, "Strict mode without docs must ABSTAIN")

    # State 4: ABSTAIN (Explicit refusal pattern)
    refusal_resp = "The provided evidence does not contain sufficient information to answer the question."
    v_abstain = verifier.audit_and_verify_response("Who won 2030 World Cup?", refusal_resp, mock_docs)
    assert_eq(v_abstain.response_state, ResponseState.ABSTAIN, "Explicit refusal must map to ABSTAIN")
    print("  ✓ All 4 states (VERIFIED, PARTIAL, UNVERIFIED, ABSTAIN) validated across hybrid & strict modes.")

    # ------------------------------------------------------------------
    # TEST SUITE 5: ORCHESTRATOR INTEGRATION & MACHINE-READABLE BADGES
    # ------------------------------------------------------------------
    print("\n[5/5] Testing Orchestrator Truth State Dispatch Integration...")
    orchestrator = NovaOrchestrator(verifier_mode="hybrid")
    
    # Internal LLM route test
    result_internal = orchestrator.process_query("What is the chemical formula for water?")
    assert_true(result_internal is not None, "Process query returns VerifiedResponse")
    assert_eq(result_internal.response_state, ResponseState.UNVERIFIED, "Internal fast-path/LLM returns UNVERIFIED")

    print("\n============================================================")
    print(f"✓ SPRINT 3 REGRESSION SUITE: {passed}/{total} TESTS PASSED (100%)")
    print("============================================================\n")


if __name__ == "__main__":
    run_all_tests()

