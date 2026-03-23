#!/usr/bin/env python3
"""
Swimming Pauls - Historical Price Tracker
Records prices at prediction time so we can resolve direction predictions.

Usage:
    python price_tracker.py                    # Record current prices
    python price_tracker.py --symbol BTC       # Record specific symbol
    python price_tracker.py --list             # Show recorded prices
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
import subprocess

sys.path.insert(0, '/Users/brain/.openclaw/workspace/skills/crypto-price')

# Default symbols to track
DEFAULT_SYMBOLS = ['BTC', 'ETH', 'SOL', 'DOGE', 'LINK', 'AVAX', 'BNB', 'ADA', 'DOT']

class PriceTracker:
    """Track historical prices for prediction resolution."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.price_file = self.data_dir / "price_history.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.prices = self._load_prices()
    
    def _load_prices(self) -> dict:
        """Load price history."""
        if self.price_file.exists():
            with open(self.price_file) as f:
                return json.load(f)
        return {}
    
    def _save_prices(self):
        """Save price history."""
        with open(self.price_file, 'w') as f:
            json.dump(self.prices, f, indent=2)
    
    def fetch_price(self, symbol: str) -> float:
        """Fetch current price for symbol."""
        try:
            result = subprocess.run(
                ['python3', '/Users/brain/.openclaw/workspace/skills/crypto-price/scripts/get_price_chart.py', symbol, '1h'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('price')
        except Exception as e:
            print(f"   ⚠️  Error fetching {symbol}: {e}")
        return None
    
    def record_prices(self, symbols: list = None):
        """Record current prices for symbols."""
        symbols = symbols or DEFAULT_SYMBOLS
        timestamp = datetime.now().isoformat()
        
        print(f"📊 Recording prices at {timestamp}")
        
        if timestamp not in self.prices:
            self.prices[timestamp] = {}
        
        for symbol in symbols:
            price = self.fetch_price(symbol)
            if price:
                self.prices[timestamp][symbol] = price
                print(f"   {symbol}: ${price:,.2f}")
        
        self._save_prices()
        print(f"\n✅ Prices saved to {self.price_file}")
    
    def get_price_at_time(self, symbol: str, timestamp: str) -> float:
        """Get price closest to given timestamp."""
        symbol = symbol.upper()
        
        # Find closest timestamp
        closest_time = None
        closest_diff = float('inf')
        
        for ts, prices in self.prices.items():
            diff = abs((datetime.fromisoformat(ts) - datetime.fromisoformat(timestamp)).total_seconds())
            if diff < closest_diff:
                closest_diff = diff
                closest_time = ts
        
        if closest_time and symbol in self.prices[closest_time]:
            return self.prices[closest_time][symbol]
        
        return None
    
    def get_price_change(self, symbol: str, start_time: str) -> dict:
        """Get price change from start_time to now."""
        symbol = symbol.upper()
        
        start_price = self.get_price_at_time(symbol, start_time)
        
        # Get current price
        current_price = self.fetch_price(symbol)
        
        if start_price and current_price:
            change = current_price - start_price
            change_pct = (change / start_price) * 100
            
            return {
                'symbol': symbol,
                'start_price': start_price,
                'current_price': current_price,
                'change': change,
                'change_pct': change_pct,
                'direction': 'UP' if change > 0 else 'DOWN'
            }
        
        return None
    
    def list_recorded(self):
        """List all recorded price snapshots."""
        print("\n📈 Recorded Price Snapshots:")
        print("-" * 50)
        
        for ts in sorted(self.prices.keys(), reverse=True)[:10]:
            prices = self.prices[ts]
            symbols = ', '.join(prices.keys())
            print(f"{ts}: {len(prices)} symbols ({symbols[:50]}...)")
        
        print(f"\nTotal snapshots: {len(self.prices)}")

def main():
    parser = argparse.ArgumentParser(description="Track historical prices")
    parser.add_argument("--symbol", type=str, help="Record specific symbol")
    parser.add_argument("--list", action="store_true", help="List recorded prices")
    parser.add_argument("--data-dir", type=str, default="data", help="Data directory")
    
    args = parser.parse_args()
    
    tracker = PriceTracker(args.data_dir)
    
    if args.list:
        tracker.list_recorded()
    elif args.symbol:
        tracker.record_prices([args.symbol.upper()])
    else:
        tracker.record_prices()

if __name__ == "__main__":
    main()
