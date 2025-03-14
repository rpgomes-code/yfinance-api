"""Sector performance endpoint for YFinance API."""
from typing import Dict, Any

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
    "/{sector}/performance",
    response_model=Dict[str, Any],
    summary="Get Sector Performance",
    description="Returns detailed performance metrics for the specified sector over various time periods."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_sector_performance(
        sector_obj=Depends(get_sector_object),
        period: str = Query("1y", description="Performance period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, max)")
):
    """
    Get detailed performance metrics for a sector.

    Args:
        sector_obj: YFinance Sector object
        period: Performance period

    Returns:
        Dict[str, Any]: Performance metrics for the sector
    """
    # Create YFinance service
    yfinance_service = YFinanceService()

    # Get sector overview to extract key information
    overview = sector_obj.overview or {}
    performance = {"key": sector_obj.key, "name": sector_obj.name, "symbol": sector_obj.symbol}

    # Extract performance from overview if available
    if "performance" in overview:
        performance["metrics"] = overview.get("performance", {})
    else:
        # Default empty performance metrics structure
        performance["metrics"] = {
            "day": None,
            "week": None,
            "month": None,
            "three_month": None,
            "year": None,
            "ytd": None,
            "three_year": None,
            "five_year": None,
            "ten_year": None
        }

    # Get sector symbol for historical data if available
    sector_symbol = sector_obj.symbol

    if sector_symbol:
        try:
            # Get historical data for a specified period
            history = yfinance_service.get_ticker_history(sector_symbol, period=period, interval="1d")

            if not history.empty:
                # Calculate performance metrics
                first_close = history['Close'].iloc[0]
                last_close = history['Close'].iloc[-1]
                total_return = ((last_close / first_close) - 1) * 100

                # Calculate high/low metrics
                high = history['High'].max()
                high_date = history.loc[history['High'].idxmax()].name.strftime('%Y-%m-%d')
                low = history['Low'].min()
                low_date = history.loc[history['Low'].idxmin()].name.strftime('%Y-%m-%d')

                # Calculate volatility
                volatility = history['Close'].pct_change().std() * 100

                # Add historical performance data
                performance["historical"] = {
                    "period": period,
                    "total_return": round(total_return, 2),
                    "start_date": history.index[0].strftime('%Y-%m-%d'),
                    "end_date": history.index[-1].strftime('%Y-%m-%d'),
                    "start_value": round(first_close, 2),
                    "end_value": round(last_close, 2),
                    "high": round(high, 2),
                    "high_date": high_date,
                    "low": round(low, 2),
                    "low_date": low_date,
                    "volatility": round(volatility, 2)
                }

                # Calculate drawdowns (periods of decline from peak)
                rolling_max = history['Close'].cummax()
                drawdown = (history['Close'] / rolling_max - 1) * 100
                max_drawdown = drawdown.min()
                max_drawdown_date = history.loc[drawdown.idxmin()].name.strftime('%Y-%m-%d')

                performance["historical"]["max_drawdown"] = round(max_drawdown, 2)
                performance["historical"]["max_drawdown_date"] = max_drawdown_date

        except Exception as e:
            # Log error but continue
            performance["historical_error"] = f"Error retrieving historical data: {str(e)}"

    # Get relative performance compared to market
    try:
        # Use S&P 500 as market benchmark
        market_symbol = "^GSPC"
        market_history = yfinance_service.get_ticker_history(market_symbol, period=period, interval="1d")

        if not market_history.empty and not history.empty:
            # Calculate sector and market returns
            sector_return = ((history['Close'].iloc[-1] / history['Close'].iloc[0]) - 1) * 100
            market_return = ((market_history['Close'].iloc[-1] / market_history['Close'].iloc[0]) - 1) * 100

            # Calculate relative performance (alpha)
            relative_performance = sector_return - market_return

            performance["relative_to_market"] = {
                "benchmark": "S&P 500",
                "sector_return": round(sector_return, 2),
                "market_return": round(market_return, 2),
                "alpha": round(relative_performance, 2)
            }
    except Exception:
        # Ignore relative performance errors
        pass

    return performance