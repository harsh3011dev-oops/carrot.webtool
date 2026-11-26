"""
PROJECT NOVA - Sprint 2 Quality Gatekeeper Test Suite
=====================================================
Tests and verifies all Sprint 2 acceptance criteria:
1. Strict Entity & Variant Matching (iPhone 16 vs 16e, Senior vs Youth/Blind)
2. Decoupled Relevance vs Sufficiency (50 distinct test cases)
3. Event Date vs Publication Date Semantic Attribution
4. Source Quality & Authority Ranking
"""

import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from retriever.entity_matcher import extract_entity_profile, match_entity, EntityProfile
from retriever.models import ExtractedDocument
from retriever.relevance import (
    evaluate_relevance,
    evaluate_sufficiency,
    extract_attributed_event_date,
    filter_and_rank_documents,
    is_evidence_relevant,
    is_evidence_sufficient,
    score_document,
)


def run_sprint_2_tests():
    print("=" * 70)
    print("       PROJECT NOVA - SPRINT 2 QUALITY GATEKEEPER SUITE")
    print("=" * 70)

    total_tests = 0
    passed_tests = 0

    # =========================================================================
    # PART 1: Strict Entity & Variant Matching (Item 18 & 4)
    # =========================================================================
    print("\n[PART 1] Testing Strict Entity & Variant Matching...")

    variant_tests = [
        # (Query, Candidate Title, Expected Match, Expected Variant Conflict)
        ("What was the official launch date of the iPhone 16?", "iPhone 16e launch as it happened - Apple's next-gen", False, True),
        ("What was the official launch date of the iPhone 16?", "iPhone 16 - Wikipedia", True, False),
        ("What was the official launch date of the iPhone 16?", "Apple iPhone 16 official specifications and launch date", True, False),
        ("Which team won last Asia Cup in cricket?", "Controversy in blind Asia Cup 2026 final: India boycott", False, True),
        ("Which team won last Asia Cup in cricket?", "India vs Pakistan Shaheens ACC Men's Asia Cup Rising Stars", False, True),
        ("Which team won last Asia Cup in cricket?", "Asia Cup - Wikipedia", True, False),
        ("Release date of Samsung Galaxy S24", "Samsung Galaxy S24 Ultra review and release date", False, True),
        ("Release date of Samsung Galaxy S24", "Samsung Galaxy S24 released worldwide", True, False),
        ("Who won the 2023 ICC Men's Cricket World Cup?", "2023 Cricket World Cup final - Wikipedia", True, False),
        ("Who won the 2023 ICC Men's Cricket World Cup?", "2024 ICC Men's T20 World Cup - Wikipedia", False, True),
    ]

    for query, title, exp_match, exp_conflict in variant_tests:
        total_tests += 1
        q_prof = extract_entity_profile(query)
        res = match_entity(q_prof, title)
        if res.is_match == exp_match and res.has_variant_conflict == exp_conflict:
            passed_tests += 1
        else:
            print(f"  ❌ Variant Match Failed: Query='{query}' vs Title='{title}' -> (Got match={res.is_match}, conflict={res.has_variant_conflict})")

    print(f"  ✓ {passed_tests}/{total_tests} Strict entity & variant conflict tests passed!")

    # =========================================================================
    # PART 2: Decoupled Relevance vs Sufficiency (50 Distinct Cases - Item 28/29)
    # =========================================================================
    print("\n[PART 2] Testing Decoupled Relevance vs Sufficiency (50 Cases)...")

    # Sample test fixtures generator
    decoupled_cases = []
    
    # 10 Tech Cases: High relevance, High Sufficiency (Function/Definition asked and present)
    for i in range(1, 11):
        decoupled_cases.append({
            "query": f"What is the primary function of CPU component {i}?",
            "doc": ExtractedDocument(
                source_index=1,
                title=f"Central Processing Unit Component {i} Overview",
                url=f"https://en.wikipedia.org/wiki/CPU_{i}",
                clean_text=f"The primary function of the CPU is to execute instructions and manage data flow for task {i}.",
                word_count=80
            ),
            "exp_relevant": True,
            "exp_sufficient": True,
        })

    # 10 Tech Cases: High relevance, INSUFFICIENT (Clock speed asked, but only instructions discussed)
    for i in range(1, 11):
        decoupled_cases.append({
            "query": f"What is the exact maximum clock speed in GHz of CPU {i}?",
            "doc": ExtractedDocument(
                source_index=1,
                title=f"CPU Architecture and Processing Overview {i}",
                url=f"https://en.wikipedia.org/wiki/Processor_{i}",
                clean_text="The CPU executes computer program instructions, including arithmetic and logic operations.",
                word_count=70
            ),
            "exp_relevant": True,
            "exp_sufficient": False,  # Clock speed missing!
        })

    # 10 Sports Cases: High relevance, High sufficiency (Winner asked, winner present)
    for i in range(1, 11):
        decoupled_cases.append({
            "query": f"Who won the {2020 + i} tournament final?",
            "doc": ExtractedDocument(
                source_index=1,
                title=f"{2020 + i} Tournament Final Results",
                url=f"https://en.wikipedia.org/wiki/Final_{i}",
                clean_text=f"Team Australia won the tournament final, defeating India by 6 wickets to lift the trophy.",
                word_count=85
            ),
            "exp_relevant": True,
            "exp_sufficient": True,
        })

    # 10 Sports Cases: High relevance, INSUFFICIENT (Final score asked, but only dates discussed)
    for i in range(1, 11):
        decoupled_cases.append({
            "query": f"What was the final score of the {2020 + i} final match?",
            "doc": ExtractedDocument(
                source_index=1,
                title=f"{2020 + i} Final Schedule and Venue Announcement",
                url=f"https://www.uefa.com/news_{i}",
                clean_text=f"The final match will be hosted at Wembley Stadium in London with tickets available.",
                word_count=60
            ),
            "exp_relevant": True,
            "exp_sufficient": False,  # Score missing!
        })

    # 10 Irrelevant Cases (Topic mismatch e.g. Chandrayaan vs Tariffs)
    for i in range(1, 11):
        decoupled_cases.append({
            "query": f"Find official announcement of Chandrayaan-{i} lunar landing date",
            "doc": ExtractedDocument(
                source_index=1,
                title=f"US Prepares Fresh Tariff Hikes on China and Global Markets #{i}",
                url=f"https://www.livemint.com/economy/tariffs_{i}",
                clean_text="The finance ministry discussed global tariffs and trade deficit updates today.",
                word_count=80
            ),
            "exp_relevant": False,
            "exp_sufficient": False,
        })

    decoupled_passed = 0
    for idx, c in enumerate(decoupled_cases, start=1):
        total_tests += 1
        rel_score = evaluate_relevance(c["query"], c["doc"])
        is_rel = rel_score >= 40.0
        is_suff, suff_score, _ = evaluate_sufficiency(c["query"], c["doc"])

        if is_rel == c["exp_relevant"] and is_suff == c["exp_sufficient"]:
            decoupled_passed += 1
            passed_tests += 1
        else:
            print(f"  ❌ Decoupled case {idx} failed: Query='{c['query'][:35]}' -> Expected (Rel={c['exp_relevant']}, Suff={c['exp_sufficient']}), Got (Rel={is_rel}, Suff={is_suff})")

    print(f"  ✓ {decoupled_passed}/50 Decoupled Relevance & Sufficiency test cases passed!")

    # =========================================================================
    # PART 3: Semantic Event Date vs Article Publication Date (Item 37)
    # =========================================================================
    print("\n[PART 3] Testing Semantic Date Attribution (Event Date vs PubDate)...")

    # Document published in 2026, but discussing iPhone XR launched in 2018
    xr_doc = ExtractedDocument(
        source_index=1,
        title="Every iPhone Generation: A Full History of Release Dates",
        url="https://tech.yahoo.com/phones/articles/every-iphone-generation-230200542.html",
        published_date="2026-03-03",
        clean_text=(
            "The iPhone XS and iPhone XS Max went on sale in September 2018. "
            "A month later, the iPhone XR was released on October 26, 2018 at a starting price of $749."
        ),
        word_count=50
    )

    total_tests += 1
    xr_profile = extract_entity_profile("tell me launch date of iphone xr")
    extracted_event_date = extract_attributed_event_date(xr_profile, xr_doc)

    if extracted_event_date and "october 26, 2018" in extracted_event_date.lower():
        passed_tests += 1
        print(f"  ✓ Accurately extracted Event Date '{extracted_event_date}' instead of article PubDate '{xr_doc.published_date}'!")
    else:
        print(f"  ❌ Date attribution failed! Extracted: {extracted_event_date}")

    # Chandrayaan-3 landing date attribution
    ch3_doc = ExtractedDocument(
        source_index=2,
        title="India's Chandrayaan-3 successfully lands on the Moon",
        url="https://www.esa.int/articles/chandrayaan-3",
        published_date="2023-08-01",
        clean_text="India's Chandrayaan-3 successfully landed on the Moon on 23 August 2023 near the lunar south pole.",
        word_count=40
    )
    total_tests += 1
    ch3_profile = extract_entity_profile("On what date did Chandrayaan-3 land on the Moon?")
    ch3_event_date = extract_attributed_event_date(ch3_profile, ch3_doc)
    if ch3_event_date and "23 august 2023" in ch3_event_date.lower():
        passed_tests += 1
        print(f"  ✓ Accurately extracted Landing Date '{ch3_event_date}' instead of article PubDate '{ch3_doc.published_date}'!")
    else:
        print(f"  ❌ Date attribution failed! Extracted: {ch3_event_date}")

    # =========================================================================
    # PART 4: Multi-Dimensional Source Authority Ranking (Task 4)
    # =========================================================================
    print("\n[PART 4] Testing Source Authority & Multi-Dimensional Ranking...")

    doc_wiki = ExtractedDocument(
        source_index=1,
        title="iPhone 16 - Wikipedia",
        url="https://en.wikipedia.org/wiki/IPhone_16",
        clean_text="The iPhone 16 and iPhone 16 Plus were announced on September 9, 2024 and officially released on September 20, 2024.",
        word_count=150
    )
    doc_aggregator = ExtractedDocument(
        source_index=2,
        title="iPhone 16e launch as it happened - Apple budget phone",
        url="https://tech.yahoo.com/articles/iphone-16e-live-updates",
        clean_text="Apple officially launched the new iPhone 16e budget model on February 19, 2025.",
        word_count=150
    )

    query = "What was the official launch date of the iPhone 16?"
    ranked = filter_and_rank_documents(query, [doc_aggregator, doc_wiki], max_return=2)

    total_tests += 1
    # Wikipedia must rank #1 and iPhone 16e variant must be filtered or ranked lower
    if ranked and ranked[0].url == doc_wiki.url:
        passed_tests += 1
        print(f"  ✓ Authoritative exact-match source ranked #1: {ranked[0].title} ({ranked[0].url})")
    else:
        print(f"  ❌ Ranking failed! Ranked #1 was: {ranked[0].title if ranked else 'None'}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    success_rate = (passed_tests / total_tests) * 100
    print(f" SPRINT 2 REGRESSION RESULTS: {passed_tests}/{total_tests} PASSED ({success_rate:.1f}%)")
    print("=" * 70)

    if passed_tests == total_tests:
        print("🎉 ALL SPRINT 2 ACCEPTANCE CRITERIA SATISFIED SUCCESSFULLY!")
        return 0
    else:
        print(f"⚠️ {total_tests - passed_tests} tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(run_sprint_2_tests())

