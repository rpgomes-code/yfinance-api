"""Sector rankings endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Query

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/rankings",
    response_model=List[Dict[str, Any]],
    summary="Get Sector Rankings",
    description="Returns performance rankings of all sectors based on specified metric."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_sector_rankings(
        metric: str = Query("performance",
                            description="Ranking metric (performance, market_cap, dividend_yield, pe_ratio, volume)"),
        period: str = Query("1d", description="Time period for performance metrics (1d, 5d, 1mo, 3mo, 6mo, 1y, ytd)"),
        order: str = Query("desc", description="Sort order (asc, desc)")
):
    """
    Get rankings of all sectors by specified metric.

    Args:
        metric: Ranking metric
        period: Time period for performance metrics
        order: Sort order
    Returns:
        List[Dict[str, Any]]: Ranked list of sectors
    """
    # Create YFinance service
    yfinance_service = YFinanceService()

    # Sector ETFs mapping for getting sector data
    sector_etfs = {
        "Technology": {"symbol": "XLK", "name": "Technology"},
        "Financial": {"symbol": "XLF", "name": "Financial Services"},
        "Healthcare": {"symbol": "XLV", "name": "Healthcare"},
        "Consumer Cyclical": {"symbol": "XLY", "name": "Consumer Cyclical"},
        "Consumer Defensive": {"symbol": "XLP", "name": "Consumer Defensive"},
        "Energy": {"symbol": "XLE", "name": "Energy"},
        "Industrials": {"symbol": "XLI", "name": "Industrials"},
        "Basic Materials": {"symbol": "XLB", "name": "Basic Materials"},
        "Utilities": {"symbol": "XLU", "name": "Utilities"},
        "Real Estate": {"symbol": "XLRE", "name": "Real Estate"},
        "Communication Services": {"symbol": "XLC", "name": "Communication Services"}
    }

    # Collect data for each sector
    sectors_data = []

    for sector_name, info in sector_etfs.items():
        try:
            etf_symbol = info["symbol"]

            # Get ETF data as proxy for sector
            ticker_info = yfinance_service.get_ticker_data(etf_symbol, "info")

            if not ticker_info:
                continue

            # Get historical data for performance calculation
            if metric == "performance":
                history = yfinance_service.get_ticker_history(etf_symbol, period=period)

                if history.empty:
                    continue

                # Calculate performance
                first_close = history['Close'].iloc[0]
                last_close = history['Close'].iloc[-1]
                performance = ((last_close / first_close) - 1) * 100

                sector_data = {
                    "name": sector_name,
                    "performance": round(performance, 2),
                    "period": period,
                    "start_price": round(first_close, 2),
                    "current_price": round(last_close, 2),
                    "symbol": etf_symbol
                }
            else:
                # Extract other metrics
                sector_data = {
                    "name": sector_name,
                    "symbol": etf_symbol,
                    "price": ticker_info.get("regularMarketPrice"),
                    "market_cap": ticker_info.get("marketCap"),
                    "volume": ticker_info.get("volume"),
                    "pe_ratio": ticker_info.get("trailingPE"),
                    "dividend_yield": ticker_info.get("dividendYield", 0) * 100 if ticker_info.get(
                        "dividendYield") else 0,
                }

            sectors_data.append(sector_data)

        except Exception:
            # Skip sectors with errors
            continue

    # Sort by selected metric
    if metric == "performance":
        sort_key = "performance"
    elif metric in ["market_cap", "volume", "pe_ratio", "dividend_yield"]:
        sort_key = metric
    else:
        sort_key = "performance"

    # Apply sorting
    reverse_order = order.lower() == "desc"
    sorted_sectors = sorted(
        sectors_data,
        key=lambda x: x.get(sort_key, 0) if x.get(sort_key) is not None else 0,
        reverse=reverse_order
    )

    # Add rank
    for i, sector in enumerate(sorted_sectors):
        sector["rank"] = i + 1

    return sorted_sectors