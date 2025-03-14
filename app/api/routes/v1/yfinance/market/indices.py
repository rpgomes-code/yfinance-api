"""Market indices endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Depends

from app.api.routes.v1.yfinance.base import create_market_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/indices",
    response_model=List[Dict[str, Any]],
    summary="Get Market Indices",
    description="Returns the major indices for the specified market with their current values and performance metrics."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_market_indices(
        market_obj=Depends(get_market_object)
):
    """
    Get the major indices for a market.

    Args:
        market_obj: YFinance Market object

    Returns:
        List[Dict[str, Any]]: List of market indices
    """
    # This is a custom implementation to extract indices from market data
    market_data = market_obj.summary

    indices = []
    if market_data and 'marketSummaryResponse' in market_data:
        result = market_data['marketSummaryResponse'].get('result', [])

        for item in result:
            # Filter to include only indices (type "INDEX")
            if item.get('type') == 'INDEX':
                index_data = {
                    "symbol": item.get('symbol'),
                    "name": item.get('shortName') or item.get('fullName'),
                    "exchange": item.get('exchange'),
                    "type": item.get('type')
                }

                # Extract price data
                if 'regularMarketPrice' in item:
                    index_data["price"] = item['regularMarketPrice'].get('raw')

                if 'regularMarketChange' in item:
                    index_data["change"] = item['regularMarketChange'].get('raw')

                if 'regularMarketChangePercent' in item:
                    index_data["percent_change"] = item['regularMarketChangePercent'].get('raw')

                if 'regularMarketPreviousClose' in item:
                    index_data["previous_close"] = item['regularMarketPreviousClose'].get('raw')

                indices.append(index_data)

    return indices