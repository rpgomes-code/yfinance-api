"""Earnings dates endpoint for YFinance API."""
from typing import List, Dict, Any
from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/earnings-dates",
    response_model=List[Dict[str, Any]],
    summary="Get Earnings Dates",
    description="Returns upcoming and past earnings dates for the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/earnings-dates",
    cache_duration="1_week",
    attribute_name="earnings_dates"
)
async def get_ticker_earnings_dates(
):
    """
    Get earnings dates for a ticker.

    Returns:
        List[Dict[str, Any]]: List of earnings dates
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass