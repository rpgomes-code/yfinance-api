"""Response models for the YFinance API.

This module contains response model definitions that wrap
data models for API responses.
"""
from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field
from pydantic.generics import GenericModel

from app.models.common import Metadata, Pagination, PaginatedMetadata
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
from app.models.search import SearchResponse, SearchResult
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
    TickerInfo,
    TickerPrice
)

# Generic type for list item
T = TypeVar('T')


class ErrorResponse(BaseModel):
    """Model for error responses."""

    error: Dict[str, Any] = Field(..., description="Error details")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )


class DataResponse(GenericModel, Generic[T]):
    """Generic model for data responses."""

    data: T = Field(..., description="Response data")
    metadata: Optional[Metadata] = Field(None, description="Response metadata")


class ListResponse(GenericModel, Generic[T]):
    """Generic model for list responses."""

    items: List[T] = Field(..., description="List of items")
    count: int = Field(..., description="Number of items")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class PaginatedResponse(GenericModel, Generic[T]):
    """Generic model for paginated responses."""

    items: List[T] = Field(..., description="List of items")
    pagination: Pagination = Field(..., description="Pagination information")
    metadata: Optional[Metadata] = Field(None, description="Response metadata")


# Ticker response models
class TickerActionsResponse(ListResponse[TickerAction]):
    """Model for ticker actions response."""
    pass


class TickerAnalystPriceTargetsResponse(ListResponse[AnalystPriceTarget]):
    """Model for ticker analyst price targets response."""
    pass


class TickerHistoryResponse(ListResponse[HistoricalData]):
    """Model for ticker history response."""
    pass


class TickerBalanceSheetResponse(ListResponse[FinancialStatement]):
    """Model for ticker balance sheet response."""
    pass


class TickerCashFlowResponse(ListResponse[FinancialStatement]):
    """Model for ticker cash flow response."""
    pass


class TickerIncomeStatementResponse(ListResponse[FinancialStatement]):
    """Model for ticker income statement response."""
    pass


class TickerEarningsResponse(ListResponse[EarningsData]):
    """Model for ticker earnings response."""
    pass


class TickerHoldersResponse(ListResponse[Holder]):
    """Model for ticker holders response."""
    pass


class TickerInsiderTransactionsResponse(ListResponse[InsiderTransaction]):
    """Model for ticker insider transactions response."""
    pass


class TickerRecommendationsResponse(ListResponse[Recommendation]):
    """Model for ticker recommendations response."""
    pass


class TickerNewsResponse(ListResponse[NewsItem]):
    """Model for ticker news response."""
    pass


class TickerOptionChainsResponse(ListResponse[OptionChain]):
    """Model for ticker option chains response."""
    pass


class TickerInfoResponse(DataResponse[TickerInfo]):
    """Model for ticker info response."""
    pass


class TickerBasicInfoResponse(DataResponse[TickerBasicInfo]):
    """Model for ticker basic info response."""
    pass


class TickerEarningsEstimateResponse(DataResponse[EarningsEstimate]):
    """Model for ticker earnings estimate response."""
    pass


class TickerRevenueEstimateResponse(DataResponse[RevenueEstimate]):
    """Model for ticker revenue estimate response."""
    pass


class TickerSustainabilityResponse(DataResponse[SustainabilityMetric]):
    """Model for ticker sustainability response."""
    pass


# Market response models
class MarketStatusResponse(DataResponse[MarketStatus]):
    """Model for market status response."""
    pass


class MarketSummaryResponse(DataResponse[MarketSummary]):
    """Model for market summary response."""
    pass


# Search response models
class SearchResultsResponse(DataResponse[SearchResponse]):
    """Model for search results response."""
    pass


# Sector response models
class SectorInfoResponse(DataResponse[SectorInfo]):
    """Model for sector info response."""
    pass


class SectorOverviewResponse(DataResponse[SectorOverview]):
    """Model for sector overview response."""
    pass


class SectorDetailsResponse(DataResponse[SectorDetails]):
    """Model for sector details response."""
    pass


class SectorIndustriesResponse(ListResponse[SectorIndustry]):
    """Model for sector industries response."""
    pass


class SectorCompaniesResponse(ListResponse[SectorCompany]):
    """Model for sector companies response."""
    pass


class SectorETFsResponse(ListResponse[SectorETF]):
    """Model for sector ETFs response."""
    pass


class SectorFundsResponse(ListResponse[SectorFund]):
    """Model for sector funds response."""
    pass


class SectorResearchReportsResponse(ListResponse[ResearchReport]):
    """Model for sector research reports response."""
    pass


# Industry response models
class IndustryInfoResponse(DataResponse[IndustryInfo]):
    """Model for industry info response."""
    pass


class IndustryOverviewResponse(DataResponse[IndustryOverview]):
    """Model for industry overview response."""
    pass


class IndustryDetailsResponse(DataResponse[IndustryDetails]):
    """Model for industry details response."""
    pass


class IndustryCompaniesResponse(ListResponse[IndustryCompany]):
    """Model for industry companies response."""
    pass


class IndustryGrowthCompaniesResponse(ListResponse[IndustryGrowthCompany]):
    """Model for industry growth companies response."""
    pass


class IndustryPerformingCompaniesResponse(ListResponse[IndustryPerformingCompany]):
    """Model for industry performing companies response."""
    pass


class IndustryComparisonResponse(ListResponse[IndustryComparison]):
    """Model for industry comparison response."""
    pass