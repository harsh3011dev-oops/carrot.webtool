"""
PROJECT NOVA - SPRINT 5.3: ANSWER SANITIZATION SUITE
====================================================
Validates that:
1. Unsupported hallucinations are excised or disclaimed from final output rather than merely appended with a warning.
2. Verified factual claims are preserved and clearly reported.
3. Truth state is accurately assigned (VERIFIED, PARTIAL, UNVERIFIED, ABSTAIN).
4. Citation precision, coverage, and support rates reflect sanitized propositions.
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


def run_sanitization_suite():
    global passed_tests, total_tests
    verifier = ClaimVerifier(mode="hybrid")

    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.3: ANSWER SANITIZATION TEST SUITE")
    print("=" * 70)

    doc_cup = [
        ExtractedDocument(
            title="2023 ICC World Cup Final Report",
            url="https://cricinfo.com/wc2023",
            clean_text="Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets in Ahmedabad.",
            source_index=1,
            relevance_score=0.96,
        )
    ]

    # Test 1: Mixed response containing verified fact + hallucination
    raw_mixed_response = (
        "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]. "
        "The winning squad was then awarded 500 million dollars and flew to the Moon on an Apollo rocket."
    )

    audit = verifier.audit_and_verify_response("Who won 2023 World Cup?", raw_mixed_response, doc_cup)

    # 1. State must be PARTIAL
    assert_eq(audit.response_state, ResponseState.PARTIAL, "Case 1: Response state is PARTIAL")
    
    # 2. Unsupported claim count is 1
    assert_eq(audit.unsupported_claims_count, 1, "Case 2: Exactly 1 unsupported claim identified")

    # 3. Verified claim retained in final_text
    assert_true("Australia won the 2023 ICC Men's Cricket World Cup" in audit.final_text, "Case 3: Verified claim retained in final text")

    # 4. Hallucination ("flew to the Moon") must be PRUNED from final_text
    assert_true("flew to the Moon" not in audit.final_text, "Case 4: Hallucinated claim ('flew to the Moon') pruned from final answer")
    assert_true("500 million dollars" not in audit.final_text, "Case 5: Hallucinated prize pruned from final answer")

    # 5. Warning banner attached
    assert_true("Note: Some statements in this response could not be fully verified" in audit.final_text, "Case 6: Verification notice banner attached")

    # 6. Decomposed metrics
    assert_eq(audit.claim_support_rate, 0.5, "Case 7: Claim support rate is 50%")
    assert_eq(audit.citation_precision, 1.0, "Case 8: Citation precision is 100% (the only cited statement was valid)")
    assert_eq(audit.citation_coverage, 1.0, "Case 9: Citation coverage is 100%")

    # Test 2: Clean 100% verified response
    clean_response = "Australia won the 2023 ICC Men's Cricket World Cup by defeating India by 6 wickets [1]."
    audit_clean = verifier.audit_and_verify_response("Who won 2023 World Cup?", clean_response, doc_cup)

    assert_eq(audit_clean.response_state, ResponseState.VERIFIED, "Case 10: Clean response is VERIFIED")
    assert_eq(audit_clean.unsupported_claims_count, 0, "Case 11: 0 unsupported claims")
    assert_eq(audit_clean.final_text, clean_response, "Case 12: final_text is unchanged clean response")
    assert_true("Note: Some statements" not in audit_clean.final_text, "Case 13: No partial warning banner attached")

    # Test 3: Completely unsupported response in strict mode must ABSTAIN
    strict_verifier = ClaimVerifier(mode="strict")
    audit_strict = strict_verifier.audit_and_verify_response("Random topic", "Completely unsubstantiated rumor about dragons.", doc_cup)
    assert_eq(audit_strict.response_state, ResponseState.ABSTAIN, "Case 14: Strict mode with unsupported claims triggers ABSTAIN")
    assert_true("Strict RAG Mode" in audit_strict.final_text, "Case 15: Strict RAG notice emitted")

    print("\n" + "=" * 70)
    print(f"✓ SPRINT 5.3 ANSWER SANITIZATION SUITE: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_sanitization_suite()
