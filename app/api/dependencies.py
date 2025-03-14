"""API dependencies for the YFinance API.

This module contains dependency functions that can be used in FastAPI routes
to inject common dependencies like database connections, authentication, etc.
"""
import logging
from typing import Dict, Optional

from fastapi import Path, Query, Request, HTTPException, status
import yfinance as yf

from app.core.config import settings
from app.core.exceptions import ValidationError, TickerNotFoundError
from app.models.enums import (
    ResponseFormat,
    SortOrder
)
from app.models.common import (
    HistoryParams,
    QueryParams
)
from app.services.yfinance_service import YFinanceService
from app.utils.validators import (
    validate_ticker,
    validate_market,
    validate_sector,
    validate_industry,
    validate_search_query
)

logger = logging.getLogger(__name__)

# Create service instances
yfinance_service = YFinanceService()


async def get_ticker_object(
        ticker: str = Path(..., description="Stock ticker symbol", example="AAPL")
) -> yf.Ticker:
    """
    Dependency to get a yfinance Ticker object.

    Args:
        ticker: Ticker symbol

    Returns:
        yf.Ticker: Ticker object

    Raises:
        TickerNotFoundError: If ticker is not found
        ValidationError: If ticker is invalid
    """
    try:
        # Validate ticker format
        validated_ticker = validate_ticker(ticker)

        # Get ticker object
        return yfinance_service.get_ticker(validated_ticker)
    except ValidationError as e:
        logger.warning(f"Invalid ticker format: {ticker} - {str(e)}")
        raise
    except TickerNotFoundError as e:
        logger.warning(f"Ticker not found: {ticker} - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error getting ticker object for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting ticker data: {str(e)}"
        )


async def get_market_object(
        market: str = Path(..., description="Market identifier", example="US")
) -> yf.Market:
    """
    Dependency to get a yfinance Market object.

    Args:
        market: Market identifier

    Returns:
        yf.Market: Market object

    Raises:
        ValidationError: If market is invalid
        HTTPException: If market is not found
    """
    try:
        # Validate market format
        validated_market = validate_market(market)

        # Get a market object
        return yfinance_service.get_market(validated_market)
    except ValidationError as e:
        logger.warning(f"Invalid market format: {market} - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error getting market object for {market}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting market data: {str(e)}"
        )


async def get_sector_object(
        sector: str = Path(..., description="Sector identifier", example="technology")
) -> yf.Sector:
    """
    Dependency to get a yfinance Sector object.

    Args:
        sector: Sector identifier

    Returns:
        yf.Sector: Sector object

    Raises:
        ValidationError: If sector is invalid
        HTTPException: If sector is not found
    """
    try:
        # Validate sector format
        validated_sector = validate_sector(sector)

        # Get a sector object
        return yfinance_service.get_sector(validated_sector)
    except ValidationError as e:
        logger.warning(f"Invalid sector format: {sector} - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error getting sector object for {sector}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector not found: {sector}"
        )


async def get_industry_object(
        industry: str = Path(..., description="Industry identifier", example="software")
) -> yf.Industry:
    """
    Dependency to get a yfinance Industry object.

    Args:
        industry: Industry identifier

    Returns:
        yf.Industry: Industry object

    Raises:
        ValidationError: If industry is invalid
        HTTPException: If industry is not found
    """
    try:
        # Validate industry format
        validated_industry = validate_industry(industry)

        # Get an industry object
        return yfinance_service.get_industry(validated_industry)
    except ValidationError as e:
        logger.warning(f"Invalid industry format: {industry} - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error getting industry object for {industry}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Industry not found: {industry}"
        )


async def get_search_object(
        query: str = Path(..., description="Search query", example="AAPL")
) -> yf.Search:
    """
    Dependency to get a yfinance Search object.

    Args:
        query: Search query

    Returns:
        yf.Search: Search object

    Raises:
        ValidationError: If a query is invalid
        HTTPException: If search fails
    """
    try:
        # Validate search query
        validated_query = validate_search_query(query)

        # Get a search object
        return yfinance_service.get_search(validated_query)
    except ValidationError as e:
        logger.warning(f"Invalid search query: {query} - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error getting search object for {query}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching for {query}: {str(e)}"
        )


async def get_history_params(
        period: Optional[str] = Query(None, description="Time period to download"),
        interval: str = Query("1d", description="Data interval"),
        start: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
        end: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
        prepost: bool = Query(False, description="Include pre and post market data"),
        actions: bool = Query(True, description="Include dividends and stock splits"),
        auto_adjust: bool = Query(True, description="Adjust all OHLC automatically")
) -> Dict[str, any]:
    """
    Dependency to get history parameters.

    Args:
        period: Time period
        interval: Data interval
        start: Start date
        end: End date
        prepost: Include pre- and post-market data
        actions: Include dividends and stock splits
        auto_adjust: Adjust all OHLC automatically

    Returns:
        Dict[str, any]: History parameters

    Raises:
        ValidationError: If parameters are invalid
    """
    try:
        # Create a history params model
        params = HistoryParams(
            period=period,
            interval=interval,
            start=start,
            end=end,
            prepost=prepost,
            actions=actions,
            auto_adjust=auto_adjust
        )

        # Convert to dictionary
        params_dict = params.model_dump(exclude_none=True)

        # Handle period/start/end logic
        if start or end:
            # If start or end is provided, don't use period
            if 'period' in params_dict:
                del params_dict['period']
        elif not period:
            # If neither period nor start/end is provided, use a default period
            params_dict['period'] = '1mo'

        return params_dict
    except Exception as e:
        logger.warning(f"Invalid history parameters: {str(e)}")
        raise ValidationError(f"Invalid history parameters: {str(e)}")


async def get_query_params(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(100, ge=1, le=1000, description="Items per page"),
        sort_by: Optional[str] = Query(None, description="Field to sort by"),
        sort_order: SortOrder = Query(SortOrder.ASC, description="Sort order"),
        query_format: ResponseFormat = Query(ResponseFormat.DEFAULT, description="Response format")
) -> QueryParams:
    """
    Dependency to get common query parameters.

    Args:
        page: Page number
        page_size: Items per page
        sort_by: Field to sort by
        sort_order: Sort order
        query_format: Response format

    Returns:
        QueryParams: Query parameters model
    """
    return QueryParams(
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
        format=query_format,
        filters=None
    )


def get_current_user(request: Request) -> Optional[Dict[str, any]]:
    """
    Dependency to get the current user (placeholder for authentication).

    Args:
        request: FastAPI request object

    Returns:
        Optional[Dict[str, any]]: User information or None if not authenticated
    """
    # This is a placeholder for authentication
    # In a real application; you would implement token validation, etc.
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    # Extract token
    token = auth_header.replace("Bearer ", "")

    # Validate token (placeholder)
    if token == "test_token":
        return {
            "user_id": "test_user",
            "username": "testuser",
            "scopes": ["read", "write"]
        }

    return None


def verify_api_key(request: Request) -> bool:
    """
    Dependency to verify API key (placeholder for API key validation).

    Args:
        request: FastAPI request object

    Returns:
        bool: True if API key is valid, False otherwise
    """
    # This is a placeholder for API key validation
    # In a real application; you would validate against a database, etc.
    api_key = request.headers.get("X-API-Key")
    return api_key == settings.API_KEY