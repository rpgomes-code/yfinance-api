"""Cashflow endpoint for YFinance API (alias for cash_flow)."""
from typing import List, Dict, Any

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/cashflow",
    response_model=List[Dict[str, Any]],  # Changed from List[FinancialStatement]
    summary="Get Cash Flow",
    description="Returns the cash flow statement for the specified ticker (alias for cash-flow). Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/cashflow",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="cashflow"
)
async def get_ticker_cashflow(
):
    """
    Get the cash flow statement for a ticker (alias for cash-flow).

    Returns:
        List[Dict[str, Any]]: Cash flow statements
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass