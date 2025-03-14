"""Dividends endpoint for YFinance API."""
from typing import Dict, Any

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/dividends",
    response_model=Dict[str, Any],
    summary="Get Dividends",
    description="Returns historical dividends for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/dividends",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="dividends"
)
async def get_ticker_dividends(
):
    """
    Get historical dividends for a ticker.

    Returns:
        Dict[str, Any]: Historical dividends
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass