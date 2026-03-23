#!/usr/bin/env python3
"""
Swimming Pauls - Demo Data Generator
Create sample predictions for new users to explore

Usage:
    python generate_demo_data.py              # Generate demo predictions
    python generate_demo_data.py --count 10   # Generate 10 predictions
    python generate_demo_data.py --clean      # Remove demo data
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta

DEMO_QUESTIONS = [
    "Will Bitcoin reach $100,000 by end of 2025?",
    "Should I buy ETH or SOL right now?",
    "Is the AI bubble going to burst in 2025?",
    "Will the Fed cut rates in the next meeting?",
    "Should I invest in meme coins or stick to BTC?",
    "Will Tesla stock recover to $300?",
    "Is this a good time to buy the dip?",
    "Will crypto regulations get stricter in 2025?",
    "Should I hold or sell my altcoins?",
    "Will ETH flip BTC in market cap?"
]

PAUL_NAMES = [
    ("Visionary Paul", "Long-term", "🔮"),
    ("Trader Paul", "Timing", "📈"),
    ("Skeptic Paul", "Risk", "🤨"),
    ("Whale Paul", "Institutional", "🐋"),
    ("Quant Paul", "Data", "📊"),
    ("Contrarian Paul", "Contrarian", "🐻"),
    ("Professor Paul", "Macro", "👨‍🏫"),
    ("Degen Paul", "High Risk", "🎰"),
    ("News Paul", "Sentiment", "📰"),
    ("Tech Paul", "Innovation", "💻")
]

def generate_demo_prediction(index):
    """Generate a single demo prediction."""
    question = DEMO_QUESTIONS[index % len(DEMO_QUESTIONS)]
    
    # Random consensus
    direction = random.choice(["BULLISH", "BEARISH", "NEUTRAL"])
    confidence = random.uniform(0.4, 0.95)
    sentiment = random.uniform(-0.8, 0.8)
    
    # Generate Pauls
    num_pauls = random.randint(5, 10)
    agents = []
    
    for i in range(num_pauls):
        name, specialty, emoji = random.choice(PAUL_NAMES)
        
        # Reasoning based on direction
        if direction == "BULLISH":
            reasons = [
                "Technical indicators pointing up. Volume increasing.",
                "Fundamentals remain strong. Adoption accelerating.",
                "Smart money accumulating. On-chain metrics bullish.",
                "Momentum building. Breakout imminent.",
                "Institutional interest growing. ETF flows positive."
            ]
        elif direction == "BEARISH":
            reasons = [
                "Resistance levels holding. Distribution pattern.",
                "Macro headwinds remain. Risk-off sentiment.",
                "Overbought conditions. Correction overdue.",
                "Selling pressure increasing. Support breaking.",
                "Regulatory uncertainty. Profit taking likely."
            ]
        else:
            reasons = [
                "Mixed signals. Waiting for clarity.",
                "Consolidation phase. Range-bound likely.",
                "Bullish and bearish cases balanced.",
                "Low conviction either direction. Sideways.",
                "Patience required. No clear edge."
            ]
        
        agents.append({
            "name": name,
            "specialty": specialty,
            "emoji": emoji,
            "reasoning": random.choice(reasons),
            "direction": random.choice(["BULLISH", "BEARISH", "NEUTRAL"]),
            "confidence": random.uniform(0.3, 0.9)
        })
    
    # Vote counts
    if direction == "BULLISH":
        bullish = random.randint(6, 8)
        bearish = random.randint(1, 3)
        neutral = 10 - bullish - bearish
    elif direction == "BEARISH":
        bullish = random.randint(1, 3)
        bearish = random.randint(6, 8)
        neutral = 10 - bullish - bearish
    else:
        bullish = random.randint(3, 4)
        bearish = random.randint(3, 4)
        neutral = 10 - bullish - bearish
    
    # Create prediction data
    prediction = {
        "question": question,
        "consensus": {
            "direction": direction,
            "confidence": round(confidence, 2),
            "vote_breakdown": {
                "BULLISH": bullish,
                "BEARISH": bearish,
                "NEUTRAL": neutral
            }
        },
        "sentiment": round(sentiment, 3),
        "pauls_count": num_pauls,
        "rounds": random.randint(5, 20),
        "agents": agents,
        "saved_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
        "demo": True
    }
    
    return prediction

def generate_demo_data(count=5):
    """Generate demo predictions."""
    results_dir = Path(__file__).parent / 'data' / 'results'
    results_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎲 Generating {count} demo predictions...")
    
    generated = []
    for i in range(count):
        prediction = generate_demo_prediction(i)
        
        # Generate ID
        import hashlib
        pred_id = hashlib.md5(f"demo_{i}_{datetime.now()}".encode()).hexdigest()[:8]
        
        # Save
        output_file = results_dir / f"{pred_id}.json"
        with open(output_file, 'w') as f:
            json.dump(prediction, f, indent=2)
        
        generated.append({
            'id': pred_id,
            'question': prediction['question'][:50],
            'consensus': prediction['consensus']['direction']
        })
    
    print(f"✅ Generated {count} demo predictions")
    print("\n📊 Demo Predictions:")
    for g in generated:
        print(f"   {g['id']}: {g['question']}... ({g['consensus']})")
    
    print(f"\n🔗 View them at:")
    print(f"   http://localhost:3005/explorer.html?id={generated[0]['id']}")

def clean_demo_data():
    """Remove demo predictions."""
    results_dir = Path(__file__).parent / 'data' / 'results'
    
    if not results_dir.exists():
        print("ℹ️  No data directory")
        return
    
    removed = 0
    for f in results_dir.glob("*.json"):
        try:
            with open(f) as file:
                data = json.load(file)
                if data.get('demo'):
                    f.unlink()
                    removed += 1
        except:
            pass
    
    print(f"🗑️  Removed {removed} demo predictions")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate demo data")
    parser.add_argument("--count", type=int, default=5, help="Number of predictions")
    parser.add_argument("--clean", action="store_true", help="Remove demo data")
    
    args = parser.parse_args()
    
    if args.clean:
        clean_demo_data()
    else:
        generate_demo_data(args.count)
        print("\n💡 Start the UI to explore: python start.py")

if __name__ == "__main__":
    main()
