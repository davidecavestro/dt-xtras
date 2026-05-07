#!/bin/bash
# Run unit tests (Vitest) - fast, no browser needed
# Usage: ./scripts/test-unit.sh [watch|run]

set -e

cd "$(dirname "$0")/../frontend"

MODE="${1:-run}"

case "$MODE" in
  watch)
    echo "Running unit tests in watch mode..."
    npm run test
    ;;
  run|ci)
    echo "Running unit tests (one shot)..."
    npm run test:run
    ;;
  coverage)
    echo "Running unit tests with coverage..."
    npm run test:ci
    ;;
  *)
    echo "Usage: $0 [watch|run|coverage]"
    echo "  watch    - Run tests in watch mode (for development)"
    echo "  run      - Run tests once (default)"
    echo "  coverage - Run tests with coverage report"
    exit 1
    ;;
esac
