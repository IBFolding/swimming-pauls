# Swimming Pauls Skill

Ask 1,000 to 1,000,000 AI agents for predictions. Local-first. No cloud required.

## Installation

```bash
# Via OpenClaw CLI
openclaw skills install swimming-pauls

# Or tell your agent:
"Install the swimming-pauls skill"
```

## Quick Start

```python
# Ask the swarm
result = ask_pauls("Will BTC hit $100K this year?")
print(result['consensus'])
# {'direction': 'BULLISH', 'confidence': 0.73}

# Customize the swarm
pauls = generate_pauls(count=500, specialties=["trading", "macro", "technical"])
result = run_simulation("Is AAPL a buy?", agents=pauls, rounds=7)
```

## Functions

### `ask_pauls(question, paul_count=100, rounds=5, mode="standard")`

Ask the Paul swarm a question and get consensus.

**Parameters:**
- `question` (str): What you want to know
- `paul_count` (int): Number of Pauls (10-10,000 standard, up to 1M in high_scale mode)
- `rounds` (int): Deliberation rounds (3-10)
- `mode` (str): "standard" or "high_scale"

**Returns:**
```json
{
  "consensus": {
    "direction": "BULLISH",
    "confidence": 0.73
  },
  "sentiment": 0.45,
  "distribution": {
    "bullish": 58,
    "bearish": 23,
    "neutral": 19
  }
}
```

### `generate_pauls(count=100, specialties=None)`

Create a pool of Pauls with unique personalities.

### `get_paul_world_status()`

Check active Pauls, locations, and recent performance.

### `run_simulation(question, agents, rounds=5)`

Run full simulation with custom Paul pool.

## Use Cases

- **Trading:** Market predictions, risk assessment
- **Content:** Script analysis, creative decisions
- **Product:** Feature validation, user research
- **Healthcare:** Treatment outcome predictions
- **Any decision:** Get swarm consensus

## Modes

**Standard Mode:**
- Full personas with skills
- ~10KB per Paul
- 10,000 tested on M4
- Rich reasoning output

**High-Scale Mode:**
- Lightweight agents
- ~64 bytes per Paul
- 1,000,000+ possible
- Batch inference (100x faster)

## Requirements

- Python 3.9+
- 16GB RAM recommended (10K Pauls)
- Local LLM or API key

## Links

- Docs: https://swimmingpauls.vercel.app
- GitHub: https://github.com/IBFolding/swimming-pauls
- Trading Dashboard: https://swimmingpauls.vercel.app/trading.html

## License

MIT
