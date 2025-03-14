"""Sector overview endpoint for YFinance API."""
from typing import Dict, Any

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint

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
):
    """
    Get a comprehensive overview of a sector.

    Returns:
        Dict[str, Any]: Sector overview information
    """
    # Implementation is handled by the endpoint decorator
    pass