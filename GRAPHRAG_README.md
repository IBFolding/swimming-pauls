# GraphRAG - Graph Retrieval-Augmented Generation for Swimming Pauls

Structured knowledge extraction from documents with semantic search and traversable knowledge graphs.

## Overview

GraphRAG extends the Swimming Pauls prediction system with advanced knowledge management capabilities:

- **Entity Extraction**: Automatically extract people, organizations, technologies, and concepts from documents
- **Relationship Mapping**: Build connected graphs showing how entities relate to each other
- **Semantic Search**: Find relevant information using embeddings and similarity matching
- **Graph Traversal**: Navigate connections between entities to discover insights
- **Paul's World Integration**: Let Pauls research topics using the knowledge graph

## Features

### 1. Document Support
- **PDF** - Extract text and structure from PDF files
- **TXT** - Plain text documents
- **MD** - Markdown files
- **JSON** - Structured data files
- **Code files** - Python, JavaScript, TypeScript, Solidity

### 2. Entity Types
- Person (founders, CEOs, developers)
- Organization (companies, funds, foundations)
- Location (cities, regions, countries)
- Technology (blockchains, protocols, tools)
- Concept (ideas, theories, methodologies)
- Product (specific products, platforms)
- Event (conferences, launches, incidents)
- Market (financial markets, indices)
- Currency (crypto tokens, fiat currencies)
- Protocol (DeFi protocols, standards)

### 3. Relationship Types
- `founded_by` - Company founded by person
- `works_at` - Person employed by organization
- `invested_in` - Investment relationships
- `acquired` - Acquisition events
- `partnered_with` - Partnership agreements
- `competes_with` - Competitive relationships
- `built_on` - Technical dependencies
- `uses` - Utilization relationships
- `depends_on` - Dependencies
- `part_of` - Hierarchical relationships
- `located_in` - Geographic relationships
- `created` - Creation relationships
- `influences` - Influence relationships
- `related_to` - General connections

## Installation

### Basic Installation
```bash
# Core functionality (pattern-based extraction)
pip install graphrag  # No additional dependencies needed
```

### Enhanced Installation
```bash
# For PDF support
pip install PyPDF2

# For graph algorithms
pip install networkx

# For semantic search with embeddings
pip install sentence-transformers

# For LLM-powered extraction (optional)
# Configure LLM client in your environment
```

## Quick Start

### Basic Usage

```python
from graphrag import GraphRAG
import asyncio

async def main():
    # Initialize GraphRAG
    graphrag = GraphRAG(storage_path="data/graphrag")
    
    # Ingest a document
    result = await graphrag.ingest_file("document.pdf")
    print(f"Ingested: {result['entities']} entities")
    
    # Query the knowledge graph
    results = graphrag.query("What do we know about Ethereum?")
    print(results['summary'])
    
    # Get specific entity information
    for entity in results['entities']:
        print(f"- {entity['name']}: {entity['type']}")

asyncio.run(main())
```

### Paul's World Integration

```python
from graphrag import PaulWorldGraphRAG

# Initialize integration
pw_graphrag = PaulWorldGraphRAG()

# Have a Paul research a topic
research = await pw_graphrag.research_topic(
    topic="Ethereum scaling solutions",
    paul_name="Professor Paul"
)

print(research['summary'])
print(research['insights'])
```

## API Reference

### GraphRAG Class

#### Constructor
```python
GraphRAG(
    storage_path: str = "data/graphrag",
    use_llm: bool = True,
    llm_provider: str = "ollama",
    llm_model: str = "llama3",
    embedding_model: Optional[str] = None
)
```

#### Methods

**ingest_file(file_path)**
```python
result = await graphrag.ingest_file("path/to/document.pdf")
# Returns: {'status': 'success', 'entities': 5, 'relationships': 3, ...}
```

**ingest_directory(directory)**
```python
results = await graphrag.ingest_directory("path/to/documents/")
# Ingests all supported files in the directory
```

**ingest_text(text, source)**
```python
result = await graphrag.ingest_text("Raw text content", source="user_input")
```

**query(question, top_k=5)**
```python
results = graphrag.query("What do we know about X?")
# Returns: {
#     'question': '...',
#     'entities': [...],
#     'relationships': [...],
#     'chunks': [...],
#     'paths': [...],
#     'summary': '...'
# }
```

**get_neighbors(entity_id)**
```python
neighbors = graphrag.get_neighbors("entity_id")
# Returns connected entities with relationship information
```

**find_path(source_id, target_id)**
```python
path = graphrag.find_path("entity_a_id", "entity_b_id")
# Returns list of relationships connecting the entities
```

**get_stats()**
```python
stats = graphrag.get_stats()
# Returns: {
#     'total_entities': 100,
#     'total_relationships': 250,
#     'entity_types': {...},
#     'embedding_available': True
# }
```

**export_json(output_path)**
```python
json_data = graphrag.export_json("output.json")
# Exports entire graph to JSON format
```

### PaulWorldGraphRAG Class

#### Methods

**research_topic(topic, paul_name)**
```python
research = await pw_graphrag.research_topic(
    "Bitcoin price prediction",
    paul_name="Trader Paul"
)
# Returns structured research results for Paul consumption
```

**ingest_paul_knowledge(paul_name, knowledge_content, topic)**
```python
await pw_graphrag.ingest_paul_knowledge(
    "Professor Paul",
    "Ethereum uses proof-of-stake",
    topic="Ethereum"
)
```

**get_related_predictions(market_question)**
```python
analysis = pw_graphrag.get_related_predictions("Will BTC go up?")
# Returns related entities and context for prediction
```

## CLI Usage

```bash
# Ingest a file
python graphrag.py ingest document.pdf

# Ingest a directory
python graphrag.py ingest ./documents/

# Query the graph
python graphrag.py query "What do we know about Ethereum?"

# Show statistics
python graphrag.py stats

# Export to JSON
python graphrag.py export graph_export.json

# Clear all data
python graphrag.py clear
```

## Architecture

### Components

1. **DocumentProcessor**: Handles different file formats and chunks text
2. **HybridEntityExtractor**: Combines LLM and pattern-based extraction
3. **EmbeddingManager**: Manages vector embeddings for semantic search
4. **GraphRAG**: Main class coordinating all components
5. **PaulWorldGraphRAG**: Integration layer with Paul's World

### Data Flow

```
Document → DocumentProcessor → Chunks
    ↓
HybridEntityExtractor → Entities + Relationships
    ↓
EmbeddingManager → Vector Embeddings
    ↓
Knowledge Graph (NetworkX) → Query/Search
    ↓
Paul's World Integration → Research Insights
```

### Storage

- **JSON Files**: Entities, relationships, chunks stored as JSON
- **Vector Cache**: Embeddings cached for performance
- **NetworkX Graph**: In-memory graph for traversal operations

## Query Examples

### Basic Queries
```python
# Find information about a specific entity
graphrag.query("Ethereum")

# Find people
graphrag.query("founders and CEOs")

# Find organizations
graphrag.query("venture capital firms")
```

### Advanced Queries
```python
# Find competitive relationships
results = graphrag.query("competition")
for r in results['relationships']:
    if 'compet' in r['type']:
        print(f"{r['source']['name']} vs {r['target']['name']}")

# Find paths between entities
path = graphrag.find_path("bitcoin_id", "ethereum_id")
for rel in path:
    print(f"{rel.source_id} --{rel.relation_type}--> {rel.target_id}")

# Get entity network
neighbors = graphrag.get_neighbors("entity_id")
for n in neighbors:
    print(f"{n['entity']['name']} ({n['direction']}: {n['relationship']['type']})")
```

## Integration with Existing Knowledge Graph

GraphRAG is backward compatible with the existing `knowledge_graph.py`:

```python
from knowledge_graph import KnowledgeGraph, GraphRAGIntegration

# Create traditional knowledge graph
kg = KnowledgeGraph(name="legacy")

# Add some data...

# Convert to GraphRAG
integration = GraphRAGIntegration(kg)
graphrag = integration.to_graphrag()

# Now use GraphRAG features
results = graphrag.query("What do we know about X?")
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m pytest test_graphrag.py -v

# Run specific test class
python -m pytest test_graphrag.py::TestGraphRAG -v

# Run with coverage
python -m pytest test_graphrag.py --cov=graphrag --cov-report=html
```

## Performance Considerations

### Without Embeddings (Pattern-based only)
- Fast extraction (~100 docs/minute)
- Lower accuracy
- No semantic search

### With Embeddings
- Slower initial ingestion (~10 docs/minute)
- High-quality semantic search
- Requires ~500MB RAM for model

### With LLM
- Slow extraction (~1-5 docs/minute)
- Highest accuracy
- Requires LLM API or local model

### Recommended Configuration

**For Production:**
```python
GraphRAG(
    use_llm=True,           # Enable LLM extraction
    llm_provider="ollama",  # Local LLM
    embedding_model="all-MiniLM-L6-v2"  # Fast embeddings
)
```

**For Development:**
```python
GraphRAG(
    use_llm=False,  # Fast pattern-based extraction
    # Embeddings optional
)
```

## Troubleshooting

### Common Issues

**ImportError for PyPDF2**
```bash
pip install PyPDF2
```

**Slow ingestion**
- Disable LLM: `use_llm=False`
- Reduce chunk size: `chunk_size=500`

**Out of memory**
- Use smaller embedding model
- Process files in batches
- Clear cache periodically

**No entities extracted**
- Check file format is supported
- Verify text is extractable (try plain text first)
- Enable LLM for better extraction

## Future Enhancements

- [ ] Neo4j backend for large-scale graphs
- [ ] Real-time graph updates
- [ ] Multi-modal extraction (images, tables)
- [ ] Incremental learning from Paul predictions
- [ ] Graph visualization integration
- [ ] Collaborative filtering based on entity relationships

## License

Part of the Swimming Pauls prediction system.

## Author

Howard (H.O.W.A.R.D) - Heuristic Operations, Workflow Automation, Resource Director
