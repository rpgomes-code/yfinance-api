"""Market status endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends
from app.models.responses import MarketStatusResponse

from app.api.routes.v1.yfinance.base import create_market_router, market_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object, get_query_params
from app.models.common import QueryParams

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/status",
    response_model=MarketStatusResponse,
    summary="Get Market Status",
    description="Returns the current status of the specified market, including whether it's open, trading hours, and timezone information."
)
@market_endpoint(
    path="/{market}/status",
    cache_duration="30_minutes",
    attribute_name="status"
)
async def get_market_status(
        market_obj=Depends(get_market_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the current status of a market.

    Args:
        market_obj: YFinance Market object
        query_params: Query parameters

    Returns:
        MarketStatusResponse: Market status information
    """
    # Implementation is handled by the endpoint decorator
    pass