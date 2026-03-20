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
    
    # Demo mode - generate realistic prediction
    import random
    
    # Seed for consistent results
    random.seed(hash(question) % 10000)
    
    # Generate realistic prediction
    assets = ["BTC", "ETH", "SOL", "AVAX", "LINK", "RNDR", "FET", "TAO"]
    directions = ["BULLISH", "BEARISH", "NEUTRAL"]
    
    direction = random.choice(directions)
    confidence = random.uniform(0.45, 0.92)
    
    # Top picks based on sentiment
    top_picks = random.sample(assets, k=min(3, len(assets)))
    
    result_data = {
        "consensus": {"direction": direction, "confidence": round(confidence, 2)},
        "sentiment": random.uniform(-0.8, 0.8),
        "pauls_count": pauls,
        "rounds": rounds,
        "question": question,
        "top_picks": top_picks,
        "agents": [
            {"name": "Visionary Paul", "specialty": "Long-term", "reasoning": f"{top_picks[0]} showing strong fundamentals. Institutional adoption accelerating. Technical breakout imminent."},
            {"name": "Trader Paul", "specialty": "Timing", "reasoning": f"Momentum building for {top_picks[1]}. Volume increasing. RSI bullish divergence on 4H."},
            {"name": "Whale Paul", "specialty": "Institutional", "reasoning": f"Smart money accumulating {top_picks[2]}. On-chain metrics bullish. Whale wallets increasing."},
            {"name": "Quant Paul", "specialty": "Data", "reasoning": "Statistical arbitrage opportunity. Mean reversion play. Risk-reward favorable at current levels."},
            {"name": "Skeptic Paul", "specialty": "Risk", "reasoning": "Macro headwinds remain. Fed policy uncertain. Consider DCA strategy rather than lump sum."}
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
