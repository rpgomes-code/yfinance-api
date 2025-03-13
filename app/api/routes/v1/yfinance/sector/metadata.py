"""Sector metadata endpoint for YFinance API."""
from typing import Dict, Any

from fastapi import Path, Depends
from app.models.responses import DataResponse

from app.api.routes.v1.yfinance.base import create_sector_router
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import get_sector_object, get_query_params
from app.models.common import QueryParams
from app.utils.decorators import performance_tracker, error_handler, response_formatter
from app.core.cache import cache_3_months

# Create router for this endpoint
router = create_sector_router()


@router.get(
    "/{sector}/metadata",
    response_model=Dict[str, Any],
    summary="Get Sector Metadata",
    description="Returns metadata for the specified sector, including its key, name, symbol, and classification information."
)
@performance_tracker()
@error_handler()
@cache_3_months()
@clean_yfinance_data
@response_formatter()
async def get_sector_metadata(
        sector_obj=Depends(get_sector_object),
        query_params: QueryParams = Depends(get_query_params)
):
    """
    Get metadata for a sector.

    Args:
        sector_obj: YFinance Sector object
        query_params: Query parameters

    Returns:
        Dict[str, Any]: Sector metadata
    """
    # Create comprehensive metadata response
    metadata = {
        "key": sector_obj.key,
        "name": sector_obj.name,
        "symbol": sector_obj.symbol
    }

    # Add GICS classification if available
    # (GICS = Global Industry Classification Standard)
    try:
        if hasattr(sector_obj, "classification") and sector_obj.classification:
            metadata["classification"] = sector_obj.classification
        else:
            # Add standard GICS sector classification
            gics_sectors = {
                "energy": {
                    "code": "10",
                    "system": "GICS",
                    "description": "Companies that engage in exploration, production, refining, marketing, storage and transportation of oil, gas, coal and consumable fuels."
                },
                "materials": {
                    "code": "15",
                    "system": "GICS",
                    "description": "Companies that manufacture chemicals, construction materials, glass, paper, forest products, metals, minerals, and mining products."
                },
                "industrials": {
                    "code": "20",
                    "system": "GICS",
                    "description": "Companies that manufacture and distribute capital goods, provide commercial services and supplies, or provide transportation services."
                },
                "consumer_discretionary": {
                    "code": "25",
                    "system": "GICS",
                    "description": "Companies that provide products and services that are considered non-essential by consumers, such as automobiles, apparel, and leisure equipment."
                },
                "consumer_staples": {
                    "code": "30",
                    "system": "GICS",
                    "description": "Companies that provide essential products and services, such as food, beverages, tobacco, and household products."
                },
                "health_care": {
                    "code": "35",
                    "system": "GICS",
                    "description": "Companies that manufacture health care equipment and supplies or provide health care services, as well as companies involved in research, development, production, and marketing of pharmaceuticals and biotechnology products."
                },
                "financials": {
                    "code": "40",
                    "system": "GICS",
                    "description": "Companies involved in banking, thrifts and mortgage finance, diversified financial services, consumer finance, capital markets, and insurance."
                },
                "information_technology": {
                    "code": "45",
                    "system": "GICS",
                    "description": "Companies that offer software and IT services, manufacture communications equipment, semiconductors, and technology hardware and equipment."
                },
                "communication_services": {
                    "code": "50",
                    "system": "GICS",
                    "description": "Companies that provide telecommunications services and companies that provide media, entertainment, and interactive media and services."
                },
                "utilities": {
                    "code": "55",
                    "system": "GICS",
                    "description": "Companies that provide electric, gas, and water utilities, as well as independent power producers and energy traders, and companies that engage in generation and distribution of electricity using renewable sources."
                },
                "real_estate": {
                    "code": "60",
                    "system": "GICS",
                    "description": "Companies engaged in real estate development and operation, as well as companies offering real estate-related services."
                }
            }

            # Normalize sector key
            normalized_key = sector_obj.key.lower().replace("-", "_")
            if normalized_key in gics_sectors:
                metadata["classification"] = gics_sectors[normalized_key]
            else:
                metadata["classification"] = {
                    "system": "GICS",
                    "description": f"Sector classification for {sector_obj.name}"
                }
    except Exception:
        # Ignore classification errors
        pass

    # Add display information
    metadata["display"] = {
        "color": _get_sector_color(sector_obj.key),
        "icon": _get_sector_icon(sector_obj.key),
        "short_name": _get_sector_short_name(sector_obj.name)
    }

    return metadata


def _get_sector_color(sector_key: str) -> str:
    """Get color for a sector."""
    sector_colors = {
        "energy": "#E74C3C",
        "materials": "#9B59B6",
        "industrials": "#3498DB",
        "consumer-discretionary": "#1ABC9C",
        "consumer-staples": "#27AE60",
        "healthcare": "#2ECC71",
        "health-care": "#2ECC71",
        "financials": "#F1C40F",
        "information-technology": "#F39C12",
        "communication-services": "#D35400",
        "utilities": "#BDC3C7",
        "real-estate": "#95A5A6"
    }
    return sector_colors.get(sector_key.lower(), "#7F8C8D")


def _get_sector_icon(sector_key: str) -> str:
    """Get icon name for a sector."""
    sector_icons = {
        "energy": "zap",
        "materials": "box",
        "industrials": "cpu",
        "consumer-discretionary": "shopping-cart",
        "consumer-staples": "shopping-bag",
        "healthcare": "heart",
        "health-care": "heart",
        "financials": "dollar-sign",
        "information-technology": "code",
        "communication-services": "message-circle",
        "utilities": "power",
        "real-estate": "home"
    }
    return sector_icons.get(sector_key.lower(), "circle")


def _get_sector_short_name(sector_name: str) -> str:
    """Get short name for a sector."""
    if len(sector_name) <= 12:
        return sector_name

    words = sector_name.split()
    if len(words) == 1:
        return sector_name[:12]

    if len(words) == 2:
        return words[0][:1] + ". " + words[1]

    return "".join(word[0] for word in words)