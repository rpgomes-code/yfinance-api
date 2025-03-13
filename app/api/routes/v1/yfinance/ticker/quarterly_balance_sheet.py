"""Quarterly balance sheet endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/quarterly-balance-sheet",
    response_model=Dict[str, Any],
    summary="Get Quarterly Balance Sheet",
    description="Returns the quarterly balance sheet for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/quarterly-balance-sheet",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="quarterly_balance_sheet"
)
async def get_ticker_quarterly_balance_sheet(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get the quarterly balance sheet for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        Dict[str, Any]: Quarterly balance sheet
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass