#!/bin/bash
# Script to deploy the YFinance API to an environment

set -e  # Exit on error

# Default values
ENVIRONMENT="staging"
IMAGE_TAG="latest"
SKIP_TESTS=0
SKIP_BUILD=0
DRY_RUN=0
CONFIG_FILE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -e|--environment)
      ENVIRONMENT="$2"
      shift
      shift
      ;;
    -t|--tag)
      IMAGE_TAG="$2"
      shift
      shift
      ;;
    --skip-tests)
      SKIP_TESTS=1
      shift
      ;;
    --skip-build)
      SKIP_BUILD=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -c|--config)
      CONFIG_FILE="$2"
      shift
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  -e, --environment ENV Set the deployment environment (default: staging)"
      echo "  -t, --tag TAG         Set the image tag to deploy (default: latest)"
      echo "  --skip-tests          Skip running tests"
      echo "  --skip-build          Skip building the Docker image"
      echo "  --dry-run             Perform a dry run without making changes"
      echo "  -c, --config FILE     Specify a deployment config file"
      echo "  -h, --help            Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Check deployment environment
if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
  echo "Error: Invalid environment '$ENVIRONMENT'. Valid values are: development, staging, production"
  exit 1
fi

# Load config file if specified
if [ -n "$CONFIG_FILE" ]; then
  if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
  fi
  echo "Loading deployment config from $CONFIG_FILE"
  source "$CONFIG_FILE"
fi

# Prepend script directory to script paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Deploying YFinance API to $ENVIRONMENT environment"
echo "-----------------------------------"

# Step 1: Run tests (if not skipped)
if [ $SKIP_TESTS -eq 0 ]; then
  echo "Running tests..."
  if [ $DRY_RUN -eq 1 ]; then
    echo "[DRY RUN] Would run: $SCRIPT_DIR/run_tests.sh"
  else
    $SCRIPT_DIR/run_tests.sh
  fi
fi

# Step 2: Build Docker image (if not skipped)
if [ $SKIP_BUILD -eq 0 ]; then
  echo "Building Docker image..."
  if [ $DRY_RUN -eq 1 ]; then
    echo "[DRY RUN] Would run: $SCRIPT_DIR/docker_build.sh --tag $IMAGE_TAG"
  else
    $SCRIPT_DIR/docker_build.sh --tag $IMAGE_TAG
  fi
fi

# Step 3: Update deployment configuration
echo "Updating deployment configuration..."
DEPLOYMENT_FILE="$REPO_ROOT/deployments/$ENVIRONMENT/deployment.yaml"
if [ ! -f "$DEPLOYMENT_FILE" ]; then
  echo "Error: Deployment file not found: $DEPLOYMENT_FILE"
  exit 1
fi

if [ $DRY_RUN -eq 1 ]; then
  echo "[DRY RUN] Would update image tag in $DEPLOYMENT_FILE to $IMAGE_TAG"
else
  # Update image tag in deployment file
  sed -i "s|image: yfinance-api:.*|image: yfinance-api:$IMAGE_TAG|g" "$DEPLOYMENT_FILE"
fi

# Step 4: Apply deployment
echo "Applying deployment..."
if [ $DRY_RUN -eq 1 ]; then
  echo "[DRY RUN] Would apply deployment configuration: kubectl apply -f $DEPLOYMENT_FILE"
else
  kubectl apply -f "$DEPLOYMENT_FILE"
fi

# Step 5: Wait for deployment
echo "Waiting for deployment to complete..."
if [ $DRY_RUN -eq 1 ]; then
  echo "[DRY RUN] Would wait for deployment: kubectl rollout status deployment/yfinance-api -n $ENVIRONMENT"
else
  kubectl rollout status deployment/yfinance-api -n $ENVIRONMENT
fi

# Step 6: Run post-deployment checks
echo "Running post-deployment checks..."
if [ $DRY_RUN -eq 1 ]; then
  echo "[DRY RUN] Would run post-deployment checks"
else
  # Example: Check if API is responding
  API_URL="https://api.$ENVIRONMENT.yfinance-api.com/health"
  echo "Checking API health at $API_URL"

  for i in {1..10}; do
    if curl -s "$API_URL" | grep -q "healthy"; then
      echo "API is healthy!"
      break
    fi

    if [ $i -eq 10 ]; then
      echo "Error: API health check failed after 10 attempts"
      exit 1
    fi

    echo "API not healthy yet, retrying in 5 seconds... (attempt $i/10)"
    sleep 5
  done
fi

echo "-----------------------------------"
echo "Deployment to $ENVIRONMENT complete!"