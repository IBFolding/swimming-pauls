#!/usr/bin/env python3
"""
Simple overnight runner using ask_pauls CLI
Runs predictions every 15 minutes overnight.
"""

import subprocess
import json
import time
from datetime import datetime
import random

QUESTIONS = [
    "Will BTC price go up in the next 4 hours?",
    "Is ETH a good buy right now?",
    "What's the market sentiment for SOL?",
    "Should we hold or sell altcoins?",
    "Is this a bullish or bearish market?",
    "What's the risk level for day trading today?",
]

def run_prediction(question, cycle):
    """Run one prediction cycle."""
    print(f"\n{'='*60}")
    print(f"🦷 Cycle {cycle} - {datetime.now().strftime('%H:%M:%S')}")
    print(f"Q: {question}")
    print('='*60)
    
    try:
        # Run ask_pauls with 50 Pauls
        result = subprocess.run(
            ['python3', 'ask_pauls.py', '--count', '50', '--question', question],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        output = result.stdout
        print(output)
        
        # Log to file
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'cycle': cycle,
            'question': question,
            'output': output
        }
        
        with open('overnight_run.jsonl', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🦷 SWIMMING PAULS - OVERNIGHT RUN")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Running 100 Pauls with Ollama (local LLM)")
    print("Interval: 15 minutes")
    print("Duration: 8 hours (32 cycles)")
    print('='*60)
    
    cycle = 1
    max_cycles = 32  # 8 hours * 4 per hour
    
    while cycle <= max_cycles:
        question = random.choice(QUESTIONS)
        run_prediction(question, cycle)
        
        if cycle < max_cycles:
            print(f"\n⏳ Next cycle in 15 minutes... (Cycle {cycle}/{max_cycles})")
            time.sleep(900)  # 15 minutes
        
        cycle += 1
    
    print(f"\n{'='*60}")
    print("🎉 OVERNIGHT RUN COMPLETE!")
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total cycles: {max_cycles}")
    print("Check overnight_run.jsonl for results")
    print('='*60)

if __name__ == "__main__":
    main()
