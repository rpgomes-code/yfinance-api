"""Market trading hours endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Depends

from app.api.routes.v1.yfinance.base import create_market_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_month

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/trading-hours",
    response_model=Dict[str, Any],
    summary="Get Market Trading Hours",
    description="Returns the trading hours for the specified market, including regular, pre-market, and after-hours sessions."
)
@performance_tracker()
@error_handler()
@cache_1_month()
@clean_yfinance_data
@response_formatter()
async def get_market_trading_hours(
        market_obj=Depends(get_market_object)
):
    """
    Get the trading hours for a market.

    Args:
        market_obj: YFinance Market object

    Returns:
        Dict[str, Any]: Market trading hours information
    """
    # Extract trading hours from market status
    status = market_obj.status
    trading_hours = {}

    if status and 'exchangeTimezoneName' in status:
        trading_hours["timezone"] = status.get('exchangeTimezoneName')

    if status and 'regularMarketTime' in status:
        trading_hours["regular_market_time"] = status.get('regularMarketTime')

    # Extract session times if available
    if hasattr(market_obj, 'exchange_data') and market_obj.exchange_data:
        exchange_data = market_obj.exchange_data

        # Regular session
        if 'regular' in exchange_data:
            trading_hours["regular_session"] = {
                "start": exchange_data['regular'].get('start'),
                "end": exchange_data['regular'].get('end')
            }

        # Pre-market session
        if 'pre' in exchange_data:
            trading_hours["pre_market_session"] = {
                "start": exchange_data['pre'].get('start'),
                "end": exchange_data['pre'].get('end')
            }

        # Post-market session
        if 'post' in exchange_data:
            trading_hours["post_market_session"] = {
                "start": exchange_data['post'].get('start'),
                "end": exchange_data['post'].get('end')
            }

    return {
        "market": market_obj.id,
        "trading_hours": trading_hours
    }