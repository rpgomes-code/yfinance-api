"""Stock splits endpoint for YFinance API."""
from typing import Dict, Any
from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/splits",
    response_model=Dict[str, Any],
    summary="Get Stock Splits",
    description="Returns historical stock splits for the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/splits",
    cache_duration="1_week",
    attribute_name="splits"
)
async def get_ticker_splits(
):
    """
    Get historical stock splits for a ticker.

    Returns:
        Dict[str, Any]: Historical stock splits
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass