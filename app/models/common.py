"""Common models used across different endpoint types.

This module contains model definitions for common data structures
used throughout the API, such as pagination, dates, and base models.
"""
from datetime import date, datetime
from typing import Any, Dict, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field, field_validator
from typing import Generic

from app.models.enums import (
    DataInterval,
    DataPeriod,
    ResponseFormat,
    SortOrder
)

# Generic type for data
T = TypeVar('T')


class DateRange(BaseModel):
    """Model for date range parameters."""

    start: Optional[Union[date, str]] = Field(
        None,
        description="Start date (ISO format or YYYY-MM-DD)"
    )
    end: Optional[Union[date, str]] = Field(
        None,
        description="End date (ISO format or YYYY-MM-DD)"
    )

    @classmethod
    @field_validator('start', 'end', mode='before')
    def validate_date(cls, v):
        """Validate and convert date strings."""
        if v is None:
            return None

        if isinstance(v, (date, datetime)):
            return v

        try:
            # Try to parse as ISO format
            return datetime.fromisoformat(v.replace('Z', '+00:00')).date()
        except (ValueError, AttributeError):
            try:
                # Try to parse as YYYY-MM-DD
                return datetime.strptime(v, '%Y-%m-%d').date()
            except (ValueError, AttributeError):
                raise ValueError(f"Invalid date format: {v}. Use ISO format or YYYY-MM-DD.")


class HistoryParams(DateRange):
    """Model for history data parameters."""

    period: Optional[DataPeriod] = Field(
        None,
        description="Time period to download"
    )
    interval: DataInterval = Field(
        DataInterval.ONE_DAY,
        description="Data interval"
    )
    prepost: bool = Field(
        False,
        description="Include pre and post market data"
    )
    actions: bool = Field(
        True,
        description="Include dividends and stock splits"
    )
    auto_adjust: bool = Field(
        True,
        description="Adjust all OHLC automatically"
    )

    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class PaginationParams(BaseModel):
    """Model for pagination parameters."""

    page: int = Field(
        1,
        ge=1,
        description="Page number (1-based)"
    )
    page_size: int = Field(
        100,
        ge=1,
        le=1000,
        description="Number of items per page"
    )


class SortParams(BaseModel):
    """Model for sorting parameters."""

    sort_by: Optional[str] = Field(
        None,
        description="Column to sort by"
    )
    sort_order: SortOrder = Field(
        SortOrder.ASC,
        description="Sort order"
    )

    class Config:
        """Pydantic configuration."""
        populate_by_name = True  # This allows both the field name and alias to work
        use_enum_values = True  # Keep any existing config options


class FilterParams(BaseModel):
    """Model for filtering parameters."""

    filters: Optional[Dict[str, Any]] = Field(
        None,
        description="Column filters as key-value pairs"
    )


class QueryParams(PaginationParams, SortParams, FilterParams):
    """Model combining pagination, sorting, and filtering parameters."""

    format: ResponseFormat = Field(
        ResponseFormat.DEFAULT,
        description="Response format"
    )

    class Config:
        """Pydantic configuration."""
        populate_by_name = True  # This allows both the field name and alias to work
        use_enum_values = True  # Keep any existing config options


class Pagination(BaseModel):
    """Model for pagination information in responses."""

    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")
    has_previous: bool = Field(..., description="Whether there is a previous page")
    has_next: bool = Field(..., description="Whether there is a next page")


class MetadataBase(BaseModel):
    """Base model for metadata in responses."""

    timestamp: datetime = Field(
        ...,
        description="Timestamp of the response"
    )


class Metadata(MetadataBase):
    """Model for metadata in responses."""

    count: Optional[int] = Field(
        None,
        description="Number of items in the response"
    )
    endpoint: Optional[str] = Field(
        None,
        description="API endpoint"
    )
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="Request parameters"
    )


class PaginatedMetadata(Metadata):
    """Model for metadata in paginated responses."""

    pagination: Pagination = Field(
        ...,
        description="Pagination information"
    )


class BaseResponse(BaseModel, Generic[T]):
    """Base model for API responses."""

    data: T = Field(..., description="Response data")
    metadata: Optional[Metadata] = Field(
        None,
        description="Response metadata"
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Model for paginated API responses."""

    items: List[T] = Field(..., description="List of items")
    pagination: Pagination = Field(..., description="Pagination information")