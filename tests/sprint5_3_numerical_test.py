"""
PROJECT NOVA - SPRINT 5.3: NUMERICAL REASONING & VARIANT INTEGRITY SUITE
========================================================================
Comprehensive test suite validating:
1. Strict variant/trim attribute binding (e.g. Tesla Model 3 RWD 272m vs AWD 341m).
2. Elimination of cross-trim numerical contamination.
3. Continuous physical measurement tolerance (e.g. Mount Everest 8,848.86m vs 8,849m).
4. Strict discrete enforcement for calendar years, currencies, and integer counts.
5. Comparative claims, margins, and percentage difference verification.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from grounding.schemas import ResponseState, StructuredNumericalClaim
from grounding.verifier import ClaimVerifier, numbers_match_with_tolerance, extract_variant
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


def run_numerical_suite():
    global passed_tests, total_tests
    verifier = ClaimVerifier(mode="hybrid")

    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.3: NUMERICAL REASONING TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # GROUP 1: VARIANT / TRIM ATTRIBUTE BINDING & CONTAMINATION REJECTION
    # -------------------------------------------------------------------------
    print("\n[GROUP 1] Variant / Trim Attribute Binding...")

    doc_tesla = [
        ExtractedDocument(
            title="Tesla Model 3 Specifications and Range Ratings",
            url="https://tesla.com/model3/specs",
            clean_text=(
                "The refreshed Tesla Model 3 Rear-Wheel Drive (RWD) has an EPA-estimated range of 272 miles.\n\n"
                "In contrast, the Model 3 Long Range All-Wheel Drive (AWD) delivers an estimated range of 341 miles.\n\n"
                "The high-performance Model 3 Performance reaches 0-60 mph in 2.9 seconds."
            ),
            source_index=1,
            relevance_score=0.98,
        )
    ]

    # Test 1: Correct trim matches its own range
    res1 = verifier.verify_single_claim("The Tesla Model 3 Rear-Wheel Drive has an EPA-estimated range of 272 miles [1].", doc_tesla)
    assert_true(res1.is_supported, "Case 1: Standard RWD with 272 miles must be SUPPORTED")
    assert_true(not res1.contradiction_detected, "Case 1: No contradiction for correct RWD range")
    assert_eq(res1.structured_numerical.variant, "rear-wheel drive", "Case 1: Variant extracted as rear-wheel drive")
    assert_eq(res1.structured_numerical.numeric_value, 272.0, "Case 1: Numeric value is 272")

    # Test 2: Competing trim range assigned to RWD must be CONTRADICTED / REJECTED
    res2 = verifier.verify_single_claim("The Tesla Model 3 Rear-Wheel Drive has an EPA-estimated range of 341 miles [1].", doc_tesla)
    assert_true(not res2.is_supported, "Case 2: RWD assigned Long Range AWD's 341 miles must NOT be supported")
    assert_true(res2.contradiction_detected, "Case 2: Cross-trim contamination must trigger contradiction")

    # Test 3: Long Range AWD matches its own 341 miles
    res3 = verifier.verify_single_claim("The Model 3 Long Range AWD delivers an estimated range of 341 miles [1].", doc_tesla)
    assert_true(res3.is_supported, "Case 3: Long Range AWD with 341 miles must be SUPPORTED")
    assert_true(not res3.contradiction_detected, "Case 3: No contradiction for correct AWD range")

    # Test 4: Long Range AWD assigned RWD's 272 miles must be REJECTED
    res4 = verifier.verify_single_claim("The Model 3 Long Range AWD has an estimated range of 272 miles [1].", doc_tesla)
    assert_true(not res4.is_supported, "Case 4: AWD assigned RWD's 272 miles must NOT be supported")
    assert_true(res4.contradiction_detected, "Case 4: Cross-trim contamination must trigger contradiction")

    # Test 5: Smartphone variant storage & price binding
    doc_phones = [
        ExtractedDocument(
            title="iPhone 15 Pricing & Storage Variants",
            url="https://apple.com/iphone-15/specs",
            clean_text=(
                "The base iPhone 15 starts at $799 for 128GB storage, while the 256GB variant costs $899.\n\n"
                "The premium iPhone 15 Pro starts at $999 for 128GB, and the iPhone 15 Pro Max starts at $1199 for 256GB."
            ),
            source_index=2,
            relevance_score=0.95,
        )
    ]

    res5 = verifier.verify_single_claim("The base iPhone 15 starts at $799 [2].", doc_phones)
    assert_true(res5.is_supported, "Case 5: Base iPhone 15 at $799 is SUPPORTED")

    res6 = verifier.verify_single_claim("The base iPhone 15 starts at $1199 [2].", doc_phones)
    assert_true(not res6.is_supported, "Case 6: Base iPhone 15 assigned Pro Max price must NOT be supported")
    assert_true(res6.contradiction_detected, "Case 6: Cross-variant price contamination triggers contradiction")

    res7 = verifier.verify_single_claim("The iPhone 15 Pro Max starts at $1199 [2].", doc_phones)
    assert_true(res7.is_supported, "Case 7: iPhone 15 Pro Max at $1199 is SUPPORTED")

    # -------------------------------------------------------------------------
    # GROUP 2: CONTINUOUS MEASUREMENT TOLERANCE & INTEGER ROUNDING
    # -------------------------------------------------------------------------
    print("\n[GROUP 2] Continuous Measurement Tolerance...")

    doc_everest = [
        ExtractedDocument(
            title="Survey of Mount Everest Elevation",
            url="https://nationalgeographic.com/everest-height",
            clean_text="The latest official joint survey established the height of Mount Everest at 8,848.86 meters above sea level.",
            source_index=3,
            relevance_score=0.96,
        )
    ]

    # Test 8: Rounded integer 8,849 meters must corroborate with 8,848.86 meters without contradiction
    res8 = verifier.verify_single_claim("The official height of Mount Everest is 8,849 meters [3].", doc_everest)
    assert_true(res8.is_supported, "Case 8: 8,849 meters is compatible with 8,848.86m survey")
    assert_true(not res8.contradiction_detected, "Case 8: 8,849m does NOT trigger false contradiction against 8,848.86m")

    # Test 9: Exact float 8,848.86 meters also corroborated
    res9 = verifier.verify_single_claim("Mount Everest stands at 8,848.86 meters [3].", doc_everest)
    assert_true(res9.is_supported, "Case 9: Exact 8,848.86 meters is corroborated")

    # Test 10: Grossly conflicting height (e.g. 8,200 meters) must trigger contradiction
    res10 = verifier.verify_single_claim("Mount Everest stands at 8,200 meters [3].", doc_everest)
    assert_true(not res10.is_supported, "Case 10: 8,200 meters is unsupported")
    assert_true(res10.contradiction_detected, "Case 10: 8,200 meters triggers contradiction against 8,848.86m")

    # Test 11: Earth-Sun distance tolerance (149.6 million km vs 150 million km)
    doc_sun = [
        ExtractedDocument(
            title="Astronomical Unit Definition",
            url="https://nasa.gov/sun-earth-distance",
            clean_text="The average distance from the Earth to the Sun is approximately 149.6 million kilometers (about 93 million miles).",
            source_index=4,
            relevance_score=0.97,
        )
    ]

    res11 = verifier.verify_single_claim("The Earth is approximately 150 million kilometers from the Sun [4].", doc_sun)
    assert_true(res11.is_supported, "Case 11: 150 million km matches 149.6 million km within rounding tolerance")
    assert_true(not res11.contradiction_detected, "Case 11: 150 million km does not trigger contradiction")

    # Test 12: Earth equatorial diameter (12,742 km vs 12,756 km)
    doc_earth = [
        ExtractedDocument(
            title="Earth Dimensions",
            url="https://nasa.gov/earth-specs",
            clean_text="The equatorial diameter of Earth is 12,756 kilometers, while the polar diameter is 12,714 kilometers.",
            source_index=5,
            relevance_score=0.95,
        )
    ]

    res12 = verifier.verify_single_claim("The diameter of the Earth at the equator is 12,756 kilometers [5].", doc_earth)
    assert_true(res12.is_supported, "Case 12: Exact 12,756 km is corroborated")

    res13 = verifier.verify_single_claim("The diameter of the Earth at the equator is 12,742 kilometers [5].", doc_earth)
    assert_true(res13.is_supported, "Case 13: 12,742 km matches within 0.1% physical measurement tolerance")

    # -------------------------------------------------------------------------
    # GROUP 3: STRICT DISCRETE MATCHING FOR YEARS, CURRENCIES & COUNTS
    # -------------------------------------------------------------------------
    print("\n[GROUP 3] Strict Discrete Matching...")

    # Test 14: Calendar year 2024 vs 2023 must NEVER match tolerance
    assert_true(not numbers_match_with_tolerance("2024", "2023"), "Case 14: Calendar year 2024 does NOT match 2023")
    assert_true(numbers_match_with_tolerance("2024", "2024"), "Case 14: Calendar year 2024 matches 2024")

    # Test 15: Cricket scores: 175 runs vs 15 runs must trigger contradiction
    doc_cricket = [
        ExtractedDocument(
            title="1983 Cricket World Cup Final",
            url="https://cricinfo.com/1983-final",
            clean_text="In the 1983 World Cup final against the West Indies, Indian captain Kapil Dev scored 15 runs.",
            source_index=6,
            relevance_score=0.95,
        )
    ]
    res15 = verifier.verify_single_claim("In the 1983 World Cup final, Kapil Dev scored 175 runs [6].", doc_cricket)
    assert_true(not res15.is_supported, "Case 15: Kapil Dev 175 in final is NOT supported")
    assert_true(res15.contradiction_detected, "Case 15: Conflicting score triggers contradiction")

    # Test 16: Human bone count: 206 bones vs 300 bones
    doc_bones = [
        ExtractedDocument(
            title="Human Anatomy Overview",
            url="https://nih.gov/skeleton",
            clean_text="An adult human skeleton is composed of exactly 206 individual bones.",
            source_index=7,
            relevance_score=0.94,
        )
    ]
    res16 = verifier.verify_single_claim("An adult human skeleton has 206 individual bones [7].", doc_bones)
    assert_true(res16.is_supported, "Case 16: 206 bones is SUPPORTED")

    res17 = verifier.verify_single_claim("An adult human skeleton has 300 individual bones [7].", doc_bones)
    assert_true(not res17.is_supported, "Case 17: 300 adult bones is NOT supported")
    assert_true(res17.contradiction_detected, "Case 17: 300 vs 206 triggers contradiction")

    # Test 18: Currency separation ($799 vs Rs 79,900 vs €799)
    doc_currency = [
        ExtractedDocument(
            title="US Market Electronics",
            url="https://store.com/us-pricing",
            clean_text="The retail price is set at $799 in the United States.",
            source_index=8,
            relevance_score=0.93,
        )
    ]
    res18 = verifier.verify_single_claim("The product costs €799 [8].", doc_currency)
    assert_true(not res18.is_supported, "Case 18: €799 must NOT be supported when source specifies $799")

    # -------------------------------------------------------------------------
    # GROUP 4: COMPARATIVE CLAIMS & MARGINS
    # -------------------------------------------------------------------------
    print("\n[GROUP 4] Comparative Claims & Margins...")

    doc_match_margin = [
        ExtractedDocument(
            title="2023 World Cup Final Summary",
            url="https://icc.com/wc2023",
            clean_text="Australia defeated India by 6 wickets to win the 2023 ICC World Cup.",
            source_index=9,
            relevance_score=0.96,
        )
    ]

    res19 = verifier.verify_single_claim("Australia won the final by 6 wickets [9].", doc_match_margin)
    assert_true(res19.is_supported, "Case 19: Victory margin of 6 wickets is SUPPORTED")

    res20 = verifier.verify_single_claim("Australia won the final by 100 runs [9].", doc_match_margin)
    assert_true(not res20.is_supported, "Case 20: 100 runs margin is unsupported and contradictory")

    # -------------------------------------------------------------------------
    # GROUP 5: STRUCTURED NUMERICAL CLAIM SCHEMA INTEGRITY
    # -------------------------------------------------------------------------
    print("\n[GROUP 5] Structured Numerical Claim Schema...")

    claim_str = "The Tesla Model 3 RWD offers 272 miles of range [1]."
    res21 = verifier.verify_single_claim(claim_str, doc_tesla)
    assert_true(res21.structured_numerical is not None, "Case 21: Structured numerical claim must be populated")
    assert_eq(res21.structured_numerical.numeric_value, 272.0, "Case 21: Parsed float value 272.0")
    assert_true(res21.structured_numerical.unit in ["mile", "miles"], f"Case 21: Physical unit is mile/miles (Got: {res21.structured_numerical.unit})")

    print("\n" + "=" * 70)
    print(f"✓ SPRINT 5.3 NUMERICAL REASONING SUITE: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_numerical_suite()
