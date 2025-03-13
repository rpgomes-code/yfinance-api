"""Sector key endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/key",
    response_model=str,
    summary="Get Sector Key",
    description="Returns the identifier key for the specified sector."
)
@sector_endpoint(
    path="/{sector}/key",
    cache_duration="3_months",
    attribute_name="key"
)
async def get_sector_key(
        sector_obj=Depends(get_sector_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the identifier key for a sector.

    Args:
        sector_obj: YFinance Sector object
        query_params: Query parameters

    Returns:
        str: Sector key
    """
    # Implementation is handled by the endpoint decorator
    pass