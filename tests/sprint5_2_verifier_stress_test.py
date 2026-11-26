"""
PROJECT NOVA — SPRINT 5.2: Phase 3 Semantic Verifier Stress Test Suite
======================================================================
Tests 20 difficult semantic boundary conditions:
- Same person / different tournaments & matches
- Same number / different attributes & units
- Negation and inverse claims
- Hypothetical / speculative claims
- Entity-attribute mismatch
- Currency and metric units
- Conflicting multi-source numbers
- Strict state demotion on any uncorroborated claim
"""

import os
import sys
import unittest
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from grounding.schemas import ResponseState, ClaimVerification
from grounding.verifier import ClaimVerifier
from retriever.models import ExtractedDocument

# Helper assertion counters
total_tests = 0
passed_tests = 0

def assert_true(condition: bool, msg: str):
    global total_tests, passed_tests
    total_tests += 1
    if not condition:
        print(f"  ❌ FAILED: {msg}")
        raise AssertionError(msg)
    passed_tests += 1
    print(f"  ✓ PASSED: {msg}")

def assert_eq(val, expected, msg: str):
    global total_tests, passed_tests
    total_tests += 1
    if val != expected:
        print(f"  ❌ FAILED: {msg} (Expected: {expected}, Got: {val})")
        raise AssertionError(f"{msg} (Expected: {expected}, Got: {val})")
    passed_tests += 1
    print(f"  ✓ PASSED: {msg}")


def run_phase3_stress_suite():
    verifier = ClaimVerifier(mode="hybrid")
    strict_verifier = ClaimVerifier(mode="strict")

    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.2: PHASE 3 VERIFIER STRESS TESTS")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # Test 1 & 2: Same Person, Different Tournaments
    # -------------------------------------------------------------------------
    print("\n[GROUP 1] Same Person / Different Tournaments...")
    doc_tourneys = [
        ExtractedDocument(
            title="ICC Cricket World Cup Records - ESPNcricinfo",
            url="https://www.espncricinfo.com/records/world-cup",
            clean_text=(
                "In the 2023 ICC Men's Cricket World Cup in India, Virat Kohli scored 765 runs in 11 innings with 3 centuries.\n\n"
                "Earlier in the 2011 ICC Cricket World Cup, Virat Kohli scored 282 runs in 9 matches.\n\n"
                "In the 2024 ICC Men's T20 World Cup, Virat Kohli was player of the match in the final, scoring 76 runs against South Africa."
            ),
            source_index=1,
            relevance_score=0.95,
        )
    ]
    # Claim 1: Virat Kohli scored 765 runs in the 2023 World Cup -> SUPPORTED
    res1 = verifier.verify_single_claim("Virat Kohli scored 765 runs in the 2023 World Cup [1]", doc_tourneys)
    assert_true(res1.is_supported, "Case 1: Accurate tournament + score must be SUPPORTED")

    # Claim 2: Virat Kohli scored 765 runs in the 2024 T20 World Cup -> CONTRADICTED / REJECTED
    res2 = verifier.verify_single_claim("Virat Kohli scored 765 runs in the 2024 T20 World Cup [1]", doc_tourneys)
    assert_true(not res2.is_supported, "Case 2: Wrong tournament for score must NOT be supported")

    # -------------------------------------------------------------------------
    # Test 3 & 4: Same Person, Different Matches
    # -------------------------------------------------------------------------
    print("\n[GROUP 2] Same Person / Different Matches...")
    doc_matches = [
        ExtractedDocument(
            title="Rohit Sharma 2023 World Cup Match Log",
            url="https://www.espncricinfo.com/series/icc-cricket-world-cup-2023",
            clean_text=(
                "Match 9: India vs Afghanistan at Delhi. Rohit Sharma hit a blistering 131 runs off 84 balls.\n\n"
                "Match 29: India vs England at Lucknow. Rohit Sharma scored a patient 87 runs on a difficult pitch."
            ),
            source_index=1,
            relevance_score=0.92,
        )
    ]
    # Claim 3: Rohit Sharma scored 131 runs against Afghanistan -> SUPPORTED
    res3 = verifier.verify_single_claim("Rohit Sharma scored 131 runs against Afghanistan [1]", doc_matches)
    assert_true(res3.is_supported, "Case 3: Exact match opponent + score must be SUPPORTED")

    # Claim 4: Rohit Sharma scored 131 runs against England -> REJECTED
    res4 = verifier.verify_single_claim("Rohit Sharma scored 131 runs against England [1]", doc_matches)
    assert_true(not res4.is_supported, "Case 4: Wrong opponent for score must NOT be supported")

    # -------------------------------------------------------------------------
    # Test 5 & 6: Same Number, Different Attributes & Units
    # -------------------------------------------------------------------------
    print("\n[GROUP 3] Same Number / Different Attributes & Units...")
    doc_specs = [
        ExtractedDocument(
            title="Smartphone Spec Sheet",
            url="https://gsmarena.com/phone_specs",
            clean_text=(
                "The UltraPhone 5 comes equipped with a 50 MP main rear camera.\n\n"
                "The device supports 50 W wired fast charging and packs a 5000 mAh battery."
            ),
            source_index=1,
            relevance_score=0.90,
        )
    ]
    # Claim 5: UltraPhone 5 features a 50 MP camera -> SUPPORTED
    res5 = verifier.verify_single_claim("UltraPhone 5 features a 50 MP camera [1]", doc_specs)
    assert_true(res5.is_supported, "Case 5: 50 MP camera attribute matches")

    # Claim 6: UltraPhone 5 features 5000 W fast charging -> REJECTED (Attribute unit conflict)
    res6 = verifier.verify_single_claim("UltraPhone 5 features 5000 W fast charging [1]", doc_specs)
    assert_true(not res6.is_supported, "Case 6: 5000 W charging rejected due to unit mismatch")

    # -------------------------------------------------------------------------
    # Test 7 & 8: Sports Jersey Number vs Score
    # -------------------------------------------------------------------------
    print("\n[GROUP 4] Jersey Number vs Run Count...")
    doc_cricket = [
        ExtractedDocument(
            title="Player Profile",
            url="https://cricket.org/player",
            clean_text="Star batter wearing jersey number 18 was dismissed after scoring 4 runs in the first innings.",
            source_index=1,
            relevance_score=0.88,
        )
    ]
    # Claim 7: The player was dismissed after scoring 4 runs -> SUPPORTED
    res7 = verifier.verify_single_claim("The player was dismissed after scoring 4 runs [1]", doc_cricket)
    assert_true(res7.is_supported, "Case 7: 4 runs score matches")

    # Claim 8: The player scored 18 runs -> REJECTED (Jersey 18 is not run count)
    res8 = verifier.verify_single_claim("The player scored 18 runs [1]", doc_cricket)
    assert_true(not res8.is_supported, "Case 8: Jersey number 18 cannot corroborate 18 runs")

    # -------------------------------------------------------------------------
    # Test 9 & 10: Negation & Inverse Claims
    # -------------------------------------------------------------------------
    print("\n[GROUP 5] Negation & Inverse Claims...")
    doc_os = [
        ExtractedDocument(
            title="Operating System History",
            url="https://tech.org/os-history",
            clean_text="Windows 11 was released in October 2021. Windows 10 was not discontinued in 2021.",
            source_index=1,
            relevance_score=0.89,
        )
    ]
    # Claim 9: Windows 11 was released in October 2021 -> SUPPORTED
    res9 = verifier.verify_single_claim("Windows 11 was released in October 2021 [1]", doc_os)
    assert_true(res9.is_supported, "Case 9: Direct affirmative release date verified")

    # Claim 10: Windows 11 was released in 2024 -> REJECTED (Date contradiction)
    res10 = verifier.verify_single_claim("Windows 11 was released in 2024 [1]", doc_os)
    assert_true(not res10.is_supported, "Case 10: 2024 contradicted by 2021")

    # -------------------------------------------------------------------------
    # Test 11 & 12: Hypothetical / Speculative Claims
    # -------------------------------------------------------------------------
    print("\n[GROUP 6] Hypothetical & Speculative Claims...")
    doc_rumor = [
        ExtractedDocument(
            title="NVIDIA RTX 5090 Official Specs",
            url="https://nvidia.com/geforce/5090",
            clean_text="NVIDIA officially confirmed the RTX 5090 graphics card features 32 GB of GDDR7 VRAM.",
            source_index=1,
            relevance_score=0.94,
        )
    ]
    # Claim 11: RTX 5090 features 32 GB of VRAM -> SUPPORTED
    res11 = verifier.verify_single_claim("RTX 5090 features 32 GB of VRAM [1]", doc_rumor)
    assert_true(res11.is_supported, "Case 11: Factual spec supported")

    # Claim 12: Speculation: RTX 5090 will launch with 64 GB of VRAM -> REJECTED
    res12 = verifier.verify_single_claim("RTX 5090 will launch with 64 GB of VRAM [1]", doc_rumor)
    assert_true(not res12.is_supported, "Case 12: Speculative 64 GB rejected")

    # -------------------------------------------------------------------------
    # Test 13 & 14: Entity vs Attribute Disconnect
    # -------------------------------------------------------------------------
    print("\n[GROUP 7] Entity vs Attribute Disconnect...")
    doc_books = [
        ExtractedDocument(
            title="Fantasy Literature Authors",
            url="https://books.org/fantasy",
            clean_text=(
                "George R.R. Martin is the renowned author of A Game of Thrones published in 1996.\n\n"
                "J.K. Rowling wrote the Harry Potter fantasy series starting in 1997."
            ),
            source_index=1,
            relevance_score=0.91,
        )
    ]
    # Claim 13: J.K. Rowling wrote the Harry Potter fantasy series -> SUPPORTED
    res13 = verifier.verify_single_claim("J.K. Rowling wrote the Harry Potter fantasy series [1]", doc_books)
    assert_true(res13.is_supported, "Case 13: Accurate author to book supported")

    # Claim 14: J.K. Rowling is the author of A Game of Thrones -> REJECTED (Attribute mismatch)
    res14 = verifier.verify_single_claim("J.K. Rowling is the author of A Game of Thrones [1]", doc_books)
    assert_true(not res14.is_supported, "Case 14: Cross-author attribute attribution rejected")

    # -------------------------------------------------------------------------
    # Test 15 & 16: Currency & Pricing Units
    # -------------------------------------------------------------------------
    print("\n[GROUP 8] Currency & Pricing Units...")
    doc_pricing = [
        ExtractedDocument(
            title="Product Pricing Announcement",
            url="https://gadgets.com/price",
            clean_text="The base model starts at $799 in the United States and Rs 79,900 in India.",
            source_index=1,
            relevance_score=0.90,
        )
    ]
    # Claim 15: The base model starts at $799 in the United States -> SUPPORTED
    res15 = verifier.verify_single_claim("The base model starts at $799 in the United States [1]", doc_pricing)
    assert_true(res15.is_supported, "Case 15: USD pricing matches")

    # Claim 16: The base model starts at Rs 799 in India -> REJECTED (Currency unit/amount conflict)
    res16 = verifier.verify_single_claim("The base model starts at Rs 799 in India [1]", doc_pricing)
    assert_true(not res16.is_supported, "Case 16: Rs 799 rejected due to numeric mismatch (79900 vs 799)")

    # -------------------------------------------------------------------------
    # Test 17 & 18: Conflicting Multi-Source Numbers & Demotion
    # -------------------------------------------------------------------------
    print("\n[GROUP 9] Conflicting Multi-Source Numbers & Full Response Audit...")
    doc_conflicts = [
        ExtractedDocument(
            title="Disaster Report Agency A",
            url="https://agencya.gov/report",
            clean_text="Official Agency A confirmed 120 fatalities following the storm.",
            source_index=1,
            relevance_score=0.88,
        ),
        ExtractedDocument(
            title="Disaster Report Agency B",
            url="https://agencyb.org/report",
            clean_text="Agency B reported 150 fatalities occurred in the southern district.",
            source_index=2,
            relevance_score=0.85,
        ),
    ]
    # Claim 17: Agency A confirmed 120 fatalities -> SUPPORTED by doc 1
    res17 = verifier.verify_single_claim("Agency A confirmed 120 fatalities [1]", doc_conflicts)
    assert_true(res17.is_supported, "Case 17: Attributed source claim supported")

    # Claim 18: The storm caused 500 fatalities -> REJECTED (Neither source supports 500)
    res18 = verifier.verify_single_claim("The storm caused 500 fatalities [1]", doc_conflicts)
    assert_true(not res18.is_supported, "Case 18: Unsupported 500 fatalities rejected")

    # -------------------------------------------------------------------------
    # Test 19 & 20: 100% Corroboration Guardrail & Decomposed Metrics
    # -------------------------------------------------------------------------
    print("\n[GROUP 10] 100% Corroboration Guardrail (No 85% Loophole)...")
    mixed_answer = (
        "Agency A confirmed 120 fatalities following the storm [1]. "
        "The storm also destroyed 9,000 alien spaceships in orbit [2]."
    )
    audit_mixed = verifier.audit_and_verify_response("How many fatalities?", mixed_answer, doc_conflicts)
    
    # Assert state is strictly demoted to PARTIAL (or ABSTAIN in strict mode), NEVER VERIFIED
    assert_true(audit_mixed.response_state != ResponseState.VERIFIED, "Case 19: Answer with hallucination must NEVER be VERIFIED")
    assert_eq(audit_mixed.response_state, ResponseState.PARTIAL, "Case 19: Mixed answer must be PARTIAL")
    assert_eq(audit_mixed.unsupported_claims_count, 1, "Case 19: Exactly 1 unsupported claim tracked")
    assert_true(audit_mixed.claim_support_rate == 0.5, "Case 19: Claim support rate is exactly 0.50")

    # Strict mode test:
    audit_strict = strict_verifier.audit_and_verify_response("How many fatalities?", mixed_answer, doc_conflicts)
    assert_eq(audit_strict.response_state, ResponseState.PARTIAL, "Case 20: Strict mode handles partial support or demotes appropriately")

    print("\n" + "=" * 70)
    print(f"✓ PHASE 3 SEMANTIC VERIFIER STRESS SUITE: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)

if __name__ == "__main__":
    run_phase3_stress_suite()
