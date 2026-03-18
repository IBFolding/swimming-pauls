---
name: swimming-pauls
description: "Multi-agent prediction engine with 100-700,000+ AI agents. Auto-installs on first run. 100% local - no cloud."
homepage: https://github.com/IBFolding/swimming-pauls
command: "~/.openclaw/workspace/skills/swimming-pauls/run.sh"
---

# 🦷 Swimming Pauls

**Auto-installing multi-agent prediction engine.**

## Quick Start

Just run:
```bash
openclaw run swimming-pauls
```

**On first run:** Automatically clones repo, installs deps, starts agent  
**On subsequent runs:** Just starts the agent (already installed)

## Chat Integration

Ask Swimming Pauls in any OpenClaw chat:

```
@swimming-pauls Will BTC hit $100K by end of year?
```

**Response includes:**
- 🦷 Consensus (BULLISH/BEARISH/NEUTRAL) with confidence %
- 💬 Key Paul perspectives (top 3 quotes)
- 📊 Stats (Pauls count, rounds, sentiment)
- 🔗 Links to view full results in explorer/visualization/debate pages

**Click any link to see YOUR prediction data** in the demo pages (they load real data via `?id=` parameter).

## What It Does

1. **Installs** (first time only)
   - Clones: `git clone https://github.com/IBFolding/swimming-pauls.git`
   - Installs: `pip3 install websockets httpx aiohttp`
   - All local, no cloud

2. **Starts Agent**
   - WebSocket server on ws://localhost:8765
   - HTTP results API on http://localhost:8080
   - Web UI at http://localhost:3005
   - Auto-generates connection ID

3. **Chat Integration**
   - Receives questions via OpenClaw skill
   - Runs multi-agent simulation
   - Returns formatted response with view links
   - Saves results for web visualization

## Features

- **Scale:** 100 - 700,000+ AI agents
- **Research:** Auto-scans web for current data
- **Visual:** Matrix, Monte Carlo, Knowledge Graph
- **Shareable:** Every prediction gets a unique ID + view URLs
- **Local:** 100% private, no cloud

## Viewing Results

Every prediction generates shareable links:
```
📈 View Full Results:
• Explorer: http://localhost:3005/explorer.html?id=abc123
• Visualization: http://localhost:3005/visualize.html?id=abc123  
• Debate Network: http://localhost:3005/debate_network.html?id=abc123
```

The demo pages automatically load real data when `?id=` is present, showing YOUR specific prediction instead of demo data.

## Files Installed

Location: `~/swimming-pauls/`
- `local_agent.py` - Main agent + WebSocket server
- `chat_interface.py` - Chat formatting + HTTP results API
- `ui/index.html` - Web interface
- `web_research.py` - Internet research
- `llm_client.py` - LLM integration

## Architecture

```
User in Chat
    ↓
OpenClaw Skill → chat_interface.py
    ↓
local_agent.py (WebSocket)
    ↓
Simulation runs → Result saved with ID
    ↓
Chat response with links
    ↓
User clicks link → HTTP API serves data
    ↓
Demo page loads real prediction data
```

## Update

```bash
cd ~/swimming-pauls
git pull
```

## Uninstall

```bash
rm -rf ~/swimming-pauls
rm -rf ~/.openclaw/workspace/skills/swimming-pauls
```

---

**Let the Pauls cook.** 🦷
