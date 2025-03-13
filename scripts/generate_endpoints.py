#!/usr/bin/env python
"""
Script to generate endpoint files based on templates.

This script reads endpoint information and generates individual endpoint files
for the YFinance API, following the granular one-file-per-endpoint structure.
"""
import argparse
import os
import re
import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_TEMPLATES_DIR = Path(__file__).parent / "templates"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "app" / "api" / "routes" / "v1" / "yfinance"

# Endpoint type definitions
ENDPOINT_TYPES = {
    "ticker": {
        "prefix": "/ticker",
        "tags": ["ticker"],
        "router_func": "create_ticker_router",
        "dependency": "get_ticker_object",
        "router_import": "from app.api.routes.v1.yfinance.base import create_ticker_router",
        "endpoint_decorator": "ticker_endpoint",
    },
    "market": {
        "prefix": "/market",
        "tags": ["market"],
        "router_func": "create_market_router",
        "dependency": "get_market_object",
        "router_import": "from app.api.routes.v1.yfinance.base import create_market_router",
        "endpoint_decorator": "market_endpoint",
    },
    "search": {
        "prefix": "/search",
        "tags": ["search"],
        "router_func": "create_search_router",
        "dependency": "get_search_object",
        "router_import": "from app.api.routes.v1.yfinance.base import create_search_router",
        "endpoint_decorator": "search_endpoint",
    },
    "sector": {
        "prefix": "/sector",
        "tags": ["sector"],
        "router_func": "create_sector_router",
        "dependency": "get_sector_object",
        "router_import": "from app.api.routes.v1.yfinance.base import create_sector_router",
        "endpoint_decorator": "sector_endpoint",
    },
    "industry": {
        "prefix": "/industry",
        "tags": ["industry"],
        "router_func": "create_industry_router",
        "dependency": "get_industry_object",
        "router_import": "from app.api.routes.v1.yfinance.base import create_industry_router",
        "endpoint_decorator": "industry_endpoint",
    },
}

# Template for a basic endpoint file
ENDPOINT_TEMPLATE = string.Template('''"""${description} endpoint for YFinance API."""
from typing import List, Dict, Any, Optional

from fastapi import Path, Query, Depends
${model_imports}

from app.models.common import QueryParams
${router_import}
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import ${dependency}, get_query_params

# Create router for this endpoint
router = ${router_func}()

@router.get(
    "/{${param}}/${endpoint}",
    response_model=${response_model},
    summary="${summary}",
    description="${description}"
)
@${endpoint_decorator}(
    path="/{${param}}/${endpoint}",
    cache_duration="${cache_duration}",
    invalidate_at_midnight=${invalidate_at_midnight},
    attribute_name="${attribute_name}"
)
async def get_${endpoint_type}_${function_name}(
    ${param}_obj = Depends(${dependency}),
    query_params: QueryParams = Depends(get_query_params)
):
    """
    Get ${description_lower}

    Args:
        ${param}_obj: YFinance ${object_type} object
        query_params: Query parameters

    Returns:
        ${return_type}: ${return_description}
    """
    # Implementation is handled by the endpoint decorator
    pass
''')

# Template for a custom endpoint file
CUSTOM_ENDPOINT_TEMPLATE = string.Template('''"""${description} endpoint for YFinance API."""
from typing import List, Dict, Any, Optional

from fastapi import Path, Query, Depends
${model_imports}

from app.models.common import QueryParams
${router_import}
from app.utils.yfinance_data_manager import clean_yfinance_data
from app.api.dependencies import ${dependency}, get_query_params

# Create router for this endpoint
router = ${router_func}()

@router.get(
    "/{${param}}/${endpoint}",
    response_model=${response_model},
    summary="${summary}",
    description="${description}"
)
@${endpoint_decorator}(
    path="/{${param}}/${endpoint}",
    cache_duration="${cache_duration}",
    invalidate_at_midnight=${invalidate_at_midnight}
)
@clean_yfinance_data
async def get_${endpoint_type}_${function_name}(
    ${param}_obj = Depends(${dependency}),
    query_params: QueryParams = Depends(get_query_params)
):
    """
    Get ${description_lower}

    Args:
        ${param}_obj: YFinance ${object_type} object
        query_params: Query parameters

    Returns:
        ${return_type}: ${return_description}
    """
    # Custom implementation
    # This is a placeholder - replace with actual implementation
    ${custom_implementation}
''')


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate endpoint files for YFinance API")
    parser.add_argument(
        "-c", "--config",
        help="Path to endpoints configuration file",
        default="endpoints.json"
    )
    parser.add_argument(
        "-t", "--templates",
        help="Path to template directory",
        default=DEFAULT_TEMPLATES_DIR
    )
    parser.add_argument(
        "-o", "--output",
        help="Path to output directory",
        default=DEFAULT_OUTPUT_DIR
    )
    parser.add_argument(
        "-f", "--force",
        help="Force overwrite existing files",
        action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    parser.add_argument(
        "-d", "--dry-run",
        help="Dry run (don't write files)",
        action="store_true"
    )
    parser.add_argument(
        "-e", "--endpoint-type",
        help="Generate only endpoints of specified type",
        choices=ENDPOINT_TYPES.keys()
    )
    return parser.parse_args()


def load_endpoints_config(config_path: Path) -> List[Dict[str, Any]]:
    """
    Load endpoints configuration from a JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        List[Dict[str, Any]]: List of endpoint configurations
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        if not isinstance(config, list):
            logger.error("Invalid configuration: root element must be a list")
            sys.exit(1)

        return config
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading configuration file: {str(e)}")
        sys.exit(1)


def validate_endpoint_config(endpoint: Dict[str, Any]) -> bool:
    """
    Validate endpoint configuration.

    Args:
        endpoint: Endpoint configuration

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = [
        "endpoint_type",
        "endpoint",
        "attribute_name",
        "description"
    ]

    # Check required fields
    missing_fields = [field for field in required_fields if field not in endpoint]
    if missing_fields:
        logger.warning(f"Missing required fields: {', '.join(missing_fields)}")
        return False

    # Check endpoint_type is valid
    if endpoint["endpoint_type"] not in ENDPOINT_TYPES:
        logger.warning(f"Invalid endpoint_type: {endpoint['endpoint_type']}")
        return False

    return True


def generate_endpoint_file(
        endpoint: Dict[str, Any],
        output_dir: Path,
        force: bool = False,
        dry_run: bool = False
) -> bool:
    """
    Generate an endpoint file from configuration.

    Args:
        endpoint: Endpoint configuration
        output_dir: Output directory
        force: Whether to force overwrite existing files
        dry_run: Whether to perform a dry run

    Returns:
        bool: True if successful, False otherwise
    """
    # Validate configuration
    if not validate_endpoint_config(endpoint):
        return False

    # Get endpoint type info
    endpoint_type = endpoint["endpoint_type"]
    endpoint_type_info = ENDPOINT_TYPES[endpoint_type]

    # Determine output path
    endpoint_dir = output_dir / endpoint_type
    output_path = endpoint_dir / f"{endpoint['endpoint']}.py"

    # Check if file already exists
    if output_path.exists() and not force:
        logger.warning(f"File already exists: {output_path}")
        return False

    # Create directory if it doesn't exist
    if not dry_run and not endpoint_dir.exists():
        endpoint_dir.mkdir(parents=True, exist_ok=True)

    # Normalize attribute name
    attribute_name = endpoint.get("attribute_name", endpoint["endpoint"])

    # Determine parameter name
    param = {
        "ticker": "ticker",
        "market": "market",
        "search": "query",
        "sector": "sector",
        "industry": "industry"
    }.get(endpoint_type, endpoint_type)

    # Determine object type
    object_type = {
        "ticker": "Ticker",
        "market": "Market",
        "search": "Search",
        "sector": "Sector",
        "industry": "Industry"
    }.get(endpoint_type, endpoint_type.capitalize())

    # Function name
    function_name = endpoint["endpoint"].replace("-", "_")

    # Get response model
    response_model = endpoint.get("response_model", "Any")

    # Get model imports
    model_imports = ""
    if response_model != "Any" and response_model != "List[Any]" and response_model != "Dict[str, Any]":
        model_imports = f"from app.models.responses import {response_model}"

    # Get return type and description
    return_type = response_model
    return_description = endpoint.get("return_description", "Response data")

    # Get cache duration
    cache_duration = endpoint.get("cache_duration", "1_day")

    # Get invalidate at midnight
    invalidate_at_midnight = str(endpoint.get("invalidate_at_midnight", True)).lower()

    # Get summary and description
    summary = endpoint.get("summary", f"Get {endpoint['endpoint'].replace('_', ' ')}")
    description = endpoint.get("description",
                               f"Get {endpoint['endpoint'].replace('_', ' ')} data for the specified {param}")
    description_lower = description.lower()

    # Choose template
    if endpoint.get("custom_implementation", False):
        template = CUSTOM_ENDPOINT_TEMPLATE
        custom_implementation = endpoint.get("custom_implementation_code", "pass  # TODO: Implement custom logic")
    else:
        template = ENDPOINT_TEMPLATE
        custom_implementation = ""

    # Fill template
    content = template.substitute(
        endpoint_type=endpoint_type,
        endpoint=endpoint["endpoint"],
        function_name=function_name,
        param=param,
        object_type=object_type,
        attribute_name=attribute_name,
        response_model=response_model,
        model_imports=model_imports,
        return_type=return_type,
        return_description=return_description,
        summary=summary,
        description=description,
        description_lower=description_lower,
        cache_duration=cache_duration,
        invalidate_at_midnight=invalidate_at_midnight,
        router_import=endpoint_type_info["router_import"],
        router_func=endpoint_type_info["router_func"],
        dependency=endpoint_type_info["dependency"],
        endpoint_decorator=endpoint_type_info["endpoint_decorator"],
        custom_implementation=custom_implementation
    )

    # Write file
    if dry_run:
        logger.info(f"Would write file: {output_path}")
    else:
        logger.info(f"Writing file: {output_path}")
        with open(output_path, "w") as f:
            f.write(content)

    return True


def generate_endpoints(
        endpoints: List[Dict[str, Any]],
        output_dir: Path,
        force: bool = False,
        dry_run: bool = False,
        endpoint_type_filter: Optional[str] = None
) -> Tuple[int, int]:
    """
    Generate multiple endpoint files from configuration.

    Args:
        endpoints: List of endpoint configurations
        output_dir: Output directory
        force: Whether to force overwrite existing files
        dry_run: Whether to perform a dry run
        endpoint_type_filter: Filter by endpoint type

    Returns:
        Tuple[int, int]: Count of successful and failed generations
    """
    successful = 0
    failed = 0

    for endpoint in endpoints:
        # Skip if not matching filter
        if endpoint_type_filter and endpoint.get("endpoint_type") != endpoint_type_filter:
            continue

        # Generate endpoint file
        if generate_endpoint_file(endpoint, output_dir, force, dry_run):
            successful += 1
        else:
            failed += 1

    return successful, failed


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config_path = Path(args.config)
    endpoints = load_endpoints_config(config_path)

    # Set output directory
    output_dir = Path(args.output)

    logger.info(f"Generating endpoints from {config_path} to {output_dir}")
    if args.dry_run:
        logger.info("Dry run mode - no files will be written")

    # Generate endpoints
    successful, failed = generate_endpoints(
        endpoints,
        output_dir,
        force=args.force,
        dry_run=args.dry_run,
        endpoint_type_filter=args.endpoint_type
    )

    logger.info(f"Generated {successful} endpoints successfully ({failed} failed)")


if __name__ == "__main__":
    main()