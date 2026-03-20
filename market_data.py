"""
Market Data Aggregator for Swimming Pauls
Combines multiple sources: Binance, CoinGecko, DexScreener, DefiLlama, on-chain

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MarketData:
    """Comprehensive market data for a token."""
    symbol: str
    price_usd: float
    price_change_24h: float
    price_change_7d: float
    volume_24h: float
    market_cap: float
    
    # Exchange data
    binance_price: Optional[float] = None
    binance_volume: Optional[float] = None
    
    # DEX data
    dex_price: Optional[float] = None
    dex_liquidity: Optional[float] = None
    dex_volume_24h: Optional[float] = None
    
    # On-chain
    holder_count: Optional[int] = None
    transaction_count_24h: Optional[int] = None
    whale_movements: List[Dict] = None
    
    # DeFi
    tvl: Optional[float] = None
    staking_apy: Optional[float] = None
    lending_apy: Optional[float] = None
    
    # Technical
    rsi: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    
    # Sentiment
    social_sentiment: Optional[float] = None  # -1 to 1
    fear_greed_index: Optional[int] = None  # 0 to 100
    
    timestamp: datetime = datetime.now()


class MarketDataAggregator:
    """
    Aggregates market data from multiple sources for comprehensive analysis.
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_time = {}
        self.cache_duration = 60  # 60 seconds
    
    async def get_binance_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from Binance API."""
        try:
            import httpx
            
            # Binance 24hr ticker
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}USDT"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        'price': float(data['lastPrice']),
                        'change_24h': float(data['priceChangePercent']),
                        'volume': float(data['volume']),
                        'high': float(data['highPrice']),
                        'low': float(data['lowPrice']),
                        'source': 'binance'
                    }
        except Exception as e:
            print(f"⚠️  Binance error for {symbol}: {e}")
        
        return {}
    
    async def get_coingecko_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch data from CoinGecko API."""
        try:
            import httpx
            
            # CoinGecko coins list to get ID
            cg_symbol = symbol.lower()
            
            url = f"https://api.coingecko.com/api/v3/coins/{cg_symbol}?localization=false"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    market = data.get('market_data', {})
                    
                    return {
                        'price': market.get('current_price', {}).get('usd'),
                        'change_24h': market.get('price_change_percentage_24h'),
                        'change_7d': market.get('price_change_percentage_7d'),
                        'market_cap': market.get('market_cap', {}).get('usd'),
                        'volume': market.get('total_volume', {}).get('usd'),
                        'sentiment': market.get('sentiment_votes_up_percentage'),
                        'source': 'coingecko'
                    }
        except Exception as e:
            print(f"⚠️  CoinGecko error for {symbol}: {e}")
        
        return {}
    
    async def get_dexscreener_data(self, symbol: str, chain: str = "solana") -> Dict[str, Any]:
        """Fetch DEX data from DexScreener."""
        try:
            import httpx
            
            url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    pairs = data.get('pairs', [])
                    
                    # Find pair on specified chain
                    for pair in pairs:
                        if pair.get('chainId') == chain:
                            return {
                                'price': float(pair.get('priceUsd', 0)),
                                'liquidity': pair.get('liquidity', {}).get('usd'),
                                'volume_24h': pair.get('volume', {}).get('h24'),
                                'dex': pair.get('dexId'),
                                'source': 'dexscreener'
                            }
        except Exception as e:
            print(f"⚠️  DexScreener error for {symbol}: {e}")
        
        return {}
    
    async def get_defillama_data(self, protocol: str) -> Dict[str, Any]:
        """Fetch DeFi data from DefiLlama."""
        try:
            import httpx
            
            url = f"https://api.llama.fi/tvl/{protocol}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                
                if response.status_code == 200:
                    tvl = response.json()
                    return {
                        'tvl': tvl,
                        'source': 'defillama'
                    }
        except Exception as e:
            print(f"⚠️  DefiLlama error for {protocol}: {e}")
        
        return {}
    
    async def get_comprehensive_data(self, symbol: str, chain: str = "solana") -> MarketData:
        """
        Get comprehensive market data from all sources.
        
        Combines:
        - Binance (CEX prices, volume)
        - CoinGecko (market data, sentiment)
        - DexScreener (DEX prices, liquidity)
        - DefiLlama (TVL for protocols)
        """
        # Check cache
        cache_key = f"{symbol}_{chain}"
        if cache_key in self.cache:
            age = (datetime.now() - self.cache_time.get(cache_key, datetime.now())).seconds
            if age < self.cache_duration:
                return self.cache[cache_key]
        
        # Fetch all sources concurrently
        binance_task = self.get_binance_data(symbol)
        coingecko_task = self.get_coingecko_data(symbol)
        dex_task = self.get_dexscreener_data(symbol, chain)
        
        results = await asyncio.gather(
            binance_task,
            coingecko_task,
            dex_task,
            return_exceptions=True
        )
        
        binance_data = results[0] if not isinstance(results[0], Exception) else {}
        coingecko_data = results[1] if not isinstance(results[1], Exception) else {}
        dex_data = results[2] if not isinstance(results[2], Exception) else {}
        
        # Merge data (priority: Binance price > DEX price > CoinGecko price)
        price = binance_data.get('price') or dex_data.get('price') or coingecko_data.get('price') or 0
        
        market_data = MarketData(
            symbol=symbol.upper(),
            price_usd=price,
            price_change_24h=binance_data.get('change_24h') or coingecko_data.get('change_24h') or 0,
            price_change_7d=coingecko_data.get('change_7d') or 0,
            volume_24h=binance_data.get('volume') or coingecko_data.get('volume') or 0,
            market_cap=coingecko_data.get('market_cap') or 0,
            binance_price=binance_data.get('price'),
            binance_volume=binance_data.get('volume'),
            dex_price=dex_data.get('price'),
            dex_liquidity=dex_data.get('liquidity'),
            dex_volume_24h=dex_data.get('volume_24h'),
            social_sentiment=coingecko_data.get('sentiment'),
        )
        
        # Cache result
        self.cache[cache_key] = market_data
        self.cache_time[cache_key] = datetime.now()
        
        return market_data
    
    def format_for_paul(self, data: MarketData) -> str:
        """Format market data for Paul context."""
        lines = [
            f"📊 Market Data for {data.symbol}:",
            f"💰 Price: ${data.price_usd:,.2f}",
            f"📈 24h Change: {data.price_change_24h:+.2f}%",
        ]
        
        if data.price_change_7d:
            lines.append(f"📊 7d Change: {data.price_change_7d:+.2f}%")
        
        lines.append(f"💎 Volume (24h): ${data.volume_24h:,.0f}")
        
        if data.market_cap:
            lines.append(f"🏢 Market Cap: ${data.market_cap:,.0f}")
        
        # DEX vs CEX comparison
        if data.binance_price and data.dex_price:
            diff = ((data.dex_price - data.binance_price) / data.binance_price) * 100
            lines.append(f"🔄 DEX/CEX Spread: {diff:+.2f}%")
        
        if data.dex_liquidity:
            lines.append(f"💧 DEX Liquidity: ${data.dex_liquidity:,.0f}")
        
        if data.tvl:
            lines.append(f"🏦 TVL: ${data.tvl:,.0f}")
        
        if data.social_sentiment:
            sentiment = "🟢 Bullish" if data.social_sentiment > 60 else "🔴 Bearish" if data.social_sentiment < 40 else "⚪ Neutral"
            lines.append(f"🗣️ Sentiment: {sentiment} ({data.social_sentiment:.0f}%)")
        
        return "\n".join(lines)


# Integration with skills
try:
    from skills import Skill, SkillMetadata, SkillResult
    
    class MarketDataSkill(Skill):
        """Skill for fetching comprehensive market data."""
        
        metadata = SkillMetadata(
            name="market_data",
            description="Get comprehensive market data from Binance, CoinGecko, DEXs",
            best_for=["Trader Paul", "Quant Paul", "Whale Paul"]
        )
        
        def __init__(self):
            self.aggregator = MarketDataAggregator()
        
        async def execute(self, symbol: str, chain: str = "solana", **kwargs) -> SkillResult:
            """Execute market data fetch."""
            try:
                data = await self.aggregator.get_comprehensive_data(symbol, chain)
                
                return SkillResult(
                    success=True,
                    data=data.__dict__,
                    message=self.aggregator.format_for_paul(data)
                )
            except Exception as e:
                return SkillResult(
                    success=False,
                    error=str(e)
                )

except ImportError:
    # Skills framework not available
    pass


# CLI for testing
async def main():
    """Test market data aggregation."""
    aggregator = MarketDataAggregator()
    
    # Test symbols
    symbols = ["BTC", "ETH", "SOL"]
    
    for symbol in symbols:
        print(f"\n{'='*50}")
        print(f"Fetching data for {symbol}...")
        print('='*50)
        
        data = await aggregator.get_comprehensive_data(symbol)
        print(aggregator.format_for_paul(data))


if __name__ == "__main__":
    asyncio.run(main())
