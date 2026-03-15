# 🦷 Swimming Pauls

> **"Let the Pauls cook."**
>
> Multi-agent prediction engine. 100% local. No cloud.

![Swimming Pauls](ui/paul.jpg)

**🌐 Live Demo:** https://swimming-pauls-deploy.vercel.app

**Swimming Pauls** is a **multi-agent prediction pool** that simulates hundreds or thousands of AI personas debating and predicting outcomes. Born on Sunset Boulevard in a self-driving car while listening to Swimming Paul and texting OpenClaw.

Ask a question. 100, 1000, or even 700,000+ Pauls argue about it. They debate, deliberate, and reach consensus.

---

## 🎯 Features

- 🎭 **Hundreds of Personas** - From 6 archetypes to 700,000+ unique perspectives
- 🌐 **Web Research** - Pauls automatically search the internet for current data before predicting
- 🔮 **Monte Carlo Simulation** - 1000-run probability distributions
- 📊 **Sensitivity Analysis** - Which variables actually matter
- 🧠 **Knowledge Graph** - Semantic entity extraction and relationships
- 🔲 **Paul Matrix** - Visual consensus map of all agents
- 📉 **Backtesting** - Historical accuracy validation
- 📢 **PR Simulation** - Test crisis responses before they happen
- 📊 **Marketing Testing** - A/B test campaigns with simulated audiences
- 📖 **Story Analysis** - Predict plot developments and character arcs
- 🔬 **Research Design** - Calculate power analysis and sample sizes
- 📎 **Context Upload** - Images, PDFs, links for analysis
- 🎨 **Custom Pauls** - Create your own personas
- 📥 **Export Results** - TSV format for Excel/sorting
- 🔌 **Local Agent** - WebSocket connection to Python backend
- 🎮 **Demo Mode** - Test without installing Python
- 💾 **100% Local** - No APIs, no cloud, no data leaves your machine

---

## 🚀 Quick Start

### Option 1: Live Demo (Fastest)
🌐 **https://swimming-pauls.vercel.app**

1. Select your mode tab (Prediction, PR Sim, Marketing, Story, Research)
2. Type a question / enter parameters
3. Click "🐟 CAST THE POOL 🐟"
4. The Pauls will debate and reach consensus

*Note: Demo mode runs entirely in browser. Connect local agent for LLM-powered predictions.*

### Option 2: Local Agent with LLM (Full Power)
```bash
# Clone the pool
git clone https://github.com/IBFolding/swimming-pauls.git
cd swimming-pauls

# Install dependencies
pip install -r requirements.txt

# Start local agent (connects to your local LLM)
python local_agent.py

# Open https://swimming-pauls-deploy.vercel.app
# Click "🔌 Connect Local" and enter the Connection ID shown in terminal
```

**Local LLM Options:**
- **Ollama:** `ollama run llama3` (default: localhost:11434)
- **LM Studio:** Start server (default: localhost:1234)
- **LocalAI:** Any OpenAI-compatible endpoint

### Option 3: OpenClaw Skill (One Command)

If you have OpenClaw installed:

```bash
# Run it (auto-installs on first use)
openclaw run swimming-pauls
```

This will:
1. Clone the repo (first time only)
2. Install dependencies
3. Start the local agent with LLM support
4. Open your browser automatically
5. Show Connection ID for linking to the UI

---

## 🐟 Meet the Pauls

Not just 6 Pauls. **Hundreds. Thousands. Up to 700,000+.** Each with unique personality and perspective.

### The 6 Archetypes (Examples of Many)

| Paul | Emoji | Style | Strength |
|------|-------|-------|----------|
| **Professor Paul** | 👨‍🏫 | Academic, data-driven | Pattern recognition, regression analysis |
| **Trader Paul** | 📈 | Market-focused, reactive | Order flow, timing, risk/reward |
| **Skeptic Paul** | 🤨 | Contrarian, cautious | Blindspot detection, tail risk analysis |
| **Visionary Paul** | 🔮 | Long-term, optimistic | Future casting, paradigm shifts |
| **Whale Paul** | 🐋 | Institutional, strategic | Liquidity analysis, smart money flows |
| **Degen Paul** | 🎰 | Chaotic, YOLO energy | Market sentiment, meme momentum |

### Plus 100+ More Professions

Chef Paul 👨‍🍳, Lawyer Paul ⚖️, Doctor Paul 🏥, Engineer Paul 🔧, Artist Paul 🎨, Musician Paul 🎵, Writer Paul ✍️, Athlete Paul 🏃, Teacher Paul 📚, Nurse Paul 👩‍⚕️, Pilot Paul ✈️, Scientist Paul 🔬, Farmer Paul 🌾, Carpenter Paul 🔨, and many more...

**Scale:** 10 → 1,000,000+ Pauls. Your hardware is the limit.

---

## 📊 Output Sections

After casting the pool, you get:

### 1. Consensus Header
- Direction (BULLISH / BEARISH / NEUTRAL)
- Confidence percentage
- Summary message

### 2. Statistics
- Number of rounds
- Number of Pauls
- Sentiment score

### 3. Individual Paul Perspectives
Each Paul provides a detailed, context-aware response with confidence level.

### 4. Key Insights
Synthesized takeaways from the collective debate.

### 5. Monte Carlo Simulation
1000-run probability distribution across bullish/neutral/bearish outcomes.

### 6. Sensitivity Analysis
Impact scores showing which factors most affect the outcome:
- Market Sentiment
- Fundamentals
- Regulation
- Competition

### 7. Knowledge Graph
- Entity extraction count
- Relationship mapping
- Emergent pattern detection
- Key concept tags

### 8. Backtesting Results
Historical performance metrics:
- Accuracy rate
- Average return
- Sharpe ratio
- Max drawdown

---

## 🎯 Prediction Modes

Swimming Pauls isn't just for financial predictions. Choose your mode:

### 🔮 Prediction (Default)
Ask anything. Market moves, event outcomes, future trends. The Pauls analyze from every angle.

### 📢 PR Simulation
Test crisis scenarios before they happen:
- Enter crisis headline
- Draft company response
- Simulate 24-hour social media reaction
- See sentiment breakdown by platform
- Get recommendations on handling

### 📊 Marketing Testing
A/B test campaigns before launch:
- Enter product name
- Create Variant A and B headlines
- Simulate 12-week campaign
- See predicted revenue for each variant
- Know which campaign wins before spending

### 📖 Story Analysis
Analyze narratives and predict plot developments:
- Enter story premise
- Select genre (Mystery, Romance, Thriller, Sci-Fi, Fantasy)
- Get predicted plot points
- See likely ending with confidence
- Identify major themes

### 🔬 Research Design
Design experiments with proper power analysis:
- Enter research question
- Define null hypothesis
- Select experiment type (RCT, A/B Test, Longitudinal)
- Get sample size calculations
- See methodology recommendations

---

## 🚀 Scale: Why Hundreds of Pauls?

**Traditional Prediction:** 1 expert opinion  
**Polling:** 10-100 human votes  
**Swimming Pauls:** 100 - 700,000+ AI agents

### Why So Many?

- **Wisdom of Crowds** - More perspectives = better consensus
- **Diverse Expertise** - Chef sees different patterns than Lawyer
- **Bias Cancellation** - Optimists and pessimists balance out
- **Tail Risk Detection** - Skeptics catch what others miss
- **Confidence Calibration** - Agreement across 1000s = high confidence

### Each Paul Is Unique

Every agent has:
- **Unique personality** - Analytical, emotional, contrarian, etc.
- **Individual memory** - Remembers past predictions
- **Specific expertise** - Professional background affects analysis
- **Real reasoning** - LLM-powered (not templates) in full mode

### Scale Options

| Mode | Pauls | Speed | Setup |
|------|-------|-------|-------|
| Demo | 6-100 | Instant | None |
| Standard | 100-1000 | Fast | Python |
| LLM Mode | 1000-700,000+ | Medium | Ollama/LM Studio |

---

## 🎮 Usage

### Web UI
```bash
# Simple HTTP server
python -m http.server 3005 --directory ui

# Or just open ui/index.html in your browser
```

### OpenClaw Skill
```bash
# Using OpenClaw CLI
openclaw run swimming-pauls

# With custom settings
openclaw run swimming-pauls --pauls 100 --rounds 50
```

### Python API
```python
from simulation import quick_simulate
from agent import Agent, PersonaType

agents = [
    Agent('Professor Paul', PersonaType.ANALYST),
    Agent('Trader Paul', PersonaType.TRADER),
    Agent('Skeptic Paul', PersonaType.SKEPTIC),
    Agent('Visionary Paul', PersonaType.VISIONARY),
    Agent('Whale Paul', PersonaType.HEDGIE),
    Agent('Degen Paul', PersonaType.ANALYST),
]

result = await quick_simulate(rounds=20, agents=agents)
print(result.rounds[-1].consensus)
```

---

## 📝 Origin Story

It started on Sunset Boulevard. 2 AM. A self-driving Tesla with no one in it.

Inside, someone was listening to **Swimming Paul** on repeat, texting OpenClaw about MiroFish, and realizing... this is too complicated for regular people.

The idea hit like a lightning bolt: **What if we made it simple?**

No cloud APIs. No complicated setup. Just download, run, and cast the pool.

**"Let the Pauls cook."**

---

## 🔒 100% Local - No Cloud

Swimming Pauls runs entirely on your machine:
- ✅ No API keys needed
- ✅ No cloud accounts
- ✅ No internet required (after install)
- ✅ No data leaves your machine
- ✅ Fully private and auditable

---

## 🤝 Contributing

The Pauls welcome new personas! To add a Paul:

1. Use the "Create Your Paul" feature in the UI
2. Or define their traits in `persona_factory.py`
3. Give them a backstory and catchphrase
4. Set their bias and confidence levels
5. Submit a PR

---

## 📜 License

MIT - Your machine, your Pauls, your predictions.

---

<p align="center">
  <i>"Let the Pauls cook."</i><br>
  <b>🦷 Cast the pool. Surface the truth. 🦷</b>
</p>
