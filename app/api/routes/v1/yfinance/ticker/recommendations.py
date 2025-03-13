"""Recommendations endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/recommendations",
    response_model=Dict[str, Any],
    summary="Get Recommendations",
    description="Returns analyst recommendations for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/recommendations",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="recommendations"
)
async def get_ticker_recommendations(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get analyst recommendations for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        Dict[str, Any]: Analyst recommendations
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass