#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

cd "$BACKEND_DIR"

echo "Running tests from: $(pwd)"
echo "================================"

pip install -r requirements.txt

if [[ "$1" == "--coverage" ]]; then
    echo "Running tests with coverage..."
    python -m pytest -v --cov=main --cov-report=term-missing --cov-report=html:htmlcov
    echo ""
    echo "Coverage report generated at: backend/htmlcov/index.html"
else
    python -m pytest -v --tb=short
fi

echo "================================"
echo "Tests complete"
