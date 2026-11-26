"""
PROJECT NOVA - Search Provider Abstraction & Fallback Engine (Sprint 4)
=======================================================================
Implements provider contracts and multi-provider resilience:
1. SearchProvider (Abstract Base Class)
2. DuckDuckGoSearchProvider (Primary live search)
3. GoogleNewsRSSSearchProvider (Resilient zero-key fallback provider)
4. MultiProviderSearchManager (Fallback orchestration, deduplication, fault tolerance)
"""

import html
import json
import logging
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import List, Optional, Set
from urllib.parse import urlparse, urlunparse

from config import settings
from retriever.models import SearchResult

logger = logging.getLogger("nova.search.providers")


def clean_url(url: str) -> str:
    """Strips tracking queries (utm_*, fbclid, etc.) from candidate URLs."""
    try:
        parsed = urlparse(url)
        clean_query = re.sub(r"utm_[^&]+&?", "", parsed.query)
        clean_query = re.sub(r"fbclid=[^&]+&?", "", clean_query).rstrip("&?")
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, clean_query, ""))
    except Exception:
        return url


def is_junk_url(url: str) -> bool:
    """Filters out known spam registries, ad redirects, and translation loops."""
    junk_indicators = [
        "translate.google",
        "zaubacorp.com",
        "thecompanycheck.com",
        "sasasas.co.uk",
        "google.com/maps",
        "login",
    ]
    lower = url.lower()
    return any(j in lower for j in junk_indicators)


class SearchProvider(ABC):
    """Abstract contract for search providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name identifier of the provider."""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """Executes search and returns standardized SearchResult items."""
        pass


class DuckDuckGoSearchProvider(SearchProvider):
    """Primary zero-key DuckDuckGo web search provider."""

    @property
    def provider_name(self) -> str:
        return "duckduckgo"

    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            results: List[SearchResult] = []
            with DDGS() as ddgs:
                # 1. Text search
                raw_text = []
                try:
                    raw_text = list(ddgs.text(query, max_results=limit))
                except Exception as e:
                    logger.warning(f"DDG text query error: {e}")

                for item in raw_text:
                    raw_url = item.get("href") or item.get("link") or ""
                    if raw_url.startswith("/"):
                        raw_url = "https://duckduckgo.com" + raw_url
                    norm_url = clean_url(raw_url)
                    title = item.get("title", "Web Result")
                    snippet = item.get("body") or item.get("snippet") or ""

                    if norm_url and not is_junk_url(norm_url):
                        if not any(r.url == norm_url for r in results):
                            results.append(
                                SearchResult(
                                    source_index=len(results) + 1,
                                    title=title,
                                    url=norm_url,
                                    snippet=snippet,
                                    source=self.provider_name,
                                )
                            )
                    if len(results) >= limit:
                        break

                # 2. News search if text was sparse
                if len(results) < limit:
                    raw_news = []
                    try:
                        raw_news = list(ddgs.news(query, max_results=limit))
                    except Exception:
                        pass

                    for item in raw_news:
                        raw_url = item.get("url") or item.get("href") or ""
                        norm_url = clean_url(raw_url)
                        title = item.get("title", "")
                        snippet = item.get("body") or item.get("snippet") or ""
                        if norm_url and not is_junk_url(norm_url):
                            if not any(r.url == norm_url for r in results):
                                results.append(
                                    SearchResult(
                                        source_index=len(results) + 1,
                                        title=title,
                                        url=norm_url,
                                        snippet=snippet,
                                        source=self.provider_name,
                                    )
                                )
                        if len(results) >= limit:
                            break

            return results

        except Exception as e:
            logger.error(f"DuckDuckGo provider failed: {e}")
            raise


class GoogleNewsRSSSearchProvider(SearchProvider):
    """
    Fallback search provider using Google News RSS feeds.
    100% free, zero external keys, high uptime, native XML parsing.
    """

    @property
    def provider_name(self) -> str:
        return "google_news_rss"

    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        encoded_query = urllib.parse.quote_plus(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        req = urllib.request.Request(rss_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                xml_data = resp.read()

            root = ET.fromstring(xml_data)
            items = root.findall(".//item")
            results: List[SearchResult] = []

            for item in items[:limit]:
                title_elem = item.find("title")
                link_elem = item.find("link")
                desc_elem = item.find("description")
                pub_date_elem = item.find("pubDate")

                title = title_elem.text if title_elem is not None and title_elem.text else "News Article"
                link = link_elem.text if link_elem is not None and link_elem.text else ""
                raw_desc = desc_elem.text if desc_elem is not None and desc_elem.text else ""
                pub_date = pub_date_elem.text if pub_date_elem is not None else None

                # Clean HTML tags and entities from RSS description snippet
                clean_snippet = re.sub(r"<[^>]+>", " ", raw_desc)
                clean_snippet = html.unescape(clean_snippet)
                clean_snippet = re.sub(r"\s+", " ", clean_snippet).strip()

                norm_url = clean_url(link)
                if norm_url and not is_junk_url(norm_url):
                    if not any(r.url == norm_url for r in results):
                        results.append(
                            SearchResult(
                                source_index=len(results) + 1,
                                title=html.unescape(title),
                                url=norm_url,
                                snippet=clean_snippet,
                                source=self.provider_name,
                                published_at=pub_date,
                            )
                        )

            return results

        except Exception as e:
            logger.error(f"GoogleNewsRSS provider failed: {e}")
            return []


class WikipediaSearchProvider(SearchProvider):
    """
    Encyclopedic fallback search provider using Wikipedia OpenSearch API.
    100% free, zero external keys, authoritative for historical, scientific, and encyclopedic facts.
    """

    @property
    def provider_name(self) -> str:
        return "wikipedia"

    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        clean_q = re.sub(r"[^\w\s\-\.]", "", query).strip()
        encoded = urllib.parse.quote_plus(clean_q)
        api_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={encoded}&limit={limit}&namespace=0&format=json"

        headers = {
            "User-Agent": "ProjectNOVA/1.0 (Educational RAG Assistant; linux-dgx-spark)"
        }
        req = urllib.request.Request(api_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            if len(data) >= 4:
                titles = data[1]
                snippets = data[2]
                urls = data[3]
                results: List[SearchResult] = []
                for idx in range(min(len(titles), limit)):
                    norm_url = clean_url(urls[idx])
                    if norm_url and not is_junk_url(norm_url):
                        results.append(
                            SearchResult(
                                source_index=len(results) + 1,
                                title=titles[idx],
                                url=norm_url,
                                snippet=snippets[idx] if idx < len(snippets) else "",
                                source=self.provider_name,
                                published_at=None,
                            )
                        )
                return results
            return []
        except Exception as e:
            logger.error(f"WikipediaSearchProvider failed: {e}")
            return []


class MultiProviderSearchManager:
    """
    Coordinates primary search with automatic graceful fallback.
    Prevents single point of failure (e.g. DDG rate limit or block).
    Cascades: DuckDuckGo -> GoogleNewsRSS -> Wikipedia
    """

    def __init__(
        self,
        primary_provider: Optional[SearchProvider] = None,
        fallback_providers: Optional[List[SearchProvider]] = None,
    ):
        self.primary = primary_provider or DuckDuckGoSearchProvider()
        self.fallbacks = fallback_providers or [
            GoogleNewsRSSSearchProvider(),
            WikipediaSearchProvider(),
        ]

    def search(self, query: str, limit: int = 5) -> List[SearchResult]:
        """
        Attempts primary provider first. If it raises an exception or returns
        zero results, cascades to fallback providers.
        """
        # 1. Try Primary Provider
        try:
            primary_results = self.primary.search(query, limit=limit)
            if primary_results:
                return primary_results
            logger.info(f"Primary provider '{self.primary.provider_name}' returned 0 results. Triggering fallback.")
        except Exception as e:
            logger.warning(f"Primary provider '{self.primary.provider_name}' error: {e}. Triggering fallback.")

        # 2. Try Fallback Providers
        for fb in self.fallbacks:
            try:
                fb_results = fb.search(query, limit=limit)
                if fb_results:
                    logger.info(f"Fallback provider '{fb.provider_name}' successfully retrieved {len(fb_results)} results.")
                    return fb_results
            except Exception as e:
                logger.warning(f"Fallback provider '{fb.provider_name}' error: {e}")

        return []

    def multi_search(self, queries: List[str], max_total_results: int = 5) -> List[SearchResult]:
        """
        Searches across multiple queries with URL deduplication, domain authority ranking,
        and contiguous indexing.
        """
        seen_urls: Set[str] = set()
        candidates: List[SearchResult] = []

        per_query_limit = max(2, (max_total_results // max(len(queries), 1)) + 1)
        for q in queries:
            results = self.search(q, limit=per_query_limit)
            for r in results:
                if r.url not in seen_urls:
                    seen_urls.add(r.url)
                    candidates.append(r)

        # Domain authority weighting
        authoritative_keys = [
            "wikipedia.org", "espncricinfo.com", "cricinfo.com", "bbc.com",
            "reuters.com", "thehindu.com", "indianexpress.com", "ndtv.com", "apple.com"
        ]

        def rank_key(res: SearchResult) -> int:
            url_lower = res.url.lower()
            for rank, key in enumerate(authoritative_keys):
                if key in url_lower:
                    return rank
            return 99

        candidates.sort(key=rank_key)
        selected = candidates[:max_total_results]

        # Re-index 1-based
        for i, item in enumerate(selected, start=1):
            item.source_index = i

        return selected

