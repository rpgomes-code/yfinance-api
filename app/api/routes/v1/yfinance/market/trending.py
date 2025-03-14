"""Market trending endpoint for YFinance API."""
from typing import List, Dict, Any, Optional
from enum import Enum

from fastapi import Depends, Query

from app.api.routes.v1.yfinance.base import create_market_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_30_minutes
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_market_router()


class TrendingCategory(str, Enum):
    """Enum for trending categories."""
    GAINERS = "gainers"
    LOSERS = "losers"
    ACTIVE = "active"
    VOLUME = "volume"
    MOMENTUM = "momentum"


@router.get(
    "/{market}/trending",
    response_model=List[Dict[str, Any]],
    summary="Get Market Trending Securities",
    description="Returns trending securities in the specified market based on different metrics like price movement, volume, and momentum."
)
@performance_tracker()
@error_handler()
@cache_30_minutes()
@clean_yfinance_data
@response_formatter()
async def get_market_trending(
        market_obj=Depends(get_market_object),
        category: TrendingCategory = Query(TrendingCategory.GAINERS, description="Trending category to return"),
        count: int = Query(10, ge=1, le=50, description="Number of securities to return"),
        min_price: Optional[float] = Query(None, description="Minimum price filter"),
        min_volume: Optional[int] = Query(None, description="Minimum volume filter")
):
    """
    Get trending securities in the market.

    Args:
        market_obj: YFinance Market object
        category: Trending category (gainers, losers, active, volume, momentum)
        count: Number of securities to return
        min_price: Minimum price filter
        min_volume: Minimum volume filter

    Returns:
        List[Dict[str, Any]]: List of trending securities
    """
    # Create YFinance service instance
    yfinance_service = YFinanceService()

    # Get market data for the specified market
    market_data = market_obj.summary

    # Initialize result
    trending_securities = []

    if market_data and 'marketSummaryResponse' in market_data:
        result = market_data['marketSummaryResponse'].get('result', [])

        # Filter to only include securities (exclude indices)
        securities = [item for item in result if item.get('type') != 'INDEX']

        # Apply min price filter if specified
        if min_price is not None:
            securities = [item for item in securities
                          if item.get('regularMarketPrice', {}).get('raw', 0) >= min_price]

        # Apply min volume filter if specified
        if min_volume is not None:
            securities = [item for item in securities
                          if item.get('regularMarketVolume', {}).get('raw', 0) >= min_volume]

        # Sort based on trending category
        if category == TrendingCategory.GAINERS:
            # Sort by percentage gain
            securities.sort(
                key=lambda x: x.get('regularMarketChangePercent', {}).get('raw', 0),
                reverse=True
            )
        elif category == TrendingCategory.LOSERS:
            # Sort by percentage loss
            securities.sort(
                key=lambda x: x.get('regularMarketChangePercent', {}).get('raw', 0)
            )
        elif category in [TrendingCategory.ACTIVE, TrendingCategory.VOLUME]:
            # Sort by volume
            securities.sort(
                key=lambda x: x.get('regularMarketVolume', {}).get('raw', 0),
                reverse=True
            )
        elif category == TrendingCategory.MOMENTUM:
            # For momentum, we'll use a combination of volume and price change
            # This is a simple heuristic: volume * abs(percent change)
            securities.sort(
                key=lambda x: (
                    x.get('regularMarketVolume', {}).get('raw', 0) *
                    abs(x.get('regularMarketChangePercent', {}).get('raw', 0))
                ),
                reverse=True
            )

        # Limit to requested count
        securities = securities[:count]

        # Format the data for response
        for item in securities:
            security = {
                "symbol": item.get('symbol'),
                "name": item.get('shortName') or item.get('longName'),
                "exchange": item.get('exchange'),
                "type": item.get('quoteType'),
                "market": market_obj.id
            }

            # Add price data
            if 'regularMarketPrice' in item:
                security["price"] = item['regularMarketPrice'].get('raw')

            if 'regularMarketChange' in item:
                security["change"] = item['regularMarketChange'].get('raw')

            if 'regularMarketChangePercent' in item:
                security["percent_change"] = item['regularMarketChangePercent'].get('raw')

            if 'regularMarketVolume' in item:
                security["volume"] = item['regularMarketVolume'].get('raw')

            if 'regularMarketPreviousClose' in item:
                security["previous_close"] = item['regularMarketPreviousClose'].get('raw')

            # Try to get additional data for each security
            try:
                ticker_data = yfinance_service.get_ticker_data(item.get('symbol'), 'fast_info')
                if ticker_data:
                    security["market_cap"] = ticker_data.get('market_cap')
                    security["sector"] = ticker_data.get('sector')
                    security["industry"] = ticker_data.get('industry')
            except Exception:
                # Ignore errors when fetching additional data
                pass

            trending_securities.append(security)

    # Add a category field to know what type of trending data was requested
    for security in trending_securities:
        security["trending_category"] = category

    return trending_securities