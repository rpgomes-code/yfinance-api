"""API package for the YFinance API.

This package contains the API routers, dependencies, and endpoint
implementations for the YFinance API.
"""

from fastapi import APIRouter

from app.api.router import register_routers

# Create the main API router
api_router = APIRouter()

# Import and include all route modules
register_routers(api_router)