#!/bin/bash
# Development helper: build, start server, run tests
# Usage: ./scripts/dev-test.sh [unit|e2e|all]

set -e

cd "$(dirname "$0")/../frontend"

MODE="${1:-all}"

echo "Development Test Helper"
echo "======================="

# Check if we're in a devcontainer
if [ -n "$DEVCONTAINER" ] || [ -f "/.dockerenv" ]; then
  echo "Detected devcontainer environment"
  IN_DEVCONTAINER=true
else
  IN_DEVCONTAINER=false
fi

case "$MODE" in
  unit)
    echo "Running unit tests in watch mode..."
    npm run test
    ;;

  e2e)
    echo "Preparing for E2E tests..."

    # Build if needed
    if [ ! -d "dist" ]; then
      echo "Building app..."
      npm run build
    fi

    if [ "$IN_DEVCONTAINER" = true ]; then
      echo ""
      echo "In devcontainer, please run in two terminals:"
      echo "  Terminal 1: npm run preview -- --port 4173 --host"
      echo "  Terminal 2: npm run test:e2e:headed"
      echo ""
      echo "Or use: ./scripts/test-e2e.sh ci (slower, self-contained)"
    else
      echo "Running E2E with auto server..."
      npm run test:e2e
    fi
    ;;

  all)
    echo "Running full test suite..."

    echo ""
    echo "1. Unit tests"
    echo "=============="
    npm run test:run

    echo ""
    echo "2. E2E tests"
    echo "=============="

    # Build if needed
    if [ ! -d "dist" ]; then
      echo "Building app..."
      npm run build
    fi

    if [ "$IN_DEVCONTAINER" = true ]; then
      echo ""
      echo "In devcontainer environment:"
      echo "  Please run preview server in another terminal:"
      echo "    npm run preview -- --port 4173 --host"
      echo ""
      echo "  Then run: npm run test:e2e:headed"
      echo ""
      echo "  Or use CI mode: ./scripts/test-all.sh ci"
    else
      npm run test:e2e:ci
    fi
    ;;

  build)
    echo "Building app for testing..."
    npm run build
    echo ""
    echo "Start preview server:"
    echo "  npm run preview -- --port 4173 --host"
    ;;

  server)
    echo "Starting preview server..."
    npm run preview -- --port 4173 --host
    ;;

  report)
    echo "Opening test report..."
    npx playwright show-report
    ;;

  *)
    echo "Usage: $0 [unit|e2e|all|build|server|report]"
    echo ""
    echo "Commands:"
    echo "  unit    - Unit tests in watch mode"
    echo "  e2e     - E2E tests (requires build)"
    echo "  all     - Full test suite"
    echo "  build   - Build app for testing"
    echo "  server  - Start preview server"
    echo "  report  - View Playwright HTML report"
    echo ""
    echo "DevContainer workflow:"
    echo "  1. ./scripts/dev-test.sh build"
    echo "  2. ./scripts/dev-test.sh server  (terminal 1)"
    echo "  3. ./scripts/dev-test.sh e2e     (terminal 2)"
    echo ""
    echo "CI workflow:"
    echo "  ./scripts/test-all.sh ci"
    exit 1
    ;;
esac
