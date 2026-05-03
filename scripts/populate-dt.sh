#!/bin/bash
# Script to populate Dependency-Track with sample OSS project SBOMs

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv-populator"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Dependency-Track SBOM Populator${NC}"
echo "================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 is not installed${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "→ Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install dependencies
if [ ! -f "$VENV_DIR/.installed" ] || [ "$SCRIPT_DIR/requirements-sbom-populator.txt" -nt "$VENV_DIR/.installed" ]; then
    echo "→ Installing dependencies..."
    pip install -q -r "$SCRIPT_DIR/requirements-sbom-populator.txt"
    touch "$VENV_DIR/.installed"
fi

# Run the populator
echo ""
echo -e "${YELLOW}Starting SBOM population...${NC}"
python3 "$SCRIPT_DIR/populate_dt_with_sboms.py" "$@"
