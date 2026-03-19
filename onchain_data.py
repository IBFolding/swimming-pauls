"""
On-Chain Data Integration for Swimming Pauls
Provides real-time blockchain data for prediction context.

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TokenData:
    """Token on-chain data."""
    symbol: str
    price_usd: float
    price_change_24h: float
    volume_24h: float
    market_cap: float
    
    # On-chain metrics
    holder_count: int
    whale_wallets: List[str]  # Top 10 wallets
    recent_transactions: int  # Last hour
    
    # DeFi metrics (if applicable)
    tvl: Optional[float] = None  # Total Value Locked
    staking_apy: Optional[float] = None
    
    timestamp: datetime = datetime.now()

@dataclass
class WalletActivity:
    """Whale wallet activity."""
    wallet_address: str
    token: str
    action: str  # "buy", "sell", "stake", "unstake"
    amount: float
    value_usd: float
    timestamp: datetime

@dataclass
class DeFiData:
    """DeFi protocol data."""
    protocol: str  # "solend", "mango", "jupiter", etc.
    total_tvl: float
    volume_24h: float
    top_pools: List[Dict[str, Any]]
    yield_opportunities: List[Dict[str, float]]


class OnChainDataProvider:
    """
    Provides on-chain data for predictions.
    
    Features:
    - Real-time token prices
    - Whale wallet tracking
    - DeFi TVL and yields
    - Transaction flow analysis
    """
    
    def __init__(self):
        self.cache = {}
        self.last_update = {}
    
    async def get_token_data(self, symbol: str, chain: str = "solana") -> Optional[TokenData]:
        """Get comprehensive on-chain data for a token."""
        try:
            # Use existing skill_bridge or web_intelligence
            from skill_bridge import get_skill_bridge
            
            bridge = get_skill_bridge()
            
            # Get price data
            price_data = await bridge.get_crypto_price(symbol.lower())
            
            # Get additional on-chain data (if available)
            # This would connect to Solana/Base RPC nodes
            
            return TokenData(
                symbol=symbol.upper(),
                price_usd=price_data.get('price', 0),
                price_change_24h=price_data.get('change_24h', 0),
                volume_24h=price_data.get('volume', 0),
                market_cap=price_data.get('market_cap', 0),
                holder_count=0,  # Would need RPC call
                whale_wallets=[],
                recent_transactions=0
            )
            
        except Exception as e:
            print(f"⚠️  Could not fetch on-chain data for {symbol}: {e}")
            return None
    
    async def get_whale_activity(self, token: str, hours: int = 24) -> List[WalletActivity]:
        """Get recent whale wallet activity."""
        # This would scan for large transactions
        # Returns buy/sell patterns from large wallets
        return []
    
    async def get_defi_data(self, protocol: Optional[str] = None) -> List[DeFiData]:
        """Get DeFi protocol data."""
        # TVL, yields, top pools
        return []
    
    def format_for_pauls(self, data: TokenData) -> str:
        """Format on-chain data for Paul context."""
        context = f"""
On-Chain Data for {data.symbol}:
- Price: ${data.price_usd:.2f} ({data.price_change_24h:+.1f}% 24h)
- Volume: ${data.volume_24h:,.0f}
- Market Cap: ${data.market_cap:,.0f}
"""
        
        if data.tvl:
            context += f"- TVL: ${data.tvl:,.0f}\n"
        
        if data.holder_count > 0:
            context += f"- Holders: {data.holder_count:,}\n"
        
        return context


# Integration with Paul's World predictions
async def enrich_prediction_with_onchain(
    question: str,
    base_result: Dict
) -> Dict:
    """
    Enrich a prediction result with on-chain data.
    
    Extracts tokens mentioned in question and adds relevant
    on-chain metrics to the result.
    """
    provider = OnChainDataProvider()
    
    # Extract potential tokens from question
    tokens = extract_tokens_from_question(question)
    
    onchain_context = {}
    
    for token in tokens:
        data = await provider.get_token_data(token)
        if data:
            onchain_context[token] = {
                'price': data.price_usd,
                'change_24h': data.price_change_24h,
                'volume': data.volume_24h,
                'formatted': provider.format_for_pauls(data)
            }
    
    # Add to result
    base_result['onchain_data'] = onchain_context
    base_result['has_onchain_context'] = len(onchain_context) > 0
    
    return base_result


def extract_tokens_from_question(question: str) -> List[str]:
    """Extract potential token symbols from a question."""
    question_upper = question.upper()
    
    # Common tokens to check for
    token_keywords = {
        'BTC': ['BTC', 'BITCOIN'],
        'ETH': ['ETH', 'ETHEREUM'],
        'SOL': ['SOL', 'SOLANA'],
        'BNB': ['BNB', 'BINANCE'],
        'ADA': ['ADA', 'CARDANO'],
        'DOT': ['DOT', 'POLKADOT'],
        'AVAX': ['AVAX', 'AVALANCHE'],
        'MATIC': ['MATIC', 'POLYGON'],
        'ARB': ['ARB', 'ARBITRUM'],
        'OP': ['OP', 'OPTIMISM'],
        'BASE': ['BASE', 'BASECHAIN'],
    }
    
    found = []
    for token, keywords in token_keywords.items():
        if any(kw in question_upper for kw in keywords):
            found.append(token)
    
    return found


# Example usage
if __name__ == "__main__":
    async def test():
        provider = OnChainDataProvider()
        
        # Get SOL data
        sol_data = await provider.get_token_data("SOL")
        if sol_data:
            print(provider.format_for_pauls(sol_data))
        
        # Enrich a prediction
        result = await enrich_prediction_with_onchain(
            "Will SOL hit $200?",
            {'consensus': {'direction': 'BULLISH', 'confidence': 0.75}}
        )
        print(f"\nEnriched with {len(result.get('onchain_data', {}))} tokens")
    
    asyncio.run(test())
