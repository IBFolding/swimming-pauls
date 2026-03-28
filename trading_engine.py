#!/usr/bin/env python3
"""Continuous paper trading simulation for 10,000 Pauls."""
import asyncio
import random
import time
import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from paul_world import PaulWorld

# Market prices (simulated)
MARKET_PRICES = {
    'BTC': 65000, 'ETH': 3500, 'SOL': 130, 
    'SPY': 500, 'AAPL': 180, 'TSLA': 180, 
    'NVDA': 900, 'DOGE': 0.15, 'LINK': 15,
    'UNI': 8, 'AAVE': 120, 'COMP': 65
}

async def simulate_market():
    """Simulate market price movements."""
    while True:
        for symbol in MARKET_PRICES:
            # Random walk (-2% to +2%)
            change = random.uniform(-0.02, 0.02)
            MARKET_PRICES[symbol] *= (1 + change)
        await asyncio.sleep(5)  # Update every 5 seconds

async def continuous_trading():
    """Main trading loop."""
    print("🦷 PAUL'S WORLD - PAPER TRADING ENGINE")
    print("=" * 60)
    
    world = PaulWorld()
    await world.initialize()
    pt = world.paper_trading
    
    # Ensure competition mode
    if pt.mode.value != 'competition':
        pt.start_competition(7)
    
    pauls_list = list(world.pauls.keys())
    symbols = list(MARKET_PRICES.keys())
    
    print(f"✅ {len(pauls_list):,} Pauls ready to trade")
    print(f"📈 {len(symbols)} markets active")
    print(f"🏆 Competition ends: {pt.competition_end.strftime('%Y-%m-%d') if pt.competition_end else 'Not set'}")
    print("\n💰 Trading started... (Ctrl+C to stop)\n")
    
    trade_count = 0
    last_leaderboard = time.time()
    
    try:
        while True:
            # Random Paul makes a trade every 1-3 seconds
            await asyncio.sleep(random.uniform(0.5, 2))
            
            paul_name = random.choice(pauls_list)
            symbol = random.choice(symbols)
            direction = random.choice(['buy', 'sell'])
            price = MARKET_PRICES[symbol]
            confidence = random.uniform(0.75, 0.98)
            
            # Execute trade
            trade = pt.execute_trade(
                paul_name=paul_name,
                symbol=symbol,
                direction=direction,
                current_price=price,
                confidence=confidence
            )
            
            if trade:
                trade_count += 1
                
                # Update prices and check stops
                pt.update_prices(MARKET_PRICES)
                
                # Show activity every 10 trades
                if trade_count % 10 == 0:
                    pnl_emoji = "📈" if random.random() > 0.4 else "📉"
                    print(f"{pnl_emoji} {trade_count} trades | {paul_name[:15]:<15} {direction.upper():4} {symbol:<6} @ ${price:>8,.0f}")
                
                # Show leaderboard every 60 seconds
                if time.time() - last_leaderboard > 60:
                    print("\n" + "=" * 60)
                    print("🏆 LEADERBOARD UPDATE")
                    print("-" * 60)
                    
                    leaderboard = pt.get_leaderboard(5)
                    for entry in leaderboard[:5]:
                        roi = entry['roi']
                        emoji = "🚀" if roi > 0.05 else "📈" if roi > 0 else "📉" if roi > -0.05 else "💀"
                        print(f"{emoji} {entry['paul_name'][:25]:<25} ${entry['total_value']:>10,.0f} ({roi:+6.1%}) {entry['total_trades']} trades")
                    
                    total_trades = pt.get_total_trades()
                    proven = pt.get_proven_traders()
                    print(f"\n📊 Total trades: {total_trades:,} | Proven traders: {len(proven)}")
                    print("=" * 60 + "\n")
                    
                    last_leaderboard = time.time()
                    await world._save_world()
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopping trading engine...")
        await world._save_world()
        print("💾 Final state saved")
        
        # Final leaderboard
        print("\n🏆 FINAL LEADERBOARD")
        leaderboard = pt.get_leaderboard(10)
        for entry in leaderboard[:10]:
            badge = "🏆" if entry.get('proven_trader') else "  "
            print(f"{badge} {entry['paul_name'][:25]:<25} ${entry['total_value']:>10,.0f} ({entry['roi']:+6.1%})")

if __name__ == "__main__":
    random.seed(int(time.time()))
    asyncio.run(continuous_trading())
