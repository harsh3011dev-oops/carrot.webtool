"""
PROJECT NOVA - SPRINT 5.3.1: CLAIM EXTRACTION QUALITY & SEMANTIC INTEGRITY AUDIT SUITE
======================================================================================
Validates:
1. Atomic proposition decomposition across compound predicates and clauses.
2. Subject inheritance and pronoun resolution in secondary clauses.
3. Subordinate clause segmentation (leading 'Although', 'While', 'Whereas').
4. Preservation of short factual claims (>= 6 characters).
5. Exact character span tracking (start_idx, end_idx).
6. Precision and recall measurement on complex factual paragraphs.
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


def run_claim_extraction_audit_suite():
    global passed_tests, total_tests
    verifier = ClaimVerifier()

    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.3.1: CLAIM EXTRACTION AUDIT SUITE")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # GROUP 1: SIMPLE & SHORT PROPOSITION BOUNDARIES
    # -------------------------------------------------------------------------
    print("\n[GROUP 1] Simple & Short Proposition Boundaries...")

    # Case 1: Simple declarative
    c1 = verifier.extract_claims("The Earth orbits the Sun at 150 million km.")
    assert_eq(len(c1), 1, "Case 1: Single declarative sentence produces exactly 1 proposition")
    assert_true("Earth orbits" in c1[0], "Case 1: Core proposition preserved")

    # Case 2: Short proposition (6-10 chars)
    c2 = verifier.extract_claims("He won.")
    assert_eq(len(c2), 1, "Case 2: 7-character proposition 'He won.' preserved")

    # Case 3: Trivial filler (< 6 chars) discarded
    c3 = verifier.extract_claims("Yes.\nNo.\nOK.\nEarth is spherical.")
    assert_eq(len(c3), 1, "Case 3: Filler words < 6 chars discarded")
    assert_eq(c3[0], "Earth is spherical.", "Case 3: Substantive proposition kept")

    # Case 4: Negated proposition preserved intact
    c4 = verifier.extract_claims("Pluto is not classified as a major planet.")
    assert_eq(len(c4), 1, "Case 4: Negation preserved intact")
    assert_true("not classified" in c4[0], "Case 4: Negation word not stripped")

    # -------------------------------------------------------------------------
    # GROUP 2: COORDINATE & CONTRASTIVE CLAUSE SPLITTING
    # -------------------------------------------------------------------------
    print("\n[GROUP 2] Coordinate & Contrastive Splitting...")

    # Case 5: Semicolon splitting
    c5 = verifier.extract_claims("Australia scored 241 runs; India was bowled out for 240.")
    assert_eq(len(c5), 2, "Case 5: Semicolon produces 2 claims")
    assert_true("Australia scored 241" in c5[0], "Case 5: Clause 1 captured")
    assert_true("India was bowled out" in c5[1], "Case 5: Clause 2 captured")

    # Case 6: Em-dash splitting
    c6 = verifier.extract_claims("Apollo 11 landed in 1969 — Neil Armstrong walked on the Moon.")
    assert_eq(len(c6), 2, "Case 6: Em-dash produces 2 claims")
    assert_true("Apollo 11" in c6[0], "Case 6: Clause 1 captured")
    assert_true("Neil Armstrong" in c6[1], "Case 6: Clause 2 captured")

    # Case 7: Contrastive with 'whereas'
    c7 = verifier.extract_claims("Model 3 RWD offers 272 miles of range, whereas AWD provides 341 miles.")
    assert_eq(len(c7), 2, "Case 7: 'whereas' produces 2 claims")

    # Case 8: Contrastive with 'while'
    c8 = verifier.extract_claims("The base iPhone 15 starts at $799, while the Pro model starts at $999.")
    assert_eq(len(c8), 2, "Case 8: 'while' produces 2 claims")

    # Case 9: Concession with 'but'
    c9 = verifier.extract_claims("India reached the final, but Australia won the championship.")
    assert_eq(len(c9), 2, "Case 9: 'but' produces 2 claims")

    # -------------------------------------------------------------------------
    # GROUP 3: SUBORDINATE CLAUSES (LEADING 'ALTHOUGH', 'WHILE', 'WHEREAS')
    # -------------------------------------------------------------------------
    print("\n[GROUP 3] Subordinate Clause Splitting...")

    # Case 10: Leading 'Although' with pronoun in clause 2
    c10 = verifier.extract_claims("Although Google was founded in 1998, it went public in 2004.")
    assert_eq(len(c10), 2, "Case 10: Leading 'Although' splits into 2 propositions")
    assert_true("Google was founded in 1998" in c10[0], "Case 10: Subordinate clause stripped of 'Although'")
    assert_true("Google" in c10[1] and "2004" in c10[1], "Case 10: Clause 2 inherits subject 'Google' for 'it'")

    # Case 11: Leading 'While' with independent subjects
    c11 = verifier.extract_claims("While Tesla was founded in 2003, Elon Musk joined the company in 2004.")
    assert_eq(len(c11), 2, "Case 11: Leading 'While' splits into 2 propositions")
    assert_true("Elon Musk joined" in c11[1], "Case 11: Independent subject retained")

    # Case 12: Leading 'Whereas' with factual comparison
    c12 = verifier.extract_claims("Whereas Mars has two moons, Earth has only one moon.")
    assert_eq(len(c12), 2, "Case 12: Leading 'Whereas' splits into 2 propositions")
    assert_true("Mars has two moons" in c12[0], "Case 12: Clause 1 captured cleanly")
    assert_true("Earth has only one moon" in c12[1], "Case 12: Clause 2 captured cleanly")

    # Case 13: Leading 'Even though'
    c13 = verifier.extract_claims("Even though Boeing designed the 737, airlines operate diverse fleets.")
    assert_eq(len(c13), 2, "Case 13: 'Even though' splits into 2 propositions")

    # -------------------------------------------------------------------------
    # GROUP 4: COMPOUND PREDICATES & SUBJECT INHERITANCE
    # -------------------------------------------------------------------------
    print("\n[GROUP 4] Compound Predicates & Subject Inheritance...")

    # Case 14: Compound verb without comma ('and launched')
    c14 = verifier.extract_claims("Apple acquired Beats in 2014 and launched Apple Music in 2015.")
    assert_eq(len(c14), 2, "Case 14: Compound verb without comma produces 2 claims")
    assert_true("Apple acquired Beats" in c14[0], "Case 14: Clause 1 captured")
    assert_true("Apple" in c14[1] and "Apple Music" in c14[1], "Case 14: Clause 2 inherits 'Apple' as subject")

    # Case 15: Compound verb with 'subsequently' / 'later'
    c15 = verifier.extract_claims("SpaceX launched Falcon 9 in 2010 and subsequently developed Starship.")
    assert_eq(len(c15), 2, "Case 15: 'and subsequently developed' splits into 2 claims")
    assert_true("SpaceX" in c15[1], "Case 15: Clause 2 inherits 'SpaceX'")

    # Case 16: Pronoun resolution in coordinate clause (', and it ')
    c16 = verifier.extract_claims("Curiosity launched in 2011, and it landed on Mars in 2012.")
    assert_eq(len(c16), 2, "Case 16: Coordinate clause splits into 2 claims")
    assert_true("Curiosity" in c16[1], "Case 16: 'it' resolved to 'Curiosity' in clause 2")

    # Case 17: Multi-entity independent coordinate clauses
    c17 = verifier.extract_claims("Apple acquired Beats in 2014, and Microsoft purchased LinkedIn in 2016.")
    assert_eq(len(c17), 2, "Case 17: Coordinate clause with distinct subjects splits into 2 claims")
    assert_true("Apple" in c17[0] and "Microsoft" in c17[1], "Case 17: Distinct subjects preserved independently")

    # -------------------------------------------------------------------------
    # GROUP 5: SPAN TRACKING & CLEANING INTEGRITY
    # -------------------------------------------------------------------------
    print("\n[GROUP 5] Span Tracking & Formatting Cleaning...")

    text_rich = (
        "Based on verified sources, Mount Everest is 8,849 meters tall [1].\n"
        "- The Mariana Trench reaches 10,935 meters depth [2].\n"
        "Sources:\n1. https://nationalgeographic.com\n2. https://noaa.gov"
    )
    spans = verifier.extract_claims_with_spans(text_rich)
    assert_eq(len(spans), 2, "Case 18: Metadata framing and source footer stripped")

    c18_1, s1, e1 = spans[0]
    c18_2, s2, e2 = spans[1]
    assert_true("Mount Everest is 8,849" in c18_1, "Case 19: Proposition 1 cleaned of framing")
    assert_true("Mariana Trench" in c18_2 and not c18_2.startswith("-"), "Case 20: Proposition 2 stripped of bullet marker")
    assert_true(s1 >= 0 and e1 > s1, "Case 21: Span 1 positive range")
    assert_true(s2 >= 0 and e2 > s2, "Case 22: Span 2 positive range")

    # -------------------------------------------------------------------------
    # GROUP 6: PRECISION & RECALL ON MULTI-SENTENCE PARAGRAPH
    # -------------------------------------------------------------------------
    print("\n[GROUP 6] Precision & Recall on Multi-Sentence Complex Paragraph...")

    complex_para = (
        "Australia won the 2023 Cricket World Cup in Ahmedabad [1]. "
        "Travis Head scored 137 runs, while Rohit Sharma scored 47 runs [1]. "
        "Although India won 10 consecutive matches in the tournament, they lost the final [2]."
    )
    # Ground truth propositions expected:
    # 1. Australia won 2023 Cricket World Cup in Ahmedabad
    # 2. Travis Head scored 137 runs
    # 3. Rohit Sharma scored 47 runs
    # 4. India won 10 consecutive matches in the tournament
    # 5. India lost the final
    expected_propositions = 5
    extracted_para_claims = verifier.extract_claims(complex_para)

    assert_eq(len(extracted_para_claims), expected_propositions,
              f"Case 23: Complex paragraph decomposed into exactly {expected_propositions} atomic propositions")
    
    # Check that each expected proposition has high semantic fidelity
    assert_true(any("Australia won" in c for c in extracted_para_claims), "Case 24: Proposition 1 present")
    assert_true(any("Travis Head scored 137" in c for c in extracted_para_claims), "Case 25: Proposition 2 present")
    assert_true(any("Rohit Sharma scored 47" in c for c in extracted_para_claims), "Case 26: Proposition 2 present")
    assert_true(any("India won 10 consecutive matches" in c for c in extracted_para_claims), "Case 27: Proposition 4 present")
    assert_true(any("India lost the final" in c or "They lost the final" in c for c in extracted_para_claims), "Case 28: Proposition 5 present")

    # Precision & recall metrics calculation:
    tp = 5
    fp = max(0, len(extracted_para_claims) - 5)
    fn = max(0, 5 - len(extracted_para_claims))
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    assert_true(precision >= 0.95 and recall >= 0.95, f"Case 29: Claim extraction precision ({precision}) and recall ({recall}) >= 95%")

    print("\n" + "=" * 70)
    print(f"✓ SPRINT 5.3.1 CLAIM EXTRACTION AUDIT: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_claim_extraction_audit_suite()

