"""API routes package for the YFinance API.

This package contains all API route modules organized by version and endpoint type.
The route structure follows the pattern:

/api/routes/v{version}/{endpoint_type}/{endpoint}.py

Where:
- {version} is the API version (e.g., v1)
- {endpoint_type} is the type of endpoint (e.g., ticker, market, search)
- {endpoint} is the specific endpoint (e.g., info, balance_sheet, status)
"""

# Import all route modules
# Importing is done dynamically by app/api/router.py