#!/usr/bin/env python3
"""
Pump.fun Token Launch Tracker
Monitors new token launches in real-time for Pauls to analyze.

Features:
- Real-time new token detection
- Market cap tracking
- Holder count analysis
- Bonding curve progress
- Social signals (Twitter mentions)
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
import aiohttp
import websockets


@dataclass
class PumpToken:
    """A token launched on Pump.fun"""
    mint: str
    name: str
    symbol: str
    uri: str  # IPFS metadata URI
    
    # Launch data
    created_at: datetime
    creator: str
    creator_twitter: Optional[str] = None
    
    # Market data
    market_cap_sol: float = 0.0
    market_cap_usd: float = 0.0
    sol_price: float = 0.0
    
    # Bonding curve
    bonding_curve_progress: float = 0.0  # 0-100%
    is_bonding: bool = True
    
    # Holder data
    holder_count: int = 0
    unique_buyers: int = 0
    unique_sellers: int = 0
    
    # Trading stats
    volume_1h: float = 0.0
    volume_24h: float = 0.0
    buy_count_1h: int = 0
    sell_count_1h: int = 0
    
    # Social signals
    twitter_mentions: int = 0
    telegram_members: int = 0
    
    # Metadata
    image_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    twitter: Optional[str] = None
    telegram: Optional[str] = None
    
    # Risk signals
    is_mintable: bool = False
    has_freeze: bool = False
    lp_burned: bool = False
    
    # Paul analysis
    paul_score: float = 0.0  # 0-100
    paul_consensus: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
    analyzed_by: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'mint': self.mint,
            'name': self.name,
            'symbol': self.symbol,
            'created_at': self.created_at.isoformat(),
            'creator': self.creator,
            'market_cap_sol': self.market_cap_sol,
            'market_cap_usd': self.market_cap_usd,
            'bonding_curve_progress': self.bonding_curve_progress,
            'is_bonding': self.is_bonding,
            'holder_count': self.holder_count,
            'volume_1h': self.volume_1h,
            'buy_count_1h': self.buy_count_1h,
            'sell_count_1h': self.sell_count_1h,
            'twitter_mentions': self.twitter_mentions,
            'paul_score': self.paul_score,
            'paul_consensus': self.paul_consensus,
        }


class PumpFunTracker:
    """Track Pump.fun token launches in real-time."""
    
    PUMP_FUN_API = "https://frontend-api.pump.fun"
    SOL_PRICE_API = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
    
    def __init__(self):
        self.tokens: Dict[str, PumpToken] = {}
        self.new_token_callbacks: List[Callable[[PumpToken], None]] = []
        self.update_callbacks: List[Callable[[PumpToken], None]] = []
        self.sol_price: float = 130.0  # Default SOL price
        self.running = False
        
    def on_new_token(self, callback: Callable[[PumpToken], None]):
        """Register callback for new token launches."""
        self.new_token_callbacks.append(callback)
        
    def on_token_update(self, callback: Callable[[PumpToken], None]):
        """Register callback for token updates."""
        self.update_callbacks.append(callback)
        
    async def get_sol_price(self) -> float:
        """Fetch current SOL price."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.SOL_PRICE_API) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data['solana']['usd']
        except Exception as e:
            print(f"⚠️ Could not fetch SOL price: {e}")
        return self.sol_price
    
    async def fetch_new_tokens(self, limit: int = 50) -> List[PumpToken]:
        """Fetch most recent token launches."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.PUMP_FUN_API}/coins?offset=0&limit={limit}&sort=created_timestamp&order=DESC&includeNsfw=true&completed=false"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        tokens = []
                        for coin in data:
                            token = self._parse_token(coin)
                            if token:
                                tokens.append(token)
                        return tokens
                    else:
                        print(f"⚠️ Pump.fun API error: {resp.status}")
        except Exception as e:
            print(f"⚠️ Error fetching tokens: {e}")
        return []
    
    async def fetch_token_details(self, mint: str) -> Optional[PumpToken]:
        """Fetch detailed info for a specific token."""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.PUMP_FUN_API}/coins/{mint}"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return self._parse_token(data)
        except Exception as e:
            print(f"⚠️ Error fetching token {mint}: {e}")
        return None
    
    def _parse_token(self, data: dict) -> Optional[PumpToken]:
        """Parse Pump.fun API response into PumpToken."""
        try:
            mint = data.get('mint')
            if not mint:
                return None
                
            # Check if we already have this token
            if mint in self.tokens:
                token = self.tokens[mint]
                is_new = False
            else:
                token = PumpToken(
                    mint=mint,
                    name=data.get('name', 'Unknown'),
                    symbol=data.get('symbol', '???'),
                    uri=data.get('uri', ''),
                    created_at=datetime.fromtimestamp(data.get('created_timestamp', 0) / 1000),
                    creator=data.get('creator', ''),
                )
                self.tokens[mint] = token
                is_new = True
            
            # Update market data
            token.market_cap_sol = data.get('market_cap', 0) / 1e9  # Convert to SOL
            token.market_cap_usd = token.market_cap_sol * self.sol_price
            
            # Bonding curve
            token.bonding_curve_progress = data.get('bonding_curve', 0)
            token.is_bonding = data.get('complete', False) == False
            
            # Trading stats
            token.volume_24h = data.get('volume_24h', 0)
            token.holder_count = data.get('holder_count', 0)
            
            # Metadata
            token.image_url = data.get('image_uri')
            token.twitter = data.get('twitter')
            token.telegram = data.get('telegram')
            token.website = data.get('website')
            
            # Risk signals
            token.is_mintable = data.get('is_mintable', False)
            token.has_freeze = data.get('freeze_authority', False)
            token.lp_burned = data.get('lp_burned', False)
            
            # Notify callbacks
            if is_new:
                for cb in self.new_token_callbacks:
                    try:
                        cb(token)
                    except Exception as e:
                        print(f"⚠️ Callback error: {e}")
            else:
                for cb in self.update_callbacks:
                    try:
                        cb(token)
                    except Exception as e:
                        print(f"⚠️ Callback error: {e}")
            
            return token
            
        except Exception as e:
            print(f"⚠️ Error parsing token: {e}")
            return None
    
    async def run(self, poll_interval: int = 10):
        """Main loop - continuously monitor for new tokens."""
        self.running = True
        print("🚀 Pump.fun Tracker started")
        print(f"   Polling every {poll_interval}s")
        
        # Initial SOL price fetch
        self.sol_price = await self.get_sol_price()
        print(f"   SOL price: ${self.sol_price}")
        
        while self.running:
            try:
                # Fetch new tokens
                tokens = await self.fetch_new_tokens(limit=20)
                
                # Count new launches
                new_count = sum(1 for t in tokens if t.mint not in self.tokens)
                if new_count > 0:
                    print(f"🆕 {new_count} new tokens detected!")
                
                # Update SOL price every 5 minutes
                if int(time.time()) % 300 < poll_interval:
                    self.sol_price = await self.get_sol_price()
                
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                print(f"⚠️ Tracker error: {e}")
                await asyncio.sleep(poll_interval)
    
    def stop(self):
        """Stop the tracker."""
        self.running = False
    
    def get_hot_tokens(self, min_age_minutes: int = 5, max_age_minutes: int = 60) -> List[PumpToken]:
        """Get tokens that are heating up (launched recently, gaining traction)."""
        now = datetime.now()
        hot = []
        
        for token in self.tokens.values():
            age = (now - token.created_at).total_seconds() / 60
            
            # Filter by age
            if not (min_age_minutes <= age <= max_age_minutes):
                continue
            
            # Must be bonding or recently graduated
            if not token.is_bonding and token.bonding_curve_progress < 95:
                continue
            
            # Minimum activity
            if token.holder_count < 10:
                continue
            
            hot.append(token)
        
        # Sort by market cap
        hot.sort(key=lambda x: x.market_cap_usd, reverse=True)
        return hot[:20]
    
    def get_graduated_tokens(self, hours: int = 24) -> List[PumpToken]:
        """Get tokens that graduated from bonding curve recently."""
        now = datetime.now()
        graduated = []
        
        for token in self.tokens.values():
            if token.is_bonding:
                continue
            
            age = (now - token.created_at).total_seconds() / 3600
            if age <= hours:
                graduated.append(token)
        
        graduated.sort(key=lambda x: x.market_cap_usd, reverse=True)
        return graduated


# Example usage
async def main():
    tracker = PumpFunTracker()
    
    # Callback when new token launches
    def on_new(token: PumpToken):
        print(f"\n🆕 NEW TOKEN: {token.name} (${token.symbol})")
        print(f"   Market Cap: ${token.market_cap_usd:,.0f}")
        print(f"   Bonding: {token.bonding_curve_progress:.1f}%")
        print(f"   Holders: {token.holder_count}")
        if token.twitter:
            print(f"   Twitter: {token.twitter}")
    
    # Callback when token updates
    def on_update(token: PumpToken):
        if token.bonding_curve_progress > 90 and token.bonding_curve_progress < 95:
            print(f"⚠️ {token.symbol} approaching graduation! ({token.bonding_curve_progress:.1f}%)")
    
    tracker.on_new_token(on_new)
    tracker.on_token_update(on_update)
    
    # Run for 60 seconds
    await tracker.run(poll_interval=5)


if __name__ == "__main__":
    asyncio.run(main())
