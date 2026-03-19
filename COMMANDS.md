# 🦷 Swimming Pauls - Commands Reference

Complete list of all commands and how to use them.

## Table of Contents
- [Quick Start Commands](#quick-start-commands)
- [Paul's World Commands](#pauls-world-commands)
- [Prediction Commands](#prediction-commands)
- [History & Analytics Commands](#history--analytics-commands)
- [Skill Management Commands](#skill-management-commands)
- [Dual Platform Commands](#dual-platform-commands)
- [ReportAgent Commands](#reportagent-commands)
- [Utility Commands](#utility-commands)

---

## Quick Start Commands

### Start the Local Agent
```bash
python local_agent.py
```
Starts the WebSocket server that handles predictions. Required before using the web UI.

### Start HTTP Server (for Web UI)
```bash
python -m http.server 3005
```
Serves the web interface at `http://localhost:3005`

### Run with OpenClaw (Easiest)
```bash
openclaw run swimming-pauls
```
One-command setup using OpenClaw CLI.

---

## Paul's World Commands

### Check World Status
```bash
python paul_world.py status
```
Shows current state: time, Paul locations, activities, energy levels.

### Run World Simulation
```bash
python paul_world.py run
```
Starts continuous simulation where Pauls live their lives (move, interact, learn).

**What happens:**
- Pauls move between locations based on needs
- Energy/hunger/social stats update each tick
- Knowledge transfer at Cafe, Research Lab
- Auto-saves to SQLite every 12 ticks

### Ask the World
```bash
python paul_world.py ask "Will BTC hit $100K?"
```
Get predictions from World Pauls with knowledge, memory, and skills.

**Output includes:**
- Consensus (BULLISH/BEARISH/NEUTRAL)
- Individual Paul reasoning with knowledge references
- Links to view results in Explorer/Visualization

### Export World State
```bash
python paul_world.py export
```
Exports all Paul states to `paul_world_export.json`

---

## Prediction Commands

### Ask from Terminal (Quick)
```bash
python ask_pauls.py "Your question here"
```
Quick CLI prediction without web UI.

### Ask with Options
```bash
python ask_pauls.py "Will ETH flip BTC?" --pauls 100 --rounds 50
```
- `--pauls`: Number of Pauls to use (default: 50)
- `--rounds`: Debate rounds (default: 20)

### Using Simulation Directly
```python
from simulation import quick_simulate
from agent import Agent, PersonaType

agents = [Agent(f"Paul_{i}", PersonaType.TRADER) for i in range(10)]
result = quick_simulate(rounds=10, agents=agents, question="Will it rain?")
```

---

## History & Analytics Commands

### View Paul Leaderboard
```bash
python history_viewer.py leaderboard
```
Shows top-performing Pauls by accuracy.

### View Recent Predictions
```bash
python history_viewer.py recent
```
Shows last 20 predictions with outcomes.

### Check Specific Paul
```bash
python history_viewer.py paul "Visionary Paul"
```
Shows all predictions and accuracy for a specific Paul.

### Mark Prediction Outcome
```bash
python history_viewer.py resolve abc123 CORRECT
```
Mark prediction ID `abc123` as correct (updates Paul accuracy scores).

### View Overall Stats
```bash
python history_viewer.py stats
```
Shows aggregate statistics: total predictions, accuracy, consensus rate.

### Export History
```bash
python history_viewer.py export predictions.json
```
Exports all prediction history to JSON.

---

## Skill Management Commands

### Create New Skill
```bash
python skills.py create my_skill "My custom skill description"
```
Creates template files in `skills/custom/my_skill/`

### List All Skills
```bash
python skills.py list
```
Shows all available skills (built-in and custom).

### Assign Skill to Paul
```bash
python skills.py assign "Trader Paul" crypto_price
```
Gives Trader Paul access to the crypto_price skill.

### Remove Skill from Paul
```bash
python skills.py remove "Trader Paul" crypto_price
```

### Test Skill
```bash
python skills.py test crypto_price bitcoin
```
Runs a skill directly with test input.

---

## Dual Platform Commands

### Run Dual Platform Simulation
```python
from dual_platform import DualPlatformBuilder
import asyncio

async def main():
    simulator = (DualPlatformBuilder()
        .add_conservative_platform()
        .add_aggressive_platform()
        .add_balanced_platform()
        .build())
    
    result = await simulator.run()
    print(f"Consensus: {result.dual_consensus.direction}")

asyncio.run(main())
```

### Quick Dual Simulation
```python
from dual_platform import quick_dual_simulation

result = quick_dual_simulation(
    market_data={"asset": "BTC", "price": 45000},
    platforms=["conservative", "aggressive"]
)
```

---

## ReportAgent Commands

### Generate Report
```python
from report_agent import ReportAgent
import asyncio

async def main():
    agent = ReportAgent()
    report, paths = await agent.generate_and_save(
        simulation_result, 
        agents,
        topic="BTC price prediction"
    )
    print(f"Report saved: {paths['html']}")

asyncio.run(main())
```

### Start Report API Server
```bash
python report_api.py
```
Starts HTTP server on port 8080 with endpoints:
- `GET /api/reports` - List all reports
- `GET /api/reports/{id}` - Get specific report
- `POST /api/simulate` - Run simulation + generate report

---

## Utility Commands

### Test System Capacity
```bash
python test_capacity.py
```
Tests how many Pauls your machine can handle.

**Sample output:**
```
✅ Max tested: 10,000 Pauls
⏱️  Average init time: 0.06s
📊 Estimated memory: ~100.0 MB
```

### Ingest Documents (GraphRAG)
```bash
python graphrag.py ingest data/knowledge/
```
Processes documents and builds knowledge graph.

### Query Knowledge Base
```bash
python graphrag.py query "What do we know about Ethereum?"
```
Natural language query against knowledge graph.

### Run Temporal Demo
```bash
python temporal_demo.py
```
Interactive demo showing belief evolution over time.

### Run Dual Platform Demo
```bash
python dual_platform.py demo
```
Shows parallel simulations with different configurations.

---

## Database Commands

### View Database Location
All data stored in `data/` directory:
- `predictions.db` - Prediction history
- `paul_world.db` - Paul's World state
- `paul_performance.db` - Paul accuracy metrics
- `results/*.json` - Saved prediction results

### Backup Data
```bash
cp -r data/ data_backup_$(date +%Y%m%d)/
```

### Reset All Data
```bash
rm -rf data/*.db data/results/*.json
```
⚠️ **Warning:** This deletes all history and Paul states!

---

## Environment Variables

### Force Local Mode
```bash
export SWIMMING_PAULS_LOCAL=1
```
Disables any cloud features.

### Enable API Mode (Optional)
```bash
export SWIMMING_PAULS_USE_APIS=1
```
Allows optional cloud API usage.

---

## Getting Help

### Check Command Help
Most commands support `--help`:
```bash
python paul_world.py --help
python history_viewer.py --help
python skills.py --help
```

### Debug Mode
Add `DEBUG=1` before any command for verbose output:
```bash
DEBUG=1 python paul_world.py ask "Will BTC go up?"
```

---

## Common Workflows

### 1. Daily Prediction Workflow
```bash
# Start services
python local_agent.py &
python -m http.server 3005 &

# Ask question
python ask_pauls.py "Will BTC hit $100K by end of year?"

# Check results in browser
open http://localhost:3005/explorer.html?id=abc123
```

### 2. Paul's World Research Workflow
```bash
# Add knowledge documents
cp research.pdf data/knowledge/

# Run simulation for a day
python paul_world.py run

# Ask informed question
python paul_world.py ask "Based on the research, what's the outlook?"
```

### 3. Backtesting Workflow
```bash
# Run prediction
python ask_pauls.py "Will ETH go up tomorrow?"

# Next day, mark outcome
python history_viewer.py resolve abc123 CORRECT

# Check Paul accuracy
python history_viewer.py leaderboard
```

---

**Need more help?** Check `docs/` directory for detailed feature documentation.
