import functools
import inspect
from typing import Any, Callable
import pandas as pd
import numpy as np

def clean_yfinance_data(func: Callable) -> Callable:
    """
    Decorator that processes data returned by yfinance methods to ensure
    they are JSON serializable.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Call the original function
            result = await func(*args, **kwargs) if inspect.iscoroutinefunction(func) else func(*args, **kwargs)

            # Process the result to make it JSON serializable
            cleaned_result = process_yfinance_output(result)
            return cleaned_result

        except Exception as e:
            # Handle any exceptions
            return {"error": f"Error processing data: {str(e)}"}

    return wrapper


def process_yfinance_output(data: Any) -> Any:
    """
    Recursively process yfinance output data to make it JSON serializable.
    Handles DataFrames, Series, NumPy types, NaN values, etc.
    """
    # Handle None
    if data is None:
        return None

    # Handle pandas DataFrame
    if isinstance(data, pd.DataFrame):
        if data.empty:
            return []
        # Reset index to make it a regular column
        df = data.reset_index()
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

    # Handle pandas Timestamp
    if isinstance(data, pd.Timestamp):
        return data.isoformat()

    # Handle NumPy data types
    if isinstance(data, (np.integer, np.floating, np.bool_)):
        return data.item()

    # Handle NaN, infinity
    if isinstance(data, (float, np.float64, np.float32)) and (np.isnan(data) or np.isinf(data)):
        return None

    # Handle lists and dictionaries recursively
    if isinstance(data, list):
        return [process_yfinance_output(item) for item in data]
    if isinstance(data, dict):
        return {str(k): process_yfinance_output(v) for k, v in data.items()}

    # Return other types as is
    return data