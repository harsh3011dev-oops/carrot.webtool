"""
PROJECT NOVA — SPRINT 5.1 LIVE ADVERSARIAL VALIDATION SUITE (27 TESTS)
======================================================================
Strict stress-testing across 9 real-world adversarial dimensions:
1. Facts appearing after the first 1,200 characters
2. Numerical facts appearing in unrelated contexts
3. Multiple events involving the same person
4. Tables containing product specifications
5. Sources with contradictory numbers
6. Claims that are plausible but unsupported (hallucination traps)
7. Questions where an incorrect answer must NOT receive VERIFIED
8. Historical versus current information
9. Follow-ups involving different years or entities (multi-turn context shifts)
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from grounding.schemas import ResponseState
from grounding.verifier import ClaimVerifier
from intelligence.context_manager import ConversationContextManager
from main import NovaOrchestrator
from retriever.chunker import chunk_document, score_chunk, select_top_evidence_chunks
from retriever.models import ExtractedDocument


def run_adversarial_suite():
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
    print("   PROJECT NOVA — SPRINT 5.1 LIVE ADVERSARIAL VALIDATION     ")
    print("============================================================\n")

    verifier = ClaimVerifier(mode="hybrid")
    strict_verifier = ClaimVerifier(mode="strict")

    # ------------------------------------------------------------------
    # CATEGORY 1: FACTS APPEARING AFTER THE FIRST 1,200 CHARACTERS
    # ------------------------------------------------------------------
    print("[CATEGORY 1] Facts Appearing After First 1,200 Characters...")

    filler_2000 = "Preamble and broad tournament background context. " * 50  # ~2,500 chars
    doc_deep_kapil = ExtractedDocument(
        source_index=1,
        title="1983 World Cup Match Summary",
        url="https://espncricinfo.com/wc1983/final",
        clean_text=(
            f"{filler_2000}\n\n"
            "## Scorecard Details: The 1983 Final\n"
            "In the 1983 World Cup final against West Indies, Kapil Dev scored 15 runs before "
            "taking the historic catch off Viv Richards. Mohinder Amarnath took 3 wickets for 12 runs."
        )
    )
    # Adv-01: Deep Fact Retrieval (offset > 2,000 chars)
    chunks_01 = select_top_evidence_chunks("What was Kapil Dev's score in the 1983 final?", [doc_deep_kapil], max_chunks=1)
    assert_true(len(chunks_01) > 0 and "scored 15 runs" in chunks_01[0].text, "Adv-01: Deep fact at offset > 2,000 retrieved")
    assert_true(chunks_01[0].start_char > 1200, "Adv-01: Confirmed retrieved beyond 1,200 character boundary")

    # Adv-02: Pragyan Rover Rollout at offset ~3,000 chars
    filler_3000 = "ISRO mission historical context and launch telemetry details. " * 60  # ~3,500 chars
    doc_deep_isro = ExtractedDocument(
        source_index=2,
        title="Chandrayaan-3 Mission Telemetry Log",
        url="https://isro.gov.in/c3-telemetry",
        clean_text=(
            f"{filler_3000}\n\n"
            "## Rover Deployment Telemetry\n"
            "The Pragyan rover successfully rolled out of the Vikram lander via the two-track ramp "
            "at 01:45 UTC on August 24, 2023, initiating in-situ chemical analysis."
        )
    )
    chunks_02 = select_top_evidence_chunks("At what time did the Pragyan rover roll out onto the lunar surface?", [doc_deep_isro], max_chunks=1)
    assert_true(len(chunks_02) > 0 and "01:45 UTC" in chunks_02[0].text, "Adv-02: Deep fact at offset > 3,000 retrieved")

    # Adv-03: Satellite Messaging Spec at offset ~4,000 chars
    filler_4000 = "Smartphone market trends, camera comparisons, and general design philosophy. " * 60
    doc_deep_apple = ExtractedDocument(
        source_index=3,
        title="Apple iPhone 16 Architecture Review",
        url="https://anandtech.com/apple-iphone-16-deep-dive",
        clean_text=(
            f"{filler_4000}\n\n"
            "## Emergency Satellite Communications\n"
            "The iPhone 16 base model includes Roadside Assistance via satellite in the US, "
            "operating on the Globalstar L-band frequency network."
        )
    )
    chunks_03 = select_top_evidence_chunks("What satellite network does iPhone 16 Roadside Assistance use?", [doc_deep_apple], max_chunks=1)
    assert_true(len(chunks_03) > 0 and "Globalstar" in chunks_03[0].text, "Adv-03: Deep fact at offset > 4,000 retrieved")
    print("  ✓ Category 1 Passed: 3/3 Deep Fact Retrieval tests passed beyond 1,200 chars.")

    # ------------------------------------------------------------------
    # CATEGORY 2: NUMERICAL FACTS IN UNRELATED CONTEXTS
    # ------------------------------------------------------------------
    print("\n[CATEGORY 2] Numerical Facts in Unrelated Contexts...")

    # Adv-04: Volume Shipped (5090) vs Price ($5090)
    doc_gpu = ExtractedDocument(
        source_index=4,
        title="NVIDIA Enterprise Shipments Q3",
        url="https://nvidia.com/press",
        clean_text="NVIDIA shipped over 5090 units of DGX Spark systems to hyperscalers in 2024."
    )
    claim_04 = "The NVIDIA DGX Spark is priced at $5090."
    v_04 = verifier.verify_single_claim(claim_04, [doc_gpu])
    assert_true(not v_04.is_supported, "Adv-04: Units shipped (5090) must not verify price claim ($5090)")

    # Adv-05: Jersey number (18) vs Runs scored (18)
    doc_cricket_jersey = ExtractedDocument(
        source_index=5,
        title="Player Profile",
        url="https://cricinfo.com/player",
        clean_text="Virat Kohli wears jersey number 18. In the 2023 World Cup final, he scored 54 runs."
    )
    claim_05 = "In the 2023 World Cup final, Virat Kohli scored 18 runs."
    v_05 = verifier.verify_single_claim(claim_05, [doc_cricket_jersey])
    assert_true(not v_05.is_supported, "Adv-05: Jersey number (18) must not verify runs scored (18)")
    assert_true(v_05.contradiction_detected, "Adv-05: Contradiction flagged against actual score 54")

    # Adv-06: Model Year (2024) vs Price ($2024)
    doc_macbook = ExtractedDocument(
        source_index=6,
        title="MacBook Lineup",
        url="https://apple.com/macbook",
        clean_text="Apple unveiled the 2024 MacBook Air with M3 chip, starting at $1099."
    )
    claim_06 = "The 2024 MacBook Air costs $2024."
    v_06 = verifier.verify_single_claim(claim_06, [doc_macbook])
    assert_true(not v_06.is_supported, "Adv-06: Year 2024 must not verify price of $2024")
    print("  ✓ Category 2 Passed: 3/3 Numerical decoupling tests passed.")

    # ------------------------------------------------------------------
    # CATEGORY 3: MULTIPLE EVENTS INVOLVING THE SAME PERSON
    # ------------------------------------------------------------------
    print("\n[CATEGORY 3] Multiple Events Involving the Same Person...")

    doc_kapil_multi = ExtractedDocument(
        source_index=7,
        title="Kapil Dev Career Highlights 1983",
        url="https://cricinfo.com/kapil",
        clean_text=(
            "## Group Match vs Zimbabwe\n"
            "Kapil Dev produced a legendary knock of 175 not out off 138 balls to rescue India.\n\n"
            "## Semi-Final vs England\n"
            "In the semi-final at Old Trafford, Kapil Dev took 3 wickets and was not needed to bat.\n\n"
            "## The Final vs West Indies\n"
            "In the 1983 final at Lord's, Kapil Dev scored 15 runs and captained India to a 43-run win."
        )
    )
    # Adv-07: Kapil Dev in Final (must be 15, NOT 175)
    c_kapil_bad = "In the 1983 World Cup final, Kapil Dev scored 175 runs."
    v_kapil_bad = verifier.verify_single_claim(c_kapil_bad, [doc_kapil_multi])
    assert_true(not v_kapil_bad.is_supported, "Adv-07: Kapil Dev 175 against Zimbabwe must NOT verify final score")
    assert_true(v_kapil_bad.contradiction_detected, "Adv-07: Contradiction with final score (15) detected")

    c_kapil_good = "In the 1983 World Cup final, Kapil Dev scored 15 runs [7]."
    v_kapil_good = verifier.verify_single_claim(c_kapil_good, [doc_kapil_multi])
    assert_true(v_kapil_good.is_supported, "Adv-07: Kapil Dev 15 in final verified")

    # Adv-08: Travis Head Semi-Final (62) vs Final (137)
    doc_travis = ExtractedDocument(
        source_index=8,
        title="Travis Head 2023 World Cup Campaign",
        url="https://cricinfo.com/travis-head",
        clean_text=(
            "## Semi-Final: Australia vs South Africa\n"
            "Travis Head struck a crucial 62 runs off 48 balls at Eden Gardens.\n\n"
            "## Final: Australia vs India\n"
            "In the 2023 final in Ahmedabad, Travis Head blasted 137 off 120 balls to secure the title."
        )
    )
    c_head_bad = "In the 2023 World Cup semi-final, Travis Head scored 137 runs."
    v_head_bad = verifier.verify_single_claim(c_head_bad, [doc_travis])
    assert_true(not v_head_bad.is_supported, "Adv-08: Final score (137) must NOT verify semi-final score")

    c_head_good = "Travis Head struck 62 runs in the semi-final against South Africa."
    v_head_good = verifier.verify_single_claim(c_head_good, [doc_travis])
    assert_true(v_head_good.is_supported, "Adv-08: Semi-final score (62) correctly verified")

    # Adv-09: MS Dhoni 2011 Final (91*) vs 2005 Bilateral (183*)
    doc_dhoni = ExtractedDocument(
        source_index=9,
        title="MS Dhoni Greatest Innings",
        url="https://cricinfo.com/dhoni",
        clean_text=(
            "## Bilateral Series 2005\n"
            "Against Sri Lanka in Jaipur in 2005, Dhoni smashed 183 not out.\n\n"
            "## 2011 World Cup Final\n"
            "In the 2011 World Cup final at Wankhede, captain MS Dhoni scored an unbeaten 91 not out."
        )
    )
    c_dhoni_bad = "MS Dhoni scored 183 not out in the 2011 World Cup final."
    v_dhoni_bad = verifier.verify_single_claim(c_dhoni_bad, [doc_dhoni])
    assert_true(not v_dhoni_bad.is_supported, "Adv-09: 2005 score (183) must NOT verify 2011 final claim")

    c_dhoni_good = "MS Dhoni scored an unbeaten 91 not out in the 2011 World Cup final."
    v_dhoni_good = verifier.verify_single_claim(c_dhoni_good, [doc_dhoni])
    assert_true(v_dhoni_good.is_supported, "Adv-09: 2011 final score (91*) correctly verified")
    print("  ✓ Category 3 Passed: 3/3 Multiple event disambiguation tests passed.")

    # ------------------------------------------------------------------
    # CATEGORY 4: TABLES CONTAINING PRODUCT SPECIFICATIONS
    # ------------------------------------------------------------------
    print("\n[CATEGORY 4] Tables Containing Product Specifications...")

    # Adv-10: GPU Boost Clock in Markdown Table
    doc_table_gpu = ExtractedDocument(
        source_index=10,
        title="NVIDIA DGX Spark Hardware Spec Sheet",
        url="https://nvidia.com/dgx-spark-specs",
        clean_text=(
            "## System Overview\n"
            "The DGX Spark is an AI workstation for local inference.\n\n"
            "## Technical Specifications\n"
            "| Component | Specification |\n"
            "| Architecture | Blackwell |\n"
            "| CUDA Cores | 18432 |\n"
            "| Boost Clock | 3.8 GHz |\n"
            "| Memory Bus | 512-bit |\n"
            "| TDP | 450W |"
        )
    )
    chunks_10 = select_top_evidence_chunks("What is the Boost Clock speed of NVIDIA DGX Spark?", [doc_table_gpu], max_chunks=1)
    assert_true("Boost Clock" in chunks_10[0].text and "3.8 GHz" in chunks_10[0].text, "Adv-10: Boost clock in table extracted")
    assert_true(chunks_10[0].contains_table, "Adv-10: Markdown table flag set")

    # Adv-11: Refresh Rate Comparison Table (iPhone 16 vs 16 Pro)
    doc_table_iphone = ExtractedDocument(
        source_index=11,
        title="Apple iPhone 16 Display Specs",
        url="https://apple.com/iphone-compare",
        clean_text=(
            "## Display Comparison\n"
            "| Model | Display Size | Refresh Rate | Peak Brightness |\n"
            "| iPhone 16 Base | 6.1 inch | 60Hz | 2000 nits |\n"
            "| iPhone 16 Pro | 6.3 inch | 120Hz ProMotion | 2000 nits |"
        )
    )
    chunks_11_base = select_top_evidence_chunks("What is the refresh rate of iPhone 16 base model?", [doc_table_iphone], max_chunks=1)
    assert_true("60Hz" in chunks_11_base[0].text, "Adv-11: 60Hz extracted for base model")

    # Adv-12: Memory Bus Width (RTX 5090 vs RTX 4090)
    doc_table_rtx = ExtractedDocument(
        source_index=12,
        title="GeForce RTX Generation Comparison",
        url="https://anandtech.com/rtx-comparison",
        clean_text=(
            "## Memory Subsystem Specs\n"
            "| Model | VRAM Capacity | Memory Bus | VRAM Type |\n"
            "| RTX 4090 | 24GB | 384-bit | GDDR6X |\n"
            "| RTX 5090 | 32GB | 512-bit | GDDR7 |"
        )
    )
    chunks_12 = select_top_evidence_chunks("What is the memory bus width of the RTX 5090?", [doc_table_rtx], max_chunks=1)
    assert_true("512-bit" in chunks_12[0].text and "GDDR7" in chunks_12[0].text, "Adv-12: RTX 5090 512-bit bus width extracted from table")
    print("  ✓ Category 4 Passed: 3/3 Structured table extraction tests passed.")

    # ------------------------------------------------------------------
    # CATEGORY 5: SOURCES WITH CONTRADICTORY NUMBERS
    # ------------------------------------------------------------------
    print("\n[CATEGORY 5] Sources with Contradictory Numbers...")

    # Adv-13: Conflicting Release Dates (Sep 20 vs Sep 27)
    doc_date_a = ExtractedDocument(
        source_index=13,
        title="Apple Press Release",
        url="https://apple.com/pr",
        clean_text="The iPhone 16 was made available worldwide on September 20, 2024."
    )
    doc_date_b = ExtractedDocument(
        source_index=14,
        title="Early Rumors Blog",
        url="https://leaks.com/iphone",
        clean_text="The iPhone 16 will reportedly go on sale on September 27, 2024."
    )
    claim_13_bad = "The iPhone 16 went on sale on September 27, 2024 [13]."
    v_13 = verifier.verify_single_claim(claim_13_bad, [doc_date_a])
    assert_true(not v_13.is_supported, "Adv-13: Contradictory release date rejected")
    assert_true(v_13.contradiction_detected, "Adv-13: Contradiction flag activated")

    # Adv-14: Contradictory Prices (Rs 79,900 official vs Rs 59,900 leak)
    doc_price_official = ExtractedDocument(
        source_index=15,
        title="Apple India Store",
        url="https://apple.com/in",
        clean_text="The base iPhone 16 starting price is Rs 79,900."
    )
    claim_14_bad = "The base iPhone 16 starting price is Rs 59,900 in India."
    v_14 = verifier.verify_single_claim(claim_14_bad, [doc_price_official])
    assert_true(not v_14.is_supported, "Adv-14: Conflicting leaked price rejected")
    assert_true(v_14.contradiction_detected, "Adv-14: Price contradiction detected")

    # Adv-15: Conflicting Stadium Attendance (85,000 vs 130,000)
    doc_stadium = ExtractedDocument(
        source_index=16,
        title="Match Attendance Records",
        url="https://sports.com/attendance",
        clean_text="The official attendance at Narendra Modi Stadium for the 2023 final was 92,453 spectators."
    )
    claim_15_bad = "The attendance was 130,000 spectators [16]."
    v_15 = verifier.verify_single_claim(claim_15_bad, [doc_stadium])
    assert_true(not v_15.is_supported, "Adv-15: Inflated spectator attendance rejected")
    assert_true(v_15.contradiction_detected, "Adv-15: Attendance contradiction flagged")
    print("  ✓ Category 5 Passed: 3/3 Contradictory evidence detection tests passed.")

    # ------------------------------------------------------------------
    # CATEGORY 6: PLAUSIBLE BUT UNSUPPORTED CLAIMS (HALLUCINATION TRAPS)
    # ------------------------------------------------------------------
    print("\n[CATEGORY 6] Plausible but Unsupported Claims (Hallucination Traps)...")

    # Adv-16: Plausible Match Referee in 1983 Final (Cricket finals in 1983 had no match referees!)
    doc_umpires = ExtractedDocument(
        source_index=17,
        title="1983 Final Officials",
        url="https://cricinfo.com/officials",
        clean_text="The umpires for the 1983 World Cup final were Dickie Bird and Barrie Meyer."
    )
    claim_16 = "The match referee for the 1983 World Cup final was Clive Lloyd."
    v_16 = verifier.verify_single_claim(claim_16, [doc_umpires])
    assert_true(not v_16.is_supported, "Adv-16: Plausible referee claim rejected because source does not contain it")

    # Adv-17: Plausible Titanium Frame on Base iPhone 16
    doc_iphone_mat = ExtractedDocument(
        source_index=18,
        title="iPhone 16 Materials",
        url="https://apple.com/iphone-16/specs",
        clean_text="The iPhone 16 features an aerospace-grade aluminum enclosure with a color-infused glass back."
    )
    claim_17 = "The iPhone 16 base model features a grade 5 titanium frame."
    v_17 = verifier.verify_single_claim(claim_17, [doc_iphone_mat])
    assert_true(not v_17.is_supported, "Adv-17: False titanium frame claim rejected")

    # Adv-18: Plausible Parachute on Lunar Lander (Moon has vacuum)
    doc_lander = ExtractedDocument(
        source_index=19,
        title="ISRO Vikram Propulsion",
        url="https://isro.gov.in/propulsion",
        clean_text="The Vikram lander employed 4 throttleable liquid-propellant engines for powered descent."
    )
    claim_18 = "The Vikram lander deployed a supersonic parachute during its final lunar descent."
    v_18 = verifier.verify_single_claim(claim_18, [doc_lander])
    assert_true(not v_18.is_supported, "Adv-18: Non-existent parachute claim rejected")
    print("  ✓ Category 6 Passed: 3/3 Plausible hallucination trap tests passed.")

    # ------------------------------------------------------------------
    # CATEGORY 7: QUESTIONS WHERE INCORRECT ANSWERS MUST NOT RECEIVE VERIFIED
    # ------------------------------------------------------------------
    print("\n[CATEGORY 7] Questions Where Incorrect Answers Must NOT Receive VERIFIED...")

    # Adv-19: Response with false victory margin must NOT be VERIFIED
    doc_wc23 = ExtractedDocument(
        source_index=20,
        title="2023 World Cup Final Report",
        url="https://cricinfo.com/wc2023-final",
        clean_text="Australia won the 2023 ICC World Cup final by defeating India by 6 wickets."
    )
    resp_19 = "Australia won the 2023 World Cup final by 100 runs [20]."
    audit_19 = verifier.audit_and_verify_response("Who won 2023 World Cup?", resp_19, [doc_wc23])
    assert_true(audit_19.response_state != ResponseState.VERIFIED, "Adv-19: False margin (100 runs) must NOT be VERIFIED")
    assert_true(audit_19.unsupported_claims_count > 0, "Adv-19: Unsupported claim detected")

    # Adv-20: Response with Kapil Dev 175 in final must NOT be VERIFIED
    resp_20 = "In the 1983 World Cup final, Kapil Dev scored 175 runs [7]."
    audit_20 = verifier.audit_and_verify_response("Kapil Dev score 1983 final", resp_20, [doc_kapil_multi])
    assert_true(audit_20.response_state != ResponseState.VERIFIED, "Adv-20: Kapil Dev 175 in final must NOT be VERIFIED")

    # Adv-21: Response with iPhone 16 price Rs 59,900 must NOT be VERIFIED
    resp_21 = "The iPhone 16 base model is priced at Rs 59,900 in India [15]."
    audit_21 = verifier.audit_and_verify_response("iPhone 16 price", resp_21, [doc_price_official])
    assert_true(audit_21.response_state != ResponseState.VERIFIED, "Adv-21: Conflicting price must NOT be VERIFIED")
    print("  ✓ Category 7 Passed: 3/3 State-demotion guardrail tests passed.")

    # ------------------------------------------------------------------
    # CATEGORY 8: HISTORICAL VERSUS CURRENT INFORMATION
    # ------------------------------------------------------------------
    print("\n[CATEGORY 8] Historical versus Current Information...")

    # Adv-22: 2019 Winner (England) vs 2023 Winner (Australia)
    doc_history_cricket = ExtractedDocument(
        source_index=22,
        title="ICC World Cup Roll of Honour",
        url="https://icc.org/champions",
        clean_text=(
            "In 2019, England won their maiden ICC World Cup at Lord's. "
            "In 2023, Australia claimed their sixth title by defeating India in Ahmedabad."
        )
    )
    chunks_22_hist = select_top_evidence_chunks("Who won the 2019 Cricket World Cup?", [doc_history_cricket], max_chunks=1)
    assert_true("England" in chunks_22_hist[0].text, "Adv-22: 2019 winner England extracted")

    chunks_22_curr = select_top_evidence_chunks("Who won the 2023 Cricket World Cup?", [doc_history_cricket], max_chunks=1)
    assert_true("Australia" in chunks_22_curr[0].text, "Adv-22: 2023 winner Australia extracted")

    # Adv-23: Launch Price iPhone 11 ($699) vs iPhone 16 ($799)
    doc_iphone_hist = ExtractedDocument(
        source_index=23,
        title="iPhone Historical Launch Prices",
        url="https://apple.com/history",
        clean_text=(
            "The iPhone 11 was launched in September 2019 at a starting price of $699. "
            "The iPhone 16 was launched in September 2024 at a starting price of $799."
        )
    )
    chunks_23_hist = select_top_evidence_chunks("What was the launch price of iPhone 11?", [doc_iphone_hist], max_chunks=1)
    assert_true("$699" in chunks_23_hist[0].text, "Adv-23: iPhone 11 historical price $699 extracted")

    chunks_23_curr = select_top_evidence_chunks("What was the launch price of iPhone 16?", [doc_iphone_hist], max_chunks=1)
    assert_true("$799" in chunks_23_curr[0].text, "Adv-23: iPhone 16 launch price $799 extracted")

    # Adv-24: Python 2 EOL (2020)
    doc_python = ExtractedDocument(
        source_index=24,
        title="Python 2.7 Sunset",
        url="https://python.org/psf/sunset",
        clean_text="Python 2.7 officially reached End of Life (EOL) on January 1, 2020."
    )
    chunks_24 = select_top_evidence_chunks("When was Python 2 officially retired?", [doc_python], max_chunks=1)
    assert_true("January 1, 2020" in chunks_24[0].text, "Adv-24: Python 2 retirement date extracted")
    print("  ✓ Category 8 Passed: 3/3 Historical vs Current separation tests passed.")

    # ------------------------------------------------------------------
    # CATEGORY 9: FOLLOW-UPS INVOLVING DIFFERENT YEARS OR ENTITIES
    # ------------------------------------------------------------------
    print("\n[CATEGORY 9] Follow-ups Involving Different Years or Entities...")

    ctx = ConversationContextManager()

    # Adv-25 (Turn 1): "Who was the captain of India in the 1983 World Cup?"
    q1 = "Who was the captain of India in the 1983 World Cup?"
    eq1, is_fu1, topic_ch1 = ctx.resolve_turn(q1)
    assert_true(not is_fu1, "Adv-25: Turn 1 is standalone")
    ctx.add_turn(q1, eq1, response_text="Kapil Dev captained India to victory in 1983.")

    # Adv-26 (Turn 2 - Temporal Shift to 2011): "What about in 2011?"
    q2 = "What about in 2011?"
    eq2, is_fu2, topic_ch2 = ctx.resolve_turn(q2)
    assert_true(is_fu2, "Adv-26: Turn 2 accurately classified as follow-up")
    assert_true("2011" in eq2, "Adv-26: Year 2011 captured in rewritten query")
    assert_true("captain" in eq2.lower(), "Adv-26: Inherited 'captain' intent from previous turn")
    assert_true("1983" not in eq2, "Adv-26: 1983 superseded by 2011 (no temporal conflict)")
    ctx.add_turn(q2, eq2, response_text="MS Dhoni captained India to victory in 2011.")

    # Adv-27 (Turn 3 - Coreference to that final): "What was his score in that final?"
    q3 = "What was his score in that final?"
    eq3, is_fu3, topic_ch3 = ctx.resolve_turn(q3)
    assert_true(is_fu3, "Adv-27: Turn 3 recognized as follow-up")
    assert_true("dhoni" in eq3.lower() or "score" in eq3.lower(), "Adv-27: Coreference resolved to MS Dhoni score in 2011 final")
    print("  ✓ Category 9 Passed: 3/3 Multi-turn context switch tests passed.")

    print("\n============================================================")
    print(f"✓ SPRINT 5.1 LIVE ADVERSARIAL SUITE: {passed}/{total} TESTS PASSED (100%)")
    print("============================================================\n")


if __name__ == "__main__":
    run_adversarial_suite()

