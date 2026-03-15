---
name: swimming-pauls
description: "Run 100+ AI agents locally for predictions. Each agent uses real LLMs (via Ollama/LM Studio) with individual memory and personality. 100% local, no cloud required."
homepage: https://github.com/IBFolding/swimming-pauls
metadata:
  openclaw:
    emoji: "🦷"
    requires:
      bins: ["python3", "pip3"]
    optional:
      bins: ["ollama"]
---

# 🦷 Swimming Pauls

Run hundreds of AI agents on your machine to simulate crowd behavior and predict outcomes.

## What Makes This Different

Unlike simple polling, Swimming Pauls creates **actual AI agents** with:
- **Individual LLM calls** per agent (via Ollama/LM Studio)
- **Unique personalities** - Professor, Trader, Skeptic, Visionary, Whale, Degen, and more
- **Memory** - Agents remember previous rounds and adjust
- **True consensus** - Agents debate and influence each other
- **100% local** - No cloud, no APIs, no data leaves your machine

## Quick Start (Local Only)

### Option 1: Demo Mode (No Setup)
```bash
# Just open the UI file directly
open swimming-pauls/ui/index.html

# Or serve it
python3 -m http.server 3005 --directory swimming-pauls/ui
```

### Option 2: Full LLM Mode (Recommended)

```bash
# 1. Install Ollama (local LLM)
brew install ollama
ollama pull llama3

# 2. Start Ollama
ollama serve

# 3. Clone Swimming Pauls
git clone https://github.com/IBFolding/swimming-pauls.git
cd swimming-pauls

# 4. Install dependencies
pip3 install websockets aiohttp

# 5. Start the agent
python3 local_agent.py --llm-mode

# 6. Open UI at http://localhost:3005
```

## How It Works

```
Your Question
     ↓
[Paul 1] ← LLM call → "Bullish because..."
[Paul 2] ← LLM call → "Bearish due to..."
[Paul 3] ← LLM call → "Neutral, waiting for..."
     ↓
Consensus Algorithm
     ↓
Final Prediction + Confidence
```

Each Paul is a separate LLM call with:
- Unique system prompt (personality)
- Individual memory context
- Specific expertise bias
- Real reasoning (not templates)

## Scale

- **Demo mode**: 6-100 rule-based agents (instant)
- **LLM mode**: 6-700,000+ actual AI agents (limited by your hardware)
- **Local only**: Everything runs on your CPU/GPU

## Example Usage

**"Should I buy Bitcoin?"**
```
1. Type question in UI
2. Select 50 Pauls
3. Click "CAST THE POOL"
4. Each of 50 Pauls gets LLM call with unique persona
5. See consensus + individual responses
6. Matrix visualization shows who's bullish/bearish
```

## The Pauls

| Paul | Style | Expertise |
|------|-------|-----------|
| 👨‍🏫 Professor | Analytical | Data, regression, patterns |
| 📈 Trader | Reactive | Markets, timing, order flow |
| 🤨 Skeptic | Contrarian | Risk, blind spots, tail risks |
| 🔮 Visionary | Long-term | Trends, paradigm shifts |
| 🐋 Whale | Strategic | Institutional, liquidity |
| 🎰 Degen | Chaotic | Sentiment, memes, vibes |

## Features

- 🎲 **Monte Carlo** - 1000-run probability distributions
- 📊 **Sensitivity Analysis** - What factors matter most  
- 🧠 **Knowledge Graph** - Entity extraction & relationships
- 🔲 **Paul Matrix** - Visual consensus map
- 🔍 **Search/Filter** - Find specific perspectives
- 🎨 **Custom Pauls** - Create your own personas

## LLM Providers (All Local)

| Provider | Setup | Speed | Quality |
|----------|-------|-------|---------|
| Ollama | `brew install ollama` | Fast | Good |
| LM Studio | Download GUI | Medium | Excellent |
| LocalAI | Docker | Medium | Good |

## Configuration

Environment variables:
```bash
export PAULS_PROVIDER=ollama        # ollama, lmstudio, localai
export PAULS_MODEL=llama3           # any local model
export PAULS_DEFAULT=50             # default Paul count
export WS_PORT=8765                 # WebSocket port
export UI_PORT=3005                 # UI port
```

## Troubleshooting

**"Ollama connection refused"**
- Make sure `ollama serve` is running
- Check Ollama is installed: `ollama --version`

**"Too slow with many Pauls"**
- Reduce Paul count (try 10-20)
- Use smaller model (llama3.2 instead of llama3)
- Get more RAM/CPU

**"Module not found"**
- Run: `pip3 install websockets aiohttp`

## Links

- GitHub: https://github.com/IBFolding/swimming-pauls
- Demo: http://localhost:3005 (after starting)

---

**Let the Pauls cook.** 🦷
