"""Info endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path
from app.models.ticker import TickerInfo
from app.models.responses import TickerInfoResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/info",
    response_model=Dict[str, Any],
    summary="Get Full Info",
    description="Returns comprehensive information about the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/info",
    cache_duration="3_months",
    attribute_name="info"
)
async def get_ticker_info(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get comprehensive information for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        Dict[str, Any]: Comprehensive ticker information
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass