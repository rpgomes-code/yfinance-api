"""Constants for the YFinance API.

This module contains constants used throughout the application.
"""
from enum import Enum

# API version
API_VERSION = "v1"

# Cache durations in seconds
THIRTY_MINUTES = 30 * 60
ONE_HOUR = 60 * 60
ONE_DAY = 24 * 60 * 60
ONE_WEEK = 7 * 24 * 60 * 60
ONE_MONTH = 30 * 24 * 60 * 60
THREE_MONTHS = 90 * 24 * 60 * 60

# Default values
DEFAULT_TICKER = "AAPL"
DEFAULT_MARKET = "US"
DEFAULT_SECTOR = "technology"
DEFAULT_INDUSTRY = "software"
DEFAULT_PERIOD = "1mo"
DEFAULT_INTERVAL = "1d"

# YFinance parameter validation
VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
VALID_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"}
VALID_MARKETS = {"US", "CA", "BR", "MX", "DE", "FR", "ES", "GB", "IT", "NL", "PT", "IN", "SG", "HK", "JP", "AU", "NZ"}
VALID_ACTIONS = {"div", "split"}

# Common sectors and industries
COMMON_SECTORS = {
    "basic_materials": "Basic Materials",
    "communication_services": "Communication Services",
    "consumer_cyclical": "Consumer Cyclical",
    "consumer_defensive": "Consumer Defensive",
    "energy": "Energy",
    "financial_services": "Financial Services",
    "healthcare": "Healthcare",
    "industrials": "Industrials",
    "real_estate": "Real Estate",
    "technology": "Technology",
    "utilities": "Utilities",
}


# Content types
class ContentType(str, Enum):
    """Enum for content types."""
    JSON = "application/json"
    TEXT = "text/plain"
    HTML = "text/html"
    CSV = "text/csv"
    XML = "application/xml"
    PDF = "application/pdf"


# HTTP methods
class HTTPMethod(str, Enum):
    """Enum for HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


# Error codes
class ErrorCode(str, Enum):
    """Enum for API error codes."""
    INVALID_REQUEST = "invalid_request"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    METHOD_NOT_ALLOWED = "method_not_allowed"
    CONFLICT = "conflict"
    UNPROCESSABLE_ENTITY = "unprocessable_entity"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    GATEWAY_TIMEOUT = "gateway_timeout"

    # Custom error codes
    TICKER_NOT_FOUND = "ticker_not_found"
    MARKET_NOT_FOUND = "market_not_found"
    SECTOR_NOT_FOUND = "sector_not_found"
    INDUSTRY_NOT_FOUND = "industry_not_found"
    INVALID_PARAMETER = "invalid_parameter"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    YFINANCE_ERROR = "yfinance_error"


# Cache keys
class CacheNamespace(str, Enum):
    """Enum for cache namespaces."""
    TICKER = "ticker"
    MARKET = "market"
    SEARCH = "search"
    SECTOR = "sector"
    INDUSTRY = "industry"
    METRICS = "metrics"
    RATE_LIMIT = "rate_limit"


# API documentation tags
API_TAGS = [
    {
        "name": "ticker",
        "description": "Operations with stock ticker data",
    },
    {
        "name": "market",
        "description": "Operations with market data",
    },
    {
        "name": "search",
        "description": "Search operations",
    },
    {
        "name": "sector",
        "description": "Operations with sector data",
    },
    {
        "name": "industry",
        "description": "Operations with industry data",
    },
    {
        "name": "metrics",
        "description": "API metrics and monitoring",
    },
]

# Endpoint groups and cache durations
ENDPOINT_CACHE_DURATIONS = {
    # Ticker endpoints
    "actions": ONE_DAY,
    "analyst_price_targets": ONE_DAY,
    "balance_sheet": ONE_DAY,
    "basic_info": THREE_MONTHS,
    "calendar": ONE_WEEK,
    "capital_gains": ONE_DAY,
    "cash_flow": ONE_DAY,
    "dividends": ONE_DAY,
    "earnings": ONE_DAY,
    "earnings_dates": ONE_WEEK,
    "fast_info": THREE_MONTHS,
    "financials": ONE_DAY,
    "isin": THREE_MONTHS,
    "major_holders": ONE_WEEK,
    "news": ONE_DAY,

    # Market endpoints
    "market_status": THIRTY_MINUTES,
    "market_summary": THIRTY_MINUTES,

    # Search endpoints
    "search_all": THIRTY_MINUTES,
    "search_quotes": THIRTY_MINUTES,

    # Sector endpoints
    "sector_industries": THREE_MONTHS,
    "sector_overview": ONE_WEEK,

    # Industry endpoints
    "industry_overview": ONE_WEEK,
    "industry_top_companies": ONE_WEEK,
}

# Midnight invalidation for endpoints
INVALIDATE_AT_MIDNIGHT = {
    "actions",
    "analyst_price_targets",
    "balance_sheet",
    "cash_flow",
    "dividends",
    "earnings",
    "financials",
    "news",
}