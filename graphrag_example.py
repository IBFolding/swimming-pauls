"""
GraphRAG Example - Demonstration of GraphRAG System for Swimming Pauls

This script demonstrates:
1. Ingesting documents (PDF, TXT, MD)
2. Building a knowledge graph from extracted entities and relationships
3. Semantic search across documents
4. Query interface: "What do we know about X?"
5. Integration with Paul's World knowledge system

Run: python graphrag_example.py
"""

import asyncio
import tempfile
import shutil
from pathlib import Path

# Import GraphRAG
from graphrag import GraphRAG, PaulWorldGraphRAG


async def demo_basic_usage():
    """Demonstrate basic GraphRAG usage."""
    print("=" * 60)
    print("🧠 GraphRAG Demo - Basic Usage")
    print("=" * 60)
    
    # Create temporary storage
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize GraphRAG (without LLM for demo speed)
        graphrag = GraphRAG(storage_path=temp_dir, use_llm=False)
        print(f"\n✅ GraphRAG initialized at {temp_dir}")
        
        # Sample text about crypto/blockchain
        sample_text = """
        Ethereum was founded by Vitalik Buterin in 2015. It is a decentralized 
        blockchain platform that enables smart contracts and decentralized applications.
        
        Solana was founded by Anatoly Yakovenko in 2020. Solana is a high-performance 
        blockchain that competes with Ethereum. Many developers have migrated from 
        Ethereum to Solana due to lower transaction fees and faster processing.
        
        Andreessen Horowitz (a16z) is a venture capital firm that invested in both 
        Ethereum and Solana. They have offices in Menlo Park, California and are 
        one of the largest crypto investors.
        
        Bitcoin was created by Satoshi Nakamoto in 2009. It is the first cryptocurrency 
        and uses proof-of-work consensus. Bitcoin's main competitor is Ethereum, though
        they serve different use cases.
        
        Coinbase partnered with Ethereum Foundation to promote Web3 development.
        Binance is a cryptocurrency exchange that competes with Coinbase.
        """
        
        # Ingest the text
        print("\n📄 Ingesting sample text...")
        result = await graphrag.ingest_text(sample_text, source="demo")
        print(f"✅ Ingested: {result['chunks']} chunks, {result['entities']} entities")
        
        # Show stats
        stats = graphrag.get_stats()
        print(f"\n📊 Graph Statistics:")
        print(f"   Entities: {stats['total_entities']}")
        print(f"   Relationships: {stats['total_relationships']}")
        print(f"   Entity types: {list(stats['entity_types'].keys())}")
        
        # Query examples
        print("\n" + "=" * 60)
        print("🔍 Query Examples")
        print("=" * 60)
        
        # Query 1: What do we know about Ethereum?
        print("\n❓ Query: What do we know about Ethereum?")
        result = graphrag.query("Ethereum")
        print(f"📋 {result['summary']}")
        print("\n📌 Key Entities:")
        for e in result['entities'][:3]:
            print(f"   • {e['name']} ({e['type']}) - confidence: {e['confidence']:.2f}")
        
        if result['relationships']:
            print("\n🔗 Key Relationships:")
            for r in result['relationships'][:3]:
                print(f"   • {r['source']['name']} → {r['type']} → {r['target']['name']}")
        
        # Query 2: Founders
        print("\n❓ Query: Who founded what?")
        result = graphrag.query("founders")
        print(f"📋 {result['summary']}")
        for e in result['entities'][:3]:
            print(f"   • {e['name']}")
        
        # Query 3: Competition
        print("\n❓ Query: What companies compete?")
        result = graphrag.query("competition")
        print(f"📋 {result['summary']}")
        for r in result['relationships'][:3]:
            if 'compet' in r['type'] or 'vs' in r['type']:
                print(f"   • {r['source']['name']} competes with {r['target']['name']}")
        
        # Get neighbors
        print("\n" + "=" * 60)
        print("🕸️  Graph Traversal - Neighbors")
        print("=" * 60)
        
        # Find Ethereum entity
        ethereum_id = None
        for eid, entity in graphrag.entities.items():
            if 'ethereum' in entity.name.lower():
                ethereum_id = eid
                break
        
        if ethereum_id:
            print(f"\n📍 Neighbors of Ethereum:")
            neighbors = graphrag.get_neighbors(ethereum_id)
            for n in neighbors[:5]:
                direction = "→" if n['direction'] == 'outgoing' else "←"
                print(f"   {direction} {n['entity']['name']} ({n['relationship']['type']})")
        
        # Path finding
        print("\n" + "=" * 60)
        print("🛤️  Path Finding")
        print("=" * 60)
        
        # Find paths between entities
        entity_ids = list(graphrag.entities.keys())
        if len(entity_ids) >= 2:
            path = graphrag.find_path(entity_ids[0], entity_ids[-1])
            if path:
                source_name = graphrag.entities[entity_ids[0]].name
                target_name = graphrag.entities[entity_ids[-1]].name
                print(f"\n🔗 Path from {source_name} to {target_name}:")
                path_str = f"{source_name}"
                for rel in path:
                    path_str += f" → ({rel.relation_type}) → {graphrag.entities[rel.target_id].name}"
                print(f"   {path_str}")
        
        # Export
        print("\n" + "=" * 60)
        print("💾 Export")
        print("=" * 60)
        
        export_path = Path(temp_dir) / "export.json"
        graphrag.export_json(str(export_path))
        print(f"\n✅ Exported to {export_path}")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up temporary storage")


async def demo_paul_world_integration():
    """Demonstrate Paul's World integration."""
    print("\n" + "=" * 60)
    print("🌍 Paul's World Integration")
    print("=" * 60)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Initialize
        graphrag = GraphRAG(storage_path=temp_dir, use_llm=False)
        pw = PaulWorldGraphRAG(graphrag)
        
        # Add some knowledge
        await graphrag.ingest_text("""
        Artificial Intelligence (AI) is transforming finance. 
        Machine Learning models are used for trading predictions.
        DeepMind is a leading AI research company.
        """, source="ai_research")
        
        # Paul researching a topic
        print("\n🔬 Professor Paul researching 'AI in finance':")
        research = await pw.research_topic("AI in finance", paul_name="Professor Paul")
        
        print(f"   Topic: {research['topic']}")
        print(f"   Summary: {research['summary']}")
        print(f"   Key entities: {[e['name'] for e in research['key_entities']]}")
        print(f"   Insights:")
        for insight in research['insights'][:3]:
            print(f"      • {insight}")
        
        # Paul adding knowledge
        print("\n💡 Trader Paul sharing knowledge:")
        result = await pw.ingest_paul_knowledge(
            "Trader Paul",
            "Bitcoin price is influenced by institutional adoption.",
            topic="Bitcoin"
        )
        print(f"   Status: {result['status']}")
        
        # Get related predictions
        print("\n📈 Analyzing market question:")
        analysis = pw.get_related_predictions("Will AI transform trading?")
        print(f"   Related entities: {[e['name'] for e in analysis['related_entities'][:3]]}")
        
    finally:
        shutil.rmtree(temp_dir)


async def demo_file_ingestion():
    """Demonstrate file ingestion."""
    print("\n" + "=" * 60)
    print("📁 File Ingestion Demo")
    print("=" * 60)
    
    temp_dir = tempfile.mkdtemp()
    docs_dir = Path(temp_dir) / "documents"
    docs_dir.mkdir()
    
    try:
        # Create sample files
        (docs_dir / "blockchain_basics.txt").write_text("""
        Blockchain is a distributed ledger technology. 
        It was invented by Satoshi Nakamoto.
        Bitcoin was the first blockchain application.
        """)
        
        (docs_dir / "defi_overview.md").write_text("""
        # DeFi Overview
        
        Decentralized Finance (DeFi) uses smart contracts.
        Uniswap is a decentralized exchange.
        Aave provides lending services.
        """)
        
        (docs_dir / "crypto_news.json").write_text("""
        {
            "articles": [
                {"title": "Ethereum Upgrade", "content": "The merge was successful."},
                {"title": "Solana Outage", "content": "Network restarted after issues."}
            ]
        }
        """)
        
        # Ingest directory
        print(f"\n📂 Ingesting files from {docs_dir}")
        graphrag = GraphRAG(storage_path=temp_dir, use_llm=False)
        
        results = await graphrag.ingest_directory(docs_dir)
        
        for result in results:
            print(f"   ✓ {Path(result['file']).name}: {result.get('entities', 0)} entities")
        
        # Query the ingested knowledge
        print("\n🔍 Querying ingested knowledge:")
        result = graphrag.query("blockchain technology")
        print(f"   Found {len(result['entities'])} entities, {len(result['relationships'])} relationships")
        
    finally:
        shutil.rmtree(temp_dir)


async def main():
    """Run all demos."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  🧠 GraphRAG for Swimming Pauls - Interactive Demo".ljust(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    
    await demo_basic_usage()
    await demo_paul_world_integration()
    await demo_file_ingestion()
    
    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print("""
GraphRAG Features Demonstrated:
• Entity extraction from documents
• Relationship mapping between entities
• Semantic search across documents
• Graph traversal and path finding
• Paul's World integration for agent research
• Support for TXT, MD, and JSON files

Next Steps:
• Install PyPDF2 for PDF support: pip install PyPDF2
• Install sentence-transformers for semantic search: pip install sentence-transformers
• Install networkx for advanced graph algorithms: pip install networkx
• Enable LLM extraction by setting use_llm=True

Usage in Your Code:
    from graphrag import GraphRAG, PaulWorldGraphRAG
    
    graphrag = GraphRAG()
    await graphrag.ingest_file("document.pdf")
    results = graphrag.query("What do we know about X?")
    """)


if __name__ == "__main__":
    asyncio.run(main())
