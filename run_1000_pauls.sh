#!/bin/bash
# Run continuous live trading with all 1000 Pauls

cd /Users/brain/.openclaw/workspace/swimming_pauls

echo "🚀 Starting Continuous Live Trading with 1000 Pauls"
echo "=================================================="
echo ""
echo "Features:"
echo "  • Real CoinGecko market data"
echo "  • 1000 curated Pauls analyzing"
echo "  • 60-second intervals"
echo "  • Auto-breeding from top performers"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Run continuous mode with 60-second intervals
python3 live_trading.py continuous 60
