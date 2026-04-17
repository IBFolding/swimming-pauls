#!/bin/bash
cd /Users/brain/.openclaw/workspace/swimming_pauls

# Simulate 20 trades per curated Paul
python3 << 'EOF'
import random
from paper_trading import PaperTradingManager
from curated_evolution import CuratedPaulEvolution

# Load curated Pauls
evolution = CuratedPaulEvolution()
curated = evolution.curated_pauls

print(f"🎲 Simulating trades for {len(curated)} curated Pauls...")

manager = PaperTradingManager()

for i, paul_name in enumerate(curated):
    if paul_name not in manager.portfolios:
        continue
    
    portfolio = manager.portfolios[paul_name]
    if not portfolio.enabled:
        continue
    
    # Simulate 10-30 trades
    num_trades = random.randint(10, 30)
    
    for _ in range(num_trades):
        symbol = random.choice(["BTC", "ETH", "SOL", "AVAX", "MATIC"])
        direction = random.choice(["buy", "sell"])
        confidence = random.uniform(0.75, 0.95)
        entry_price = random.uniform(50, 500)
        
        trade = manager.execute_trade(
            paul_name=paul_name,
            symbol=symbol,
            direction=direction,
            current_price=entry_price,
            confidence=confidence
        )
        
        if trade and random.random() < 0.7:
            exit_price = entry_price * random.uniform(0.85, 1.20)
            manager.close_trade(trade.id, exit_price, "simulated")
    
    if (i + 1) % 100 == 0:
        print(f"  Processed {i+1}/{len(curated)}...")

print(f"✅ Simulated trades for {len(curated)} Pauls")
EOF