"""
Swimming Pauls - Live Market Paper Trading

Real paper trading with live market data.
Pauls analyze actual prices, charts, and trends to make predictions.

Author: Howard (H.O.W.A.R.D)
"""

import random
import json
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import sqlite3

from paper_trading import PaperTradingManager, PaperTrade
from genetic_breeding import PaulDNA
from curated_evolution import CuratedPaulEvolution


@dataclass
class MarketData:
    """Real-time market data for a symbol."""
    symbol: str
    price: float
    change_24h: float
    change_7d: float
    volume_24h: float
    market_cap: float
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class LiveMarketDataFeed:
    """
    Fetches real-time market data from CoinGecko API.
    """
    
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.cache: Dict[str, MarketData] = {}
        self.cache_time: Optional[datetime] = None
        self.cache_duration = timedelta(minutes=1)  # Cache for 1 minute
    
    async def fetch_prices(self, symbols: List[str] = None) -> Dict[str, MarketData]:
        """
        Fetch real-time prices and market data.
        
        Args:
            symbols: List of symbols (e.g., ['BTC', 'ETH', 'SOL'])
        
        Returns:
            Dict of symbol -> MarketData
        """
        # Check cache
        if (self.cache_time and 
            datetime.now() - self.cache_time < self.cache_duration and
            self.cache):
            return self.cache
        
        if symbols is None:
            symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'ADA', 'DOT', 'AVAX', 'MATIC']
        
        # Map symbols to CoinGecko IDs
        symbol_to_id = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'SOL': 'solana',
            'BNB': 'binancecoin',
            'ADA': 'cardano',
            'DOT': 'polkadot',
            'AVAX': 'avalanche-2',
            'MATIC': 'matic-network',
            'ARB': 'arbitrum',
            'OP': 'optimism',
        }
        
        ids = [symbol_to_id.get(s, s.lower()) for s in symbols]
        
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'vs_currency': 'usd',
                    'ids': ','.join(ids),
                    'order': 'market_cap_desc',
                    'per_page': '100',
                    'page': '1',
                    'sparkline': 'false',
                    'price_change_percentage': '24h,7d',
                }
                
                async with session.get(
                    f"{self.COINGECKO_API}/coins/markets",
                    params=params
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        market_data = {}
                        for coin in data:
                            symbol = coin['symbol'].upper()
                            market_data[symbol] = MarketData(
                                symbol=symbol,
                                price=coin['current_price'],
                                change_24h=coin.get('price_change_percentage_24h_in_currency', 0) or 0,
                                change_7d=coin.get('price_change_percentage_7d_in_currency', 0) or 0,
                                volume_24h=coin.get('total_volume', 0) or 0,
                                market_cap=coin.get('market_cap', 0) or 0,
                            )
                        
                        # Update cache
                        self.cache = market_data
                        self.cache_time = datetime.now()
                        
                        return market_data
                    else:
                        print(f"⚠️  CoinGecko API error: {resp.status}")
                        return self.cache or {}
        
        except Exception as e:
            print(f"⚠️  Error fetching market data: {e}")
            return self.cache or {}
    
    def get_market_summary(self, data: Dict[str, MarketData]) -> str:
        """Generate human-readable market summary."""
        lines = ["📊 Current Market Conditions:", ""]
        
        for symbol, market in data.items():
            emoji = "🟢" if (market.change_24h or 0) > 0 else "🔴"
            price_str = f"${market.price:,.2f}" if market.price else "N/A"
            change_str = f"{market.change_24h:+.1f}" if market.change_24h else "0.0"
            lines.append(f"{emoji} {symbol}: {price_str} ({change_str}% 24h)")
        
        return "\n".join(lines)


class LiveTradingEngine:
    """
    Live market paper trading engine.
    
    Pauls analyze real market data and make trading decisions.
    """
    
    def __init__(self, db_path: str = "data/live_trading.db"):
        self.db_path = Path(db_path)
        self.market_feed = LiveMarketDataFeed()
        self.paper_trading = PaperTradingManager()
        self.evolution = CuratedPaulEvolution()
        
        self._init_db()
    
    def _init_db(self):
        """Initialize live trading database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Trading decisions log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_decisions (
                decision_id TEXT PRIMARY KEY,
                paul_name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                decision TEXT NOT NULL,  -- 'buy', 'sell', 'hold'
                confidence REAL,
                reasoning TEXT,
                market_price REAL,
                market_change_24h REAL,
                executed BOOLEAN,
                trade_id TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Market snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_snapshots (
                snapshot_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                data TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def analyze_market_for_paul(self, 
                                     paul_name: str,
                                     dna: PaulDNA,
                                     market_data: Dict[str, MarketData]) -> Dict:
        """
        Simulate how a Paul would analyze the market.
        
        Uses DNA traits to weight different market signals.
        """
        # Get DNA traits
        risk = dna.risk_management
        conviction = dna.conviction
        tech_weight = dna.technical_vs_fundamental
        emotional = dna.emotional_stability
        time_horiz = dna.time_horizon
        adapt = dna.adaptability
        
        # Determine specialty
        specialty = dna.get_dominant_specialty()
        
        # Analyze each symbol
        signals = {}
        
        for symbol, market in market_data.items():
            # Technical signal (price momentum)
            tech_signal = 0
            if market.change_24h > 5:
                tech_signal = 1  # Strong bullish
            elif market.change_24h > 2:
                tech_signal = 0.5  # Moderate bullish
            elif market.change_24h < -5:
                tech_signal = -1  # Strong bearish
            elif market.change_24h < -2:
                tech_signal = -0.5  # Moderate bearish
            
            # Fundamental signal (trend continuation)
            fund_signal = 0
            if market.change_7d > 10 and market.change_24h > 0:
                fund_signal = 1  # Strong uptrend
            elif market.change_7d < -10 and market.change_24h < 0:
                fund_signal = -1  # Strong downtrend
            
            # Weight by DNA preference
            combined_signal = (tech_signal * tech_weight + 
                             fund_signal * (1 - tech_weight))
            
            # Apply emotional stability (reduce extreme reactions if stable)
            if emotional > 0.7:
                combined_signal *= 0.7  # Dampen signals
            elif emotional < 0.3:
                combined_signal *= 1.3  # Amplify signals
            
            # Apply conviction (stronger signals = higher confidence)
            confidence = min(1.0, abs(combined_signal) * (0.5 + conviction * 0.5))
            
            signals[symbol] = {
                'signal': combined_signal,
                'confidence': confidence,
                'price': market.price,
            }
        
        # Pick best opportunity
        best_symbol = max(signals, key=lambda s: abs(signals[s]['signal']))
        best_signal = signals[best_symbol]
        
        # Determine decision
        if best_signal['signal'] > 0.3 and best_signal['confidence'] > 0.75:
            decision = 'buy'
        elif best_signal['signal'] < -0.3 and best_signal['confidence'] > 0.75:
            decision = 'sell'
        else:
            decision = 'hold'
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            paul_name, dna, best_symbol, market_data[best_symbol], 
            decision, best_signal['confidence']
        )
        
        return {
            'symbol': best_symbol,
            'decision': decision,
            'confidence': best_signal['confidence'],
            'reasoning': reasoning,
            'price': best_signal['price'],
            'all_signals': signals,
        }
    
    def _generate_reasoning(self, paul_name: str, dna: PaulDNA, 
                           symbol: str, market: MarketData,
                           decision: str, confidence: float) -> str:
        """Generate human-readable reasoning for the decision."""
        parts = [f"{paul_name} analysis:"]
        
        # Market observation
        if market.change_24h > 5:
            parts.append(f"{symbol} showing strong momentum (+{market.change_24h:.1f}% 24h)")
        elif market.change_24h < -5:
            parts.append(f"{symbol} in pullback (-{abs(market.change_24h):.1f}% 24h)")
        else:
            parts.append(f"{symbol} relatively stable ({market.change_24h:+.1f}% 24h)")
        
        # DNA-based reasoning
        if dna.technical_vs_fundamental > 0.6:
            parts.append("Technical indicators suggest this direction")
        elif dna.technical_vs_fundamental < 0.4:
            parts.append("Fundamental trend supports this view")
        
        if dna.risk_management > 0.7:
            parts.append("Risk management parameters align")
        
        if dna.get_dominant_specialty():
            parts.append(f"Specialty in {dna.get_dominant_specialty()} informs this")
        
        parts.append(f"Decision: {decision.upper()} with {confidence:.0%} confidence")
        
        return " | ".join(parts)
    
    async def run_live_trading_cycle(self, paul_names: List[str] = None):
        """
        Run one live trading cycle.
        
        1. Fetch live market data
        2. Each Paul analyzes and decides
        3. Execute paper trades for high-confidence decisions
        4. Log all decisions
        """
        print("\n🚀 LIVE TRADING CYCLE")
        print("=" * 60)
        
        # Step 1: Fetch live market data
        print("📡 Fetching live market data...")
        market_data = await self.market_feed.fetch_prices()
        
        if not market_data:
            print("❌ Failed to fetch market data")
            return
        
        print(f"✅ Fetched data for {len(market_data)} assets")
        print(self.market_feed.get_market_summary(market_data))
        
        # Step 2: Get Pauls to trade
        if paul_names is None:
            paul_names = self.evolution.curated_pauls  # All 1000 Pauls
        
        print(f"\n🧠 Analyzing market for {len(paul_names)} Pauls...")
        
        # Step 3: Each Paul analyzes and decides
        decisions = []
        trades_executed = 0
        
        for paul_name in paul_names:
            # Get Paul's DNA
            conn = sqlite3.connect(self.evolution.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT dna FROM curated_dna WHERE paul_name = ?', (paul_name,))
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                continue
            
            dna = PaulDNA.from_dict(json.loads(row[0]))
            
            # Analyze market
            analysis = await self.analyze_market_for_paul(paul_name, dna, market_data)
            
            # Log decision
            decision_id = f"dec-{datetime.now().strftime('%Y%m%d%H%M%S')}-{paul_name}"
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO trading_decisions 
                (decision_id, paul_name, symbol, decision, confidence, reasoning,
                 market_price, market_change_24h, executed, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision_id,
                paul_name,
                analysis['symbol'],
                analysis['decision'],
                analysis['confidence'],
                analysis['reasoning'],
                analysis['price'],
                market_data[analysis['symbol']].change_24h,
                False,
                datetime.now().isoformat(),
            ))
            conn.commit()
            conn.close()
            
            decisions.append({
                'paul': paul_name,
                'decision': analysis['decision'],
                'symbol': analysis['symbol'],
                'confidence': analysis['confidence'],
                'reasoning': analysis['reasoning'],
            })
            
            # Execute trade if high confidence
            if analysis['decision'] in ['buy', 'sell'] and analysis['confidence'] >= 0.75:
                trade = self.paper_trading.execute_trade(
                    paul_name=paul_name,
                    symbol=analysis['symbol'],
                    direction=analysis['decision'],
                    current_price=analysis['price'],
                    confidence=analysis['confidence'],
                )
                
                if trade:
                    # Update decision as executed
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE trading_decisions 
                        SET executed = 1, trade_id = ?
                        WHERE decision_id = ?
                    ''', (trade.id, decision_id))
                    conn.commit()
                    conn.close()
                    
                    trades_executed += 1
        
        # Summary
        buys = len([d for d in decisions if d['decision'] == 'buy'])
        sells = len([d for d in decisions if d['decision'] == 'sell'])
        holds = len([d for d in decisions if d['decision'] == 'hold'])
        
        print(f"\n📊 Trading Cycle Complete")
        print(f"  Decisions: {len(decisions)}")
        print(f"  BUY: {buys} | SELL: {sells} | HOLD: {holds}")
        print(f"  Trades Executed: {trades_executed}")
        
        # Show sample decisions
        print(f"\n📝 Sample Decisions:")
        for d in decisions[:3]:
            emoji = "🟢" if d['decision'] == 'buy' else "🔴" if d['decision'] == 'sell' else "⚪"
            print(f"  {emoji} {d['paul']}: {d['decision'].upper()} {d['symbol']} ({d['confidence']:.0%})")
            print(f"     {d['reasoning'][:80]}...")
    
    async def run_continuous(self, interval_minutes: int = 60):
        """
        Run continuous live trading.
        
        Args:
            interval_minutes: How often to run trading cycle
        """
        print(f"🔄 Starting continuous live trading (every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                await self.run_live_trading_cycle()
                
                print(f"\n⏱️  Sleeping for {interval_minutes} minutes...")
                await asyncio.sleep(interval_minutes * 60)
        
        except KeyboardInterrupt:
            print("\n🛑 Stopping live trading")


# CLI Interface
def live_trading_cli():
    """Command-line interface for live trading."""
    import sys
    
    engine = LiveTradingEngine()
    
    if len(sys.argv) < 2:
        print("Live Market Paper Trading")
        print("Commands:")
        print("  once                    - Run one trading cycle")
        print("  continuous <minutes>    - Run continuously")
        print("  market                  - Show current market data")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "once":
        asyncio.run(engine.run_live_trading_cycle())
    
    elif command == "continuous":
        minutes = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        asyncio.run(engine.run_continuous(minutes))
    
    elif command == "market":
        async def show_market():
            data = await engine.market_feed.fetch_prices()
            print(engine.market_feed.get_market_summary(data))
        
        asyncio.run(show_market())


if __name__ == "__main__":
    live_trading_cli()
