"""Cashflow endpoint for YFinance API (alias for cash_flow)."""
from typing import List

from fastapi import Path
from app.models.ticker import FinancialStatement
from app.models.responses import TickerCashFlowResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/cashflow",
    response_model=List[FinancialStatement],
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
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get the cash flow statement for a ticker (alias for cash-flow).

    Args:
        ticker: The stock ticker symbol

    Returns:
        List[FinancialStatement]: Cash flow statements
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass