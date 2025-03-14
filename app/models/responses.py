"""Response models for the YFinance API.

This module contains response model definitions that wrap
data models for API responses.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

from app.models.common import Metadata, Pagination
from app.models.industry import (
    IndustryComparison,
    IndustryCompany,
    IndustryDetails,
    IndustryGrowthCompany,
    IndustryInfo,
    IndustryOverview,
    IndustryPerformingCompany
)
from app.models.market import MarketStatus, MarketSummary
from app.models.search import SearchResponse
from app.models.sector import (
    ResearchReport,
    SectorCompany,
    SectorDetails,
    SectorETF,
    SectorFund,
    SectorIndustry,
    SectorInfo,
    SectorOverview
)
from app.models.ticker import (
    AnalystPriceTarget,
    EarningsData,
    EarningsEstimate,
    FinancialStatement,
    HistoricalData,
    Holder,
    InsiderTransaction,
    NewsItem,
    OptionChain,
    Recommendation,
    RevenueEstimate,
    SustainabilityMetric,
    TickerAction,
    TickerBasicInfo,
    TickerInfo
)

# Generic type for list item
T = TypeVar('T')


class ErrorResponse(BaseModel):
    """Model for error responses."""

    error: Dict[str, Any] = Field(..., description="Error details")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
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
        default_factory=lambda: datetime.now(timezone.utc),
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


# Ticker response models
class TickerActionsResponse(ListResponse[TickerAction]):
    """Model for ticker actions response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerAnalystPriceTargetsResponse(ListResponse[AnalystPriceTarget]):
    """Model for ticker analyst price targets response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerHistoryResponse(ListResponse[HistoricalData]):
    """Model for ticker history response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerBalanceSheetResponse(ListResponse[FinancialStatement]):
    """Model for ticker balance sheet response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerCashFlowResponse(ListResponse[FinancialStatement]):
    """Model for ticker cash flow response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerIncomeStatementResponse(ListResponse[FinancialStatement]):
    """Model for ticker income statement response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerEarningsResponse(ListResponse[EarningsData]):
    """Model for ticker earnings response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerHoldersResponse(ListResponse[Holder]):
    """Model for ticker holders response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerInsiderTransactionsResponse(ListResponse[InsiderTransaction]):
    """Model for ticker insider transactions response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerRecommendationsResponse(ListResponse[Recommendation]):
    """Model for ticker recommendations response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerNewsResponse(ListResponse[NewsItem]):
    """Model for ticker news response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerOptionChainsResponse(ListResponse[OptionChain]):
    """Model for ticker option chains response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerInfoResponse(DataResponse[TickerInfo]):
    """Model for ticker info response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerBasicInfoResponse(DataResponse[TickerBasicInfo]):
    """Model for ticker basic info response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerEarningsEstimateResponse(DataResponse[EarningsEstimate]):
    """Model for ticker earnings estimate response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerRevenueEstimateResponse(DataResponse[RevenueEstimate]):
    """Model for ticker revenue estimate response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class TickerSustainabilityResponse(DataResponse[SustainabilityMetric]):
    """Model for ticker sustainability response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


# Market response models
class MarketStatusResponse(DataResponse[MarketStatus]):
    """Model for market status response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class MarketSummaryResponse(DataResponse[MarketSummary]):
    """Model for market summary response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


# Search response models
class SearchResultsResponse(DataResponse[SearchResponse]):
    """Model for search results response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


# Sector response models
class SectorInfoResponse(DataResponse[SectorInfo]):
    """Model for sector info response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class SectorOverviewResponse(DataResponse[SectorOverview]):
    """Model for sector overview response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class SectorDetailsResponse(DataResponse[SectorDetails]):
    """Model for sector details response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class SectorIndustriesResponse(ListResponse[SectorIndustry]):
    """Model for sector industries response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class SectorCompaniesResponse(ListResponse[SectorCompany]):
    """Model for sector companies response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class SectorETFsResponse(ListResponse[SectorETF]):
    """Model for sector ETFs response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class SectorFundsResponse(ListResponse[SectorFund]):
    """Model for sector funds response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class SectorResearchReportsResponse(ListResponse[ResearchReport]):
    """Model for sector research reports response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


# Industry response models
class IndustryInfoResponse(DataResponse[IndustryInfo]):
    """Model for industry info response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class IndustryOverviewResponse(DataResponse[IndustryOverview]):
    """Model for industry overview response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class IndustryDetailsResponse(DataResponse[IndustryDetails]):
    """Model for industry details response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class IndustryCompaniesResponse(ListResponse[IndustryCompany]):
    """Model for industry companies response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class IndustryGrowthCompaniesResponse(ListResponse[IndustryGrowthCompany]):
    """Model for industry growth companies response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class IndustryPerformingCompaniesResponse(ListResponse[IndustryPerformingCompany]):
    """Model for industry performing companies' response."""
    model_config = {
        "arbitrary_types_allowed": True
    }


class IndustryComparisonResponse(ListResponse[IndustryComparison]):
    """Model for industry comparison response."""
    model_config = {
        "arbitrary_types_allowed": True
    }