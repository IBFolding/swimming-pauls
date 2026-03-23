# Swimming Pauls v2.1 - Learning Edition

## 🚀 Quick Start (New!)

```bash
# First time setup
python setup.py

# Start everything (agent + UI)
python start.py

# Or run health check first
python health_check.py
```

Then open: http://localhost:3005

---

## What's New

### 🎓 Learning System
Swimming Pauls now **learns from outcomes**:

- **Auto-resolution**: Predictions automatically checked against market data
- **Paul accuracy tracking**: Individual track records for each Paul
- **Leaderboards**: Rankings by specialty and overall accuracy
- **Price history**: Historical data enables verifying directional predictions

**How it works:**
1. You ask a question → Pauls debate → Consensus reached
2. Price tracker records market data every 30 min
3. Auto-resolver checks if predictions came true
4. Leaderboard updates with Paul accuracy scores
5. Over time, high-accuracy Pauls get more influence

**Commands:**
```bash
python resolve_predictions.py --list      # View all predictions
python resolve_predictions.py --auto      # Resolve pending predictions
python leaderboard.py                     # View Paul rankings
python leaderboard.py --specialty         # Group by expertise
python price_tracker.py                   # Record current prices
python auto_resolver.py --daemon          # Run auto-checks hourly
```

---

### 🛠️ Better Onboarding

**Setup Wizard** (`python setup.py`)
- Checks Python version and dependencies
- Creates required directories
- Runs system diagnostics
- Guides first-time users

**Health Check** (`python health_check.py`)
```bash
python health_check.py              # Full diagnostic
python health_check.py --quick      # Quick status
python health_check.py --fix        # Auto-fix common issues
```

Checks:
- Python 3.9+ installed
- Dependencies available
- Directories writable
- Ports available
- Data integrity

**Demo Data** (`python generate_demo_data.py`)
```bash
python generate_demo_data.py --count 10   # Create sample predictions
```

New users can explore the UI immediately without running a simulation.

---

### 💬 Telegram/Discord Integration

Ask Swimming Pauls directly from chat:

```
/swimming-pauls Will Bitcoin hit $100k this year?

OR

Ask the Pauls: Should I buy ETH or SOL?
```

**Response includes:**
- Consensus (BULLISH/BEARISH/NEUTRAL) with confidence %
- Stats (Pauls count, rounds, question)
- **Explorer links** to view full results in browser

**Features:**
- Auto-starts local agent if not running
- Formatted markdown responses
- One-click access to visualizations

---

### 🎯 Unified Launcher

**One command starts everything:**

```bash
python start.py                    # Default: 50 Pauls, 20 rounds
python start.py --pauls 100        # More Pauls
python start.py --port 8766        # Custom ports
python start.py --no-ui            # Agent only
```

**What it does:**
1. Starts WebSocket agent on ws://localhost:8765
2. Starts UI server on http://localhost:3005
3. Monitors both processes
4. Clean shutdown on Ctrl+C

No more managing two terminals!

---

### 📊 New Visualization: Debate Network

**Interactive D3.js force graph** showing:
- Paul nodes (color-coded by sentiment)
- Influence connections (agreement = green, disagreement = red)
- Hover tooltips with Paul details and reasoning
- Draggable nodes
- Top influencers ranked

**Access:** http://localhost:3005/debate_network.html?id=YOUR_ID

---

### ⚙️ Configuration System

Create `config.yaml` to customize defaults:

```yaml
defaults:
  pauls: 100
  rounds: 50

server:
  websocket_port: 8765
  ui_port: 3005

auto_resolver:
  enabled: true
  interval_minutes: 60

price_tracker:
  symbols:
    - BTC
    - ETH
    - SOL
```

---

### 💾 Data Export

Backup and analyze your predictions:

```bash
python export_data.py                    # Export everything
python export_data.py --predictions      # Predictions only
python export_data.py --leaderboard      # Leaderboard only
python export_data.py --format csv       # CSV format
```

Exports to:
- `predictions_export_YYYYMMDD.json/csv`
- `leaderboard_export_YYYYMMDD.json/csv`
- `export_YYYYMMDD/` (full backup)

---

## Complete Command Reference

| Command | Purpose |
|---------|---------|
| `python setup.py` | First-time setup wizard |
| `python start.py` | Start agent + UI server |
| `python health_check.py` | System diagnostics |
| `python generate_demo_data.py` | Create demo predictions |
| `python resolve_predictions.py --list` | View prediction status |
| `python resolve_predictions.py --auto` | Resolve pending predictions |
| `python leaderboard.py` | View Paul rankings |
| `python price_tracker.py` | Record market prices |
| `python export_data.py` | Backup predictions |

---

## Architecture Overview

```
User Query (Telegram/Web)
         ↓
   OpenClaw Skill / UI
         ↓
   WebSocket (ws://localhost:8765)
         ↓
   Local Agent (local_agent.py)
         ↓
   Multi-Agent Simulation (50-1000 Pauls)
         ↓
   Results Saved → data/results/{id}.json
         ↓
   Explorer Links Returned
         ↓
   User Views Results in Browser
         ↓
   [Background] Price Tracker → Price History
         ↓
   [Background] Auto-Resolver → Marks Outcomes
         ↓
   [Background] Leaderboard → Accuracy Scores
```

---

## What's Coming (V2.2)

- **Mac Mini Infrastructure**: 24/7 cloud predictions
- **Paul Marketplace**: Buy/sell high-accuracy Pauls
- **$PAUL Token**: Staking, credits, governance
- **Social Media**: Pauls post to Twitter/Telegram
- **Mobile App**: iOS/Android native apps
- **API**: REST API for external integrations

---

## Full Changelog

**Added:**
- `setup.py` - First-time setup wizard
- `start.py` - Unified launcher
- `config.example.yaml` / `config_loader.py` - Configuration system
- `health_check.py` - System diagnostics
- `export_data.py` - Data backup/export
- `generate_demo_data.py` - Demo predictions
- `resolve_predictions.py` - Prediction resolution
- `auto_resolver.py` - Auto-resolution daemon
- `leaderboard.py` - Paul accuracy rankings
- `price_tracker.py` - Historical price recording
- `openclaw-skill/skill.py` - Telegram/Discord bot
- `ui/debate_network.html` - Interactive debate visualization

**Changed:**
- Updated `.gitignore` to include UI HTML files
- Updated `SKILL.md` with new commands and usage

---

**100% Local. No Cloud. Your Data.**

Let the Pauls cook. 🦷
