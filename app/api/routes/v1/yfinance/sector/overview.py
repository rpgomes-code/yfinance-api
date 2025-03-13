"""Sector overview endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends
from app.models.responses import SectorOverviewResponse

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/overview",
    response_model=Dict[str, Any],
    summary="Get Sector Overview",
    description="Returns a comprehensive overview of the specified sector, including performance metrics, industry breakdown, and key statistics."
)
@sector_endpoint(
    path="/{sector}/overview",
    cache_duration="1_week",
    attribute_name="overview"
)
async def get_sector_overview(
        sector_obj=Depends(get_sector_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get a comprehensive overview of a sector.

    Args:
        sector_obj: YFinance Sector object
        query_params: Query parameters

    Returns:
        Dict[str, Any]: Sector overview information
    """
    # Implementation is handled by the endpoint decorator
    pass