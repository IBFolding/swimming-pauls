#!/usr/bin/env python3
"""Auto-trading engine with domain-aware learning system.

Uses Ollama with memory-enhanced prompts for intelligent predictions.
Tracks Paul accuracy per domain for continuous learning.
"""
import asyncio
import random
import time
import json
import subprocess
import sys
import yaml
from datetime import datetime
from pathlib import Path
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from paul_world import PaulWorld
from paul_learning import get_learning_system

# Config
OLLAMA_MODEL = "qwen2.5:14b"
OLLAMA_URL = "http://localhost:11434"
DOMAIN = "trading"  # Default, loaded from config

# Load domain from config
def load_domain():
    try:
        config_path = Path(__file__).parent / 'config.yaml'
        if config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config.get('domain', 'trading')
    except:
        pass
    return 'trading'

DOMAIN = load_domain()

# Market symbols
SYMBOLS = ['BTC', 'ETH', 'SOL', 'SPY', 'AAPL', 'TSLA', 'NVDA', 'DOGE', 'LINK', 'UNI', 'AAVE', 'COMP']

DEFAULT_PRICES = {
    'BTC': 65000, 'ETH': 3500, 'SOL': 130, 
    'SPY': 500, 'AAPL': 180, 'TSLA': 180, 
    'NVDA': 900, 'DOGE': 0.15, 'LINK': 15,
    'UNI': 8, 'AAVE': 120, 'COMP': 65
}

PRICE_CACHE = {}
CACHE_TIME = {}
CACHE_DURATION = 30

# Initialize learning system
learning = get_learning_system()

async def query_ollama(prompt: str) -> str:
    """Query Ollama with timeout."""
    try:
        result = subprocess.run(
            ['curl', '-s', '-X', 'POST', f'{OLLAMA_URL}/api/generate',
             '-H', 'Content-Type: application/json',
             '-d', json.dumps({
                 'model': OLLAMA_MODEL,
                 'prompt': prompt,
                 'stream': False,
                 'options': {'temperature': 0.7, 'num_predict': 60}
             })],
            capture_output=True, text=True, timeout=45
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get('response', '').strip()
    except Exception as e:
        print(f"  ⚠️  LLM error: {e}")
    return ''

async def get_llm_prediction(symbol: str, price: float, paul_name: str) -> tuple:
    """Get prediction with memory-enhanced prompt."""
    # Build prompt with track record
    prompt = learning.format_prompt_with_memory(paul_name, DOMAIN, symbol, price)
    
    response = await query_ollama(prompt)
    
    # Parse response
    sentiment = 'neutral'
    confidence = 0.75
    reasoning = ''
    
    if 'bullish' in response.lower():
        sentiment = 'bullish'
    elif 'bearish' in response.lower():
        sentiment = 'bearish'
    
    # Extract confidence
    try:
        for line in response.split('\n'):
            if 'confidence' in line.lower() or '%' in line:
                nums = [int(n) for n in line.split() if n.isdigit()]
                if nums:
                    confidence = min(0.95, max(0.70, nums[0] / 100))
    except:
        confidence = random.uniform(0.75, 0.90)
    
    # Extract reasoning
    if 'reasoning' in response.lower() or ':' in response:
        parts = response.split(':')
        if len(parts) > 1:
            reasoning = parts[-1].strip()[:100]
    
    return sentiment, confidence, reasoning

async def fetch_price(symbol: str) -> float:
    """Fetch current price."""
    now = datetime.now().timestamp()
    
    if symbol in PRICE_CACHE and (now - CACHE_TIME.get(symbol, 0)) < CACHE_DURATION:
        cached = PRICE_CACHE[symbol]
        if cached and cached > 0.01:
            return cached
    
    price = None
    try:
        result = subprocess.run(
            ['python3', '/Users/brain/.openclaw/workspace/skills/crypto-price/scripts/get_price_chart.py', symbol, '1h'],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            price = data.get('price')
    except:
        pass
    
    if price and price > 0.01:
        PRICE_CACHE[symbol] = price
        CACHE_TIME[symbol] = now
        return price
    
    fallback = DEFAULT_PRICES.get(symbol)
    if fallback and fallback > 0.01:
        return fallback
    
    return None

async def auto_trading_loop():
    """Main trading loop with learning."""
    print(f"🦷 PAUL'S WORLD - LEARNING ENABLED ({DOMAIN})")
    print("=" * 60)
    
    world = PaulWorld()
    await world.initialize()
    pt = world.paper_trading
    
    if pt.mode.value != 'competition':
        pt.start_competition(7)
    
    for p in pt.portfolios.values():
        p.enabled = True
    
    pauls_list = list(world.pauls.keys())
    
    print(f"✅ {len(pauls_list):,} Pauls | Domain: {DOMAIN}")
    print(f"🧠 Learning system active")
    print("💰 Trading with memory-enhanced LLM...\n")
    
    trade_count = 0
    llm_calls = 0
    last_summary = time.time()
    
    try:
        while True:
            await asyncio.sleep(random.uniform(8, 15))  # Slower for learning
            
            paul_name = random.choice(pauls_list)
            symbol = random.choice(SYMBOLS)
            price = await fetch_price(symbol)
            
            if not price:
                continue
            
            # Get LLM prediction with memory
            sentiment, confidence, reasoning = await get_llm_prediction(symbol, price, paul_name)
            llm_calls += 1
            
            # Record prediction for learning
            pred_id = learning.record_prediction(
                paul_name=paul_name,
                domain=DOMAIN,
                symbol=symbol,
                prediction=f"{sentiment} - {reasoning}",
                direction=sentiment,
                confidence=confidence,
                question=f"Should I trade {symbol} at ${price}?"
            )
            
            if sentiment != 'neutral' and confidence >= 0.75:
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
                    if trade_count % 2 == 0:
                        emoji = "🚀" if sentiment == 'bullish' else "🔻"
                        print(f"{emoji} {paul_name[:18]:<18} {direction.upper():4} {symbol:<6} @ ${price:>8,.0f} ({confidence:.0%})")
            
            if time.time() - last_summary > 60:
                print(f"\n📊 Trades: {trade_count} | LLM calls: {llm_calls} | Domain: {DOMAIN}")
                
                # Show top expert
                experts = learning.get_domain_experts(DOMAIN, 1)
                if experts:
                    print(f"🏆 Top expert: {experts[0][0]} ({experts[0][1]*100:.0f}% accuracy)")
                
                last_summary = time.time()
                trade_count = 0
                llm_calls = 0
                await world._save_world()
                
    except KeyboardInterrupt:
        await world._save_world()
        print("\n💾 Saved learning data")

if __name__ == "__main__":
    asyncio.run(auto_trading_loop())
