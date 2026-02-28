#!/bin/bash

# VMS Backend Test Runner
# Runs all tests with coverage reporting

set -e

echo "=========================================="
echo "VMS Backend Test Suite"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to backend directory
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q pytest pytest-asyncio pytest-cov httpx

# Run tests
echo ""
echo -e "${YELLOW}Running tests...${NC}"
echo ""

# Run with coverage
pytest \
    --verbose \
    --cov=app \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    tests/

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Coverage report generated in: backend/htmlcov/index.html"
else
    echo ""
    echo -e "${RED}✗ Some tests failed!${NC}"
    exit 1
fi

# Deactivate virtual environment
deactivate

echo ""
echo "=========================================="
echo "Test run complete"
echo "=========================================="
