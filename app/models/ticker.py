"""Models for ticker-related endpoints.

This module contains model definitions for ticker data structures
used in the ticker endpoints of the API.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, validator

from app.models.enums import (
    ActionType,
    Currency,
    Exchange,
    QuoteType
)


class TickerAction(BaseModel):
    """Model for ticker actions (dividends and splits)."""

    date: datetime = Field(..., description="Date of the action")
    action_type: ActionType = Field(..., description="Type of action", alias="type")
    value: float = Field(..., description="Value of the action")

    class Config:
        """Pydantic configuration."""
        populate_by_name = True  # This allows both the field name and alias to work
        use_enum_values = True  # Keep any existing config options


class HistoricalData(BaseModel):
    """Model for historical price data."""

    date: datetime = Field(..., description="Date of the data point")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: int = Field(..., description="Trading volume")
    dividends: Optional[float] = Field(0, description="Dividends")
    stock_splits: Optional[float] = Field(0, description="Stock splits")


class TickerPrice(BaseModel):
    """Model for basic price information."""

    symbol: str = Field(..., description="Ticker symbol")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change")
    percent_change: float = Field(..., description="Percentage price change")
    currency: Optional[str] = Field(None, description="Currency")
    last_updated: Optional[datetime] = Field(None, description="Last updated timestamp")


class TickerBasicInfo(BaseModel):
    """Model for basic ticker information."""

    symbol: str = Field(..., description="Ticker symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Industry sector")
    industry: Optional[str] = Field(None, description="Industry")
    exchange: Optional[str] = Field(None, description="Stock exchange")
    currency: Optional[str] = Field(None, description="Currency")
    country: Optional[str] = Field(None, description="Country")
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    price: Optional[float] = Field(None, description="Current price")
    change: Optional[float] = Field(None, description="Price change")
    percent_change: Optional[float] = Field(None, description="Percentage price change")
    website: Optional[str] = Field(None, description="Company website")
    logo_url: Optional[str] = Field(None, description="Company logo URL")


class TickerInfo(TickerBasicInfo):
    """Model for detailed ticker information."""

    summary: Optional[str] = Field(None, description="Business summary")
    security_type: Optional[str] = Field(None, description="Security type", alias="type")
    isin: Optional[str] = Field(None, description="ISIN code")
    employees: Optional[int] = Field(None, description="Number of employees")
    ceo: Optional[str] = Field(None, description="CEO name")
    founded: Optional[int] = Field(None, description="Year founded")
    headquarters: Optional[str] = Field(None, description="Headquarters location")
    market_open: Optional[str] = Field(None, description="Market open time")
    market_close: Optional[str] = Field(None, description="Market close time")
    timezone: Optional[str] = Field(None, description="Timezone")
    fifty_two_week_high: Optional[float] = Field(None, description="52-week high")
    fifty_two_week_low: Optional[float] = Field(None, description="52-week low")
    beta: Optional[float] = Field(None, description="Beta")
    pe_ratio: Optional[float] = Field(None, description="Price-to-earnings ratio")
    eps: Optional[float] = Field(None, description="Earnings per share")
    dividend_rate: Optional[float] = Field(None, description="Dividend rate")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield")
    payout_ratio: Optional[float] = Field(None, description="Payout ratio")
    trailing_pe: Optional[float] = Field(None, description="Trailing P/E")
    forward_pe: Optional[float] = Field(None, description="Forward P/E")
    price_to_sales: Optional[float] = Field(None, description="Price-to-sales ratio")
    price_to_book: Optional[float] = Field(None, description="Price-to-book ratio")
    book_value: Optional[float] = Field(None, description="Book value")
    market_cap: Optional[int] = Field(None, description="Market capitalization")
    enterprise_value: Optional[int] = Field(None, description="Enterprise value")
    profit_margins: Optional[float] = Field(None, description="Profit margins")
    float_shares: Optional[int] = Field(None, description="Float shares")
    shares_outstanding: Optional[int] = Field(None, description="Shares outstanding")
    shares_short: Optional[int] = Field(None, description="Short shares")
    short_ratio: Optional[float] = Field(None, description="Short ratio")
    average_volume: Optional[int] = Field(None, description="Average volume")
    average_volume_10_days: Optional[int] = Field(None, description="10-day average volume")
    average_daily_volume_10_day: Optional[int] = Field(None, description="10-day average daily volume")
    bid: Optional[float] = Field(None, description="Bid price")
    ask: Optional[float] = Field(None, description="Ask price")
    bid_size: Optional[int] = Field(None, description="Bid size")
    ask_size: Optional[int] = Field(None, description="Ask size")
    day_high: Optional[float] = Field(None, description="Day high")
    day_low: Optional[float] = Field(None, description="Day low")
    last_dividend_value: Optional[float] = Field(None, description="Last dividend value")
    last_dividend_date: Optional[date] = Field(None, description="Last dividend date")
    ex_dividend_date: Optional[date] = Field(None, description="Ex-dividend date")
    last_split_factor: Optional[str] = Field(None, description="Last split factor")
    last_split_date: Optional[date] = Field(None, description="Last split date")


class AnalystPriceTarget(BaseModel):
    """Model for analyst price targets."""

    date: datetime = Field(..., description="Date of the price target")
    firm: Optional[str] = Field(None, description="Name of the firm")
    to_grade: Optional[str] = Field(None, description="New grade")
    previous_grade: Optional[str] = Field(None, description="Previous grade", alias="from_grade")
    action: Optional[str] = Field(None, description="Action taken (e.g., 'main', 'up', 'down', 'init')")
    price_target: Optional[float] = Field(None, description="Price target")


class FinancialMetric(BaseModel):
    """Model for a single financial metric."""

    period: str = Field(..., description="Reporting period")
    value: Optional[float] = Field(None, description="Metric value")


class FinancialStatement(BaseModel):
    """Model for financial statements."""

    date: date = Field(..., description="Date of the statement")
    items: Dict[str, Optional[float]] = Field(..., description="Financial statement items")


class EarningsData(BaseModel):
    """Model for earnings data."""

    date: Optional[date] = Field(None, description="Earnings date")
    estimated_eps: Optional[float] = Field(None, description="Estimated EPS")
    reported_eps: Optional[float] = Field(None, description="Reported EPS")
    surprise: Optional[float] = Field(None, description="Earnings surprise")
    surprise_percent: Optional[float] = Field(None, description="Earnings surprise percent")


class EarningsEstimate(BaseModel):
    """Model for earnings estimate."""

    period: str = Field(..., description="Estimate period")
    estimate: Optional[float] = Field(None, description="EPS estimate")
    avg: Optional[float] = Field(None, description="Average estimate")
    low: Optional[float] = Field(None, description="Low estimate")
    high: Optional[float] = Field(None, description="High estimate")
    year_ago_eps: Optional[float] = Field(None, description="Year ago EPS")
    number_of_analysts: Optional[int] = Field(None, description="Number of analysts")
    growth: Optional[float] = Field(None, description="Growth estimate")


class RevenueEstimate(BaseModel):
    """Model for revenue estimate."""

    period: str = Field(..., description="Estimate period")
    estimate: Optional[float] = Field(None, description="Revenue estimate")
    avg: Optional[float] = Field(None, description="Average estimate")
    low: Optional[float] = Field(None, description="Low estimate")
    high: Optional[float] = Field(None, description="High estimate")
    year_ago_revenue: Optional[float] = Field(None, description="Year ago revenue")
    number_of_analysts: Optional[int] = Field(None, description="Number of analysts")
    growth: Optional[float] = Field(None, description="Growth estimate")


class Recommendation(BaseModel):
    """Model for analyst recommendations."""

    date: date = Field(..., description="Date of the recommendation")
    firm: Optional[str] = Field(None, description="Name of the firm")
    to_grade: str = Field(..., description="Recommendation grade")
    previous_grade: Optional[str] = Field(None, description="Previous grade", alias="from_grade")
    action: Optional[str] = Field(None, description="Action taken")


class Holder(BaseModel):
    """Model for a holder (institutional or insider)."""

    name: str = Field(..., description="Name of the holder")
    shares: int = Field(..., description="Number of shares held")
    date_reported: Optional[date] = Field(None, description="Date reported")
    percent: Optional[float] = Field(None, description="Percentage of outstanding shares")
    value: Optional[int] = Field(None, description="Value of holding")


class InsiderTransaction(BaseModel):
    """Model for insider transactions."""

    name: str = Field(..., description="Name of the insider")
    relation: Optional[str] = Field(None, description="Relation to the company")
    transaction: str = Field(..., description="Transaction type")
    shares: int = Field(..., description="Number of shares")
    value: Optional[int] = Field(None, description="Transaction value")
    date: date = Field(..., description="Transaction date")
    filing_date: Optional[date] = Field(None, description="Filing date")


class OptionQuote(BaseModel):
    """Model for an option quote."""

    contract_symbol: str = Field(..., description="Option contract symbol")
    strike: float = Field(..., description="Strike price")
    last_price: float = Field(..., description="Last price")
    bid: float = Field(..., description="Bid price")
    ask: float = Field(..., description="Ask price")
    change: float = Field(..., description="Price change")
    percent_change: float = Field(..., description="Percentage price change")
    volume: Optional[int] = Field(None, description="Trading volume")
    open_interest: Optional[int] = Field(None, description="Open interest")
    implied_volatility: Optional[float] = Field(None, description="Implied volatility")
    in_the_money: bool = Field(..., description="Whether the option is in the money")


class OptionChain(BaseModel):
    """Model for an option chain."""

    expiration_date: date = Field(..., description="Expiration date")
    calls: List[OptionQuote] = Field(..., description="Call options")
    puts: List[OptionQuote] = Field(..., description="Put options")


class NewsItem(BaseModel):
    """Model for a news item."""

    title: str = Field(..., description="News title")
    publisher: str = Field(..., description="News publisher")
    link: str = Field(..., description="News link")
    publish_date: datetime = Field(..., description="Publish date")
    summary: Optional[str] = Field(None, description="News summary")
    news_type: Optional[str] = Field(None, description="News type", alias="type")
    related_tickers: Optional[List[str]] = Field(None, description="Related tickers")


class SustainabilityMetric(BaseModel):
    """Model for sustainability metrics."""

    category: str = Field(..., description="Metric category")
    score: Optional[float] = Field(None, description="Metric score")
    percentile: Optional[float] = Field(None, description="Percentile rank")
    description: Optional[str] = Field(None, description="Metric description")


class Sustainability(BaseModel):
    """Model for sustainability information."""

    total_esg: Optional[float] = Field(None, description="Total ESG score")
    environmental_score: Optional[float] = Field(None, description="Environmental score")
    social_score: Optional[float] = Field(None, description="Social score")
    governance_score: Optional[float] = Field(None, description="Governance score")
    controversy_level: Optional[int] = Field(None, description="Controversy level")
    peer_count: Optional[int] = Field(None, description="Peer count")
    peer_group: Optional[str] = Field(None, description="Peer group")
    percentile: Optional[float] = Field(None, description="Percentile rank")
    metrics: Optional[List[SustainabilityMetric]] = Field(None, description="Sustainability metrics")