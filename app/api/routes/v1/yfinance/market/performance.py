"""Market performance endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends, Query
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_market_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_market_object, get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_market_router()


@router.get(
    "/{market}/performance",
    response_model=Dict[str, Any],
    summary="Get Market Performance",
    description="Returns performance metrics for the specified market, including key indices and their historical performance."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_market_performance(
        market_obj=Depends(get_market_object),
        period: str = Query("1mo",
                            description="Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get the performance metrics for a market.

    Args:
        market_obj: YFinance Market object
        period: Time period for historical data
        query_params: Query parameters

    Returns:
        Dict[str, Any]: Market performance metrics
    """
    # Create YFinance service instance
    yfinance_service = YFinanceService()

    # Determine key index for the market
    market_indices = {
        "US": "^GSPC",  # S&P 500
        "UK": "^FTSE",  # FTSE 100
        "JP": "^N225",  # Nikkei 225
        "HK": "^HSI",  # Hang Seng
        "DE": "^GDAXI",  # DAX
        "FR": "^FCHI",  # CAC 40
        "CA": "^GSPTSE",  # S&P/TSX Composite
        "AU": "^AXJO",  # ASX 200
    }

    market_id = market_obj.id.upper()
    index_symbol = market_indices.get(market_id)

    # Initialize response
    performance = {
        "market": market_id,
        "index": None,
        "performance": {}
    }

    # Get market status to include basic info
    status = market_obj.status
    if status:
        performance["timezone"] = status.get('exchangeTimezoneName')
        performance["currency"] = status.get('currency')
        performance["is_open"] = status.get('isOpen', False)

    # If we have an index for this market, get its performance
    if index_symbol:
        try:
            # Get index info
            index_info = yfinance_service.get_ticker_data(index_symbol, 'info')
            if index_info:
                performance["index"] = {
                    "symbol": index_symbol,
                    "name": index_info.get('shortName') or index_info.get('longName'),
                    "current_value": index_info.get('regularMarketPrice'),
                    "previous_close": index_info.get('previousClose'),
                    "change": index_info.get('regularMarketChange'),
                    "percent_change": index_info.get('regularMarketChangePercent'),
                }

            # Get historical data
            history = yfinance_service.get_ticker_history(index_symbol, period=period, interval="1d")
            if not history.empty:
                # Calculate period returns
                first_close = history['Close'].iloc[0]
                last_close = history['Close'].iloc[-1]
                period_return = ((last_close / first_close) - 1) * 100

                # Calculate year-to-date return if we have enough data
                import datetime
                current_year = datetime.datetime.now().year
                ytd_data = yfinance_service.get_ticker_history(
                    index_symbol,
                    start=f"{current_year}-01-01",
                    end=datetime.datetime.now().strftime("%Y-%m-%d"),
                    interval="1d"
                )

                ytd_return = None
                if not ytd_data.empty:
                    first_ytd_close = ytd_data['Close'].iloc[0]
                    last_ytd_close = ytd_data['Close'].iloc[-1]
                    ytd_return = ((last_ytd_close / first_ytd_close) - 1) * 100

                # Add performance metrics
                performance["performance"] = {
                    "period": period,
                    "period_return": round(period_return, 2),
                    "ytd_return": round(ytd_return, 2) if ytd_return is not None else None,
                    "start_date": history.index[0].strftime("%Y-%m-%d"),
                    "end_date": history.index[-1].strftime("%Y-%m-%d"),
                    "start_value": first_close,
                    "end_value": last_close,
                    "highest_value": history['High'].max(),
                    "lowest_value": history['Low'].min(),
                    "volatility": round(history['Close'].pct_change().std() * 100, 2),  # Standard deviation of returns
                }
        except Exception as e:
            # Log error but don't fail the entire endpoint
            performance["error"] = f"Error retrieving index data: {str(e)}"

    # Enrich with sector performance if possible
    try:
        # Get a summary of key sectors for this market
        sectors = {}

        # For US market, try to get sector performance
        if market_id == "US":
            sector_symbols = {
                "Technology": "XLK",
                "Financial": "XLF",
                "Healthcare": "XLV",
                "Consumer Cyclical": "XLY",
                "Consumer Defensive": "XLP",
                "Energy": "XLE",
                "Industrials": "XLI",
                "Basic Materials": "XLB",
                "Utilities": "XLU",
                "Real Estate": "XLRE",
                "Communication Services": "XLC"
            }

            for sector_name, sector_symbol in sector_symbols.items():
                try:
                    sector_info = yfinance_service.get_ticker_data(sector_symbol, 'info')
                    if sector_info:
                        sectors[sector_name] = {
                            "symbol": sector_symbol,
                            "current_value": sector_info.get('regularMarketPrice'),
                            "change": sector_info.get('regularMarketChange'),
                            "percent_change": sector_info.get('regularMarketChangePercent'),
                        }
                except Exception:
                    # Skip sectors with errors
                    pass

            performance["sectors"] = sectors
    except Exception:
        # Ignore sector errors
        pass

    return performance