# 🦷 Swimming Pauls

> **"Let the Pauls cook."**
>
> Multi-agent prediction engine. 100% local. No cloud.

![Swimming Pauls](ui/paul.jpg)

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
- 📎 **Context Upload** - Images, PDFs, links for analysis
- 🎨 **Custom Pauls** - Create your own personas
- 🔌 **Local Agent** - WebSocket connection to Python backend
- 🎮 **Demo Mode** - Test without installing Python
- 💾 **100% Local** - No APIs, no cloud, no data leaves your machine

---

## 🚀 Quick Start

### Option 1: Demo Mode (Fastest)
1. Open `http://localhost:3005` (or open `ui/index.html` directly)
2. Type a question
3. Click "🐟 CAST THE POOL 🐟"
4. The Pauls will debate and reach consensus

### Option 2: Local Agent (Full Power)
```bash
# Clone the pool
git clone https://github.com/IBFolding/swimming-pauls.git
cd swimming-pauls

# Install dependencies
pip install -r requirements.txt

# Start local agent
python local_agent.py

# Open UI and click "🔌 Connect Local"
```

### Option 3: OpenClaw Skill (One Command)

If you have OpenClaw installed:

```bash
# Install the skill
curl -sSL https://raw.githubusercontent.com/IBFolding/swimming-pauls/main/install-skill.sh | bash

# Run it
openclaw run swimming-pauls
```

Or manually:
```bash
# Copy skill to your OpenClaw skills folder
mkdir -p ~/.openclaw/workspace/skills/swimming-pauls
cp swimming-pauls/openclaw-skill/* ~/.openclaw/workspace/skills/swimming-pauls/

# Run it
openclaw run swimming-pauls
```

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

## 🐟 Meet the Pauls

| Paul | Emoji | Style | Strength |
|------|-------|-------|----------|
| **Professor Paul** | 👨‍🏫 | Academic, data-driven | Pattern recognition, regression analysis |
| **Trader Paul** | 📈 | Market-focused, reactive | Order flow, timing, risk/reward |
| **Skeptic Paul** | 🤨 | Contrarian, cautious | Blindspot detection, tail risk analysis |
| **Visionary Paul** | 🔮 | Long-term, optimistic | Future casting, paradigm shifts |
| **Whale Paul** | 🐋 | Institutional, strategic | Liquidity analysis, smart money flows |
| **Degen Paul** | 🎰 | Chaotic, YOLO energy | Market sentiment, meme momentum |

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
