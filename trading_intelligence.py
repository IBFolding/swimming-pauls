#!/usr/bin/env python3
"""
Pauls Trading Intelligence Suite
Full market analysis for smarter trading decisions.

Features:
- Technical indicators (RSI, MACD, Bollinger Bands, ATR)
- Price history & volume analysis
- News sentiment integration
- Economic calendar awareness
- Correlation analysis
"""

import asyncio
import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import aiohttp
import sys

sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')


@dataclass
class TechnicalSignal:
    """Technical analysis signal for a token."""
    symbol: str
    price: float
    timestamp: datetime
    
    # Moving Averages
    ma_20: float = 0.0
    ma_50: float = 0.0
    ma_200: float = 0.0
    
    # RSI (14-period)
    rsi: float = 50.0
    rsi_signal: str = "NEUTRAL"  # OVERSOLD, NEUTRAL, OVERBOUGHT
    
    # MACD
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_histogram: float = 0.0
    macd_trend: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
    
    # Bollinger Bands
    bb_upper: float = 0.0
    bb_lower: float = 0.0
    bb_position: float = 0.5  # 0=lower, 1=upper, 0.5=middle
    
    # ATR (Average True Range) for volatility
    atr: float = 0.0
    atr_percent: float = 0.0  # ATR as % of price
    
    # Volume
    volume_24h: float = 0.0
    volume_avg_7d: float = 0.0
    volume_ratio: float = 1.0  # Today's vol vs 7d avg
    
    # Trend
    trend: str = "SIDEWAYS"  # BULLISH, BEARISH, SIDEWAYS
    trend_strength: float = 0.0  # 0-100
    
    # Overall score (-100 to +100)
    technical_score: float = 0.0
    recommendation: str = "HOLD"  # STRONG_BUY, BUY, HOLD, SELL, STRONG_SELL


@dataclass
class MarketContext:
    """Broader market context for trading decisions."""
    timestamp: datetime
    
    # BTC dominance
    btc_dominance: float = 0.0
    
    # Fear & Greed Index
    fear_greed_index: int = 50
    fear_greed_label: str = "NEUTRAL"
    
    # Global market cap
    total_market_cap: float = 0.0
    market_cap_change_24h: float = 0.0
    
    # Top correlations
    btc_eth_correlation: float = 0.0
    btc_sp500_correlation: float = 0.0
    
    # News sentiment
    news_sentiment_score: float = 0.0  # -1 to +1
    news_headlines: List[str] = None
    
    # Economic events
    upcoming_events: List[Dict] = None


class TradingIntelligence:
    """Intelligence module for Pauls trading decisions."""
    
    COINGECKO_API = "https://api.coingecko.com/api/v3"
    ALTERNATIVE_API = "https://api.alternative.me/fng/"  # Fear & Greed
    
    def __init__(self):
        self.cache: Dict[str, any] = {}
        self.cache_time: Dict[str, datetime] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    def _get_cached(self, key: str, ttl_seconds: int = 60) -> Optional[any]:
        """Get cached data if not expired."""
        if key in self.cache and key in self.cache_time:
            age = (datetime.now() - self.cache_time[key]).total_seconds()
            if age < ttl_seconds:
                return self.cache[key]
        return None
    
    def _set_cached(self, key: str, value: any):
        """Cache data with timestamp."""
        self.cache[key] = value
        self.cache_time[key] = datetime.now()
    
    async def fetch_price_history(self, symbol: str, days: int = 30) -> List[Dict]:
        """Fetch OHLCV data for technical analysis."""
        cache_key = f"history_{symbol}_{days}"
        cached = self._get_cached(cache_key, ttl_seconds=300)  # 5 min cache
        if cached:
            return cached
        
        try:
            # Map common symbols to CoinGecko IDs
            symbol_map = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'SOL': 'solana',
                'DOGE': 'dogecoin', 'LINK': 'chainlink'
            }
            coin_id = symbol_map.get(symbol.upper(), symbol.lower())
            
            url = f"{self.COINGECKO_API}/coins/{coin_id}/market_chart"
            params = {'vs_currency': 'usd', 'days': days}
            
            async with self.session.get(url, params=params) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Format: [[timestamp, price], ...]
                    prices = data.get('prices', [])
                    volumes = data.get('total_volumes', [])
                    
                    # Combine into OHLC-like structure
                    history = []
                    for i, (ts, price) in enumerate(prices):
                        vol = volumes[i][1] if i < len(volumes) else 0
                        history.append({
                            'timestamp': datetime.fromtimestamp(ts / 1000),
                            'price': price,
                            'volume': vol
                        })
                    
                    self._set_cached(cache_key, history)
                    return history
                    
        except Exception as e:
            print(f"⚠️ Error fetching history for {symbol}: {e}")
        
        return []
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Calculate average gains and losses
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, prices: List[float]) -> Tuple[float, float, float]:
        """Calculate MACD, Signal, and Histogram."""
        if len(prices) < 35:
            return 0.0, 0.0, 0.0
        
        # Calculate EMAs
        def ema(prices, period):
            multiplier = 2 / (period + 1)
            ema_values = [sum(prices[:period]) / period]
            for price in prices[period:]:
                ema_values.append((price - ema_values[-1]) * multiplier + ema_values[-1])
            return ema_values[-1]
        
        ema_12 = ema(prices, 12)
        ema_26 = ema(prices, 26)
        macd = ema_12 - ema_26
        
        # Calculate signal line (9-period EMA of MACD)
        # Approximate using recent MACD values
        macd_values = []
        for i in range(26, len(prices)):
            e12 = ema(prices[max(0, i-12):i+1], 12)
            e26 = ema(prices[max(0, i-26):i+1], 26)
            macd_values.append(e12 - e26)
        
        signal = ema(macd_values[-9:], 9) if len(macd_values) >= 9 else macd
        histogram = macd - signal
        
        return macd, signal, histogram
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands."""
        if len(prices) < period:
            return prices[-1], prices[-1], prices[-1]
        
        recent = prices[-period:]
        sma = sum(recent) / period
        variance = sum((p - sma) ** 2 for p in recent) / period
        std_dev = variance ** 0.5
        
        upper = sma + (2 * std_dev)
        lower = sma - (2 * std_dev)
        
        return upper, sma, lower
    
    def calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """Calculate Average True Range."""
        if len(prices) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(prices)):
            tr = abs(prices[i] - prices[i-1])
            true_ranges.append(tr)
        
        return sum(true_ranges[-period:]) / period
    
    async def analyze_technicals(self, symbol: str) -> TechnicalSignal:
        """Full technical analysis for a symbol."""
        history = await self.fetch_price_history(symbol, days=30)
        
        if not history:
            return TechnicalSignal(symbol=symbol, price=0.0, timestamp=datetime.now())
        
        prices = [h['price'] for h in history]
        volumes = [h['volume'] for h in history]
        current_price = prices[-1]
        
        signal = TechnicalSignal(
            symbol=symbol,
            price=current_price,
            timestamp=datetime.now()
        )
        
        # Moving Averages
        if len(prices) >= 20:
            signal.ma_20 = sum(prices[-20:]) / 20
        if len(prices) >= 50:
            signal.ma_50 = sum(prices[-50:]) / 50
        if len(prices) >= 200:
            signal.ma_200 = sum(prices[-200:]) / 200
        
        # RSI
        signal.rsi = self.calculate_rsi(prices)
        if signal.rsi > 70:
            signal.rsi_signal = "OVERBOUGHT"
        elif signal.rsi < 30:
            signal.rsi_signal = "OVERSOLD"
        else:
            signal.rsi_signal = "NEUTRAL"
        
        # MACD
        signal.macd, signal.macd_signal, signal.macd_histogram = self.calculate_macd(prices)
        if signal.macd > signal.macd_signal and signal.macd_histogram > 0:
            signal.macd_trend = "BULLISH"
        elif signal.macd < signal.macd_signal and signal.macd_histogram < 0:
            signal.macd_trend = "BEARISH"
        else:
            signal.macd_trend = "NEUTRAL"
        
        # Bollinger Bands
        signal.bb_upper, _, signal.bb_lower = self.calculate_bollinger_bands(prices)
        if signal.bb_upper != signal.bb_lower:
            signal.bb_position = (current_price - signal.bb_lower) / (signal.bb_upper - signal.bb_lower)
        
        # ATR
        signal.atr = self.calculate_atr(prices)
        signal.atr_percent = (signal.atr / current_price) * 100 if current_price > 0 else 0
        
        # Volume
        if len(volumes) >= 24:  # Assume hourly data roughly
            signal.volume_24h = sum(volumes[-24:])
        if len(volumes) >= 7 * 24:
            signal.volume_avg_7d = sum(volumes[-7*24:]) / 7
            if signal.volume_avg_7d > 0:
                signal.volume_ratio = signal.volume_24h / signal.volume_avg_7d
        
        # Trend determination
        if current_price > signal.ma_20 > signal.ma_50:
            signal.trend = "BULLISH"
            signal.trend_strength = min(100, (current_price / signal.ma_50 - 1) * 1000)
        elif current_price < signal.ma_20 < signal.ma_50:
            signal.trend = "BEARISH"
            signal.trend_strength = min(100, (1 - current_price / signal.ma_50) * 1000)
        else:
            signal.trend = "SIDEWAYS"
            signal.trend_strength = 0
        
        # Calculate overall technical score (-100 to +100)
        score = 0
        
        # RSI contribution (-30 to +30)
        if signal.rsi_signal == "OVERSOLD":
            score += 30
        elif signal.rsi_signal == "OVERBOUGHT":
            score -= 30
        
        # MACD contribution (-25 to +25)
        if signal.macd_trend == "BULLISH":
            score += 25
        elif signal.macd_trend == "BEARISH":
            score -= 25
        
        # Trend contribution (-30 to +30)
        if signal.trend == "BULLISH":
            score += signal.trend_strength * 0.3
        elif signal.trend == "BEARISH":
            score -= signal.trend_strength * 0.3
        
        # Volume confirmation (-15 to +15)
        if signal.volume_ratio > 1.5:
            score += 15 if score > 0 else -15  # Confirm direction
        elif signal.volume_ratio < 0.5:
            score *= 0.7  # Reduce confidence on low volume
        
        signal.technical_score = max(-100, min(100, score))
        
        # Recommendation
        if signal.technical_score > 50:
            signal.recommendation = "STRONG_BUY"
        elif signal.technical_score > 20:
            signal.recommendation = "BUY"
        elif signal.technical_score < -50:
            signal.recommendation = "STRONG_SELL"
        elif signal.technical_score < -20:
            signal.recommendation = "SELL"
        else:
            signal.recommendation = "HOLD"
        
        return signal
    
    async def get_market_context(self) -> MarketContext:
        """Get broader market context."""
        context = MarketContext(timestamp=datetime.now())
        
        try:
            # Fear & Greed Index
            async with self.session.get(self.ALTERNATIVE_API) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'data' in data and len(data['data']) > 0:
                        fng = data['data'][0]
                        context.fear_greed_index = int(fng['value'])
                        context.fear_greed_label = fng['value_classification']
        except Exception as e:
            print(f"⚠️ Could not fetch Fear & Greed: {e}")
        
        return context
    
    def format_signal_summary(self, signal: TechnicalSignal) -> str:
        """Format technical signal for display."""
        lines = [
            f"📊 {signal.symbol} Technical Analysis",
            f"   Price: ${signal.price:,.2f}",
            f"   RSI: {signal.rsi:.1f} ({signal.rsi_signal})",
            f"   MACD: {signal.macd_trend}",
            f"   Trend: {signal.trend} (strength: {signal.trend_strength:.0f})",
            f"   Volume Ratio: {signal.volume_ratio:.2f}x",
            f"   ATR: {signal.atr_percent:.2f}%",
            f"   Score: {signal.technical_score:+.0f} → {signal.recommendation}",
        ]
        return "\n".join(lines)


async def demo_intelligence():
    """Demo the trading intelligence system."""
    print("🧠 PAULS TRADING INTELLIGENCE")
    print("=" * 60)
    
    async with TradingIntelligence() as intel:
        symbols = ['BTC', 'ETH', 'SOL']
        
        for symbol in symbols:
            print(f"\n📈 Analyzing {symbol}...")
            signal = await intel.analyze_technicals(symbol)
            print(intel.format_signal_summary(signal))
            await asyncio.sleep(1)  # Rate limit
        
        print("\n" + "=" * 60)
        print("✅ Technical analysis complete!")


if __name__ == "__main__":
    asyncio.run(demo_intelligence())
