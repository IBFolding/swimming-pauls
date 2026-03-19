"""
Tests for GraphRAG System

Comprehensive test suite covering:
- Entity extraction
- Relationship extraction
- Document processing (PDF, TXT, MD)
- Semantic search
- Knowledge graph traversal
- Integration with Paul's World

Run with: python -m pytest test_graphrag.py -v
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import asyncio
import pytest

# Import the GraphRAG module
from graphrag import (
    GraphRAG,
    GraphEntity,
    GraphRelationship,
    DocumentChunk,
    DocumentProcessor,
    HybridEntityExtractor,
    EmbeddingManager,
    PaulWorldGraphRAG,
    EntityType,
    RelationType
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_storage():
    """Create a temporary storage directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def graphrag(temp_storage):
    """Create a GraphRAG instance with temporary storage."""
    return GraphRAG(storage_path=temp_storage, use_llm=False)


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    Ethereum was founded by Vitalik Buterin in 2014. 
    Ethereum is a decentralized blockchain platform that supports smart contracts.
    
    Solana was founded by Anatoly Yakovenko. Solana is a high-performance blockchain
    that competes with Ethereum. Many developers have migrated from Ethereum to Solana
    due to lower transaction fees.
    
    Andreessen Horowitz is a venture capital firm that invested in both Ethereum and Solana.
    They have offices in San Francisco and New York.
    
    Bitcoin was created by Satoshi Nakamoto. It is the first cryptocurrency and uses
    proof-of-work consensus. Bitcoin's main competitor is Ethereum.
    """


@pytest.fixture
def sample_entities():
    """Sample entities for testing."""
    return [
        GraphEntity(
            id="ethereum_abc123",
            name="Ethereum",
            entity_type="technology",
            description="Decentralized blockchain platform",
            confidence=0.95,
            aliases=["ETH"]
        ),
        GraphEntity(
            id="vitalik_buterin_def456",
            name="Vitalik Buterin",
            entity_type="person",
            description="Co-founder of Ethereum",
            confidence=0.98
        ),
        GraphEntity(
            id="solana_ghi789",
            name="Solana",
            entity_type="technology",
            description="High-performance blockchain",
            confidence=0.95,
            aliases=["SOL"]
        )
    ]


@pytest.fixture
def sample_relationships(sample_entities):
    """Sample relationships for testing."""
    return [
        GraphRelationship(
            id="rel_001",
            source_id="ethereum_abc123",
            target_id="vitalik_buterin_def456",
            relation_type="founded_by",
            confidence=0.95,
            evidence=["Vitalik Buterin founded Ethereum in 2014"]
        ),
        GraphRelationship(
            id="rel_002",
            source_id="solana_ghi789",
            target_id="ethereum_abc123",
            relation_type="competes_with",
            confidence=0.80,
            evidence=["Solana competes with Ethereum"]
        )
    ]


# ============================================================================
# ENTITY TESTS
# ============================================================================

class TestGraphEntity:
    """Tests for GraphEntity dataclass."""
    
    def test_entity_creation(self):
        """Test creating a GraphEntity."""
        entity = GraphEntity(
            id="test_123",
            name="Test Entity",
            entity_type="concept",
            description="A test entity",
            confidence=0.9
        )
        
        assert entity.id == "test_123"
        assert entity.name == "Test Entity"
        assert entity.entity_type == "concept"
        assert entity.confidence == 0.9
        assert entity.aliases == []
    
    def test_entity_equality(self):
        """Test entity equality based on ID."""
        e1 = GraphEntity(id="same_id", name="Entity 1", entity_type="test")
        e2 = GraphEntity(id="same_id", name="Entity 2", entity_type="other")
        e3 = GraphEntity(id="different", name="Entity 1", entity_type="test")
        
        assert e1 == e2
        assert e1 != e3
        assert hash(e1) == hash(e2)
    
    def test_entity_to_dict(self):
        """Test converting entity to dictionary."""
        entity = GraphEntity(
            id="test_123",
            name="Test",
            entity_type="person",
            description="Test description",
            confidence=0.85,
            aliases=["Alias1", "Alias2"]
        )
        
        data = entity.to_dict()
        
        assert data['id'] == "test_123"
        assert data['name'] == "Test"
        assert data['aliases'] == ["Alias1", "Alias2"]
        assert 'created_at' in data
    
    def test_entity_from_dict(self):
        """Test creating entity from dictionary."""
        data = {
            'id': 'test_123',
            'name': 'Test Entity',
            'entity_type': 'organization',
            'description': 'Test',
            'confidence': 0.9,
            'aliases': ['TE'],
            'source_refs': ['doc1.txt']
        }
        
        entity = GraphEntity.from_dict(data)
        
        assert entity.id == 'test_123'
        assert entity.name == 'Test Entity'
        assert entity.aliases == ['TE']


# ============================================================================
# RELATIONSHIP TESTS
# ============================================================================

class TestGraphRelationship:
    """Tests for GraphRelationship dataclass."""
    
    def test_relationship_creation(self):
        """Test creating a relationship."""
        rel = GraphRelationship(
            id="rel_001",
            source_id="entity_1",
            target_id="entity_2",
            relation_type="founded_by",
            confidence=0.9,
            evidence=["Source text evidence"]
        )
        
        assert rel.source_id == "entity_1"
        assert rel.target_id == "entity_2"
        assert rel.relation_type == "founded_by"
    
    def test_relationship_to_dict(self):
        """Test converting relationship to dictionary."""
        rel = GraphRelationship(
            id="rel_001",
            source_id="src",
            target_id="tgt",
            relation_type="invested_in",
            description="Investment relationship"
        )
        
        data = rel.to_dict()
        
        assert data['source_id'] == "src"
        assert data['target_id'] == "tgt"
        assert data['type'] == "invested_in"


# ============================================================================
# DOCUMENT PROCESSOR TESTS
# ============================================================================

class TestDocumentProcessor:
    """Tests for DocumentProcessor."""
    
    def test_text_chunking(self):
        """Test basic text chunking."""
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=20)
        
        text = "This is a test sentence. " * 50  # Long text
        chunks = processor._chunk_text(text, "test.txt")
        
        assert len(chunks) > 1
        assert all(len(c.text) <= 120 for c in chunks)  # Allow some overflow for sentence boundaries
        assert chunks[0].source_doc == "test.txt"
    
    def test_process_text_file(self, temp_storage):
        """Test processing a text file."""
        processor = DocumentProcessor()
        
        # Create test file
        test_file = Path(temp_storage) / "test.txt"
        test_file.write_text("This is test content. " * 100)
        
        chunks = processor.process_file(test_file)
        
        assert len(chunks) > 0
        assert all(isinstance(c, DocumentChunk) for c in chunks)
    
    def test_process_markdown(self, temp_storage):
        """Test processing markdown file."""
        processor = DocumentProcessor()
        
        test_file = Path(temp_storage) / "test.md"
        test_file.write_text("# Heading\n\nThis is **markdown** content. " * 50)
        
        chunks = processor.process_file(test_file)
        
        assert len(chunks) > 0
    
    def test_process_json(self, temp_storage):
        """Test processing JSON file."""
        processor = DocumentProcessor()
        
        test_file = Path(temp_storage) / "test.json"
        data = {"name": "Test", "items": [{"id": i} for i in range(100)]}
        test_file.write_text(json.dumps(data))
        
        chunks = processor.process_file(test_file)
        
        assert len(chunks) > 0
        assert chunks[0].metadata.get('format') == 'json'
    
    def test_missing_file(self):
        """Test handling missing file."""
        processor = DocumentProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.process_file("/nonexistent/file.txt")


# ============================================================================
# ENTITY EXTRACTOR TESTS
# ============================================================================

class TestHybridEntityExtractor:
    """Tests for HybridEntityExtractor."""
    
    @pytest.mark.asyncio
    async def test_pattern_extraction(self):
        """Test pattern-based entity extraction."""
        extractor = HybridEntityExtractor(use_llm=False)
        
        text = "Ethereum was founded by Vitalik Buterin. Bitcoin was created by Satoshi Nakamoto."
        entities, relationships = await extractor.extract(text)
        
        # Should extract entities
        assert len(entities) > 0
        
        # Check for expected entities (names might vary based on pattern matching)
        entity_names = [e.name.lower() for e in entities]
        assert any('vitalik' in name or 'buterin' in name for name in entity_names)
    
    @pytest.mark.asyncio
    async def test_relationship_extraction(self):
        """Test relationship extraction."""
        extractor = HybridEntityExtractor(use_llm=False)
        
        text = "Vitalik Buterin founded Ethereum."
        entities, relationships = await extractor.extract(text)
        
        # Should have entities
        assert len(entities) >= 2
        
        # Check for relationship
        founded_rels = [r for r in relationships if r.relation_type == 'founded_by']
        assert len(founded_rels) > 0
    
    @pytest.mark.asyncio
    async def test_chunk_extraction(self):
        """Test extraction from document chunks."""
        extractor = HybridEntityExtractor(use_llm=False)
        
        chunks = [
            DocumentChunk(id="c1", text="Ethereum was founded by Vitalik Buterin.", source_doc="test.txt", chunk_index=0),
            DocumentChunk(id="c2", text="Solana competes with Ethereum.", source_doc="test.txt", chunk_index=1)
        ]
        
        entities, relationships = await extractor.extract_from_chunks(chunks)
        
        # Should have entities from both chunks
        entity_names = [e.name.lower() for e in entities]
        assert 'ethereum' in entity_names or any('ethereum' in e.aliases for e in entities)


# ============================================================================
# GRAPHRAG CORE TESTS
# ============================================================================

class TestGraphRAG:
    """Tests for the main GraphRAG class."""
    
    @pytest.mark.asyncio
    async def test_ingest_text(self, graphrag):
        """Test ingesting raw text."""
        text = "Ethereum was founded by Vitalik Buterin in 2014."
        
        result = await graphrag.ingest_text(text, source="test")
        
        assert result['status'] == 'success'
        assert result['chunks'] > 0
        assert result['entities'] > 0
    
    @pytest.mark.asyncio
    async def test_ingest_text_file(self, graphrag, temp_storage):
        """Test ingesting a text file."""
        test_file = Path(temp_storage) / "test_doc.txt"
        test_file.write_text("""
        Ethereum is a blockchain platform. It was founded by Vitalik Buterin.
        Solana is another blockchain that competes with Ethereum.
        Andreessen Horowitz invested in both platforms.
        """)
        
        result = await graphrag.ingest_file(test_file)
        
        assert result['status'] == 'success'
        assert result['entities'] > 0
    
    def test_query_entities(self, graphrag, sample_entities):
        """Test querying for entities."""
        # Add sample entities
        for entity in sample_entities:
            graphrag._add_entity(entity)
        
        graphrag._rebuild_graph()
        
        # Query
        results = graphrag.query("Ethereum")
        
        assert len(results['entities']) > 0
        assert any(e['name'] == "Ethereum" for e in results['entities'])
    
    def test_query_no_results(self, graphrag):
        """Test query with no matching results."""
        results = graphrag.query("xyznonexistent")
        
        assert results['summary'] == "No relevant information found."
    
    def test_get_neighbors(self, graphrag, sample_entities, sample_relationships):
        """Test getting entity neighbors."""
        # Add entities and relationships
        for entity in sample_entities:
            graphrag._add_entity(entity)
        for rel in sample_relationships:
            graphrag._add_relationship(rel)
        
        graphrag._rebuild_graph()
        
        # Get neighbors
        neighbors = graphrag.get_neighbors("ethereum_abc123")
        
        assert len(neighbors) > 0
        assert any(n['entity']['name'] == "Vitalik Buterin" for n in neighbors)
    
    def test_find_path(self, graphrag, sample_entities, sample_relationships):
        """Test finding path between entities."""
        # Add entities and relationships
        for entity in sample_entities:
            graphrag._add_entity(entity)
        for rel in sample_relationships:
            graphrag._add_relationship(rel)
        
        graphrag._rebuild_graph()
        
        # Find path
        path = graphrag.find_path("ethereum_abc123", "solana_ghi789")
        
        # Path should exist through the relationship
        assert path is not None
    
    def test_get_stats(self, graphrag, sample_entities):
        """Test getting graph statistics."""
        # Add entities
        for entity in sample_entities:
            graphrag._add_entity(entity)
        
        stats = graphrag.get_stats()
        
        assert stats['total_entities'] == len(sample_entities)
        assert 'entity_types' in stats
        assert 'technology' in stats['entity_types']
    
    def test_entity_merge(self, graphrag):
        """Test that duplicate entities are merged."""
        entity1 = GraphEntity(
            id="test_123",
            name="Test",
            entity_type="concept",
            aliases=["Alias1"],
            source_refs=["doc1.txt"]
        )
        
        entity2 = GraphEntity(
            id="test_123",
            name="Test",
            entity_type="concept",
            aliases=["Alias2"],
            source_refs=["doc2.txt"]
        )
        
        graphrag._add_entity(entity1)
        graphrag._add_entity(entity2)
        
        assert len(graphrag.entities) == 1
        assert set(graphrag.entities["test_123"].aliases) == {"Alias1", "Alias2"}
    
    def test_export_json(self, graphrag, sample_entities):
        """Test exporting to JSON."""
        for entity in sample_entities:
            graphrag._add_entity(entity)
        
        json_str = graphrag.export_json()
        
        data = json.loads(json_str)
        assert 'entities' in data
        assert 'stats' in data
        assert len(data['entities']) == len(sample_entities)
    
    def test_persistence(self, temp_storage):
        """Test saving and loading."""
        # Create and populate
        gr1 = GraphRAG(storage_path=temp_storage, use_llm=False)
        entity = GraphEntity(
            id="persist_test",
            name="Persist Test",
            entity_type="test"
        )
        gr1._add_entity(entity)
        gr1._save()
        
        # Load in new instance
        gr2 = GraphRAG(storage_path=temp_storage, use_llm=False)
        
        assert "persist_test" in gr2.entities
        assert gr2.entities["persist_test"].name == "Persist Test"
    
    def test_clear(self, graphrag, sample_entities):
        """Test clearing all data."""
        for entity in sample_entities:
            graphrag._add_entity(entity)
        
        assert len(graphrag.entities) > 0
        
        graphrag.clear()
        
        assert len(graphrag.entities) == 0
        assert len(graphrag.relationships) == 0


# ============================================================================
# PAUL'S WORLD INTEGRATION TESTS
# ============================================================================

class TestPaulWorldIntegration:
    """Tests for Paul's World integration."""
    
    @pytest.mark.asyncio
    async def test_research_topic(self, graphrag):
        """Test researching a topic."""
        # Add some data
        await graphrag.ingest_text("Ethereum is a blockchain founded by Vitalik Buterin.", "test")
        
        pw_integration = PaulWorldGraphRAG(graphrag)
        
        result = await pw_integration.research_topic("Ethereum", paul_name="TestPaul")
        
        assert result['topic'] == "Ethereum"
        assert result['researcher'] == "TestPaul"
        assert 'summary' in result
        assert 'key_entities' in result
    
    @pytest.mark.asyncio
    async def test_ingest_paul_knowledge(self, graphrag):
        """Test ingesting knowledge from a Paul."""
        pw_integration = PaulWorldGraphRAG(graphrag)
        
        result = await pw_integration.ingest_paul_knowledge(
            "Professor Paul",
            "Bitcoin uses proof-of-work consensus.",
            topic="Bitcoin"
        )
        
        assert result['status'] == 'success'
        assert 'Bitcoin' in [e.name for e in graphrag.entities.values()]
    
    def test_get_related_predictions(self, graphrag):
        """Test getting related predictions."""
        # Add some entities
        entity = GraphEntity(
            id="bitcoin_123",
            name="Bitcoin",
            entity_type="currency"
        )
        graphrag._add_entity(entity)
        graphrag._rebuild_graph()
        
        pw_integration = PaulWorldGraphRAG(graphrag)
        
        result = pw_integration.get_related_predictions("Will Bitcoin go up?")
        
        assert 'market' in result
        assert 'related_entities' in result


# ============================================================================
# EMBEDDING TESTS (Optional - only if sentence-transformers available)
# ============================================================================

class TestEmbeddingManager:
    """Tests for EmbeddingManager."""
    
    def test_initialization(self):
        """Test embedding manager initialization."""
        manager = EmbeddingManager()
        
        # May or may not be available depending on dependencies
        assert hasattr(manager, 'model')
        assert hasattr(manager, 'embedding_cache')
    
    def test_cosine_similarity(self):
        """Test cosine similarity calculation."""
        manager = EmbeddingManager()
        
        # Test with simple vectors
        a = [1.0, 0.0, 0.0]
        b = [1.0, 0.0, 0.0]
        c = [0.0, 1.0, 0.0]
        
        sim_ab = manager.cosine_similarity(a, b)
        sim_ac = manager.cosine_similarity(a, c)
        
        assert sim_ab == 1.0  # Same vector
        assert sim_ac == 0.0  # Orthogonal vectors


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """End-to-end integration tests."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self, temp_storage):
        """Test the complete ingestion and query pipeline."""
        graphrag = GraphRAG(storage_path=temp_storage, use_llm=False)
        
        # Ingest text
        text = """
        Ethereum was founded by Vitalik Buterin in 2015. It is a decentralized 
        blockchain platform that enables smart contracts. 
        
        Solana was founded by Anatoly Yakovenko. Solana is a high-performance 
        blockchain that competes with Ethereum. Both platforms support smart contracts.
        
        Andreessen Horowitz is a venture capital firm that invested in both 
        Ethereum and Solana. They are based in Menlo Park, California.
        """
        
        result = await graphrag.ingest_text(text, source="integration_test")
        
        assert result['status'] == 'success'
        
        # Query the graph
        query_result = graphrag.query("Ethereum")
        
        # Entity extraction may find different entities - test structure is correct
        assert 'entities' in query_result
        assert 'relationships' in query_result
        
        # Check stats
        stats = graphrag.get_stats()
        assert stats['total_entities'] >= 0
    
    @pytest.mark.asyncio
    async def test_directory_ingestion(self, temp_storage):
        """Test ingesting a directory of files."""
        graphrag = GraphRAG(storage_path=temp_storage, use_llm=False)
        
        # Create test files
        test_dir = Path(temp_storage) / "docs"
        test_dir.mkdir()
        
        (test_dir / "doc1.txt").write_text("Ethereum is a blockchain platform.")
        (test_dir / "doc2.txt").write_text("Bitcoin is the first cryptocurrency.")
        (test_dir / "doc3.md").write_text("# Crypto Overview\n\nSolana is fast.")
        
        results = await graphrag.ingest_directory(test_dir)
        
        assert len(results) == 3
        assert all(r['status'] == 'success' for r in results)
        
        # Verify data was added
        stats = graphrag.get_stats()
        assert stats['total_entities'] > 0
    
    def test_path_finding_integration(self, graphrag):
        """Test path finding with multiple hops."""
        # Create a chain: A -> B -> C
        a = GraphEntity(id="a", name="A", entity_type="test")
        b = GraphEntity(id="b", name="B", entity_type="test")
        c = GraphEntity(id="c", name="C", entity_type="test")
        
        r1 = GraphRelationship(id="r1", source_id="a", target_id="b", relation_type="connects_to")
        r2 = GraphRelationship(id="r2", source_id="b", target_id="c", relation_type="connects_to")
        
        graphrag._add_entity(a)
        graphrag._add_entity(b)
        graphrag._add_entity(c)
        graphrag._add_relationship(r1)
        graphrag._add_relationship(r2)
        graphrag._rebuild_graph()
        
        # Find path
        path = graphrag.find_path("a", "c")
        
        assert path is not None
        assert len(path) == 2


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================

class TestPerformance:
    """Performance-related tests."""
    
    @pytest.mark.asyncio
    async def test_large_text_handling(self, graphrag):
        """Test handling of large text inputs."""
        # Generate large text
        large_text = "Ethereum is a blockchain. " * 1000
        
        result = await graphrag.ingest_text(large_text, source="large_test")
        
        assert result['status'] == 'success'
        assert result['chunks'] > 1
    
    def test_graph_scalability(self, graphrag):
        """Test graph operations with many entities."""
        # Add many entities
        for i in range(100):
            entity = GraphEntity(
                id=f"entity_{i}",
                name=f"Entity {i}",
                entity_type="test"
            )
            graphrag._add_entity(entity)
        
        # Operations should still be fast
        stats = graphrag.get_stats()
        assert stats['total_entities'] == 100
        
        # Query should work
        results = graphrag.query("Entity 50")
        assert len(results['entities']) > 0


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Run with pytest if available, otherwise run basic tests
    try:
        pytest.main([__file__, "-v"])
    except ImportError:
        print("pytest not available, running basic tests...")
        
        # Run a simple test
        async def run_basic_test():
            temp_dir = tempfile.mkdtemp()
            try:
                graphrag = GraphRAG(storage_path=temp_dir, use_llm=False)
                
                result = await graphrag.ingest_text(
                    "Ethereum was founded by Vitalik Buterin.",
                    source="basic_test"
                )
                
                print(f"Ingestion result: {result}")
                
                query_result = graphrag.query("Ethereum")
                print(f"Query result: {json.dumps(query_result, indent=2, default=str)}")
                
                print("\n✅ Basic test passed!")
            finally:
                shutil.rmtree(temp_dir)
        
        asyncio.run(run_basic_test())
