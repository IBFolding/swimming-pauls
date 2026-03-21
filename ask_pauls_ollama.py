#!/usr/bin/env python3
"""
Swimming Pauls CLI - Ask questions using local LLM (Ollama)

Usage:
    python ask_pauls_ollama.py "Will BTC hit $100K by end of year?"
    python ask_pauls_ollama.py --pauls 50 --question "Your question"
"""

import asyncio
import json
import sys
import argparse
import random
from pathlib import Path
import httpx
from datetime import datetime

# Ollama config
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen3-coder:latest"  # or qwen2.5:14b when downloaded

# Paul personas
PAULS = [
    {"name": "Visionary Paul", "specialty": "Long-term trends", "style": "Sees the big picture, focuses on fundamentals"},
    {"name": "Trader Paul", "specialty": "Technical analysis", "style": "Reads charts, follows momentum"},
    {"name": "Whale Paul", "specialty": "Institutional flows", "style": "Follows smart money, on-chain data"},
    {"name": "Quant Paul", "specialty": "Statistical models", "style": "Data-driven, mathematical"},
    {"name": "Skeptic Paul", "specialty": "Risk management", "style": "Cautious, looks for downside"},
    {"name": "Degen Paul", "specialty": "Sentiment", "style": "Gut feel, market vibes"},
    {"name": "Macro Paul", "specialty": "Global economics", "style": "Fed policy, geopolitics"},
    {"name": "News Paul", "specialty": "Event-driven", "style": "Breaking news, catalysts"},
]

async def ask_ollama(prompt: str) -> str:
    """Send prompt to Ollama and get response."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 100
                    }
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json().get("response", "")
    except Exception as e:
        return f"Error: {e}"

async def run_paul(paul: dict, question: str) -> dict:
    """Run a single Paul with the question."""
    prompt = f"""You are {paul['name']}, a {paul['specialty']} trader.
Your style: {paul['style']}

Question: {question}

Respond in this exact format:
DIRECTION: [BULLISH/BEARISH/NEUTRAL]
CONFIDENCE: [0-100]
REASONING: [one sentence]

Be decisive."""
    
    response = await ask_ollama(prompt)
    
    # Parse response
    direction = "NEUTRAL"
    confidence = 50
    
    if "BULLISH" in response.upper():
        direction = "BULLISH"
    elif "BEARISH" in response.upper():
        direction = "BEARISH"
    
    # Extract confidence
    for line in response.split('\n'):
        if 'CONFIDENCE:' in line:
            try:
                conf = int(''.join(filter(str.isdigit, line)))
                confidence = min(100, max(0, conf))
            except:
                pass
    
    return {
        "name": paul['name'],
        "direction": direction,
        "confidence": confidence / 100,
        "reasoning": response.split('REASONING:')[-1].strip()[:100] if 'REASONING:' in response else response[:100]
    }

async def ask_pauls(question: str, paul_count: int = 50):
    """Ask multiple Pauls and aggregate."""
    print(f"🦷 Asking {paul_count} Pauls via Ollama...")
    print(f"Model: {OLLAMA_MODEL}")
    print(f"Q: {question}\n")
    
    # Select random Pauls
    selected_pauls = random.sample(PAULS, min(paul_count, len(PAULS)))
    
    # Run all Pauls concurrently (limited to not overwhelm Ollama)
    results = []
    batch_size = 4  # Ollama can handle 4 concurrent requests on M4
    
    for i in range(0, len(selected_pauls), batch_size):
        batch = selected_pauls[i:i+batch_size]
        batch_results = await asyncio.gather(*[
            run_paul(paul, question) for paul in batch
        ])
        results.extend(batch_results)
        print(f"  Completed {len(results)}/{len(selected_pauls)} Pauls...")
        await asyncio.sleep(0.5)  # Brief pause between batches
    
    # Aggregate results
    bullish = sum(1 for r in results if r['direction'] == 'BULLISH')
    bearish = sum(1 for r in results if r['direction'] == 'BEARISH')
    neutral = len(results) - bullish - bearish
    
    avg_confidence = sum(r['confidence'] for r in results) / len(results)
    sentiment = (bullish - bearish) / len(results)
    
    # Determine consensus
    if bullish > bearish and bullish > neutral:
        consensus_dir = "BULLISH"
    elif bearish > bullish and bearish > neutral:
        consensus_dir = "BEARISH"
    else:
        consensus_dir = "NEUTRAL"
    
    result_data = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "consensus": {
            "direction": consensus_dir,
            "confidence": round(avg_confidence, 2)
        },
        "sentiment": round(sentiment, 2),
        "distribution": {
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral
        },
        "paul_count": len(results),
        "agents": sorted(results, key=lambda x: x['confidence'], reverse=True)[:5]
    }
    
    # Print results
    print(f"\n{'='*60}")
    print(f"📊 CONSENSUS: {consensus_dir}")
    print(f"   Confidence: {avg_confidence:.0%}")
    print(f"   Sentiment: {sentiment:+.2f}")
    print(f"   Distribution: {bullish}↑ {bearish}↓ {neutral}→")
    print('='*60)
    print("\n🥇 Top Pauls:")
    for agent in result_data['agents'][:5]:
        emoji = "🟢" if agent['direction'] == 'BULLISH' else "🔴" if agent['direction'] == 'BEARISH' else "⚪"
        print(f"   {emoji} {agent['name']}: {agent['confidence']:.0%} - {agent['reasoning'][:60]}...")
    
    # Save result
    with open('overnight_results.jsonl', 'a') as f:
        f.write(json.dumps(result_data) + '\n')
    
    return result_data


def main():
    parser = argparse.ArgumentParser(description="Ask Swimming Pauls via Ollama")
    parser.add_argument("--question", required=True, help="The question to ask")
    parser.add_argument("--pauls", type=int, default=8, help="Number of Pauls (max 8)")
    
    args = parser.parse_args()
    
    if args.pauls > 8:
        print("⚠️  Max 8 Pauls with Ollama for reasonable speed")
        args.pauls = 8
    
    result = asyncio.run(ask_pauls(args.question, args.pauls))
    
    print(f"\n💾 Saved to overnight_results.jsonl")


if __name__ == "__main__":
    main()
