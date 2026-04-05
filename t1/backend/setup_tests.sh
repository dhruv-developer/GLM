#!/bin/bash

# ZIEL-MAS Backend Test Setup Script
# Quick setup for running backend tests

set -e

echo "=================================================="
echo "ZIEL-MAS Backend Test Setup"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo ""
echo "Installing testing dependencies..."
pip install -r requirements_test.txt --quiet

echo "✓ Testing dependencies installed"

# Check if MongoDB and Redis are available
echo ""
echo "Checking for MongoDB..."
if command -v mongod &> /dev/null || docker ps | grep -q mongo; then
    echo "✓ MongoDB is available"
else
    echo "⚠ MongoDB not found - tests will use mongomock (in-memory)"
fi

echo ""
echo "Checking for Redis..."
if command -v redis-server &> /dev/null || docker ps | grep -q redis; then
    echo "✓ Redis is available"
else
    echo "⚠ Redis not found - tests will use mock Redis"
fi

# Run quick smoke test
echo ""
echo "=================================================="
echo "Running Quick Smoke Test"
echo "=================================================="
echo ""

python run_tests.py --quick --verbose

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "To run all tests:"
echo "  python run_tests.py --all"
echo ""
echo "To run specific test categories:"
echo "  python run_tests.py --unit"
echo "  python run_tests.py --integration"
echo "  python run_tests.py --security"
echo "  python run_tests.py --performance"
echo ""
echo "To run with coverage:"
echo "  python run_tests.py --coverage"
echo ""
echo "For more information, see tests/README.md"
echo ""
