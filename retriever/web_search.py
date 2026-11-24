"""
PROJECT NOVA - Free Live Web Search Engine
==========================================
Uses DuckDuckGo Search (Zero API Keys, 100% Free).
Features:
- Multi-query search support (for decomposed sub-queries)
- URL deduplication & UTM tracking parameter stripping
- Robust fallback and error handling
"""

import logging
import re
from typing import List, Optional, Set
from urllib.parse import urlparse, urlunparse

from config import settings
from retriever.models import SearchResult

logger = logging.getLogger("nova.search")


class WebSearchEngine:
    """
    DuckDuckGo-backed live search client for Project NOVA.
    Requires zero API keys and zero billing.
    """

    def __init__(self, max_results: int = settings.MAX_SEARCH_RESULTS):
        self.max_results = max_results

    def _clean_url(self, url: str) -> str:
        """Removes tracking query parameters (like utm_*, fbclid, etc.) to normalize URLs."""
        try:
            parsed = urlparse(url)
            # Remove common marketing tracking parameters
            clean_query = re.sub(r"utm_[^&]+&?", "", parsed.query)
            clean_query = re.sub(r"fbclid=[^&]+&?", "", clean_query).rstrip("&?")
            return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, clean_query, ""))
        except Exception:
            return url

    def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """
        Executes an intelligent dual-channel search (News + General Web).
        Filters out junk/advertising redirects and returns high-relevance sources.
        """
        limit = max_results or self.max_results
        clean_query = query.strip()

        # Clean conversational stopwords for search engine
        search_term = re.sub(
            r"^(who\s+is\s+(the\s+)?(new\s+)?|what\s+is\s+(the\s+)?|tell\s+me\s+(about\s+)?(who\s+was\s+)?|can\s+you\s+tell\s+me\s+about\s+)",
            "",
            clean_query,
            flags=re.IGNORECASE
        )
        search_term = re.sub(r"[?!.,]+$", "", search_term).strip()
        if len(search_term) < 4:
            search_term = clean_query

        logger.info(f"Executing web search for: '{search_term}' (limit={limit})")
        results: List[SearchResult] = []

        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                # Channel 1: Try News Search first for fresh news, sports, prices, current events
                raw_news = []
                try:
                    raw_news = list(ddgs.news(search_term, max_results=limit))
                except Exception:
                    pass

                # If news found genuine articles, use them!
                if raw_news and len(raw_news) > 0:
                    for idx, item in enumerate(raw_news, start=1):
                        url = item.get("url") or item.get("href") or ""
                        title = item.get("title", "")
                        snippet = item.get("body") or item.get("snippet") or ""
                        if url and not self._is_junk_domain(url):
                            results.append(
                                SearchResult(
                                    source_index=idx,
                                    title=title,
                                    url=self._clean_url(url),
                                    snippet=snippet,
                                )
                            )

                # Channel 2: If news search has insufficient items, fall back to standard text search
                if len(results) < limit:
                    raw_text = []
                    try:
                        raw_text = list(ddgs.text(search_term, max_results=limit))
                    except Exception:
                        pass

                    for item in raw_text:
                        raw_url = item.get("href") or item.get("link") or ""
                        if raw_url.startswith("/"):
                            raw_url = "https://duckduckgo.com" + raw_url
                        normalized_url = self._clean_url(raw_url)
                        title = item.get("title", "Web Result")
                        snippet = item.get("body") or item.get("snippet") or ""

                        if normalized_url and not self._is_junk_domain(normalized_url):
                            if not any(r.url == normalized_url for r in results):
                                results.append(
                                    SearchResult(
                                        source_index=len(results) + 1,
                                        title=title,
                                        url=normalized_url,
                                        snippet=snippet,
                                    )
                                )
                        if len(results) >= limit:
                            break

        except Exception as e:
            logger.error(f"Search error for query '{search_term}': {e}")

        # Ensure contiguous 1-based indexing
        for i, res in enumerate(results, start=1):
            res.source_index = i

        logger.info(f"Retrieved {len(results)} verified search results.")
        return results

    def _is_junk_domain(self, url: str) -> bool:
        """Filters out ad-redirects, spam registries, and translator loops."""
        junk_indicators = [
            "translate.google",
            "zaubacorp.com",
            "thecompanycheck.com",
            "sasasas.co.uk",
            "google.com/maps",
            "login",
        ]
        lower_url = url.lower()
        return any(junk in lower_url for junk in junk_indicators)

        logger.info(f"Retrieved {len(results)} search results.")
        return results

    def multi_search(self, queries: List[str], max_total_results: Optional[int] = None) -> List[SearchResult]:
        """
        Executes multiple search queries (e.g. from sub-query decomposition),
        deduplicates by URL, and re-indexes them sequentially.
        """
        max_total = max_total_results or self.max_results
        seen_urls: Set[str] = set()
        aggregated: List[SearchResult] = []

        for q in queries:
            if len(aggregated) >= max_total:
                break
            query_results = self.search(q, max_results=max_total)
            for r in query_results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    aggregated.append(r)
                if len(aggregated) >= max_total:
                    break

        # Re-index so indices are contiguous: 1, 2, 3...
        final_results = []
        for i, item in enumerate(aggregated, start=1):
            item.source_index = i
            final_results.append(item)

        return final_results
