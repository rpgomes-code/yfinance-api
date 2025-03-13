#!/usr/bin/env python
"""
Script to clean up generated files and cache.

This script helps maintain a clean development environment by removing
generated files, cache, and other temporary artifacts.
"""
import argparse
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List, Set, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Default paths
DEFAULT_APP_DIR = Path(__file__).parent.parent

# Files and directories to clean
CLEANUP_PATTERNS = {
    "cache": [
        "**/__pycache__",
        "**/.pytest_cache",
        "**/.coverage",
        "**/htmlcov",
        ".coverage",
        "coverage.xml",
    ],
    "build": [
        "build/",
        "dist/",
        "*.egg-info/",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.pyd",
    ],
    "docs": [
        "docs/generated/",
    ],
    "logs": [
        "logs/",
        "*.log",
    ],
    "temp": [
        ".tmp/",
        "tmp/",
        "**/.DS_Store",
    ],
    "venv": [
        "venv/",
        ".venv/",
        "env/",
        ".env/",
    ]
}


def find_matching_paths(
        base_dir: Path,
        patterns: List[str],
        exclude_dirs: Set[str] = None
) -> List[Path]:
    """
    Find paths matching the given patterns.

    Args:
        base_dir: Base directory to search
        patterns: List of glob patterns
        exclude_dirs: Set of directory names to exclude

    Returns:
        List[Path]: List of matching paths
    """
    exclude_dirs = exclude_dirs or set()
    matching_paths = []

    for pattern in patterns:
        for path in base_dir.glob(pattern):
            # Skip excluded directories
            if any(parent.name in exclude_dirs for parent in path.parents):
                continue

            matching_paths.append(path)

    return matching_paths


def remove_paths(paths: List[Path], dry_run: bool = False) -> int:
    """
    Remove the given paths.

    Args:
        paths: List of paths to remove
        dry_run: Whether to perform a dry run

    Returns:
        int: Number of paths removed
    """
    removed_count = 0

    for path in paths:
        try:
            if dry_run:
                logger.info(f"Would remove: {path}")
                removed_count += 1
            else:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                logger.info(f"Removed: {path}")
                removed_count += 1
        except (PermissionError, OSError) as e:
            logger.warning(f"Error removing {path}: {str(e)}")

    return removed_count


def clean_redis_cache(
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        prefix: str = "yfinance_api:",
        dry_run: bool = False
) -> int:
    """
    Clean Redis cache.

    Args:
        host: Redis host
        port: Redis port
        db: Redis database
        password: Redis password
        prefix: Key prefix to clean
        dry_run: Whether to perform a dry run

    Returns:
        int: Number of keys removed
    """
    try:
        import redis
    except ImportError:
        logger.warning("Redis package not installed. Skipping Redis cache cleanup.")
        return 0

    try:
        # Connect to Redis
        r = redis.Redis(host=host, port=port, db=db, password=password)

        # Test connection
        r.ping()

        # Find keys with prefix
        keys = r.keys(f"{prefix}*")

        if not keys:
            logger.info(f"No keys found with prefix '{prefix}'")
            return 0

        # Remove keys
        if dry_run:
            logger.info(f"Would remove {len(keys)} Redis keys with prefix '{prefix}'")
            return len(keys)
        else:
            if len(keys) > 0:
                r.delete(*keys)
            logger.info(f"Removed {len(keys)} Redis keys with prefix '{prefix}'")
            return len(keys)

    except redis.RedisError as e:
        logger.warning(f"Error cleaning Redis cache: {str(e)}")
        return 0


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Clean up generated files and cache")
    parser.add_argument(
        "-d", "--directory",
        help="Base directory to clean",
        default=DEFAULT_APP_DIR
    )
    parser.add_argument(
        "--cache",
        help="Clean Python cache files",
        action="store_true"
    )
    parser.add_argument(
        "--build",
        help="Clean build artifacts",
        action="store_true"
    )
    parser.add_argument(
        "--docs",
        help="Clean generated documentation",
        action="store_true"
    )
    parser.add_argument(
        "--logs",
        help="Clean log files",
        action="store_true"
    )
    parser.add_argument(
        "--temp",
        help="Clean temporary files",
        action="store_true"
    )
    parser.add_argument(
        "--venv",
        help="Clean virtual environments",
        action="store_true"
    )
    parser.add_argument(
        "--redis",
        help="Clean Redis cache",
        action="store_true"
    )
    parser.add_argument(
        "--redis-host",
        help="Redis host",
        default="localhost"
    )
    parser.add_argument(
        "--redis-port",
        help="Redis port",
        type=int,
        default=6379
    )
    parser.add_argument(
        "--redis-db",
        help="Redis database",
        type=int,
        default=0
    )
    parser.add_argument(
        "--redis-password",
        help="Redis password",
        default=None
    )
    parser.add_argument(
        "--redis-prefix",
        help="Redis key prefix to clean",
        default="yfinance_api:"
    )
    parser.add_argument(
        "--all",
        help="Clean everything",
        action="store_true"
    )
    parser.add_argument(
        "--dry-run",
        help="Perform a dry run without removing anything",
        action="store_true"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Enable verbose output",
        action="store_true"
    )
    parser.add_argument(
        "-e", "--exclude",
        help="Directories to exclude (comma-separated)",
        default=""
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_args()

    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Set base directory
    base_dir = Path(args.directory)
    if not base_dir.exists():
        logger.error(f"Base directory not found: {base_dir}")
        sys.exit(1)

    # Set options
    if args.all:
        clean_cache = clean_build = clean_docs = True
        clean_logs = clean_temp = clean_venv = clean_redis = True
    else:
        clean_cache = args.cache
        clean_build = args.build
        clean_docs = args.docs
        clean_logs = args.logs
        clean_temp = args.temp
        clean_venv = args.venv
        clean_redis = args.redis

        # Default to cache if nothing specified
        if not any([clean_cache, clean_build, clean_docs, clean_logs, clean_temp, clean_venv, clean_redis]):
            clean_cache = True

    # Parse excluded directories
    exclude_dirs = set(d.strip() for d in args.exclude.split(",") if d.strip())

    # Log configuration
    logger.info(f"Base directory: {base_dir}")
    logger.info(f"Excluded directories: {', '.join(exclude_dirs) if exclude_dirs else 'None'}")
    if args.dry_run:
        logger.info("Dry run mode - not removing any files")

    total_removed = 0

    # Clean Python cache
    if clean_cache:
        logger.info("Cleaning Python cache files...")
        paths = find_matching_paths(base_dir, CLEANUP_PATTERNS["cache"], exclude_dirs)
        removed = remove_paths(paths, args.dry_run)
        logger.info(f"Removed {removed} Python cache files/directories")
        total_removed += removed

    # Clean build artifacts
    if clean_build:
        logger.info("Cleaning build artifacts...")
        paths = find_matching_paths(base_dir, CLEANUP_PATTERNS["build"], exclude_dirs)
        removed = remove_paths(paths, args.dry_run)
        logger.info(f"Removed {removed} build artifacts")
        total_removed += removed

    # Clean generated documentation
    if clean_docs:
        logger.info("Cleaning generated documentation...")
        paths = find_matching_paths(base_dir, CLEANUP_PATTERNS["docs"], exclude_dirs)
        removed = remove_paths(paths, args.dry_run)
        logger.info(f"Removed {removed} documentation files/directories")
        total_removed += removed

    # Clean log files
    if clean_logs:
        logger.info("Cleaning log files...")
        paths = find_matching_paths(base_dir, CLEANUP_PATTERNS["logs"], exclude_dirs)
        removed = remove_paths(paths, args.dry_run)
        logger.info(f"Removed {removed} log files/directories")
        total_removed += removed

    # Clean temporary files
    if clean_temp:
        logger.info("Cleaning temporary files...")
        paths = find_matching_paths(base_dir, CLEANUP_PATTERNS["temp"], exclude_dirs)
        removed = remove_paths(paths, args.dry_run)
        logger.info(f"Removed {removed} temporary files/directories")
        total_removed += removed

    # Clean virtual environments
    if clean_venv:
        logger.info("Cleaning virtual environments...")
        paths = find_matching_paths(base_dir, CLEANUP_PATTERNS["venv"], exclude_dirs)
        removed = remove_paths(paths, args.dry_run)
        logger.info(f"Removed {removed} virtual environments")
        total_removed += removed

    # Clean Redis cache
    if clean_redis:
        logger.info("Cleaning Redis cache...")
        removed = clean_redis_cache(
            host=args.redis_host,
            port=args.redis_port,
            db=args.redis_db,
            password=args.redis_password,
            prefix=args.redis_prefix,
            dry_run=args.dry_run
        )
        total_removed += removed

    # Summary
    if args.dry_run:
        logger.info(f"Would remove {total_removed} files/directories in total")
    else:
        logger.info(f"Removed {total_removed} files/directories in total")


if __name__ == "__main__":
    main()