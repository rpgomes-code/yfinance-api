"""Fast info endpoint for YFinance API."""
from typing import Dict, Any
from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/fast-info",
    response_model=Dict[str, Any],
    summary="Get Fast Info",
    description="Returns quickly accessible basic information for the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/fast-info",
    cache_duration="3_months",
    attribute_name="fast_info"
)
async def get_ticker_fast_info(
):
    """
    Get quickly accessible basic information for a ticker.

    Returns:
        Dict[str, Any]: Fast info data
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass