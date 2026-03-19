# 🌍 Paul's World - Enhanced Simulation

**Persistent virtual world where Swimming Pauls live, learn, and evolve.**

Paul's World is a living simulation where 1000+ AI personas have daily routines, form relationships, learn from documents, teach each other, and remember everything.

## What's New

### 1. Knowledge System 📚
Pauls can read and learn from documents:

```bash
# Drop documents into knowledge directory
echo "Your content here" > data/knowledge/my_topic.txt

# Pauls in Research Lab automatically read them
# Knowledge is stored per-Paul with confidence scores
```

**Supported formats:** `.txt`, `.md`, `.pdf`

### 2. Memory System 🧠
Pauls remember:
- Every prediction they made
- Conversations with other Pauls
- Lessons learned (from documents or other Pauls)
- Market events and world happenings

Old memories fade (max 50 per Paul). Important memories are reinforced.

### 3. Skills Integration 🛠️
World Pauls have the same skills as local Pauls:
- `crypto_price` - Real-time crypto data
- `yahoo_finance` - Stock prices
- `news_summarizer` - Current news
- `web_search` - Internet research
- `polymarket` - Prediction markets
- `base_blockchain` - On-chain data

Skills are used during predictions when relevant.

### 4. Dynamic Reasoning 💭
Responses are generated based on:
- **Knowledge** - What they know about the topic
- **Memories** - Past experiences with similar questions
- **Personality** - Specialty, optimism, risk tolerance
- **State** - Energy, mood, location
- **Skills** - Data from tools

No more static templates. Every response is unique.

### 5. Mood & Energy System 😊⚡
Pauls have needs:
- **Energy** - Decreases with activity, restored by resting
- **Hunger** - Must eat (go home) or energy drains faster
- **Social** - Need interaction or mood suffers
- **Mood** - Affects optimism and confidence

Tired Pauls give cautious responses. Well-rested Pauls are more confident.

### 6. Teaching & Learning 🎓
At the Cafe, knowledgeable Pauls teach others:
```
Professor Paul (Teaching) + Degen Paul (Learning)
  → Knowledge transfer happens
  → Degen Paul learns about Macroeconomics
  → Both gain social satisfaction
```

Relationships track shared knowledge topics.

## Usage

### Start the World
```bash
python paul_world.py run
```

### Ask a Question
```bash
python paul_world.py ask "Will BTC hit $100K?"
```

Response includes:
- Consensus (BULLISH/BEARISH/NEUTRAL)
- Individual Paul responses with reasoning
- Knowledge sources referenced
- Memories that influenced the answer
- Links to view in Explorer/Visualization/Debate Network

### Check Status
```bash
python paul_world.py status
```

Shows:
- Current world time
- Paul locations
- Energy/mood levels
- Knowledge counts

### Add Knowledge
```bash
# Create a document
cat > data/knowledge/ethereum_defi.txt << 'EOF'
Ethereum is the leading smart contract platform. 
DeFi (Decentralized Finance) has $50B+ TVL.
Major protocols include Uniswap, Aave, and MakerDAO.
EOF

# Pauls in Research Lab will read it automatically
```

## Paul States

| Attribute | Description |
|-----------|-------------|
| `energy` | 0-100, affects confidence and activity |
| `hunger` | 0-100, must eat or energy drains |
| `knowledge_freshness` | How up-to-date their knowledge is |
| `social` | Need for interaction |
| `mood` | -1 to 1, affects optimism |
| `accuracy_score` | Track record of predictions |
| `curiosity` | How much they seek new knowledge |
| `teaching_ability` | How effectively they teach others |

## Locations

| Location | Activities | Effect |
|----------|-----------|--------|
| **Market Floor** | Trading, Analyzing | Pauls are more bullish |
| **Research Lab** | Researching, Reading | Knowledge increases |
| **Cafe** | Socializing, Teaching | Social need met, knowledge transfer |
| **Conference Room** | Debating, Presenting | Influence increases |
| **Home** | Resting, Eating | Energy restored |
| **Park** | Socializing, Thinking | Mood improves |

## Simulation Loop

Every hour (tick):
1. Pauls decide activity based on needs
2. Energy/hunger/social update
3. Mood recalculates
4. Knowledge decays slightly
5. Interactions happen (teaching, gossip)
6. New documents scanned
7. State saved to SQLite

## Integration with Main System

When you run `local_agent.py` or `ask_pauls.py`:
- Predictions are saved with IDs
- Results can be viewed in demo pages via `?id=xxx`
- Paul's World tracks all predictions as memories
- Accuracy scores update when outcomes are marked

## Example Session

```bash
# Start simulation
$ python paul_world.py run

📅 Day 1 in Paul's World (2026-03-18)
   home: 45 Pauls
   research_lab: 12 Pauls
   cafe: 8 Pauls
   market_floor: 35 Pauls
   Most active: Professor Paul (3 predictions)
   Average mood: 😊 (0.35)

# In another terminal, ask a question
$ python paul_world.py ask "Will ETH flip BTC?"

🦷 Paul's World Consensus
Question: Will ETH flip BTC?
Consensus: BEARISH (62%)

💬 Responses (8 Pauls):

  🔮 Visionary Paul 😊 ⚡
     BEARISH (78%)
     "Based on my research on Bitcoin Overview: Bitcoin is a decentralized digital currency created in 2009. It uses blockchain... Looking at the long-term trajectory..."
     📚 Knows about: Bitcoin Overview, Ethereum DeFi

  👨‍🏫 Professor Paul 😊 🔋
     NEUTRAL (65%)
     "Historical patterns suggest... I recall 'Predicted NEUTRAL on: Will BTC hit $50K?'..."
     📚 Knows about: Bitcoin Overview, Market Cycles

📈 View full results:
   http://localhost:3005/explorer.html?id=abc123
```

## Database Schema

SQLite database (`data/paul_world.db`) stores:
- `paul_states` - Current state of each Paul
- `paul_knowledge` - All knowledge items
- `paul_memories` - Complete memory history
- `relationships` - Trust/respect between Paul pairs
- `world_events` - Market moves, news, etc.
- `world_state` - Simulation time and settings

## Scaling

Paul's World auto-detects your system:
- **Laptop**: 10-100 Pauls
- **Mac Mini M4**: 500+ Pauls
- **Cluster**: 10,000+ Pauls

Memory usage: ~10MB per Paul (includes knowledge + memories + state)

## Future Enhancements

- Pauls travel between worlds (when you have multiple Mac Minis)
- Paul marketplace (buy/sell unique Pauls)
- Paul breeding (combine traits)
- World events affect all Pauls (major news, crashes)
- Paul retirement (old Pauls mentor young ones)

---

**Let the Pauls live.** 🦷
