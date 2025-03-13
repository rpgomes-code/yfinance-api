#!/bin/bash
# Script to run tests for the YFinance API

set -e  # Exit on error

# Set environment variables
export PYTHONPATH=$PYTHONPATH:$(pwd)
export TESTING=1

# Default values
COVERAGE=0
VERBOSE=0
ENDPOINT_TYPE=""
TEST_PATH="tests"

# Parse arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -c|--coverage)
      COVERAGE=1
      shift
      ;;
    -v|--verbose)
      VERBOSE=1
      shift
      ;;
    -t|--endpoint-type)
      ENDPOINT_TYPE="$2"
      shift
      shift
      ;;
    -p|--path)
      TEST_PATH="$2"
      shift
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  -c, --coverage     Run tests with coverage"
      echo "  -v, --verbose      Run tests in verbose mode"
      echo "  -t, --endpoint-type Run tests for a specific endpoint type (ticker, market, search, sector, industry)"
      echo "  -p, --path         Run tests in a specific path"
      echo "  -h, --help         Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
  echo "Error: pytest is not installed"
  echo "Please install it with: pip install pytest"
  exit 1
fi

# Build test command
TEST_CMD="pytest"

if [ $VERBOSE -eq 1 ]; then
  TEST_CMD="$TEST_CMD -v"
fi

# Add endpoint type if specified
if [ -n "$ENDPOINT_TYPE" ]; then
  echo "Running tests for endpoint type: $ENDPOINT_TYPE"
  TEST_PATH="tests/api/routes/v1/yfinance/$ENDPOINT_TYPE"
fi

# Add test path
TEST_CMD="$TEST_CMD $TEST_PATH"

# Run with coverage if requested
if [ $COVERAGE -eq 1 ]; then
  # Check if pytest-cov is installed
  if ! python -c "import pytest_cov" &> /dev/null; then
    echo "Error: pytest-cov is not installed"
    echo "Please install it with: pip install pytest-cov"
    exit 1
  fi

  echo "Running tests with coverage..."
  TEST_CMD="$TEST_CMD --cov=app --cov-report=term --cov-report=html"
else
  echo "Running tests..."
fi

# Display test command
echo "Test command: $TEST_CMD"
echo "-----------------------------------"

# Run tests
$TEST_CMD

# Exit with test command exit code
exit $?