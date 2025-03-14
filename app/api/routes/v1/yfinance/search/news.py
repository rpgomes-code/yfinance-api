"""Search news endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Depends, Query

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint
from app.api.dependencies import get_search_object

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/news",
    response_model=List[Dict[str, Any]],
    summary="Search News",
    description="Searches Yahoo Finance for news articles related to the specified query."
)
@search_endpoint(
    path="/{query}/news",
    cache_duration="30_minutes",
    attribute_name="news"
)
async def search_news(
        search_obj=Depends(get_search_object),
        limit: int = Query(10, ge=1, le=50, description="Maximum number of results to return")
):
    """
    Search for news articles matching a query.

    Args:
        search_obj: YFinance Search object
        limit: Maximum number of results to return

    Returns:
        List[Dict[str, Any]]: List of matching news articles
    """
    # Get news from a search object
    news = search_obj.news

    # Limit results if needed
    if isinstance(news, list) and len(news) > limit:
        news = news[:limit]

    return news