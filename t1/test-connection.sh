#!/bin/bash

# ZIEL-MAS Connection Test Script
# This script tests the connection between frontend and backend

echo "🔍 Testing ZIEL-MAS Frontend-Backend Connection..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test function
test_endpoint() {
    local name=$1
    local url=$2
    local expected=$3

    echo -n "Testing $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected)"
        return 1
    fi
}

# Configuration
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:3000}"

echo "Backend URL: $BACKEND_URL"
echo "Frontend URL: $FRONTEND_URL"
echo ""

# Test Backend Health
echo "=== Backend Health Tests ==="
test_endpoint "Health Check" "$BACKEND_URL/health" "200"
test_endpoint "API Docs" "$BACKEND_URL/docs" "200"
echo ""

# Test API Endpoints
echo "=== API Endpoint Tests ==="
test_endpoint "Stats Endpoint" "$BACKEND_URL/api/v1/stats" "200"

# Test Task Creation (will fail without proper data, but should return 4xx not 5xx)
echo -n "Testing Create Task Endpoint (validates endpoint exists)... "
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BACKEND_URL/api/v1/create-task" \
  -H "Content-Type: application/json" \
  -d '{"intent":"test"}')
if [ "$response" -ge 400 ] && [ "$response" -lt 500 ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $response - endpoint exists, validation working)"
elif [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $response - endpoint working)"
else
    echo -e "${RED}✗ FAIL${NC} (HTTP $response)"
fi
echo ""

# Test Frontend
echo "=== Frontend Tests ==="
test_endpoint "Frontend Home" "$FRONTEND_URL" "200"
test_endpoint "Frontend Robots" "$FRONTEND_URL/robots.txt" "200"
echo ""

# Test CORS
echo "=== CORS Test ==="
echo -n "Testing CORS headers... "
cors=$(curl -s -I "$BACKEND_URL/health" | grep -i "access-control-allow-origin")
if [ -n "$cors" ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  $cors"
else
    echo -e "${YELLOW}⚠ WARNING${NC} - CORS headers not found"
fi
echo ""

# Test Services
echo "=== Service Availability ==="
echo -n "MongoDB... "
if lsof -i :27017 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
fi

echo -n "Redis... "
if lsof -i :6379 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
fi

echo -n "Backend... "
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
fi

echo -n "Frontend... "
if lsof -i :3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Running${NC}"
else
    echo -e "${RED}✗ Not running${NC}"
fi

echo ""
echo "=== Test Complete ==="
echo ""
echo "If all tests pass, your frontend and backend are properly connected!"
echo ""
echo "Next steps:"
echo "1. Open $FRONTEND_URL in your browser"
echo "2. Create a test task"
echo "3. Monitor the execution in real-time"
