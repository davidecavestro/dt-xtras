#!/bin/bash
# Run all tests - both unit and E2E
# Usage: ./scripts/test-all.sh [ci|local]

set -e

cd "$(dirname "$0")/../frontend"

MODE="${1:-local}"

echo "========================================"
echo "Running Full Test Suite"
echo "Mode: $MODE"
echo "========================================"

case "$MODE" in
  ci)
    echo ""
    echo "Step 1/2: Unit tests with coverage..."
    echo "========================================"
    npm run test:ci

    echo ""
    echo "Step 2/2: E2E tests (CI mode)..."
    echo "========================================"
    npm run test:e2e:ci

    echo ""
    echo "========================================"
    echo "All tests passed!"
    echo "========================================"
    ;;

  local)
    echo ""
    echo "Step 1/2: Unit tests..."
    echo "========================================"
    npm run test:run

    echo ""
    echo "Step 2/2: E2E tests..."
    echo "========================================"

    # Check if preview server is running on port 4173
    if ! curl -s http://localhost:4173 > /dev/null 2>&1; then
      echo "Preview server not found, starting it..."
      npm run build
      npm run preview -- --port 4173 --host &
      PREVIEW_PID=$!
      echo "Waiting for preview server to start..."
      sleep 3

      # Verify server started
      if ! curl -s http://localhost:4173 > /dev/null 2>&1; then
        echo "Error: Failed to start preview server"
        kill $PREVIEW_PID 2>/dev/null || true
        exit 1
      fi
      echo "Preview server started (PID: $PREVIEW_PID)"
    else
      echo "Preview server already running"
      PREVIEW_PID=""
    fi

    npm run test:e2e

    # Clean up preview server if we started it
    if [ -n "$PREVIEW_PID" ]; then
      echo "Stopping preview server..."
      kill $PREVIEW_PID 2>/dev/null || true
    fi

    echo ""
    echo "========================================"
    echo "All tests passed!"
    echo "========================================"
    ;;

  *)
    echo "Usage: $0 [ci|local]"
    echo "  ci     - Full CI pipeline (self-contained, headless)"
    echo "  local  - Local development (auto-starts preview server)"
    echo ""
    echo "Examples:"
    echo "  ./scripts/test-all.sh ci     # Use in CI/CD"
    echo "  ./scripts/test-all.sh local  # For local dev (faster)"
    exit 1
    ;;
esac
