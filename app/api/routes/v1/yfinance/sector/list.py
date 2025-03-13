"""Sector list endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Depends
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_3_months
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/list",
    response_model=List[Dict[str, Any]],
    summary="List All Sectors",
    description="Returns a list of all available sectors in Yahoo Finance with their keys, names, and symbols."
)
@performance_tracker()
@error_handler()
@cache_3_months()
@clean_yfinance_data
@response_formatter()
async def list_sectors(
        query_params: QueryParams = Depends(get_query_params)
):
    """
    List all available sectors.

    Args:
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of sectors
    """
    # YFinance doesn't provide a direct method to list all sectors,
    # so we'll use a predefined list of the standard GICS sectors

    sectors = [
        {
            "key": "energy",
            "name": "Energy",
            "symbol": "XLE",  # Energy Select Sector SPDR Fund
            "description": "Companies involved in exploration, production, and distribution of oil, gas, and other forms of energy."
        },
        {
            "key": "materials",
            "name": "Materials",
            "symbol": "XLB",  # Materials Select Sector SPDR Fund
            "description": "Companies involved in the discovery, development, and processing of raw materials."
        },
        {
            "key": "industrials",
            "name": "Industrials",
            "symbol": "XLI",  # Industrial Select Sector SPDR Fund
            "description": "Companies that produce goods used in construction and manufacturing."
        },
        {
            "key": "consumer-discretionary",
            "name": "Consumer Discretionary",
            "symbol": "XLY",  # Consumer Discretionary Select Sector SPDR Fund
            "description": "Companies that provide non-essential goods and services."
        },
        {
            "key": "consumer-staples",
            "name": "Consumer Staples",
            "symbol": "XLP",  # Consumer Staples Select Sector SPDR Fund
            "description": "Companies that provide essential products and services."
        },
        {
            "key": "health-care",
            "name": "Health Care",
            "symbol": "XLV",  # Health Care Select Sector SPDR Fund
            "description": "Companies that provide medical services, manufacture medical equipment, or drugs."
        },
        {
            "key": "financials",
            "name": "Financials",
            "symbol": "XLF",  # Financial Select Sector SPDR Fund
            "description": "Companies that provide financial services to commercial and retail customers."
        },
        {
            "key": "information-technology",
            "name": "Information Technology",
            "symbol": "XLK",  # Technology Select Sector SPDR Fund
            "description": "Companies involved in technology and technology services."
        },
        {
            "key": "communication-services",
            "name": "Communication Services",
            "symbol": "XLC",  # Communication Services Select Sector SPDR Fund
            "description": "Companies involved in communication and entertainment content and distribution."
        },
        {
            "key": "utilities",
            "name": "Utilities",
            "symbol": "XLU",  # Utilities Select Sector SPDR Fund
            "description": "Companies that provide electricity, gas, and water."
        },
        {
            "key": "real-estate",
            "name": "Real Estate",
            "symbol": "XLRE",  # Real Estate Select Sector SPDR Fund
            "description": "Companies involved in real estate development and management."
        }
    ]

    # Enrich with market cap data if possible
    yfinance_service = YFinanceService()
    for sector in sectors:
        try:
            # Try to get market cap from sector ETF
            ticker_data = yfinance_service.get_ticker_data(sector["symbol"], "fast_info")
            if ticker_data and "last_price" in ticker_data:
                sector["etf_price"] = ticker_data.get("last_price")
        except Exception:
            # Skip if we can't get the data
            pass

    # Apply sorting if requested
    sort_by = query_params.sort_by
    if sort_by:
        reverse = query_params.sort_order == "desc"

        if sort_by == "name":
            sectors.sort(key=lambda x: x["name"], reverse=reverse)
        elif sort_by == "key":
            sectors.sort(key=lambda x: x["key"], reverse=reverse)
        elif sort_by == "etf_price" and any("etf_price" in sector for sector in sectors):
            # Sort by ETF price if available, otherwise keep original order
            sectors.sort(
                key=lambda x: x.get("etf_price", 0) if "etf_price" in x else float("-inf"),
                reverse=reverse
            )

    return sectors