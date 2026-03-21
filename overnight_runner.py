#!/usr/bin/env python3
"""
Overnight Paul's World Runner
Runs 100 Pauls with local LLM, paper trading, and data ingestion.

Usage: python overnight_runner.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

# Mock config for local LLM
os.environ['LLM_PROVIDER'] = 'ollama'
os.environ['OLLAMA_MODEL'] = 'qwen3-coder:latest'

from swimming_pauls import PersonaFactory, Simulation

# Overnight run configuration
CONFIG = {
    'paul_count': 100,  # Start small with local LLM
    'rounds': 5,
    'questions_per_hour': 4,  # 4 predictions per hour
    'hours_to_run': 8,  # Run overnight (8 hours)
    'enable_paper_trading': True,
    'initial_balance': 10000,
    'data_ingestion': True,
}

PREDICTION_QUESTIONS = [
    "Will BTC price increase in the next 4 hours?",
    "Is now a good time to buy ETH?",
    "What's the sentiment on SOL?",
    "Should we hold or sell current positions?",
    "Which altcoin has the most upside potential?",
    "Is the market bullish or bearish right now?",
    "What's the risk level for trading today?",
]

async def run_prediction_cycle(pauls, cycle_num):
    """Run one prediction cycle with all Pauls."""
    import random
    question = random.choice(PREDICTION_QUESTIONS)
    
    print(f"\n{'='*60}")
    print(f"🦷 Cycle {cycle_num} - {datetime.now().strftime('%H:%M:%S')}")
    print(f"Question: {question}")
    print('='*60)
    
    try:
        # Run simulation
        result = await Simulation.run(
            question=question,
            agents=pauls,
            rounds=CONFIG['rounds']
        )
        
        # Log result
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'cycle': cycle_num,
            'question': question,
            'consensus': result.get('consensus', {}),
            'sentiment': result.get('sentiment', 0),
            'agent_count': len(pauls)
        }
        
        # Save to log file
        with open('overnight_log.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        # Print summary
        consensus = result.get('consensus', {})
        print(f"✅ Consensus: {consensus.get('direction', 'UNKNOWN')}")
        print(f"   Confidence: {consensus.get('confidence', 0):.1%}")
        print(f"   Sentiment: {result.get('sentiment', 0):+.2f}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in cycle {cycle_num}: {e}")
        return None

async def main():
    """Main overnight runner."""
    print("🦷 SWIMMING PAULS - OVERNIGHT RUN")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {CONFIG['hours_to_run']} hours")
    print(f"Pauls: {CONFIG['paul_count']}")
    print(f"Model: {os.environ.get('OLLAMA_MODEL', 'unknown')}")
    print('='*60)
    
    # Generate Pauls
    print("\n👥 Generizing Pauls...")
    pauls = PersonaFactory.generate_pauls(count=CONFIG['paul_count'])
    print(f"✅ Generated {len(pauls)} Pauls")
    
    # Calculate total cycles
    total_cycles = CONFIG['hours_to_run'] * CONFIG['questions_per_hour']
    cycle_delay = 3600 / CONFIG['questions_per_hour']  # seconds between cycles
    
    print(f"\n🚀 Starting {total_cycles} prediction cycles...")
    print(f"Interval: {cycle_delay/60:.0f} minutes between cycles\n")
    
    # Run cycles
    for cycle in range(1, total_cycles + 1):
        result = await run_prediction_cycle(pauls, cycle)
        
        if cycle < total_cycles:
            print(f"\n⏳ Sleeping for {cycle_delay/60:.0f} minutes...")
            await asyncio.sleep(cycle_delay)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 OVERNIGHT RUN COMPLETE")
    print(f"Ended: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Cycles completed: {total_cycles}")
    print(f"Log saved to: overnight_log.jsonl")
    print('='*60)

if __name__ == "__main__":
    asyncio.run(main())
