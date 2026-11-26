"""
PROJECT NOVA - Resilient Live Web Search Engine (Sprint 4 Upgrade)
==================================================================
Uses Multi-Provider Abstraction (DuckDuckGo + Google News RSS Fallback).
Features:
- Automatic graceful fallback if primary search engine fails or is rate-limited
- Multi-query search support (for decomposed sub-queries)
- URL deduplication & UTM tracking parameter stripping
- 100% Free, zero paid API keys
"""

import logging
from typing import List, Optional

from config import settings
from retriever.models import SearchResult
from retriever.search_providers import (
    DuckDuckGoSearchProvider,
    GoogleNewsRSSSearchProvider,
    MultiProviderSearchManager,
)

logger = logging.getLogger("nova.search")


class WebSearchEngine:
    """
    Resilient live search client for Project NOVA.
    Delegates to MultiProviderSearchManager with zero-key DuckDuckGo + Google News RSS fallback.
    """

    def __init__(self, max_results: int = settings.MAX_SEARCH_RESULTS):
        self.max_results = max_results
        self.manager = MultiProviderSearchManager(
            primary_provider=DuckDuckGoSearchProvider(),
            fallback_providers=[GoogleNewsRSSSearchProvider()]
        )

    def search(self, query: str, max_results: Optional[int] = None) -> List[SearchResult]:
        """Executes search with automatic fallback across providers."""
        limit = max_results or self.max_results
        return self.manager.search(query, limit=limit)

    def multi_search(self, queries: List[str], max_total_results: Optional[int] = None) -> List[SearchResult]:
        """Searches across multiple queries with URL deduplication and fallback."""
        max_total = max_total_results or self.max_results
        return self.manager.multi_search(queries, max_total_results=max_total)
