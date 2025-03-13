"""Market holidays endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path, Depends, Query
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_market_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object, get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_week

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/holidays",
    response_model=Dict[str, Any],
    summary="Get Market Holidays",
    description="Returns the trading holidays for the specified market for the current year."
)
@performance_tracker()
@error_handler()
@cache_1_week()
@clean_yfinance_data
@response_formatter()
async def get_market_holidays(
        market_obj=Depends(get_market_object),
        year: int = Query(None, description="Year to get holidays for (defaults to current year)"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the trading holidays for a market.

    Args:
        market_obj: YFinance Market object
        year: Year to get holidays for
        query_params: Query parameters

    Returns:
        Dict[str, Any]: Market holidays information
    """
    # This is a custom implementation since yfinance doesn't have a direct holidays attribute
    # We'll extract it from the market calendar

    # Get the market calendar
    calendar = market_obj.calendar

    # Filter holidays for the requested year if provided
    holidays = {}

    if calendar and hasattr(calendar, 'get'):
        # Extract holidays from calendar
        all_holidays = calendar.get('holidays', {})

        # Filter by year if requested
        if year:
            holidays = {
                date: name for date, name in all_holidays.items()
                if date.startswith(str(year))
            }
        else:
            holidays = all_holidays

    return {
        "market": market_obj.id,
        "holidays": holidays
    }