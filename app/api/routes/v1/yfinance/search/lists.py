"""Search lists endpoint for YFinance API."""
from typing import List, Dict, Any

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/lists",
    response_model=List[Dict[str, Any]],
    summary="Search Lists",
    description="Searches Yahoo Finance for lists (portfolios, watchlist, etc.) related to the specified query."
)
@search_endpoint(
    path="/{query}/lists",
    cache_duration="30_minutes",
    attribute_name="lists"
)
async def search_lists(
):
    """
    Search for lists matching a query.

    Returns:
        List[Dict[str, Any]]: List of matching lists
    """
    # Implementation is handled by the endpoint decorator
    pass