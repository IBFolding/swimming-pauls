#!/usr/bin/env python3
"""
Quick Paper Trading Test - Small Scale
"""
import random
from paper_trading import PaperTradingManager, PaperPortfolio

# Create fresh manager for testing
manager = PaperTradingManager(db_path="data/paper_trading_test.db")

print("🧪 QUICK PAPER TRADING TEST")
print("=" * 60)

# Create 5 test Pauls
test_pauls = ["Visionary Paul", "Trader Paul", "Degen Paul", "Skeptic Paul", "Quant Paul"]

print("\n1. Creating portfolios...")
for paul in test_pauls:
    portfolio = manager.create_portfolio(paul, initial_balance=10000.0, enabled=True)
    print(f"  ✅ {paul}: ${portfolio.initial_balance:,.2f}")

print("\n2. Simulating trades...")
# Simulate 10 trades per Paul
for paul in test_pauls:
    for i in range(10):
        symbol = random.choice(["BTC", "ETH", "SOL"])
        direction = random.choice(["buy", "sell"])
        confidence = random.uniform(0.75, 0.95)
        entry_price = random.uniform(50000, 70000) if symbol == "BTC" else random.uniform(2000, 4000)
        
        trade = manager.execute_trade(
            paul_name=paul,
            symbol=symbol,
            direction=direction,
            current_price=entry_price,
            confidence=confidence
        )
        
        if trade:
            # Simulate price movement and close 70% of trades
            if random.random() < 0.7:
                exit_price = entry_price * random.uniform(0.9, 1.15)  # -10% to +15%
                reason = random.choice(["manual", "take_profit", "stop_loss"])
                manager.close_trade(trade.id, exit_price, reason)

print(f"\n3. Trades executed: {len(manager.trades)}")

print("\n4. Leaderboard:")
print("-" * 60)
leaderboard = manager.get_leaderboard(10)

for i, paul in enumerate(leaderboard, 1):
    badge = "🏆" if paul.get('proven_trader') else ""
    print(f"{i}. {paul['paul_name']:<20} ${paul['total_value']:>10,.2f} ({paul['roi']:>+6.1%}) {badge}")
    print(f"   Trades: {paul['total_trades']} | Win Rate: {paul['win_rate']:.0%} | DD: {paul['max_drawdown']:.1%}")

proven = manager.get_proven_traders()
print(f"\n5. Proven Traders: {len(proven)}")
for name in proven:
    print(f"   ✓ {name}")

print("\n✅ Test complete!")
