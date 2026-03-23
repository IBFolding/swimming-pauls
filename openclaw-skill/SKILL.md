---
name: swimming-pauls
description: Run Swimming Pauls multi-agent prediction engine locally. Connect UI to local agent for 100% private, no-cloud simulations.
triggers:
  - swimming pauls
  - cast the pool
  - run pauls
  - connect pauls
  - local agent
role: specialist
scope: implementation
---

# Swimming Pauls Skill

Run 100+ AI agents on your machine for prediction markets, analysis, and decision-making.

## Quick Start

### Option 1: Unified Launcher (Recommended)
```bash
# Start both WebSocket agent and UI server
python start.py

# Or with custom settings
python start.py --pauls 100 --rounds 50 --port 8766 --ui-port 3006
```

### Option 2: Manual Start
```bash
# Terminal 1 - Start WebSocket agent
python local_agent.py

# Terminal 2 - Start UI server
cd ui && python -m http.server 3005
```

### Option 3: Via OpenClaw
```bash
# Ask OpenClaw to run a prediction
/openclaw run swimming-pauls "Will ETH reach $10k by end of 2025?"
```

## Usage

### From Telegram/Chat
Once the skill is configured, simply type:
```
/swimming-pauls Will Bitcoin hit $100k this year?
```

Or:
```
Ask the Pauls: Should I invest in AI stocks?
```

### Response Format
The skill returns:
- **Consensus**: BULLISH/BEARISH/NEUTRAL with confidence %
- **Stats**: Number of Pauls, rounds, question
- **Explorer Links**: Clickable links to view full results
  - 📊 Explorer - Detailed breakdown with Paul quotes
  - 🕸️ Network - Visualization of agent connections
  - 💬 Debate - Interactive debate network graph

### Example Output
```
🦷 SWIMMING PAULS CONSENSUS

🟢 BULLISH (73% confidence)

📊 Stats:
• Pauls: 100
• Rounds: 20
• Question: Will Bitcoin hit $100k this year?...

🔗 View Full Results:
• 📊 Explorer: http://localhost:3005/explorer.html?id=abc123
• 🕸️ Network: http://localhost:3005/visualize.html?id=abc123
• 💬 Debate: http://localhost:3005/debate_network.html?id=abc123
```

## Configuration

Add to your OpenClaw config:

```yaml
skills:
  swimming-pauls:
    path: /path/to/swimming_pauls
    default_pauls: 50
    default_rounds: 20
    auto_connect_ui: true
    ui_port: 3005
    ws_port: 8765
```

## Environment Variables

```bash
export PAULS_DEFAULT_COUNT=100      # Default number of Pauls
export PAULS_DEFAULT_ROUNDS=50      # Default number of rounds
export PAULS_WS_PORT=8765           # WebSocket port
export PAULS_UI_PORT=3005           # UI server port
```

## Requirements

- Python 3.9+
- Dependencies in `requirements.txt`:
  - websockets
  - psutil (optional, for system monitoring)

## Architecture

```
User Query (Telegram/CLI)
         ↓
   OpenClaw Skill
         ↓
   skill.py (WebSocket client)
         ↓
   local_agent.py (WebSocket server)
         ↓
   Multi-Agent Simulation
         ↓
   Result saved to data/results/{id}.json
         ↓
   Explorer links returned to user
         ↓
   User opens http://localhost:3005/explorer.html?id={id}
```

## Viewing Results

After a prediction completes, you can view results at:

1. **Explorer** (`explorer.html?id={id}`)
   - Full consensus breakdown
   - Individual Paul quotes
   - Vote distribution
   - Monte Carlo simulation results

2. **Visualization** (`visualize.html?id={id}`)
   - Agent network graph
   - Influence connections
   - Agreement/disagreement links

3. **Debate Network** (`debate_network.html?id={id}`)
   - Interactive D3.js force graph
   - Hover for Paul details
   - Key influencers ranked

## Troubleshooting

### "Connection refused" error
Make sure the local agent is running:
```bash
python start.py
```

### Port already in use
Change ports:
```bash
python start.py --port 8766 --ui-port 3006
```

### Results not showing in explorer
Check that `data/results/` directory exists and is writable:
```bash
ls -la data/results/
```

100% local. No cloud APIs. Your machine runs everything.
