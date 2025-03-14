"""Sector research reports endpoint for YFinance API."""
from typing import List, Dict, Any

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint

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
):
    """
    Get research reports for a sector.

    Returns:
        List[Dict[str, Any]]: List of research reports for the sector
    """
    # Implementation is handled by the endpoint decorator
    pass