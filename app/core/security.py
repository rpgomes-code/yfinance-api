"""Security utilities for the YFinance API.

This module contains security-related functionality, including
- API key validation
- Rate limiting functions
- Request validation
"""
import logging
import secrets
from typing import Callable, Dict, List, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader, APIKeyQuery

from app.core.config import settings

logger = logging.getLogger(__name__)

# API key security schemes
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)

# Valid API keys (in a real application, these would be stored in a database)
# In development mode, we use a hardcoded key for simplicity
VALID_API_KEYS = {
    "dev_key": {
        "name": "Development Key",
        "rate_limit": 1000,  # Higher limit for development
        "scopes": ["read", "write", "admin"],
    }
}

# Add metrics endpoint token if configured
if settings.METRICS_ENDPOINT_TOKEN:
    VALID_API_KEYS[settings.METRICS_ENDPOINT_TOKEN] = {
        "name": "Metrics Endpoint Token",
        "rate_limit": 100,
        "scopes": ["metrics"],
    }


def verify_api_key(
        apikey_header: Optional[str] = Security(api_key_header),
        apikey_query: Optional[str] = Security(api_key_query),
) -> Optional[Dict]:
    """
    Verify an API key from header or query parameter.

    Args:
        apikey_header: API key from header
        apikey_query: API key from query parameter

    Returns:
        Optional[Dict]: API key information if valid

    Raises:
        HTTPException: If the API key is invalid
    """
    # Only validate API keys if security is enabled
    if not settings.METRICS_ENDPOINT_ENABLED:
        return None

    # Get API key from header or query parameter
    api_key = apikey_header or apikey_query

    if not api_key:
        return None

    # Check if an API key is valid
    if api_key not in VALID_API_KEYS:
        logger.warning(f"Invalid API key: {api_key[:5]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Return API key information
    return {
        "key": api_key,
        **VALID_API_KEYS[api_key],
    }


def require_api_key(scopes: List[str] = None) -> Callable:
    """
    Dependency for requiring a valid API key with specific scopes.

    Args:
        scopes: Required API key scopes

    Returns:
        Callable: Dependency function
    """
    scopes = scopes or []

    def _require_api_key(
            api_key: Optional[Dict] = Depends(verify_api_key),
    ) -> Dict:
        # Check if an API key is present
        if not api_key:
            logger.warning("Missing API key")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        # Check if API key has required scopes
        if scopes and not any(scope in api_key.get("scopes", []) for scope in scopes):
            logger.warning(f"Insufficient permissions for API key: {api_key['key'][:5]}...")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
                headers={"WWW-Authenticate": "ApiKey"},
            )

        return api_key

    return _require_api_key


def generate_api_key() -> str:
    """
    Generate a new API key.

    Returns:
        str: New API key
    """
    return secrets.token_urlsafe(32)


def secure_headers() -> Dict[str, str]:
    """
    Get secure headers for API responses.

    Returns:
        Dict[str, str]: Secure headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;",
    }