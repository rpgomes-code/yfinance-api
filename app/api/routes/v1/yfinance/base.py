"""Base module for YFinance routes.

This module provides common functionality and factory functions for creating
YFinance route endpoints, reducing duplication across endpoint modules.
"""
import functools
import logging
from typing import Callable, Optional, TypeVar, Dict, Any, Union, List

from fastapi import APIRouter, Depends

from app.core.cache import (
    cache_30_minutes,
    cache_1_day,
    cache_1_week,
    cache_1_month,
    cache_3_months
)
from app.core.constants import (
    ENDPOINT_CACHE_DURATIONS,
    INVALIDATE_AT_MIDNIGHT
)
from app.api.dependencies import (
    get_ticker_object,
    get_market_object,
    get_search_object,
    get_sector_object,
    get_industry_object
)
from app.services.yfinance_service import YFinanceService
from app.utils.decorators import (
    error_handler,
    performance_tracker,
    response_formatter
)
from app.utils.yfinance_data_manager import clean_yfinance_data

# Setup logger
logger = logging.getLogger(__name__)

# Create service instance
yfinance_service = YFinanceService()

# Type for response models
ResponseModel = TypeVar('ResponseModel')

def create_ticker_router() -> APIRouter:
    """
    Create a router for ticker endpoints with standard configuration.

    Returns:
        APIRouter: Configured router
    """
    return APIRouter(prefix="/ticker", tags=["ticker"])

def create_market_router() -> APIRouter:
    """
    Create a router for market endpoints with standard configuration.

    Returns:
        APIRouter: Configured router
    """
    return APIRouter(prefix="/market", tags=["market"])

def create_search_router() -> APIRouter:
    """
    Create a router for search endpoints with standard configuration.

    Returns:
        APIRouter: Configured router
    """
    return APIRouter(prefix="/search", tags=["search"])

def create_sector_router() -> APIRouter:
    """
    Create a router for sector endpoints with standard configuration.

    Returns:
        APIRouter: Configured router
    """
    return APIRouter(prefix="/sector", tags=["sector"])

def create_industry_router() -> APIRouter:
    """
    Create a router for industry endpoints with standard configuration.

    Returns:
        APIRouter: Configured router
    """
    return APIRouter(prefix="/industry", tags=["industry"])

def get_cache_decorator(
    attribute_name: str,
    invalidate_at_midnight: bool = False
) -> Callable:
    """
    Get the appropriate cache decorator for an attribute.

    Args:
        attribute_name: YFinance attribute name
        invalidate_at_midnight: Whether to invalidate at midnight

    Returns:
        Callable: Cache decorator
    """
    # Get cache duration from constants
    cache_duration = ENDPOINT_CACHE_DURATIONS.get(attribute_name, "1_day")

    # Force invalidate at midnight for specific attributes
    if attribute_name in INVALIDATE_AT_MIDNIGHT:
        invalidate_at_midnight = True

    # Select appropriate cache decorator
    if cache_duration == "30_minutes":
        return cache_30_minutes()
    elif cache_duration == "1_day":
        return cache_1_day(invalidate_at_midnight=invalidate_at_midnight)
    elif cache_duration == "1_week":
        return cache_1_week()
    elif cache_duration == "1_month":
        return cache_1_month()
    elif cache_duration == "3_months":
        return cache_3_months()
    else:
        # Default to 1 day
        return cache_1_day(invalidate_at_midnight=invalidate_at_midnight)

def ticker_endpoint(
    attribute_name: Optional[str] = None,
    invalidate_at_midnight: bool = True,
    cache_duration: Optional[str] = None,
    path: Optional[str] = None
) -> Callable:
    """
    Factory function to create a standard ticker endpoint.

    Args:
        attribute_name: YFinance attribute name
        invalidate_at_midnight: Whether to invalidate cache at midnight
        cache_duration: Cache duration string (overrides default based on attribute)
        path: Endpoint path (ignored but accepted to maintain compatibility)

    Returns:
        Callable: Decorator function for endpoint
    """
    def decorator(func: Callable) -> Callable:
        # Apply standard decorators
        decorated = performance_tracker()(func)
        decorated = error_handler()(decorated)

        # Apply caching if attribute name is provided
        if attribute_name:
            if cache_duration:
                # Use provided cache duration
                if cache_duration == "30_minutes":
                    decorated = cache_30_minutes()(decorated)
                elif cache_duration == "1_day":
                    decorated = cache_1_day(invalidate_at_midnight=invalidate_at_midnight)(decorated)
                elif cache_duration == "1_week":
                    decorated = cache_1_week()(decorated)
                elif cache_duration == "1_month":
                    decorated = cache_1_month()(decorated)
                elif cache_duration == "3_months":
                    decorated = cache_3_months()(decorated)
            else:
                # Use cache duration based on attribute name
                decorated = get_cache_decorator(
                    attribute_name,
                    invalidate_at_midnight
                )(decorated)

        # Apply data cleaning
        decorated = clean_yfinance_data(decorated)

        # Apply response formatting
        decorated = response_formatter()(decorated)

        # If attribute name is provided, create a standard implementation
        if attribute_name:
            @functools.wraps(func)
            async def implementation(
                ticker_obj = Depends(get_ticker_object)
            ):
                """
                Standard implementation for ticker endpoints.

                Args:
                    ticker_obj: YFinance Ticker object

                Returns:
                    Any: Ticker attribute data
                """
                # Get the data from the ticker object
                return getattr(ticker_obj, attribute_name)

            # Use the standard implementation
            return implementation

        # Otherwise return the decorated function
        return decorated

    return decorator

def market_endpoint(
    cache_duration: str = "30_minutes",
    attribute_name: Optional[str] = None,
    path: Optional[str] = None
) -> Callable:
    """
    Factory function to create a standard market endpoint.

    Args:
        cache_duration: Cache duration
        attribute_name: YFinance attribute name
        path: Endpoint path (ignored but accepted to maintain compatibility)

    Returns:
        Callable: Decorator function for endpoint
    """
    def decorator(func: Callable) -> Callable:
        # Apply standard decorators
        decorated = performance_tracker()(func)
        decorated = error_handler()(decorated)

        # Apply caching
        if cache_duration == "30_minutes":
            decorated = cache_30_minutes()(decorated)
        elif cache_duration == "1_day":
            decorated = cache_1_day()(decorated)
        elif cache_duration == "1_week":
            decorated = cache_1_week()(decorated)

        # Apply data cleaning
        decorated = clean_yfinance_data(decorated)

        # Apply response formatting
        decorated = response_formatter()(decorated)

        # If attribute name is provided, create a standard implementation
        if attribute_name:
            @functools.wraps(func)
            async def implementation(
                market_obj = Depends(get_market_object),
            ):
                """
                Standard implementation for market endpoints.

                Args:
                    market_obj: YFinance Market object

                Returns:
                    Any: Market attribute data
                """
                # Get the data from the market object
                return getattr(market_obj, attribute_name)

            # Use the standard implementation
            return implementation

        # Otherwise return the decorated function
        return decorated

    return decorator

def search_endpoint(
    cache_duration: str = "30_minutes",
    attribute_name: Optional[str] = None,
    path: Optional[str] = None
) -> Callable:
    """
    Factory function to create a standard search endpoint.

    Args:
        cache_duration: Cache duration
        attribute_name: YFinance attribute name
        path: Endpoint path (ignored but accepted to maintain compatibility)

    Returns:
        Callable: Decorator function for endpoint
    """
    def decorator(func: Callable) -> Callable:
        # Apply standard decorators
        decorated = performance_tracker()(func)
        decorated = error_handler()(decorated)

        # Apply caching
        if cache_duration == "30_minutes":
            decorated = cache_30_minutes()(decorated)
        elif cache_duration == "1_day":
            decorated = cache_1_day()(decorated)

        # Apply data cleaning
        decorated = clean_yfinance_data(decorated)

        # Apply response formatting
        decorated = response_formatter()(decorated)

        # If attribute name is provided, create a standard implementation
        if attribute_name:
            @functools.wraps(func)
            async def implementation(
                search_obj = Depends(get_search_object),
            ):
                """
                Standard implementation for search endpoints.

                Args:
                    search_obj: YFinance Search object

                Returns:
                    Any: Search attribute data
                """
                # Get the data from the search object
                return getattr(search_obj, attribute_name)

            # Use the standard implementation
            return implementation

        # Otherwise return the decorated function
        return decorated

    return decorator

def sector_endpoint(
    cache_duration: str = "1_week",
    attribute_name: Optional[str] = None,
    path: Optional[str] = None
) -> Callable:
    """
    Factory function to create a standard sector endpoint.

    Args:
        cache_duration: Cache duration
        attribute_name: YFinance attribute name
        path: Endpoint path (ignored but accepted to maintain compatibility)

    Returns:
        Callable: Decorator function for endpoint
    """
    def decorator(func: Callable) -> Callable:
        # Apply standard decorators
        decorated = performance_tracker()(func)
        decorated = error_handler()(decorated)

        # Apply caching
        if cache_duration == "1_day":
            decorated = cache_1_day()(decorated)
        elif cache_duration == "1_week":
            decorated = cache_1_week()(decorated)
        elif cache_duration == "1_month":
            decorated = cache_1_month()(decorated)
        elif cache_duration == "3_months":
            decorated = cache_3_months()(decorated)

        # Apply data cleaning
        decorated = clean_yfinance_data(decorated)

        # Apply response formatting
        decorated = response_formatter()(decorated)

        # If attribute name is provided, create a standard implementation
        if attribute_name:
            @functools.wraps(func)
            async def implementation(
                sector_obj = Depends(get_sector_object),
            ):
                """
                Standard implementation for sector endpoints.

                Args:
                    sector_obj: YFinance Sector object

                Returns:
                    Any: Sector attribute data
                """
                # Get the data from the sector object
                return getattr(sector_obj, attribute_name)

            # Use the standard implementation
            return implementation

        # Otherwise return the decorated function
        return decorated

    return decorator

def industry_endpoint(
    cache_duration: str = "1_week",
    attribute_name: Optional[str] = None,
    path: Optional[str] = None
) -> Callable:
    """
    Factory function to create a standard industry endpoint.

    Args:
        cache_duration: Cache duration
        attribute_name: YFinance attribute name
        path: Endpoint path (ignored but accepted to maintain compatibility)

    Returns:
        Callable: Decorator function for endpoint
    """
    def decorator(func: Callable) -> Callable:
        # Apply standard decorators
        decorated = performance_tracker()(func)
        decorated = error_handler()(decorated)

        # Apply caching
        if cache_duration == "1_day":
            decorated = cache_1_day()(decorated)
        elif cache_duration == "1_week":
            decorated = cache_1_week()(decorated)
        elif cache_duration == "1_month":
            decorated = cache_1_month()(decorated)
        elif cache_duration == "3_months":
            decorated = cache_3_months()(decorated)

        # Apply data cleaning
        decorated = clean_yfinance_data(decorated)

        # Apply response formatting
        decorated = response_formatter()(decorated)

        # If attribute name is provided, create a standard implementation
        if attribute_name:
            @functools.wraps(func)
            async def implementation(
                industry_obj = Depends(get_industry_object)
            ):
                """
                Standard implementation for industry endpoints.

                Args:
                    industry_obj: YFinance Industry object

                Returns:
                    Any: Industry attribute data
                """
                # Get the data from the industry object
                return getattr(industry_obj, attribute_name)

            # Use the standard implementation
            return implementation

        # Otherwise return the decorated function
        return decorated

    return decorator