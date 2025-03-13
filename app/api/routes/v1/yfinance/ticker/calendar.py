"""Calendar endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/calendar",
    response_model=Dict[str, Any],
    summary="Get Calendar Events",
    description="Returns upcoming calendar events like earnings and ex-dividend dates for the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/calendar",
    cache_duration="1_week",
    attribute_name="calendar"
)
async def get_ticker_calendar(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get calendar events for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        Dict[str, Any]: Calendar events
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass