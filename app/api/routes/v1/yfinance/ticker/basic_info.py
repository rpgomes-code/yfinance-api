"""Basic info endpoint for YFinance API."""
from fastapi import Path

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint
from app.models.ticker import TickerBasicInfo

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/basic-info",
    response_model=TickerBasicInfo,
    summary="Get Basic Info",
    description="Returns basic information about the specified ticker, including name, sector, industry, and market data."
)
@ticker_endpoint(
    path="/{ticker}/basic-info",
    cache_duration="3_months",
    attribute_name="basic_info"
)
async def get_ticker_basic_info(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get basic information for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        TickerBasicInfo: Basic ticker information
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass