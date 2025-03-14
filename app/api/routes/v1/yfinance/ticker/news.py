"""News endpoint for YFinance API."""
from typing import List
from app.models.ticker import NewsItem

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
async def get_ticker_news():
    """
    Get recent news for a ticker.

    Returns:
        List[NewsItem]: List of news articles
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass