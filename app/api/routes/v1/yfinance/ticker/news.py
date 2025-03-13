"""News endpoint for YFinance API."""
from typing import List, Optional

from fastapi import Path, Query
from app.models.ticker import NewsItem
from app.models.responses import TickerNewsResponse

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/news",
    response_model=List[NewsItem],
    summary="Get News",
    description="Returns recent news articles for the specified ticker. Updated daily at midnight UTC."
)
@ticker_endpoint(
    path="/{ticker}/news",
    cache_duration="1_day",
    invalidate_at_midnight=True,
    attribute_name="news"
)
async def get_ticker_news(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL"),
        limit: Optional[int] = Query(None, ge=1, le=100, description="Maximum number of news items to return")
):
    """
    Get recent news for a ticker.

    Args:
        ticker: The stock ticker symbol
        limit: Maximum number of news items to return

    Returns:
        List[NewsItem]: List of news articles
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass