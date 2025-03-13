"""Market summary endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends
from app.models.responses import MarketSummaryResponse

from app.api.routes.v1.yfinance.base import create_market_router, market_endpoint
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object, get_query_params
from app.models.common import QueryParams

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/summary",
    response_model=MarketSummaryResponse,
    summary="Get Market Summary",
    description="Returns a summary of the specified market, including performance metrics, major indices, and trending securities."
)
@market_endpoint(
    path="/{market}/summary",
    cache_duration="30_minutes",
    attribute_name="summary"
)
async def get_market_summary(
        market_obj=Depends(get_market_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get a summary of a market.

    Args:
        market_obj: YFinance Market object
        query_params: Query parameters

    Returns:
        MarketSummaryResponse: Market summary information
    """
    # Implementation is handled by the endpoint decorator
    pass