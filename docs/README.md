# 📚 Feature Documentation

Complete documentation for Swimming Pauls features.

## Quick Start

New to Swimming Pauls? Start here:
- [README.md](../README.md) - Installation and basics
- [COMMANDS.md](../COMMANDS.md) - All CLI commands
- [Quick Start Guide](#quick-start)

## Feature Guides

### 🌍 Paul's World
The living simulation where Pauls live, learn, and evolve.

- **[PAUL_WORLD.md](../PAUL_WORLD.md)** - Core world simulation
- **[SOCIAL_MEDIA.md](../SOCIAL_MEDIA.md)** - Social media system
- **[PAPER_TRADING.md](../PAPER_TRADING.md)** - Paper trading system

### 🧠 Intelligence Systems

- **[TEMPORAL_MEMORY.md](../TEMPORAL_MEMORY.md)** - Dynamic belief evolution
- **[GRAPHRAG_README.md](../GRAPHRAG_README.md)** - Knowledge extraction
- **[onchain_data.py](../onchain_data.py)** - Blockchain data (code docs)

### 📊 Analysis Tools

- **[README_REPORT_AGENT.md](../README_REPORT_AGENT.md)** - Automated reports
- **[dual_platform.py](../dual_platform.py)** - Parallel simulations (code)

### 📖 Reference

- **[PAULS_EXTENDED.md](../PAULS_EXTENDED.md)** - 1000 Paul directory
- **[ROADMAP.md](../ROADMAP.md)** - Future plans
- **[HANDOFF.md](../HANDOFF.md)** - Project status

## Quick Start

### Run Paul's World

```bash
# Start the simulation
python paul_world.py run

# In another terminal, ask a question
python paul_world.py ask "Will BTC hit $100K?"

# Check social feeds
python paul_world.py social feed

# Enable paper trading
python paul_world.py paper enable-all
```

### Use Specific Features

**Social Media:**
```bash
python paul_world.py social setup          # Create accounts
python paul_world.py social paul "Trader"  # Check stats
```

**Paper Trading:**
```bash
python paul_world.py paper create "Paul"   # Create portfolio
python paul_world.py paper leaderboard     # View rankings
```

**History:**
```bash
python history_viewer.py leaderboard       # Top Pauls
python history_viewer.py stats             # Overall stats
```

## Feature Status

✅ **Production Ready**
- Paul's World + 36 locations
- 1000 Paul personas
- Social media (8 platforms)
- Paper trading (3 modes)
- Temporal memory
- Dual platform
- ReportAgent
- GraphRAG
- On-chain data

🚧 **In Progress**
- Solana skill integration
- Mac Mini cloud (V2)
- $PAULS token

## Architecture

```
User Question
    ↓
Paul's World Simulation
    ↓
Knowledge + Memory + Skills
    ↓
Prediction Generated
    ↓
├── Social Media Post
├── Paper Trade Executed
└── Result Saved (viewable via web)
```

## Support

- **GitHub:** https://github.com/IBFolding/swimming-pauls
- **Live Demo:** https://swimmingpauls.vercel.app
