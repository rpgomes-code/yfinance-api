"""Sector trends endpoint for YFinance API."""
from typing import Dict, Any, List

import pandas as pd
from fastapi import Path, Depends, Query
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
    "/{sector}/trends",
    response_model=Dict[str, Any],
    summary="Get Sector Trends",
    description="Returns trend analysis for the specified sector, including historical performance, momentum indicators, and relative strength compared to the broader market."
)
@performance_tracker()
@error_handler()
@cache_1_week()
@clean_yfinance_data
@response_formatter()
async def get_sector_trends(
        sector_obj=Depends(get_sector_object),
        period: str = Query("1y", description="Time period for trend analysis (1mo, 3mo, 6mo, 1y, 2y, 5y)"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get trend analysis for a sector.

    Args:
        sector_obj: YFinance Sector object
        period: Time period for trend analysis
        query_params: Query parameters

    Returns:
        Dict[str, Any]: Sector trend analysis
    """
    # Create YFinance service
    yfinance_service = YFinanceService()

    # Get sector symbol
    sector_symbol = sector_obj.symbol

    # Initialize response
    trends = {
        "sector": sector_obj.name,
        "period": period,
        "trends": {}
    }

    # Get sector performance
    try:
        if sector_symbol:
            # Get historical data for the sector
            sector_history = yfinance_service.get_ticker_history(sector_symbol, period=period)

            if not sector_history.empty:
                # Calculate trend metrics

                # Overall trend
                first_close = sector_history['Close'].iloc[0]
                last_close = sector_history['Close'].iloc[-1]
                overall_change = ((last_close / first_close) - 1) * 100

                # Moving averages
                ma_50 = sector_history['Close'].rolling(window=50).mean().iloc[-1]
                ma_200 = sector_history['Close'].rolling(window=200).mean().iloc[-1]

                # Momentum (rate of change)
                momentum_1m = ((last_close / sector_history['Close'].iloc[-22]) - 1) * 100 if len(
                    sector_history) >= 22 else None
                momentum_3m = ((last_close / sector_history['Close'].iloc[-66]) - 1) * 100 if len(
                    sector_history) >= 66 else None

                # Volatility (standard deviation of returns)
                volatility = sector_history['Close'].pct_change().std() * 100

                # Add trend metrics to response
                trends["trends"] = {
                    "overall_change_percent": round(overall_change, 2),
                    "above_ma_50": last_close > ma_50,
                    "above_ma_200": last_close > ma_200,
                    "ma_50_value": round(ma_50, 2) if not pd.isna(ma_50) else None,
                    "ma_200_value": round(ma_200, 2) if not pd.isna(ma_200) else None,
                    "momentum_1m": round(momentum_1m, 2) if momentum_1m is not None else None,
                    "momentum_3m": round(momentum_3m, 2) if momentum_3m is not None else None,
                    "volatility": round(volatility, 2),
                    "current_price": round(last_close, 2),
                    "start_price": round(first_close, 2),
                    "start_date": sector_history.index[0].strftime("%Y-%m-%d"),
                    "end_date": sector_history.index[-1].strftime("%Y-%m-%d"),
                }

                # Get market benchmark for comparison (S&P 500)
                market_history = yfinance_service.get_ticker_history("^GSPC", period=period)

                if not market_history.empty:
                    market_first_close = market_history['Close'].iloc[0]
                    market_last_close = market_history['Close'].iloc[-1]
                    market_change = ((market_last_close / market_first_close) - 1) * 100

                    # Relative strength vs market
                    relative_strength = overall_change - market_change

                    # Add market comparison
                    trends["market_comparison"] = {
                        "market_change_percent": round(market_change, 2),
                        "relative_strength": round(relative_strength, 2),
                        "outperforming_market": relative_strength > 0
                    }
    except Exception as e:
        trends["error"] = f"Error calculating trends: {str(e)}"

    # Try to get trend data from top companies
    try:
        top_companies = sector_obj.top_companies

        if isinstance(top_companies, list) and len(top_companies) > 0:
            # Calculate sector trend based on top companies
            advancing_count = 0
            declining_count = 0
            neutral_count = 0

            for company in top_companies:
                price_change = company.get('regularMarketChangePercent', 0)

                if price_change > 0.5:  # More than 0.5% up
                    advancing_count += 1
                elif price_change < -0.5:  # More than 0.5% down
                    declining_count += 1
                else:  # Between -0.5% and 0.5%
                    neutral_count += 1

            # Add breadth indicators
            trends["breadth"] = {
                "advancing_count": advancing_count,
                "declining_count": declining_count,
                "neutral_count": neutral_count,
                "advance_decline_ratio": round(advancing_count / max(declining_count, 1), 2),
                "market_breadth": "bullish" if advancing_count > declining_count else "bearish" if declining_count > advancing_count else "neutral"
            }
    except Exception:
        # Ignore errors in breadth calculation
        pass

    return trends