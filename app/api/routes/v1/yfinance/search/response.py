"""Search response endpoint for YFinance API."""
from typing import Dict, Any

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/response",
    response_model=Dict[str, Any],
    summary="Get Raw Search Response",
    description="Returns the raw response from Yahoo Finance search for the specified query."
)
@search_endpoint(
    path="/{query}/response",
    cache_duration="30_minutes",
    attribute_name="response"
)
async def search_response(
):
    """
    Get the raw response from a search query.

    Returns:
        Dict[str, Any]: Raw search response
    """
    # Implementation is handled by the endpoint decorator
    pass