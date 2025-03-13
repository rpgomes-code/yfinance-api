#!/usr/bin/env python
"""
Script to benchmark API performance.

This script runs performance tests against the YFinance API to measure
response times, throughput, and error rates under various load scenarios.
"""
import argparse
import asyncio
import json
import logging
import statistics
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import random

import aiohttp
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default benchmark configuration
DEFAULT_CONFIG_PATH = Path(__file__).parent / "benchmark_config.json"


class BenchmarkResult:
    """Class to store benchmark results."""

    def __init__(
            self,
            name: str,
            concurrency: int,
            duration: float,
            requests: int,
            successful: int,
            failed: int,
            response_times: List[float]
    ):
        """
        Initialize benchmark result.

        Args:
            name: Benchmark name
            concurrency: Concurrency level
            duration: Test duration in seconds
            requests: Total requests
            successful: Successful requests
            failed: Failed requests
            response_times: List of response times
        """
        self.name = name
        self.concurrency = concurrency
        self.duration = duration
        self.requests = requests
        self.successful = successful
        self.failed = failed
        self.response_times = response_times

        # Calculate stats
        self.rps = requests / duration if duration > 0 else 0
        self.success_rate = (successful / requests) * 100 if requests > 0 else 0

        # Calculate percentiles
        self.percentiles = {}
        if response_times:
            self.min_time = min(response_times)
            self.max_time = max(response_times)
            self.avg_time = statistics.mean(response_times)
            self.median_time = statistics.median(response_times)
            self.percentiles = {
                "50": self.median_time,
                "90": np.percentile(response_times, 90),
                "95": np.percentile(response_times, 95),
                "99": np.percentile(response_times, 99)
            }
        else:
            self.min_time = 0
            self.max_time = 0
            self.avg_time = 0
            self.median_time = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "concurrency": self.concurrency,
            "duration": round(self.duration, 2),
            "requests": self.requests,
            "successful": self.successful,
            "failed": self.failed,
            "success_rate": round(self.success_rate, 2),
            "requests_per_second": round(self.rps, 2),
            "response_time": {
                "min": round(self.min_time * 1000, 2),  # Convert to ms
                "max": round(self.max_time * 1000, 2),  # Convert to ms
                "avg": round(self.avg_time * 1000, 2),  # Convert to ms
                "median": round(self.median_time * 1000, 2),  # Convert to ms
                "p90": round(self.percentiles.get("90", 0) * 1000, 2),  # Convert to ms
                "p95": round(self.percentiles.get("95", 0) * 1000, 2),  # Convert to ms
                "p99": round(self.percentiles.get("99", 0) * 1000, 2)  # Convert to ms
            }
        }


async def run_benchmark(
        name: str,
        base_url: str,
        endpoints: List[str],
        concurrency: int,
        duration: int,
        warmup_duration: int = 5,
        timeout: int = 30
) -> BenchmarkResult:
    """
    Run a benchmark test.

    Args:
        name: Benchmark name
        base_url: Base URL for the API
        endpoints: List of endpoint paths to test
        concurrency: Number of concurrent requests
        duration: Test duration in seconds
        warmup_duration: Warmup duration in seconds
        timeout: Request timeout in seconds

    Returns:
        BenchmarkResult: Benchmark results
    """
    logger.info(f"Starting benchmark: {name}")
    logger.info(f"Concurrency: {concurrency}, Duration: {duration}s")

    # Initialize counters
    request_count = 0
    success_count = 0
    fail_count = 0
    response_times = []

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(concurrency)

    # Flag to indicate benchmark is running
    running = True

    async def make_request(session: aiohttp.ClientSession) -> Tuple[bool, float]:
        """Make a request to a random endpoint."""
        nonlocal request_count

        # Select a random endpoint
        endpoint = random.choice(endpoints)
        url = f"{base_url}{endpoint}"

        # Make request
        start_time = time.time()
        try:
            async with session.get(url, timeout=timeout) as response:
                await response.text()  # Ensure response is read
                elapsed = time.time() - start_time
                return response.status == 200, elapsed
        except Exception as e:
            logger.debug(f"Error requesting {url}: {str(e)}")
            return False, time.time() - start_time

    async def worker(session: aiohttp.ClientSession, is_warmup: bool = False):
        """Worker task to make requests."""
        nonlocal request_count, success_count, fail_count

        while running:
            async with semaphore:
                success, elapsed = await make_request(session)

                if not is_warmup:
                    request_count += 1
                    if success:
                        success_count += 1
                        response_times.append(elapsed)
                    else:
                        fail_count += 1

    # Create HTTP session
    async with aiohttp.ClientSession() as session:
        # Start workers
        workers = []

        # Run warmup if requested
        if warmup_duration > 0:
            logger.info(f"Running warmup for {warmup_duration}s...")
            warmup_workers = [worker(session, True) for _ in range(concurrency)]
            await asyncio.gather(*warmup_workers, return_exceptions=True)
            logger.info("Warmup completed")

        # Start benchmark timer
        start_time = time.time()
        end_time = start_time + duration

        # Create progress bar
        pbar = tqdm(total=duration, desc=f"Benchmark: {name}")

        # Start workers
        for _ in range(concurrency):
            workers.append(asyncio.create_task(worker(session)))

        # Update progress bar
        while time.time() < end_time:
            await asyncio.sleep(0.5)
            elapsed = min(time.time() - start_time, duration)
            pbar.update(elapsed - pbar.n)

        # Stop benchmark
        running = False
        pbar.update(duration - pbar.n)
        pbar.close()

        # Wait for workers to complete
        for w in workers:
            w.cancel()

        await asyncio.gather(*workers, return_exceptions=True)

    # Calculate actual duration
    actual_duration = time.time() - start_time

    # Create result
    result = BenchmarkResult(
        name=name,
        concurrency=concurrency,
        duration=actual_duration,
        requests=request_count,
        successful=success_count,
        failed=fail_count,
        response_times=response_times
    )

    logger.info(f"Completed benchmark: {name}")
    logger.info(f"Requests: {request_count}, Successful: {success_count}, Failed: {fail_count}")
    logger.info(f"Requests/sec: {result.rps:.2f}, Success rate: {result.success_rate:.2f}%")
    logger.info(
        f"Avg response time: {result.avg_time * 1000:.2f}ms, 95th percentile: {result.percentiles.get('95', 0) * 1000:.2f}ms")

    return result


def plot_results(results: List[BenchmarkResult], output_dir: Path) -> None:
    """
    Plot benchmark results.

    Args:
        results: List of benchmark results
        output_dir: Output directory for plots
    """
    if not results:
        logger.warning("No results to plot")
        return

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Sort results by concurrency
    results.sort(key=lambda r: r.concurrency)

    # Extract data for plotting
    concurrencies = [r.concurrency for r in results]
    rps_values = [r.rps for r in results]
    avg_times = [r.avg_time * 1000 for r in results]  # Convert to ms
    p95_times = [r.percentiles.get("95", 0) * 1000 for r in results]  # Convert to ms
    success_rates = [r.success_rate for r in results]

    # Plot requests per second
    plt.figure(figsize=(10, 6))
    plt.plot(concurrencies, rps_values, marker='o', linestyle='-', linewidth=2)
    plt.xlabel('Concurrency')
    plt.ylabel('Requests per Second')
    plt.title('Throughput vs Concurrency')
    plt.grid(True)
    plt.savefig(output_dir / "throughput.png")

    # Plot response times
    plt.figure(figsize=(10, 6))
    plt.plot(concurrencies, avg_times, marker='o', linestyle='-', linewidth=2, label='Average')
    plt.plot(concurrencies, p95_times, marker='s', linestyle='-', linewidth=2, label='95th Percentile')
    plt.xlabel('Concurrency')
    plt.ylabel('Response Time (ms)')
    plt.title('Response Time vs Concurrency')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_dir / "response_time.png")

    # Plot success rate
    plt.figure(figsize=(10, 6))
    plt.plot(concurrencies, success_rates, marker='o', linestyle='-', linewidth=2)
    plt.xlabel('Concurrency')
    plt.ylabel('Success Rate (%)')
    plt.title('Success Rate vs Concurrency')
    plt.grid(True)
    plt.ylim(min(success_rates) - 5 if min(success_rates) < 95 else 95, 100.5)
    plt.savefig(output_dir / "success_rate.png")

    logger.info(f"Plots saved to {output_dir}")


def load_benchmark_config(config_path: Path) -> Dict[str, Any]:
    """
    Load benchmark configuration from a JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Dict[str, Any]: Benchmark configuration
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

        if "scenarios" not in config or not isinstance(config["scenarios"], list):
            logger.error("Missing or invalid 'scenarios' in configuration")
            sys.exit(1)

        return config
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error loading configuration file: {str(e)}")
        sys.exit(1)


def generate_default_config(output_path: Path) -> None:
    """
    Generate a default benchmark configuration file.

    Args:
        output_path: Path to output file
    """
    default_config = {
        "base_url": "http://localhost:8000",
        "timeout": 30,
        "warmup_duration": 5,
        "endpoints": [
            # Ticker endpoints for popular stocks
            "/v1/ticker/AAPL/basic-info",
            "/v1/ticker/AAPL/history",
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
            "/v1/search/microsoft/all"
        ],
        "scenarios": [
            {
                "name": "Low Concurrency",
                "concurrency": 1,
                "duration": 30
            },
            {
                "name": "Medium Concurrency",
                "concurrency": 5,
                "duration": 30
            },
            {
                "name": "High Concurrency",
                "concurrency": 10,
                "duration": 30
            },
            {
                "name": "Very High Concurrency",
                "concurrency": 20,
                "duration": 30
            }
        ]
    }

    with open(output_path, "w") as f:
        json.dump(default_config, f, indent=2)

    logger.info(f"Generated default configuration at {output_path}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Benchmark API performance")
    parser.add_argument(
        "-c", "--config",
        help="Path to benchmark configuration file",
        default=DEFAULT_CONFIG_PATH
    )
    parser.add_argument(
        "-b", "--base-url",
        help="Base URL for the API (overrides config)",
        default=None
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Output directory for results",
        default="benchmark_results"
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
    parser.add_argument(
        "-p", "--plot-only",
        help="Only generate plots from existing results",
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

    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate default configuration if requested
    if args.generate_config:
        generate_default_config(Path(args.config))
        return

    # Load results and plot if plot-only mode
    if args.plot_only:
        results_file = output_dir / "results.json"
        if not results_file.exists():
            logger.error(f"Results file not found: {results_file}")
            sys.exit(1)

        with open(results_file, "r") as f:
            results_data = json.load(f)

        # Convert raw results to BenchmarkResult objects
        results = []
        for r in results_data:
            # Extract response times (not stored in JSON)
            # We'll approximate based on other stats
            avg_time = r["response_time"]["avg"] / 1000  # Convert from ms
            response_times = [avg_time] * r["successful"]  # Dummy values

            result = BenchmarkResult(
                name=r["name"],
                concurrency=r["concurrency"],
                duration=r["duration"],
                requests=r["requests"],
                successful=r["successful"],
                failed=r["failed"],
                response_times=response_times
            )
            results.append(result)

        # Plot results
        plot_results(results, output_dir)
        return

    # Load configuration
    config_path = Path(args.config)
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        logger.info("Run with --generate-config to create a default configuration file")
        sys.exit(1)

    config = load_benchmark_config(config_path)

    # Override configuration with command line arguments
    base_url = args.base_url or config["base_url"]
    endpoints = config["endpoints"]
    scenarios = config["scenarios"]
    timeout = config.get("timeout", 30)
    warmup_duration = config.get("warmup_duration", 5)

    # Log configuration
    logger.info(f"Base URL: {base_url}")
    logger.info(f"Endpoints: {len(endpoints)}")
    logger.info(f"Scenarios: {len(scenarios)}")

    # Run benchmarks
    results = []
    for scenario in scenarios:
        result = await run_benchmark(
            name=scenario["name"],
            base_url=base_url,
            endpoints=endpoints,
            concurrency=scenario["concurrency"],
            duration=scenario["duration"],
            warmup_duration=warmup_duration,
            timeout=timeout
        )
        results.append(result)

    # Save results
    results_data = [r.to_dict() for r in results]
    with open(output_dir / "results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    # Plot results
    plot_results(results, output_dir)


if __name__ == "__main__":
    asyncio.run(main())