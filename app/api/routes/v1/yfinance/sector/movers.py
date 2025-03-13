"""Sector movers endpoint for YFinance API."""
from typing import List, Dict, Any
from enum import Enum

from fastapi import Path, Depends, Query
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day

# Create router for this endpoint
router = create_sector_router()


class MoverType(str, Enum):
    """Enum for market mover types."""
    GAINERS = "gainers"
    LOSERS = "losers"
    ACTIVE = "active"


@router.get(
    "/{sector}/movers",
    response_model=List[Dict[str, Any]],
    summary="Get Sector Movers",
    description="Returns the top gainers, losers, or most active securities within the specified sector."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_sector_movers(
        sector_obj=Depends(get_sector_object),
        mover_type: MoverType = Query(MoverType.GAINERS, description="Type of movers to return"),
        count: int = Query(5, ge=1, le=25, description="Number of movers to return"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the top market movers (gainers, losers, or most active) within a sector.

    Args:
        sector_obj: YFinance Sector object
        mover_type: Type of movers to return
        count: Number of movers to return
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of sector movers
    """
    # Get top companies in the sector
    companies = sector_obj.top_companies

    # Filter out companies with missing data
    filtered_companies = []
    for company in companies:
        # Ensure we have the required fields
        if all(field in company for field in
               ['symbol', 'shortName', 'regularMarketPrice', 'regularMarketChangePercent']):
            filtered_companies.append(company)

    # Sort based on mover type
    if mover_type == MoverType.GAINERS:
        filtered_companies.sort(
            key=lambda x: x.get('regularMarketChangePercent', 0),
            reverse=True
        )
    elif mover_type == MoverType.LOSERS:
        filtered_companies.sort(
            key=lambda x: x.get('regularMarketChangePercent', 0)
        )
    elif mover_type == MoverType.ACTIVE:
        # Sort by trading volume if available, otherwise by market cap
        if any('regularMarketVolume' in company for company in filtered_companies):
            filtered_companies.sort(
                key=lambda x: x.get('regularMarketVolume', 0),
                reverse=True
            )
        else:
            filtered_companies.sort(
                key=lambda x: x.get('marketCap', 0),
                reverse=True
            )

    # Limit to requested count
    movers = filtered_companies[:count]

    # Format the response
    formatted_movers = []
    for company in movers:
        formatted_company = {
            "symbol": company.get('symbol'),
            "name": company.get('shortName', company.get('longName', company.get('symbol'))),
            "price": company.get('regularMarketPrice'),
            "change": company.get('regularMarketChange'),
            "percent_change": company.get('regularMarketChangePercent'),
            "volume": company.get('regularMarketVolume'),
            "market_cap": company.get('marketCap')
        }
        formatted_movers.append(formatted_company)

    return formatted_movers