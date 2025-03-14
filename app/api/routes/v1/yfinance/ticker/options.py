"""Options endpoint for YFinance API."""
from typing import List

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/options",
    response_model=List[str],
    summary="Get Options Expiration Dates",
    description="Returns available options expiration dates for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/options",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="options"
)
async def get_ticker_options(
):
    """
    Get available options expiration dates for a ticker.

    Returns:
        List[str]: List of options expiration dates
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass