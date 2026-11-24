"""
PROJECT NOVA - Web Search & Content Extraction Test
Verifies DuckDuckGo live search + parallel Trafilatura article extraction.
"""

import sys
import time
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from retriever.extractor import WebContentExtractor
from retriever.web_search import WebSearchEngine


def test_web_retrieval_suite():
    print("=" * 70)
    print("   PROJECT NOVA - LIVE WEB SEARCH & EXTRACTION BENCHMARK")
    print("=" * 70)

    search_engine = WebSearchEngine(max_results=3)
    extractor = WebContentExtractor(max_chars_per_page=3000)

    test_query = "NASA Artemis mission latest updates"
    print(f"\n1. Executing live DuckDuckGo search for: '{test_query}'...")
    start_time = time.time()
    search_results = search_engine.search(test_query, max_results=3)
    search_latency = time.time() - start_time

    print(f"-> Search completed in: {search_latency:.2f} seconds")
    print(f"-> Retrieved {len(search_results)} search results:\n")

    assert len(search_results) > 0, "Search engine returned 0 results!"

    for res in search_results:
        print(f"  [{res.source_index}] Title  : {res.title}")
        print(f"      URL    : {res.url}")
        print(f"      Snippet: {res.snippet[:90]}...\n")

    print("2. Extracting and cleaning full web articles in parallel (Trafilatura)...")
    start_time = time.time()
    extracted_docs = extractor.extract_batch(search_results)
    extract_latency = time.time() - start_time

    print(f"-> Extraction completed in: {extract_latency:.2f} seconds")
    print(f"-> Extracted {len(extracted_docs)} documents:\n")

    assert len(extracted_docs) == len(search_results), "Mismatch in extracted documents count!"

    for doc in extracted_docs:
        print(f"  === SOURCE [{doc.source_index}]: {doc.title} ===")
        print(f"  URL        : {doc.url}")
        print(f"  Word Count : {doc.word_count} words")
        print(f"  Date/Author: {doc.published_date or 'N/A'} | {doc.author or 'N/A'}")
        print(f"  Clean Text Preview (first 200 chars):\n  \"{doc.clean_text[:200]}...\"\n")
        assert len(doc.clean_text) > 30, f"Clean text for source {doc.source_index} is too short!"

    print("=" * 70)
    print(">>> LIVE WEB SEARCH & PARALLEL EXTRACTION PASSED 100%! <<<")
    print(f"Total Pipeline Latency: {search_latency + extract_latency:.2f}s")
    print("=" * 70)


if __name__ == "__main__":
    test_web_retrieval_suite()

