"""Sector comparison endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path, Depends, Query
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/comparison",
    response_model=List[Dict[str, Any]],
    summary="Compare Sectors",
    description="Returns a comparison of all sectors with key performance metrics and statistics."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_sector_comparison(
        query_params: QueryParams = Depends(get_query_params),
        sort_by: str = Query("performance", description="Field to sort by (name, performance, market_cap, companies)"),
        order: str = Query("desc", description="Sort order (asc, desc)")
):
    """
    Compare all sectors with key metrics.

    Args:
        query_params: Query parameters
        sort_by: Field to sort by
        order: Sort order

    Returns:
        List[Dict[str, Any]]: List of sectors with comparison metrics
    """
    # Create YFinance service
    yfinance_service = YFinanceService()

    # List of major sectors
    sectors = [
        "basic_materials",
        "communication_services",
        "consumer_cyclical",
        "consumer_defensive",
        "energy",
        "financial_services",
        "healthcare",
        "industrials",
        "real_estate",
        "technology",
        "utilities"
    ]

    # Gather data for each sector
    comparison = []

    for sector_key in sectors:
        try:
            # Get sector object
            sector_obj = yfinance_service.get_sector(sector_key)

            # Basic sector info
            sector_data = {
                "key": sector_key,
                "name": sector_obj.name,
                "symbol": sector_obj.symbol
            }

            # Get overview to extract key metrics
            overview = sector_obj.overview or {}

            # Add performance if available
            if "performance" in overview:
                # Get day performance
                day_perf = overview.get("performance", {}).get("day")
                if day_perf is not None:
                    sector_data["day_performance"] = day_perf

                # Get month performance
                month_perf = overview.get("performance", {}).get("month")
                if month_perf is not None:
                    sector_data["month_performance"] = month_perf

                # Get year performance
                year_perf = overview.get("performance", {}).get("year")
                if year_perf is not None:
                    sector_data["year_performance"] = year_perf

                # For sorting, use day performance if available
                if "day_performance" in sector_data:
                    sector_data["performance"] = sector_data["day_performance"]
                elif "month_performance" in sector_data:
                    sector_data["performance"] = sector_data["month_performance"]
                else:
                    sector_data["performance"] = 0

            # Add market cap if available
            if "market_cap" in overview:
                sector_data["market_cap"] = overview.get("market_cap")

            # Add company count if available
            if "company_count" in overview:
                sector_data["company_count"] = overview.get("company_count")

            # Add P/E ratio if available
            if "average_pe" in overview:
                sector_data["pe_ratio"] = overview.get("average_pe")

            # Add dividend yield if available
            if "average_dividend_yield" in overview:
                sector_data["dividend_yield"] = overview.get("average_dividend_yield")

            comparison.append(sector_data)

        except Exception as e:
            # Log error but continue with other sectors
            print(f"Error processing sector {sector_key}: {str(e)}")

    # Sort the results
    reverse = order.lower() == "desc"

    if sort_by == "name":
        comparison.sort(key=lambda x: x.get("name", ""), reverse=reverse)
    elif sort_by == "performance":
        comparison.sort(key=lambda x: x.get("performance", 0), reverse=reverse)
    elif sort_by == "market_cap":
        comparison.sort(key=lambda x: x.get("market_cap", 0), reverse=reverse)
    elif sort_by == "companies":
        comparison.sort(key=lambda x: x.get("company_count", 0), reverse=reverse)
    elif sort_by == "pe_ratio":
        comparison.sort(key=lambda x: x.get("pe_ratio", 0), reverse=reverse)
    elif sort_by == "dividend_yield":
        comparison.sort(key=lambda x: x.get("dividend_yield", 0), reverse=reverse)

    return comparison