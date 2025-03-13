"""Search research endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path, Depends
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_search_object, get_query_params
from app.models.common import QueryParams

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
        search_obj=Depends(get_search_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Search for research reports matching a query.

    Args:
        search_obj: YFinance Search object
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of matching research reports
    """
    # Implementation is handled by the endpoint decorator
    pass