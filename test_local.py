#!/usr/bin/env python3
"""
Test script to verify Swimming Pauls works 100% locally.
Run this to confirm no API keys or internet are required.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for proper package import
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_local_news():
    """Test local news connector works without API keys."""
    print("\n📰 Testing Local News Connector...")
    
    from swimming_pauls.local_data_feeds import LocalNewsConnector
    
    async def run():
        connector = LocalNewsConnector()
        articles = await connector.fetch(query="crypto", limit=5)
        
        assert len(articles) > 0, "Should return articles"
        assert all(hasattr(a, 'title') for a in articles), "Articles should have titles"
        
        print(f"  ✓ Fetched {len(articles)} articles locally")
        print(f"  ✓ Sample: {articles[0].title[:50]}...")
        
        await connector.close()
    
    asyncio.run(run())


def test_local_market():
    """Test local market connector works without API keys."""
    print("\n📈 Testing Local Market Connector...")
    
    from swimming_pauls.local_data_feeds import LocalMarketConnector
    
    async def run():
        connector = LocalMarketConnector()
        prices = await connector.fetch(symbols=["BTC", "ETH", "SOL"])
        
        assert len(prices) == 3, "Should return 3 prices"
        assert all(hasattr(p, 'price') for p in prices), "Prices should have values"
        assert all(p.price > 0 for p in prices), "Prices should be positive"
        
        print(f"  ✓ Fetched {len(prices)} prices locally")
        for p in prices:
            print(f"    {p.symbol}: ${p.price:,.2f}")
    
    asyncio.run(run())


def test_local_sentiment():
    """Test local sentiment connector works without API keys."""
    print("\n💭 Testing Local Sentiment Connector...")
    
    from swimming_pauls.local_data_feeds import LocalSentimentConnector
    
    async def run():
        connector = LocalSentimentConnector()
        scores = await connector.fetch(topic="bitcoin")
        
        assert len(scores) > 0, "Should return sentiment scores"
        assert all(hasattr(s, 'score') for s in scores), "Scores should have values"
        
        print(f"  ✓ Analyzed {len(scores)} sentiment sources locally")
        for s in scores:
            print(f"    {s.platform}: {s.score:+.3f} (volume: {s.volume})")
    
    asyncio.run(run())


def test_file_watcher():
    """Test file watcher works locally."""
    print("\n📁 Testing File Watcher...")
    
    from swimming_pauls.local_data_feeds import FileWatcherConnector
    
    async def run():
        # Create test directory
        test_dir = Path("./test_watch_dir")
        test_dir.mkdir(exist_ok=True)
        
        connector = FileWatcherConnector(watch_paths=[test_dir])
        changes = await connector.fetch(check_changes=True)
        
        print(f"  ✓ Watching {len(connector.watch_paths)} directories")
        print(f"  ✓ Found {len(changes)} files/changes")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)
    
    asyncio.run(run())


def test_persona_factory():
    """Test persona generation works locally."""
    print("\n👥 Testing Persona Factory...")
    
    from swimming_pauls.persona_factory import PaulPersonaFactory
    
    factory = PaulPersonaFactory(seed=42)
    personas = factory.create_diverse_pool(total_count=40)
    
    assert len(personas) == 40, "Should generate 40 personas"
    
    print(f"  ✓ Generated {len(personas)} unique Paul personas")
    print(f"  ✓ Sample: {personas[0].name} ({personas[0].trading_style.value})")


def test_knowledge_graph():
    """Test knowledge graph works locally."""
    print("\n🕸️  Testing Knowledge Graph...")
    
    from swimming_pauls.knowledge_graph import KnowledgeGraph, Entity, Relationship
    
    graph = KnowledgeGraph(name="test")
    
    # Add entities
    eth = Entity(id="eth", name="Ethereum", entity_type="TECHNOLOGY")
    vitalik = Entity(id="vitalik", name="Vitalik Buterin", entity_type="PERSON")
    
    graph.add_entity(eth)
    graph.add_entity(vitalik)
    
    # Add relationship
    rel = Relationship(id="rel1", source_id="vitalik", target_id="eth", relation_type="founded")
    graph.add_relationship(rel)
    
    assert len(graph.entities) == 2, "Should have 2 entities"
    assert len(graph.relationships) == 1, "Should have 1 relationship"
    
    print(f"  ✓ Created graph with {len(graph.entities)} entities, {len(graph.relationships)} relationships")


def test_graph_memory():
    """Test graph memory works locally with SQLite."""
    print("\n🧠 Testing Graph Memory...")
    
    from swimming_pauls.graph_memory import GraphMemory
    from swimming_pauls.knowledge_graph import Entity
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_memory.db"
        
        memory = GraphMemory(db_path=str(db_path))
        
        # Add entity
        entity = Entity(id="btc", name="Bitcoin", entity_type="ASSET")
        memory.add_entity(entity)
        
        # Teach agent
        memory.teach_agent("agent_001", "btc", belief_strength=0.9)
        
        # Query
        knowledge = memory.get_agent_knowledge("agent_001")
        
        assert len(knowledge) > 0, "Agent should know about entity"
        
        print(f"  ✓ SQLite memory working with {len(knowledge)} knowledge entries")
        
        memory.close()


def test_mirofish_integration():
    """Test full MiroFish integration works locally."""
    print("\n🐟 Testing MiroFish Integration...")
    
    from swimming_pauls.mirofish_integration import MiroFishSwimmingPauls, MiroFishConfig
    
    config = MiroFishConfig(
        paul_count=5,  # Small pool for testing
        enable_graph_memory=True,
        enable_zep_memory=False,  # Explicitly disable cloud
    )
    
    mirofish = MiroFishSwimmingPauls(config)
    mirofish.initialize()
    mirofish.spawn_paul_pool()
    
    assert len(mirofish.agents) == 5, "Should spawn 5 agents"
    
    # Run prediction
    result = mirofish.run_prediction_round({
        'asset': 'BTC',
        'price_trend': 0.1,
        'sentiment': 0.5,
    })
    
    assert 'consensus' in result, "Should have consensus"
    assert result['participation_rate'] > 0, "Should have participation"
    
    print(f"  ✓ Spawned {len(mirofish.agents)} agents")
    print(f"  ✓ Consensus: {result['consensus']['dominant'].upper()}")
    print(f"  ✓ Participation: {result['participation_rate']:.0%}")
    
    mirofish.cleanup()


def main():
    """Run all local tests."""
    print("=" * 60)
    print("Swimming Pauls - 100% Local Verification Test")
    print("=" * 60)
    print("\nTesting that all functionality works WITHOUT:")
    print("  - API keys")
    print("  - Cloud services")
    print("  - Internet connection")
    print()
    
    try:
        test_local_news()
        test_local_market()
        test_local_sentiment()
        test_file_watcher()
        test_persona_factory()
        test_knowledge_graph()
        test_graph_memory()
        test_mirofish_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nSwimming Pauls is 100% local-capable.")
        print("No API keys or internet required for full functionality.")
        return 0
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
