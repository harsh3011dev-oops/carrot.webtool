"""
PROJECT NOVA - Sprint 5 Phase 2 Acceptance Test Suite
=====================================================
Validates Claim-Level Proposition Proximity Verifier:
1. Kapil Dev 1983 Final Test (Eliminates cross-paragraph false corroboration)
2. Unrelated Numerical Match Prevention (Units vs Price)
3. Entity Match Alone Cannot Verify Missing Attribute
4. Contradictory Evidence Detection
5. Truth-State & Citation Support Rate Metric Integrity
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from grounding.schemas import ResponseState
from grounding.verifier import ClaimVerifier
from retriever.models import ExtractedDocument


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
    print("       PROJECT NOVA - SPRINT 5 PHASE 2 ACCEPTANCE SUITE     ")
    print("============================================================\n")

    verifier = ClaimVerifier(mode="hybrid")

    # ------------------------------------------------------------------
    # TEST 1: KAPIL DEV 1983 WORLD CUP FINAL (ELIMINATES CROSS-PARAGRAPH FUSION)
    # ------------------------------------------------------------------
    print("[1/5] Testing Proposition Proximity & Cross-Paragraph Isolation...")
    doc_1983 = ExtractedDocument(
        source_index=1,
        title="1983 Cricket World Cup Tournament Summary",
        url="https://espncricinfo.com/series/prudential-world-cup-1983",
        clean_text=(
            "## Group Stage: India vs Zimbabwe\n"
            "India faced Zimbabwe at Tunbridge Wells. In one of the greatest ODI innings, "
            "Kapil Dev scored an unbeaten 175 not out off 138 balls to rescue India from 17 for 5.\n\n"
            "## The Grand Final: India vs West Indies\n"
            "The 1983 World Cup final was played at Lord's on June 25, 1983. India batted first "
            "and were dismissed for 183. In the final, Kapil Dev scored 15 runs before taking a sensational "
            "running catch to dismiss Viv Richards. India won the match by 43 runs to lift their first World Cup title."
        )
    )

    # False claim: fusing 175 from Zimbabwe match into the Final
    false_claim_final = "In the 1983 World Cup final, Kapil Dev scored 175 runs [1]."
    v_false = verifier.verify_single_claim(false_claim_final, [doc_1983])
    assert_true(not v_false.is_supported, "Kapil Dev's score of 175 from Zimbabwe match must NOT verify final score")
    assert_true(v_false.contradiction_detected or len(v_false.supporting_source_indices) == 0, "Must detect contradiction or lack of support")

    # True claim for final
    true_claim_final = "Kapil Dev scored 15 runs in the 1983 World Cup final [1]."
    v_true_final = verifier.verify_single_claim(true_claim_final, [doc_1983])
    assert_true(v_true_final.is_supported, "Exact score in the final must be verified")
    assert_eq(v_true_final.supporting_source_indices, [1], "Corroborated by Source 1")

    # True claim for Zimbabwe
    true_claim_zimbabwe = "Kapil Dev scored 175 not out against Zimbabwe [1]."
    v_true_zim = verifier.verify_single_claim(true_claim_zimbabwe, [doc_1983])
    assert_true(v_true_zim.is_supported, "Score against Zimbabwe must be verified in its proper context")
    print("  ✓ Cross-paragraph proposition leakage eliminated: Kapil Dev 175 correctly isolated from 1983 final!")

    # ------------------------------------------------------------------
    # TEST 2: UNRELATED NUMERICAL MATCH (UNITS VS PRICE)
    # ------------------------------------------------------------------
    print("\n[2/5] Testing Unrelated Numerical Match Rejection...")
    doc_gpu = ExtractedDocument(
        source_index=2,
        title="NVIDIA DGX Spark Enterprise Shipments",
        url="https://nvidia.com/enterprise/news",
        clean_text=(
            "NVIDIA today announced that OEM partners have shipped over 5090 units of the DGX Spark "
            "system worldwide. The workstation features 128GB unified memory and operates at 3.8 GHz."
        )
    )
    false_claim_price = "The NVIDIA DGX Spark costs $5090."
    v_price = verifier.verify_single_claim(false_claim_price, [doc_gpu])
    assert_true(not v_price.is_supported, "Number of units shipped (5090) must not verify price ($5090)")
    print("  ✓ Unrelated numerical presence rejected when attribute semantics conflict!")

    # ------------------------------------------------------------------
    # TEST 3: ENTITY MATCH ALONE CANNOT VERIFY MISSING ATTRIBUTE
    # ------------------------------------------------------------------
    print("\n[3/5] Testing Entity Match Without Required Attribute...")
    doc_isro = ExtractedDocument(
        source_index=3,
        title="ISRO Chandrayaan-3 Mission Overview",
        url="https://isro.gov.in/chandrayaan3",
        clean_text=(
            "Chandrayaan-3 is the third lunar exploration mission developed by the Indian Space "
            "Research Organisation (ISRO). The spacecraft was launched from Satish Dhawan Space Centre."
        )
    )
    claim_missing_attr = "Chandrayaan-3 landed on the Moon on August 23, 2023 [3]."
    v_isro = verifier.verify_single_claim(claim_missing_attr, [doc_isro])
    assert_true(not v_isro.is_supported, "Missing landing date attribute must result in unsupported status")
    print("  ✓ Entity match alone strictly rejected when requested attribute is absent!")

    # ------------------------------------------------------------------
    # TEST 4: CONTRADICTORY EVIDENCE DETECTION
    # ------------------------------------------------------------------
    print("\n[4/5] Testing Direct Contradiction Detection...")
    doc_iphone = ExtractedDocument(
        source_index=4,
        title="Apple iPhone 16 Official Price in India",
        url="https://apple.com/in/iphone-16",
        clean_text="The iPhone 16 base model starts at Rs 79,900 for the 128GB storage configuration in India."
    )
    claim_contradictory = "The iPhone 16 base model is priced at Rs 59,900 in India."
    v_contradiction = verifier.verify_single_claim(claim_contradictory, [doc_iphone])
    assert_true(not v_contradiction.is_supported, "Contradictory price must not be supported")
    assert_true(v_contradiction.contradiction_detected, "Contradiction flag must be set")
    print("  ✓ Direct factual contradiction detected and flagged!")

    # ------------------------------------------------------------------
    # TEST 5: TRUTH STATE INTEGRITY & CITATION METRICS
    # ------------------------------------------------------------------
    print("\n[5/5] Testing Response Truth State & Citation Metric Linkage...")
    mixed_response_text = (
        "Kapil Dev scored 15 runs in the 1983 World Cup final [1]. "
        "In the 1983 World Cup final, Kapil Dev scored 175 runs [1]."
    )
    audit = verifier.audit_and_verify_response("What was Kapil Dev's score in the 1983 final?", mixed_response_text, [doc_1983])
    assert_eq(audit.response_state, ResponseState.PARTIAL, "Mixed supported + contradictory response must NOT be VERIFIED")
    assert_eq(audit.unsupported_claims_count, 1, "Must accurately report 1 unsupported claim")
    assert_true(audit.citation_support_rate == 0.5, f"Citation support rate must reflect 1/2 supported citations (got {audit.citation_support_rate})")
    print("  ✓ Truth-state is reliably downgraded to PARTIAL and citation rate is exactly 50%!")

    print("\n============================================================")
    print(f"✓ SPRINT 5 PHASE 2: {passed}/{total} ACCEPTANCE TESTS PASSED (100%)")
    print("============================================================\n")


if __name__ == "__main__":
    run_all_tests()

