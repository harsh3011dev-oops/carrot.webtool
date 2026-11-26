"""
PROJECT NOVA - SPRINT 5.3.1: FINAL ANSWER SANITIZATION & TRUTH-STATE AUDIT SUITE
================================================================================
Comprehensive adversarial audit validating:
1. Complete sanitization of unsupported claims across all truth states.
2. Complete sanitization of contradicted claims (zero false statements pass through).
3. Zero-claim handling (empty or non-assertive text never defaults to VERIFIED).
4. Truth-state fidelity across Hybrid and Strict modes.
5. Decomposed citation precision, coverage, and claim support rate consistency.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from grounding.schemas import ResponseState
from grounding.verifier import ClaimVerifier
from retriever.models import ExtractedDocument

passed_tests = 0
total_tests = 0


def assert_true(condition: bool, msg: str):
    global passed_tests, total_tests
    total_tests += 1
    if not condition:
        print(f"  ❌ FAILED: {msg}")
        raise AssertionError(msg)
    passed_tests += 1
    print(f"  ✓ PASSED: {msg}")


def assert_eq(actual, expected, msg: str):
    assert_true(actual == expected, f"{msg} (Expected: {expected}, Got: {actual})")


def run_sanitization_audit_suite():
    global passed_tests, total_tests
    hybrid_verifier = ClaimVerifier(mode="hybrid")
    strict_verifier = ClaimVerifier(mode="strict")

    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.3.1: SANITIZATION & SAFETY AUDIT SUITE")
    print("=" * 70)

    # Standard reference evidence
    docs = [
        ExtractedDocument(
            title="ICC Cricket World Cup 2023",
            url="https://cricinfo.com/wc2023",
            clean_text="Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets in Ahmedabad. Travis Head scored 137 runs.",
            source_index=1,
            relevance_score=0.98,
        ),
        ExtractedDocument(
            title="Apple Hardware Launch 2024",
            url="https://apple.com/iphone-16",
            clean_text="The base iPhone 16 is priced at Rs 79,900 in India. It features the A18 Bionic chip.",
            source_index=2,
            relevance_score=0.95,
        ),
    ]

    # -------------------------------------------------------------------------
    # TEST 1: 100% VERIFIED CLEAN PASS
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Clean 100% verified response...")
    resp_clean = "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]."
    a1 = hybrid_verifier.audit_and_verify_response("Who won 2023 World Cup?", resp_clean, docs)
    assert_eq(a1.response_state, ResponseState.VERIFIED, "Case 1: Clean response receives VERIFIED")
    assert_eq(a1.unsupported_claims_count, 0, "Case 1: Zero unsupported claims")
    assert_true("Note: Some statements" not in a1.final_text, "Case 1: No disclaimer on clean verified answer")
    assert_true("Australia won" in a1.final_text, "Case 1: Verified content intact")

    # -------------------------------------------------------------------------
    # TEST 2: 1 VERIFIED + 1 UNSUPPORTED (PRUNED)
    # -------------------------------------------------------------------------
    print("\n[TEST 2] 1 Verified + 1 Unsupported claim...")
    resp_mix_unsupported = (
        "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]. "
        "The Australian team was awarded 500 million dollars and celebrated on Mars."
    )
    a2 = hybrid_verifier.audit_and_verify_response("Who won 2023 World Cup?", resp_mix_unsupported, docs)
    assert_eq(a2.response_state, ResponseState.PARTIAL, "Case 2: Mixed support receives PARTIAL")
    assert_true("Australia won" in a2.final_text, "Case 2: Verified proposition retained")
    assert_true("500 million dollars" not in a2.final_text, "Case 2: Unsupported money pruned")
    assert_true("celebrated on Mars" not in a2.final_text, "Case 2: Unsupported Mars celebration pruned")
    assert_true("Note: Some statements" in a2.final_text, "Case 2: Disclaimer attached to partial output")

    # -------------------------------------------------------------------------
    # TEST 3: 1 VERIFIED + 1 CONTRADICTED (PRUNED)
    # -------------------------------------------------------------------------
    print("\n[TEST 3] 1 Verified + 1 Contradicted claim...")
    resp_mix_contradiction = (
        "The base iPhone 16 is priced at Rs 79,900 in India [2]. "
        "However, some stores sell the base iPhone 16 priced at Rs 59,900 in India [2]."
    )
    a3 = hybrid_verifier.audit_and_verify_response("iPhone 16 price", resp_mix_contradiction, docs)
    assert_eq(a3.response_state, ResponseState.PARTIAL, "Case 3: Mixed with contradiction receives PARTIAL")
    assert_true("Rs 79,900" in a3.final_text, "Case 3: Corroborated price retained")
    assert_true("Rs 59,900" not in a3.final_text, "Case 3: Contradicted price (59,900) strictly PRUNED")
    assert_true("Note: Some statements" in a3.final_text, "Case 3: Partial disclaimer attached")

    # -------------------------------------------------------------------------
    # TEST 4: 2 VERIFIED + 2 UNSUPPORTED (PRUNED)
    # -------------------------------------------------------------------------
    print("\n[TEST 4] 2 Verified + 2 Unsupported claims...")
    resp_2v_2u = (
        "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]. "
        "Travis Head scored 137 runs [1]. "
        "The ICC president resigned immediately following the match. "
        "The stadium was completely dismantled the next morning."
    )
    a4 = hybrid_verifier.audit_and_verify_response("2023 final summary", resp_2v_2u, docs)
    assert_eq(a4.response_state, ResponseState.PARTIAL, "Case 4: 2v+2u receives PARTIAL")
    assert_true("Australia won" in a4.final_text and "Travis Head scored 137" in a4.final_text, "Case 4: Both verified claims retained")
    assert_true("president resigned" not in a4.final_text, "Case 4: First unsupported claim pruned")
    assert_true("dismantled" not in a4.final_text, "Case 4: Second unsupported claim pruned")

    # -------------------------------------------------------------------------
    # TEST 5 & 6: 100% UNSUPPORTED (STRICT VS HYBRID)
    # -------------------------------------------------------------------------
    print("\n[TEST 5 & 6] 100% Unsupported response across modes...")
    resp_100_unsupported = "Intergalactic spaceships were discovered orbiting Jupiter."
    a5_strict = strict_verifier.audit_and_verify_response("Spaceships", resp_100_unsupported, docs)
    assert_eq(a5_strict.response_state, ResponseState.ABSTAIN, "Case 5: Strict mode 100% unsupported triggers ABSTAIN")
    assert_true("Strict RAG Mode" in a5_strict.final_text, "Case 5: Strict RAG notice present")

    a6_hybrid = hybrid_verifier.audit_and_verify_response("Spaceships", resp_100_unsupported, docs)
    assert_eq(a6_hybrid.response_state, ResponseState.UNVERIFIED, "Case 6: Hybrid mode 100% unsupported triggers UNVERIFIED")
    assert_true("Warning: Response contains unverified" in a6_hybrid.final_text, "Case 6: Warning banner attached")

    # -------------------------------------------------------------------------
    # TEST 7 & 8: 100% CONTRADICTED (STRICT VS HYBRID)
    # -------------------------------------------------------------------------
    print("\n[TEST 7 & 8] 100% Contradicted response across modes...")
    resp_100_contra = "The base iPhone 16 is priced at Rs 59,900 in India [2]."
    a7_strict = strict_verifier.audit_and_verify_response("iPhone 16 price", resp_100_contra, docs)
    assert_eq(a7_strict.response_state, ResponseState.ABSTAIN, "Case 7: Strict mode 100% contradiction triggers ABSTAIN")

    a8_hybrid = hybrid_verifier.audit_and_verify_response("iPhone 16 price", resp_100_contra, docs)
    assert_eq(a8_hybrid.response_state, ResponseState.ABSTAIN, "Case 8: Hybrid mode 100% contradiction triggers ABSTAIN")
    assert_true("contradicts the generated claims" in a8_hybrid.final_text, "Case 8: Contradiction disclosure emitted")

    # -------------------------------------------------------------------------
    # TEST 9 & 10: EMPTY STRING RESPONSE (STRICT VS HYBRID)
    # -------------------------------------------------------------------------
    print("\n[TEST 9 & 10] Empty response string handling...")
    a9_strict = strict_verifier.audit_and_verify_response("Query", "", docs)
    assert_eq(a9_strict.response_state, ResponseState.ABSTAIN, "Case 9: Strict mode empty response triggers ABSTAIN")

    a10_hybrid = hybrid_verifier.audit_and_verify_response("Query", "   ", docs)
    assert_eq(a10_hybrid.response_state, ResponseState.UNVERIFIED, "Case 10: Hybrid mode empty response triggers UNVERIFIED (never VERIFIED)")
    assert_true("No factual claims" in a10_hybrid.final_text, "Case 10: Clear unverified notice for empty text")

    # -------------------------------------------------------------------------
    # TEST 11 & 12: 0 CLAIMS FROM NON-ASSERTIVE PROSE (STRICT VS HYBRID)
    # -------------------------------------------------------------------------
    print("\n[TEST 11 & 12] Zero claims extracted from non-assertive prose...")
    non_assertive = "Hello! Thank you very much. I hope you are having a wonderful day."
    a11_strict = strict_verifier.audit_and_verify_response("Greeting", non_assertive, docs)
    assert_eq(a11_strict.response_state, ResponseState.ABSTAIN, "Case 11: Strict mode non-assertive triggers ABSTAIN")

    a12_hybrid = hybrid_verifier.audit_and_verify_response("Greeting", non_assertive, docs)
    assert_eq(a12_hybrid.response_state, ResponseState.UNVERIFIED, "Case 12: Hybrid mode non-assertive triggers UNVERIFIED (never VERIFIED)")

    # -------------------------------------------------------------------------
    # TEST 13: MULTIPLE VERIFIED CLAIMS ORDERING PRESERVED
    # -------------------------------------------------------------------------
    print("\n[TEST 13] Order preservation of multiple verified claims...")
    resp_ordered = (
        "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]. "
        "The winning coach celebrated with a special pizza on the moon. "
        "Travis Head scored 137 runs [1]."
    )
    a13 = hybrid_verifier.audit_and_verify_response("2023 World Cup", resp_ordered, docs)
    pos_aus = a13.final_text.find("Australia won")
    pos_head = a13.final_text.find("Travis Head scored 137")
    assert_true(pos_aus != -1 and pos_head != -1 and pos_aus < pos_head, "Case 13: Temporal sequence of verified claims preserved")
    assert_true("pizza on the moon" not in a13.final_text, "Case 13: Interleaved hallucination pruned")

    # -------------------------------------------------------------------------
    # TEST 14: CONTRADICTED NUMERICAL CLAIM COMPLETELY EXCISED
    # -------------------------------------------------------------------------
    print("\n[TEST 14] Contradicted numerical claim completely excised...")
    resp_contra_num = (
        "The base iPhone 16 features the A18 Bionic chip [2]. "
        "The base iPhone 16 is priced at Rs 35,000 in India [2]."
    )
    a14 = hybrid_verifier.audit_and_verify_response("iPhone 16 specs", resp_contra_num, docs)
    assert_true("A18 Bionic chip" in a14.final_text, "Case 14: Supported spec retained")
    assert_true("35,000" not in a14.final_text, "Case 14: Conflicting price (35,000) completely eliminated")

    # -------------------------------------------------------------------------
    # TEST 15: UNSUPPORTED ENTITY MISMATCH COMPLETELY EXCISED
    # -------------------------------------------------------------------------
    print("\n[TEST 15] Unsupported entity mismatch completely excised...")
    resp_entity_mismatch = (
        "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]. "
        "Lionel Messi scored 3 goals during the cricket match."
    )
    a15 = hybrid_verifier.audit_and_verify_response("Cricket final", resp_entity_mismatch, docs)
    assert_true("Lionel Messi" not in a15.final_text, "Case 15: Entity mismatch (Lionel Messi) pruned")

    # -------------------------------------------------------------------------
    # TEST 16: WARNING DISCLAIMER PRESENT ON ALL PARTIAL OUTPUTS
    # -------------------------------------------------------------------------
    print("\n[TEST 16] Warning disclaimer present on all PARTIAL outputs...")
    assert_true("Note: Some statements in this response could not be fully verified" in a2.final_text, "Case 16a: Disclaimer on a2")
    assert_true("Note: Some statements in this response could not be fully verified" in a3.final_text, "Case 16b: Disclaimer on a3")
    assert_true("Note: Some statements in this response could not be fully verified" in a4.final_text, "Case 16c: Disclaimer on a4")

    # -------------------------------------------------------------------------
    # TEST 17: WARNING DISCLAIMER ABSENT ON 100% VERIFIED OUTPUTS
    # -------------------------------------------------------------------------
    print("\n[TEST 17] Warning disclaimer absent on 100% VERIFIED outputs...")
    assert_true("Note: Some statements" not in a1.final_text, "Case 17: Zero warning banners on verified output")

    # -------------------------------------------------------------------------
    # TEST 18: DECOMPOSED CITATION & COVERAGE METRICS CONSISTENCY
    # -------------------------------------------------------------------------
    print("\n[TEST 18] Citation and coverage metrics consistency after pruning...")
    # In a2: 2 claims, 1 supported with citation [1], 1 unsupported without citation
    assert_eq(a2.claim_support_rate, 0.5, "Case 18: Claim support rate is 0.5")
    assert_eq(a2.citation_precision, 1.0, "Case 18: Citation precision is 1.0 (valid citation on supported claim)")
    assert_eq(a2.citation_coverage, 1.0, "Case 18: Citation coverage is 1.0")

    print("\n" + "=" * 70)
    print(f"✓ SPRINT 5.3.1 SANITIZATION AUDIT SUITE: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_sanitization_audit_suite()
