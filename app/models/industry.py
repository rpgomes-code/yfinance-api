"""Models for industry-related endpoints.

This module contains model definitions for industry data structures
used in the industry endpoints of the API.
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.sector import (
    ResearchReport,
    SectorCompany,
    SectorETF,
    SectorFund,
    SectorPerformance
)


class IndustryInfo(BaseModel):
    """Model for basic industry information."""

    key: str = Field(..., description="Industry key")
    name: str = Field(..., description="Industry name")
    symbol: Optional[str] = Field(None, description="Industry symbol")
    sector_key: str = Field(..., description="Parent sector key")
    sector_name: str = Field(..., description="Parent sector name")


class IndustryOverview(IndustryInfo):
    """Model for industry overview information."""

    performance: Optional[SectorPerformance] = Field(None, description="Industry performance")
    market_cap: Optional[int] = Field(None, description="Total market capitalization")
    average_pe: Optional[float] = Field(None, description="Average P/E ratio")
    average_dividend_yield: Optional[float] = Field(None, description="Average dividend yield (%)")
    company_count: Optional[int] = Field(None, description="Number of companies")
    description: Optional[str] = Field(None, description="Industry description")


class IndustryCompany(SectorCompany):
    """Model for a company in an industry."""

    revenue_growth: Optional[float] = Field(None, description="Revenue growth (%)")
    earnings_growth: Optional[float] = Field(None, description="Earnings growth (%)")
    profit_margin: Optional[float] = Field(None, description="Profit margin (%)")
    debt_to_equity: Optional[float] = Field(None, description="Debt-to-equity ratio")
    return_on_equity: Optional[float] = Field(None, description="Return on equity (%)")
    return_on_assets: Optional[float] = Field(None, description="Return on assets (%)")


class IndustryGrowthCompany(IndustryCompany):
    """Model for a growth company in an industry."""

    revenue_growth_3y: Optional[float] = Field(None, description="3-year revenue growth (%)")
    earnings_growth_3y: Optional[float] = Field(None, description="3-year earnings growth (%)")
    eps_growth_3y: Optional[float] = Field(None, description="3-year EPS growth (%)")
    sales_growth_quarterly: Optional[float] = Field(None, description="Quarterly sales growth (%)")
    earnings_growth_quarterly: Optional[float] = Field(None, description="Quarterly earnings growth (%)")
    eps_growth_quarterly: Optional[float] = Field(None, description="Quarterly EPS growth (%)")


class IndustryPerformingCompany(IndustryCompany):
    """Model for a top performing company in an industry."""

    ytd_return: Optional[float] = Field(None, description="Year-to-date return (%)")
    one_year_return: Optional[float] = Field(None, description="1-year return (%)")
    three_year_return: Optional[float] = Field(None, description="3-year return (%)")
    five_year_return: Optional[float] = Field(None, description="5-year return (%)")
    beta: Optional[float] = Field(None, description="Beta")
    alpha: Optional[float] = Field(None, description="Alpha")
    sharpe_ratio: Optional[float] = Field(None, description="Sharpe ratio")


class IndustryDetails(IndustryOverview):
    """Model for detailed industry information."""

    top_companies: Optional[List[IndustryCompany]] = Field(None, description="Top companies in the industry")
    top_growth_companies: Optional[List[IndustryGrowthCompany]] = Field(None, description="Top growth companies")
    top_performing_companies: Optional[List[IndustryPerformingCompany]] = Field(None,
                                                                                description="Top performing companies")
    research_reports: Optional[List[ResearchReport]] = Field(None, description="Research reports")
    related_industries: Optional[List[IndustryInfo]] = Field(None, description="Related industries")
    top_etfs: Optional[List[SectorETF]] = Field(None, description="Top ETFs tracking the industry")
    top_mutual_funds: Optional[List[SectorFund]] = Field(None, description="Top mutual funds in the industry")


class IndustryComparison(BaseModel):
    """Model for industry comparison."""

    industry_key: str = Field(..., description="Industry key")
    industry_name: str = Field(..., description="Industry name")
    sector_key: str = Field(..., description="Parent sector key")
    sector_name: str = Field(..., description="Parent sector name")
    market_cap: Optional[int] = Field(None, description="Total market capitalization")
    company_count: Optional[int] = Field(None, description="Number of companies")
    average_pe: Optional[float] = Field(None, description="Average P/E ratio")
    average_dividend_yield: Optional[float] = Field(None, description="Average dividend yield (%)")
    day_change: Optional[float] = Field(None, description="1-day change (%)")
    ytd_change: Optional[float] = Field(None, description="Year-to-date change (%)")
    one_year_change: Optional[float] = Field(None, description="1-year change (%)")