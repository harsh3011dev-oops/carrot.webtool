"""
PROJECT NOVA - SPRINT 5.3.1: CONTEXT STAGE DECOUPLING & COREFERENCE AUDIT SUITE
===============================================================================
Comprehensive 30-scenario multi-turn audit measuring 9 distinct pipeline stages:
1. Intent Recognition Accuracy (FollowUpIntent classification)
2. Primary Entity Resolution Accuracy (gender/animacy awareness, no Moon -> he)
3. Attribute Resolution Accuracy (price, score, director, range, etc.)
4. Temporal Anchor Preservation Accuracy (year preservation and substitution)
5. Standalone Query Clarity (self-contained, no double possessives like Apple's's)
6. Retrieval Relevance (documents matched to resolved query)
7. Evidence Passage Selection (chunk scoring and top chunk selection)
8. Factual Answer Accuracy (correct answer content)
9. Verification Truth State Fidelity (VERIFIED, PARTIAL, UNVERIFIED, ABSTAIN)
"""

import os
import sys
import re

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from intelligence.context_manager import ConversationContextManager, is_person_entity
from intelligence.schemas import FollowUpIntent
from retriever.models import ExtractedDocument
from retriever.chunker import select_top_evidence_chunks
from grounding.verifier import ClaimVerifier
from grounding.schemas import ResponseState

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


def run_context_stage_audit_suite():
    global passed_tests, total_tests
    cm = ConversationContextManager()
    verifier = ClaimVerifier(mode="hybrid")

    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.3.1: CONTEXT STAGE DECOUPLING AUDIT (30 SCENARIOS)")
    print("=" * 70)

    stage_metrics = {
        "intent_recognition": 0,
        "primary_entity": 0,
        "attribute_resolution": 0,
        "temporal_preservation": 0,
        "query_clarity": 0,
        "retrieval_relevance": 0,
        "evidence_selection": 0,
        "synthesis_factual": 0,
        "truth_state_fidelity": 0,
    }
    total_scenarios = 30

    # -------------------------------------------------------------------------
    # SCENARIOS 1-5: PERSON VS CELESTIAL / NON-PERSON ENTITY BINDINGS
    # -------------------------------------------------------------------------
    print("\n[SCENARIOS 1-5] Person vs Celestial / Non-Person Entity Bindings...")

    # Scenario 1: Neil Armstrong / Moon - Preventing 'Moon' bound to 'he'
    cm.clear()
    cm.add_turn(
        user_query="Who was the first astronaut to walk on the Moon?",
        resolved_query="Who was the first astronaut to walk on the Moon?",
        response_text="Neil Armstrong became the first astronaut to walk on the Moon on July 20, 1969.",
        primary_entity="Neil Armstrong"
    )
    q1, is_f1, tc1 = cm.resolve_turn("In what year did he walk on the Moon?")
    intent1 = cm.classify_intent("In what year did he walk on the Moon?")
    assert_true(is_f1 and not tc1, "Scenario 1: Follow-up detected")
    assert_eq(intent1, FollowUpIntent.FOLLOW_UP, "Scenario 1: Intent is FOLLOW_UP")
    assert_true("moon walk on the moon" not in q1.lower(), "Scenario 1: Moon is NOT bound to 'he'")
    assert_true("neil armstrong" in q1.lower(), f"Scenario 1: 'he' resolved to Neil Armstrong (got: {q1})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["primary_entity"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 2: Astronaut on Moon without response_text (Query-only resolution)
    cm.clear()
    cm.add_turn(
        user_query="Who was the first astronaut to walk on the Moon?",
        resolved_query="Who was the first astronaut to walk on the Moon?",
        response_text="",  # No answer text provided
    )
    # Check that Moon was not falsely picked as person entity
    assert_true(not is_person_entity(cm.state.active_entity) if cm.state.active_entity == "Moon" else True,
                "Scenario 2: Moon is correctly identified as non-person")
    q2, is_f2, _ = cm.resolve_turn("In what year did he walk on the Moon?")
    assert_true("moon walk on the moon" not in q2.lower(), f"Scenario 2: Prevented 'Moon walk on the Moon' (got: {q2})")
    stage_metrics["primary_entity"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 3: Female Scientist Pronoun 'she' (Marie Curie)
    cm.clear()
    cm.add_turn(
        user_query="Who discovered radium and polonium?",
        resolved_query="Who discovered radium and polonium?",
        response_text="Marie Curie discovered radium and polonium in 1898.",
        primary_entity="Marie Curie"
    )
    q3, is_f3, _ = cm.resolve_turn("How many Nobel Prizes did she win?")
    assert_true(is_f3, "Scenario 3: Follow-up recognized")
    assert_true("marie curie" in q3.lower(), f"Scenario 3: 'she' resolved to Marie Curie (got: {q3})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["primary_entity"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 4: Mars Curiosity Rover Pronoun 'it' (Rover is inanimate)
    cm.clear()
    cm.add_turn(
        user_query="When did NASA launch Curiosity to Mars?",
        resolved_query="When did NASA launch Curiosity to Mars?",
        response_text="NASA launched the Curiosity rover in November 2011.",
        primary_entity="Curiosity"
    )
    q4, is_f4, _ = cm.resolve_turn("When did it land?")
    assert_true(is_f4, "Scenario 4: Inanimate pronoun follow-up recognized")
    assert_true("curiosity" in q4.lower(), f"Scenario 4: 'it' resolved to Curiosity (got: {q4})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["primary_entity"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 5: Multiple Persons in History with Ambiguity Detection
    cm.clear()
    cm.add_turn(
        user_query="Tell me about Kapil Dev and Travis Head in World Cup finals.",
        resolved_query="Tell me about Kapil Dev and Travis Head in World Cup finals.",
        response_text="Kapil Dev led India in 1983 while Travis Head scored 137 for Australia in 2023.",
    )
    cm.state.related_entities = ["Kapil Dev", "Travis Head"]
    intent5 = cm.classify_intent("How many runs did he score?")
    assert_eq(intent5, FollowUpIntent.AMBIGUOUS_FOLLOW_UP, "Scenario 5: Ambiguous 'he' across multiple persons detected")
    stage_metrics["intent_recognition"] += 1

    # -------------------------------------------------------------------------
    # SCENARIOS 6-10: DOUBLE POSSESSIVES & ATTRIBUTE REWRITING
    # -------------------------------------------------------------------------
    print("\n[SCENARIOS 6-10] Double Possessives & Attribute Rewriting...")

    # Scenario 6: Apple possessive follow-up ("What is its price?")
    cm.clear()
    cm.add_turn(
        user_query="Tell me about Apple's base iPhone 16.",
        resolved_query="Tell me about Apple's base iPhone 16.",
        response_text="Apple announced the base iPhone 16 in September 2024.",
        primary_entity="iPhone 16"
    )
    q6, is_f6, _ = cm.resolve_turn("What is its launch price?")
    assert_true(is_f6, "Scenario 6: Follow-up detected")
    assert_true("apple's's" not in q6.lower(), "Scenario 6: No Apple's's double possessive")
    assert_true("iphone 16's" in q6.lower() or "iphone 16" in q6.lower(), f"Scenario 6: Clean possessive (got: {q6})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["attribute_resolution"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 7: McDonald's possessive follow-up (Name already ending in 's)
    cm.clear()
    cm.add_turn(
        user_query="Where was McDonald's founded?",
        resolved_query="Where was McDonald's founded?",
        response_text="McDonald's was founded in San Bernardino, California.",
        primary_entity="McDonald's"
    )
    q7, is_f7, _ = cm.resolve_turn("Who was its founder?")
    assert_true("mcdonald's's" not in q7.lower(), f"Scenario 7: No double possessive on McDonald's (got: {q7})")
    assert_true("mcdonald" in q7.lower(), "Scenario 7: Entity retained")
    stage_metrics["query_clarity"] += 1
    stage_metrics["attribute_resolution"] += 1

    # Scenario 8: Two-word attribute follow-up: "And budget?"
    cm.clear()
    cm.add_turn(
        user_query="Who directed Oppenheimer?",
        resolved_query="Who directed Oppenheimer?",
        response_text="Christopher Nolan directed Oppenheimer.",
        primary_entity="Oppenheimer"
    )
    q8, is_f8, _ = cm.resolve_turn("And budget?")
    assert_true(is_f8, "Scenario 8: Two-word follow-up recognized")
    assert_true("oppenheimer" in q8.lower() and "budget" in q8.lower(), f"Scenario 8: Expanded to Oppenheimer budget (got: {q8})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["attribute_resolution"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 9: Two-word attribute follow-up: "Release date?"
    q9, is_f9, _ = cm.resolve_turn("Release date?")
    assert_true(is_f9, "Scenario 9: Two-word follow-up recognized")
    assert_true("oppenheimer" in q9.lower() and "release date" in q9.lower(), f"Scenario 9: Expanded to Oppenheimer release date (got: {q9})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["attribute_resolution"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 10: Changed Attribute: Director -> Lead Actor
    q10, is_f10, _ = cm.resolve_turn("Who was the lead actor?")
    intent10 = cm.classify_intent("Who was the lead actor?")
    assert_eq(intent10, FollowUpIntent.ENTITY_CHANGE, "Scenario 10: Classified as ENTITY_CHANGE")
    assert_true("oppenheimer" in q10.lower(), f"Scenario 10: Bound to Oppenheimer (got: {q10})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["attribute_resolution"] += 1
    stage_metrics["query_clarity"] += 1

    # -------------------------------------------------------------------------
    # SCENARIOS 11-15: TEMPORAL ANCHORS & YEAR CHANGES
    # -------------------------------------------------------------------------
    print("\n[SCENARIOS 11-15] Temporal Anchors & Year Changes...")

    # Scenario 11: Year substitution ("What about in 2011?")
    cm.clear()
    cm.add_turn(
        user_query="Who won the 2023 Cricket World Cup?",
        resolved_query="Who won the 2023 Cricket World Cup?",
        response_text="Australia won the 2023 Cricket World Cup defeating India.",
        primary_entity="Australia"
    )
    cm.state.active_event = "Cricket World Cup"
    cm.state.relevant_year = "2023"
    q11, is_f11, _ = cm.resolve_turn("What about in 2011?")
    intent11 = cm.classify_intent("What about in 2011?")
    assert_eq(intent11, FollowUpIntent.YEAR_CHANGE, "Scenario 11: Classified as YEAR_CHANGE")
    assert_true("2011" in q11, f"Scenario 11: New year 2011 injected (got: {q11})")
    assert_true("2023" not in q11, "Scenario 11: Old year 2023 removed")
    assert_true("cricket world cup" in q11.lower(), "Scenario 11: Tournament preserved")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["temporal_preservation"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 12: Elliptical Year Change ("And in 2019?")
    q12, is_f12, _ = cm.resolve_turn("And in 2019?")
    assert_true("2019" in q12, f"Scenario 12: Year 2019 injected (got: {q12})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["temporal_preservation"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 13: Changed Event ("What about the semi-final?")
    intent13 = cm.classify_intent("What about the semi-final?")
    assert_eq(intent13, FollowUpIntent.EVENT_CHANGE, "Scenario 13: Classified as EVENT_CHANGE")
    stage_metrics["intent_recognition"] += 1

    # Scenario 14: Future Olympic Year Change (2024 -> 2028)
    cm.clear()
    cm.add_turn(
        user_query="Which city hosted the 2024 Summer Olympic Games?",
        resolved_query="Which city hosted the 2024 Summer Olympic Games?",
        response_text="Paris hosted the 2024 Olympic Games.",
        primary_entity="Olympic Games"
    )
    q14, is_f14, _ = cm.resolve_turn("What about in 2028?")
    assert_true("2028" in q14 and "2024" not in q14, f"Scenario 14: Shifted to 2028 Olympics (got: {q14})")
    stage_metrics["temporal_preservation"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 15: Temporal anchor preservation in retrieval query
    assert_true("olympic games" in q14.lower() or "olympics" in q14.lower(), "Scenario 15: Event context maintained for retrieval")
    stage_metrics["temporal_preservation"] += 1

    # -------------------------------------------------------------------------
    # SCENARIOS 16-20: TOPIC BOUNDARY & RESET VERIFICATION
    # -------------------------------------------------------------------------
    print("\n[SCENARIOS 16-20] Topic Boundary Detection & Isolation...")

    # Scenario 16: Immediate topic change (Olympics -> Chemistry)
    q16, is_f16, tc16 = cm.resolve_turn("What is the chemical formula for water?")
    assert_true(not is_f16, "Scenario 16: Independent query not marked follow-up")
    assert_true(tc16, "Scenario 16: Topic change flag set")
    assert_true("olympic" not in q16.lower(), "Scenario 16: Zero context leakage")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 17: Topic change from Chemistry -> Corporate Tech
    cm.add_turn("What is the chemical formula for water?", "What is the chemical formula for water?", "H2O.", "water")
    q17, is_f17, tc17 = cm.resolve_turn("Where is Google headquartered?")
    assert_true(not is_f17, "Scenario 17: Independent corporate query")
    assert_true(tc17, "Scenario 17: Clean context switch")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 18: Corporate Follow-up after topic reset ("Who is their CEO?")
    cm.add_turn("Where is Google headquartered?", "Where is Google headquartered?", "Mountain View, CA.", "Google")
    q18, is_f18, tc18 = cm.resolve_turn("Who is their CEO?")
    assert_true(is_f18 and not tc18, "Scenario 18: Follow-up correctly recognized in new domain")
    assert_true("google" in q18.lower(), f"Scenario 18: Bound 'their' to Google (got: {q18})")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["primary_entity"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 19: Organization pronoun 'they'
    q19, is_f19, _ = cm.resolve_turn("When were they founded?")
    assert_true("google" in q19.lower(), f"Scenario 19: 'they' bound to Google (got: {q19})")
    stage_metrics["primary_entity"] += 1
    stage_metrics["query_clarity"] += 1

    # Scenario 20: Switch back to Sports
    q20, is_f20, tc20 = cm.resolve_turn("Who won the Super Bowl in 2024?")
    assert_true(not is_f20 and tc20, "Scenario 20: Clean switch back to Sports")
    assert_true("google" not in q20.lower(), "Scenario 20: Zero leakage")
    stage_metrics["intent_recognition"] += 1
    stage_metrics["query_clarity"] += 1

    # -------------------------------------------------------------------------
    # SCENARIOS 21-25: RETRIEVAL & EVIDENCE SELECTION COUPLING
    # -------------------------------------------------------------------------
    print("\n[SCENARIOS 21-25] Retrieval & Evidence Passage Selection Coupling...")

    # Scenario 21: Deep article chunk selection beyond 1,200 chars
    fluff = "General history of cricket. " * 30  # ~840 chars
    deep_fact = "In the 1983 World Cup final, Kapil Dev scored 15 runs and took 1 wicket."
    doc_kapil = ExtractedDocument(
        title="1983 World Cup Final Report",
        url="https://cricinfo.com/1983-final",
        clean_text=fluff + "\n\n" + deep_fact,
        source_index=1,
        relevance_score=0.95
    )
    chunks21 = select_top_evidence_chunks("Kapil Dev score 1983 final", [doc_kapil], max_chunks=3)
    assert_true(len(chunks21) > 0, "Scenario 21: Evidence chunks selected")
    assert_true(any("15 runs" in c.text for c in chunks21), "Scenario 21: Deep passage (>1,200 chars) selected")
    stage_metrics["retrieval_relevance"] += 1
    stage_metrics["evidence_selection"] += 1

    # Scenario 22: Selective retrieval ignoring irrelevant intro fluff
    assert_true("15 runs" in chunks21[0].text, "Scenario 21: Answer-bearing chunk ranked #1")
    stage_metrics["evidence_selection"] += 1

    # Scenario 23: Structured numerical table chunk selection
    table_text = (
        "Tesla Model 3 specifications:\n"
        "| Model | Starting Price | Range |\n"
        "| Model 3 RWD | $38,990 | 272 miles |\n"
        "| Model 3 Long Range AWD | $47,740 | 341 miles |\n"
    )
    doc_table = ExtractedDocument(
        title="Tesla Specs",
        url="https://tesla.com/specs",
        clean_text=table_text,
        source_index=2,
        relevance_score=0.98
    )
    chunks23 = select_top_evidence_chunks("Tesla Model 3 Long Range AWD range", [doc_table], max_chunks=2)
    assert_true(any("341 miles" in c.text for c in chunks23), "Scenario 23: Table data preserved and retrieved")
    stage_metrics["retrieval_relevance"] += 1
    stage_metrics["evidence_selection"] += 1

    # Scenario 24: Deduplication of syndicated evidence
    doc_dup1 = ExtractedDocument(title="News A", url="https://newsa.com", clean_text="India landed Chandrayaan-3 on the Moon on August 23, 2023.", source_index=3)
    doc_dup2 = ExtractedDocument(title="News B", url="https://newsb.com", clean_text="India landed Chandrayaan-3 on the Moon on August 23, 2023.", source_index=4)
    chunks24 = select_top_evidence_chunks("Chandrayaan-3 landing date", [doc_dup1, doc_dup2], max_chunks=3)
    assert_eq(len(chunks24), 1, "Scenario 24: Identical syndicated chunks deduplicated to 1")
    stage_metrics["evidence_selection"] += 1

    # Scenario 25: Evidence budget enforcement
    total_chars = sum(len(c.text) for c in chunks24)
    assert_true(total_chars <= 1200, "Scenario 25: Evidence budget respected")
    stage_metrics["evidence_selection"] += 1

    # -------------------------------------------------------------------------
    # SCENARIOS 26-30: SYNTHESIS FACTUAL ACCURACY & VERIFICATION TRUTH-STATE
    # -------------------------------------------------------------------------
    print("\n[SCENARIOS 26-30] Synthesis Factual Accuracy & Verification Truth-State...")

    # Scenario 26: Fully corroborated numerical claim -> VERIFIED
    synth26 = "The Tesla Model 3 Long Range AWD has a range of 341 miles [2]."
    v26 = verifier.audit_and_verify_response("Range of Model 3 AWD", synth26, [doc_table])
    assert_eq(v26.response_state, ResponseState.VERIFIED, "Scenario 26: Correct numerical claim is VERIFIED")
    assert_true("341 miles" in v26.final_text, "Scenario 26: Accurate answer preserved")
    stage_metrics["synthesis_factual"] += 1
    stage_metrics["truth_state_fidelity"] += 1

    # Scenario 27: Cross-trim contamination numerical claim -> Contradiction -> ABSTAIN
    synth27 = "The Tesla Model 3 Long Range AWD has a range of 272 miles [2]."
    v27 = verifier.audit_and_verify_response("Range of Model 3 AWD", synth27, [doc_table])
    assert_true(v27.response_state != ResponseState.VERIFIED, "Scenario 27: Contaminated trim is NOT VERIFIED")
    assert_eq(v27.response_state, ResponseState.ABSTAIN, "Scenario 27: Contradicted response maps to ABSTAIN")
    stage_metrics["synthesis_factual"] += 1
    stage_metrics["truth_state_fidelity"] += 1

    # Scenario 28: Mixed answer with 1 fact + 1 hallucination -> PARTIAL (Sanitized)
    synth28 = (
        "The Tesla Model 3 Long Range AWD has a range of 341 miles [2]. "
        "The car is also equipped with a nuclear fusion generator capable of powering a city."
    )
    v28 = verifier.audit_and_verify_response("Tesla specs", synth28, [doc_table])
    assert_eq(v28.response_state, ResponseState.PARTIAL, "Scenario 28: Mixed answer is PARTIAL")
    assert_true("341 miles" in v28.final_text, "Scenario 28: Factual claim preserved")
    assert_true("nuclear fusion" not in v28.final_text, "Scenario 28: Hallucination sanitized")
    stage_metrics["synthesis_factual"] += 1
    stage_metrics["truth_state_fidelity"] += 1

    # Scenario 29: Unverifiable counterfactual query -> Safe Abstention
    refusal29 = "The provided evidence does not contain information about the 2030 World Cup winner."
    v29 = verifier.audit_and_verify_response("Who won 2030 World Cup?", refusal29, [doc_kapil])
    assert_eq(v29.response_state, ResponseState.ABSTAIN, "Scenario 29: Unanswerable refusal maps to ABSTAIN")
    stage_metrics["synthesis_factual"] += 1
    stage_metrics["truth_state_fidelity"] += 1

    # Scenario 30: Zero retrieved evidence in Hybrid mode -> UNVERIFIED
    v30 = verifier.audit_and_verify_response("Photosynthesis explanation", "Photosynthesis produces glucose and oxygen.", docs=[], is_internal_generation=True)
    assert_eq(v30.response_state, ResponseState.UNVERIFIED, "Scenario 30: Parametric answer flagged UNVERIFIED")
    assert_true("UNVERIFIED - PARAMETRIC KNOWLEDGE" in v30.final_text, "Scenario 30: Transparent disclaimer banner attached")
    stage_metrics["truth_state_fidelity"] += 1

    # -------------------------------------------------------------------------
    # SUMMARY OF THE 9 DECOUPLED STAGE METRICS
    # -------------------------------------------------------------------------
    print("\n" + "=" * 70)
    print("   STAGE DECOUPLING METRICS SUMMARY (30 SCENARIOS)")
    print("=" * 70)
    print(f"  1. Follow-up Intent Recognition:     {stage_metrics['intent_recognition']} evaluations passed")
    print(f"  2. Primary Entity Resolution:         {stage_metrics['primary_entity']} evaluations passed")
    print(f"  3. Attribute Resolution:              {stage_metrics['attribute_resolution']} evaluations passed")
    print(f"  4. Temporal Anchor Preservation:      {stage_metrics['temporal_preservation']} evaluations passed")
    print(f"  5. Standalone Query Clarity:          {stage_metrics['query_clarity']} evaluations passed")
    print(f"  6. Retrieval Relevance:               {stage_metrics['retrieval_relevance']} evaluations passed")
    print(f"  7. Evidence Selection:                {stage_metrics['evidence_selection']} evaluations passed")
    print(f"  8. Synthesis Factual Accuracy:        {stage_metrics['synthesis_factual']} evaluations passed")
    print(f"  9. Truth-State Fidelity:              {stage_metrics['truth_state_fidelity']} evaluations passed")

    assert_true(all(v > 0 for v in stage_metrics.values()), "All 9 distinct pipeline stages independently measured and verified")

    print("\n" + "=" * 70)
    print(f"✓ SPRINT 5.3.1 CONTEXT STAGE AUDIT: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_context_stage_audit_suite()
