#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="${SCRIPT_DIR}/../frontend"

cd "$FRONTEND_DIR"

echo "Running frontend tests from: $(pwd)"
echo "================================"

npm ci

if [[ "$1" == "--coverage" ]]; then
    echo "Running tests with coverage..."
    npm run test:run -- --coverage
    echo ""
    echo "Coverage report generated at: frontend/coverage/index.html"
else
    npm run test:run
fi

echo "================================"
echo "Tests complete"
