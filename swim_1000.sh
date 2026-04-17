#!/bin/bash
# Start continuous live trading with 1000 Pauls

cd /Users/brain/.openclaw/workspace/swimming_pauls

echo "🏊‍♂️ 1000 PAULS NOW SWIMMING!"
echo "============================"
echo "Started: $(date)"
echo "Interval: 60 seconds"
echo "Log: live_trading_1000.log"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 live_trading.py continuous 60 2>&1 | tee live_trading_1000.log