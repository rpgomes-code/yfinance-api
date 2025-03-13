"""Sector industries endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path, Depends
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/industries",
    response_model=List[Dict[str, Any]],
    summary="Get Sector Industries",
    description="Returns the list of industries within the specified sector."
)
@sector_endpoint(
    path="/{sector}/industries",
    cache_duration="3_months",
    attribute_name="industries"
)
async def get_sector_industries(
        sector_obj=Depends(get_sector_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the industries within a sector.

    Args:
        sector_obj: YFinance Sector object
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of industries in the sector
    """
    # Implementation is handled by the endpoint decorator
    pass