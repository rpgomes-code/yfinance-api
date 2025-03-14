"""Market exchanges endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Depends

from app.api.routes.v1.yfinance.base import create_market_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_3_months

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/exchanges",
    response_model=List[Dict[str, Any]],
    summary="Get Market Exchanges",
    description="Returns the exchanges that are part of the specified market."
)
@performance_tracker()
@error_handler()
@cache_3_months()
@clean_yfinance_data
@response_formatter()
async def get_market_exchanges(
        market_obj=Depends(get_market_object)
):
    """
    Get the exchanges for a market.

    Args:
        market_obj: YFinance Market object

    Returns:
        List[Dict[str, Any]]: List of exchanges in the market
    """
    # This is a custom implementation to extract exchanges from market data
    # YFinance doesn't directly provide this, so we'll use market-specific logic

    market_id = market_obj.id

    # Map of exchanges by market
    market_exchanges = {
        "US": [
            {"code": "NYSE", "name": "New York Stock Exchange", "country": "United States",
             "timezone": "America/New_York"},
            {"code": "NASDAQ", "name": "NASDAQ Stock Market", "country": "United States",
             "timezone": "America/New_York"},
            {"code": "AMEX", "name": "NYSE American", "country": "United States", "timezone": "America/New_York"},
            {"code": "BATS", "name": "BATS Global Markets", "country": "United States", "timezone": "America/New_York"},
            {"code": "NYSEARCA", "name": "NYSE Arca", "country": "United States", "timezone": "America/New_York"},
            {"code": "OTCMKTS", "name": "OTC Markets", "country": "United States", "timezone": "America/New_York"},
        ],
        "CA": [
            {"code": "TSX", "name": "Toronto Stock Exchange", "country": "Canada", "timezone": "America/Toronto"},
            {"code": "TSXV", "name": "TSX Venture Exchange", "country": "Canada", "timezone": "America/Toronto"},
            {"code": "CNSX", "name": "Canadian Securities Exchange", "country": "Canada",
             "timezone": "America/Toronto"},
        ],
        "UK": [
            {"code": "LSE", "name": "London Stock Exchange", "country": "United Kingdom", "timezone": "Europe/London"},
        ],
        "DE": [
            {"code": "XETRA", "name": "XETRA", "country": "Germany", "timezone": "Europe/Berlin"},
            {"code": "FSE", "name": "Frankfurt Stock Exchange", "country": "Germany", "timezone": "Europe/Berlin"},
        ],
        "FR": [
            {"code": "PAR", "name": "Euronext Paris", "country": "France", "timezone": "Europe/Paris"},
        ],
        "JP": [
            {"code": "TSE", "name": "Tokyo Stock Exchange", "country": "Japan", "timezone": "Asia/Tokyo"},
        ],
        "HK": [
            {"code": "HKSE", "name": "Hong Kong Stock Exchange", "country": "Hong Kong", "timezone": "Asia/Hong_Kong"},
        ],
        "AU": [
            {"code": "ASX", "name": "Australian Securities Exchange", "country": "Australia",
             "timezone": "Australia/Sydney"},
        ],
    }

    # Get exchanges for the requested market
    exchanges = market_exchanges.get(market_id.upper(), [])

    # Add market ID to each exchange
    for exchange in exchanges:
        exchange["market"] = market_id

    return exchanges