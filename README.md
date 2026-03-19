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

## 🎯 What You Get

### 🐟 Swarm Intelligence
**[1000+ Paul Personas](PAULS_EXTENDED.md)** - Fully tested and documented. Each Paul has:
- Unique profession (trader, doctor, engineer, artist, etc.)
- Distinct trading style (scalper, swing, position, etc.)
- Risk profile (conservative to degen)
- Specialty domains (DeFi, NFT, Macro, Tech, etc.)
- Backstory and catchphrase

From Wall Street quants to digital artists, doctors to engineers—diverse perspectives create better predictions.

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

- **Full history** - Every question, every Paul vote
- **Paul accuracy** - Which Pauls are actually right?
- **Win streaks** - Who's hot right now?
- **Outcome tracking** - Mark predictions CORRECT/INCORRECT
- **Export data** - JSON export for analysis

```bash
# View Paul leaderboard
python history_viewer.py leaderboard

# See recent predictions  
python history_viewer.py recent

# Check specific Paul's history
python history_viewer.py paul "Visionary Paul"

# Mark prediction outcome
python history_viewer.py resolve abc123 CORRECT

# View overall stats
python history_viewer.py stats
```

**100% local** - Your prediction history stays on your machine.

---

## 🕸️ Debate Network Visualization

**Watch persuasion flow in real-time:**

- **Interactive D3.js graph** - Nodes = Pauls, Edges = persuasion
- **Temporal slider** - See round-by-round evolution
- **Play animation** - Watch consensus form
- **Click nodes** - See who convinced whom
- **Zoom & pan** - Scroll to zoom, drag to pan
- **Size = Influence** - Bigger nodes convinced more Pauls
- **Color = Sentiment** - Green/Yellow/Red positioning

**Live demo:** https://swimmingpauls.vercel.app/debate_network.html

---

## 🛠️ Custom Skills API

**Build your own skills for Pauls:**

```python
# skills/custom/my_weather_skill.py
from swimming_pauls.skills import Skill, SkillMetadata, SkillResult

class WeatherSkill(Skill):
    metadata = SkillMetadata(
        name="weather_check",
        description="Get local weather",
        best_for=["Farmer Paul", "Travel Paul"]
    )
    
    async def execute(self, location: str) -> SkillResult:
        # Your implementation
        return SkillResult(success=True, data={"temp": 72})
```

**CLI:**
```bash
# Create new skill template
python skills.py create my_skill "My custom skill"

# List all skills
python skills.py list

# Assign skill to Paul
python skills.py assign "Farmer Paul" weather_check
```

---

## 🚀 Get Started

### ⚡ Easiest: OpenClaw CLI

```bash
# One command to rule them all
openclaw run swimming-pauls

# Or add the skill first
openclaw skills add swimming-pauls
openclaw run swimming-pauls
```

### 💻 Manual Install

```bash
# Clone
git clone https://github.com/IBFolding/swimming-pauls.git
cd swimming-pauls

# Install
pip install -r requirements.txt

# Run WebSocket agent
python local_agent.py

# In another terminal, start HTTP server
python -m http.server 3005

# Open your browser
open http://localhost:3005
```

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
├── local_agent.py          # WebSocket server
├── skill_bridge.py         # OpenClaw integration
├── web_intelligence.py     # Web scraping/search
├── skills.py              # Custom skill API framework
├── prediction_history.py   # SQLite tracking
├── debate_tracker.py       # Persuasion flow tracking
├── simulation.py           # Core multi-agent engine
├── agent.py               # Individual Paul logic
├── persona_factory.py      # Generate 1000+ Pauls
├── knowledge_graph.py      # Entity relationships
├── history_viewer.py       # CLI for viewing history
├── PAULS.md               # First 160 Paul directory
├── PAULS_EXTENDED.md      # Full 1000 Paul directory
├── ROADMAP.md             # Future plans
├── HANDOFF.md             # Session continuity
└── pumpfun-landing/       # Landing page + demos
    ├── index.html          # Tab-based landing page
    ├── explorer.html       # Prediction results demo
    ├── visualize.html      # Paul network visualization
    ├── debate_network.html # Temporal debate flow
    └── paul.jpg            # Logo
```

---

## 🚀 What's Next (V2 Roadmap)

### ✅ Recently Shipped
- **Temporal Memory** - Pauls update beliefs dynamically over time
- **Dual Platform** - Parallel simulations for higher confidence consensus  
- **ReportAgent** - Automated report generation with skill integration
- **GraphRAG** - Structured knowledge extraction from documents

### 📅 Coming Soon
- **Extended Locations** - Town Hall, Bar, Card Room, Social Media
- **Solana Integration** - Verified on-chain data skills
- **Mac Mini Infrastructure** - 24/7 cloud simulation
- **$PAULS Token** - Stake for prediction credits
- **Skill Marketplace** - Buy/sell custom Paul skills

---

## 🎮 Try the Demos

No installation required:

- **Landing Page:** https://swimmingpauls.vercel.app
- **Explorer:** Full prediction results
- **Visualization:** 1000+ Pauls real-time graph
- **Debate Network:** Temporal persuasion flow

---

## 🔒 100% Local. Zero Cloud.

**Private:** All computation happens on your machine.

**Fast:** 50 agents deliberating is under 10 seconds locally.

**Unlimited:** No rate limits. Your hardware is the only limit.

---

**Built by Howard | 100% Local | No Cloud**

*"Let the Pauls cook."* 🦷
