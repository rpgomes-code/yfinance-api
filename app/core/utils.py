"""Utility functions for the YFinance API.

This module contains utility functions used throughout the application.
"""
import asyncio
import inspect
import re
from datetime import datetime, date
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
import pandas as pd

from app.core.constants import VALID_PERIODS, VALID_INTERVALS


def is_valid_ticker(ticker: str) -> bool:
    """
    Check if a ticker symbol is valid.

    This is a basic validation that checks if the ticker
    matches the pattern of valid stock symbols.

    Args:
        ticker: Ticker symbol to validate

    Returns:
        bool: True if valid, False otherwise
    """
    # Basic validation: 1-5 uppercase letters, optionally followed by a dot and 1-2 letters
    pattern = r'^[A-Z]{1,5}(\.[A-Z]{1,2})?$'
    return bool(re.match(pattern, ticker))


def is_valid_period(period: str) -> bool:
    """
    Check if a period string is valid.

    Args:
        period: Period string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    return period.lower() in VALID_PERIODS


def is_valid_interval(interval: str) -> bool:
    """
    Check if an interval string is valid.

    Args:
        interval: Interval string to validate

    Returns:
        bool: True if valid, False otherwise
    """
    return interval.lower() in VALID_INTERVALS


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


def format_datetime(dt: Union[datetime, date, str]) -> str:
    """
    Format datetime as ISO string.

    Args:
        dt: Datetime to format

    Returns:
        str: Formatted datetime string
    """
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except ValueError:
            try:
                dt = datetime.strptime(dt, '%Y-%m-%d')
            except ValueError:
                return dt

    if isinstance(dt, datetime):
        return dt.isoformat()
    elif isinstance(dt, date):
        return dt.isoformat()

    return str(dt)


def format_decimal(value: Union[float, int]) -> Union[float, int]:
    """
    Format decimal value, removing trailing zeros.

    Args:
        value: Value to format

    Returns:
        Union[float, int]: Formatted value
    """
    if isinstance(value, float):
        # Convert to int if it's a whole number
        if value.is_integer():
            return int(value)

        # Otherwise format to 6 decimal places
        return round(value, 6)

    return value


def df_to_json(
        df: pd.DataFrame,
        orient: str = 'records',
        date_format: str = 'iso',
        double_precision: int = 6
) -> List[Dict[str, Any]]:
    """
    Convert pandas DataFrame to JSON.

    Args:
        df: DataFrame to convert
        orient: JSON orientation
        date_format: Date format
        double_precision: Decimal precision

    Returns:
        List[Dict[str, Any]]: JSON representation of DataFrame
    """
    if df.empty:
        return []

    # Reset index if it's not a default RangeIndex
    if not isinstance(df.index, pd.RangeIndex):
        df = df.reset_index()

    # Convert to JSON
    json_data = df.to_json(
        orient=orient,
        date_format=date_format,
        double_precision=double_precision,
        force_ascii=False
    )

    # Parse JSON string to Python objects
    import json
    return json.loads(json_data)


def series_to_json(
        series: pd.Series,
        date_format: str = 'iso',
        double_precision: int = 6
) -> Dict[str, Any]:
    """
    Convert pandas Series to JSON.

    Args:
        series: Series to convert
        date_format: Date format
        double_precision: Decimal precision

    Returns:
        Dict[str, Any]: JSON representation of Series
    """
    if series.empty:
        return {}

    # Convert to JSON
    json_data = series.to_json(
        date_format=date_format,
        double_precision=double_precision,
        force_ascii=False
    )

    # Parse JSON string to Python objects
    import json
    return json.loads(json_data)


def async_wrap(func: Callable) -> Callable:
    """
    Wrap a synchronous function to be async.

    This function allows using synchronous functions in async contexts.

    Args:
        func: Synchronous function to wrap

    Returns:
        Callable: Async wrapper function
    """

    @wraps(func)
    async def run(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))

    return run


def paginate(
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
        Tuple[List[Any], Dict[str, Any]]: Paginated items and pagination metadata
    """
    # Ensure page and page_size are valid
    page = max(1, page)
    page_size = max(1, min(1000, page_size))

    # Calculate start and end indices
    start = (page - 1) * page_size
    end = start + page_size

    # Get paginated items
    paginated_items = items[start:end]

    # Calculate total pages
    total_items = len(items)
    total_pages = (total_items + page_size - 1) // page_size

    # Create pagination metadata
    pagination = {
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
    }

    return paginated_items, pagination


def get_yfinance_params_from_func(func: Callable) -> Set[str]:
    """
    Get the parameter names from a yfinance function.

    Args:
        func: yfinance function

    Returns:
        Set[str]: Set of parameter names
    """
    signature = inspect.signature(func)
    return set(signature.parameters.keys())