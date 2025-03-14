"""Search quotes endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Depends, Query

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint
from app.api.dependencies import get_search_object

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/quotes",
    response_model=List[Dict[str, Any]],
    summary="Search Quotes",
    description="Searches Yahoo Finance for securities (stocks, ETFs, indices, etc.) matching the specified query."
)
@search_endpoint(
    path="/{query}/quotes",
    cache_duration="30_minutes",
    attribute_name="quotes"
)
async def search_quotes(
        search_obj=Depends(get_search_object),
        limit: int = Query(20, ge=1, le=100, description="Maximum number of results to return")
):
    """
    Search for quotes matching a query.

    Args:
        search_obj: YFinance Search object
        limit: Maximum number of results to return

    Returns:
        List[Dict[str, Any]]: List of matching securities
    """
    # Get quotes from a search object
    quotes = search_obj.quotes

    # Limit results if needed
    if isinstance(quotes, list) and len(quotes) > limit:
        quotes = quotes[:limit]

    return quotes