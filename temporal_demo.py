"""
Temporal Memory Demo for Swimming Pauls

Demonstrates the temporal memory system with:
- Belief formation and evolution
- Evidence-based reinforcement
- Time-based decay
- Temporal context in predictions

Run with: python3 temporal_demo.py
"""

import asyncio
from datetime import datetime, timedelta
from temporal_memory import (
    TemporalMemory,
    TemporalMemoryManager,
    simulate_belief_evolution,
    create_temporal_prediction_reasoning,
)


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def demo_basic_belief_formation():
    """Demo: Creating and tracking beliefs."""
    print_header("1. BASIC BELIEF FORMATION")
    
    memory = TemporalMemory(paul_name="TraderPaul", db_path=None)
    
    # Form initial beliefs
    belief1 = memory.form_belief(
        topic="BTC",
        proposition="Bitcoin is bullish",
        initial_confidence=0.6,
        source_reliability=0.8
    )
    print(f"✓ Formed belief: {belief1.proposition} (confidence: {belief1.confidence:.0%})")
    
    belief2 = memory.form_belief(
        topic="ETH",
        proposition="Ethereum is neutral",
        initial_confidence=0.5,
        source_reliability=0.7
    )
    print(f"✓ Formed belief: {belief2.proposition} (confidence: {belief2.confidence:.0%})")
    
    # Show active beliefs
    active = memory.get_all_active_beliefs()
    print(f"\n📊 Active beliefs: {len(active)}")
    for b in active:
        print(f"   • {b.topic}: {b.proposition} ({b.confidence:.0%})")


def demo_evidence_reinforcement():
    """Demo: How evidence reinforces beliefs."""
    print_header("2. EVIDENCE REINFORCEMENT")
    
    memory = TemporalMemory(paul_name="AnalystPaul", db_path=None)
    
    # Form initial belief
    belief = memory.form_belief(
        topic="AI",
        proposition="AI stocks will outperform",
        initial_confidence=0.5
    )
    print(f"Initial belief: {belief.proposition}")
    print(f"   Confidence: {belief.confidence:.0%}")
    
    # Add supporting evidence
    print("\n📈 Adding supporting evidence...")
    
    evidence_items = [
        ("NVIDIA reports record earnings", 0.8, 0.9),
        ("New LLM breakthrough announced", 0.7, 0.8),
        ("AI adoption accelerates in enterprises", 0.6, 0.85),
    ]
    
    for content, impact, reliability in evidence_items:
        old_conf = memory.get_belief("AI").confidence
        memory.add_evidence("AI", content, impact, reliability=reliability)
        new_conf = memory.get_belief("AI").confidence
        print(f"   + '{content[:40]}...' → confidence {old_conf:.0%} → {new_conf:.0%}")
    
    final_belief = memory.get_belief("AI")
    print(f"\n✓ Final confidence: {final_belief.confidence:.0%} (+{final_belief.confidence - 0.5:.0%})")
    print(f"✓ Evidence count: {final_belief.evidence_count}")


def demo_contradiction_and_revision():
    """Demo: How contradictions challenge beliefs."""
    print_header("3. CONTRADICTION & BELIEF REVISION")
    
    memory = TemporalMemory(paul_name="SkepticPaul", db_path=None)
    
    # Form initial bullish belief
    belief = memory.form_belief(
        topic="TechSector",
        proposition="Tech sector will grow",
        initial_confidence=0.7
    )
    print(f"Initial belief: {belief.proposition} ({belief.confidence:.0%})")
    
    # Positive evidence
    memory.add_evidence("TechSector", "Strong earnings season", 0.6, reliability=0.8)
    print(f"After positive news: {memory.get_belief('TechSector').confidence:.0%}")
    
    # Contradicting evidence arrives
    print("\n📉 Contradicting evidence arrives...")
    
    contradictions = [
        ("Interest rates hiked significantly", -0.7, 0.9),
        ("Tech layoffs announced", -0.6, 0.8),
        ("Regulatory scrutiny increases", -0.5, 0.75),
    ]
    
    for content, impact, reliability in contradictions:
        old_conf = memory.get_belief("TechSector", include_challenged=True).confidence
        memory.add_evidence("TechSector", content, impact, reliability=reliability)
        new_belief = memory.get_belief("TechSector", include_challenged=True)
        print(f"   - '{content[:35]}...' → confidence {old_conf:.0%} → {new_belief.confidence:.0%}")
        
        if new_belief.status.value == "abandoned":
            print(f"   ⚠️  Belief abandoned!")
            break
    
    final = memory.get_belief("TechSector", include_challenged=True)
    print(f"\n✓ Final status: {final.status.value}")
    print(f"✓ Contradictions faced: {final.contradiction_count}")


def demo_temporal_decay():
    """Demo: Belief decay over time."""
    print_header("4. BELIEF DECAY OVER TIME")
    
    memory = TemporalMemory(
        paul_name="LongTermPaul",
        decay_rate=0.05,  # 5% per day
        db_path=None
    )
    
    # Start at a specific time
    start_time = datetime(2024, 1, 1, 12, 0)
    
    # Form belief
    belief = memory.form_belief(
        topic="Market",
        proposition="Market conditions are favorable",
        initial_confidence=0.8,
        timestamp=start_time
    )
    
    print(f"Initial belief ({start_time.strftime('%Y-%m-%d')}):")
    print(f"   Confidence: {belief.confidence:.0%}")
    
    # Simulate time passing
    print("\n⏰ Simulating time passing...")
    
    time_points = [
        ("1 day later", timedelta(days=1)),
        ("3 days later", timedelta(days=3)),
        ("1 week later", timedelta(days=7)),
        ("2 weeks later", timedelta(days=14)),
    ]
    
    for label, delta in time_points:
        current_time = start_time + delta
        decayed = memory.decay_beliefs(current_time)
        belief = memory.get_belief("Market", include_challenged=True)
        
        if belief.status.value == "abandoned":
            print(f"   {label}: Belief abandoned (confidence fell below threshold)")
            break
        else:
            print(f"   {label}: Confidence = {belief.confidence:.0%}")


def demo_temporal_context():
    """Demo: Temporal context in predictions."""
    print_header("5. TEMPORAL CONTEXT IN PREDICTIONS")
    
    memory = TemporalMemory(paul_name="ContextPaul", db_path=None)
    
    start_time = datetime(2024, 1, 1, 12, 0)
    
    # Form initial belief
    memory.form_belief(
        topic="Crypto",
        proposition="Crypto market is risky",
        initial_confidence=0.5,
        timestamp=start_time
    )
    
    # Get temporal context
    context = memory.get_temporal_context("Crypto", current_time=start_time)
    reasoning = context.format_temporal_reasoning()
    
    print("Initial prediction:")
    print(f"   📝 {reasoning}")
    
    # Time passes, evidence accumulates
    print("\n📊 3 days pass, new evidence emerges...")
    
    day3 = start_time + timedelta(days=3)
    memory.add_evidence("Crypto", "ETF approvals announced", 0.8, reliability=0.9, timestamp=day3)
    memory.add_evidence("Crypto", "Institutional adoption grows", 0.7, reliability=0.85, timestamp=day3)
    
    context = memory.get_temporal_context("Crypto", current_time=day3)
    reasoning = context.format_temporal_reasoning()
    
    print("Updated prediction:")
    print(f"   📝 {reasoning}")
    print(f"\n   Belief shift: {context.belief_shift:+.0%}")
    print(f"   Evolution: {context.evolution_summary}")


def demo_social_influence():
    """Demo: Pauls influencing each other."""
    print_header("6. SOCIAL INFLUENCE BETWEEN PAULS")
    
    manager = TemporalMemoryManager(db_path=None)
    
    # Paul1 is confident about BTC
    paul1 = manager.get_memory("VisionaryPaul")
    paul1.form_belief("BTC", "Bitcoin will reach $100k", 0.85)
    
    # Paul2 is uncertain
    paul2 = manager.get_memory("SkepticPaul")
    paul2.form_belief("BTC", "Bitcoin will stay flat", 0.4)
    
    print("Before influence:")
    print(f"   VisionaryPaul: {paul1.get_belief('BTC').proposition} ({paul1.get_belief('BTC').confidence:.0%})")
    print(f"   SkepticPaul: {paul2.get_belief('BTC').proposition} ({paul2.get_belief('BTC').confidence:.0%})")
    
    # Paul1 influences Paul2
    print("\n🤝 VisionaryPaul shares view with SkepticPaul...")
    manager.spread_influence("VisionaryPaul", "SkepticPaul", "BTC", influence_strength=0.4)
    
    print("\nAfter influence:")
    paul2_belief = paul2.get_belief("BTC", include_challenged=True)
    print(f"   SkepticPaul: {paul2_belief.proposition} ({paul2_belief.confidence:.0%})")
    print(f"   Status: {paul2_belief.status.value}")
    print(f"   Contradictions: {paul2_belief.contradiction_count}")
    
    # Check consensus
    consensus = manager.get_cross_paul_consensus("BTC")
    print(f"\n📊 Consensus on BTC: {consensus['consensus']} ({consensus['consensus_strength']:.0%} agreement)")


def demo_belief_simulation():
    """Demo: Simulating belief evolution."""
    print_header("7. BELIEF EVOLUTION SIMULATION")
    
    print("Simulating belief evolution for 'DeFi' topic:\n")
    
    evidence_sequence = [
        (0.6, "New DeFi protocol launches successfully"),
        (0.4, "TVL increases across major platforms"),
        (-0.3, "Smart contract vulnerability discovered"),
        (0.5, "Security audit passes with high marks"),
        (0.7, "Major institution enters DeFi space"),
        (-0.4, "Regulatory uncertainty emerges"),
        (0.3, "Clear regulatory framework proposed"),
    ]
    
    history = simulate_belief_evolution(
        topic="DeFi",
        initial_proposition="DeFi has potential",
        evidence_sequence=evidence_sequence,
        decay_rate=0.02,
        reinforcement_rate=0.15
    )
    
    print("Evolution timeline:")
    for step in history:
        if step['event'] == 'initial_belief':
            print(f"   Start: Confidence = {step['confidence']:.0%}")
        else:
            impact = step.get('impact', 0)
            impact_emoji = "📈" if impact > 0 else "📉" if impact < 0 else "➡️"
            print(f"   {impact_emoji} {step['event'][:40]}...")
            print(f"      → Confidence = {step['confidence']:.0%}")


def demo_statistics():
    """Demo: Memory statistics."""
    print_header("8. MEMORY STATISTICS")
    
    manager = TemporalMemoryManager(db_path=None)
    
    # Create beliefs for multiple Pauls
    for paul_name in ["Paul1", "Paul2", "Paul3"]:
        memory = manager.get_memory(paul_name)
        memory.form_belief("BTC", f"{paul_name} thinks BTC is bullish", 0.6)
        memory.form_belief("ETH", f"{paul_name} thinks ETH is neutral", 0.5)
        
        # Add some evidence
        if paul_name == "Paul1":
            memory.add_evidence("BTC", "Strong institutional buying", 0.8)
            memory.add_evidence("BTC", "ETF inflows", 0.7)
    
    # Get all statistics
    all_stats = manager.get_all_statistics()
    
    print("Paul statistics:")
    for paul_name, stats in all_stats.items():
        print(f"\n   {paul_name}:")
        print(f"      Active beliefs: {stats['active_beliefs']}")
        print(f"      Topics covered: {stats['topics_count']}")
        print(f"      Evidence gathered: {stats['evidence_count']}")
        print(f"      Avg confidence: {stats['average_confidence']:.0%}")


async def main():
    """Run all demos."""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🧠 TEMPORAL MEMORY SYSTEM DEMO                                 ║
║                                                                  ║
║   Demonstrating dynamic belief evolution over time              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    demo_basic_belief_formation()
    demo_evidence_reinforcement()
    demo_contradiction_and_revision()
    demo_temporal_decay()
    demo_temporal_context()
    demo_social_influence()
    demo_belief_simulation()
    demo_statistics()
    
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ✅ DEMO COMPLETE                                               ║
║                                                                  ║
║   Key Features Demonstrated:                                     ║
║   • Beliefs form with confidence levels                          ║
║   • Evidence reinforces or challenges beliefs                    ║
║   • Beliefs decay over time without reinforcement                ║
║   • Temporal context enables "3 days ago I thought..."           ║
║   • Pauls can influence each other's beliefs                     ║
║   • Belief evolution can be simulated                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    asyncio.run(main())
