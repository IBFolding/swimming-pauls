#!/usr/bin/env python3
"""Auto-trading with live price updates for P&L."""
import asyncio
import random
import time
import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from paul_world import PaulWorld

# Starting prices
MARKET_PRICES = {
    'BTC': 65000, 'ETH': 3500, 'SOL': 130, 
    'SPY': 500, 'AAPL': 180, 'TSLA': 180, 
    'NVDA': 900, 'DOGE': 0.15, 'LINK': 15,
    'UNI': 8, 'AAVE': 120, 'COMP': 65
}

async def price_simulator(pt):
    """Continuously update prices and check stops."""
    while True:
        # Random walk each price
        for symbol in MARKET_PRICES:
            change = random.uniform(-0.02, 0.02)  # 2% moves
            MARKET_PRICES[symbol] *= (1 + change)
        
        # Update all portfolios with new prices
        if pt:
            pt.update_prices(MARKET_PRICES)
        
        await asyncio.sleep(2)

async def auto_trading_loop():
    print("🦷 PAUL'S WORLD - AUTO-TRADING")
    print("=" * 60)
    
    world = PaulWorld()
    await world.initialize()
    pt = world.paper_trading
    
    # Start competition
    pt.start_competition(7)
    for p in pt.portfolios.values():
        p.enabled = True
    
    pauls_list = list(world.pauls.keys())
    symbols = list(MARKET_PRICES.keys())
    
    print(f"✅ {len(pauls_list):,} Pauls")
    print(f"📈 {len(symbols)} markets")
    print(f"🏆 Comp ends: {pt.competition_end.strftime('%Y-%m-%d')}")
    print("💰 Trading...\n")
    
    trade_count = len(pt.trades)
    last_status = time.time()
    
    # Start price simulator in background
    asyncio.create_task(price_simulator(pt))
    
    try:
        while True:
            await asyncio.sleep(random.uniform(1, 3))
            
            # Random Paul trades
            paul_name = random.choice(pauls_list)
            symbol = random.choice(symbols)
            price = MARKET_PRICES[symbol]
            confidence = random.uniform(0.75, 0.98)
            sentiment = random.choice(['bullish', 'bearish'])
            direction = 'buy' if sentiment == 'bullish' else 'sell'
            
            trade = pt.execute_trade(
                paul_name=paul_name,
                symbol=symbol,
                direction=direction,
                current_price=price,
                confidence=confidence
            )
            
            if trade:
                trade_count += 1
                
                # Show every 10th trade
                if trade_count % 10 == 0:
                    emoji = "🚀" if sentiment == 'bullish' else "🔻"
                    print(f"{emoji} Trade #{trade_count}: {paul_name[:15]} {direction.upper()} {symbol} @ ${price:,.0f}")
            
            # Status every 30 seconds
            if time.time() - last_status > 30:
                print("\n" + "=" * 60)
                print("📊 STATUS UPDATE")
                print(f"   Total trades: {trade_count}")
                print(f"   Open positions: {sum(len(p.positions) for p in pt.portfolios.values())}")
                
                # Top 3
                lb = pt.get_leaderboard(3)
                if lb:
                    print("\n🏆 Top 3:")
                    for e in lb[:3]:
                        roi = e['roi']
                        em = "🚀" if roi > 0.05 else "📈" if roi > 0 else "📉"
                        print(f"   {em} {e['paul_name'][:20]:<20} ${e['total_value']:>9,.0f} ({roi:+5.1%})")
                
                print("=" * 60 + "\n")
                await world._save_world()
                last_status = time.time()
                
    except KeyboardInterrupt:
        print("\n👋 Stopping...")
        await world._save_world()

if __name__ == "__main__":
    random.seed(int(time.time()))
    asyncio.run(auto_trading_loop())
