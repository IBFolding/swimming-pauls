#!/usr/bin/env python3
"""
Real-time price feed updater for Paul's World paper trading.
Fetches live prices and updates all open positions.
"""
import asyncio
import json
import sqlite3
import subprocess
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

# Known prices cache
PRICE_CACHE = {}
CACHE_TIME = {}
CACHE_DURATION = 300  # 5 minutes (respecting CoinGecko rate limits)

# Fallback prices if API fails
DEFAULT_PRICES = {
    'BTC': 70791, 'ETH': 2153, 'SOL': 91, 'BNB': 641,
    'ADA': 0.26, 'DOT': 7, 'AVAX': 9.55, 'MATIC': 0.65,
    'ARB': 1.2, 'OP': 2.3, 'DOGE': 0.09, 'LINK': 9.12,
    'UNI': 3.55, 'AAVE': 111, 'COMP': 19, 'SPY': 500,
    'AAPL': 180, 'TSLA': 180, 'NVDA': 900, 'QQQ': 440
}


async def fetch_price(symbol: str) -> float:
    """Fetch current price for a symbol using crypto-price skill."""
    now = datetime.now().timestamp()
    
    # Check cache
    if symbol in PRICE_CACHE and (now - CACHE_TIME.get(symbol, 0)) < CACHE_DURATION:
        return PRICE_CACHE[symbol]
    
    price = None
    
    # Try crypto-price skill via subprocess
    try:
        result = subprocess.run(
            ['python3', '/Users/brain/.openclaw/workspace/skills/crypto-price/scripts/get_price_chart.py', symbol, '1h'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            price = data.get('price')
    except Exception as e:
        pass
    
    # Fallback to default
    if price is None:
        price = DEFAULT_PRICES.get(symbol)
        if price:
            print(f"  ⚠️  Using fallback for {symbol}: ${price}")
    
    # Update cache
    if price:
        PRICE_CACHE[symbol] = price
        CACHE_TIME[symbol] = now
    
    return price


def update_database_prices(prices: dict):
    """Update all open positions in the database with current prices."""
    db_path = Path('/Users/brain/.openclaw/workspace/swimming_pauls/data/paper_trading.db')
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 0
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all open trades
    cursor.execute('SELECT id, data FROM paper_trades WHERE closed_at IS NULL')
    open_trades = cursor.fetchall()
    
    updated = 0
    for trade_id, data_json in open_trades:
        try:
            data = json.loads(data_json)
            symbol = data.get('symbol')
            
            if symbol and symbol in prices:
                new_price = prices[symbol]
                
                # Validate price before updating
                if not new_price or new_price < 0.01:
                    print(f"⚠️  Skipping invalid price for {symbol}: ${new_price}")
                    continue
                
                old_price = data.get('current_price', data.get('entry_price', 0))
                
                if old_price != new_price:
                    data['current_price'] = new_price
                    
                    # Calculate unrealized PNL
                    direction = data.get('direction', 'buy')
                    entry = data.get('entry_price', 0)
                    quantity = data.get('quantity', 0)
                    
                    if direction == 'buy':
                        unrealized = (new_price - entry) * quantity
                    else:  # sell
                        unrealized = (entry - new_price) * quantity
                    
                    data['unrealized_pnl'] = unrealized
                    data['unrealized_pnl_percent'] = (unrealized / (entry * quantity)) * 100 if entry > 0 else 0
                    
                    cursor.execute(
                        'UPDATE paper_trades SET data = ? WHERE id = ?',
                        (json.dumps(data), trade_id)
                    )
                    updated += 1
        except Exception as e:
            pass
    
    conn.commit()
    conn.close()
    return updated


def get_unique_symbols() -> list:
    """Get all unique symbols from open positions."""
    db_path = Path('/Users/brain/.openclaw/workspace/swimming_pauls/data/paper_trading.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT data FROM paper_trades WHERE closed_at IS NULL')
    rows = cursor.fetchall()
    
    symbols = set()
    for row in rows:
        try:
            data = json.loads(row[0])
            symbol = data.get('symbol')
            if symbol:
                symbols.add(symbol)
        except:
            pass
    
    conn.close()
    return list(symbols)


async def price_feed_loop():
    """Main loop - continuously update prices."""
    print("🦷 PAUL'S WORLD - PRICE FEED")
    print("=" * 50)
    print("Updating prices every 30 seconds...")
    print("Press Ctrl+C to stop\n")
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            
            # Get unique symbols from open positions
            symbols = get_unique_symbols()
            
            if not symbols:
                print(f"[{iteration}] No open positions found")
                await asyncio.sleep(30)
                continue
            
            print(f"[{iteration}] Fetching prices for: {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
            
            # Fetch prices
            prices = {}
            for symbol in symbols:
                price = await fetch_price(symbol)
                if price:
                    prices[symbol] = price
            
            # Add defaults for missing symbols
            for symbol in symbols:
                if symbol not in prices and symbol in DEFAULT_PRICES:
                    prices[symbol] = DEFAULT_PRICES[symbol]
            
            # Update database
            updated = update_database_prices(prices)
            
            # Show sample prices
            sample = {k: v for k, v in list(prices.items())[:5]}
            price_str = ', '.join([f"{k}:${v:,.0f}" for k, v in sample.items()])
            print(f"[{iteration}] Updated {updated} positions | Prices: {price_str}")
            
            await asyncio.sleep(30)
            
    except KeyboardInterrupt:
        print("\n👋 Price feed stopped")


if __name__ == "__main__":
    asyncio.run(price_feed_loop())
