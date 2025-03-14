"""ISIN endpoint for YFinance API."""

from app.api.routes.v1.yfinance.base import create_ticker_router, ticker_endpoint

# Create router for this endpoint
router = create_ticker_router()


@router.get(
    "/{ticker}/isin",
    response_model=str,
    summary="Get ISIN",
    description="Returns the International Securities Identification Number (ISIN) for the specified ticker."
)
@ticker_endpoint(
    path="/{ticker}/isin",
    cache_duration="3_months",
    attribute_name="isin"
)
async def get_ticker_isin(
):
    """
    Get the ISIN for a ticker.

    Returns:
        str: ISIN code
    """
    # No implementation needed - the ticker_endpoint decorator handles it
    # when attribute_name is provided
    pass