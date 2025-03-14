"""Sector industries endpoint for YFinance API."""
from typing import List, Dict, Any

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint

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
):
    """
    Get the industries within a sector.

    Returns:
        List[Dict[str, Any]]: List of industries in the sector
    """
    # Implementation is handled by the endpoint decorator
    pass