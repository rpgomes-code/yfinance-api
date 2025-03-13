"""Sector historical data endpoint for YFinance API."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import Path, Depends, Query
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams, HistoryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_day
from app.services.yfinance_service import YFinanceService

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/historical",
    response_model=Dict[str, Any],
    summary="Get Sector Historical Data",
    description="Returns historical price and performance data for the specified sector, based on a representative ETF or index."
)
@performance_tracker()
@error_handler()
@cache_1_day()
@clean_yfinance_data
@response_formatter()
async def get_sector_historical(
        sector_obj=Depends(get_sector_object),
        period: str = Query("1mo",
                            description="Time period for historical data (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)"),
        interval: str = Query("1d",
                              description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)"),
        start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        include_companies: bool = Query(False, description="Include performance data for top companies in the sector"),
        company_limit: int = Query(5, ge=1, le=20, description="Number of top companies to include"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get historical performance data for a sector.

    Args:
        sector_obj: YFinance Sector object
        period: Time period for historical data
        interval: Data interval
        start: Start date
        end: End date
        include_companies: Whether to include data for top companies
        company_limit: Number of top companies to include
        query_params: Query parameters

    Returns:
        Dict[str, Any]: Historical data for the sector
    """
    # Create YFinance service
    yfinance_service = YFinanceService()

    # Get sector symbol (typically an ETF that tracks the sector)
    sector_symbol = sector_obj.symbol

    # If no sector symbol is available, use a predefined mapping
    if not sector_symbol:
        sector_etfs = {
            "energy": "XLE",
            "materials": "XLB",
            "industrials": "XLI",
            "consumer-discretionary": "XLY",
            "consumer-staples": "XLP",
            "health-care": "XLV",
            "healthcare": "XLV",
            "financials": "XLF",
            "information-technology": "XLK",
            "technology": "XLK",
            "communication-services": "XLC",
            "communications": "XLC",
            "utilities": "XLU",
            "real-estate": "XLRE",
            "real-estate-investment-trusts": "XLRE"
        }
        sector_symbol = sector_etfs.get(sector_obj.key.lower(), "SPY")  # Default to S&P 500 if no match

    # Prepare response structure
    response = {
        "sector": {
            "key": sector_obj.key,
            "name": sector_obj.name,
            "symbol": sector_symbol
        },
        "parameters": {
            "period": period,
            "interval": interval,
            "start": start,
            "end": end
        },
        "historical_data": [],
        "performance_metrics": {}
    }

    # Get historical data for the sector
    try:
        # Set up history parameters
        history_params = {
            "period": period if not (start or end) else None,
            "interval": interval,
            "auto_adjust": True
        }

        if start:
            history_params["start"] = start
        if end:
            history_params["end"] = end

        # Get historical data
        sector_history = yfinance_service.get_ticker_history(sector_symbol, **history_params)

        if not sector_history.empty:
            # Convert history to list format
            history_data = []
            for date, row in sector_history.iterrows():
                data_point = {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]) if "Open" in row else None,
                    "high": float(row["High"]) if "High" in row else None,
                    "low": float(row["Low"]) if "Low" in row else None,
                    "close": float(row["Close"]) if "Close" in row else None,
                    "volume": int(row["Volume"]) if "Volume" in row else None,
                }
                history_data.append(data_point)

            response["historical_data"] = history_data

            # Calculate performance metrics
            first_close = float(sector_history["Close"].iloc[0])
            last_close = float(sector_history["Close"].iloc[-1])
            max_close = float(sector_history["Close"].max())
            min_close = float(sector_history["Close"].min())

            # Calculate returns
            total_return = ((last_close / first_close) - 1) * 100

            # Calculate volatility (standard deviation of daily returns)
            daily_returns = sector_history["Close"].pct_change().dropna()
            volatility = float(daily_returns.std() * 100)

            # Add metrics to response
            response["performance_metrics"] = {
                "start_price": first_close,
                "end_price": last_close,
                "max_price": max_close,
                "min_price": min_close,
                "total_return": round(total_return, 2),
                "volatility": round(volatility, 2),
                "start_date": sector_history.index[0].strftime("%Y-%m-%d"),
                "end_date": sector_history.index[-1].strftime("%Y-%m-%d")
            }
    except Exception as e:
        response["error"] = f"Error retrieving historical data: {str(e)}"

    # Include top companies if requested
    if include_companies:
        try:
            # Get top companies in the sector
            top_companies = sector_obj.top_companies

            if top_companies and len(top_companies) > 0:
                # Limit to requested number
                top_companies = top_companies[:company_limit]

                # Prepare company data
                companies_data = []

                for company in top_companies:
                    company_symbol = company.get("symbol")
                    if not company_symbol:
                        continue

                    # Get historical data for company
                    try:
                        company_history = yfinance_service.get_ticker_history(company_symbol, **history_params)

                        if not company_history.empty:
                            # Calculate company returns
                            company_first_close = float(company_history["Close"].iloc[0])
                            company_last_close = float(company_history["Close"].iloc[-1])
                            company_return = ((company_last_close / company_first_close) - 1) * 100

                            companies_data.append({
                                "symbol": company_symbol,
                                "name": company.get("name", company_symbol),
                                "start_price": company_first_close,
                                "end_price": company_last_close,
                                "total_return": round(company_return, 2)
                            })
                    except Exception:
                        # Skip companies with errors
                        continue

                response["top_companies"] = companies_data
        except Exception as e:
            response["top_companies_error"] = f"Error retrieving top companies: {str(e)}"

    return response