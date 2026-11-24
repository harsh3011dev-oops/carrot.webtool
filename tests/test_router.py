"""
PROJECT NOVA - Intelligent Query Router Test Suite
Tests diverse queries: Static, Dynamic, Ambiguous, Private Doc, and Hybrid.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from intelligence.router import IntelligentQueryRouter
from intelligence.schemas import RouteType


def test_iqr_suite():
    router = IntelligentQueryRouter()
    print("=" * 70)
    print("   PROJECT NOVA - INTELLIGENT QUERY ROUTING BENCHMARK")
    print("=" * 70)

    test_cases = [
        # 1. Conversational Greeting
        {
            "query": "Hello! Who are you?",
            "expected": RouteType.INTERNAL_LLM,
            "description": "Conversational Greeting",
        },
        # 2. Static Math Formula
        {
            "query": "What is the derivative of sin(x)*cos(x)?",
            "expected": RouteType.INTERNAL_LLM,
            "description": "Pure Math Calculus",
        },
        # 3. Static Code Generation
        {
            "query": "Write a python function to check if a string is a palindrome",
            "expected": RouteType.INTERNAL_LLM,
            "description": "Code Generation / Algorithm",
        },
        # 4. Static Deep Concept
        {
            "query": "Explain how the self-attention mechanism works in Transformer neural networks.",
            "expected": RouteType.INTERNAL_LLM,
            "description": "Deep Technical Explanation",
        },
        # 5. Misleading Word (Has 'current', but is actually static physics)
        {
            "query": "What does the word current mean in physics and electrical circuits?",
            "expected": RouteType.INTERNAL_LLM,
            "description": "Ambiguous/Misleading Freshness Keyword ('current')",
        },
        # 6. Extreme Volatility (Live Financial Price)
        {
            "query": "What is the current Bitcoin price in USD right now?",
            "expected": RouteType.WEB_SEARCH,
            "description": "Extreme Volatility (Crypto Price)",
        },
        # 7. Dynamic Breaking News / Post-Cutoff Event
        {
            "query": "What are the latest updates about NASA Artemis mission in 2026?",
            "expected": RouteType.WEB_SEARCH,
            "description": "Time-Sensitive 2026 News",
        },
        # 8. Private Document / Uploaded File
        {
            "query": "Summarize the key financial highlights from my uploaded PDF report.",
            "expected": RouteType.INTERNAL_RAG,
            "description": "Private Document Reference",
        },
    ]

    passed = 0
    failed = 0

    for i, tc in enumerate(test_cases, 1):
        query = tc["query"]
        expected = tc["expected"]
        desc = tc["description"]

        print(f"\n[Test {i}/8] {desc}")
        print(f"Query: \"{query}\"")

        decision = router.route(query)

        print(f"-> Primary Route : {decision.primary_route.value}")
        print(f"-> Tier Source   : {decision.tier_source}")
        print(f"-> Volatility    : {decision.volatility.value}")
        print(f"-> Time Sensitive: {decision.is_time_sensitive}")
        print(f"-> Reasoning     : {decision.reasoning}")
        if decision.search_queries:
            print(f"-> Search Queries: {decision.search_queries}")

        if decision.primary_route == expected:
            print(f"RESULT: PASS [Expected: {expected.value}]")
            passed += 1
        else:
            print(f"RESULT: FAIL [Expected: {expected.value}, Got: {decision.primary_route.value}]")
            failed += 1

    print("\n" + "=" * 70)
    print(f"BENCHMARK COMPLETED: {passed}/{len(test_cases)} PASSED ({passed/len(test_cases)*100:.1f}%)")
    print(f"Routing decisions logged to: {router.dataset_path}")
    print("=" * 70)

    assert passed >= 7, f"Expected at least 7/8 passing tests, got {passed}"


if __name__ == "__main__":
    test_iqr_suite()

