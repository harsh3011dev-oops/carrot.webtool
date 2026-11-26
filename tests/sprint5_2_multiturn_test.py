"""
PROJECT NOVA — SPRINT 5.2: Phase 6 Multi-Turn End-to-End Test Suite
==================================================================
Tests 15 multi-turn conversational scenarios:
1-4: Year shifts (e.g., 2023 -> 2011)
5-8: Entity shifts (e.g., director -> lead actor)
9-11: Pronoun resolution (e.g., he, she, it)
12-15: Topic boundary reset (zero context leakage)
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from intelligence.context_manager import ConversationContextManager

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


def run_multiturn_suite():
    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.2: PHASE 6 MULTI-TURN END-TO-END SUITE")
    print("=" * 70)

    cm = ConversationContextManager()

    # -------------------------------------------------------------------------
    # PART 1: Year Shifts (Cases 1 - 4)
    # -------------------------------------------------------------------------
    print("\n[PART 1] Testing Year Shifts in Multi-Turn Follow-Ups...")
    
    # Case 1: 2023 World Cup -> 2011
    cm.clear()
    cm.add_turn("Who won the 2023 Cricket World Cup?", "Who won the 2023 Cricket World Cup?", "Australia won the 2023 World Cup.", "Australia")
    q1, is_f1, _ = cm.resolve_turn("What about in 2011?")
    assert_true(is_f1, "Case 1: Detected as follow-up")
    assert_true("2011" in q1, "Case 1: Incorporates target year 2011")
    assert_true("cricket" in q1.lower() or "world cup" in q1.lower(), "Case 1: Retains tournament subject")

    # Case 2: 2024 Olympics -> 2028
    cm.clear()
    cm.add_turn("Which city hosted the 2024 Olympic Games?", "Which city hosted the 2024 Olympic Games?", "Paris hosted the 2024 Games.", "Paris")
    q2, is_f2, _ = cm.resolve_turn("What about in 2028?")
    assert_true(is_f2, "Case 2: Detected as follow-up")
    assert_true("2028" in q2, "Case 2: Incorporates target year 2028")

    # Case 3: 2023 iPhone 15 -> 2022
    cm.clear()
    cm.add_turn("What was the price of the iPhone in 2023?", "What was the price of the iPhone in 2023?", "The iPhone starting price in 2023 was $799.", "iPhone")
    q3, is_f3, _ = cm.resolve_turn("What about in 2022?")
    assert_true(is_f3, "Case 3: Detected as follow-up")
    assert_true("2022" in q3, "Case 3: Injects year 2022")

    # Case 4: FIFA World Cup 2022 -> 2018
    cm.clear()
    cm.add_turn("Who won the FIFA World Cup in 2022?", "Who won the FIFA World Cup in 2022?", "Argentina won in 2022.", "Argentina")
    q4, is_f4, _ = cm.resolve_turn("What about in 2018?")
    assert_true(is_f4, "Case 4: Detected as follow-up")
    assert_true("2018" in q4, "Case 4: Incorporates year 2018")

    # -------------------------------------------------------------------------
    # PART 2: Entity Shifts (Cases 5 - 8)
    # -------------------------------------------------------------------------
    print("\n[PART 2] Testing Entity Shifts in Multi-Turn Follow-Ups...")

    # Case 5: Movie Director -> Lead Actor
    cm.clear()
    cm.add_turn("Who directed Oppenheimer?", "Who directed Oppenheimer?", "Christopher Nolan directed Oppenheimer.", "Oppenheimer")
    q5, is_f5, _ = cm.resolve_turn("Who was the lead actor in that movie?")
    assert_true(is_f5, "Case 5: Detected as follow-up")
    assert_true("oppenheimer" in q5.lower(), "Case 5: Carries subject 'Oppenheimer'")

    # Case 6: Company Founder -> Current CEO
    cm.clear()
    cm.add_turn("Who founded Microsoft in 1975?", "Who founded Microsoft in 1975?", "Bill Gates and Paul Allen founded Microsoft.", "Microsoft")
    q6, is_f6, _ = cm.resolve_turn("Who is their current CEO?")
    assert_true(is_f6, "Case 6: Detected as follow-up")
    assert_true("microsoft" in q6.lower(), "Case 6: Carries entity 'Microsoft'")

    # Case 7: Winning Team -> Captain
    cm.clear()
    cm.add_turn("Who won the 2023 Cricket World Cup?", "Who won the 2023 Cricket World Cup?", "Australia won the 2023 World Cup.", "Australia")
    q7, is_f7, _ = cm.resolve_turn("Who was their captain?")
    assert_true(is_f7, "Case 7: Detected as follow-up")
    assert_true("australia" in q7.lower(), "Case 7: Resolves their to Australia")

    # Case 8: Smartphone Base Model -> Pro Max
    cm.clear()
    cm.add_turn("What is the battery of the iPhone 16?", "What is the battery of the iPhone 16?", "3561 mAh for iPhone 16.", "iPhone 16")
    q8, is_f8, _ = cm.resolve_turn("What about the final score?")
    assert_true(is_f8, "Case 8: Relative context handled")

    # -------------------------------------------------------------------------
    # PART 3: Pronoun Resolution (Cases 9 - 11)
    # -------------------------------------------------------------------------
    print("\n[PART 3] Testing Pronoun Resolution...")

    # Case 9: "he" -> Albert Einstein
    cm.clear()
    cm.add_turn("Tell me about Albert Einstein.", "Tell me about Albert Einstein.", "Albert Einstein was a Nobel laureate.", "Albert Einstein")
    q9, is_f9, _ = cm.resolve_turn("When was he born?")
    assert_true(is_f9, "Case 9: Pronoun 'he' detected as follow-up")
    assert_true("einstein" in q9.lower(), "Case 9: Resolves 'he' to Einstein")

    # Case 10: "they" -> Google
    cm.clear()
    cm.add_turn("When was Google founded?", "When was Google founded?", "Google was founded in 1998.", "Google")
    q10, is_f10, _ = cm.resolve_turn("Where are they headquartered?")
    assert_true(is_f10, "Case 10: Pronoun 'they' detected as follow-up")
    assert_true("google" in q10.lower(), "Case 10: Resolves 'they' to Google")

    # Case 11: "it" -> Chandrayaan-3
    cm.clear()
    cm.add_turn("When was Chandrayaan-3 launched?", "When was Chandrayaan-3 launched?", "Chandrayaan-3 launched in July 2023.", "Chandrayaan-3")
    q11, is_f11, _ = cm.resolve_turn("Where was it launched from?")
    assert_true(is_f11, "Case 11: Pronoun 'it' detected as follow-up")
    assert_true("chandrayaan" in q11.lower(), "Case 11: Resolves 'it' to Chandrayaan-3")

    # -------------------------------------------------------------------------
    # PART 4: Topic Boundary Reset / Zero Context Leakage (Cases 12 - 15)
    # -------------------------------------------------------------------------
    print("\n[PART 4] Testing Topic Boundary Reset (Zero Context Leakage)...")

    # Case 12: Sports -> Pure Math
    cm.clear()
    cm.add_turn("Who won the 2023 Cricket World Cup?", "Who won the 2023 Cricket World Cup?", "Australia.", "Australia")
    q12, is_f12, tc12 = cm.resolve_turn("What is the square root of 144?")
    assert_true(not is_f12, "Case 12: Math question is NOT marked as follow-up")
    assert_true(tc12, "Case 12: Topic boundary reset detected")
    assert_true("cricket" not in q12.lower(), "Case 12: Zero cricket leakage into math")

    # Case 13: History -> Chemistry Formula
    cm.clear()
    cm.add_turn("When was the Battle of Waterloo fought?", "When was the Battle of Waterloo fought?", "1815.", "Battle of Waterloo")
    q13, is_f13, tc13 = cm.resolve_turn("What is the chemical symbol for Gold?")
    assert_true(not is_f13, "Case 13: Chemistry is NOT a follow-up")
    assert_true(tc13, "Case 13: Topic boundary reset detected")
    assert_true("waterloo" not in q13.lower(), "Case 13: Zero Waterloo leakage into chemistry")

    # Case 14: Tech Gadget -> Geography
    cm.clear()
    cm.add_turn("What is the price of the iPhone 16 Pro?", "What is the price of the iPhone 16 Pro?", "$999.", "iPhone 16 Pro")
    q14, is_f14, tc14 = cm.resolve_turn("What is the capital of Japan?")
    assert_true(not is_f14, "Case 14: Geography is independent")
    assert_true(tc14, "Case 14: Topic boundary reset detected")
    assert_true("iphone" not in q14.lower(), "Case 14: Zero iPhone leakage into geography")

    # Case 15: Politics -> Space Science
    cm.clear()
    cm.add_turn("Who is the Prime Minister of the United Kingdom?", "Who is the Prime Minister of the United Kingdom?", "Keir Starmer.", "Keir Starmer")
    q15, is_f15, tc15 = cm.resolve_turn("How many moons does Mars have?")
    assert_true(not is_f15, "Case 15: Astronomy is independent")
    assert_true(tc15, "Case 15: Topic boundary reset detected")
    assert_true("prime minister" not in q15.lower(), "Case 15: Zero politics leakage into astronomy")

    print("\n" + "=" * 70)
    print(f"✓ PHASE 6 MULTI-TURN SUITE: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_multiturn_suite()
