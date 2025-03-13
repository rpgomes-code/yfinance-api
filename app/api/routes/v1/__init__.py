"""API v1 routes package for the YFinance API.

This package contains the v1 API routes organized by endpoint type.
"""

from fastapi import APIRouter

# Create v1 API router
v1_router = APIRouter(prefix="/v1")

# Import all v1 route modules
# Importing is done dynamically by app/api/router.py