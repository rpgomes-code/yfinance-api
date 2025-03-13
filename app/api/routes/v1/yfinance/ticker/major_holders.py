"""Major holders endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/major-holders",
    response_model=List[Dict[str, Any]],
    summary="Get Major Holders",
    description="Returns major holders for the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/major-holders",
    cache_duration="1_week",
    attribute_name="major_holders"
)
async def get_ticker_major_holders(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
):
    """
    Get major holders for a ticker.

    Args:
        ticker: The stock ticker symbol

    Returns:
        List[Dict[str, Any]]: List of major holders
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass