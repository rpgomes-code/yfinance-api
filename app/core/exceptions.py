"""Custom exception handling for the YFinance API.

This module defines custom exceptions and exception handlers for the API.
"""
import logging
from typing import Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception for API errors."""

    def __init__(
            self,
            status_code: int,
            detail: str,
            error_code: Optional[str] = None,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize API exception.

        Args:
            status_code: HTTP status code
            detail: Error detail message
            error_code: Internal error code identifier
            headers: Additional HTTP headers
        """
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code or "api_error"
        self.headers = headers


class YFinanceError(APIException):
    """Exception for errors from the YFinance library."""

    def __init__(
            self,
            detail: str,
            error_code: str = "yfinance_error",
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize YFinance error.

        Args:
            detail: Error detail message
            error_code: Internal error code identifier
            status_code: HTTP status code
            headers: Additional HTTP headers
        """
        super().__init__(status_code, detail, error_code, headers)


class TickerNotFoundError(APIException):
    """Exception for when a ticker is not found."""

    def __init__(
            self,
            ticker: str,
            error_code: str = "ticker_not_found",
            status_code: int = status.HTTP_404_NOT_FOUND,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize ticker not found error.

        Args:
            ticker: The ticker symbol that was not found
            error_code: Internal error code identifier
            status_code: HTTP status code
            headers: Additional HTTP headers
        """
        detail = f"Ticker '{ticker}' not found"
        super().__init__(status_code, detail, error_code, headers)


class ValidationError(APIException):
    """Exception for input validation errors."""

    def __init__(
            self,
            detail: str,
            field: Optional[str] = None,
            error_code: str = "validation_error",
            status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize validation error.

        Args:
            detail: Error detail message
            field: The field that failed validation
            error_code: Internal error code identifier
            status_code: HTTP status code
            headers: Additional HTTP headers
        """
        message = f"Validation error: {detail}"
        if field:
            message = f"Validation error for field '{field}': {detail}"
        super().__init__(status_code, message, error_code, headers)


class RateLimitExceededError(APIException):
    """Exception for rate limit exceeded."""

    def __init__(
            self,
            detail: str = "Rate limit exceeded",
            error_code: str = "rate_limit_exceeded",
            status_code: int = status.HTTP_429_TOO_MANY_REQUESTS,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize rate limit exceeded error.

        Args:
            detail: Error detail message
            error_code: Internal error code identifier
            status_code: HTTP status code
            headers: Additional HTTP headers
        """
        super().__init__(status_code, detail, error_code, headers)


class NotImplementedYetError(APIException):
    """Exception for not implemented features."""

    def __init__(
            self,
            detail: str = "This feature is not implemented yet",
            error_code: str = "not_implemented",
            status_code: int = status.HTTP_501_NOT_IMPLEMENTED,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize not implemented error.

        Args:
            detail: Error detail message
            error_code: Internal error code identifier
            status_code: HTTP status code
            headers: Additional HTTP headers
        """
        super().__init__(status_code, detail, error_code, headers)


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handle API exceptions.

    Args:
        request: The HTTP request
        exc: The API exception

    Returns:
        JSONResponse: JSON response with error details
    """
    # Log the error
    logger.error(
        f"API Exception: {exc.error_code} - {exc.detail}",
        extra={"path": request.url.path, "status_code": exc.status_code}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.detail,
                "status": exc.status_code
            }
        },
        headers=exc.headers
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.

    Args:
        request: The HTTP request
        exc: The HTTP exception

    Returns:
        JSONResponse: JSON response with error details
    """
    # Log the error
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={"path": request.url.path}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "http_error",
                "message": exc.detail,
                "status": exc.status_code
            }
        },
        headers=exc.headers
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation exceptions.

    Args:
        request: The HTTP request
        exc: The validation exception

    Returns:
        JSONResponse: JSON response with error details
    """
    # Extract validation errors
    errors = []
    for error in exc.errors():
        # Extract field information
        location = error.get("loc", [])
        field = location[-1] if location else ""
        field_path = ".".join(str(loc) for loc in location if loc != "body")

        # Format error message
        error_msg = {
            "field": field_path or field,
            "message": error.get("msg", "Validation error"),
            "type": error.get("type", "unknown")
        }
        errors.append(error_msg)

    # Log the error
    logger.warning(
        f"Validation Exception: {len(errors)} errors",
        extra={"path": request.url.path, "errors": errors}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "status": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "errors": errors
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions.

    Args:
        request: The HTTP request
        exc: The exception

    Returns:
        JSONResponse: JSON response with error details
    """
    # Log the error
    logger.exception(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
        extra={"path": request.url.path}
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "server_error",
                "message": "An unexpected error occurred",
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR
            }
        }
    )


def add_exception_handlers(app: FastAPI) -> None:
    """
    Add exception handlers to FastAPI application.

    Args:
        app: FastAPI application
    """
    app.add_exception_handler(APIException, api_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)