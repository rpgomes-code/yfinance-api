"""Sector breakdown endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_week
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/breakdown",
    response_model=Dict[str, Any],
    summary="Get Sector Breakdown",
    description="Returns a detailed breakdown of a sector by industries, market cap, geography, and other metrics."
)
@performance_tracker()
@error_handler()
@cache_1_week()
@clean_yfinance_data
@response_formatter()
async def get_sector_breakdown(
        sector_obj=Depends(get_sector_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get detailed breakdown of a sector.

    Args:
        sector_obj: YFinance Sector object
        query_params: Query parameters

    Returns:
        Dict[str, Any]: Sector breakdown data
    """
    # Create YFinance service
    yfinance_service = YFinanceService()

    # Get sector basic info
    sector_key = sector_obj.key
    sector_name = sector_obj.name

    # Get industries in the sector
    industries = sector_obj.industries

    # Get top companies
    top_companies = sector_obj.top_companies

    # Initialize response
    breakdown = {
        "sector": {
            "key": sector_key,
            "name": sector_name
        },
        "industry_breakdown": [],
        "market_cap_breakdown": {
            "large_cap": 0,
            "mid_cap": 0,
            "small_cap": 0
        },
        "geographic_breakdown": {},
        "metrics": {}
    }

    # Process industry breakdown
    if industries:
        industry_total_market_cap = 0

        for industry in industries:
            industry_name = industry.get("name", "")
            industry_companies = industry.get("companies", [])

            # Calculate industry market cap
            industry_market_cap = sum(
                company.get("marketCap", 0) for company in industry_companies if company.get("marketCap"))
            industry_total_market_cap += industry_market_cap

            # Count companies by market cap category
            large_cap_count = sum(
                1 for company in industry_companies if company.get("marketCap", 0) > 10000000000)  # >$10B
            mid_cap_count = sum(1 for company in industry_companies if
                                2000000000 <= company.get("marketCap", 0) <= 10000000000)  # $2-10B
            small_cap_count = sum(
                1 for company in industry_companies if company.get("marketCap", 0) < 2000000000)  # <$2B

            # Add to industry breakdown
            breakdown["industry_breakdown"].append({
                "name": industry_name,
                "company_count": len(industry_companies),
                "market_cap": industry_market_cap,
                "large_cap_count": large_cap_count,
                "mid_cap_count": mid_cap_count,
                "small_cap_count": small_cap_count
            })

        # Calculate percentage of total for each industry
        if industry_total_market_cap > 0:
            for industry in breakdown["industry_breakdown"]:
                industry["market_cap_percentage"] = (industry["market_cap"] / industry_total_market_cap) * 100

    # Process market cap breakdown from top companies
    if top_companies:
        large_cap = 0
        mid_cap = 0
        small_cap = 0

        for company in top_companies:
            market_cap = company.get("marketCap", 0)

            if market_cap > 10000000000:  # Large cap: >$10B
                large_cap += 1
            elif market_cap >= 2000000000:  # Mid cap: $2-10B
                mid_cap += 1
            elif market_cap > 0:  # Small cap: <$2B
                small_cap += 1

        total_companies = large_cap + mid_cap + small_cap

        if total_companies > 0:
            breakdown["market_cap_breakdown"] = {
                "large_cap": large_cap,
                "mid_cap": mid_cap,
                "small_cap": small_cap,
                "large_cap_percentage": (large_cap / total_companies) * 100,
                "mid_cap_percentage": (mid_cap / total_companies) * 100,
                "small_cap_percentage": (small_cap / total_companies) * 100
            }

    # Process geographic breakdown from top companies
    if top_companies:
        countries = {}

        for company in top_companies:
            country = company.get("country", "Unknown")
            if country not in countries:
                countries[country] = 0

            countries[country] += 1

        total_companies = len(top_companies)
        geographic_breakdown = []

        for country, count in countries.items():
            geographic_breakdown.append({
                "country": country,
                "company_count": count,
                "percentage": (count / total_companies) * 100
            })

        # Sort by company count
        geographic_breakdown.sort(key=lambda x: x["company_count"], reverse=True)

        breakdown["geographic_breakdown"] = geographic_breakdown

    # Calculate sector metrics from top companies
    if top_companies:
        # Filter companies with required data
        pe_ratios = [company.get("trailingPE") for company in top_companies if company.get("trailingPE")]
        dividend_yields = [company.get("dividendYield", 0) * 100 for company in top_companies if
                           company.get("dividendYield") is not None]

        # Calculate averages
        avg_pe = sum(pe_ratios) / len(pe_ratios) if pe_ratios else None
        avg_dividend_yield = sum(dividend_yields) / len(dividend_yields) if dividend_yields else None

        # Add metrics
        breakdown["metrics"] = {
            "avg_pe_ratio": avg_pe,
            "avg_dividend_yield": avg_dividend_yield,
            "total_market_cap": sum(company.get("marketCap", 0) for company in top_companies),
            "company_count": len(top_companies)
        }

    return breakdown