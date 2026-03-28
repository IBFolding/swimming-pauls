#!/usr/bin/env python3
"""Spawn 10,000 Pauls focused on learning to trade."""
import asyncio
import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from persona_factory import PaulPersonaFactory, TradingStyle, RiskProfile, SpecialtyDomain
from paul_world import PaulWorld

async def main():
    print("🦷 SWIMMING PAULS - MASS DEPLOYMENT")
    print("=" * 50)
    
    # Create factory
    factory = PaulPersonaFactory()
    
    # Generate 10,000 Pauls with trading focus
    print("\n🎯 Generating 10,000 trading-focused Pauls...")
    
    # Create diverse pool with heavy trading focus
    all_personas = []
    
    # Batch 1-5: Core traders (5000 Pauls)
    for batch in range(1, 6):
        print(f"   Batch {batch}/10: Creating traders...")
        batch_personas = factory.create_diverse_pool(total_count=1000)
        for p in batch_personas:
            p.generation_batch = batch
            # Ensure all have trading specialties
            if SpecialtyDomain.EQUITIES not in p.specialties:
                p.specialties.append(SpecialtyDomain.EQUITIES)
        all_personas.extend(batch_personas)
    
    # Batch 6-8: Crypto specialists (3000 Pauls)
    for batch in range(6, 9):
        print(f"   Batch {batch}/10: Creating crypto specialists...")
        for _ in range(1000):
            style = random.choice([TradingStyle.SCALPER, TradingStyle.MOMENTUM, TradingStyle.EVENT_DRIVEN])
            risk = random.choice([RiskProfile.AGGRESSIVE, RiskProfile.ULTRA_AGGRESSIVE, RiskProfile.DEGEN])
            specialties = [SpecialtyDomain.DEFI, SpecialtyDomain.LAYER1, SpecialtyDomain.MEMECOINS]
            p = factory.create_persona(trading_style=style, risk_profile=risk, specialties=specialties)
            p.generation_batch = batch
            all_personas.append(p)
    
    # Batch 9-10: Quant/Algorithmic (2000 Pauls)
    for batch in range(9, 11):
        print(f"   Batch {batch}/10: Creating quants...")
        for _ in range(1000):
            style = random.choice([TradingStyle.ALGORITHMIC, TradingStyle.QUANTITATIVE])
            risk = random.choice([RiskProfile.MODERATE, RiskProfile.CONSERVATIVE])
            specialties = [SpecialtyDomain.DERIVATIVES, SpecialtyDomain.ARBITRAGE, SpecialtyDomain.ONCHAIN]
            p = factory.create_persona(trading_style=style, risk_profile=risk, specialties=specialties)
            p.generation_batch = batch
            p.pattern_recognition += 0.2  # Boost for quants
            p.technical_analysis += 0.2
            all_personas.append(p)
    
    print(f"\n✅ Generated {len(all_personas):,} Pauls")
    print(f"   Trading styles: {len(set(p.trading_style for p in all_personas))}")
    print(f"   Risk profiles: {len(set(p.risk_profile for p in all_personas))}")
    
    # Initialize Paul's World
    print("\n🌍 Initializing Paul's World...")
    world = PaulWorld()
    await world.initialize()
    
    # Add all personas to world
    print("   Adding Pauls to world...")
    for persona in all_personas:
        # Create Paul instance (simplified for mass deployment)
        from paul_world import PaulState, Location
        specialty = persona.specialties[0].value if persona.specialties else "general"
        paul = PaulState(
            name=persona.name,
            emoji="🦷",
            specialty=specialty,
            trading_style=persona.trading_style.value,
            risk_profile=persona.risk_profile.name.lower(),
            location=random.choice(list(Location)),
            risk_tolerance=persona.risk_profile.value,
            curiosity=persona.adaptability,
        )
        world.pauls[persona.name] = paul
    
    print(f"   Total Pauls in world: {len(world.pauls):,}")
    
    # Enable paper trading for all
    if hasattr(world, 'paper_trading') and world.paper_trading:
        print("\n📊 Enabling paper trading for all Pauls...")
        for paul_name in world.pauls.keys():
            world.paper_trading.create_portfolio(paul_name)
            world.paper_trading.portfolios[paul_name].enabled = True
        print(f"   ✅ Paper trading enabled for {len(world.pauls):,} Pauls")
    
    # Save world state
    await world._save_world()
    print("\n💾 World state saved")
    
    print("\n" + "=" * 50)
    print("🚀 READY TO RUN")
    print("   Start simulation: python3 paul_world.py run")
    print("   Check status: python3 paul_world.py status")
    print("   Trading leaderboard: python3 paul_world.py paper leaderboard")
    print("=" * 50)

if __name__ == "__main__":
    import random
    random.seed(42)  # Reproducible
    asyncio.run(main())
