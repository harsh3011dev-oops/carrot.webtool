"""
PROJECT NOVA - High-Fidelity Web Content Extractor
==================================================
Extracts clean, readable Markdown/text from web pages using Trafilatura.
Features:
- Strips ads, navigation bars, cookie banners, footer links, and CSS boilerplate
- Concurrent multi-threaded page extraction for ultra-low latency (~1s for 4 URLs)
- Automatic BeautifulSoup fallback if Trafilatura returns empty text
- Search snippet fallback if website blocks scraping or times out
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from bs4 import BeautifulSoup
import trafilatura
from trafilatura.settings import use_config

from config import settings
from retriever.models import ExtractedDocument, SearchResult

logger = logging.getLogger("nova.extractor")

# Configure Trafilatura timeouts
traf_config = use_config()
traf_config.set("DEFAULT", "DOWNLOAD_TIMEOUT", str(settings.SEARCH_TIMEOUT_SECONDS))


class WebContentExtractor:
    """
    Fetches and cleans web pages into high-density, noise-free text.
    Preserves full article text for paragraph-aware semantic chunking.
    """

    def __init__(self, max_chars_per_page: int = 25000):
        self.max_chars_per_page = max_chars_per_page

    def extract_single(self, search_item: SearchResult) -> ExtractedDocument:
        """
        Fetches and cleans a single URL.
        Falls back to search snippet if the web page is paywalled or unreachable.
        """
        url = search_item.url
        logger.info(f"Extracting content from [{search_item.source_index}]: {url}")

        try:
            # 0. If DuckDuckGo redirect URL, resolve to final real destination URL
            if "duckduckgo.com/go/v1" in url:
                try:
                    import requests
                    head_res = requests.get(url, allow_redirects=True, timeout=4, headers={"User-Agent": settings.USER_AGENT})
                    if head_res and head_res.url:
                        url = head_res.url
                except Exception:
                    pass

            # 1. Fetch raw HTML using Trafilatura with custom user-agent
            downloaded = trafilatura.fetch_url(url, config=traf_config)
            clean_text = None

            # 1B. Fallback: Jina Reader if direct Trafilatura is blocked by Cloudflare/WAF
            if not downloaded:
                try:
                    import requests
                    jina_res = requests.get(
                        f"https://r.jina.ai/{url}",
                        headers={"User-Agent": settings.USER_AGENT},
                        timeout=settings.SEARCH_TIMEOUT_SECONDS,
                    )
                    if jina_res.status_code == 200 and len(jina_res.text.strip()) > 100:
                        clean_text = jina_res.text.strip()
                except Exception:
                    pass

            if not downloaded and not clean_text:
                logger.warning(f"Failed to download URL: {url}. Using search snippet fallback.")
                return ExtractedDocument(
                    source_index=search_item.source_index,
                    title=search_item.title,
                    url=url,
                    clean_text=search_item.snippet,
                    word_count=len(search_item.snippet.split()),
                    is_success=False,
                    error_message="Page could not be fetched (timeout or blocked). Search snippet retained.",
                )

            # 2. Extract clean article text & remove boilerplate if not already rescued by Jina
            if not clean_text and downloaded:
                clean_text = trafilatura.extract(
                    downloaded,
                    include_links=False,
                    include_images=False,
                    include_tables=True,
                    output_format="txt",
                    config=traf_config,
                )

            # 3. Fallback to BeautifulSoup if Trafilatura returned nothing
            if not clean_text or len(clean_text.strip()) < 50:
                logger.debug(f"Trafilatura returned sparse text for {url}. Attempting BeautifulSoup fallback.")
                soup = BeautifulSoup(downloaded, "html.parser")
                # Remove script, style, header, footer, nav tags
                for element in soup(["script", "style", "nav", "footer", "header", "noscript"]):
                    element.decompose()
                clean_text = " ".join(soup.stripped_strings)

            # 4. If still empty, fall back to the search snippet
            if not clean_text or len(clean_text.strip()) < 30:
                clean_text = search_item.snippet

            # 5. Extract metadata (Date, Author) if available
            metadata = trafilatura.extract_metadata(downloaded)
            pub_date = metadata.date if metadata else None
            author = metadata.author if metadata else None

            # 6. Truncate long pages to avoid filling the context window with fluff
            if len(clean_text) > self.max_chars_per_page:
                clean_text = clean_text[:self.max_chars_per_page].rsplit(" ", 1)[0] + " ... [Truncated]"

            words = len(clean_text.split())

            return ExtractedDocument(
                source_index=search_item.source_index,
                title=search_item.title,
                url=url,
                clean_text=clean_text.strip(),
                published_date=pub_date,
                author=author,
                word_count=words,
                is_success=True,
            )

        except Exception as e:
            logger.error(f"Error extracting from {url}: {e}")
            # Fall back to search snippet so we never lose evidence completely
            return ExtractedDocument(
                source_index=search_item.source_index,
                title=search_item.title,
                url=url,
                clean_text=search_item.snippet,
                word_count=len(search_item.snippet.split()),
                is_success=False,
                error_message=f"Extraction error: {str(e)}",
            )

    def extract_batch(self, search_results: List[SearchResult]) -> List[ExtractedDocument]:
        """
        Extracts content from multiple search results in parallel using ThreadPoolExecutor.
        Maintains the original 1-based source indexing order.
        """
        if not search_results:
            return []

        logger.info(f"Extracting {len(search_results)} web pages in parallel...")
        docs: List[ExtractedDocument] = []

        # Execute extractions concurrently (1-2 seconds total for all pages)
        with ThreadPoolExecutor(max_workers=min(len(search_results), 5)) as executor:
            future_to_item = {
                executor.submit(self.extract_single, item): item.source_index
                for item in search_results
            }
            for future in as_completed(future_to_item):
                try:
                    doc = future.result()
                    docs.append(doc)
                except Exception as e:
                    logger.error(f"Thread execution error during extraction: {e}")

        # Sort back to original source_index order: [1], [2], [3]...
        docs.sort(key=lambda d: d.source_index)
        return docs

