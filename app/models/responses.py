"""Response models for the YFinance API.

This module contains response model definitions that wrap
data models for API responses.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

from app.models.common import Metadata, Pagination

# Define model imports but replace with Any for now
T = TypeVar('T')

class ErrorResponse(BaseModel):
    """Model for error responses."""

    error: Dict[str, Any] = Field(..., description="Error details")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Error timestamp"
    )

    model_config = {
        "arbitrary_types_allowed": True
    }


class DataResponse(BaseModel, Generic[T]):
    """Generic model for data responses."""

    data: T = Field(..., description="Response data")
    metadata: Optional[Metadata] = Field(None, description="Response metadata")

    model_config = {
        "arbitrary_types_allowed": True
    }


class ListResponse(BaseModel, Generic[T]):
    """Generic model for list responses."""

    items: List[T] = Field(..., description="List of items")
    count: int = Field(..., description="Number of items")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="Response timestamp"
    )

    model_config = {
        "arbitrary_types_allowed": True
    }


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic model for paginated responses."""

    items: List[T] = Field(..., description="List of items")
    pagination: Pagination = Field(..., description="Pagination information")
    metadata: Optional[Metadata] = Field(None, description="Response metadata")

    model_config = {
        "arbitrary_types_allowed": True
    }


# Simplified response type definitions to avoid circular imports
TickerActionResponse = Dict[str, Any]
TickerAnalystPriceTargetsResponse = Dict[str, Any]
TickerHistoryResponse = Dict[str, Any]
TickerBalanceSheetResponse = Dict[str, Any]
TickerCashFlowResponse = Dict[str, Any]
TickerIncomeStatementResponse = Dict[str, Any]
TickerEarningsResponse = Dict[str, Any]
TickerHoldersResponse = Dict[str, Any]
TickerInsiderTransactionsResponse = Dict[str, Any]
TickerRecommendationsResponse = Dict[str, Any]
TickerNewsResponse = Dict[str, Any]
TickerOptionChainsResponse = Dict[str, Any]
TickerInfoResponse = Dict[str, Any]
TickerBasicInfoResponse = Dict[str, Any]
TickerEarningsEstimateResponse = Dict[str, Any]
TickerRevenueEstimateResponse = Dict[str, Any]
TickerSustainabilityResponse = Dict[str, Any]
MarketStatusResponse = Dict[str, Any]
MarketSummaryResponse = Dict[str, Any]
SearchResultsResponse = Dict[str, Any]
SectorInfoResponse = Dict[str, Any]
SectorOverviewResponse = Dict[str, Any]
SectorDetailsResponse = Dict[str, Any]
SectorIndustriesResponse = Dict[str, Any]
SectorCompaniesResponse = Dict[str, Any]
SectorETFsResponse = Dict[str, Any]
SectorFundsResponse = Dict[str, Any]
SectorResearchReportsResponse = Dict[str, Any]
IndustryInfoResponse = Dict[str, Any]
IndustryOverviewResponse = Dict[str, Any]
IndustryDetailsResponse = Dict[str, Any]
IndustryCompaniesResponse = Dict[str, Any]
IndustryGrowthCompaniesResponse = Dict[str, Any]
IndustryPerformingCompaniesResponse = Dict[str, Any]
IndustryComparisonResponse = Dict[str, Any]