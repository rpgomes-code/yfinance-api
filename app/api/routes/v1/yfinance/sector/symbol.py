"""Sector symbol endpoint for YFinance API."""

from app.api.routes.v1.yfinance.base import create_sector_router, sector_endpoint

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/symbol",
    response_model=str,
    summary="Get Sector Symbol",
    description="Returns the ticker symbol that represents the specified sector, typically an ETF or index."
)
@sector_endpoint(
    path="/{sector}/symbol",
    cache_duration="3_months",
    attribute_name="symbol"
)
async def get_sector_symbol(
):
    """
    Get the ticker symbol for a sector.

    Returns:
        str: Sector symbol
    """
    # Implementation is handled by the endpoint decorator
    pass