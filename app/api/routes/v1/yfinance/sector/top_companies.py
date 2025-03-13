"""Sector top companies endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path, Depends, Query
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/top-companies",
    response_model=List[Dict[str, Any]],
    summary="Get Sector Top Companies",
    description="Returns the top companies within the specified sector, sorted by market capitalization or other criteria."
)
@sector_endpoint(
    path="/{sector}/top-companies",
    cache_duration="1_week",
    attribute_name="top_companies"
)
async def get_sector_top_companies(
        sector_obj=Depends(get_sector_object),
        limit: int = Query(10, ge=1, le=100, description="Maximum number of companies to return"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the top companies within a sector.

    Args:
        sector_obj: YFinance Sector object
        limit: Maximum number of companies to return
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of top companies in the sector
    """
    # Get top companies from sector object
    companies = sector_obj.top_companies

    # Limit results if needed
    if isinstance(companies, list) and len(companies) > limit:
        companies = companies[:limit]

    return companies