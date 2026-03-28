#!/usr/bin/env python3
"""Auto-trading with LIVE market data from real exchanges."""
import asyncio
import random
import time
import json
import subprocess
import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from paul_world import PaulWorld

# Market symbols to trade
CRYPTO_SYMBOLS = ['BTC', 'ETH', 'SOL', 'DOGE', 'LINK']
STOCK_SYMBOLS = ['SPY', 'AAPL', 'TSLA', 'NVDA']

# Cache prices
price_cache = {}
last_price_update = 0

async def fetch_crypto_price(symbol):
    """Fetch live crypto price from CoinGecko/Hyperliquid."""
    try:
        script_path = '/Users/brain/.openclaw/workspace/skills/crypto-price/scripts/get_price_chart.py'
        result = subprocess.run(
            ['python3', script_path, symbol, '1h'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get('price', 0)
    except Exception as e:
        print(f"   ⚠️ Crypto price error for {symbol}: {e}")
    return None

async def fetch_stock_price(symbol):
    """Fetch live stock price from Yahoo Finance."""
    try:
        result = subprocess.run(
            ['yf', 'quote', symbol],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get('regularMarketPrice', 0)
    except Exception as e:
        print(f"   ⚠️ Stock price error for {symbol}: {e}")
    return None

async def update_all_prices():
    """Update all market prices from live sources."""
    global price_cache, last_price_update
    
    print("\n📡 Fetching live market data...")
    
    # Fetch crypto prices
    for symbol in CRYPTO_SYMBOLS:
        price = await fetch_crypto_price(symbol)
        if price:
            price_cache[symbol] = price
            print(f"   ✓ {symbol}: ${price:,.2f}")
        await asyncio.sleep(0.5)  # Rate limit
    
    # Fetch stock prices
    for symbol in STOCK_SYMBOLS:
        price = await fetch_stock_price(symbol)
        if price:
            price_cache[symbol] = price
            print(f"   ✓ {symbol}: ${price:,.2f}")
        await asyncio.sleep(0.5)
    
    last_price_update = time.time()
    print(f"✅ Live prices updated: {len(price_cache)} markets\n")
    return price_cache

async def auto_trading_loop():
    print("🦷 PAUL'S WORLD - LIVE MARKET TRADING")
    print("=" * 60)
    print("Trading against REAL market data from CoinGecko & Yahoo Finance")
    print("(Paper trading - fake money, real prices)\n")
    
    world = PaulWorld()
    await world.initialize()
    pt = world.paper_trading
    
    # Start competition
    pt.start_competition(7)
    for p in pt.portfolios.values():
        p.enabled = True
    
    pauls_list = list(world.pauls.keys())
    all_symbols = CRYPTO_SYMBOLS + STOCK_SYMBOLS
    
    print(f"✅ {len(pauls_list):,} Pauls ready")
    print(f"📈 {len(all_symbols)} live markets")
    print(f"🏆 Competition ends: {pt.competition_end.strftime('%Y-%m-%d')}")
    
    # Initial price fetch
    await update_all_prices()
    
    if not price_cache:
        print("❌ Could not fetch live prices. Using fallback.")
        # Fallback prices
        price_cache.update({
            'BTC': 65000, 'ETH': 3500, 'SOL': 130, 'DOGE': 0.15, 'LINK': 15,
            'SPY': 500, 'AAPL': 180, 'TSLA': 180, 'NVDA': 900
        })
    
    print("\n💰 Live trading started...\n")
    
    trade_count = len(pt.trades)
    last_status = time.time()
    
    try:
        while True:
            # Refresh prices every 60 seconds
            if time.time() - last_price_update > 60:
                await update_all_prices()
                # Update all portfolio positions with new prices
                if pt:
                    pt.update_prices(price_cache)
            
            # Random Paul trades every 2-5 seconds
            await asyncio.sleep(random.uniform(2, 5))
            
            paul_name = random.choice(pauls_list)
            symbol = random.choice(list(price_cache.keys()))
            price = price_cache[symbol]
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
                emoji = "🚀" if sentiment == 'bullish' else "🔻"
                market_type = "₿" if symbol in CRYPTO_SYMBOLS else "📊"
                print(f"{emoji}{market_type} {paul_name[:15]:<15} {direction.upper():4} {symbol:<6} @ ${price:>10,.2f}")
            
            # Status every 30 seconds
            if time.time() - last_status > 30:
                print("\n" + "=" * 60)
                print("📊 STATUS")
                print(f"   Total trades: {trade_count}")
                print(f"   Open positions: {sum(len(p.positions) for p in pt.portfolios.values())}")
                
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
