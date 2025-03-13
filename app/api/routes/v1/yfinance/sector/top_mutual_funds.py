"""Sector top mutual funds endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path, Depends, Query
from app.models.responses import SectorFundsResponse

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/top-mutual-funds",
    response_model=List[Dict[str, Any]],
    summary="Get Top Mutual Funds for Sector",
    description="Returns the top mutual funds investing in the specified sector."
)
@sector_endpoint(
    path="/{sector}/top-mutual-funds",
    cache_duration="1_week",
    attribute_name="top_mutual_funds"
)
async def get_sector_top_mutual_funds(
        sector_obj=Depends(get_sector_object),
        limit: int = Query(10, ge=1, le=50, description="Maximum number of mutual funds to return"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the top mutual funds for a sector.

    Args:
        sector_obj: YFinance Sector object
        limit: Maximum number of mutual funds to return
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of top mutual funds in the sector
    """
    # Get top mutual funds from sector object
    funds = sector_obj.top_mutual_funds

    # Limit results if needed
    if isinstance(funds, list) and len(funds) > limit:
        funds = funds[:limit]

    return funds