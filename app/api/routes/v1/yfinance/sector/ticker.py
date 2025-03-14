"""Sector ticker endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Depends

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_3_months
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/ticker",
    response_model=Dict[str, Any],
    summary="Get Sector Ticker Information",
    description="Returns detailed ticker information for the specified sector's representative ticker symbol."
)
@performance_tracker()
@error_handler()
@cache_3_months()
@clean_yfinance_data
@response_formatter()
async def get_sector_ticker(
        sector_obj=Depends(get_sector_object)
):
    """
    Get detailed ticker information for a sector's representative symbol.

    Args:
        sector_obj: YFinance Sector object

    Returns:
        Dict[str, Any]: Ticker information for the sector
    """
    # Custom implementation since we need to create a ticker from the sector symbol

    # Get the sector symbol
    symbol = sector_obj.symbol

    # If no symbol is available, return error info
    if not symbol:
        return {
            "error": "No representative ticker symbol available for this sector",
            "sector": sector_obj.name
        }

    # Create service
    yfinance_service = YFinanceService()

    # Get ticker information
    ticker_info = yfinance_service.get_ticker_data(symbol, 'info')

    # Add sector context
    result = {
        "sector": {
            "key": sector_obj.key,
            "name": sector_obj.name
        },
        "ticker": symbol,
        "info": ticker_info
    }

    return result