"""Search all endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends
from app.models.responses import SearchResultsResponse

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_search_object, get_query_params
from app.models.common import QueryParams

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/all",
    response_model=SearchResultsResponse,
    summary="Search All",
    description="Searches Yahoo Finance for the specified query, returning results across all categories including quotes, news, lists, and research reports."
)
@search_endpoint(
    path="/{query}/all",
    cache_duration="30_minutes",
    attribute_name="all"
)
async def search_all(
        search_obj=Depends(get_search_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Search all categories for a query.

    Args:
        search_obj: YFinance Search object
        query_params: Query parameters

    Returns:
        SearchResultsResponse: Combined search results across all categories
    """
    # Implementation is handled by the endpoint decorator
    pass