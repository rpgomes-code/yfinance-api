#!/usr/bin/env python
"""
Script to warm up the API cache with common requests.

This script makes requests to commonly accessed endpoints to ensure
that the cache is populated, improving response times for users.
"""
import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any

import aiohttp
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default warmup configuration
DEFAULT_CONFIG_PATH = Path(__file__).parent / "warmup_config.json"
DEFAULT_CONCURRENCY = 5


async def make_request(
        session: aiohttp.ClientSession,
        base_url: str,
        endpoint: str,
        timeout: int = 30
) -> Tuple[str, int, float]:
    """
    Make a request to an API endpoint.

    Args:
        session: HTTP session
        base_url: Base URL for the API
        endpoint: Endpoint path
        timeout: Request timeout in seconds

    Returns:
        Tuple[str, int, float]: Endpoint, status code, and request time
    """
    url = f"{base_url}{endpoint}"
    start_time = time.time()

    try:
        async with session.get(url, timeout=timeout) as response:
            await response.text()  # Ensure response is read
            status = response.status
            elapsed = time.time() - start_time
            return endpoint, status, elapsed
    except Exception as e:
        logger.error(f"Error requesting {url}: {str(e)}")
        return endpoint, -1, time.time() - start_time


async def warm_up_endpoints(
        base_url: str,
        endpoints: List[str],
        concurrency: int = 5,
        timeout: int = 30
) -> Dict[str, Dict[str, Any]]:
    """
    Warm up multiple API endpoints.

    Args:
        base_url: Base URL for the API
        endpoints: List of endpoint paths
        concurrency: Maximum number of concurrent requests
        timeout: Request timeout in seconds

    Returns:
        Dict[str, Dict[str, Any]]: Results for each endpoint
    """
    results = {}

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded_request(endpoint: str) -> Tuple[str, int, float]:
        """Make a request with concurrency control."""
        async with semaphore:
            return await make_request(session, base_url, endpoint, timeout)

    # Setup progress bar
    pbar = tqdm(total=len(endpoints), desc="Warming up cache")

    # Make requests
    async with aiohttp.ClientSession() as session:
        tasks = [bounded_request(endpoint) for endpoint in endpoints]

        for future in asyncio.as_completed(tasks):
            endpoint, status, elapsed = await future
            results[endpoint] = {
                "status": status,
                "time": round(elapsed, 3)
            }
            pbar.update(1)

    pbar.close()
    return results


def load_warmup_config(config_path: Path) -> Dict[str, Any]:
    """
    Load warmup configuration from a JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Dict[str, Any]: Warmup configuration
    """
    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        # Validate configuration
        if "base_url" not in config:
            logger.error("Missing 'base_url' in configuration")
            sys.exit(1)

        if "endpoints" not in config or not isinstance(config["endpoints"], list):
            logger.error("Missing or invalid 'endpoints' in configuration")
            sys.exit(1)

        return config
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading configuration file: {str(e)}")
        sys.exit(1)


def generate_default_config(output_path: Path) -> None:
    """
    Generate a default warmup configuration file.

    Args:
        output_path: Path to output file
    """
    default_config = {
        "base_url": "http://localhost:8000",
        "concurrency": 5,
        "timeout": 30,
        "endpoints": [
            # Ticker endpoints for popular stocks
            "/v1/ticker/AAPL/basic-info",
            "/v1/ticker/AAPL/history",
            "/v1/ticker/AAPL/balance-sheet",
            "/v1/ticker/AAPL/cash-flow",
            "/v1/ticker/AAPL/income-stmt",
            "/v1/ticker/MSFT/basic-info",
            "/v1/ticker/MSFT/history",
            "/v1/ticker/GOOG/basic-info",
            "/v1/ticker/GOOG/history",
            "/v1/ticker/AMZN/basic-info",
            "/v1/ticker/AMZN/history",

            # Market endpoints
            "/v1/market/US/status",
            "/v1/market/US/summary",

            # Search endpoints
            "/v1/search/apple/all",
            "/v1/search/microsoft/all",
            "/v1/search/amazon/all",

            # Sector endpoints
            "/v1/sector/technology/overview",
            "/v1/sector/healthcare/overview",
            "/v1/sector/financials/overview",

            # Industry endpoints
            "/v1/industry/software/overview",
            "/v1/industry/semiconductors/overview",
            "/v1/industry/biotechnology/overview"
        ]
    }

    with open(output_path, "w") as f:
        json.dump(default_config, f, indent=2)

    logger.info(f"Generated default configuration at {output_path}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Warm up the API cache with common requests")
    parser.add_argument(
        "-c", "--config",
        help="Path to warmup configuration file",
        default=DEFAULT_CONFIG_PATH
    )
    parser.add_argument(
        "-b", "--base-url",
        help="Base URL for the API (overrides config)",
        default=None
    )
    parser.add_argument(
        "-n", "--concurrency",
        help="Maximum number of concurrent requests",
        type=int,
        default=None
    )
    parser.add_argument(
        "-t", "--timeout",
        help="Request timeout in seconds",
        type=int,
        default=None
    )
    parser.add_argument(
        "-g", "--generate-config",
        help="Generate a default configuration file",
        action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    return parser.parse_args()


async def main():
    """Main entry point."""
    # Parse arguments
    args = parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Generate default configuration if requested
    if args.generate_config:
        generate_default_config(Path(args.config))
        return

    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        logger.info("Run with --generate-config to create a default configuration file")
        sys.exit(1)

    config = load_warmup_config(config_path)

    # Override configuration with command line arguments
    base_url = args.base_url or config["base_url"]
    concurrency = args.concurrency or config.get("concurrency", DEFAULT_CONCURRENCY)
    timeout = args.timeout or config.get("timeout", 30)
    endpoints = config["endpoints"]

    # Log configuration
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Concurrency: {concurrency}")
    logger.info(f"Timeout: {timeout}s")
    logger.info(f"Endpoints: {len(endpoints)}")

    # Warm up endpoints
    start_time = time.time()
    results = await warm_up_endpoints(base_url, endpoints, concurrency, timeout)
    total_time = time.time() - start_time

    # Count successful requests
    successful = sum(1 for r in results.values() if r["status"] == 200)

    # Log results
    logger.info(f"Cache warmup completed in {total_time:.2f}s")
    logger.info(f"Successful requests: {successful}/{len(endpoints)}")

    # Log failed requests
    failed = {e: r for e, r in results.items() if r["status"] != 200}
    if failed:
        logger.warning(f"Failed requests: {len(failed)}")
        for endpoint, result in failed.items():
            logger.warning(f"  {endpoint}: Status {result['status']}")

    # Calculate statistics
    times = [r["time"] for r in results.values() if r["status"] == 200]
    if times:
        avg_time = sum(times) / len(times)
        max_time = max(times)
        min_time = min(times)
        logger.info(f"Average request time: {avg_time:.3f}s")
        logger.info(f"Maximum request time: {max_time:.3f}s")
        logger.info(f"Minimum request time: {min_time:.3f}s")


if __name__ == "__main__":
    asyncio.run(main())