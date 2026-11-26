"""
PROJECT NOVA - SPRINT 5.3: CLAIM EXTRACTION SUITE
=================================================
Validates atomic proposition decomposition:
1. Short factual proposition preservation (>= 6 characters, eliminating the arbitrary 15-char trap).
2. Compound sentence splitting across coordinate & contrastive clauses (whereas, while, but, ;, —, and).
3. Text span tracking (start_idx, end_idx).
4. Meta-framing and formatting stripping.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from grounding.verifier import ClaimVerifier

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


def run_claim_extraction_suite():
    global passed_tests, total_tests
    verifier = ClaimVerifier()

    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.3: CLAIM EXTRACTION TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # GROUP 1: SHORT FACTUAL PROPOSITIONS (ELIMINATION OF 15-CHAR TRUNCATION)
    # -------------------------------------------------------------------------
    print("\n[GROUP 1] Short Factual Propositions...")

    # Case 1: "India won." (10 chars)
    claims1 = verifier.extract_claims("India won.")
    assert_true(len(claims1) == 1, "Case 1: 'India won.' must not be discarded")
    assert_eq(claims1[0], "India won.", "Case 1: Clean claim extraction")

    # Case 2: "Price: $799." (12 chars)
    claims2 = verifier.extract_claims("Price: $799.")
    assert_true(len(claims2) == 1, "Case 2: 'Price: $799.' must be preserved")

    # Case 3: "He scored 175." (14 chars)
    claims3 = verifier.extract_claims("He scored 175.")
    assert_true(len(claims3) == 1, "Case 3: 'He scored 175.' must be preserved")

    # Case 4: Non-proposition filler discarded (< 6 chars or trivial)
    claims4 = verifier.extract_claims("Yes.\nNo.\nOK.\nValid statement about physics.")
    assert_true(len(claims4) == 1, "Case 4: Filler words (<6 chars) discarded, substantive retained")
    assert_eq(claims4[0], "Valid statement about physics.", "Case 4: Substantive statement kept")

    # -------------------------------------------------------------------------
    # GROUP 2: COMPOUND SENTENCE SPLITTING
    # -------------------------------------------------------------------------
    print("\n[GROUP 2] Compound Sentence Splitting...")

    # Case 5: Semicolon split
    compound_semi = "Australia scored 241 runs; India was bowled out for 240."
    claims5 = verifier.extract_claims(compound_semi)
    assert_true(len(claims5) == 2, "Case 5: Semicolon separates two atomic claims")
    assert_true("Australia scored 241 runs" in claims5[0], "Case 5: First clause captured")
    assert_true("India was bowled out for 240" in claims5[1], "Case 5: Second clause captured")

    # Case 6: Contrastive split with 'whereas'
    compound_whereas = "The Model 3 RWD has 272 miles of range, whereas the AWD provides 341 miles."
    claims6 = verifier.extract_claims(compound_whereas)
    assert_true(len(claims6) == 2, "Case 6: 'whereas' splits into two propositions")
    assert_true("272 miles" in claims6[0], "Case 6: RWD proposition extracted")
    assert_true("341 miles" in claims6[1], "Case 6: AWD proposition extracted")

    # Case 7: Contrastive split with 'while'
    compound_while = "The base iPhone 15 starts at $799, while the iPhone 15 Pro starts at $999."
    claims7 = verifier.extract_claims(compound_while)
    assert_true(len(claims7) == 2, "Case 7: 'while' splits into two propositions")

    # Case 8: Contrastive split with 'but'
    compound_but = "India won the 1983 World Cup, but Kapil Dev scored only 15 runs in the final."
    claims8 = verifier.extract_claims(compound_but)
    assert_true(len(claims8) == 2, "Case 8: 'but' splits two propositions")

    # Case 9: Em-dash split
    compound_dash = "Mount Everest is 8,849 meters tall — it is located in the Himalayas."
    claims9 = verifier.extract_claims(compound_dash)
    assert_true(len(claims9) == 2, "Case 9: Em-dash splits into two propositions")

    # Case 10: Coordinate split with ', and '
    compound_and = "The PlayStation 5 launched in November 2020, and it cost $499 at release."
    claims10 = verifier.extract_claims(compound_and)
    assert_true(len(claims10) == 2, "Case 10: ', and ' splits coordinate clauses")

    # -------------------------------------------------------------------------
    # GROUP 3: TEXT SPANS & META-FRAMING REMOVAL
    # -------------------------------------------------------------------------
    print("\n[GROUP 3] Text Spans & Formatting Cleaning...")

    text_sample = (
        "Based on the provided evidence, the Earth orbits the Sun at approximately 150 million km [1].\n"
        "* India won the 2024 T20 World Cup [2].\n"
        "Sources: https://example.com/source"
    )
    spans = verifier.extract_claims_with_spans(text_sample)
    assert_true(len(spans) == 2, "Case 11: Sources footer stripped and 2 claims identified")
    
    # Check that leading bullet was stripped
    assert_true(not spans[1][0].startswith("*"), "Case 12: Bullet marker stripped from proposition")
    
    # Check start and end indexes
    c1, start1, end1 = spans[0]
    assert_true(start1 >= 0 and end1 > start1, "Case 13: Span 1 has valid positive character boundaries")
    
    c2, start2, end2 = spans[1]
    assert_true(start2 >= 0 and end2 > start2, "Case 14: Span 2 has valid positive character boundaries")

    print("\n" + "=" * 70)
    print(f"✓ SPRINT 5.3 CLAIM EXTRACTION SUITE: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_claim_extraction_suite()
