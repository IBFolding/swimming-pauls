"""
Swimming Pauls - Backend Fixes
Implements all fixes from INTELLIGENCE_FIX_PLAN.md
"""

import asyncio
import httpx
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PriceData:
    symbol: str
    price: float
    change_24h: float
    timestamp: datetime
    source: str


class PriceFeedFix:
    """Fix 1: Replace subprocess price calls with direct API calls."""
    
    def __init__(self):
        self.cache: Dict[str, PriceData] = {}
        self.cache_ttl = 60  # seconds
        
    async def get_crypto_price(self, symbol: str) -> Optional[PriceData]:
        """Get crypto price from CoinGecko API."""
        # Check cache
        if symbol in self.cache:
            cached = self.cache[symbol]
            if (datetime.now() - cached.timestamp).seconds < self.cache_ttl:
                return cached
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Map symbol to CoinGecko ID
                coin_id = self._symbol_to_id(symbol)
                url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true"
                
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if coin_id in data:
                        price_data = PriceData(
                            symbol=symbol.upper(),
                            price=data[coin_id]["usd"],
                            change_24h=data[coin_id].get("usd_24h_change", 0),
                            timestamp=datetime.now(),
                            source="coingecko"
                        )
                        self.cache[symbol] = price_data
                        return price_data
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
        
        return None
    
    async def get_stock_price(self, symbol: str) -> Optional[PriceData]:
        """Get stock price from Yahoo Finance."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Yahoo Finance API
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
                response = await client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    result = data.get("chart", {}).get("result", [{}])[0]
                    meta = result.get("meta", {})
                    price = meta.get("regularMarketPrice", 0)
                    prev_close = meta.get("previousClose", price)
                    change = ((price - prev_close) / prev_close * 100) if prev_close else 0
                    
                    price_data = PriceData(
                        symbol=symbol.upper(),
                        price=price,
                        change_24h=change,
                        timestamp=datetime.now(),
                        source="yahoo_finance"
                    )
                    self.cache[symbol] = price_data
                    return price_data
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
        
        return None
    
    def _symbol_to_id(self, symbol: str) -> str:
        """Map common symbols to CoinGecko IDs."""
        mapping = {
            "BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana",
            "BNB": "binancecoin", "XRP": "ripple", "ADA": "cardano",
            "DOGE": "dogecoin", "TRX": "tron", "AVAX": "avalanche-2",
            "LINK": "chainlink", "DOT": "polkadot", "MATIC": "matic-network",
            "UNI": "uniswap", "LTC": "litecoin", "BCH": "bitcoin-cash",
            "ATOM": "cosmos", "ETC": "ethereum-classic", "XLM": "stellar",
            "NEAR": "near", "FIL": "filecoin", "ALGO": "algorand",
            "VET": "vechain", "ICP": "internet-computer", "APT": "aptos",
            "HBAR": "hedera-hashgraph"
        }
        return mapping.get(symbol.upper(), symbol.lower())
    
    def is_price_stale(self, symbol: str, max_age_seconds: int = 600) -> bool:
        """Check if cached price is stale."""
        if symbol not in self.cache:
            return True
        age = (datetime.now() - self.cache[symbol].timestamp).seconds
        return age > max_age_seconds


class DataCleanupFix:
    """Fix 2: Clean up anomalous trades and recalculate portfolios."""
    
    def __init__(self, db_path: str = "data/paul_learning.db"):
        self.db_path = db_path
        self.price_ranges = {
            "BTC": (10000, 500000), "ETH": (500, 20000), "SOL": (10, 500),
            "AAPL": (50, 500), "TSLA": (50, 1000), "NVDA": (100, 2000),
            "SPY": (200, 800), "QQQ": (150, 600), "MSFT": (100, 1000),
            "GOOGL": (50, 500), "AMZN": (50, 500), "META": (100, 1000)
        }
    
    def invalidate_anomalous_trades(self) -> int:
        """Invalidate trades with prices outside reasonable ranges."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        invalidated = 0
        for symbol, (min_price, max_price) in self.price_ranges.items():
            cursor.execute("""
                UPDATE paper_trades 
                SET status = 'invalidated', 
                    notes = 'Invalidated: price outside reasonable range'
                WHERE symbol = ? 
                AND (entry_price < ? OR entry_price > ? OR exit_price < ? OR exit_price > ?)
                AND status != 'invalidated'
            """, (symbol, min_price, max_price, min_price, max_price))
            invalidated += cursor.rowcount
        
        conn.commit()
        conn.close()
        logger.info(f"Invalidated {invalidated} anomalous trades")
        return invalidated
    
    def recalculate_portfolios(self) -> Dict[str, float]:
        """Recalculate portfolio values from actual closed trades."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all closed valid trades
        cursor.execute("""
            SELECT wallet, SUM(pnl) as total_pnl, COUNT(*) as trade_count
            FROM paper_trades
            WHERE status = 'closed' AND pnl IS NOT NULL
            GROUP BY wallet
        """)
        
        portfolios = {}
        for row in cursor.fetchall():
            wallet, total_pnl, trade_count = row
            starting_balance = 100000  # Default starting balance
            current_balance = starting_balance + total_pnl
            
            portfolios[wallet] = {
                "starting_balance": starting_balance,
                "current_balance": current_balance,
                "total_pnl": total_pnl,
                "trade_count": trade_count
            }
            
            # Update portfolio in database
            cursor.execute("""
                INSERT OR REPLACE INTO paper_portfolios 
                (wallet, starting_balance, current_balance, total_pnl, trade_count, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (wallet, starting_balance, current_balance, total_pnl, trade_count, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Recalculated {len(portfolios)} portfolios")
        return portfolios


class PredictionResolutionFix:
    """Fix 3: Auto-resolve predictions when trades close."""
    
    def __init__(self, db_path: str = "data/paul_learning.db"):
        self.db_path = db_path
    
    def link_predictions_to_trades(self):
        """Add pred_id column to paper_trades if not exists."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(paper_trades)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "pred_id" not in columns:
            cursor.execute("ALTER TABLE paper_trades ADD COLUMN pred_id TEXT")
            logger.info("Added pred_id column to paper_trades")
        
        conn.commit()
        conn.close()
    
    def resolve_prediction_for_trade(self, trade_id: str, actual_outcome: str, accuracy: float):
        """Resolve a prediction when its linked trade closes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the prediction ID for this trade
        cursor.execute("SELECT pred_id FROM paper_trades WHERE id = ?", (trade_id,))
        row = cursor.fetchone()
        
        if row and row[0]:
            pred_id = row[0]
            
            # Update prediction as resolved
            cursor.execute("""
                UPDATE predictions 
                SET resolved = TRUE, 
                    actual_outcome = ?,
                    accuracy = ?,
                    resolved_at = ?
                WHERE id = ? AND resolved = FALSE
            """, (actual_outcome, accuracy, datetime.now().isoformat(), pred_id))
            
            if cursor.rowcount > 0:
                logger.info(f"Resolved prediction {pred_id} for trade {trade_id}")
        
        conn.commit()
        conn.close()
    
    def batch_resolve_pending(self) -> int:
        """Resolve all pending predictions that have closed trades."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find trades with predictions that are closed but predictions not resolved
        cursor.execute("""
            SELECT pt.id, pt.pred_id, pt.pnl, pt.symbol
            FROM paper_trades pt
            JOIN predictions p ON pt.pred_id = p.id
            WHERE pt.status = 'closed' 
            AND p.resolved = FALSE
            AND pt.pred_id IS NOT NULL
        """)
        
        resolved = 0
        for row in cursor.fetchall():
            trade_id, pred_id, pnl, symbol = row
            
            # Determine outcome based on PnL
            outcome = "bullish" if pnl > 0 else "bearish" if pnl < 0 else "neutral"
            accuracy = min(abs(pnl) / 100, 1.0) if pnl != 0 else 0.5
            
            cursor.execute("""
                UPDATE predictions 
                SET resolved = TRUE, 
                    actual_outcome = ?,
                    accuracy = ?,
                    resolved_at = ?
                WHERE id = ?
            """, (outcome, accuracy, datetime.now().isoformat(), pred_id))
            
            resolved += cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Batch resolved {resolved} predictions")
        return resolved


class LLMResponseFix:
    """Fix 4: Improve LLM responses to avoid 100% neutral."""
    
    IMPROVED_PROMPT = """You are a crypto trading analyst. Analyze the following market data and give a DIRECT trading signal.

Market Data:
{market_data}

Rules:
1. You MUST choose: BULLISH or BEARISH (rarely NEUTRAL)
2. Confidence: 50-99%
3. Be decisive - no hedging

Respond EXACTLY in this format:
SENTIMENT: [bullish/bearish/neutral]
CONFIDENCE: [number]%
REASON: [one sentence]

Your response:"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "qwen2.5:7b"  # Faster than 14b, good quality
        self.timeout = 120  # Increased from 45
        self.max_tokens = 30  # Reduced from 60
    
    async def get_prediction(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get prediction from LLM with improved prompt."""
        prompt = self.IMPROVED_PROMPT.format(market_data=json.dumps(market_data, indent=2))
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": self.max_tokens,
                            "temperature": 0.7
                        }
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("response", "")
                    
                    # Parse response
                    parsed = self._parse_response(text)
                    
                    # Validate - if neutral with high confidence, retry once
                    if parsed["sentiment"] == "neutral" and parsed["confidence"] > 80:
                        logger.warning("Got neutral with high confidence, retrying...")
                        return await self._retry_with_stronger_prompt(market_data)
                    
                    return parsed
                else:
                    logger.error(f"Ollama error: {response.status_code}")
                    return {"sentiment": "neutral", "confidence": 50, "reason": "API error"}
                    
        except httpx.TimeoutException:
            logger.error("Ollama timeout")
            return {"sentiment": "neutral", "confidence": 50, "reason": "Timeout"}
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return {"sentiment": "neutral", "confidence": 50, "reason": str(e)}
    
    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse LLM response."""
        text_lower = text.lower()
        
        sentiment = "neutral"
        if "bullish" in text_lower:
            sentiment = "bullish"
        elif "bearish" in text_lower:
            sentiment = "bearish"
        
        # Extract confidence
        confidence = 50
        import re
        match = re.search(r'(\d+)%', text)
        if match:
            confidence = int(match.group(1))
        
        # Extract reason
        reason = ""
        if "reason:" in text_lower:
            reason = text.split("reason:", 1)[1].strip()
        
        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "reason": reason,
            "raw": text
        }
    
    async def _retry_with_stronger_prompt(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Retry with stronger directive to avoid neutral."""
        stronger_prompt = """FORCE A DIRECTION. Market data:
{data}

CHOOSE NOW:
1. BULLISH (buy signal)
2. BEARISH (sell signal)

SENTIMENT: [pick one]
CONFIDENCE: [50-99]%""".format(data=json.dumps(market_data))
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": stronger_prompt,
                        "stream": False,
                        "options": {"num_predict": 20, "temperature": 0.8}
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get("response", "")
                    return self._parse_response(text)
        except Exception as e:
            logger.error(f"Retry failed: {e}")
        
        return {"sentiment": "neutral", "confidence": 50, "reason": "Retry failed"}


async def run_all_fixes():
    """Run all backend fixes."""
    logger.info("Starting backend fixes...")
    
    # Fix 1: Price feed
    logger.info("\n=== Fix 1: Testing Price Feed ===")
    price_feed = PriceFeedFix()
    btc_price = await price_feed.get_crypto_price("BTC")
    if btc_price:
        logger.info(f"BTC Price: ${btc_price.price:,.2f} (from {btc_price.source})")
    else:
        logger.error("Failed to fetch BTC price")
    
    # Fix 2: Data cleanup
    logger.info("\n=== Fix 2: Data Cleanup ===")
    cleanup = DataCleanupFix()
    invalidated = cleanup.invalidate_anomalous_trades()
    portfolios = cleanup.recalculate_portfolios()
    logger.info(f"Recalculated {len(portfolios)} portfolios")
    
    # Fix 3: Prediction resolution
    logger.info("\n=== Fix 3: Prediction Resolution ===")
    resolver = PredictionResolutionFix()
    resolver.link_predictions_to_trades()
    resolved = resolver.batch_resolve_pending()
    
    # Fix 4: Test LLM
    logger.info("\n=== Fix 4: Testing LLM ===")
    llm_fix = LLMResponseFix()
    test_data = {"BTC": 87000, "trend": "up", "volume": "high"}
    prediction = await llm_fix.get_prediction(test_data)
    logger.info(f"Test prediction: {prediction['sentiment']} ({prediction['confidence']}%)")
    
    logger.info("\n=== All fixes complete ===")
    return {
        "prices_working": btc_price is not None,
        "trades_invalidated": invalidated,
        "portfolios_recalculated": len(portfolios),
        "predictions_resolved": resolved,
        "llm_test": prediction
    }


if __name__ == "__main__":
    result = asyncio.run(run_all_fixes())
    print(json.dumps(result, indent=2))
