#!/usr/bin/env python3
"""
Live batch prediction test with Swimming Pauls using Kimi API
"""

import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from skill_bridge import BatchPredictionEngine
from persona_factory import generate_swimming_pauls_pool

# Generate 10 Paul personas
print("=" * 60)
print("GENERATING 10 SWIMMING PAUL PERSONAS")
print("=" * 60)

pauls = generate_swimming_pauls_pool(count=10, seed=42)

print(f"\nCreated {len(pauls)} Paul personas:")
for paul in pauls:
    print(f"  - {paul['name']} ({paul['trading_style']}, Risk: {paul['risk_profile']})")

# Create the batch prediction engine
print("\n" + "=" * 60)
print("INITIALIZING BATCH PREDICTION ENGINE")
print("=" * 60)

engine = BatchPredictionEngine()

# Run batch prediction
question = "Will Bitcoin reach $100,000 by end of 2025?"

print(f"\nQuestion: {question}")
print("\nRunning batch prediction...")
print("-" * 60)

predictions = engine.batch_predict(question, pauls)

# Print individual predictions
print("\n" + "=" * 60)
print("INDIVIDUAL PAUL PREDICTIONS")
print("=" * 60)

for pred in predictions:
    print(f"\n🎯 {pred.paul_name}")
    print(f"   Sentiment: {pred.sentiment.upper()}")
    print(f"   Confidence: {pred.confidence:.0%}")
    print(f"   Reasoning: {pred.reasoning}")
    if pred.specialty:
        print(f"   Specialty: {pred.specialty}")
    if pred.trading_style:
        print(f"   Trading Style: {pred.trading_style}")

# Calculate consensus
print("\n" + "=" * 60)
print("CONSENSUS SUMMARY")
print("=" * 60)

bullish_count = sum(1 for p in predictions if p.sentiment == "bullish")
bearish_count = sum(1 for p in predictions if p.sentiment == "bearish")
neutral_count = sum(1 for p in predictions if p.sentiment == "neutral")

avg_confidence = sum(p.confidence for p in predictions) / len(predictions)

print(f"\n📊 Total Pauls: {len(predictions)}")
print(f"🟢 Bullish: {bullish_count} ({bullish_count/len(predictions):.0%})")
print(f"🔴 Bearish: {bearish_count} ({bearish_count/len(predictions):.0%})")
print(f"⚪ Neutral: {neutral_count} ({neutral_count/len(predictions):.0%})")
print(f"\n📈 Average Confidence: {avg_confidence:.0%}")

# Determine overall consensus
if bullish_count > bearish_count and bullish_count > neutral_count:
    consensus = "BULLISH"
    consensus_emoji = "🟢"
elif bearish_count > bullish_count and bearish_count > neutral_count:
    consensus = "BEARISH"
    consensus_emoji = "🔴"
else:
    consensus = "NEUTRAL/UNCERTAIN"
    consensus_emoji = "⚪"

print(f"\n{consensus_emoji} OVERALL CONSENSUS: {consensus}")

# Check if we used real API or mock
print("\n" + "=" * 60)
print("API STATUS")
print("=" * 60)

# The _generate_mock_response would have printed if it was used
print("\n✅ Batch prediction completed!")
print("   (Check output above - if you see varied reasoning per Paul, likely real API)")
