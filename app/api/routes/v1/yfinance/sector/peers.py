"""Sector peers endpoint for YFinance API."""
from typing import List, Dict, Any

from fastapi import Path, Depends, Query
from app.models.responses import ListResponse

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_1_week

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/peers",
    response_model=List[Dict[str, Any]],
    summary="Get Sector Peers",
    description="Returns comparable sectors that are peers to the specified sector."
)
@performance_tracker()
@error_handler()
@cache_1_week()
@clean_yfinance_data
@response_formatter()
async def get_sector_peers(
        sector_obj=Depends(get_sector_object),
        limit: int = Query(5, ge=1, le=10, description="Maximum number of peer sectors to return"),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get peer sectors for a sector.

    Args:
        sector_obj: YFinance Sector object
        limit: Maximum number of peers to return
        query_params: Query parameters

    Returns:
        List[Dict[str, Any]]: List of peer sectors
    """
    # Get sector name
    sector_name = sector_obj.name

    # Define sector relationships and similarity scores
    # These are manually defined based on typical sector correlations
    sector_relationships = {
        "Technology": [
            {"name": "Communication Services", "similarity": 0.8,
             "reason": "Tech and communication businesses are closely aligned"},
            {"name": "Consumer Cyclical", "similarity": 0.6,
             "reason": "Consumer tech is a major part of cyclical spending"},
            {"name": "Industrials", "similarity": 0.5, "reason": "Industrial automation and tech overlap"},
            {"name": "Healthcare", "similarity": 0.4, "reason": "Healthcare technology is a growing segment"}
        ],
        "Financial Services": [
            {"name": "Real Estate", "similarity": 0.7, "reason": "Real estate financing and investment connection"},
            {"name": "Industrials", "similarity": 0.5, "reason": "Both are economically sensitive sectors"},
            {"name": "Consumer Cyclical", "similarity": 0.5, "reason": "Consumer credit and spending correlation"},
            {"name": "Insurance", "similarity": 0.9, "reason": "Insurance is a financial service subsector"}
        ],
        "Healthcare": [
            {"name": "Technology", "similarity": 0.4, "reason": "Healthcare technology overlap"},
            {"name": "Consumer Defensive", "similarity": 0.5,
             "reason": "Healthcare is a defensive sector with consumer focus"},
            {"name": "Industrials", "similarity": 0.3, "reason": "Medical equipment manufacturing overlap"}
        ],
        "Consumer Cyclical": [
            {"name": "Communication Services", "similarity": 0.6, "reason": "Media and entertainment overlap"},
            {"name": "Technology", "similarity": 0.6, "reason": "Consumer tech products correlation"},
            {"name": "Industrials", "similarity": 0.5, "reason": "Manufacturing and economic sensitivity connection"},
            {"name": "Financial Services", "similarity": 0.5,
             "reason": "Consumer credit and retail banking relationship"}
        ],
        "Consumer Defensive": [
            {"name": "Healthcare", "similarity": 0.5, "reason": "Both are defensive sectors with consumer focus"},
            {"name": "Utilities", "similarity": 0.6, "reason": "Both are defensive sectors with stable demand"},
            {"name": "Real Estate", "similarity": 0.4, "reason": "Both can provide inflation protection"}
        ],
        "Energy": [
            {"name": "Basic Materials", "similarity": 0.7, "reason": "Natural resource and commodity connection"},
            {"name": "Industrials", "similarity": 0.5, "reason": "Energy infrastructure and industrial usage"},
            {"name": "Utilities", "similarity": 0.6, "reason": "Energy production and utility operations overlap"}
        ],
        "Industrials": [
            {"name": "Basic Materials", "similarity": 0.6, "reason": "Manufacturing input relationship"},
            {"name": "Energy", "similarity": 0.5, "reason": "Energy usage in industrial processes"},
            {"name": "Technology", "similarity": 0.5, "reason": "Industrial technology and automation"},
            {"name": "Consumer Cyclical", "similarity": 0.5, "reason": "Manufacturing and economic sensitivity"}
        ],
        "Basic Materials": [
            {"name": "Energy", "similarity": 0.7, "reason": "Natural resource and commodity connection"},
            {"name": "Industrials", "similarity": 0.6, "reason": "Material inputs for manufacturing"},
            {"name": "Real Estate", "similarity": 0.4, "reason": "Construction materials connection"}
        ],
        "Utilities": [
            {"name": "Energy", "similarity": 0.6, "reason": "Energy production and distribution overlap"},
            {"name": "Consumer Defensive", "similarity": 0.6,
             "reason": "Both are defensive sectors with stable demand"},
            {"name": "Real Estate", "similarity": 0.5, "reason": "Both are income-generating sectors"}
        ],
        "Real Estate": [
            {"name": "Financial Services", "similarity": 0.7,
             "reason": "Real estate financing and investment connection"},
            {"name": "Utilities", "similarity": 0.5, "reason": "Both are income-generating sectors"},
            {"name": "Basic Materials", "similarity": 0.4, "reason": "Construction materials connection"}
        ],
        "Communication Services": [
            {"name": "Technology", "similarity": 0.8,
             "reason": "Tech and communication businesses are closely aligned"},
            {"name": "Consumer Cyclical", "similarity": 0.6, "reason": "Media and entertainment overlap"},
            {"name": "Utilities", "similarity": 0.4, "reason": "Telecom utility-like services"}
        ]
    }

    # Standard sector names match
    standardized_names = {
        "technology": "Technology",
        "tech": "Technology",
        "financial": "Financial Services",
        "financial services": "Financial Services",
        "financials": "Financial Services",
        "healthcare": "Healthcare",
        "health care": "Healthcare",
        "consumer cyclical": "Consumer Cyclical",
        "consumer discretionary": "Consumer Cyclical",
        "consumer defensive": "Consumer Defensive",
        "consumer staples": "Consumer Defensive",
        "energy": "Energy",
        "industrials": "Industrials",
        "industrial": "Industrials",
        "basic materials": "Basic Materials",
        "materials": "Basic Materials",
        "utilities": "Utilities",
        "utility": "Utilities",
        "real estate": "Real Estate",
        "reits": "Real Estate",
        "communication services": "Communication Services",
        "communication": "Communication Services",
        "telecom": "Communication Services"
    }

    # Standardize sector name
    standardized_sector = standardized_names.get(sector_name.lower(), sector_name)

    # Get peer sectors
    peers = sector_relationships.get(standardized_sector, [])

    # Limit number of peers
    peers = peers[:limit]

    # Add sector key for each peer
    for peer in peers:
        # Convert spaces to underscores and lowercase for key
        peer["key"] = peer["name"].lower().replace(" ", "_")

    # Return peer sectors
    return peers