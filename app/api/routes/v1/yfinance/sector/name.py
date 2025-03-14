"""Sector name endpoint for YFinance API."""
from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/name",
    response_model=str,
    summary="Get Sector Name",
    description="Returns the display name for the specified sector."
)
@sector_endpoint(
    path="/{sector}/name",
    cache_duration="3_months",
    attribute_name="name"
)
async def get_sector_name(
):
    """
    Get the display name for a sector.

    Returns:
        str: Sector name
    """
    # Implementation is handled by the endpoint decorator
    pass