#!/bin/bash
# Run E2E tests (Playwright) - requires built app and preview server
# Usage: ./scripts/test-e2e.sh [headed|ui|debug|ci]

set -e

cd "$(dirname "$0")/../frontend"

MODE="${1:-headed}"

# Check if preview server is running
check_server() {
  curl -s -o /dev/null -w "%{http_code}" http://localhost:4173/ 2>/dev/null || echo "000"
}

# Build if needed
if [ ! -d "dist" ] || [ "$(find src -newer dist -type f 2>/dev/null | wc -l)" -gt 0 ]; then
  echo "Building app..."
  npm run build
fi

case "$MODE" in
  ci)
    echo "Running E2E tests in CI mode (headless, auto-managed server)..."
    npm run test:e2e:ci
    ;;
  headed)
    echo "Running E2E tests with headed browser..."
    echo "Make sure preview server is running: npm run preview -- --port 4173 --host"
    npm run test:e2e:headed
    ;;
  ui)
    echo "Running E2E tests in UI mode..."
    echo "Make sure preview server is running: npm run preview -- --port 4173 --host"
    npm run test:e2e:ui
    ;;
  debug)
    echo "Running E2E tests in debug mode..."
    echo "Make sure preview server is running: npm run preview -- --port 4173 --host"
    npm run test:e2e:debug
    ;;
  headless)
    echo "Running E2E tests headless..."
    echo "Make sure preview server is running: npm run preview -- --port 4173 --host"
    npm run test:e2e
    ;;
  server)
    echo "Starting preview server on port 4173..."
    npm run preview -- --port 4173 --host
    ;;
  *)
    echo "Usage: $0 [headed|headless|ui|debug|ci|server]"
    echo "  headed    - Run with visible browser (default, for debugging)"
    echo "  headless  - Run headless (requires preview server)"
    echo "  ui        - Interactive UI mode for debugging"
    echo "  debug     - Full debug mode with step-through"
    echo "  ci        - Self-contained: builds, starts server, tests, cleanup"
    echo "  server    - Just start the preview server"
    echo ""
    echo "For development:"
    echo "  Terminal 1: ./scripts/test-e2e.sh server"
    echo "  Terminal 2: ./scripts/test-e2e.sh headed"
    exit 1
    ;;
esac
