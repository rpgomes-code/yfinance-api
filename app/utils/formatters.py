"""Data formatting utilities for the YFinance API.

This module provides functions for formatting data for API responses,
including formatting dates, numbers, and structured data.
"""
import logging
import json
from datetime import datetime, date, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union, Hashable

import pandas as pd
import numpy as np

from app.core.utils import format_datetime, format_decimal

logger = logging.getLogger(__name__)


def format_response(
        data: Any,
        format_type: str = 'default',
        metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format API response with optional metadata.

    Args:
        data: Response data
        format_type: Format type (default, compact, extended)
        metadata: Additional metadata

    Returns:
        Dict[str, Any]: Formatted response
    """
    # Handle None data
    if data is None:
        data = []

    # Basic metadata
    response_metadata = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Add data count for lists
    if isinstance(data, list):
        response_metadata["count"] = len(data)

    # Add additional metadata if provided
    if metadata:
        response_metadata.update(metadata)

    # Format based on type
    if format_type == 'compact':
        # Compact format returns just the data
        return data
    elif format_type == 'extended':
        # Extended format includes metadata
        return {
            "data": data,
            "metadata": response_metadata
        }
    else:
        # Default format may include minimal metadata depending on data type
        if isinstance(data, list) and len(data) > 0:
            return {
                "items": data,
                "count": len(data)
            }
        return data


def format_dataframe(
        df: pd.DataFrame,
        format_type: str = 'default',
        index_col: Optional[str] = None
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Format a pandas DataFrame for API response.

    Args:
        df: DataFrame to format
        format_type: Format type (default, records, dict, split)
        index_col: Column to use as index in dict format

    Returns:
        Union[List[Dict[str, Any]], Dict[str, Any]]: Formatted DataFrame
    """
    if df.empty:
        return []

    # Reset index if it's not a default RangeIndex
    if not isinstance(df.index, pd.RangeIndex):
        df = df.reset_index()

    # Format timestamps and dates
    for col in df.select_dtypes(include=['datetime64', 'datetime64[ns]']).columns:
        df[col] = df[col].apply(lambda x: x.isoformat() if pd.notna(x) else None)

    # Format decimal values
    for col in df.select_dtypes(include=['float64', 'float32']).columns:
        df[col] = df[col].apply(lambda x: format_decimal(x) if pd.notna(x) else None)

    # Format based on type
    if format_type == 'records':
        # Records format (list of dictionaries)
        return df.to_dict(orient='records')
    elif format_type == 'dict' and index_col:
        # Dict format (dictionary with index as keys)
        if index_col in df.columns:
            return df.set_index(index_col).to_dict(orient='index')
        return df.to_dict(orient='index')
    elif format_type == 'split':
        # Split format (separate columns and values)
        split_data = df.to_dict(orient='split')
        return {
            "columns": split_data["columns"],
            "data": split_data["data"]
        }
    else:
        # Default format (records)
        return df.to_dict(orient='records')


def format_series(
        series: pd.Series,
        format_type: str = 'default',
        name: Optional[str] = None
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """
    Format a pandas Series for API response.

    Args:
        series: Series to format
        format_type: Format type (default, dict, list)
        name: Name for the series

    Returns:
        Union[Dict[str, Any], List[Dict[str, Any]]]: Formatted Series
    """
    if series.empty:
        return {}

    # Format timestamps and dates
    if pd.api.types.is_datetime64_any_dtype(series):
        series = series.apply(lambda x: x.isoformat() if pd.notna(x) else None)

    # Format decimal values
    if pd.api.types.is_float_dtype(series):
        series = series.apply(lambda x: format_decimal(x) if pd.notna(x) else None)

    # Format based on type
    if format_type == 'dict':
        # Dict format (index as keys)
        return series.to_dict()
    elif format_type == 'list':
        # List format (list of dicts with index and value)
        if name is None:
            name = series.name if series.name else 'value'

        return [{"index": i, name: v} for i, v in series.items()]
    else:
        # Default format (dict)
        return series.to_dict()


def format_ticker_actions(actions: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Format ticker actions for API response.

    Args:
        actions: DataFrame of ticker actions

    Returns:
        List[Dict[str, Any]]: Formatted ticker actions
    """
    if actions.empty:
        return []

    # Reset index to get date as a column
    actions = actions.reset_index()

    # Format each action type
    formatted_actions = []

    for _, row in actions.iterrows():
        date_str = format_datetime(row['Date']) if 'Date' in row else None

        action = {
            "date": date_str,
            "type": None,
            "value": None
        }

        # Check for dividends
        if 'Dividends' in row and row['Dividends'] > 0:
            action["type"] = "dividend"
            action["value"] = format_decimal(row['Dividends'])
            formatted_actions.append(action.copy())

        # Check for splits
        if 'Stock Splits' in row and row['Stock Splits'] != 0 and row['Stock Splits'] != 1:
            action["type"] = "split"
            action["value"] = format_decimal(row['Stock Splits'])
            formatted_actions.append(action.copy())

    return formatted_actions


def format_ticker_holders(holders: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Format ticker holders for API response.

    Args:
        holders: DataFrame of ticker holders

    Returns:
        List[Dict[str, Any]]: Formatted ticker holders
    """
    if holders.empty:
        return []

    # Format each holder
    formatted_holders = []

    for _, row in holders.iterrows():
        holder = {}

        for col in holders.columns:
            # Format column name
            col_name = col.replace(' ', '_').lower()

            # Format value based on type
            if pd.api.types.is_numeric_dtype(holders[col]):
                holder[col_name] = format_decimal(row[col])
            elif pd.api.types.is_datetime64_any_dtype(holders[col]):
                holder[col_name] = format_datetime(row[col])
            else:
                holder[col_name] = row[col]

        formatted_holders.append(holder)

    return formatted_holders


def format_ticker_financials(financials: pd.DataFrame) -> Union[
    dict[Any, Any], dict[Hashable, list[dict[str, Union[Union[float, int, None, str], Any]]]]]:
    """
    Format ticker financials for API response.

    Args:
        financials: DataFrame of ticker financials

    Returns:
        Dict[str, Any]: Formatted ticker financials
    """
    if financials.empty:
        return {}

    # Get periods (columns)
    periods = [format_datetime(period) for period in financials.columns]

    # Format each financial metric
    formatted_financials = {}

    for metric, row in financials.iterrows():
        # Create an array of values for each period
        values = []

        for period, value in zip(periods, row):
            # Format value based on type
            if pd.isna(value):
                formatted_value = None
            elif isinstance(value, (int, float)):
                formatted_value = format_decimal(value)
            else:
                formatted_value = value

            values.append({
                "period": period,
                "value": formatted_value
            })

        # Add to formatted financials
        formatted_financials[metric] = values

    return formatted_financials


def format_ticker_history(history: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Format ticker history for API response.

    Args:
        history: DataFrame of ticker history

    Returns:
        List[Dict[str, Any]]: Formatted ticker history
    """
    if history.empty:
        return []

    # Reset index to get date as a column
    history = history.reset_index()

    # Format each history record
    formatted_history = []

    for _, row in history.iterrows():
        record = {}

        for col in history.columns:
            # Format column name
            col_name = col.replace(' ', '_').lower()

            # Format value based on type
            if col == 'Date' or pd.api.types.is_datetime64_any_dtype(history[col]):
                record[col_name] = format_datetime(row[col])
            elif pd.api.types.is_numeric_dtype(history[col]):
                record[col_name] = format_decimal(row[col])
            else:
                record[col_name] = row[col]

        formatted_history.append(record)

    return formatted_history


def format_search_results(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format search results for API response.

    Args:
        results: Dictionary of search results

    Returns:
        List[Dict[str, Any]]: Formatted search results
    """
    formatted_results = []

    # Process quotes
    if 'quotes' in results and results['quotes']:
        for quote in results['quotes']:
            formatted_quote = {
                "type": "quote",
                "symbol": quote.get('symbol'),
                "name": quote.get('shortname') or quote.get('longname'),
                "exchange": quote.get('exchange'),
                "market": quote.get('market'),
                "quote_type": quote.get('quoteType'),
                "score": quote.get('score')
            }
            formatted_results.append(formatted_quote)

    # Process news
    if 'news' in results and results['news']:
        for news in results['news']:
            formatted_news = {
                "type": "news",
                "title": news.get('title'),
                "publisher": news.get('publisher'),
                "published_at": format_datetime(news.get('published_at')),
                "url": news.get('url'),
                "source": news.get('source'),
                "score": news.get('score')
            }
            formatted_results.append(formatted_news)

    return formatted_results


def format_market_status(status: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format market status for API response.

    Args:
        status: Dictionary of market status

    Returns:
        Dict[str, Any]: Formatted market status
    """
    formatted_status = {"market": status.get('market'), "region": status.get('region'),
                        "is_open": status.get('is_open', False)}

    # Basic market info

    # Trading hours
    if 'trading_hours' in status:
        hours = status['trading_hours']
        formatted_status["trading_hours"] = {
            "regular": {
                "open": hours.get('regular', {}).get('open'),
                "close": hours.get('regular', {}).get('close')
            },
            "pre": {
                "open": hours.get('pre', {}).get('open'),
                "close": hours.get('pre', {}).get('close')
            },
            "post": {
                "open": hours.get('post', {}).get('open'),
                "close": hours.get('post', {}).get('close')
            }
        }

    # Current time
    formatted_status["current_time"] = format_datetime(datetime.now(timezone.utc))

    # Market timezone
    formatted_status["timezone"] = status.get('timezone')

    return formatted_status


def format_sector_data(sector_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format sector data for API response.

    Args:
        sector_data: Dictionary of sector data

    Returns:
        Dict[str, Any]: Formatted sector data
    """
    formatted_data = {
        "name": sector_data.get('name'),
        "key": sector_data.get('key'),
        "symbol": sector_data.get('symbol'),
    }

    # Format performance data if available
    if 'performance' in sector_data:
        perf = sector_data['performance']
        formatted_data["performance"] = {
            "day": format_decimal(perf.get('day', 0)),
            "week": format_decimal(perf.get('week', 0)),
            "month": format_decimal(perf.get('month', 0)),
            "three_month": format_decimal(perf.get('three_month', 0)),
            "year": format_decimal(perf.get('year', 0)),
            "ytd": format_decimal(perf.get('ytd', 0))
        }

    # Format top companies if available
    if 'top_companies' in sector_data and sector_data['top_companies']:
        companies = []

        for company in sector_data['top_companies']:
            companies.append({
                "symbol": company.get('symbol'),
                "name": company.get('name'),
                "price": format_decimal(company.get('price', 0)),
                "change": format_decimal(company.get('change', 0)),
                "percent_change": format_decimal(company.get('percent_change', 0)),
                "market_cap": format_decimal(company.get('market_cap', 0))
            })

        formatted_data["top_companies"] = companies

    return formatted_data


def json_encoder(obj: Any) -> Any:
    """
    Custom JSON encoder for types not supported by default encoder.

    Args:
        obj: Object to encode

    Returns:
        Any: JSON encodable representation of an object
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (np.integer, np.floating, np.bool_)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if pd.isna(obj):
        return None

    # Try to convert to dict or list
    try:
        return dict(obj)
    except (TypeError, ValueError):
        try:
            return list(obj)
        except (TypeError, ValueError):
            return str(obj)


def to_json(data: Any, indent: Optional[int] = None) -> str:
    """
    Convert data to JSON string.

    Args:
        data: Data to convert
        indent: Indentation level

    Returns:
        str: JSON string
    """
    return json.dumps(data, default=json_encoder, indent=indent, ensure_ascii=False)


def to_csv(df: pd.DataFrame) -> str:
    """
    Convert DataFrame to CSV string.

    Args:
        df: DataFrame to convert

    Returns:
        str: CSV string
    """
    return df.to_csv(index=False)