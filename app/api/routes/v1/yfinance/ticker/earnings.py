"""Earnings endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path
from app.models.responses import TickerEarningsResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/earnings",
    response_model=Dict[str, Any],
    summary="Get Earnings",
    description="Returns historical earnings data for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/earnings",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="earnings"
)
async def get_ticker_earnings(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get historical earnings data for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        Dict[str, Any]: Historical earnings data
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass