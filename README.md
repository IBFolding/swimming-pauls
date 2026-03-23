# 🦷 Swimming Pauls

> **"Let the Pauls cook."**
> 
> *"I created Swimming Pauls after watching my friend Paul—an eccentric quant trader—correctly predict three consecutive market crashes by simply 'taking his gut.' His gut wasn't magic; it was pattern recognition from 20 years of staring at charts. I realized: what if I could bottle that intuition? Not one Paul, but an army of Pauls—each with different expertise, biases, and blindspots—debating until consensus emerges. The Pauls don't predict the future. They surface the truth you're too biased to see."*
> 
> **— Howard, Creator**

**🌐 Live Demos:**
- **Landing Page:** https://swimmingpauls.vercel.app
- **Explorer Demo:** https://swimmingpauls.vercel.app/explorer.html?id=demo
- **Visualization Demo:** https://swimmingpauls.vercel.app/visualize.html
- **Debate Network:** https://swimmingpauls.vercel.app/debate_network.html

**Swimming Pauls** is a **multi-agent prediction engine** that runs entirely on your machine. No cloud. No API keys. No data leaves your computer.

Ask a question. 10, 100, or 500+ diverse AI personas debate and predict outcomes. They argue, deliberate, and reach consensus. Each Paul has unique expertise—from quant analysts to visionary thinkers.

---

## 🚀 Quick Start (New in v2.1!)

```bash
# Clone and enter directory
git clone https://github.com/IBFolding/swimming-pauls.git
cd swimming-pauls

# First-time setup (installs deps, checks system)
python setup.py

# Start everything (WebSocket agent + UI server)
python start.py

# Open browser
open http://localhost:3005
```

**That's it!** The setup wizard handles everything. No manual configuration needed.

---

## 🎯 What You Get

### 🐟 Swarm Intelligence
**[1000+ Paul Personas](PAULS_EXTENDED.md)** - View the complete directory. Each Paul has:
- Unique profession (trader, doctor, engineer, artist, etc.)
- Distinct trading style (scalper, swing, position, etc.)
- Risk profile (conservative to degen)
- Specialty domains (DeFi, NFT, Macro, Tech, etc.)
- Backstory and catchphrase

From Wall Street quants to digital artists, doctors to engineers—diverse perspectives create better predictions.

### 🎓 Learning System (v2.1)
**Pauls get smarter over time:**

- **Auto-resolution** - Predictions automatically checked against market data
- **Accuracy tracking** - Individual track records for each Paul
- **Leaderboards** - Rankings by specialty and overall accuracy
- **Price history** - Historical data enables verifying predictions

The longer you run it, the smarter the Pauls get.

### 🧠 Knowledge Graph  
26 market entities with relationship mapping. AI Sector, Labor Market, Automation, GDP, Tech Stocks, Productivity, Regulation, Innovation—and their interconnections.

### 📊 Deep Analysis
Sentiment scoring, risk metrics, market regime detection, and individual agent reasoning—all transparent.

### 🔌 Data Sources (100% Local)

**Layer 1: OpenClaw Skills (structured data)**
- **💰 Crypto prices** - Real-time token data
- **📈 Yahoo Finance** - Stock prices and earnings
- **🎯 Polymarket** - Prediction market odds
- **📰 News Summarizer** - Real-time sentiment analysis
- **🔷 Base blockchain** - On-chain metrics
- **📊 Market Analysis** - Comprehensive financial research

**Layer 2: Web Intelligence (unstructured research)**
- **🔍 Multi-engine search** - DuckDuckGo, SearXNG, Bing aggregated
- **📖 Wikipedia** - Instant topic summaries
- **💬 Reddit** - Community discussions and sentiment
- **🐙 GitHub** - Dev activity and project metrics
- **📈 Trend analysis** - Volume, velocity, sentiment scoring
- **📰 Article scraping** - Full text extraction
- **📡 RSS feeds** - Latest news from any source

**Layer 3: Custom Skills (user-defined)**
- Create your own skills in Python
- Attach to specific Pauls
- Share with community
- Monetize via Skill Marketplace (V2)

**Each Paul uses the right tools for their specialty.**

---

## 🏆 Prediction History & Leaderboards

**Every prediction tracked locally in SQLite:**

```bash
# View Paul accuracy leaderboard
python leaderboard.py

# Group by specialty
python leaderboard.py --specialty

# Check specific Paul's track record
python leaderboard.py --paul "Visionary Paul"

# View all predictions
python resolve_predictions.py --list

# Auto-resolve pending predictions
python resolve_predictions.py --auto

# Export for analysis
python export_data.py --predictions --format csv
```

**Sample leaderboard output:**
```
🏆 PAUL ACCURACY LEADERBOARD
Rank   Name                 Specialty       Correct  Total  Accuracy  
🥇     Visionary Paul       Long-term       12       15     80%      
🥈     Trader Paul          Timing          18       24     75%      
🥉     Quant Paul           Data            9        12     75%      
```

**100% local** - Your prediction history stays on your machine.

---

## 💬 Telegram/Discord Integration (v2.1)

Ask Swimming Pauls directly from chat:

```
/swimming-pauls Will Bitcoin hit $100k this year?

OR

Ask the Pauls: Should I buy ETH or SOL?
```

**Response includes:**
- Consensus (BULLISH/BEARISH/NEUTRAL) with confidence %
- Stats (Pauls count, rounds)
- **Clickable explorer links** to view full results

**Features:**
- Auto-starts local agent if not running
- Formatted markdown responses
- One-click access to visualizations

---

## 🕸️ Debate Network Visualization

**Watch persuasion flow in real-time:**

- **Interactive D3.js graph** - Nodes = Pauls, Edges = persuasion
- **Color-coded nodes** - Green (bullish), Red (bearish), Yellow (neutral)
- **Agreement/disagreement links** - Green = same direction, Red = opposite
- **Hover tooltips** - Paul details and reasoning
- **Draggable nodes** - Rearrange the network
- **Top influencers** - Ranked by impact

**Access:** http://localhost:3005/debate_network.html?id=YOUR_ID

---

## 🛠️ Complete Command Reference

### Setup & System
```bash
python setup.py                    # First-time setup wizard
python start.py                    # Start agent + UI server
python start.py --pauls 100        # Start with 100 Pauls
python health_check.py             # System diagnostics
python health_check.py --fix       # Auto-fix issues
```

### Predictions
```bash
# Via OpenClaw skill (Telegram/Discord)
/swimming-pauls "Your question here"

# Via CLI
python openclaw-skill/skill.py "Will BTC go up?"

# Generate demo data
python generate_demo_data.py --count 10
```

### Learning & Analytics
```bash
python leaderboard.py                    # View Paul rankings
python leaderboard.py --specialty        # Group by specialty
python resolve_predictions.py --list     # View prediction status
python resolve_predictions.py --auto     # Resolve pending predictions
python price_tracker.py                  # Record current prices
python auto_resolver.py --daemon         # Run auto-checks hourly
```

### Data Management
```bash
python export_data.py                    # Export everything
python export_data.py --predictions      # Predictions only
python export_data.py --leaderboard      # Leaderboard only
python export_data.py --format csv       # CSV format
```

---

## ⚙️ Configuration (Optional)

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

Copy from `config.example.yaml` to get started.

---

## 💻 Hardware Requirements & Capacity

**Tested on MacBook M4 (16GB RAM):**
- **10,000 Pauls** initialized in 0.21 seconds
- **Memory usage:** ~100MB for 10,000 Pauls (~10KB per Paul)
- **Conservative limit:** 5,000-7,500 Pauls for live simulation
- **Maximum tested:** 10,000+ Pauls

**What this means:**
- **Laptop (8GB):** 1,000-2,000 Pauls
- **Mac Mini M4 (16GB):** 5,000-10,000 Pauls  
- **Mac Mini Cluster:** 50,000+ Pauls
- **Workstation (64GB+):** 50,000-100,000 Pauls

> **Note:** Memory isn't the limiting factor—simulation time is. Running 10,000 Pauls through 20 rounds means 200,000 individual predictions (each Paul reasons, checks memory, updates beliefs). That takes CPU time regardless of RAM. With 10,000 Pauls, a full simulation might take 30-60 seconds vs 5 seconds with 100 Pauls.

Run your own test: `python test_capacity.py`

---

## 📁 Project Structure

```
swimming-pauls/
├── start.py                # 🆕 Unified launcher (v2.1)
├── setup.py                # 🆕 First-time setup wizard (v2.1)
├── health_check.py         # 🆕 System diagnostics (v2.1)
├── local_agent.py          # WebSocket server
├── skill_bridge.py         # OpenClaw integration
├── web_intelligence.py     # Web scraping/search
├── skills.py              # Custom skill API framework
├── prediction_history.py   # SQLite tracking
├── debate_tracker.py       # Persuasion flow tracking
├── resolve_predictions.py  # 🆕 Prediction resolution (v2.1)
├── leaderboard.py          # 🆕 Paul accuracy rankings (v2.1)
├── price_tracker.py        # 🆕 Historical prices (v2.1)
├── auto_resolver.py        # 🆕 Auto-resolution daemon (v2.1)
├── export_data.py          # 🆕 Data backup/export (v2.1)
├── generate_demo_data.py   # 🆕 Demo predictions (v2.1)
├── simulation.py           # Core multi-agent engine
├── agent.py               # Individual Paul logic
├── persona_factory.py      # Generate 1000+ Pauls
├── knowledge_graph.py      # Entity relationships
├── history_viewer.py       # CLI for viewing history
├── config.example.yaml     # 🆕 Example configuration (v2.1)
├── PAULS.md               # First 160 Paul directory
├── PAULS_EXTENDED.md      # Full 1000 Paul directory
├── ROADMAP.md             # Future plans
├── HANDOFF.md             # Session continuity
└── ui/                    # Web interface
    ├── index.html         # Main UI
    ├── explorer.html      # Prediction results
    ├── visualize.html     # Paul network
    └── debate_network.html # 🆕 Interactive debate (v2.1)
```

---

## 📖 Documentation

- **[RELEASE_NOTES_v2.1.md](RELEASE_NOTES_v2.1.md)** - What's new in v2.1
- **[COMMANDS.md](COMMANDS.md)** - Complete CLI reference with all commands
- **[PAPER_TRADING.md](PAPER_TRADING.md)** - Paper trading system guide
- **[SOCIAL_MEDIA.md](SOCIAL_MEDIA.md)** - Social media system
- **[docs/](docs/)** - Detailed feature documentation
- **[HANDOFF.md](HANDOFF.md)** - Project status and session continuity

---

## 🚀 What's Next (V2 Roadmap)

### ✅ Recently Shipped (v2.1)
- **Setup Wizard** - One-command first-time setup
- **Unified Launcher** - `python start.py` starts everything
- **Learning System** - Auto-resolution, accuracy tracking, leaderboards
- **Telegram Integration** - Ask Pauls from chat
- **Health Check** - System diagnostics and auto-fix
- **Data Export** - Backup to JSON/CSV
- **Demo Data** - Explore without running simulations
- **Debate Network** - Interactive D3 visualization

### 📅 Coming Soon (v2.2)
- **Mac Mini Infrastructure** - 24/7 cloud simulation with $PAUL credits
- **Social Media Integration** - Pauls post predictions to Twitter/Telegram
- **Paul Marketplace** - Buy/sell high-accuracy Pauls
- **Mobile App** - iOS/Android native apps
- **API** - REST API for external integrations

---

## 🎮 Try the Demos

No installation required:

- **Landing Page:** https://swimmingpauls.vercel.app
- **Explorer:** Full prediction results
- **Visualization:** 1000+ Pauls real-time graph
- **Debate Network:** Interactive persuasion flow

---

## 🔒 100% Local. Zero Cloud.

**Private:** All computation happens on your machine.

**Fast:** 50 agents deliberating is under 10 seconds locally.

**Unlimited:** No rate limits. Your hardware is the only limit.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Built by Howard | 100% Local | No Cloud**

*"Let the Pauls cook."* 🦷
