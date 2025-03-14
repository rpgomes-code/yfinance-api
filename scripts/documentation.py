#!/usr/bin/env python
"""
Script to generate documentation for the YFinance API.

This script analyzes the API structure and generates markdown documentation
for endpoints, models, and services.
"""
import argparse
import importlib
import inspect
import logging
import sys
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_APP_DIR = Path(__file__).parent.parent / "app"
DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "docs"


def generate_endpoint_docs(
        app_dir: Path,
        output_dir: Path,
        endpoint_types: Optional[List[str]] = None
) -> None:
    """
    Generate documentation for API endpoints.

    Args:
        app_dir: Application directory
        output_dir: Output directory
        endpoint_types: List of endpoint types to document (None for all)
    """
    logger.info("Generating endpoint documentation...")

    # Base path for endpoints
    endpoints_path = app_dir / "api" / "routes" / "v1" / "yfinance"

    if not endpoints_path.exists():
        logger.error(f"Endpoints path not found: {endpoints_path}")
        return

    # Create output directory
    endpoint_docs_dir = output_dir / "endpoints"
    endpoint_docs_dir.mkdir(parents=True, exist_ok=True)

    # Create an index file
    index_file = endpoint_docs_dir / "README.md"
    with open(index_file, "w") as f:
        f.write("# API Endpoints\n\n")
        f.write("This documentation covers the available endpoints in the YFinance API.\n\n")
        f.write("## Endpoint Types\n\n")

    # Process each endpoint type
    for endpoint_dir in sorted(endpoints_path.iterdir()):
        if not endpoint_dir.is_dir():
            continue

        endpoint_type = endpoint_dir.name

        # Skip if not in requested types
        if endpoint_types and endpoint_type not in endpoint_types:
            continue

        logger.info(f"Processing {endpoint_type} endpoints")

        # Create endpoint type directory
        type_docs_dir = endpoint_docs_dir / endpoint_type
        type_docs_dir.mkdir(exist_ok=True)

        # Create an endpoint type index file
        type_index_file = type_docs_dir / "README.md"
        with open(type_index_file, "w") as f:
            f.write(f"# {endpoint_type.capitalize()} Endpoints\n\n")
            f.write(f"This documentation covers the available {endpoint_type} endpoints in the YFinance API.\n\n")
            f.write("## Available Endpoints\n\n")

        # Add to the main index
        with open(index_file, "a") as f:
            f.write(f"- [{endpoint_type.capitalize()} Endpoints]({endpoint_type}/README.md)\n")

        # Process endpoint files
        endpoints = []
        for endpoint_file in sorted(endpoint_dir.glob("*.py")):
            # Skip __init__ files
            if endpoint_file.stem == "__init__":
                continue

            endpoints.append(endpoint_file.stem)

            # Try to import the module
            module_name = f"app.api.routes.v1.yfinance.{endpoint_type}.{endpoint_file.stem}"
            try:
                module = importlib.import_module(module_name)

                # Generate endpoint documentation
                endpoint_doc = generate_endpoint_doc(module, endpoint_type, endpoint_file.stem)

                # Write endpoint documentation
                endpoint_doc_file = type_docs_dir / f"{endpoint_file.stem}.md"
                with open(endpoint_doc_file, "w") as f:
                    f.write(endpoint_doc)

                # Add to type index
                with open(type_index_file, "a") as f:
                    f.write(f"- [{endpoint_file.stem}]({endpoint_file.stem}.md)\n")

            except (ImportError, AttributeError) as e:
                logger.warning(f"Error importing {module_name}: {str(e)}")

        logger.info(f"Processed {len(endpoints)} {endpoint_type} endpoints")


def generate_endpoint_doc(module, endpoint_type: str, endpoint_name: str) -> str:
    """
    Generate documentation for a single endpoint.

    Args:
        module: Endpoint module
        endpoint_type: Endpoint type
        endpoint_name: Endpoint name

    Returns:
        str: Markdown documentation
    """
    # Get module docstring
    module_doc = inspect.getdoc(module) or f"{endpoint_name} endpoint"

    # Find router and route functions
    router = getattr(module, "router", None)
    route_funcs = []

    if router and hasattr(router, "routes"):
        for route in router.routes:
            if hasattr(route, "endpoint") and inspect.isfunction(route.endpoint):
                route_funcs.append((route, route.endpoint))

    # Start documentation
    doc = f"# {endpoint_name.replace('_', ' ').title()}\n\n"
    doc += f"{module_doc}\n\n"

    # Process route functions
    for route, func in route_funcs:
        # Get function docstring
        func_doc = inspect.getdoc(func) or "No description"

        # Get route details
        path = getattr(route, "path", "unknown")
        methods = getattr(route, "methods", ["GET"])
        response_model = getattr(route, "response_model", None)

        # Add route details
        doc += f"## {', '.join(methods)} `{path}`\n\n"
        doc += f"{func_doc}\n\n"

        # Add a response model if available
        if response_model:
            doc += f"**Response Model:** `{response_model.__name__}`\n\n"

        # Try to get parameters
        try:
            sig = inspect.signature(func)
            params = sig.parameters

            if params:
                doc += "### Parameters\n\n"

                for name, param in params.items():
                    # Skip self and request parameters
                    if name in ("self", "request"):
                        continue

                    # Check for type annotation
                    param_type = param.annotation.__name__ if param.annotation is not inspect.Parameter.empty else "Any"

                    # Check for default value
                    default = param.default if param.default is not inspect.Parameter.empty else "Required"

                    doc += f"- **{name}** (`{param_type}`): {default}\n"

                doc += "\n"
        except (ValueError, AttributeError):
            pass

        # Add example (placeholder)
        doc += "### Example\n\n"
        doc += "```http\n"
        doc += f"GET /v1/{endpoint_type}/{'{' + endpoint_type[:-1] + '}'}/{endpoint_name}\n"
        doc += "```\n\n"

        doc += "```json\n"
        doc += "{\n  // Response will depend on the specific endpoint\n}\n"
        doc += "```\n\n"

    return doc


def generate_model_docs(app_dir: Path, output_dir: Path) -> None:
    """
    Generate documentation for API models.

    Args:
        app_dir: Application directory
        output_dir: Output directory
    """
    logger.info("Generating model documentation...")

    # Base path for models
    models_path = app_dir / "models"

    if not models_path.exists():
        logger.error(f"Models path not found: {models_path}")
        return

    # Create output directory
    model_docs_dir = output_dir / "models"
    model_docs_dir.mkdir(parents=True, exist_ok=True)

    # Create an index file
    index_file = model_docs_dir / "README.md"
    with open(index_file, "w") as f:
        f.write("# API Models\n\n")
        f.write("This documentation covers the data models used in the YFinance API.\n\n")
        f.write("## Model Categories\n\n")

    # Process model files
    for model_file in sorted(models_path.glob("*.py")):
        # Skip __init__ files
        if model_file.stem == "__init__":
            continue

        model_category = model_file.stem

        logger.info(f"Processing {model_category} models")

        # Try to import the module
        module_name = f"app.models.{model_category}"
        try:
            module = importlib.import_module(module_name)

            # Generate model documentation
            model_doc = generate_model_category_doc(module, model_category)

            # Write model documentation
            model_doc_file = model_docs_dir / f"{model_category}.md"
            with open(model_doc_file, "w") as f:
                f.write(model_doc)

            # Add to index
            with open(index_file, "a") as f:
                f.write(f"- [{model_category.capitalize()} Models]({model_category}.md)\n")

        except ImportError as e:
            logger.warning(f"Error importing {module_name}: {str(e)}")


def generate_model_category_doc(module, category: str) -> str:
    """
    Generate documentation for a model category.

    Args:
        module: Model module
        category: Model category

    Returns:
        str: Markdown documentation
    """
    # Get module docstring
    module_doc = inspect.getdoc(module) or f"{category} models"

    # Find model classes
    model_classes = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and hasattr(obj, "__module__") and obj.__module__ == module.__name__:
            model_classes.append((name, obj))

    # Start documentation
    doc = f"# {category.capitalize()} Models\n\n"
    doc += f"{module_doc}\n\n"
    doc += "## Table of Contents\n\n"

    # Add TOC
    for name, _ in model_classes:
        doc += f"- [{name}](#{name.lower()})\n"

    doc += "\n"

    # Process model classes
    for name, cls in model_classes:
        # Get class docstring
        cls_doc = inspect.getdoc(cls) or f"{name} model"

        # Add class details
        doc += f"## {name}\n\n"
        doc += f"{cls_doc}\n\n"

        # Try to get fields
        fields = {}
        for base in cls.__mro__:
            if hasattr(base, "__annotations__"):
                fields.update(base.__annotations__)

        if fields:
            doc += "### Fields\n\n"
            doc += "| Name | Type | Description |\n"
            doc += "|------|------|-------------|\n"

            for field_name, field_type in fields.items():
                # Skip private fields
                if field_name.startswith("_"):
                    continue

                # Get field type name
                type_name = getattr(field_type, "__name__", str(field_type))

                # Try to get field description
                description = "No description"
                if hasattr(cls, field_name):
                    field = getattr(cls, field_name)
                    if hasattr(field, "description"):
                        description = field.description

                doc += f"| {field_name} | {type_name} | {description} |\n"

            doc += "\n"

    return doc


def generate_service_docs(app_dir: Path, output_dir: Path) -> None:
    """
    Generate documentation for API services.

    Args:
        app_dir: Application directory
        output_dir: Output directory
    """
    logger.info("Generating service documentation...")

    # Base path for services
    services_path = app_dir / "services"

    if not services_path.exists():
        logger.error(f"Services path not found: {services_path}")
        return

    # Create output directory
    service_docs_dir = output_dir / "services"
    service_docs_dir.mkdir(parents=True, exist_ok=True)

    # Create an index file
    index_file = service_docs_dir / "README.md"
    with open(index_file, "w") as f:
        f.write("# API Services\n\n")
        f.write("This documentation covers the services used in the YFinance API.\n\n")
        f.write("## Available Services\n\n")

    # Process service files
    for service_file in sorted(services_path.glob("*.py")):
        # Skip __init__ files
        if service_file.stem == "__init__":
            continue

        service_name = service_file.stem

        logger.info(f"Processing {service_name} service")

        # Try to import the module
        module_name = f"app.services.{service_name}"
        try:
            module = importlib.import_module(module_name)

            # Generate service documentation
            service_doc = generate_service_doc(module, service_name)

            # Write service documentation
            service_doc_file = service_docs_dir / f"{service_name}.md"
            with open(service_doc_file, "w") as f:
                f.write(service_doc)

            # Add to index
            with open(index_file, "a") as f:
                f.write(f"- [{service_name.replace('_', ' ').title()}]({service_name}.md)\n")

        except ImportError as e:
            logger.warning(f"Error importing {module_name}: {str(e)}")


def generate_service_doc(module, service_name: str) -> str:
    """
    Generate documentation for a service.

    Args:
        module: Service module
        service_name: Service name

    Returns:
        str: Markdown documentation
    """
    # Get module docstring
    module_doc = inspect.getdoc(module) or f"{service_name} service"

    # Find service classes
    service_classes = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and hasattr(obj, "__module__") and obj.__module__ == module.__name__:
            service_classes.append((name, obj))

    # Start documentation
    doc = f"# {service_name.replace('_', ' ').title()}\n\n"
    doc += f"{module_doc}\n\n"

    # Process service classes
    for class_name, cls in service_classes:
        # Get class docstring
        cls_doc = inspect.getdoc(cls) or f"{class_name} class"

        # Add class details
        doc += f"## {class_name}\n\n"
        doc += f"{cls_doc}\n\n"

        # Find methods
        methods = []
        for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            # Skip private methods
            if name.startswith("_"):
                continue

            methods.append((name, method))

        # Add methods
        if methods:
            doc += "### Methods\n\n"

            for method_name, method in methods:
                # Get method docstring
                method_doc = inspect.getdoc(method) or f"{method_name} method"

                # Add method details
                doc += f"#### {method_name}\n\n"
                doc += f"{method_doc}\n\n"

                # Try to get signature
                try:
                    sig = inspect.signature(method)
                    doc += f"```python\n{method_name}{sig}\n```\n\n"
                except (ValueError, TypeError):
                    pass

        doc += "\n"

    return doc


def generate_index(output_dir: Path) -> None:
    """
    Generate the main index file.

    Args:
        output_dir: Output directory
    """
    logger.info("Generating main index...")

    # Create an index file
    index_file = output_dir / "README.md"
    with open(index_file, "w") as f:
        f.write("# YFinance API Documentation\n\n")
        f.write("Welcome to the YFinance API documentation.\n\n")
        f.write("## Documentation Sections\n\n")
        f.write("- [API Endpoints](endpoints/README.md)\n")
        f.write("- [API Models](models/README.md)\n")
        f.write("- [API Services](services/README.md)\n")
        f.write("\n")
        f.write("## Overview\n\n")
        f.write(
            "The YFinance API provides access to financial data from Yahoo Finance through a RESTful API interface. ")
        f.write(
            "It includes endpoints for retrieving data about tickers, markets, sectors, and industries, as well as search functionality.\n\n")
        f.write("## Getting Started\n\n")
        f.write("To get started with the YFinance API, see the [API Endpoints](endpoints/README.md) documentation.\n\n")
        f.write("## API Reference\n\n")
        f.write("For a complete API reference, see the following sections:\n\n")
        f.write("- [API Endpoints](endpoints/README.md)\n")
        f.write("- [API Models](models/README.md)\n")
        f.write("- [API Services](services/README.md)\n")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Generate documentation for the YFinance API")
    parser.add_argument(
        "-a", "--app-dir",
        help="Application directory",
        default=DEFAULT_APP_DIR
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory",
        default=DEFAULT_OUTPUT_DIR
    )
    parser.add_argument(
        "-t", "--endpoint-types",
        help="Endpoint types to document (comma-separated)",
        default=None
    )
    parser.add_argument(
        "--skip-endpoints",
        help="Skip endpoint documentation",
        action="store_true"
    )
    parser.add_argument(
        "--skip-models",
        help="Skip model documentation",
        action="store_true"
    )
    parser.add_argument(
        "--skip-services",
        help="Skip service documentation",
        action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Set paths
    app_dir = Path(args.app_dir)
    output_dir = Path(args.output_dir)

    # Check app directory
    if not app_dir.exists():
        logger.error(f"Application directory not found: {app_dir}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Parse endpoint types
    endpoint_types = None
    if args.endpoint_types:
        endpoint_types = [t.strip() for t in args.endpoint_types.split(",")]

    # Generate documentation
    if not args.skip_endpoints:
        generate_endpoint_docs(app_dir, output_dir, endpoint_types)

    if not args.skip_models:
        generate_model_docs(app_dir, output_dir)

    if not args.skip_services:
        generate_service_docs(app_dir, output_dir)

    # Generate main index
    generate_index(output_dir)

    logger.info(f"Documentation generated at {output_dir}")


if __name__ == "__main__":
    main()