#!/bin/bash
# Swimming Pauls - Quick Test Script
# Run this to verify all components are working

set -e

echo "🧪 Swimming Pauls Test Suite"
echo "============================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Helper function
run_test() {
    local name=$1
    local command=$2
    echo -n "Testing $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAILED++))
        return 1
    fi
}

echo ""
echo "📦 1. Checking Dependencies..."
echo "------------------------------"

run_test "Python 3" "python3 --version"
run_test "Node.js" "node --version"
run_test "npm" "npm --version"
run_test "SQLite3" "sqlite3 --version"

echo ""
echo "🔌 2. Testing API Endpoints..."
echo "------------------------------"

run_test "World V2 API" "curl -s http://localhost:3001/api/stats"
run_test "World V3 API" "curl -s http://localhost:3002/api/stats"
run_test "World V2 Buildings" "curl -s http://localhost:3001/api/buildings"
run_test "World V3 Buildings" "curl -s http://localhost:3002/api/buildings"

echo ""
echo "🗄️  3. Testing Database..."
echo "------------------------------"

run_test "Database exists" "test -f data/predictions.db"
run_test "Database readable" "python3 -c \"import sqlite3; conn = sqlite3.connect('data/predictions.db'); conn.close()\""

echo ""
echo "🌐 4. Testing WebSocket..."
echo "------------------------------"

# Check if WebSocket server is running
if lsof -ti:8765 > /dev/null 2>&1; then
    echo -e "WebSocket Server... ${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "WebSocket Server... ${YELLOW}⚠ NOT RUNNING${NC} (Start with: python local_agent.py)"
fi

echo ""
echo "🎮 5. Testing World Simulation..."
echo "------------------------------"

# Check if World V2 is running
if lsof -ti:3001 > /dev/null 2>&1; then
    echo -e "World V2 Server... ${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "World V2 Server... ${YELLOW}⚠ NOT RUNNING${NC} (Start with: cd pauls-world-v2 && npm start)"
fi

# Check if World V3 is running
if lsof -ti:3002 > /dev/null 2>&1; then
    echo -e "World V3 Server... ${GREEN}✓ RUNNING${NC}"
    ((PASSED++))
else
    echo -e "World V3 Server... ${YELLOW}⚠ NOT RUNNING${NC} (Start with: cd pauls-world-v3 && npm start)"
fi

echo ""
echo "🤖 6. Testing Prediction Engine..."
echo "------------------------------"

# Quick prediction test (if dependencies available)
if python3 -c "import openai" 2>/dev/null; then
    echo "OpenAI available - prediction tests possible"
else
    echo -e "${YELLOW}⚠ OpenAI not configured - skipping prediction tests${NC}"
fi

echo ""
echo "📊 7. Checking File Structure..."
echo "------------------------------"

run_test "Main app exists" "test -f swimming_pauls.py"
run_test "Config exists" "test -f config.yaml"
run_test "World V2 exists" "test -d pauls-world-v2"
run_test "World V3 exists" "test -d pauls-world-v3"
run_test "App folder exists" "test -d app"

echo ""
echo "============================"
echo "📈 TEST RESULTS"
echo "============================"
echo -e "${GREEN}✓ Passed: $PASSED${NC}"
echo -e "${RED}✗ Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${YELLOW}⚠ Some tests failed. Check the output above.${NC}"
    exit 1
fi
