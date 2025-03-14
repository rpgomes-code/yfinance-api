"""Cash flow endpoint for YFinance API."""
from typing import List

from app.models.ticker import FinancialStatement

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/cash-flow",
    response_model=List[FinancialStatement],
    summary="Get Cash Flow",
    description="Returns the cash flow statement for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/cash-flow",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="cash_flow"
)
async def get_ticker_cash_flow(
):
    """
    Get the cash flow statement for a ticker.

    Returns:
        List[FinancialStatement]: Cash flow statements
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass