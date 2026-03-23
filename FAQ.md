# Frequently Asked Questions

## General

### What is Swimming Pauls?
Swimming Pauls is a **100% local multi-agent prediction engine**. You ask a question, and 10-1000+ AI personas (called "Pauls") debate and reach consensus. Each Paul has unique expertise—from Wall Street traders to doctors to artists.

### Why "Pauls"?
The creator (Howard) had a friend named Paul who was an eccentric quant trader. Paul could predict market crashes using intuition from 20 years of experience. The project bottles that "Paul magic" into an army of specialized agents.

### Is it really 100% local?
**Yes.** All computation happens on your machine. No data is sent to the cloud. No API keys required (though you can add them for enhanced features).

### How much does it cost?
**Free and open source.** MIT license. No subscriptions, no credits, no hidden fees.

---

## Getting Started

### What's the fastest way to try it?
```bash
python setup.py   # First time only
python start.py   # Start everything
```
Then open http://localhost:3005

### Do I need a GPU?
**No.** Swimming Pauls uses CPU only. It runs fine on laptops.

### What are the minimum requirements?
- Python 3.9+
- 4GB RAM (8GB+ recommended)
- Any modern OS (macOS, Linux, Windows)

### How many Pauls can I run?
- **8GB RAM:** 1,000-2,000 Pauls
- **16GB RAM:** 5,000-10,000 Pauls
- **64GB+ RAM:** 50,000+ Pauls

Run `python test_capacity.py` to test your machine.

---

## Using Swimming Pauls

### How do I ask a question?
**Via web UI:**
1. Go to http://localhost:3005
2. Click "Connect Local"
3. Type your question

**Via Telegram/Discord:**
```
/swimming-pauls Will Bitcoin hit $100k?
```

**Via CLI:**
```bash
python openclaw-skill/skill.py "Your question here"
```

### What kinds of questions work best?
- Prediction questions ("Will X happen?")
- Comparison questions ("Should I buy A or B?")
- Direction questions ("Will BTC go up?")
- Timing questions ("Is now a good time to...?")

### How long does a prediction take?
- **50 Pauls:** ~5-10 seconds
- **100 Pauls:** ~10-20 seconds
- **500 Pauls:** ~30-60 seconds
- **1000+ Pauls:** 1-5 minutes

### Can I stop a running simulation?
Yes, press Ctrl+C. The system will gracefully shut down.

---

## Learning System

### How do Pauls get smarter?
1. You make predictions
2. Price tracker records market data
3. Auto-resolver checks if predictions came true
4. Leaderboard tracks which Pauls are accurate
5. Over time, accurate Pauls get more influence

### How do I see the leaderboard?
```bash
python leaderboard.py
```

### How are predictions resolved?
- **Price targets:** Compare target price to actual price
- **Direction:** Compare prediction-time price to current price
- **Time-based:** Check outcomes after deadline passes

### What if a prediction can't be resolved?
Some predictions ("Will AI take over the world?") can't be objectively resolved. These stay as PENDING.

---

## Technical

### Where is my data stored?
- **Predictions:** `data/results/*.json`
- **History:** `data/predictions.db` (SQLite)
- **Prices:** `data/price_history.json`
- **Leaderboard:** Derived from prediction history

All local. You own your data.

### Can I export my data?
Yes:
```bash
python export_data.py --predictions --format json
python export_data.py --leaderboard --format csv
```

### How do I backup everything?
```bash
python export_data.py  # Creates export_YYYYMMDD/ folder
```

### Is there an API?
Not yet (coming in v2.2). For now, use the CLI or WebSocket interface.

---

## Troubleshooting

### "Port already in use" error
Something is using port 8765 (WebSocket) or 3005 (UI).

**Fix:**
```bash
# Use different ports
python start.py --port 8766 --ui-port 3006
```

### "Module not found" error
Dependencies aren't installed.

**Fix:**
```bash
pip install -r requirements.txt
```

### Predictions not saving
Check directory permissions:
```bash
python health_check.py --fix
```

### WebSocket connection failed
Make sure the agent is running:
```bash
python health_check.py --quick
```

If not running:
```bash
python start.py
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more.

---

## Roadmap

### What's coming in v2.2?
- Mac Mini infrastructure for 24/7 predictions
- $PAUL token for staking and credits
- Paul Marketplace (buy/sell high-accuracy Pauls)
- REST API
- Mobile apps

### How can I contribute?
See [CONTRIBUTING.md](CONTRIBUTING.md). We'd love help with:
- New Paul personas
- Additional skills
- UI improvements
- Documentation
- Bug fixes

---

## Support

### Where can I get help?
- **Discord:** [Join our server](https://discord.gg/clawd)
- **GitHub Issues:** For bugs and features
- **GitHub Discussions:** For questions and ideas

### Is there commercial support?
Not officially, but the community is active on Discord.

### Can I hire you to customize it?
The project is open source. You're free to modify it for your needs. For significant custom work, reach out on Discord.

---

## Philosophy

### Why 100% local?
- **Privacy:** Your predictions stay private
- **Speed:** No network latency
- **Cost:** No API fees
- **Control:** You own everything

### What's the catch?
There isn't one. It's genuinely free, open source, and local-first. The creator believes in building tools that respect user autonomy.

### How do you make money?
Currently, we don't. Future plans include:
- Optional cloud service (Mac Mini infrastructure)
- $PAUL token (for those who want it)
- Skill marketplace commissions

But the core product will always be free and local.

---

**Still have questions?**
- Check the [README](README.md)
- Read [CONTRIBUTING.md](CONTRIBUTING.md)
- Join our [Discord](https://discord.gg/clawd)
- Open a [GitHub Discussion](https://github.com/IBFolding/swimming-pauls/discussions)
