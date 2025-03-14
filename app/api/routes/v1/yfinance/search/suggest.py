"""Search suggest endpoint for YFinance API."""
from typing import Dict, Any
import re

from fastapi import Depends, Query

from app.api.routes.v1.yfinance.base import create_search_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_search_object
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_search_router()


@router.get(
    "/{query}/suggest",
    response_model=Dict[str, Any],
    summary="Get Search Suggestions",
    description="Returns personalized search suggestions for the specified query, including related symbols and topics."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def search_suggest(
        search_obj=Depends(get_search_object),
        limit: int = Query(5, ge=1, le=20, description="Maximum number of results per category")
):
    """
    Get personalized search suggestions.

    Args:
        search_obj: YFinance Search object
        limit: Maximum number of results per category

    Returns:
        Dict[str, Any]: Search suggestions in multiple categories
    """
    # Custom implementation for search suggestions
    # This is different from autocomplete as it provides more context and categorization

    # Create YFinance service
    YFinanceService()

    # Get search results
    quotes = search_obj.quotes or []
    news = search_obj.news or []

    # Get query string
    query_str = getattr(search_obj, 'query', '')

    # Initialize response structure
    suggestions = {
        "query": query_str,
        "securities": [],
        "related_queries": [],
        "news_topics": [],
        "sectors": []
    }

    # Process securities (quotes)
    for quote in quotes[:limit]:
        if not quote.get('symbol'):
            continue

        security = {
            "symbol": quote.get('symbol'),
            "name": quote.get('shortName') or quote.get('longName', ''),
            "type": quote.get('quoteType'),
            "exchange": quote.get('exchange'),
            "score": quote.get('score', 0)
        }
        suggestions["securities"].append(security)

    # Identify sectors if any securities were found
    sectors = {}
    for quote in quotes:
        sector = quote.get('sector')
        if sector and sector not in sectors and len(sectors) < limit:
            sectors[sector] = {
                "name": sector,
                "related_symbol": quote.get('symbol')
            }

    suggestions["sectors"] = list(sectors.values())

    # Generate related queries based on the current query
    query_str = query_str.strip().lower()

    # Add common modifiers to generate related queries
    modifiers = ["stock", "price", "news", "earnings", "dividend", "forecast", "analysis"]
    related = []

    # If a query is a symbol, suggest common lookups
    if re.match(r'^[A-Za-z]{1,5}$', query_str):
        for modifier in modifiers:
            if len(related) < limit:
                related.append(f"{query_str} {modifier}")
    # Otherwise, try to extract topics
    else:
        words = query_str.split()
        if len(words) > 1:
            # Suggest variations by removing a word
            for i in range(len(words)):
                if len(related) < limit:
                    suggested_query = " ".join(words[:i] + words[i + 1:])
                    if suggested_query and suggested_query != query_str:
                        related.append(suggested_query)

        # Add some general financial terms if we don't have enough
        common_terms = [
            "stocks", "etf", "index", "market", "investing", "trading", "finance", "dividend", "earnings"
        ]

        for term in common_terms:
            if term not in query_str and len(related) < limit:
                related.append(f"{query_str} {term}")

    suggestions["related_queries"] = related

    # Extract news topics
    topics = {}
    for item in news[:10]:
        # Try to extract topics from news titles
        title = item.get('title', '')
        if title:
            # Use a simple approach - extract capitalized phrases
            capitalized_phrases = re.findall(r'\b([A-Z][a-z]+(?: [A-Z][a-z]+)*)\b', title)
            for phrase in capitalized_phrases:
                if len(phrase.split()) > 1 and phrase not in topics and len(topics) < limit:
                    topics[phrase] = {
                        "topic": phrase,
                        "source": "news",
                        "title": title[:50] + "..." if len(title) > 50 else title
                    }

    suggestions["news_topics"] = list(topics.values())

    return suggestions