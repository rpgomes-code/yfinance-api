#!/bin/bash
# Script to build Docker images for the YFinance API

set -e  # Exit on error

# Default values
TAG="latest"
PUSH=0
REGISTRY=""
BUILD_ARG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -t|--tag)
      TAG="$2"
      shift
      shift
      ;;
    -p|--push)
      PUSH=1
      shift
      ;;
    -r|--registry)
      REGISTRY="$2"
      shift
      shift
      ;;
    -b|--build-arg)
      BUILD_ARG="--build-arg $2"
      shift
      shift
      ;;
    -h|--help)
      echo "Usage: $0 [options]"
      echo ""
      echo "Options:"
      echo "  -t, --tag TAG      Set the image tag (default: latest)"
      echo "  -p, --push         Push the image to the registry"
      echo "  -r, --registry REG Set the registry (default: none)"
      echo "  -b, --build-arg ARG Additional build argument"
      echo "  -h, --help         Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Set image name
IMAGE_NAME="yfinance-api"
if [ -n "$REGISTRY" ]; then
  IMAGE_NAME="$REGISTRY/$IMAGE_NAME"
fi

# Full image reference
IMAGE="$IMAGE_NAME:$TAG"

echo "Building Docker image: $IMAGE"
echo "-----------------------------------"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
  echo "Error: Docker is not installed or not in PATH"
  exit 1
fi

# Check if Dockerfile exists
if [ ! -f "Dockerfile" ]; then
  echo "Error: Dockerfile not found in current directory"
  exit 1
fi

# Build the image
echo "Building image..."
docker build -t "$IMAGE" $BUILD_ARG .

# Tag as latest if not already
if [ "$TAG" != "latest" ]; then
  echo "Tagging as latest..."
  docker tag "$IMAGE" "$IMAGE_NAME:latest"
fi

# Push if requested
if [ $PUSH -eq 1 ]; then
  echo "Pushing image to registry..."
  docker push "$IMAGE"

  # Push latest if not the same
  if [ "$TAG" != "latest" ]; then
    docker push "$IMAGE_NAME:latest"
  fi

  echo "Image pushed successfully"
fi

echo "-----------------------------------"
echo "Docker image built successfully: $IMAGE"