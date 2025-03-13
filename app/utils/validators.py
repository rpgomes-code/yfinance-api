"""Input validation utilities for the YFinance API.

This module provides functions for validating input parameters
to ensure they meet the requirements of the YFinance library.
"""
import logging
import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from fastapi import Path, Query, HTTPException, status
from pydantic import BaseModel, validator, Field

from app.core.constants import (
    VALID_PERIODS,
    VALID_INTERVALS,
    VALID_MARKETS,
    VALID_ACTIONS,
    DEFAULT_TICKER,
    DEFAULT_MARKET,
    DEFAULT_SECTOR,
    DEFAULT_INDUSTRY,
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL
)
from app.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


def validate_ticker(ticker: str) -> str:
    """
    Validate a ticker symbol.

    Args:
        ticker: Ticker symbol to validate

    Returns:
        str: Validated ticker symbol

    Raises:
        ValidationError: If ticker is invalid
    """
    # Strip whitespace and convert to uppercase
    ticker = ticker.strip().upper()

    # Check if ticker is empty
    if not ticker:
        raise ValidationError("Ticker symbol cannot be empty")

    # Basic validation: 1-5 uppercase letters, optionally followed by a dot and 1-2 letters
    # or a hyphen and additional characters for international tickers
    pattern = r'^[A-Z0-9]{1,5}(\.[A-Z]{1,2}|-[A-Z0-9]+)?$'

    if not re.match(pattern, ticker):
        raise ValidationError(
            f"Invalid ticker symbol: {ticker}. "
            "Ticker should be 1-5 uppercase letters, optionally followed by a dot and 1-2 letters."
        )

    return ticker


def validate_market(market: str) -> str:
    """
    Validate a market identifier.

    Args:
        market: Market identifier to validate

    Returns:
        str: Validated market identifier

    Raises:
        ValidationError: If market is invalid
    """
    # Strip whitespace and convert to uppercase
    market = market.strip().upper()

    # Check if market is empty
    if not market:
        raise ValidationError("Market identifier cannot be empty")

    # Check if market is valid
    if market not in VALID_MARKETS:
        raise ValidationError(
            f"Invalid market: {market}. "
            f"Valid markets are: {', '.join(sorted(VALID_MARKETS))}"
        )

    return market


def validate_sector(sector: str) -> str:
    """
    Validate a sector identifier.

    Args:
        sector: Sector identifier to validate

    Returns:
        str: Validated sector identifier

    Raises:
        ValidationError: If sector is invalid
    """
    # Strip whitespace and convert to lowercase
    sector = sector.strip().lower()

    # Check if sector is empty
    if not sector:
        raise ValidationError("Sector identifier cannot be empty")

    # Basic validation: only letters, numbers, and underscores
    pattern = r'^[a-z0-9_]+$'

    if not re.match(pattern, sector):
        raise ValidationError(
            f"Invalid sector identifier: {sector}. "
            "Sector should contain only letters, numbers, and underscores."
        )

    return sector


def validate_industry(industry: str) -> str:
    """
    Validate an industry identifier.

    Args:
        industry: Industry identifier to validate

    Returns:
        str: Validated industry identifier

    Raises:
        ValidationError: If industry is invalid
    """
    # Strip whitespace and convert to lowercase
    industry = industry.strip().lower()

    # Check if industry is empty
    if not industry:
        raise ValidationError("Industry identifier cannot be empty")

    # Basic validation: only letters, numbers, and underscores
    pattern = r'^[a-z0-9_]+$'

    if not re.match(pattern, industry):
        raise ValidationError(
            f"Invalid industry identifier: {industry}. "
            "Industry should contain only letters, numbers, and underscores."
        )

    return industry


def validate_period(period: str) -> str:
    """
    Validate a period string.

    Args:
        period: Period string to validate

    Returns:
        str: Validated period string

    Raises:
        ValidationError: If period is invalid
    """
    # Strip whitespace and convert to lowercase
    period = period.strip().lower()

    # Check if period is empty
    if not period:
        return DEFAULT_PERIOD

    # Check if period is valid
    if period not in VALID_PERIODS:
        raise ValidationError(
            f"Invalid period: {period}. "
            f"Valid periods are: {', '.join(sorted(VALID_PERIODS))}"
        )

    return period


def validate_interval(interval: str) -> str:
    """
    Validate an interval string.

    Args:
        interval: Interval string to validate

    Returns:
        str: Validated interval string

    Raises:
        ValidationError: If interval is invalid
    """
    # Strip whitespace and convert to lowercase
    interval = interval.strip().lower()

    # Check if interval is empty
    if not interval:
        return DEFAULT_INTERVAL

    # Check if interval is valid
    if interval not in VALID_INTERVALS:
        raise ValidationError(
            f"Invalid interval: {interval}. "
            f"Valid intervals are: {', '.join(sorted(VALID_INTERVALS))}"
        )

    return interval


def validate_date(date_str: str) -> str:
    """
    Validate a date string.

    Args:
        date_str: Date string to validate

    Returns:
        str: Validated date string

    Raises:
        ValidationError: If date is invalid
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
            raise ValidationError(f"Invalid date format: {date_str}. Use ISO format or YYYY-MM-DD.")


def validate_action(action: str) -> str:
    """
    Validate an action string.

    Args:
        action: Action string to validate

    Returns:
        str: Validated action string

    Raises:
        ValidationError: If action is invalid
    """
    # Strip whitespace and convert to lowercase
    action = action.strip().lower()

    # Check if action is empty
    if not action:
        raise ValidationError("Action cannot be empty")

    # Check if action is valid
    if action not in VALID_ACTIONS:
        raise ValidationError(
            f"Invalid action: {action}. "
            f"Valid actions are: {', '.join(sorted(VALID_ACTIONS))}"
        )

    return action


def validate_integer(value: int, name: str, min_value: Optional[int] = None, max_value: Optional[int] = None) -> int:
    """
    Validate an integer value.

    Args:
        value: Integer value to validate
        name: Name of the parameter
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        int: Validated integer value

    Raises:
        ValidationError: If value is invalid
    """
    if value is None:
        raise ValidationError(f"{name} cannot be None")

    try:
        value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be an integer")

    if min_value is not None and value < min_value:
        raise ValidationError(f"{name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{name} must be at most {max_value}")

    return value


def validate_float(value: float, name: str, min_value: Optional[float] = None,
                   max_value: Optional[float] = None) -> float:
    """
    Validate a float value.

    Args:
        value: Float value to validate
        name: Name of the parameter
        min_value: Minimum allowed value
        max_value: Maximum allowed value

    Returns:
        float: Validated float value

    Raises:
        ValidationError: If value is invalid
    """
    if value is None:
        raise ValidationError(f"{name} cannot be None")

    try:
        value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be a number")

    if min_value is not None and value < min_value:
        raise ValidationError(f"{name} must be at least {min_value}")

    if max_value is not None and value > max_value:
        raise ValidationError(f"{name} must be at most {max_value}")

    return value


def validate_boolean(value: Any, name: str) -> bool:
    """
    Validate a boolean value.

    Args:
        value: Value to validate
        name: Name of the parameter

    Returns:
        bool: Validated boolean value

    Raises:
        ValidationError: If value is invalid
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.strip().lower()
        if value in ('true', 't', 'yes', 'y', '1'):
            return True
        if value in ('false', 'f', 'no', 'n', '0'):
            return False

    if isinstance(value, (int, float)):
        if value == 1:
            return True
        if value == 0:
            return False

    raise ValidationError(f"{name} must be a boolean value")


def validate_search_query(query: str) -> str:
    """
    Validate a search query.

    Args:
        query: Search query to validate

    Returns:
        str: Validated search query

    Raises:
        ValidationError: If query is invalid
    """
    # Strip whitespace
    query = query.strip()

    # Check if query is empty
    if not query:
        raise ValidationError("Search query cannot be empty")

    # Check if query is too short
    if len(query) < 2:
        raise ValidationError("Search query must be at least 2 characters long")

    # Check if query is too long
    if len(query) > 100:
        raise ValidationError("Search query cannot be longer than 100 characters")

    return query


# Path parameter validators for FastAPI

def TickerPath(description: str = "Stock ticker symbol", example: str = DEFAULT_TICKER) -> Any:
    """
    Path parameter validator for ticker symbols.

    Args:
        description: Parameter description
        example: Example value

    Returns:
        Any: Path parameter validator
    """
    return Path(..., description=description, example=example)


def MarketPath(description: str = "Market identifier", example: str = DEFAULT_MARKET) -> Any:
    """
    Path parameter validator for market identifiers.

    Args:
        description: Parameter description
        example: Example value

    Returns:
        Any: Path parameter validator
    """
    return Path(..., description=description, example=example)


def SectorPath(description: str = "Sector identifier", example: str = DEFAULT_SECTOR) -> Any:
    """
    Path parameter validator for sector identifiers.

    Args:
        description: Parameter description
        example: Example value

    Returns:
        Any: Path parameter validator
    """
    return Path(..., description=description, example=example)


def IndustryPath(description: str = "Industry identifier", example: str = DEFAULT_INDUSTRY) -> Any:
    """
    Path parameter validator for industry identifiers.

    Args:
        description: Parameter description
        example: Example value

    Returns:
        Any: Path parameter validator
    """
    return Path(..., description=description, example=example)


def QuerySearch(description: str = "Search query", example: str = "Apple") -> Any:
    """
    Path parameter validator for search queries.

    Args:
        description: Parameter description
        example: Example value

    Returns:
        Any: Path parameter validator
    """
    return Path(..., description=description, example=example)


# Query parameter validators for FastAPI

def PeriodQuery(
        description: str = "Time period to download",
        default: str = DEFAULT_PERIOD
) -> Any:
    """
    Query parameter validator for period strings.

    Args:
        description: Parameter description
        default: Default value

    Returns:
        Any: Query parameter validator
    """
    return Query(
        default,
        description=f"{description} ({', '.join(sorted(VALID_PERIODS))})"
    )


def IntervalQuery(
        description: str = "Data interval",
        default: str = DEFAULT_INTERVAL
) -> Any:
    """
    Query parameter validator for interval strings.

    Args:
        description: Parameter description
        default: Default value

    Returns:
        Any: Query parameter validator
    """
    return Query(
        default,
        description=f"{description} ({', '.join(sorted(VALID_INTERVALS))})"
    )


def DateQuery(
        name: str,
        description: str,
        required: bool = False
) -> Any:
    """
    Query parameter validator for date strings.

    Args:
        name: Parameter name
        description: Parameter description
        required: Whether the parameter is required

    Returns:
        Any: Query parameter validator
    """
    if required:
        return Query(
            ...,
            description=f"{description} (ISO format or YYYY-MM-DD)"
        )
    else:
        return Query(
            None,
            description=f"{description} (ISO format or YYYY-MM-DD)"
        )


def FormatQuery(
        description: str = "Response format",
        default: str = "default"
) -> Any:
    """
    Query parameter validator for response format.

    Args:
        description: Parameter description
        default: Default value

    Returns:
        Any: Query parameter validator
    """
    return Query(
        default,
        description=f"{description} (default, compact, extended)"
    )


def validate_request_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate request parameters.

    Args:
        params: Parameters to validate

    Returns:
        Dict[str, Any]: Validated parameters

    Raises:
        ValidationError: If parameters are invalid
    """
    validated = {}

    # Validate ticker
    if 'ticker' in params:
        validated['ticker'] = validate_ticker(params['ticker'])

    # Validate market
    if 'market' in params:
        validated['market'] = validate_market(params['market'])

    # Validate sector
    if 'sector' in params:
        validated['sector'] = validate_sector(params['sector'])

    # Validate industry
    if 'industry' in params:
        validated['industry'] = validate_industry(params['industry'])

    # Validate period
    if 'period' in params:
        validated['period'] = validate_period(params['period'])

    # Validate interval
    if 'interval' in params:
        validated['interval'] = validate_interval(params['interval'])

    # Validate start and end dates
    if 'start' in params:
        validated['start'] = validate_date(params['start'])

    if 'end' in params:
        validated['end'] = validate_date(params['end'])

    # Validate action
    if 'action' in params:
        validated['action'] = validate_action(params['action'])

    # Validate search query
    if 'query' in params:
        validated['query'] = validate_search_query(params['query'])

    # Pass through other parameters
    for key, value in params.items():
        if key not in validated:
            validated[key] = value

    return validated