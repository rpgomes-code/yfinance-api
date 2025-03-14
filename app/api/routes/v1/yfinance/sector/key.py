"""Sector key endpoint for YFinance API."""

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint

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
):
    """
    Get the identifier key for a sector.

    Returns:
        str: Sector key
    """
    # Implementation is handled by the endpoint decorator
    pass