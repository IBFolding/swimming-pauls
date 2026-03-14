# 🐟 Swimming Pauls

> **When MiroFish is too hard, ask Paul. And his multiples.**
>
> Many Pauls from many universes and many professions contemplate the future of your question.

![Swimming Pauls Logo](docs/logo.png)

Swimming Pauls is a **multi-agent prediction pool** that simulates diverse personas debating and predicting outcomes. Named for the collective intelligence of multiple perspectives converging on truth.

## 🎯 What is This?

Instead of asking one AI for an answer, you cast a **pool of Pauls** - each with unique expertise, biases, and perspectives - and let them debate until consensus emerges.

Like fish in a school, individual Pauls have limited perspective. But together, swimming through data in parallel, they create **emergent intelligence** greater than any single agent.

## ✨ Features

- 🎭 **40+ Personas** - From Analyst Paul to Visionary Paul, each with unique traits
- 🔮 **Multi-Agent Simulation** - Async debates with weighted consensus
- 📊 **Monte Carlo** - 1000+ scenario probability distributions
- 📈 **Sensitivity Analysis** - Which variables actually matter
- 📉 **Backtesting** - Validate predictions against history
- 🎨 **Rich Visualizations** - Terminal charts, HTML reports, PNG exports
- 🧠 **Knowledge Graphs** - Semantic memory and reasoning
- 💾 **100% Local** - No APIs, no cloud, no data leaves your machine

## 🚀 Quick Start

```bash
# Clone the pool
git clone https://github.com/howardtherekt/swimming-pauls.git
cd swimming-pauls

# No dependencies needed! (Optional ones below)
pip install -r requirements.txt

# Cast the Pauls
python main.py --topic "Will CRITIC succeed?" --rounds 20
```

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
| **+ 30+ more** | Various | Various | Various |

## 💬 Example Session

```
$ python main.py --topic "Should I launch a coffee maker that mines Bitcoin?"

🐟 Casting 8 Pauls for analysis...

📊 Round 1/10
   Consensus: BULLISH (confidence: 0.60, strength: strong)

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

## 🎮 Commands

### Predict
```bash
# Basic prediction
python main.py --topic "Netflix stock price next quarter"

# With custom team
python main.py --topic "AI regulation impact" --analysts 3 --skeptics 2

# Full analysis
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

## 📊 Output Formats

- **Terminal** - ASCII charts and tables (default)
- **JSON** - Structured data for integration
- **HTML** - Interactive reports with Chart.js
- **PNG** - Static charts for presentations

## 🏗️ Architecture

```
swimming-pauls/
├── agent.py              # The Pauls themselves (40+ personas)
├── simulation.py         # Pool orchestration & consensus
├── persona_factory.py    # Generate custom Pauls
├── knowledge_graph.py    # Semantic memory & reasoning
├── memory.py            # SQLite persistence
├── local_memory.py      # 100% local memory (no cloud)
├── data_feeds_local.py  # Local data connectors
├── advanced.py          # Monte Carlo, sensitivity, backtesting
├── visualization.py     # Charts & reports
├── main.py             # CLI entry point
└── swimming_pauls.py   # Unified API
```

## 🔒 100% Local - No Cloud

Swimming Pauls runs entirely on your machine:
- ✅ No API keys needed
- ✅ No cloud accounts  
- ✅ No internet required (after install)
- ✅ No data leaves your machine
- ✅ Fully private and auditable

See [LOCAL_ONLY.md](LOCAL_ONLY.md) for details.

## 🧪 Advanced Usage

```python
from swimming_pauls import SwimmingPauls

# Create the pool
pauls = SwimmingPauls()

# Cast 40 Pauls and run simulation
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

## 📸 Screenshots

### Terminal Output
![Terminal](docs/screenshot-terminal.png)

### HTML Report
![HTML Report](docs/screenshot-html.png)

### Monte Carlo Distribution
![Monte Carlo](docs/screenshot-monte-carlo.png)

## 🤝 Contributing

The Pauls welcome new personas! To add a Paul:

1. Define their traits in `persona_factory.py`
2. Give them a backstory and catchphrase
3. Set their bias and confidence levels
4. Submit a PR

## 📜 License

MIT - Your machine, your Pauls, your predictions.

---

<p align="center">
  <i>"When one Paul doubts, ten Pauls know."</i><br>
  <b>🐟 Cast the pool. Surface the truth. 🐟</b>
</p>
