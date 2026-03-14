# 🐟 MiroFish - Enhanced Knowledge & Memory for Swimming Pauls

MiroFish adds semantic knowledge graphs, persistent graph memory, and expanded persona generation to Swimming Pauls. It enables agents to learn from structured data, remember relationships between entities, and make more informed predictions.

## Features

### 1. Knowledge Graph (`knowledge_graph.py`)

Construct semantic knowledge graphs from seed data (PDFs, text, JSON):

```python
from swimming_pauls import GraphBuilder, KnowledgeGraph

# Build from directory
builder = GraphBuilder(name="crypto_knowledge")
builder.add_directory("./seed_data", extensions=['.txt', '.md', '.json', '.pdf'])
graph = builder.build()

# Query entities
technologies = graph.query_entities(entity_type='TECHNOLOGY')
founders = graph.query_entities(entity_type='PERSON')

# Find paths
path = graph.find_path("vitalik_buterin", "ethereum")

# Export/import
graph.export_json("knowledge.json")
loaded_graph = KnowledgeGraph.import_json("knowledge.json")
```

**Features:**
- Extract entities from text using regex patterns
- PDF text extraction support
- JSON structured data import
- Entity relationship mapping
- Path finding between entities
- NetworkX integration for advanced graph analysis
- Community detection
- Centrality calculations

### 2. Graph Memory (`graph_memory.py`)

Persistent SQLite-backed memory for agent knowledge:

```python
from swimming_pauls import GraphMemory

with GraphMemory() as memory:
    # Add entities
    entity = Entity(id="btc_1", name="Bitcoin", entity_type="ASSET")
    memory.add_entity(entity)
    
    # Teach an agent
    memory.teach_agent("paul_001", "btc_1", belief_strength=0.9)
    
    # Query agent knowledge
    knowledge = memory.get_agent_knowledge("paul_001")
    
    # Get prediction context
    context = memory.get_context_for_prediction(
        "paul_001", 
        market_entities=["btc_1", "eth_1"],
        depth=2
    )
```

**Features:**
- Multi-agent knowledge sharing
- Belief-weighted reasoning
- Temporal tracking
- Semantic search
- Knowledge observations
- Graph traversal for context retrieval

### 3. Persona Factory (`persona_factory.py`)

Generate 40+ unique Paul personas:

```python
from swimming_pauls import PaulPersonaFactory, generate_swimming_pauls_pool

# Generate diverse pool
factory = PaulPersonaFactory(seed=42)
pauls = factory.create_diverse_pool(total_count=40)

# Or use quick function
persona_dicts = generate_swimming_pauls_pool(count=40)

# Create specialized team
defi_team = factory.create_specialized_team(
    focus=SpecialtyDomain.DEFI, 
    size=5
)

# Breed personas
child = factory.breed_personas(parent1, parent2, mutation_rate=0.1)
```

**Persona Attributes:**
- Trading Style (scalper, swing, position, momentum, contrarian, etc.)
- Risk Profile (ultra-conservative to degen)
- Specialties (DeFi, NFT, Layer1, Macro, etc.)
- Cognitive strengths (pattern recognition, TA, FA, sentiment)
- Behavioral traits (patience, conviction, FOMO susceptibility)
- Unique backstories and catchphrases
- Avatar descriptions

### 4. Zep Cloud Integration (`zep_memory.py`) - Optional

Persistent long-term memory via Zep Cloud:

```python
from swimming_pauls import ZepMemoryManager, ZepMemoryConfig

# Requires ZEP_API_KEY environment variable
config = ZepMemoryConfig(api_key="your_key")
zep = ZepMemoryManager(config)
zep.initialize()

# Store memories
zep.remember(agent_id, "BTC broke $50k resistance", role="assistant")

# Recall with semantic search
memories = zep.recall(agent_id, query="Bitcoin price predictions")

# Get prediction context
context = zep.get_prediction_context(agent_id, market_context)
```

**Features:**
- Cross-session memory persistence
- Semantic search through experiences
- Automatic fact extraction
- Entity and relationship tracking
- Memory synthesis and profiling

### 5. Main Integration (`mirofish_integration.py`)

Unified interface combining all features:

```python
from swimming_pauls import MiroFishSwimmingPauls, MiroFishConfig

# Quick start
from swimming_pauls import quick_start
mirofish = quick_start(seed_data_path="./data", paul_count=40)

# Or with full configuration
config = MiroFishConfig(
    seed_data_path="./seed_data",
    paul_count=40,
    enable_graph_memory=True,
    enable_zep_memory=True,  # Optional
    zep_api_key="..."
)

mirofish = MiroFishSwimmingPauls(config)
mirofish.initialize()
mirofish.spawn_paul_pool()

# Run prediction
market_data = {
    'asset': 'BTC',
    'price_trend': 0.15,
    'volume': 0.8,
    'sentiment': 0.6
}

result = mirofish.run_prediction_round(market_data)
print(f"Consensus: {result['consensus']['dominant']}")
print(f"Confidence: {result['consensus']['confidence']:.1%}")
```

## Installation

```bash
# Basic installation
pip install -r requirements.txt

# With PDF support
pip install PyPDF2

# With Zep Cloud (optional)
pip install zep-cloud
export ZEP_API_KEY="your_api_key"

# With full graph analysis
pip install networkx
```

## Directory Structure

```
swimming_pauls/
├── knowledge_graph.py       # Semantic graph construction
├── graph_memory.py          # Persistent agent memory
├── persona_factory.py       # 40+ Paul generation
├── zep_memory.py           # Zep Cloud integration (optional)
├── mirofish_integration.py # Main integration module
└── requirements.txt        # Updated dependencies
```

## Usage Examples

### Example 1: Building Knowledge from Research

```python
from swimming_pauls import GraphBuilder, GraphMemory

# Build knowledge from research papers
builder = GraphBuilder("crypto_research")
builder.add_directory("./research_papers", extensions=['.pdf', '.txt'])
graph = builder.build()

# Store in memory
memory = GraphMemory()
memory.import_knowledge_graph(graph, teaching_agents=["paul_analyst"])
```

### Example 2: Running with Knowledge-Aware Agents

```python
from swimming_pauls import MiroFishSwimmingPauls

mirofish = MiroFishSwimmingPauls()
mirofish.initialize()
mirofish.initialize_knowledge_graph("./crypto_data")
mirofish.spawn_paul_pool(count=40)

# Agents now use knowledge graph for context
result = mirofish.run_prediction_round(market_data)
```

### Example 3: Creating Specialized Teams

```python
from swimming_pauls import PaulPersonaFactory, SpecialtyDomain

factory = PaulPersonaFactory()

# Create DeFi specialists
defi_team = factory.create_specialized_team(SpecialtyDomain.DEFI, size=5)

# Create NFT specialists  
nft_team = factory.create_specialized_team(SpecialtyDomain.NFT, size=5)

# Create macro analysts
macro_team = factory.create_specialized_team(SpecialtyDomain.MACRO, size=5)
```

### Example 4: Memory-Augmented Predictions

```python
# Each agent automatically:
# 1. Recalls relevant knowledge from graph memory
# 2. Searches past predictions via Zep
# 3. Considers relationships between entities
# 4. Generates enhanced reasoning

prediction = agent.predict_with_context(market_data)
# Returns: direction, confidence, enhanced_reasoning, 
#          knowledge_context, zep_context
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MiroFishSwimmingPauls                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │Knowledge    │  │  Graph      │  │   Zep Cloud         │  │
│  │  Graph      │  │  Memory     │  │   (Optional)        │  │
│  │             │  │             │  │                     │  │
│  │• Entities   │  │• SQLite     │  │• Long-term memory   │  │
│  │• Relations  │  │• Beliefs    │  │• Semantic search    │  │
│  │• Paths      │  │• Traversal  │  │• Fact extraction    │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                     │             │
│         └────────────────┴─────────────────────┘             │
│                          │                                   │
│              ┌───────────┴───────────┐                       │
│              │   MiroFishAgent       │                       │
│              │                       │                       │
│              │ • GraphMemoryMixin    │                       │
│              │ • Zep memory          │                       │
│              │ • Paul persona        │                       │
│              │ • Enhanced reasoning  │                       │
│              └───────────┬───────────┘                       │
│                          │                                   │
│              ┌───────────┴───────────┐                       │
│              │   40+ Paul Pool       │                       │
│              │                       │                       │
│              │ • Diverse trading     │                       │
│              │   styles              │                       │
│              │ • Risk profiles       │                       │
│              │ • Specialties         │                       │
│              └───────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Performance

- Knowledge Graph: Handles 10k+ entities efficiently
- Graph Memory: SQLite-based, supports concurrent access
- Persona Generation: ~1000 personas/second
- Zep Cloud: API call latency dependent (~100-500ms per call)

## Environment Variables

```bash
# Zep Cloud (optional)
export ZEP_API_KEY="your_zep_api_key"
export ZEP_BASE_URL="https://api.getzep.com"  # Optional
export ZEP_MAX_CONTEXT=20
export ZEP_SEARCH_TOP_K=5

# Graph Memory
export GRAPH_MEMORY_PATH="~/.scales/graph_memory.db"
```

## License

MIT License - See main project license
