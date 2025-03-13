"""Search trending endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path, Depends, Query
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_search_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/trending",
    response_model=List[Dict[str, Any]],
    summary="Get Trending Searches",
    description="Returns trending search topics and symbols on Yahoo Finance."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def search_trending(
        count: int = Query(10, ge=1, le=25, description="Maximum number of results to return"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get trending search topics and symbols.

    Args:
        count: Maximum number of results to return
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of trending searches
    """
    # Custom implementation for trending searches
    # YFinance doesn't have a direct API for this, so we'll return popular tickers

    # Create YFinance service
    yfinance_service = YFinanceService()

    # Popular tickers by market/category
    popular_tickers = [
        # Major US indices
        "^GSPC",  # S&P 500
        "^DJI",  # Dow Jones Industrial Average
        "^IXIC",  # NASDAQ Composite
        "^RUT",  # Russell 2000

        # Major tech stocks
        "AAPL",  # Apple
        "MSFT",  # Microsoft
        "GOOGL",  # Alphabet (Google)
        "AMZN",  # Amazon
        "META",  # Meta (Facebook)
        "TSLA",  # Tesla
        "NVDA",  # NVIDIA

        # Other popular stocks
        "JPM",  # JPMorgan Chase
        "BAC",  # Bank of America
        "WMT",  # Walmart
        "JNJ",  # Johnson & Johnson
        "PG",  # Procter & Gamble
        "V",  # Visa
        "DIS",  # Disney
        "KO",  # Coca-Cola
        "MCD",  # McDonald's

        # Popular ETFs
        "SPY",  # SPDR S&P 500 ETF
        "QQQ",  # Invesco QQQ Trust (NASDAQ-100)
        "VTI",  # Vanguard Total Stock Market ETF
        "GLD",  # SPDR Gold Shares
        "IWM",  # iShares Russell 2000 ETF
    ]

    # Limit to requested count
    popular_tickers = popular_tickers[:count]

    # Get additional info for these tickers
    trending = []

    for symbol in popular_tickers:
        try:
            # Get basic info
            ticker_info = yfinance_service.get_ticker_data(symbol, 'fast_info')

            if ticker_info:
                trending_item = {
                    "symbol": symbol,
                    "name": ticker_info.get('name', symbol),
                    "price": ticker_info.get('price'),
                    "change": ticker_info.get('day_change'),
                    "percent_change": ticker_info.get('day_percent_change'),
                    "volume": ticker_info.get('volume')
                }
                trending.append(trending_item)

        except Exception:
            # Skip tickers that fail
            continue

    return trending