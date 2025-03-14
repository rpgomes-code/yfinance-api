"""Market summary endpoint for YFinance API."""

from app.models.responses import MarketSummaryResponse

from app.api.routes.v1.yfinance.base import create_market_router, market_endpoint

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/summary",
    response_model=MarketSummaryResponse,
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
        MarketSummaryResponse: Market summary information
    """
    # Implementation is handled by the endpoint decorator
    pass