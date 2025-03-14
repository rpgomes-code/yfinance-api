"""Insider transactions endpoint for YFinance API."""
from typing import List, Dict, Any
from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/insider-transactions",
    response_model=List[Dict[str, Any]],
    summary="Get Insider Transactions",
    description="Returns insider transactions for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/insider-transactions",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="insider_transactions"
)
async def get_ticker_insider_transactions(
):
    """
    Get insider transactions for a ticker.

    Returns:
        List[Dict[str, Any]]: List of insider transactions
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass