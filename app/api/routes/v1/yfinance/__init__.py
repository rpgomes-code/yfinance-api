"""YFinance routes package for the API v1.

This package contains routes for YFinance data, organized into these main categories:
- ticker: Endpoints for stock ticker data
- market: Endpoints for market data
- search: Endpoints for search functionality
- sector: Endpoints for sector data
- industry: Endpoints for industry data

Each category is a subpackage containing individual endpoint modules.
"""

from fastapi import APIRouter

# Create yfinance router
yfinance_router = APIRouter(prefix="/yfinance")

# Import all yfinance route modules
# Importing is done dynamically by app/api/router.py