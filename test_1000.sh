#!/bin/bash
# Test live trading with 1000 Pauls - one cycle

cd /Users/brain/.openclaw/workspace/swimming_pauls

echo "🚀 Testing Live Trading with 1000 Pauls"
echo "========================================"

# Run one cycle
python3 live_trading.py once 2>&1 | head -150

echo ""
echo "✅ Test complete"
echo "To run continuous: ./run_1000_pauls.sh"