"""Enumeration types used across models.

This module contains enumerations used in models for
request validation and response serialization.
"""
from enum import Enum
from typing import List


class DataPeriod(str, Enum):
    """Enum for data period options."""

    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    ONE_YEAR = "1y"
    TWO_YEARS = "2y"
    FIVE_YEARS = "5y"
    TEN_YEARS = "10y"
    YEAR_TO_DATE = "ytd"
    MAX = "max"

    @classmethod
    def list(cls) -> List[str]:
        """Get a list of all period values."""
        return [e.value for e in cls]


class DataInterval(str, Enum):
    """Enum for data interval options."""

    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"

    @classmethod
    def list(cls) -> List[str]:
        """Get a list of all interval values."""
        return [e.value for e in cls]


class ResponseFormat(str, Enum):
    """Enum for response format options."""

    DEFAULT = "default"
    COMPACT = "compact"
    EXTENDED = "extended"


class SortOrder(str, Enum):
    """Enum for sort order options."""

    ASC = "asc"
    DESC = "desc"


class FinancialStatement(str, Enum):
    """Enum for financial statement types."""

    INCOME_STATEMENT = "income_statement"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"


class ActionType(str, Enum):
    """Enum for action types."""

    DIVIDEND = "dividend"
    SPLIT = "split"


class CacheNamespace(str, Enum):
    """Enum for cache namespaces."""

    TICKER = "ticker"
    MARKET = "market"
    SEARCH = "search"
    SECTOR = "sector"
    INDUSTRY = "industry"
    METRICS = "metrics"
    RATE_LIMIT = "rate_limit"


class MarketRegion(str, Enum):
    """Enum for market regions."""

    US = "US"
    CA = "CA"
    BR = "BR"
    MX = "MX"
    DE = "DE"
    FR = "FR"
    ES = "ES"
    GB = "GB"
    IT = "IT"
    NL = "NL"
    PT = "PT"
    IN = "IN"
    SG = "SG"
    HK = "HK"
    JP = "JP"
    AU = "AU"
    NZ = "NZ"

    @classmethod
    def list(cls) -> List[str]:
        """Get a list of all market region values."""
        return [e.value for e in cls]


class Currency(str, Enum):
    """Enum for currency types."""

    USD = "USD"
    CAD = "CAD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    CNY = "CNY"
    HKD = "HKD"
    INR = "INR"
    AUD = "AUD"
    BRL = "BRL"
    MXN = "MXN"
    SGD = "SGD"


class Exchange(str, Enum):
    """Enum for stock exchanges."""

    NYSE = "NYSE"  # New York Stock Exchange
    NASDAQ = "NASDAQ"  # Nasdaq Stock Exchange
    TSX = "TSX"  # Toronto Stock Exchange
    LSE = "LSE"  # London Stock Exchange
    FSE = "FSE"  # Frankfurt Stock Exchange
    PAR = "PAR"  # Euronext Paris
    AMS = "AMS"  # Euronext Amsterdam
    BRU = "BRU"  # Euronext Brussels
    SIX = "SIX"  # SIX Swiss Exchange
    JSE = "JSE"  # Johannesburg Stock Exchange
    TSE = "TSE"  # Tokyo Stock Exchange
    HKEX = "HKEX"  # Hong Kong Stock Exchange
    SSE = "SSE"  # Shanghai Stock Exchange
    SZSE = "SZSE"  # Shenzhen Stock Exchange
    NSE = "NSE"  # National Stock Exchange of India
    BSE = "BSE"  # Bombay Stock Exchange
    ASX = "ASX"  # Australian Securities Exchange
    NZX = "NZX"  # New Zealand Stock Exchange
    KRX = "KRX"  # Korea Exchange
    SGX = "SGX"  # Singapore Exchange
    BOVESPA = "BOVESPA"  # Brasil Bolsa Balcão
    BMV = "BMV"  # Bolsa Mexicana de Valores

    @classmethod
    def list(cls) -> List[str]:
        """Get a list of all exchange values."""
        return [e.value for e in cls]


class QuoteType(str, Enum):
    """Enum for quote types."""

    EQUITY = "EQUITY"
    ETF = "ETF"
    MUTUAL_FUND = "MUTUALFUND"
    INDEX = "INDEX"
    CURRENCY = "CURRENCY"
    FUTURES = "FUTURES"
    CRYPTOCURRENCY = "CRYPTOCURRENCY"

    @classmethod
    def list(cls) -> List[str]:
        """Get a list of all quote type values."""
        return [e.value for e in cls]