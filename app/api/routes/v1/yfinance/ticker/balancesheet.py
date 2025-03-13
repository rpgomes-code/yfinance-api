"""Balancesheet endpoint for YFinance API (alias for balance_sheet)."""
from fastapi import Path

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint
from app.models.ticker import FinancialStatement

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/balancesheet",
    response_model=List[FinancialStatement],
    summary="Get Balance Sheet",
    description="Returns the balance sheet for the specified ticker (alias for balance-sheet). Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/balancesheet",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="balancesheet"
)
async def get_ticker_balancesheet(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get the balance sheet for a ticker (alias for balance-sheet).

    Args:
        ticker: The stock ticker symbol

    Returns:
        List of balance sheet statements
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass