"""Sustainability endpoint for YFinance API."""
from typing import Dict, Any
from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/sustainability",
    response_model=Dict[str, Any],
    summary="Get Sustainability",
    description="Returns sustainability (ESG) scores and data for the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/sustainability",
    cache_duration="1_month",
    attribute_name="sustainability"
)
async def get_ticker_sustainability():
    """
    Get sustainability data for a ticker.

    Returns:
        Dict[str, Any]: Sustainability data
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass