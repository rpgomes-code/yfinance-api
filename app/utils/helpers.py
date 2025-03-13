"""Helper functions for the YFinance API.

This module provides various helper functions used throughout the API,
including data processing, conversion, and utility functions.
"""
import logging
import asyncio
import functools
import re
from datetime import datetime, date, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas as pd
import numpy as np
import yfinance as yf

from app.core.constants import (
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
    VALID_PERIODS,
    VALID_INTERVALS
)

logger = logging.getLogger(__name__)


def get_ticker_info(ticker: str) -> Dict[str, Any]:
    """
    Get basic information about a ticker.

    Args:
        ticker: Ticker symbol

    Returns:
        Dict[str, Any]: Basic ticker information
    """
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info

        # Extract essential information
        essential_info = {
            "symbol": ticker,
            "name": info.get("shortName") or info.get("longName", ticker),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
            "market_cap": info.get("marketCap"),
            "price": info.get("regularMarketPrice") or info.get("currentPrice"),
            "website": info.get("website"),
        }

        return essential_info
    except Exception as e:
        logger.error(f"Error getting info for ticker {ticker}: {str(e)}")
        return {"symbol": ticker, "error": str(e)}


def get_market_status(market: str) -> Dict[str, Any]:
    """
    Get current market status.

    Args:
        market: Market identifier

    Returns:
        Dict[str, Any]: Market status information
    """
    try:
        market_obj = yf.Market(market)
        status = market_obj.status

        return status
    except Exception as e:
        logger.error(f"Error getting status for market {market}: {str(e)}")
        return {
            "market": market,
            "is_open": False,
            "error": str(e)
        }


def get_sector_info(sector: str) -> Dict[str, Any]:
    """
    Get basic information about a sector.

    Args:
        sector: Sector identifier

    Returns:
        Dict[str, Any]: Basic sector information
    """
    try:
        sector_obj = yf.Sector(sector)

        # Extract essential information
        essential_info = {
            "key": sector_obj.key,
            "name": sector_obj.name,
            "symbol": sector_obj.symbol,
        }

        return essential_info
    except Exception as e:
        logger.error(f"Error getting info for sector {sector}: {str(e)}")
        return {"sector": sector, "error": str(e)}


def get_industry_info(industry: str) -> Dict[str, Any]:
    """
    Get basic information about an industry.

    Args:
        industry: Industry identifier

    Returns:
        Dict[str, Any]: Basic industry information
    """
    try:
        industry_obj = yf.Industry(industry)

        # Extract essential information
        essential_info = {
            "key": industry_obj.key,
            "name": industry_obj.name,
            "symbol": industry_obj.symbol,
            "sector_key": industry_obj.sector_key,
            "sector_name": industry_obj.sector_name,
        }

        return essential_info
    except Exception as e:
        logger.error(f"Error getting info for industry {industry}: {str(e)}")
        return {"industry": industry, "error": str(e)}


def convert_date_format(date_str: Optional[str]) -> Optional[str]:
    """
    Convert date string to format accepted by yfinance.

    Args:
        date_str: Date string

    Returns:
        Optional[str]: Converted date string or None
    """
    if not date_str:
        return None

    try:
        # Try to parse as ISO format
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime('%Y-%m-%d')
    except ValueError:
        try:
            # Try to parse as YYYY-MM-DD
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError:
            # Return original string, yfinance will handle validation
            return date_str


def parse_period_interval(
        period: Optional[str] = None,
        interval: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None
) -> Tuple[str, str, Optional[str], Optional[str]]:
    """
    Parse and validate period and interval parameters.

    Args:
        period: Time period
        interval: Data interval
        start: Start date
        end: End date

    Returns:
        Tuple[str, str, Optional[str], Optional[str]]: Parsed parameters
    """
    # Default values
    if not period and not start:
        period = DEFAULT_PERIOD

    if not interval:
        interval = DEFAULT_INTERVAL

    # Validate period
    if period and period not in VALID_PERIODS:
        period = DEFAULT_PERIOD

    # Validate interval
    if interval not in VALID_INTERVALS:
        interval = DEFAULT_INTERVAL

    # Convert date formats
    start = convert_date_format(start)
    end = convert_date_format(end)

    # If start and end are provided, set period to None
    if start and end:
        period = None

    return period, interval, start, end


def get_history_args(
        period: Optional[str] = None,
        interval: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        prepost: bool = False,
        actions: bool = True,
        auto_adjust: bool = True,
        **kwargs
) -> Dict[str, Any]:
    """
    Get arguments for ticker.history() method.

    Args:
        period: Time period
        interval: Data interval
        start: Start date
        end: End date
        prepost: Include pre/post market data
        actions: Include dividends and splits
        auto_adjust: Auto-adjust prices
        **kwargs: Additional arguments

    Returns:
        Dict[str, Any]: Arguments for history method
    """
    # Parse and validate parameters
    period, interval, start, end = parse_period_interval(period, interval, start, end)

    # Build arguments dictionary
    args = {
        "interval": interval,
        "prepost": prepost,
        "actions": actions,
        "auto_adjust": auto_adjust,
    }

    # Add period or start/end
    if period:
        args["period"] = period
    else:
        if start:
            args["start"] = start
        if end:
            args["end"] = end

    # Add additional arguments
    args.update(kwargs)

    return args


def snake_to_camel(snake_str: str) -> str:
    """
    Convert snake_case to camelCase.

    Args:
        snake_str: String in snake_case

    Returns:
        str: String in camelCase
    """
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def camel_to_snake(camel_str: str) -> str:
    """
    Convert camelCase to snake_case.

    Args:
        camel_str: String in camelCase

    Returns:
        str: String in snake_case
    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize DataFrame column names to snake_case.

    Args:
        df: DataFrame to normalize

    Returns:
        pd.DataFrame: DataFrame with normalized column names
    """
    if df.empty:
        return df

    # Convert column names to snake_case
    df = df.copy()
    df.columns = [camel_to_snake(col) if col[0].isupper() else col for col in df.columns]

    # Replace spaces with underscores
    df.columns = [col.replace(' ', '_').lower() for col in df.columns]

    return df


def convert_date_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert date-like columns to datetime.

    Args:
        df: DataFrame to convert

    Returns:
        pd.DataFrame: DataFrame with converted date columns
    """
    if df.empty:
        return df

    df = df.copy()

    # Identify potential date columns
    date_columns = []
    date_patterns = [
        r'date', r'time', r'period', r'year', r'month', r'day',
        r'created', r'updated', r'modified', r'published', r'posted'
    ]

    for col in df.columns:
        col_lower = str(col).lower()
        if any(re.search(pattern, col_lower) for pattern in date_patterns):
            date_columns.append(col)

    # Convert date columns to datetime
    for col in date_columns:
        try:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        except Exception:
            # Skip columns that can't be converted
            pass

    return df


def safe_get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """
    Safely get an attribute from an object.

    Args:
        obj: Object to get attribute from
        attr: Attribute name
        default: Default value if attribute doesn't exist

    Returns:
        Any: Attribute value or default
    """
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        return default


def safe_divide(numerator: Union[int, float], denominator: Union[int, float], default: Any = None) -> Any:
    """
    Safely divide two numbers.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value if division fails

    Returns:
        Any: Division result or default
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError, ZeroDivisionError):
        return default


def paginate_results(
        items: List[Any],
        page: int = 1,
        page_size: int = 100
) -> Tuple[List[Any], Dict[str, Any]]:
    """
    Paginate a list of items.

    Args:
        items: List of items to paginate
        page: Page number (1-based)
        page_size: Number of items per page

    Returns:
        Tuple[List[Any], Dict[str, Any]]: Paginated items and pagination info
    """
    # Validate page and page_size
    page = max(1, page)
    page_size = max(1, min(1000, page_size))

    # Calculate start and end indices
    start = (page - 1) * page_size
    end = start + page_size

    # Slice the items
    paginated_items = items[start:end]

    # Create pagination info
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size

    pagination = {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
    }

    return paginated_items, pagination


def filter_dataframe(
        df: pd.DataFrame,
        filters: Dict[str, Any]
) -> pd.DataFrame:
    """
    Filter a DataFrame based on column conditions.

    Args:
        df: DataFrame to filter
        filters: Dictionary of column-value pairs

    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    if df.empty or not filters:
        return df

    filtered_df = df.copy()

    for column, value in filters.items():
        if column in filtered_df.columns:
            if isinstance(value, (list, tuple, set)):
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            elif isinstance(value, dict):
                # Handle operators like gt, lt, eq, ne
                if 'gt' in value:
                    filtered_df = filtered_df[filtered_df[column] > value['gt']]
                if 'gte' in value:
                    filtered_df = filtered_df[filtered_df[column] >= value['gte']]
                if 'lt' in value:
                    filtered_df = filtered_df[filtered_df[column] < value['lt']]
                if 'lte' in value:
                    filtered_df = filtered_df[filtered_df[column] <= value['lte']]
                if 'eq' in value:
                    filtered_df = filtered_df[filtered_df[column] == value['eq']]
                if 'ne' in value:
                    filtered_df = filtered_df[filtered_df[column] != value['ne']]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]

    return filtered_df


def sort_dataframe(
        df: pd.DataFrame,
        sort_by: str,
        ascending: bool = True
) -> pd.DataFrame:
    """
    Sort a DataFrame by column.

    Args:
        df: DataFrame to sort
        sort_by: Column to sort by
        ascending: Sort in ascending order

    Returns:
        pd.DataFrame: Sorted DataFrame
    """
    if df.empty or sort_by not in df.columns:
        return df

    return df.sort_values(by=sort_by, ascending=ascending)


def async_wrap(func: Callable) -> Callable:
    """
    Wrap a synchronous function to be asynchronous.

    Args:
        func: Function to wrap

    Returns:
        Callable: Asynchronous wrapper function
    """

    @functools.wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return run


def parse_date_range(
        period: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None
) -> Tuple[Optional[date], Optional[date]]:
    """
    Parse period or start/end dates.

    Args:
        period: Time period string
        start: Start date string
        end: End date string

    Returns:
        Tuple[Optional[date], Optional[date]]: Start and end dates
    """
    # If start and end are provided, use them
    if start or end:
        start_date = None
        end_date = None

        if start:
            try:
                start_date = datetime.fromisoformat(start.replace('Z', '+00:00')).date()
            except ValueError:
                try:
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                except ValueError:
                    pass

        if end:
            try:
                end_date = datetime.fromisoformat(end.replace('Z', '+00:00')).date()
            except ValueError:
                try:
                    end_date = datetime.strptime(end, '%Y-%m-%d').date()
                except ValueError:
                    pass

        # Default end date to today if not provided
        if not end_date:
            end_date = datetime.now().date()

        return start_date, end_date

    # If period is provided, calculate start date based on period
    if period:
        end_date = datetime.now().date()

        if period == '1d':
            start_date = end_date - timedelta(days=1)
        elif period == '5d':
            start_date = end_date - timedelta(days=5)
        elif period == '1mo':
            start_date = end_date - timedelta(days=30)
        elif period == '3mo':
            start_date = end_date - timedelta(days=90)
        elif period == '6mo':
            start_date = end_date - timedelta(days=180)
        elif period == '1y':
            start_date = end_date - timedelta(days=365)
        elif period == '2y':
            start_date = end_date - timedelta(days=2 * 365)
        elif period == '5y':
            start_date = end_date - timedelta(days=5 * 365)
        elif period == '10y':
            start_date = end_date - timedelta(days=10 * 365)
        elif period == 'ytd':
            start_date = date(end_date.year, 1, 1)
        elif period == 'max':
            start_date = date(1900, 1, 1)  # A very old date
        else:
            # Default to 1 month
            start_date = end_date - timedelta(days=30)

        return start_date, end_date

    # Default to 1 month
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    return start_date, end_date