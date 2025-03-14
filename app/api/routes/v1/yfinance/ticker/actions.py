"""Actions endpoint for YFinance API."""
from typing import List

from app.models.ticker import TickerAction

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/actions",
    response_model=List[TickerAction],
    summary="Get Actions",
    description="Returns corporate actions (dividends and splits) for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/actions",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="actions"
)
async def get_ticker_actions(
):
    """
    Get corporate actions for a ticker.

    Returns:
        List[TickerAction]: List of corporate actions
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass