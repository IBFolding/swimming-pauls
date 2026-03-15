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

```bash
# Start local agent
openclaw run swimming-pauls

# Or with options
openclaw run swimming-pauls --pauls 100 --rounds 50
```

## What It Does

Spawns the Swimming Pauls local agent which:
1. Starts WebSocket server on ws://localhost:8765
2. Runs multi-agent simulations using local AI models
3. Connects to the UI at http://localhost:3005
4. Returns consensus predictions with confidence scores

## Configuration

Add to your OpenClaw config:

```yaml
skills:
  swimming-pauls:
    path: /path/to/swimming_pauls
    default_pauls: 50
    default_rounds: 100
    auto_connect_ui: true
```

## Usage

### Start Local Agent
```
/openclaw run swimming-pauls
```

### Start with Custom Settings
```
/openclaw run swimming-pauls --pauls 200 --rounds 500
```

### Connect UI to Existing Agent
```
/openclaw run swimming-pauls --connect-only
```

## Requirements

- Python 3.9+
- See swimming_pauls/requirements.txt

## Architecture

```
User Query → OpenClaw Skill → local_agent.py → WebSocket → UI
                                        ↓
                                   Multi-Agent Simulation
                                        ↓
                                   Consensus Result
```

100% local. No cloud APIs. Your machine runs everything.
