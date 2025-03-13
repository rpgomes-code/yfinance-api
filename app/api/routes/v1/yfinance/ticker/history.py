"""History endpoint for YFinance API."""
from typing import Dict, Any, Optional

from fastapi import Path, Query, Depends
from app.models.common import HistoryParams
from app.models.responses import TickerHistoryResponse

from app.api.routes.v1.yfinance.base import create_ticker_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/history",
    response_model=Dict[str, Any],
    summary="Get Historical Data",
    description="Returns historical price and volume data for the specified ticker."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_ticker_history(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL"),
        period: Optional[str] = Query(None, description="Time period to download (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
        interval: str = Query("1d", description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)"),
        start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        prepost: bool = Query(False, description="Include pre and post market data"),
        actions: bool = Query(True, description="Include dividends and stock splits"),
        auto_adjust: bool = Query(True, description="Adjust all OHLC automatically")
):
    """
    Get historical data for a ticker.

    Args:
        ticker: Stock ticker symbol
        period: Time period to download
        interval: Data interval
        start: Start date
        end: End date
        prepost: Include pre and post market data
        actions: Include dividends and stock splits
        auto_adjust: Adjust all OHLC automatically

    Returns:
        Dict[str, Any]: Historical price and volume data
    """
    # Create YFinance service
    yfinance_service = YFinanceService()

    # Set up history parameters
    history_params = {
        "interval": interval,
        "prepost": prepost,
        "actions": actions,
        "auto_adjust": auto_adjust
    }

    # If start and end are provided, use them instead of period
    if start or end:
        if start:
            history_params["start"] = start
        if end:
            history_params["end"] = end
    else:
        # If neither start nor end is provided, use period
        history_params["period"] = period or "1mo"

    # Get historical data
    history = yfinance_service.get_ticker_history(ticker, **history_params)

    # Convert to dictionary and process
    result = {
        "ticker": ticker,
        "parameters": {
            "period": period,
            "interval": interval,
            "start": start,
            "end": end,
            "prepost": prepost,
            "actions": actions,
            "auto_adjust": auto_adjust
        },
        "data": []
    }

    if not history.empty:
        # Convert to list of records
        for date, row in history.iterrows():
            data_point = {
                "date": date.strftime("%Y-%m-%d"),
                "open": float(row["Open"]) if "Open" in row else None,
                "high": float(row["High"]) if "High" in row else None,
                "low": float(row["Low"]) if "Low" in row else None,
                "close": float(row["Close"]) if "Close" in row else None,
                "volume": int(row["Volume"]) if "Volume" in row else None
            }

            # Add dividends and splits if available
            if "Dividends" in row and row["Dividends"] > 0:
                data_point["dividends"] = float(row["Dividends"])

            if "Stock Splits" in row and row["Stock Splits"] != 0:
                data_point["stock_splits"] = float(row["Stock Splits"])

            result["data"].append(data_point)

    return result