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

## What It Does

1. **Installs** (first time only)
   - Clones: `git clone https://github.com/IBFolding/swimming-pauls.git`
   - Installs: `pip3 install websockets httpx aiohttp`
   - All local, no cloud

2. **Starts Agent**
   - WebSocket server on ws://localhost:8765
   - Web UI at http://localhost:3005
   - Auto-generates connection ID

3. **Ready to Use**
   - Open browser to http://localhost:3005
   - Click "Connect Local"
   - Ask questions, get predictions

## Features

- **Scale:** 100 - 700,000+ AI agents
- **Research:** Auto-scans web for current data
- **Visual:** Matrix, Monte Carlo, Knowledge Graph
- **Local:** 100% private, no cloud

## Files Installed

Location: `~/swimming-pauls/`
- `local_agent.py` - Main agent
- `ui/index.html` - Web interface
- `web_research.py` - Internet research
- `llm_client.py` - LLM integration

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
