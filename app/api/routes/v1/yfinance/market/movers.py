"""Market movers endpoint for YFinance API."""
from typing import List, Dict, Any, Optional
from enum import Enum

from fastapi import Path, Depends, Query
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_market_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object, get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_market_router()


class MoverType(str, Enum):
    """Enum for market mover types."""
    GAINERS = "gainers"
    LOSERS = "losers"
    ACTIVE = "active"


@router.get(
    "/{market}/movers",
    response_model=List[Dict[str, Any]],
    summary="Get Market Movers",
    description="Returns the top gainers, losers, or most active securities for the specified market."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_market_movers(
        market_obj=Depends(get_market_object),
        mover_type: MoverType = Query(MoverType.GAINERS, description="Type of movers to return"),
        count: int = Query(5, ge=1, le=25, description="Number of movers to return"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the top market movers (gainers, losers, or most active).

    Args:
        market_obj: YFinance Market object
        mover_type: Type of movers to return
        count: Number of movers to return
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of market movers
    """
    # Get market summary data
    market_data = market_obj.summary

    # Create YFinance service instance
    yfinance_service = YFinanceService()

    movers = []
    if market_data and 'marketSummaryResponse' in market_data:
        result = market_data['marketSummaryResponse'].get('result', [])

        # Filter to securities (excluding indices)
        securities = [item for item in result if item.get('type') != 'INDEX']

        # Sort based on mover type
        if mover_type == MoverType.GAINERS:
            securities.sort(
                key=lambda x: x.get('regularMarketChangePercent', {}).get('raw', 0),
                reverse=True
            )
        elif mover_type == MoverType.LOSERS:
            securities.sort(
                key=lambda x: x.get('regularMarketChangePercent', {}).get('raw', 0)
            )
        elif mover_type == MoverType.ACTIVE:
            securities.sort(
                key=lambda x: x.get('regularMarketVolume', {}).get('raw', 0),
                reverse=True
            )

        # Limit to requested count
        securities = securities[:count]

        # Format data
        for item in securities:
            mover_data = {
                "symbol": item.get('symbol'),
                "name": item.get('shortName') or item.get('fullName'),
                "exchange": item.get('exchange'),
                "type": item.get('type')
            }

            # Extract price data
            if 'regularMarketPrice' in item:
                mover_data["price"] = item['regularMarketPrice'].get('raw')

            if 'regularMarketChange' in item:
                mover_data["change"] = item['regularMarketChange'].get('raw')

            if 'regularMarketChangePercent' in item:
                mover_data["percent_change"] = item['regularMarketChangePercent'].get('raw')

            if 'regularMarketVolume' in item:
                mover_data["volume"] = item['regularMarketVolume'].get('raw')

            # Try to get additional data from ticker
            try:
                ticker_data = yfinance_service.get_ticker_data(item.get('symbol'), 'fast_info')
                if ticker_data:
                    mover_data["market_cap"] = ticker_data.get('market_cap')
                    mover_data["currency"] = ticker_data.get('currency')
            except Exception:
                # Ignore errors when getting additional data
                pass

            movers.append(mover_data)

    return movers