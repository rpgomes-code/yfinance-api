"""Sector research reports endpoint for YFinance API."""
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
    "/{sector}/research-reports",
    response_model=List[Dict[str, Any]],
    summary="Get Sector Research Reports",
    description="Returns research reports for the specified sector."
)
@sector_endpoint(
    path="/{sector}/research-reports",
    cache_duration="1_day",
    attribute_name="research_reports"
)
async def get_sector_research_reports(
    sector_obj = Depends(get_sector_object),
    query_params: QueryParams = Depends(get_query_params)
):
    """
    Get research reports for a sector.

    Args:
        sector_obj: YFinance Sector object
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of research reports for the sector
    """
    # Implementation is handled by the endpoint decorator
    pass