"""Analyst price targets endpoint for YFinance API."""
from typing import List

from app.models.ticker import AnalystPriceTarget

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/analyst-price-targets",
    response_model=List[AnalystPriceTarget],
    summary="Get Analyst Price Targets",
    description="Returns analyst price targets for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/analyst-price-targets",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="analyst_price_targets"
)
async def get_ticker_analyst_price_targets(
):
    """
    Get analyst price targets for a ticker.

    Returns:
        List[AnalystPriceTarget]: List of analyst price targets
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass