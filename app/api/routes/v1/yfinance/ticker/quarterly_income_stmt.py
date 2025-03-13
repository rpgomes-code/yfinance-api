"""Quarterly income statement endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/quarterly-income-stmt",
    response_model=Dict[str, Any],
    summary="Get Quarterly Income Statement",
    description="Returns the quarterly income statement for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/quarterly-income-stmt",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="quarterly_income_stmt"
)
async def get_ticker_quarterly_income_stmt(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get the quarterly income statement for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        Dict[str, Any]: Quarterly income statement
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass