"""Market status endpoint for YFinance API."""

from app.models.responses import MarketStatusResponse

from app.api.routes.v1.yfinance.base import create_market_router, market_endpoint

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/status",
    response_model=MarketStatusResponse,
    summary="Get Market Status",
    description="Returns the current status of the specified market, including whether it's open, trading hours, and timezone information."
)
@market_endpoint(
    path="/{market}/status",
    cache_duration="30_minutes",
    attribute_name="status"
)
async def get_market_status(
):
    """
    Get the current status of a market.

    Returns:
        MarketStatusResponse: Market status information
    """
    # Implementation is handled by the endpoint decorator
    pass