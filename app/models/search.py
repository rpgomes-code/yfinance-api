"""Models for search-related endpoints.

This module contains model definitions for search data structures
used in the search endpoints of the API.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from app.models.enums import QuoteType


class SearchResultBase(BaseModel):
    """Base model for search results."""

    type: str = Field(..., description="Result type")
    score: Optional[float] = Field(None, description="Relevance score")


class QuoteSearchResult(SearchResultBase):
    """Model for quote search results."""

    type: str = Field("quote", const=True, description="Result type")
    symbol: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Company or instrument name")
    exchange: Optional[str] = Field(None, description="Exchange")
    quote_type: Optional[str] = Field(None, description="Quote type")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    market: Optional[str] = Field(None, description="Market")
    score: float = Field(..., description="Relevance score")


class NewsSearchResult(SearchResultBase):
    """Model for news search results."""

    type: str = Field("news", const=True, description="Result type")
    title: str = Field(..., description="News title")
    publisher: str = Field(..., description="News publisher")
    published_at: datetime = Field(..., description="Publish date and time")
    url: str = Field(..., description="News URL")
    summary: Optional[str] = Field(None, description="News summary")
    source: Optional[str] = Field(None, description="News source")
    score: float = Field(..., description="Relevance score")
    related_symbols: Optional[List[str]] = Field(None, description="Related ticker symbols")


class ListSearchResult(SearchResultBase):
    """Model for list search results."""

    type: str = Field("list", const=True, description="Result type")
    name: str = Field(..., description="List name")
    description: Optional[str] = Field(None, description="List description")
    symbols: List[str] = Field(..., description="Ticker symbols in the list")
    score: float = Field(..., description="Relevance score")


class ResearchReportSearchResult(SearchResultBase):
    """Model for research report search results."""

    type: str = Field("research", const=True, description="Result type")
    title: str = Field(..., description="Report title")
    publisher: str = Field(..., description="Report publisher")
    published_at: datetime = Field(..., description="Publish date and time")
    summary: Optional[str] = Field(None, description="Report summary")
    url: Optional[str] = Field(None, description="Report URL")
    score: float = Field(..., description="Relevance score")
    symbols: Optional[List[str]] = Field(None, description="Related ticker symbols")


class SearchResult(BaseModel):
    """Model for search results (union of all result types)."""

    __root__: Union[
        QuoteSearchResult,
        NewsSearchResult,
        ListSearchResult,
        ResearchReportSearchResult
    ] = Field(..., description="Search result")


class SearchQuery(BaseModel):
    """Model for search query parameters."""

    query: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Search query string"
    )
    limit: Optional[int] = Field(
        10,
        ge=1,
        le=100,
        description="Maximum number of results to return"
    )
    types: Optional[List[str]] = Field(
        None,
        description="Result types to include (quotes, news, lists, research)"
    )

    @validator('types', each_item=True)
    def validate_types(cls, v):
        """Validate search result types."""
        valid_types = {'quotes', 'news', 'lists', 'research'}
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid type: {v}. Valid types are: {', '.join(valid_types)}")
        return v.lower()


class SearchResponse(BaseModel):
    """Model for search response."""

    query: str = Field(..., description="Original search query")
    quotes: Optional[List[QuoteSearchResult]] = Field(None, description="Quote results")
    news: Optional[List[NewsSearchResult]] = Field(None, description="News results")
    lists: Optional[List[ListSearchResult]] = Field(None, description="List results")
    research: Optional[List[ResearchReportSearchResult]] = Field(None, description="Research report results")