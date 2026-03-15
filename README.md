# 🐟 Swimming Pauls

> **"When MiroFish is too hard, ask Paul. And his multiples."**
>
> Many Pauls from many universes and many professions contemplate the future of your question.

![Swimming Pauls](docs/logo.png)

**Swimming Pauls** is a **multi-agent prediction pool** that simulates diverse personas debating and predicting outcomes. Born from the realization that single-agent AI predictions are limited, Swimming Pauls casts a pool of specialized agents - each with unique expertise, biases, and perspectives - and lets them debate until consensus emerges.

Like fish in a school, individual Pauls have limited perspective. But together, swimming through data in parallel, they create **emergent intelligence** greater than any single agent. The collective surfaces truth through disagreement and debate.

---

## 🎯 Why Swimming Pauls?

Most AI predictions come from a single model with a single perspective. But real decisions benefit from **diverse viewpoints**:

- The **Analyst** sees patterns in data
- The **Skeptic** finds the blindspots  
- The **Visionary** imagines futures
- The **Hedgie** protects against downside
- The **Entrepreneur** spots opportunities

Swimming Pauls brings all these perspectives together, lets them debate, and surfaces a **weighted consensus** that reflects multi-dimensional thinking.

---

## ✨ Features

- 🎭 **100+ Personas** - Professors, lawyers, mechanics, artists, moms, dads, young, old, all walks of life
- 🔮 **Multi-Agent Simulation** - Async debates with weighted consensus
- 📊 **Monte Carlo** - 1000+ scenario probability distributions
- 📈 **Sensitivity Analysis** - Which variables actually matter
- 📉 **Backtesting** - Validate predictions against history
- 🎨 **Rich Visualizations** - Terminal charts, HTML reports, PNG exports
- 🧠 **Knowledge Graphs** - Semantic memory and reasoning
- 💾 **100% Local** - No APIs, no cloud, no data leaves your machine

---

## 🚀 Quick Start

```bash
# Clone the pool
git clone https://github.com/howardtherekt/swimming-pauls.git
cd swimming-pauls

# Install (optional dependencies for enhanced features)
pip install -r requirements.txt

# Cast the Pauls
python main.py --topic "Will my startup succeed?" --rounds 20
```

---

## 🐟 Meet the Pauls

| Paul | Type | Bias | Strength |
|------|------|------|----------|
| **Analyst Paul** | Data-driven | Neutral | Pattern recognition |
| **Trader Paul** | Short-term | Reactive | Market timing |
| **Visionary Paul** | Long-term | Bullish | Future casting |
| **Skeptic Paul** | Contrarian | Bearish | Blindspot detection |
| **Producer Paul** | Budget-focused | Conservative | ROI analysis |
| **Director Paul** | Creative | Optimistic | Trend spotting |
| **Hedgie Paul** | Risk-manager | Defensive | Downside protection |
| **Entrepreneur Paul** | Innovation | Aggressive | Opportunity spotting |
| **Academic Paul** | Research | Cautious | Evidence-based |
| **Journalist Paul** | Narrative | Inquisitive | Story sensing |
| **+ 90+ more** | Various | Various | Various |

---

## 💬 Example Session

```bash
$ python main.py --topic "Should I launch a coffee maker that mines Bitcoin?"

🐟 Casting 8 Pauls for analysis...

📊 Round 1/10
   Consensus: BULLISH (confidence: 0.60, strength: strong)
   [Entrepreneur Paul and Visionary Paul are excited]

📊 Round 5/10
   Consensus: NEUTRAL (confidence: 0.52, strength: moderate)
   [Skeptic Paul and Hedgie Paul are pushing back...]

📊 Round 10/10
   Consensus: BULLISH (confidence: 0.48, strength: moderate)

🏁 FINAL CONSENSUS
Direction: BULLISH
Confidence: 48%
Sentiment: +0.47

🟢 THE PAULS SAY: This might actually work (as a meme product)

Key insights:
  → Viral marketing potential
  → Crypto bros buy anything with "mine Bitcoin" on it
  → But the economics are impossible
  → And the fire risk is real

Recommendation: Launch as novelty hardware with disclaimers.
Don't promise actual mining profits.
```

---

## 🎮 Commands

### Basic Prediction
```bash
# Standard prediction
python main.py --topic "Netflix stock price next quarter"

# With custom team composition
python main.py --topic "AI regulation impact" --analysts 3 --skeptics 2

# Full analysis suite
python main.py --topic "Should I quit my job?" --full-analysis
```

### Monte Carlo Simulation
```bash
python main.py --topic "Bitcoin price 2026" --monte-carlo --runs 1000
```

### Compare Scenarios
```bash
python main.py --compare --scenario-a "Launch now" --scenario-b "Wait 6 months"
```

### Interactive Mode
```bash
python main.py --interactive
```

### Web UI
```bash
# Start local web interface
python -m http.server 8765 --directory ui

# Open browser
open http://localhost:8765
```

---

## 📊 Output Formats

- **Terminal** - ASCII charts and tables (default)
- **JSON** - Structured data for integration
- **HTML** - Interactive reports with Chart.js
- **PNG** - Static charts for presentations

---

## 🏗️ Architecture

```
swimming-pauls/
├── agent.py              # The Pauls themselves (100+ personas)
├── simulation.py         # Pool orchestration & consensus
├── persona_factory.py    # Generate custom Pauls
├── knowledge_graph.py    # Semantic memory & reasoning
├── memory.py            # SQLite persistence
├── local_memory.py      # 100% local memory (no cloud)
├── data_feeds_local.py  # Local data connectors (RSS, files, web scraping)
├── advanced.py          # Monte Carlo, sensitivity, backtesting
├── visualization.py     # Charts & reports
├── main.py             # CLI entry point
├── swimming_pauls.py   # Unified API
└── ui/                 # Web interface
    └── index.html
```

---

## 🔒 100% Local - No Cloud

Swimming Pauls runs entirely on your machine:
- ✅ No API keys needed
- ✅ No cloud accounts  
- ✅ No internet required (after install)
- ✅ No data leaves your machine
- ✅ Fully private and auditable

See [LOCAL_ONLY.md](LOCAL_ONLY.md) for details.

---

## 🧪 Advanced Usage

```python
from swimming_pauls import SwimmingPauls

# Create the pool
pauls = SwimmingPauls()

# Cast 100 Pauls and run simulation
result = await pauls.run_simulation(
    topic="Will CRITIC succeed?",
    rounds=20
)

# Monte Carlo analysis
mc_result = await pauls.monte_carlo(runs=1000)

# Generate visualizations
pauls.visualize(format='html', output='report.html')

# Full analysis suite
await pauls.full_analysis(topic="Should I pivot?")
```

---

## 📝 Origin Story

Swimming Pauls was born on a drive down Sunset Boulevard, in a self-driving car, while listening to Swimming Paul and texting OpenClaw. The realization: single-agent AI is like asking one person for advice. But real decisions benefit from a **pool of perspectives** - analysts, skeptics, visionaries, and hedges all debating until truth emerges.

When MiroFish felt too heavy and too cloud-dependent, Swimming Pauls was built to be **lightweight, local, and 100% private**. Your questions, your Pauls, your machine.

---

## 🤝 Contributing

The Pauls welcome new personas! To add a Paul:

1. Define their traits in `persona_factory.py`
2. Give them a backstory and catchphrase
3. Set their bias and confidence levels
4. Submit a PR

---

## 📜 License

MIT - Your machine, your Pauls, your predictions.

---

<p align="center">
  <i>"When one Paul doubts, ten Pauls know."</i><br>
  <b>🐟 Cast the pool. Surface the truth. 🐟</b>
</p>
