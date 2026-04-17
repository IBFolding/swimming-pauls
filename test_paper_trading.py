#!/usr/bin/env python3
"""
Test Paper Trading System with Simulated Price Updates
"""
import random
from paper_trading import PaperTradingManager

# Initialize manager
manager = PaperTradingManager()

print("🧪 PAPER TRADING TEST - Simulated Price Updates")
print("=" * 60)

# Get current open trades
open_trades = [t for t in manager.trades.values() if t.status.value == "open"]
print(f"Starting with {len(open_trades)} open trades")

# Simulate price movements for 5 rounds
for round_num in range(1, 6):
    print(f"\n📊 Round {round_num}: Simulating Price Updates")
    print("-" * 60)
    
    # Generate random prices for symbols that have open trades
    symbols = list(set(t.symbol for t in open_trades if t.status.value == "open"))
    prices = {}
    
    for sym in symbols[:10]:  # Test with first 10 symbols
        # Random price between $50 and $200
        prices[sym] = random.uniform(50, 200)
    
    print(f"Updating prices for {len(prices)} symbols...")
    
    # Update prices (this triggers stop loss / take profit checks)
    manager.update_prices(prices)
    
    # Count current state
    open_count = len([t for t in manager.trades.values() if t.status.value == "open"])
    closed_count = len([t for t in manager.trades.values() if t.status.value == "closed"])
    stopped_count = len([t for t in manager.trades.values() if t.status.value == "stopped"])
    
    print(f"  Trades: {open_count} open, {closed_count} closed, {stopped_count} stopped")

# Final leaderboard
print("\n" + "=" * 60)
print("🏆 FINAL LEADERBOARD AFTER SIMULATION")
print("=" * 60)

leaderboard = manager.get_leaderboard(10)

if leaderboard:
    for i, paul in enumerate(leaderboard, 1):
        badge = "🏆" if paul.get('proven_trader') else ""
        print(f"{i:2d}. {paul['paul_name']:<25} {badge}")
        print(f"    Value: ${paul['total_value']:>10,.2f} ({paul['roi']:>+7.1%})")
        print(f"    Win Rate: {paul['win_rate']:>6.0%} | Trades: {paul['total_trades']}")
        print()
else:
    print("No Pauls qualify for leaderboard yet (need trades with results)")

# Check for proven traders
proven = manager.get_proven_traders()
print(f"\n🏆 PROVEN TRADERS: {len(proven)} total")
if proven:
    for name in proven[:5]:
        print(f"  ✓ {name}")
else:
    print("  (None yet - need 50+ trades and 60%+ win rate)")

print("\n✅ Test complete!")
