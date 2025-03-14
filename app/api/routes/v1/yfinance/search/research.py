"""Search research endpoint for YFinance API."""
from typing import List, Dict, Any

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/research",
    response_model=List[Dict[str, Any]],
    summary="Search Research",
    description="Searches Yahoo Finance for research reports related to the specified query."
)
@search_endpoint(
    path="/{query}/research",
    cache_duration="30_minutes",
    attribute_name="research"
)
async def search_research(
):
    """
    Search for research reports matching a query.

    Returns:
        List[Dict[str, Any]]: List of matching research reports
    """
    # Implementation is handled by the endpoint decorator
    pass