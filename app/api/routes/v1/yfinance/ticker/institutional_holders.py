"""Institutional holders endpoint for YFinance API."""
from typing import List, Dict, Any
from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/institutional-holders",
    response_model=List[Dict[str, Any]],
    summary="Get Institutional Holders",
    description="Returns institutional holders for the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/institutional-holders",
    cache_duration="1_week",
    attribute_name="institutional_holders"
)
async def get_ticker_institutional_holders(
):
    """
    Get institutional holders for a ticker.

    Returns:
        List[Dict[str, Any]]: List of institutional holders
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass