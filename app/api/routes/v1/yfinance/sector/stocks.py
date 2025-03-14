"""Sector stocks endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Depends, Query

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/stocks",
    response_model=List[Dict[str, Any]],
    summary="Get All Stocks in Sector",
    description="Returns a comprehensive list of all stocks in the specified sector with optional filtering and sorting."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_sector_stocks(
        sector_obj=Depends(get_sector_object),
        min_market_cap: float = Query(None, ge=0, description="Minimum market cap in billions"),
        max_pe: float = Query(None, ge=0, description="Maximum P/E ratio"),
        min_dividend_yield: float = Query(None, ge=0, description="Minimum dividend yield (%)"),
        country: str = Query(None, description="Filter by country"),
        sort_by: str = Query("market_cap", description="Field to sort by (market_cap, price, change, name)"),
        order: str = Query("desc", description="Sort order (asc, desc)"),
        limit: int = Query(100, ge=1, le=500, description="Maximum number of stocks to return")
):
    """
    Get a comprehensive list of all stocks in the sector.

    Args:
        sector_obj: YFinance Sector object
        min_market_cap: Minimum market cap in billions
        max_pe: Maximum P/E ratio
        min_dividend_yield: Minimum dividend yield (%)
        country: Filter by country
        sort_by: Field to sort by
        order: Sort order
        limit: Maximum number of stocks to return

    Returns:
        List[Dict[str, Any]]: List of stocks in the sector
    """
    # Create YFinance service
    yfinance_service = YFinanceService()

    # First, try to get top companies as a starting point
    companies = sector_obj.top_companies or []

    # Initialize a stock list
    stocks = []

    # Process and filter companies
    for company in companies:
        # Skip if missing essential data
        if not company.get('symbol'):
            continue

        stock = {
            "symbol": company.get('symbol'),
            "name": company.get('name', company.get('symbol')),
            "price": company.get('price'),
            "change": company.get('change'),
            "percent_change": company.get('percent_change'),
            "market_cap": company.get('market_cap'),
            "sector": sector_obj.name,
            "industry": company.get('industry')
        }

        # Try to get additional data from ticker info
        try:
            symbol = company.get('symbol')
            ticker_info = yfinance_service.get_ticker_data(symbol, 'info')

            if ticker_info:
                # Add country if available
                if 'country' in ticker_info:
                    stock['country'] = ticker_info.get('country')

                # Add PE ratio if available
                if 'trailingPE' in ticker_info:
                    stock['pe_ratio'] = ticker_info.get('trailingPE')

                # Add dividend yield if available
                if 'dividendYield' in ticker_info:
                    dividend_yield = ticker_info.get('dividendYield')
                    if dividend_yield is not None:
                        stock['dividend_yield'] = dividend_yield * 100  # Convert to percentage

                # Add volume if available
                if 'volume' in ticker_info:
                    stock['volume'] = ticker_info.get('volume')
        except Exception:
            # Continue if we can't get additional data
            pass

        # Apply filters
        if min_market_cap is not None:
            if 'market_cap' not in stock or stock.get('market_cap', 0) < (min_market_cap * 1e9):
                continue

        if max_pe is not None:
            if 'pe_ratio' not in stock or stock.get('pe_ratio', float('inf')) > max_pe:
                continue

        if min_dividend_yield is not None:
            if 'dividend_yield' not in stock or stock.get('dividend_yield', 0) < min_dividend_yield:
                continue

        if country is not None:
            if 'country' not in stock or stock.get('country', '').lower() != country.lower():
                continue

        stocks.append(stock)

    # Sort the results
    reverse = order.lower() == "desc"

    if sort_by == "market_cap":
        stocks.sort(key=lambda x: x.get("market_cap", 0), reverse=reverse)
    elif sort_by == "price":
        stocks.sort(key=lambda x: x.get("price", 0), reverse=reverse)
    elif sort_by == "change":
        stocks.sort(key=lambda x: x.get("percent_change", 0), reverse=reverse)
    elif sort_by == "name":
        stocks.sort(key=lambda x: x.get("name", ""), reverse=reverse)
    elif sort_by == "pe_ratio":
        stocks.sort(key=lambda x: x.get("pe_ratio", float('inf')), reverse=reverse)
    elif sort_by == "dividend_yield":
        stocks.sort(key=lambda x: x.get("dividend_yield", 0), reverse=reverse)

    # Limit the results
    if len(stocks) > limit:
        stocks = stocks[:limit]

    return stocks