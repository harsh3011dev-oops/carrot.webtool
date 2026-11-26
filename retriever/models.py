"""
PROJECT NOVA - Web Retrieval Data Models
Data structures for search results, extracted web documents, and source citations.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Raw result item returned from the search engine."""
    source_index: int = Field(default=1, description="1-based numerical index, e.g. 1 for [1]")
    title: str = Field(description="Title of the web page")
    url: str = Field(description="Canonical URL of the web page")
    snippet: str = Field(description="Brief snippet or summary from the search engine")
    source: str = Field(default="ddg", description="Provider source identifier (e.g. ddg, google_news_rss)")
    published_at: Optional[str] = Field(default=None, description="Optional publication date string")


class ExtractedDocument(BaseModel):
    """
    Clean, parsed content of a fetched web page, stripped of HTML boilerplate and ads.
    """
    source_index: int = Field(description="1-based numerical index corresponding to [1], [2], etc.")
    title: str = Field(description="Title of the article/page")
    url: str = Field(description="Source URL")
    clean_text: str = Field(description="Boilerplate-free readable text content")
    published_date: Optional[str] = Field(default=None, description="Extracted publication or update date")
    author: Optional[str] = Field(default=None, description="Author or publisher name")
    word_count: int = Field(default=0, description="Total word count of extracted text")
    is_success: bool = Field(default=True, description="Whether retrieval and extraction succeeded")
    error_message: Optional[str] = Field(default=None, description="Error reason if extraction failed")


class EvidenceChunk(BaseModel):
    """
    Atomic paragraph-aware evidence chunk extracted from a document.
    Enables deep factual retrieval beyond arbitrary document head truncation.
    """
    chunk_id: str = Field(description="Unique chunk identifier e.g. 'doc1_chunk2'")
    source_index: int = Field(description="1-based index corresponding to [1], [2]")
    title: str = Field(description="Document title")
    url: str = Field(description="Source URL")
    text: str = Field(description="Extracted chunk text content")
    start_char: int = Field(default=0, description="Start character offset in full text")
    end_char: int = Field(default=0, description="End character offset in full text")
    relevance_score: float = Field(default=0.0, description="Composite ranking score for this chunk")
    published_date: Optional[str] = None
    author: Optional[str] = None
    heading: Optional[str] = None
    contains_table: bool = Field(default=False, description="Whether chunk contains structured table markdown")

