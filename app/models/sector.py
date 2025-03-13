"""Models for sector-related endpoints.

This module contains model definitions for sector data structures
used in the sector endpoints of the API.
"""
from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SectorPerformance(BaseModel):
    """Model for sector performance metrics."""

    day: Optional[float] = Field(None, description="1-day performance (%)")
    week: Optional[float] = Field(None, description="1-week performance (%)")
    month: Optional[float] = Field(None, description="1-month performance (%)")
    three_month: Optional[float] = Field(None, description="3-month performance (%)")
    year: Optional[float] = Field(None, description="1-year performance (%)")
    ytd: Optional[float] = Field(None, description="Year-to-date performance (%)")
    three_year: Optional[float] = Field(None, description="3-year performance (%)")
    five_year: Optional[float] = Field(None, description="5-year performance (%)")
    ten_year: Optional[float] = Field(None, description="10-year performance (%)")


class SectorCompany(BaseModel):
    """Model for a company in a sector."""

    symbol: str = Field(..., description="Company ticker symbol")
    name: str = Field(..., description="Company name")
    price: Optional[float] = Field(None, description="Current stock price")
    change: Optional[float] = Field(None, description="Price change")
    percent_change: Optional[float] = Field(None, description="Percentage price change")
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    industry: Optional[str] = Field(None, description="Industry within the sector")
    country: Optional[str] = Field(None, description="Country")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield (%)")


class SectorETF(BaseModel):
    """Model for a sector ETF."""

    symbol: str = Field(..., description="ETF ticker symbol")
    name: str = Field(..., description="ETF name")
    price: Optional[float] = Field(None, description="Current price")
    change: Optional[float] = Field(None, description="Price change")
    percent_change: Optional[float] = Field(None, description="Percentage price change")
    aum: Optional[int] = Field(None, description="Assets under management")
    expense_ratio: Optional[float] = Field(None, description="Expense ratio (%)")
    provider: Optional[str] = Field(None, description="ETF provider")
    ytd_return: Optional[float] = Field(None, description="Year-to-date return (%)")
    one_year_return: Optional[float] = Field(None, description="1-year return (%)")


class SectorFund(BaseModel):
    """Model for a sector mutual fund."""

    symbol: str = Field(..., description="Fund ticker symbol")
    name: str = Field(..., description="Fund name")
    price: Optional[float] = Field(None, description="Current NAV")
    change: Optional[float] = Field(None, description="NAV change")
    percent_change: Optional[float] = Field(None, description="Percentage NAV change")
    aum: Optional[int] = Field(None, description="Assets under management")
    expense_ratio: Optional[float] = Field(None, description="Expense ratio (%)")
    provider: Optional[str] = Field(None, description="Fund provider")
    ytd_return: Optional[float] = Field(None, description="Year-to-date return (%)")
    one_year_return: Optional[float] = Field(None, description="1-year return (%)")
    three_year_return: Optional[float] = Field(None, description="3-year return (%)")
    five_year_return: Optional[float] = Field(None, description="5-year return (%)")


class SectorIndustry(BaseModel):
    """Model for an industry within a sector."""

    key: str = Field(..., description="Industry key")
    name: str = Field(..., description="Industry name")
    company_count: Optional[int] = Field(None, description="Number of companies")
    performance: Optional[SectorPerformance] = Field(None, description="Industry performance")
    market_cap: Optional[int] = Field(None, description="Total market capitalization")
    average_pe: Optional[float] = Field(None, description="Average P/E ratio")
    average_dividend_yield: Optional[float] = Field(None, description="Average dividend yield (%)")


class ResearchReport(BaseModel):
    """Model for a sector research report."""

    title: str = Field(..., description="Report title")
    publisher: str = Field(..., description="Report publisher")
    published_at: date = Field(..., description="Publication date")
    summary: Optional[str] = Field(None, description="Report summary")
    url: Optional[str] = Field(None, description="Report URL")
    tickers: Optional[List[str]] = Field(None, description="Related ticker symbols")


class SectorInfo(BaseModel):
    """Model for basic sector information."""

    key: str = Field(..., description="Sector key")
    name: str = Field(..., description="Sector name")
    symbol: Optional[str] = Field(None, description="Sector symbol")


class SectorOverview(SectorInfo):
    """Model for sector overview information."""

    performance: Optional[SectorPerformance] = Field(None, description="Sector performance")
    market_cap: Optional[int] = Field(None, description="Total market capitalization")
    average_pe: Optional[float] = Field(None, description="Average P/E ratio")
    average_dividend_yield: Optional[float] = Field(None, description="Average dividend yield (%)")
    company_count: Optional[int] = Field(None, description="Number of companies")
    industry_count: Optional[int] = Field(None, description="Number of industries")
    description: Optional[str] = Field(None, description="Sector description")


class SectorDetails(SectorOverview):
    """Model for detailed sector information."""

    industries: Optional[List[SectorIndustry]] = Field(None, description="Industries in the sector")
    top_companies: Optional[List[SectorCompany]] = Field(None, description="Top companies in the sector")
    top_etfs: Optional[List[SectorETF]] = Field(None, description="Top ETFs tracking the sector")
    top_mutual_funds: Optional[List[SectorFund]] = Field(None, description="Top mutual funds in the sector")
    research_reports: Optional[List[ResearchReport]] = Field(None, description="Research reports")