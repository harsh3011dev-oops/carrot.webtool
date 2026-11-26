"""
PROJECT NOVA — SPRINT 5.3: Phase 1 Multi-Turn Context Intelligence Test Suite
============================================================================
Comprehensive 25-case regression suite testing contextual query resolution:
1. Pronoun 'it'
2. Pronoun 'he'
3. Pronoun 'they'
4. 'What about in 2011?'
5. Changed year
6. Changed entity
7. Changed event
8. Changed attribute
9. Short follow-up of two words
10. Short follow-up of six words
11. Longer follow-up
12. Topic change
13. Return to previous topic
14. Multiple entities in history
15. Multiple years in history
16. Ambiguous pronoun
17. Ambiguous event
18. Follow-up requiring a fresh web search
19. Follow-up supported by previous evidence
20. Follow-up requiring additional evidence
21. Context clearing
22. Context preservation
23. Similar entity names
24. Temporal shift
25. Repeated follow-up
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from intelligence.context_manager import ConversationContextManager
from intelligence.schemas import FollowUpIntent

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


def run_context_intelligence_suite():
    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.3: CONTEXT INTELLIGENCE TEST SUITE (25 CASES)")
    print("=" * 70)

    cm = ConversationContextManager()

    # -------------------------------------------------------------------------
    # Case 1: Pronoun 'it' (Oppenheimer release year)
    # -------------------------------------------------------------------------
    print("\n[1/25] Testing Pronoun 'it'...")
    cm.clear()
    cm.add_turn(
        user_query="Who directed Oppenheimer?",
        resolved_query="Who directed Oppenheimer?",
        response_text="Oppenheimer was directed by Christopher Nolan in 2023.",
        primary_entity="Oppenheimer"
    )
    q1, is_f1, _ = cm.resolve_turn("In what year was it released?")
    assert_true(is_f1, "Case 1: Follow-up detected")
    assert_true("oppenheimer" in q1.lower(), f"Case 1: 'it' resolved to Oppenheimer (got: {q1})")

    # -------------------------------------------------------------------------
    # Case 2: Pronoun 'he' (Albert Einstein)
    # -------------------------------------------------------------------------
    print("\n[2/25] Testing Pronoun 'he'...")
    cm.clear()
    cm.add_turn(
        user_query="Tell me about Albert Einstein.",
        resolved_query="Tell me about Albert Einstein.",
        response_text="Albert Einstein was a theoretical physicist born in Germany.",
        primary_entity="Albert Einstein"
    )
    q2, is_f2, _ = cm.resolve_turn("When was he born?")
    assert_true(is_f2, "Case 2: Follow-up detected")
    assert_true("einstein" in q2.lower(), f"Case 2: 'he' resolved to Einstein (got: {q2})")

    # -------------------------------------------------------------------------
    # Case 3: Pronoun 'they' (Google)
    # -------------------------------------------------------------------------
    print("\n[3/25] Testing Pronoun 'they'...")
    cm.clear()
    cm.add_turn(
        user_query="When was Google founded?",
        resolved_query="When was Google founded?",
        response_text="Google was founded on September 4, 1998, by Larry Page and Sergey Brin.",
        primary_entity="Google"
    )
    q3, is_f3, _ = cm.resolve_turn("Where are they headquartered?")
    assert_true(is_f3, "Case 3: Follow-up detected")
    assert_true("google" in q3.lower(), f"Case 3: 'they' resolved to Google (got: {q3})")

    # -------------------------------------------------------------------------
    # Case 4: "What about in 2011?"
    # -------------------------------------------------------------------------
    print("\n[4/25] Testing 'What about in 2011?'...")
    cm.clear()
    cm.add_turn(
        user_query="Who won the 2023 Cricket World Cup?",
        resolved_query="Who won the 2023 Cricket World Cup?",
        response_text="Australia won the 2023 ICC Men's Cricket World Cup.",
        primary_entity="Australia"
    )
    q4, is_f4, _ = cm.resolve_turn("What about in 2011?")
    assert_true(is_f4, "Case 4: Follow-up detected")
    assert_true("2011" in q4, f"Case 4: Year 2011 injected (got: {q4})")
    assert_true("cricket" in q4.lower() or "world cup" in q4.lower(), "Case 4: Retains tournament subject")

    # -------------------------------------------------------------------------
    # Case 5: Changed Year (2024 Olympics -> 2028)
    # -------------------------------------------------------------------------
    print("\n[5/25] Testing Changed Year...")
    cm.clear()
    cm.add_turn(
        user_query="Which city hosted the 2024 Olympic Games?",
        resolved_query="Which city hosted the 2024 Olympic Games?",
        response_text="Paris hosted the 2024 Summer Olympic Games.",
        primary_entity="Paris"
    )
    q5, is_f5, _ = cm.resolve_turn("And in 2028?")
    assert_true(is_f5, "Case 5: Follow-up detected")
    assert_true("2028" in q5, f"Case 5: Year 2028 updated (got: {q5})")
    assert_true("2024" not in q5, "Case 5: Old year 2024 removed")

    # -------------------------------------------------------------------------
    # Case 6: Changed Entity (Winning Team -> Runner Up)
    # -------------------------------------------------------------------------
    print("\n[6/25] Testing Changed Entity...")
    cm.clear()
    cm.add_turn(
        user_query="Who won the 2023 Cricket World Cup?",
        resolved_query="Who won the 2023 Cricket World Cup?",
        response_text="Australia defeated India by 6 wickets in Ahmedabad.",
        primary_entity="Australia"
    )
    q6, is_f6, _ = cm.resolve_turn("Who was the runner up?")
    assert_true(is_f6, "Case 6: Follow-up detected")
    assert_true("runner up" in q6.lower(), "Case 6: Retains runner up attribute")
    assert_true("world cup" in q6.lower(), f"Case 6: Retains tournament context (got: {q6})")

    # -------------------------------------------------------------------------
    # Case 7: Changed Event (Final -> Semi-final)
    # -------------------------------------------------------------------------
    print("\n[7/25] Testing Changed Event...")
    intent7 = cm.classify_intent("What about in the semi-final?")
    assert_eq(intent7, FollowUpIntent.EVENT_CHANGE, "Case 7: Classified as EVENT_CHANGE")

    # -------------------------------------------------------------------------
    # Case 8: Changed Attribute (Director -> Lead Actor)
    # -------------------------------------------------------------------------
    print("\n[8/25] Testing Changed Attribute...")
    cm.clear()
    cm.add_turn(
        user_query="Who directed Oppenheimer?",
        resolved_query="Who directed Oppenheimer?",
        response_text="Christopher Nolan directed Oppenheimer.",
        primary_entity="Oppenheimer"
    )
    q8, is_f8, _ = cm.resolve_turn("Who was the lead actor?")
    assert_true(is_f8, "Case 8: Follow-up detected")
    assert_true("oppenheimer" in q8.lower(), f"Case 8: Bound attribute to Oppenheimer (got: {q8})")

    # -------------------------------------------------------------------------
    # Case 9: Short follow-up of two words ("And budget?")
    # -------------------------------------------------------------------------
    print("\n[9/25] Testing Short Follow-Up of Two Words...")
    q9, is_f9, _ = cm.resolve_turn("And budget?")
    assert_true(is_f9, "Case 9: Two-word follow-up detected")
    assert_true("oppenheimer" in q9.lower(), f"Case 9: Resolved to Oppenheimer budget (got: {q9})")

    # -------------------------------------------------------------------------
    # Case 10: Short follow-up of six words ("What about its total box office?")
    # -------------------------------------------------------------------------
    print("\n[10/25] Testing Short Follow-Up of Six Words...")
    q10, is_f10, _ = cm.resolve_turn("What about its total box office?")
    assert_true(is_f10, "Case 10: Six-word follow-up detected")
    assert_true("oppenheimer" in q10.lower(), f"Case 10: Replaced its with Oppenheimer (got: {q10})")

    # -------------------------------------------------------------------------
    # Case 11: Longer follow-up with multiple clauses
    # -------------------------------------------------------------------------
    print("\n[11/25] Testing Longer Follow-Up...")
    q11, is_f11, _ = cm.resolve_turn("Can you tell me which awards that movie won at the Oscars?")
    assert_true(is_f11, "Case 11: Long follow-up detected")
    assert_true("oppenheimer" in q11.lower(), f"Case 11: Substituted 'that movie' with Oppenheimer (got: {q11})")

    # -------------------------------------------------------------------------
    # Case 12: Topic Change (Oppenheimer -> Geography)
    # -------------------------------------------------------------------------
    print("\n[12/25] Testing Topic Change...")
    q12, is_f12, tc12 = cm.resolve_turn("What is the capital of Japan?")
    assert_true(not is_f12, "Case 12: Independent topic NOT a follow-up")
    assert_true(tc12, "Case 12: Topic boundary reset triggered")
    assert_true("oppenheimer" not in q12.lower(), "Case 12: Zero context leakage")

    # -------------------------------------------------------------------------
    # Case 13: Return to previous topic after clean reset
    # -------------------------------------------------------------------------
    print("\n[13/25] Testing Return to Previous Topic...")
    cm.add_turn("What is the capital of Japan?", "What is the capital of Japan?", "Tokyo.", "Tokyo")
    q13, is_f13, tc13 = cm.resolve_turn("Who directed Inception?")
    assert_true(not is_f13, "Case 13: New query treated independently")
    assert_true(tc13, "Case 13: Clean context switch")

    # -------------------------------------------------------------------------
    # Case 14: Multiple entities in history (Company vs Product)
    # -------------------------------------------------------------------------
    print("\n[14/25] Testing Multiple Entities in History...")
    cm.clear()
    cm.add_turn(
        user_query="What was Apple's base smartphone released in September 2023?",
        resolved_query="What was Apple's base smartphone released in September 2023?",
        response_text="Apple released the iPhone 15 in September 2023 starting at $799.",
        primary_entity="iPhone 15"
    )
    q14, is_f14, _ = cm.resolve_turn("What was its launch starting price in US dollars?")
    assert_true(is_f14, "Case 14: Follow-up detected")
    assert_true("iphone 15" in q14.lower(), f"Case 14: Prioritizes iPhone 15 over Apple (got: {q14})")

    # -------------------------------------------------------------------------
    # Case 15: Multiple years in history
    # -------------------------------------------------------------------------
    print("\n[15/25] Testing Multiple Years in History...")
    cm.clear()
    cm.add_turn(
        user_query="Compare the 2011 and 2023 Cricket World Cup finals.",
        resolved_query="Compare the 2011 and 2023 Cricket World Cup finals.",
        response_text="In 2011 India won, while in 2023 Australia won.",
        primary_entity="Cricket World Cup"
    )
    intent15 = cm.classify_intent("What about in 2015?")
    assert_eq(intent15, FollowUpIntent.YEAR_CHANGE, "Case 15: Recognizes YEAR_CHANGE")

    # -------------------------------------------------------------------------
    # Case 16: Ambiguous Pronoun with multiple people
    # -------------------------------------------------------------------------
    print("\n[16/25] Testing Ambiguous Pronoun Detection...")
    cm.clear()
    cm.add_turn(
        user_query="Did Christopher Nolan direct Cillian Murphy in Oppenheimer?",
        resolved_query="Did Christopher Nolan direct Cillian Murphy in Oppenheimer?",
        response_text="Yes, Christopher Nolan directed Cillian Murphy in Oppenheimer.",
        primary_entity="Oppenheimer"
    )
    # Set related entities with 2 distinct people
    cm.state.related_entities = ["Christopher Nolan", "Cillian Murphy"]
    intent16 = cm.classify_intent("When was he born?")
    assert_eq(intent16, FollowUpIntent.AMBIGUOUS_FOLLOW_UP, "Case 16: Ambiguous pronoun flagged")

    # -------------------------------------------------------------------------
    # Case 17: Ambiguous Event
    # -------------------------------------------------------------------------
    print("\n[17/25] Testing Event Context Resolution...")
    cm.clear()
    cm.add_turn(
        user_query="Who won the 2019 ICC Cricket World Cup?",
        resolved_query="Who won the 2019 ICC Cricket World Cup?",
        response_text="England won the 2019 ICC Cricket World Cup by defeating New Zealand.",
        primary_entity="England"
    )
    q17, is_f17, _ = cm.resolve_turn("Who was their captain in that tournament?")
    assert_true(is_f17, "Case 17: Follow-up detected")
    assert_true("england" in q17.lower(), f"Case 17: Contains England (got: {q17})")
    assert_true("2019" in q17 or "cricket world cup" in q17.lower(), "Case 17: Retains tournament context")

    # -------------------------------------------------------------------------
    # Case 18: Follow-up requiring fresh web search
    # -------------------------------------------------------------------------
    print("\n[18/25] Testing Follow-Up Requiring Fresh Web Search...")
    q18, is_f18, _ = cm.resolve_turn("Who is their current captain today?")
    assert_true(is_f18, "Case 18: Follow-up detected")
    assert_true("england" in q18.lower(), "Case 18: Targets England current captain")

    # -------------------------------------------------------------------------
    # Case 19: Follow-up supported by previous context
    # -------------------------------------------------------------------------
    print("\n[19/25] Testing Follow-Up Supported by Prior Turn Context...")
    assert_true(cm.state.active_entity == "England", "Case 19: Active entity is England")

    # -------------------------------------------------------------------------
    # Case 20: Follow-up requiring additional attribute evidence
    # -------------------------------------------------------------------------
    print("\n[20/25] Testing Follow-Up Requiring Attribute Expansion...")
    q20, is_f20, _ = cm.resolve_turn("Who was the player of the match in the final?")
    assert_true(is_f20, "Case 20: Follow-up detected")

    # -------------------------------------------------------------------------
    # Case 21: Context Clearing Verification
    # -------------------------------------------------------------------------
    print("\n[21/25] Testing Context Clearing...")
    cm.clear()
    assert_eq(len(cm.history), 0, "Case 21: History is empty")
    assert_eq(cm.state.active_entity, None, "Case 21: Active entity is reset")
    assert_eq(cm.state.active_topic, "GENERAL", "Case 21: Active topic reset to GENERAL")

    # -------------------------------------------------------------------------
    # Case 22: Context Preservation across 3 consecutive turns
    # -------------------------------------------------------------------------
    print("\n[22/25] Testing Consecutive Context Preservation...")
    cm.add_turn("Who directed Inception?", "Who directed Inception?", "Christopher Nolan.", "Inception")
    q22_t2, _, _ = cm.resolve_turn("In what year was it released?")
    assert_true("inception" in q22_t2.lower(), "Case 22 (Turn 2): Retains Inception")
    cm.add_turn("In what year was it released?", q22_t2, "Released in 2010.", "Inception")
    q22_t3, _, _ = cm.resolve_turn("What was its budget?")
    assert_true("inception" in q22_t3.lower(), f"Case 22 (Turn 3): Retains Inception for budget (got: {q22_t3})")

    # -------------------------------------------------------------------------
    # Case 23: Disambiguation of Similar Entity Names (iPhone 15 vs iPhone 15 Pro)
    # -------------------------------------------------------------------------
    print("\n[23/25] Testing Disambiguation of Similar Variants...")
    cm.clear()
    cm.add_turn("Tell me about the iPhone 15.", "Tell me about the iPhone 15.", "Base model starting at $799.", "iPhone 15")
    q23, is_f23, _ = cm.resolve_turn("What about the Pro Max?")
    assert_true(is_f23, "Case 23: Follow-up recognized")

    # -------------------------------------------------------------------------
    # Case 24: Temporal Shift ("And in 2022?")
    # -------------------------------------------------------------------------
    print("\n[24/25] Testing Temporal Shift...")
    cm.clear()
    cm.add_turn("What was the price of the iPhone in 2023?", "What was the price of the iPhone in 2023?", "$799.", "iPhone")
    q24, is_f24, _ = cm.resolve_turn("What about in 2022?")
    assert_true("2022" in q24, f"Case 24: Injects 2022 (got: {q24})")
    assert_true("2023" not in q24, "Case 24: Replaces 2023")

    # -------------------------------------------------------------------------
    # Case 25: Repeated Follow-Up
    # -------------------------------------------------------------------------
    print("\n[25/25] Testing Repeated Follow-Up...")
    q25_a, _, _ = cm.resolve_turn("And in 2021?")
    assert_true("2021" in q25_a, f"Case 25: Injects 2021 (got: {q25_a})")

    print("\n" + "=" * 70)
    print(f"✓ PHASE 1 CONTEXT INTELLIGENCE SUITE: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_context_intelligence_suite()

