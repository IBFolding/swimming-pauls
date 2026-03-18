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

**Swimming Pauls** is a **multi-agent prediction engine** that runs entirely on your machine. No cloud. No API keys. No data leaves your computer.

Ask a question. 10, 100, or 500+ diverse AI personas debate and predict outcomes. They argue, deliberate, and reach consensus. Each Paul has unique expertise—from quant analysts to visionary thinkers.

---

## 🎯 What You Get

### 🐟 Swarm Intelligence
**[500+ Paul Personas](PAULS.md)** - View the complete directory. Each Paul has:
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

### 🔌 OpenClaw Skill Integration
Pauls now have access to OpenClaw's ecosystem of skills:
- **💰 Crypto prices** - Real-time token data
- **📈 Yahoo Finance** - Stock prices and earnings
- **🎯 Polymarket** - Prediction market odds
- **📰 News Summarizer** - Real-time sentiment analysis
- **🔷 Base blockchain** - On-chain metrics
- **📊 Market Analysis** - Comprehensive financial research
- **🕷️ Web Scraper** - Data from any source

Each Paul uses skills relevant to their specialty. Trader Paul pulls crypto prices. Professor Paul checks financial data. Visionary Paul scans prediction markets.

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

This will:
1. Clone the repo (first time only)
2. Install dependencies
3. Start the local agent
4. Open your browser automatically
5. Show Connection ID for linking to the UI

Then:
1. Type your question (e.g., "Will ETH reach $10K?")
2. The system prompts: **"How many Pauls?"** (10-500+, max depends on your hardware)
3. The system prompts: **"How many rounds?"** (10-1000, more rounds = deeper deliberation)
4. Watch the Pauls debate in real-time
5. Get consensus + confidence score

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

### 🔗 Connect to UI

1. Go to https://swimmingpauls.vercel.app
2. Click "🔌 Connect Local"
3. Enter the Connection ID from your terminal
4. Ask questions, get predictions

**Local LLM Options:**
- **Ollama:** `ollama run llama3` (default: localhost:11434)
- **LM Studio:** Start server (default: localhost:1234)
- **LocalAI:** Any OpenAI-compatible endpoint

---

## 🐟 Meet the Pauls

Not just one Paul. **An army of Pauls.** Each with unique personality, expertise, and biases.

| Paul | Emoji | Specialty | Trading Style | Best Tools |
|------|-------|-----------|---------------|------------|
| **Visionary Paul** | 🔮 | Disruptive Innovation | Long-term | Polymarket, News |
| **Professor Paul** | 👨‍🏫 | Macro Research | Systematic | Yahoo Finance, Market Analysis |
| **Skeptic Paul** | 🤨 | Risk Assessment | Defensive | All tools for verification |
| **Quant Paul** | 📊 | Quantitative Analysis | Systematic | Yahoo Finance, Technicals |
| **Trader Paul** | 📈 | Market Timing | Active | Crypto prices, Order flow |
| **Whale Paul** | 🐋 | Institutional Flow | Strategic | On-chain data, Block explorers |
| **Degen Paul** | 🎰 | High Risk | Aggressive | Crypto prices, Social sentiment |
| **Value Paul** | 💎 | Fundamental Analysis | Patient | Financial data, Earnings |

*And 32+ more unique personas...*

---

## 🛠️ Capabilities

### 🔮 Prediction Mode (Default)
Ask anything. Get consensus forecasting with confidence scores.

**Example:**
```
Question: "Will AI eliminate more jobs than it creates by 2030?"
Pauls: 100
Rounds: 10
Result: NEUTRAL • 74% Confidence • Weak Consensus
```

**Output includes:**
- Vote Distribution (Bullish/Neutral/Bearish breakdown)
- Sentiment Analysis (Raw score, interpretation, directional bias)
- Market Regime (Trending, Range Bound, etc.)
- Risk Metrics (Consensus strength, uncertainty level, volatility)
- Time Analysis (Convergence speed, stability score)
- Knowledge Graph (26 entities, relationship insights)
- Agent Perspectives (Each Paul's reasoning with confidence)
- Skill Data (Live prices if relevant)

### 📢 PR Simulation
Test crisis responses before they happen.

### 📊 Marketing Testing
A/B test campaigns with simulated audiences.

### 📖 Story Analysis
Predict plot developments and character arcs.

### 🔬 Research Design
Calculate power analysis and sample sizes.

---

## 📊 What the Results Look Like

### Consensus Header
```
🦷 NEUTRAL
74% Confidence
WEAK CONSENSUS badge
Simulation complete. 100 Pauls reached consensus after 10 rounds.
```

### Vote Distribution
```
Bullish:  35% (35 Pauls) ████████░░░░░░░░░░░░  Avg Confidence: 78%
Neutral:  38% (38 Pauls) █████████░░░░░░░░░░░  Avg Confidence: 70%
Bearish:  27% (27 Pauls) ██████░░░░░░░░░░░░░░  Avg Confidence: 72%
```

### Agent Perspective Example
```
🔮 Visionary Paul
Disruptive Innovation • Long-term
[ BULLISH 82% ]

"The narrative is shifting bullish. Early adopters see AI creating 
more jobs than it eliminates—this is where alpha lives."

💡 Knows: AI Sector, Innovation, Tech Stocks | Memory: 68% accuracy
```

---

## 🔒 100% Local. Zero Cloud.

**Private:** All computation happens on your machine. Your questions never leave.

**Fast:** No network latency. 50 agents deliberating is under 10 seconds locally.

**Unlimited:** No rate limits. Query as much as you want. Your hardware is the only limit.

---

## 🎮 Try the Demos

No installation required:

- **Explorer Demo:** See full prediction results with agent reasoning
- **Visualization Demo:** Watch 500+ Pauls debate in real-time (click nodes to see perspectives)

Then run locally to get YOUR predictions with live data.

---

## 📁 Project Structure

```
swimming-pauls/
├── local_agent.py          # WebSocket server for UI connection
├── skill_bridge.py         # OpenClaw skill integration
├── simulation.py           # Core multi-agent simulation
├── agent.py                # Individual Paul logic
├── persona_factory.py      # Generate unique personas
├── knowledge_graph.py      # Entity relationships
├── data_feeds_local.py     # Local data sources
├── web_research.py         # Internet search integration
├── advanced.py             # Monte Carlo, sensitivity analysis
├── crisis_pr_simulator.py  # PR crisis simulation
├── marketing_simulator.py  # Marketing campaign testing
├── story_deduction.py      # Narrative analysis
├── academic_research.py    # Research design
├── ui/
│   ├── index.html          # Main UI (connects to local agent)
│   ├── explorer.html       # Results explorer
│   └── visualize.html      # Real-time visualization
└── pumpfun-landing/        # Landing page + demos
    ├── index.html
    ├── explorer.html
    └── visualize.html
```

---

## 🤝 How It Works

1. **Ask Anywhere** - Terminal, Telegram, or web UI
2. **Configure Pool** - System asks: "How many Pauls?" and "How many rounds?"
3. **Swarm Deliberates** - Pauls debate using local knowledge graph + OpenClaw skills
4. **Get Consensus** - Direction, confidence, sentiment, and full transparency
5. **Explore Deeply** - Click explorer to see agent reasoning, relationships, risk metrics

---

## 🛠️ Requirements

- Python 3.9+
- 4GB+ RAM (for 100 Pauls)
- Optional: Local LLM (Ollama, LM Studio, LocalAI)
- Optional: OpenClaw CLI for skill integration

---

## 📝 License

MIT - Build your own Paul army.

---

**Built by Howard | 100% Local | No Cloud**

*"Let the Pauls cook."* 🦷
