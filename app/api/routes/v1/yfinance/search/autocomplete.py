"""Search autocomplete endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Depends, Query

from app.api.routes.v1.yfinance.base import create_search_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_search_object
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_30_minutes

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/autocomplete",
    response_model=List[Dict[str, Any]],
    summary="Search Autocomplete",
    description="Returns autocomplete suggestions for the specified search query, primarily focused on security symbols and names."
)
@performance_tracker()
@error_handler()
@cache_30_minutes()
@clean_yfinance_data
@response_formatter()
async def search_autocomplete(
        search_obj=Depends(get_search_object),
        limit: int = Query(10, ge=1, le=25, description="Maximum number of results to return")
):
    """
    Get autocomplete suggestions for a search query.

    Args:
        search_obj: YFinance Search object
        limit: Maximum number of results to return

    Returns:
        List[Dict[str, Any]]: List of autocomplete suggestions
    """
    # Custom implementation since autocomplete is not directly available in yfinance

    # Start with quotes which are most relevant for autocomplete
    quotes = search_obj.quotes or []

    # Create autocomplete suggestions
    suggestions = []

    # Process quotes (stocks, ETFs, indices)
    for quote in quotes[:limit]:
        # Skip if missing key fields
        if not quote.get('symbol') or not quote.get('shortName'):
            continue

        suggestion = {
            "symbol": quote.get('symbol'),
            "name": quote.get('shortName') or quote.get('longName', ''),
            "type": quote.get('quoteType'),
            "exchange": quote.get('exchange'),
            "score": quote.get('score', 0)
        }

        suggestions.append(suggestion)

    # If we still need more suggestions, add from other categories
    if len(suggestions) < limit:
        remaining = limit - len(suggestions)

        # Try to add relevant companies from news results
        news = search_obj.news or []
        news_symbols = set()

        for item in news[:10]:  # Check top news items
            if 'ticker_symbols' in item and item['ticker_symbols']:
                for symbol in item['ticker_symbols']:
                    if symbol not in news_symbols and len(news_symbols) < remaining:
                        news_symbols.add(symbol)

        # If we found symbols in news, add basic info
        for symbol in news_symbols:
            suggestions.append({
                "symbol": symbol,
                "name": "",  # We don't have the name from news
                "type": "EQUITY",
                "exchange": "",
                "score": 0
            })

    return suggestions