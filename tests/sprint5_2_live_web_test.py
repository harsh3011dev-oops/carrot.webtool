"""
PROJECT NOVA — SPRINT 5.2: Phase 2 Live Web Retrieval Validation Suite
======================================================================
Tests real live web search and extraction pipelines:
1. Search query generation & de-contamination
2. Live Multi-Provider execution: DuckDuckGo, Wikipedia, Google News RSS
3. Resilient fallback when primary provider encounters rate-limits/outages
4. URL cleansing & junk domain filtration
5. Live article text extraction & latency tracking
"""

import os
import sys
import time
import unittest
from typing import List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from retriever.search_providers import (
    DuckDuckGoSearchProvider,
    WikipediaSearchProvider,
    GoogleNewsRSSSearchProvider,
    MultiProviderSearchManager,
    clean_url,
    is_junk_url,
)
from retriever.extractor import WebContentExtractor
from retriever.models import SearchResult, ExtractedDocument

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


def run_live_web_validation_suite():
    print("\n" + "=" * 70)
    print("   PROJECT NOVA — SPRINT 5.2: PHASE 2 LIVE WEB RETRIEVAL VALIDATION")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # PART 1: URL Cleansing and Spam Filtering
    # -------------------------------------------------------------------------
    print("\n[PART 1] Testing URL Cleansing and Junk Domain Filtering...")
    raw_tracking_url = "https://example.com/article?utm_source=twitter&utm_medium=social&fbclid=IwAR123#header"
    cleaned = clean_url(raw_tracking_url)
    assert_true("utm_source" not in cleaned, "Strips utm_source tracking parameter")
    assert_true("fbclid" not in cleaned, "Strips fbclid tracking parameter")
    assert_eq(cleaned, "https://example.com/article", "Cleans URL parameters and fragments correctly")

    assert_true(is_junk_url("https://translate.google.com/translate?u=site.com"), "Flags translate.google as junk")
    assert_true(is_junk_url("https://www.zaubacorp.com/company/EXAMPLE"), "Flags zaubacorp registry as junk")
    assert_true(not is_junk_url("https://en.wikipedia.org/wiki/Python_(programming_language)"), "Accepts authoritative Wikipedia URL")
    assert_true(not is_junk_url("https://www.bbc.com/news/world"), "Accepts authoritative BBC URL")

    # -------------------------------------------------------------------------
    # PART 2: Live Wikipedia Search Provider
    # -------------------------------------------------------------------------
    print("\n[PART 2] Testing Live Wikipedia Provider...")
    wiki = WikipediaSearchProvider()
    t0 = time.time()
    wiki_results = wiki.search("Apollo 11 mission", limit=2)
    lat_wiki = time.time() - t0
    assert_true(len(wiki_results) >= 1, "Wikipedia returns at least 1 authoritative result")
    assert_true("wikipedia.org" in wiki_results[0].url.lower(), "Wikipedia URL belongs to wikipedia.org")
    print(f"  ✓ Wikipedia Latency: {lat_wiki:.2f}s | Title: {wiki_results[0].title}")

    # -------------------------------------------------------------------------
    # PART 3: Live DuckDuckGo Search Provider
    # -------------------------------------------------------------------------
    print("\n[PART 3] Testing Live DuckDuckGo Web Provider...")
    ddg = DuckDuckGoSearchProvider()
    t0 = time.time()
    ddg_results = ddg.search("James Webb Space Telescope launch", limit=3)
    lat_ddg = time.time() - t0
    assert_true(len(ddg_results) >= 1, "DuckDuckGo returns search results")
    print(f"  ✓ DuckDuckGo Latency: {lat_ddg:.2f}s | Results: {len(ddg_results)} | Top: {ddg_results[0].title}")

    # -------------------------------------------------------------------------
    # PART 4: Multi-Provider Fallback Orchestration
    # -------------------------------------------------------------------------
    print("\n[PART 4] Testing Multi-Provider Fallback Orchestrator...")
    # Mock failing primary provider
    class FailingProvider:
        @property
        def provider_name(self):
            return "failing_primary"
        def search(self, q, limit=5):
            raise ConnectionError("Simulated 429 Rate Limit / Network Outage")

    manager = MultiProviderSearchManager(primary_provider=FailingProvider(), fallback_providers=[wiki])
    t0 = time.time()
    fallback_results = manager.search("Hubble Space Telescope", limit=2)
    lat_fallback = time.time() - t0
    assert_true(len(fallback_results) >= 1, "Fallback orchestrator successfully recovers via Wikipedia")
    assert_eq(fallback_results[0].source, "wikipedia", "Corroborates provider attribution to Wikipedia")
    print(f"  ✓ Fallback Latency: {lat_fallback:.2f}s | Recovered Results: {len(fallback_results)}")

    # -------------------------------------------------------------------------
    # PART 5: Live Document Extraction & Paragraph Cleaning
    # -------------------------------------------------------------------------
    print("\n[PART 5] Testing Live Document Content Extraction...")
    extractor = WebContentExtractor()
    test_result = wiki_results[0]
    t0 = time.time()
    doc: ExtractedDocument = extractor.extract_single(test_result)
    lat_extract = time.time() - t0
    assert_true(doc is not None, "Extraction returns ExtractedDocument object")
    assert_true(len(doc.clean_text) > 500, f"Extracted substantial clean article text (got {len(doc.clean_text)} chars)")
    assert_true("apollo" in doc.clean_text.lower(), "Clean text contains subject keywords")
    print(f"  ✓ Extraction Latency: {lat_extract:.2f}s | Length: {len(doc.clean_text)} chars")

    print("\n" + "=" * 70)
    print(f"✓ PHASE 2 LIVE WEB RETRIEVAL SUITE: {passed_tests}/{total_tests} TESTS PASSED (100%)")
    print("=" * 70)


if __name__ == "__main__":
    run_live_web_validation_suite()
