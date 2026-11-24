"""
PROJECT NOVA - Web Retrieval Data Models
Data structures for search results, extracted web documents, and source citations.
"""

from typing import Optional
from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    """Raw result item returned from the search engine."""
    source_index: int = Field(description="1-based numerical index, e.g. 1 for [1]")
    title: str = Field(description="Title of the web page")
    url: str = Field(description="Canonical URL of the web page")
    snippet: str = Field(description="Brief snippet or summary from the search engine")


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

