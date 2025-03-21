"""Sector top ETFs endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Depends, Query

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint
from app.api.dependencies import get_sector_object

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/top-etfs",
    response_model=List[Dict[str, Any]],
    summary="Get Top ETFs for Sector",
    description="Returns the top ETFs tracking the specified sector."
)
@sector_endpoint(
    path="/{sector}/top-etfs",
    cache_duration="1_week",
    attribute_name="top_etfs"
)
async def get_sector_top_etfs(
        sector_obj=Depends(get_sector_object),
        limit: int = Query(10, ge=1, le=50, description="Maximum number of ETFs to return")
):
    """
    Get the top ETFs for a sector.

    Args:
        sector_obj: YFinance Sector object
        limit: Maximum number of ETFs to return

    Returns:
        List[Dict[str, Any]]: List of top ETFs in the sector
    """
    # Get top ETFs from a sector object
    etfs = sector_obj.top_etfs

    # Limit results if needed
    if isinstance(etfs, list) and len(etfs) > limit:
        etfs = etfs[:limit]

    return etfs