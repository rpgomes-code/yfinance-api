"""Market summary endpoint for YFinance API."""
from typing import Dict, Any

from app.api.routes.v1.yfinance.base import create_market_router, market_endpoint

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/summary",
    response_model=Dict[str, Any],  # Changed from MarketSummaryResponse
    summary="Get Market Summary",
    description="Returns a summary of the specified market, including performance metrics, major indices, and trending securities."
)
@market_endpoint(
    path="/{market}/summary",
    cache_duration="30_minutes",
    attribute_name="summary"
)
async def get_market_summary(
):
    """
    Get a summary of the market.

    Returns:
        Dict[str, Any]: Market summary information
    """
    # Implementation is handled by the endpoint decorator
    pass