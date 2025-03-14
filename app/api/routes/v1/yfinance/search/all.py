"""Search all endpoint for YFinance API."""
from typing import Dict, Any

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/all",
    response_model=Dict[str, Any],  # Changed from SearchResultsResponse
    summary="Search All",
    description="Searches Yahoo Finance for the specified query, returning results across all categories including quotes, news, lists, and research reports."
)
@search_endpoint(
    path="/{query}/all",
    cache_duration="30_minutes",
    attribute_name="all"
)
async def search_all(
):
    """
    Search all categories for a query.

    Returns:
        Dict[str, Any]: Combined search results across all categories
    """
    # Implementation is handled by the endpoint decorator
    pass