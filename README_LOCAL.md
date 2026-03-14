# Swimming Pauls - 100% Local Multi-Agent Platform

A fully autonomous multi-agent prediction and analysis system that runs entirely on your machine with **NO API keys, NO cloud services, and NO internet required**.

## 🎯 Key Features

- ✅ **100% Local** - No API keys, no cloud dependencies
- ✅ **Works Offline** - Complete functionality without internet
- ✅ **SQLite Memory** - Persistent local storage
- ✅ **40+ AI Agents** - Diverse persona-driven agents
- ✅ **Knowledge Graphs** - Semantic entity-relationship mapping
- ✅ **Market Analysis** - Local data, RSS feeds, web scraping
- ✅ **Monte Carlo Simulations** - Statistical modeling
- ✅ **Terminal Visualizations** - Rich local output

## Quick Start

```bash
# Install (minimal dependencies)
pip install httpx networkx

# Run 100% locally
python -c "
from swimming_pauls import MiroFishSwimmingPauls

# Create 40 agents - no internet needed
mirofish = MiroFishSwimmingPauls.quick_start(paul_count=40)

# Run prediction
result = mirofish.run_prediction_round({
    'asset': 'BTC',
    'price_trend': 0.15,
    'sentiment': 0.6
})

print(f\"Consensus: {result['consensus']['dominant']}\")
print(f\"Confidence: {result['consensus']['confidence']:.1%}\")
"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Swimming Pauls                           │
│                    (100% LOCAL)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │Local News    │  │Local Market  │  │Local Sentiment│     │
│  │Connector     │  │Connector     │  │Connector      │     │
│  │              │  │              │  │               │     │
│  │• Local files │  │• CSV files   │  │• Text files   │     │
│  │• RSS feeds   │  │• Cache       │  │• Rule-based   │     │
│  │• Web scraping│  │• Demo data   │  │• Keywords     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                   ┌────────┴────────┐                        │
│                   │  Data Feed      │                        │
│                   │  Manager        │                        │
│                   └────────┬────────┘                        │
│                            │                                 │
│  ┌─────────────────────────┼─────────────────────────┐       │
│  │                         │                         │       │
│  │  ┌─────────────┐  ┌────┴────┐  ┌─────────────┐  │       │
│  │  │ 40+ Pauls   │  │Knowledge│  │  Graph      │  │       │
│  │  │  Agents     │  │ Graph   │  │  Memory     │  │       │
│  │  │             │  │         │  │             │  │       │
│  │  │• Diverse    │  │• Entities│ │• SQLite     │  │       │
│  │  │  personas   │  │• Relations│ │• Beliefs    │  │       │
│  │  │• Specialties│  │• Paths    │ │• Traversal  │  │       │
│  │  │• Risk models│  └─────────┘  └─────────────┘  │       │
│  │  └─────────────┘                                 │       │
│  │                                                  │       │
│  └──────────────────────────────────────────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Sources (All Local)

### News
- **Local Files**: JSON, CSV, TXT in `./data/news/`
- **RSS Feeds**: No API key required
- **Web Scraping**: httpx + regex (BeautifulSoup optional)
- **Demo Mode**: Always works offline

### Market Data
- **Local CSV**: Price history files
- **Cache**: Previous data stored in SQLite
- **Demo Data**: Deterministic simulated prices

### Sentiment
- **Local Text**: Analyzes local text files
- **Rule-Based**: Keyword sentiment scoring
- **Deterministic**: Consistent demo sentiment

## File Structure

```
swimming_pauls/
├── __init__.py                 # Package exports
├── agent.py                    # Core agent implementation
├── simulation.py               # Simulation engine
├── memory.py                   # SQLite memory (original)
├── local_memory.py             # Extended local memory
├── local_data_feeds.py         # ⭐ 100% local data feeds
├── knowledge_graph.py          # ⭐ Semantic knowledge graphs
├── graph_memory.py             # ⭐ Graph-based agent memory
├── persona_factory.py          # ⭐ 40+ Paul generator
├── mirofish_integration.py     # ⭐ Unified integration
├── zep_memory.py               # Optional cloud (disabled by default)
├── visualization.py            # Terminal/HTML output
├── advanced.py                 # Monte Carlo, sensitivity
├── test_local.py               # Local-only test suite
└── requirements.txt            # Minimal dependencies
```

## Usage Examples

### Basic Simulation (Local Only)

```python
from swimming_pauls import SwimmingPauls

pauls = SwimmingPauls()
result = await pauls.run_simulation(rounds=20)
pauls.visualize()
```

### MiroFish with 40+ Pauls

```python
from swimming_pauls import MiroFishSwimmingPauls, MiroFishConfig

config = MiroFishConfig(
    paul_count=40,
    enable_graph_memory=True,
    enable_zep_memory=False,  # Explicitly local
)

mirofish = MiroFishSwimmingPauls(config)
mirofish.initialize()
mirofish.spawn_paul_pool()

# Run with knowledge context
result = mirofish.run_prediction_round({
    'asset': 'BTC',
    'price_trend': 0.15,
    'volume': 0.8,
    'sentiment': 0.6,
})

print(f"Consensus: {result['consensus']['dominant']}")
print(f"Confidence: {result['consensus']['confidence']:.1%}")

# Get individual predictions
for pred in result['predictions'][:5]:
    print(f"{pred['agent_name']}: {pred['direction']} ({pred['confidence']:.0%})")
```

### Knowledge Graph Construction

```python
from swimming_pauls import GraphBuilder, KnowledgeGraph

# Build from local files
builder = GraphBuilder(name="crypto_knowledge")
builder.add_directory("./research_papers", extensions=['.pdf', '.txt'])
graph = builder.build()

# Query knowledge
entities = graph.query_entities(entity_type='TECHNOLOGY')
paths = graph.find_path("bitcoin", "ethereum")

# Export
graph.export_json("knowledge.json")
```

### Custom Personas

```python
from swimming_pauls import PaulPersonaFactory, SpecialtyDomain

factory = PaulPersonaFactory(seed=42)

# Create diverse pool
pauls = factory.create_diverse_pool(total_count=40)

# Create specialized team
defi_team = factory.create_specialized_team(
    focus=SpecialtyDomain.DEFI,
    size=5
)

# Breed personas
child = factory.breed_personas(parent1, parent2, mutation_rate=0.1)
```

### Local Data Feeds

```python
from swimming_pauls import (
    LocalNewsConnector, 
    LocalMarketConnector,
    LocalSentimentConnector
)

# News from local files + RSS
news = LocalNewsConnector(local_data_path="./data/news")
articles = await news.fetch(query="crypto", limit=10)

# Market from CSV + cache
market = LocalMarketConnector(local_data_path="./data/market")
prices = await market.fetch(symbols=["BTC", "ETH"])

# Sentiment from text analysis
sentiment = LocalSentimentConnector(local_data_path="./data/sentiment")
scores = await sentiment.fetch(topic="bitcoin")
```

## Configuration

### Environment Variables (Optional)

```bash
# Force local-only mode (default)
export SWIMMING_PAULS_LOCAL=1

# Disable all API calls
export SWIMMING_PAULS_USE_APIS=0

# Optional: Enable cloud features (disabled by default)
export SWIMMING_PAULS_USE_APIS=1
```

### Directory Structure for Local Data

```
./data/
├── news/
│   ├── articles.json      # JSON array of articles
│   ├── headlines.csv      # CSV with title,date,source
│   └── sources/           # Text files
├── market/
│   ├── BTC.csv            # Symbol-specific CSV
│   ├── ETH.csv
│   └── prices.csv         # Combined prices
└── sentiment/
    └── posts/             # Text files to analyze
```

## Dependencies

### Required (Minimal)
```
httpx>=0.25.0      # HTTP for RSS and web scraping
networkx>=3.0      # Graph analysis
```

### Optional (Enhanced functionality)
```
beautifulsoup4     # Better web scraping
lxml               # Faster XML parsing
PyPDF2             # PDF text extraction
```

### NOT Required
```
# No API keys needed:
# - NEWS_API_KEY
# - MARKET_API_KEY
# - REDDIT_CLIENT_ID
# - OPENAI_API_KEY
# - etc.
```

## Testing

```bash
# Run local-only tests
cd swimming_pauls
python3 test_local.py

# Expected output:
# ✅ ALL TESTS PASSED!
# Swimming Pauls is 100% local-capable.
```

## Comparison: Local vs Cloud

| Feature | Local Mode | Cloud Mode (Optional) |
|---------|-----------|----------------------|
| News | RSS + Files + Scraping | NewsAPI, etc. |
| Market | CSV + Cache + Demo | CoinGecko, etc. |
| Sentiment | Rule-based + Files | Reddit API, Twitter |
| Memory | SQLite | Zep Cloud |
| LLM | Local (future: ollama) | OpenAI, etc. |
| **Works Offline** | ✅ Yes | ❌ No |
| **API Keys** | ❌ None | ✅ Required |

## Troubleshooting

### "No module named 'swimming_pauls'"
```bash
# Run from parent directory
cd /path/to/workspace
python3 -m swimming_pauls.test_local
```

### "Empty data"
```bash
# Create data directories
mkdir -p data/news data/market data/sentiment

# The system uses demo data by default - no action needed!
```

### Import errors
```bash
# Install minimal dependencies
pip install httpx networkx
```

## License

MIT License - See LICENSE file

## Credits

Created by Howard (H.O.W.A.R.D) - Heuristic Operations, Workflow Automation, Resource Director
