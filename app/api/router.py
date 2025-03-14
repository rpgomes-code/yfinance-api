"""Router registration module for the YFinance API.

This module contains functions for automatically discovering and registering
API endpoint routers.
"""
import importlib
import os
import pkgutil
import logging
from pathlib import Path
from typing import List

from fastapi import APIRouter

logger = logging.getLogger(__name__)

def register_routers(router: APIRouter) -> None:
    """
    Discover and register all routers in the API package.

    Args:
        router: Parent router to add child routers to
    """
    logger.info("Registering API routers...")

    # Get the base router path for v1/yfinance
    routes_base_path = "app.api.routes.v1.yfinance"

    # Register endpoint directories
    endpoint_types = ["ticker", "market", "search", "sector", "industry"]

    for endpoint_type in endpoint_types:
        # Full path to the endpoint directory
        endpoint_path = f"{routes_base_path}.{endpoint_type}"

        try:
            # Import the endpoint package
            endpoint_pkg = importlib.import_module(endpoint_path)

            # Register all modules in the endpoint package
            register_package_routers(router, endpoint_pkg)

            logger.info(f"Registered {endpoint_type} endpoints")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Error registering {endpoint_type} endpoints: {str(e)}")

    logger.info("API routers registered successfully")

def register_package_routers(router: APIRouter, package) -> None:
    """
    Register all routers in a package.

    Args:
        router: Parent router to add child routers to
        package: Package to scan for routers
    """
    # Check if package is properly imported and has __file__ attribute
    if not hasattr(package, '__file__') or package.__file__ is None:
        logger.warning(f"Cannot register routers from {getattr(package, '__name__', 'unknown')}: Package not properly imported")
        return

    # Get package path
    pkg_path = os.path.dirname(package.__file__)

    # Find all Python modules in the package
    modules = [name for _, name, is_pkg in pkgutil.iter_modules([pkg_path]) if not is_pkg]

    # Import each module and check for routers
    for module_name in modules:
        full_name = f"{package.__name__}.{module_name}"

        try:
            # Import the module
            module = importlib.import_module(full_name)

            # Look for 'router' attribute
            if hasattr(module, "router") and isinstance(module.router, APIRouter):
                # Include the router in the parent router
                router.include_router(module.router)
                logger.debug(f"Registered router from {full_name}")
        except Exception as e:
            logger.warning(f"Error registering router from {full_name}: {str(e)}")

def recursive_register_routers(parent_router: APIRouter, package_path: str) -> None:
    """
    Recursively register all routers in a package and its subpackages.

    Args:
        parent_router: Parent router to add child routers to
        package_path: Package path to scan (dot notation)
    """
    logger.info(f"Recursively registering routers in {package_path}...")

    try:
        # Import the package
        package = importlib.import_module(package_path)

        # Get the file system path
        fs_path = getattr(package, "__path__", None)
        if not fs_path:
            logger.warning(f"{package_path} is not a package")
            return

        # Register routers in this package
        register_package_routers(parent_router, package)

        # Find all subpackages
        for _, name, is_pkg in pkgutil.iter_modules(fs_path):
            if is_pkg:
                # Recursively register subpackage routers
                recursive_register_routers(parent_router, f"{package_path}.{name}")
    except ImportError as e:
        logger.warning(f"Error importing {package_path}: {str(e)}")

def register_routers_from_endpoints(router: APIRouter) -> None:
    """
    Register routers from endpoint directory structure.

    This uses the file system to discover endpoint modules.

    Args:
        router: Parent router to add child routers to
    """
    # Base path for endpoints
    endpoints_path = Path(__file__).parent / "routes" / "v1" / "yfinance"

    if not endpoints_path.exists():
        logger.warning(f"Endpoints path not found: {endpoints_path}")
        return

    # Register endpoint types
    for endpoint_dir in endpoints_path.iterdir():
        if endpoint_dir.is_dir():
            endpoint_type = endpoint_dir.name
            logger.info(f"Registering {endpoint_type} endpoints")

            # Register module routers
            for module_file in endpoint_dir.glob("*.py"):
                # Skip __init__ files
                if module_file.stem == "__init__":
                    continue

                # Form module name
                module_name = f"app.api.routes.v1.yfinance.{endpoint_type}.{module_file.stem}"

                try:
                    # Import the module
                    module = importlib.import_module(module_name)

                    # Look for 'router' attribute
                    if hasattr(module, "router") and isinstance(module.router, APIRouter):
                        # Include the router in the parent router
                        router.include_router(module.router)
                        logger.debug(f"Registered router from {module_name}")
                except Exception as e:
                    logger.warning(f"Error registering router from {module_name}: {str(e)}")

def get_all_route_paths(router: APIRouter) -> List[str]:
    """
    Get all route paths from a router.

    Args:
        router: Router to get paths from

    Returns:
        List[str]: List of route paths
    """
    paths = []

    # Get all routes
    for route in router.routes:
        if hasattr(route, "path"):
            paths.append(route.path)

        # Check for included routers
        if hasattr(route, "routes"):
            for sub_route in route.routes:
                if hasattr(sub_route, "path"):
                    # Get prefix if available
                    prefix = getattr(route, "prefix", "")
                    paths.append(f"{prefix}{sub_route.path}")

    return sorted(paths)

def get_router_details(router: APIRouter) -> dict:
    """
    Get details about a router.

    Args:
        router: Router to get details for

    Returns:
        dict: Router details
    """
    details = {
        "routes": [],
        "total_routes": 0,
        "included_routers": []
    }

    # Process direct routes
    for route in router.routes:
        if hasattr(route, "path"):
            route_info = {
                "path": route.path,
                "methods": list(route.methods) if hasattr(route, "methods") else [],
                "name": route.name if hasattr(route, "name") else None,
                "tags": route.tags if hasattr(route, "tags") else []
            }
            details["routes"].append(route_info)
            details["total_routes"] += 1

        # Process included routers
        if hasattr(route, "routes"):
            router_info = {
                "prefix": route.prefix if hasattr(route, "prefix") else "",
                "tags": route.tags if hasattr(route, "tags") else [],
                "routes": []
            }

            # Process routes in included router
            for sub_route in route.routes:
                if hasattr(sub_route, "path"):
                    sub_route_info = {
                        "path": f"{router_info['prefix']}{sub_route.path}",
                        "methods": list(sub_route.methods) if hasattr(sub_route, "methods") else [],
                        "name": sub_route.name if hasattr(sub_route, "name") else None,
                        "tags": sub_route.tags if hasattr(sub_route, "tags") else []
                    }
                    router_info["routes"].append(sub_route_info)
                    details["total_routes"] += 1

            details["included_routers"].append(router_info)

    return details