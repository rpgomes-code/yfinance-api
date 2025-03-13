"""Search response endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_search_router, search_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_search_object, get_query_params
from app.models.common import QueryParams

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
        search_obj=Depends(get_search_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the raw response from a search query.

    Args:
        search_obj: YFinance Search object
        query_params: Query parameters

    Returns:
        Dict[str, Any]: Raw search response
    """
    # Implementation is handled by the endpoint decorator
    pass