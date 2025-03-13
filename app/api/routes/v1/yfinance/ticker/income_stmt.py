"""Income statement endpoint for YFinance API."""
from typing import List

from fastapi import Path
from app.models.ticker import FinancialStatement
from app.models.responses import TickerIncomeStatementResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/income-stmt",
    response_model=List[FinancialStatement],
    summary="Get Income Statement",
    description="Returns the income statement for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/income-stmt",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="income_stmt"
)
async def get_ticker_income_stmt(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get the income statement for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        List[FinancialStatement]: Income statements
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass