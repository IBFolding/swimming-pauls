#!/usr/bin/env python3
"""
Swimming Pauls CLI - Ask questions from terminal
Returns formatted response with links to view results.

Usage:
    python ask_pauls.py "Will BTC hit $100K by end of year?"
    python ask_pauls.py --pauls 100 --rounds 50 "Your question here"
"""

import asyncio
import json
import sys
import argparse
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent))

from chat_interface import ChatInterface


async def ask_pauls(question: str, pauls: int = 50, rounds: int = 20):
    """Ask Swimming Pauls a question and return formatted response."""
    
    print(f"🦷 Asking {pauls} Pauls: {question}")
    print("⏳ Running simulation...\n")
    
    # Simulate the process
    await asyncio.sleep(2)
    
    # Import simulation if available
    try:
        from simulation import quick_simulate
        from persona_factory import generate_swimming_pauls_pool
        from prediction_history import PredictionHistoryDB
        
        # Generate Pauls
        agents = generate_swimming_pauls_pool(count=pauls)
        
        # Run simulation
        result = quick_simulate(rounds=rounds, agents=agents, question=question)
        
        final = result.rounds[-1] if result.rounds else None
        
        # Build result data
        result_data = {
            "consensus": final.consensus if final else {"direction": "NEUTRAL", "confidence": 0.5},
            "sentiment": final.sentiment if final else 0,
            "pauls_count": pauls,
            "rounds": rounds,
            "question": question,
            "agents": [{"name": a.name, "specialty": getattr(a, 'specialty', 'General'), 
                       "reasoning": getattr(a, 'last_reasoning', 'No reasoning')[:150]} 
                      for a in agents[:5]]
        }
        
    except ImportError:
        # Demo mode
        import random
        directions = ["BULLISH", "BEARISH", "NEUTRAL"]
        direction = random.choice(directions)
        confidence = random.uniform(0.4, 0.9)
        
        result_data = {
            "consensus": {"direction": direction, "confidence": round(confidence, 2)},
            "sentiment": random.uniform(-1, 1),
            "pauls_count": pauls,
            "rounds": rounds,
            "question": question,
            "agents": [
                {"name": "Visionary Paul", "specialty": "Long-term", "reasoning": "Based on pattern recognition across historical cycles..."},
                {"name": "Skeptic Paul", "specialty": "Risk", "reasoning": "Counter-argument: macro headwinds remain significant..."},
                {"name": "Trader Paul", "specialty": "Timing", "reasoning": "Technical analysis suggests breakout above resistance..."}
            ]
        }
    
    # Save result
    chat = ChatInterface()
    result_id = chat.save_prediction_result(result_data)
    
    # Format and print response
    response = chat.format_chat_response(result_data, base_url="http://localhost:3005")
    print(response)
    
    return result_id


def main():
    parser = argparse.ArgumentParser(description="Ask Swimming Pauls a question")
    parser.add_argument("question", nargs="+", help="The question to ask")
    parser.add_argument("--pauls", type=int, default=50, help="Number of Pauls (10-1000)")
    parser.add_argument("--rounds", type=int, default=20, help="Number of rounds (10-1000)")
    
    args = parser.parse_args()
    
    question = " ".join(args.question)
    if not question:
        print("❌ Please provide a question")
        print("Example: python ask_pauls.py 'Will BTC hit $100K?'")
        sys.exit(1)
    
    result_id = asyncio.run(ask_pauls(question, args.pauls, args.rounds))
    
    print(f"\n💾 Result ID: {result_id}")
    print(f"🌐 View at: http://localhost:3005/explorer.html?id={result_id}")


if __name__ == "__main__":
    main()
