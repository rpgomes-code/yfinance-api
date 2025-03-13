"""Data manager for processing YFinance output.

This module provides utilities for processing and transforming data
returned by YFinance to ensure it is JSON serializable and well-formatted.
"""
import functools
import inspect
import logging
from datetime import datetime, date
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from app.core.exceptions import YFinanceError, TickerNotFoundError
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)


def clean_yfinance_data(func: Callable) -> Callable:
    """
    Decorator that processes data returned by yfinance methods to ensure
    they are JSON serializable.

    Args:
        func: The function to decorate

    Returns:
        Callable: Decorated function
    """
    metrics_service = MetricsService()

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        """Async wrapper for coroutine functions."""
        # Extract identifier from path parameters if present
        identifier = _extract_identifier(kwargs)

        try:
            # Call the original function
            result = await func(*args, **kwargs)

            # Check for empty results that might indicate a not found condition
            if _is_empty_result(result):
                if identifier:
                    raise TickerNotFoundError(identifier)
                return []

            # Process the result to make it JSON serializable
            cleaned_result = process_yfinance_output(result)
            return cleaned_result

        except TickerNotFoundError:
            # Re-raise ticker not found errors
            raise
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error processing yfinance data: {str(e)}")

            # Check for common yfinance errors
            if "No data found" in str(e) and identifier:
                raise TickerNotFoundError(identifier)

            # For other errors, provide a structured error response
            raise YFinanceError(str(e))

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        """Sync wrapper for regular functions."""
        # Extract identifier from path parameters if present
        identifier = _extract_identifier(kwargs)

        try:
            # Call the original function
            result = func(*args, **kwargs)

            # Check for empty results that might indicate a not found condition
            if _is_empty_result(result):
                if identifier:
                    raise TickerNotFoundError(identifier)
                return []

            # Process the result to make it JSON serializable
            cleaned_result = process_yfinance_output(result)
            return cleaned_result

        except TickerNotFoundError:
            # Re-raise ticker not found errors
            raise
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error processing yfinance data: {str(e)}")

            # Check for common yfinance errors
            if "No data found" in str(e) and identifier:
                raise TickerNotFoundError(identifier)

            # For other errors, provide a structured error response
            raise YFinanceError(str(e))

    # Return the appropriate wrapper based on whether the function is async
    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def _extract_identifier(kwargs: Dict[str, Any]) -> Optional[str]:
    """
    Extract identifier from path parameters.

    Args:
        kwargs: Keyword arguments

    Returns:
        Optional[str]: Identifier or None
    """
    if 'ticker' in kwargs:
        return kwargs['ticker']
    elif 'market' in kwargs:
        return kwargs['market']
    elif 'sector' in kwargs:
        return kwargs['sector']
    elif 'industry' in kwargs:
        return kwargs['industry']
    elif 'query' in kwargs:
        return kwargs['query']
    return None


def _is_empty_result(result: Any) -> bool:
    """
    Check if a result is empty.

    Args:
        result: Result to check

    Returns:
        bool: True if empty, False otherwise
    """
    if result is None:
        return True

    if isinstance(result, (pd.DataFrame, pd.Series)) and result.empty:
        return True

    if isinstance(result, (list, dict, str)) and not result:
        return True

    return False


def process_yfinance_output(data: Any) -> Any:
    """
    Recursively process yfinance output data to make it JSON serializable.
    Handles DataFrames, Series, NumPy types, NaN values, etc.

    Args:
        data: Data to process

    Returns:
        Any: Processed data that is JSON serializable
    """
    # Handle None
    if data is None:
        return None

    # Handle pandas DataFrame
    if isinstance(data, pd.DataFrame):
        if data.empty:
            return []
        # Reset index to make it a regular column if it's not a RangeIndex
        if not isinstance(data.index, pd.RangeIndex):
            df = data.reset_index()
        else:
            df = data.copy()

        # Convert to records and process each value
        records = []
        for _, row in df.iterrows():
            record = {}
            for col_name, value in row.items():
                record[str(col_name)] = process_yfinance_output(value)
            records.append(record)
        return records

    # Handle pandas Series
    if isinstance(data, pd.Series):
        result = {}
        for idx, value in data.items():
            result[str(idx)] = process_yfinance_output(value)
        return result

    # Handle pandas Timestamp or datetime
    if isinstance(data, (pd.Timestamp, datetime)):
        return data.isoformat()

    # Handle date
    if isinstance(data, date):
        return data.isoformat()

    # Handle NumPy data types
    if isinstance(data, (np.integer, np.floating, np.bool_)):
        return data.item()

    # Handle NaN, infinity
    if isinstance(data, (float, np.float64, np.float32)) and (np.isnan(data) or np.isinf(data)):
        return None

    # Handle NumPy arrays
    if isinstance(data, np.ndarray):
        return [process_yfinance_output(item) for item in data]

    # Handle lists and dictionaries recursively
    if isinstance(data, list):
        return [process_yfinance_output(item) for item in data]
    if isinstance(data, dict):
        return {str(k): process_yfinance_output(v) for k, v in data.items()}

    # Handle sets
    if isinstance(data, set):
        return [process_yfinance_output(item) for item in data]

    # Return other types as is
    return data


def format_yfinance_response(data: Any, response_format: str = 'default') -> Any:
    """
    Format YFinance response according to specified format.

    Args:
        data: Data to format
        response_format: Format type (default, compact, extended)

    Returns:
        Any: Formatted data
    """
    # Process data to ensure it's JSON serializable
    processed_data = process_yfinance_output(data)

    # Apply formatting based on format type
    if response_format == 'compact':
        return _compact_format(processed_data)
    elif response_format == 'extended':
        return _extended_format(processed_data)
    else:
        return processed_data


def _compact_format(data: Any) -> Any:
    """
    Apply compact formatting to data.

    Args:
        data: Data to format

    Returns:
        Any: Compactly formatted data
    """
    if isinstance(data, list) and data and isinstance(data[0], dict):
        # For list of records, keep only essential fields
        essential_fields = _get_essential_fields(data[0])
        return [{k: v for k, v in item.items() if k in essential_fields} for item in data]

    if isinstance(data, dict):
        # For dictionaries, keep only essential fields
        essential_fields = _get_essential_fields(data)
        return {k: v for k, v in data.items() if k in essential_fields}

    return data


def _extended_format(data: Any) -> Any:
    """
    Apply extended formatting to data.

    Args:
        data: Data to format

    Returns:
        Any: Extended formatted data with metadata
    """
    if not data:
        return {
            "data": data,
            "metadata": {
                "count": 0,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }

    if isinstance(data, list):
        return {
            "data": data,
            "metadata": {
                "count": len(data),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }

    if isinstance(data, dict):
        return {
            "data": data,
            "metadata": {
                "fields": list(data.keys()),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }

    return {
        "data": data,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "type": type(data).__name__,
        }
    }


def _get_essential_fields(data: Dict[str, Any]) -> List[str]:
    """
    Get essential fields from data based on field names.

    Args:
        data: Data dictionary

    Returns:
        List[str]: List of essential field names
    """
    # Define field importance based on common patterns
    high_importance = {
        'symbol', 'ticker', 'name', 'date', 'period', 'value', 'price',
        'open', 'high', 'low', 'close', 'volume', 'market_cap',
        'sector', 'industry', 'exchange'
    }

    medium_importance = {
        'currency', 'description', 'summary', 'recommendation',
        'target', 'estimate', 'growth', 'revenue', 'earnings', 'eps',
        'pe_ratio', 'dividend', 'yield', 'beta', 'change', 'percent_change'
    }

    # Identify essential fields
    essential_fields = set()

    for field in data.keys():
        field_lower = field.lower()

        # Check if field name contains high importance keywords
        if any(keyword in field_lower for keyword in high_importance):
            essential_fields.add(field)
            continue

        # Check if field name contains medium importance keywords
        if any(keyword in field_lower for keyword in medium_importance):
            essential_fields.add(field)
            continue

    # If we didn't identify enough fields, add some based on data types
    if len(essential_fields) < min(5, len(data)):
        for field, value in data.items():
            if field in essential_fields:
                continue

            # Prioritize simpler data types
            if isinstance(value, (str, int, float, bool)) and not isinstance(value, (list, dict)):
                essential_fields.add(field)

                if len(essential_fields) >= min(5, len(data)):
                    break

    # Return list of fields, preserving original order
    return [field for field in data.keys() if field in essential_fields]