# 🌍 Paul World - Persistent Simulation

## What Is Paul World?

**A living virtual world where Pauls exist 24/7.**

Instead of spawning Pauls for each prediction, they:
- Live persistently in a virtual space
- Have daily routines (research, debate, rest, socialize)
- Form relationships (trust, respect)
- React to world events
- Evolve based on accuracy
- Age and develop over time

---

## Can It Run Locally?

**YES - with tradeoffs:**

### Local Mode (Your Machine)
```bash
# Start the world
python paul_world.py run

# World ticks every hour (simulated)
# Pauls move around, interact, evolve
# Data saved to SQLite (data/paul_world.db)
```

**Limitations:**
- Must keep computer on
- ~50-100 Pauls max (RAM)
- Ticks when computer is awake

### Mac Mini Mode (24/7)
```bash
# Running on dedicated Mac Mini M4
# World runs continuously
# 500+ Pauls
# Real-time web data ingestion
# Accessible via web dashboard
```

**Advantages:**
- Never stops running
- More Pauls = richer world
- Real market data feeds
- Accessible from anywhere

---

## How It Works

### Time System
```python
# Time moves in ticks (1 tick = 1 hour world time)
# Can speed up or slow down
world.time_speed = 1.0    # 1 hour = 1 real hour
world.time_speed = 60.0   # 1 hour = 1 real minute (for testing)
world.time_speed = 3600.0 # 1 hour = 1 real second (fast simulation)
```

### Paul Daily Cycle
```
08:00 - Wake up, check energy
09:00 - Research (if knowledge low)
10:00 - Trading (if Trader Paul)
12:00 - Lunch/Socialize at Cafe
14:00 - Debate in Conference Room
16:00 - Analyze market moves
18:00 - Rest (energy recovers)
22:00 - Sleep
```

### Locations
- **Market Floor** - Trading, analysis
- **Research Lab** - Deep research
- **Cafe** - Socializing, casual debate
- **Conference Room** - Formal debates
- **Park** - Relaxation
- **Home** - Rest, recovery

### Relationships
```python
# Pauls build trust over time
Visionary Paul ──trust: 0.8──→ Trader Paul
        ↓                           ↓
   respect: 0.9              respect: 0.6
        ↓                           ↓
   "My go-to for            "Often right but
    big ideas"              too cautious"
```

---

## User Questions = World Events

When you ask a question:

1. **World reacts** - Nearby Pauls hear it first
2. **Relationships matter** - Pauls check who they trust
3. **Location matters** - Pauls in same room influence each other
4. **Real-time state** - Energy, knowledge, mood affect response
5. **Consensus forms** - Through the living network

**Example:**
```
User: "Will ETH hit $10K?"

09:15 - Visionary Paul at Research Lab hears question
09:16 - Visionary Paul moves to Conference Room
09:17 - Calls debate: "ETH to $10K - discuss"
09:20 - Trader Paul (at Market Floor) joins
09:22 - Skeptic Paul (high trust with Trader) joins
09:30 - Debate concludes
09:31 - Consensus: BULLISH (influenced by location dynamics)
```

---

## Visualization Ideas

### 1. Isometric World Map
```
    🏠 HOME    🏢 LAB     ☕ CAFE
       ↓         ↓          ↓
    😴😴      🔮📊       🗣️🐋
    
    🏛️ CONF    📈 MARKET   🌳 PARK
       ↓         ↓          ↓
    👨‍🏫🤨      📈🎰       🐻😌
```

### 2. Time-Lapse Heatmap
- See Pauls move through day
- Hot spots = debate locations
- Follow individual Paul journeys

### 3. Relationship Graph
- Web of trust between Pauls
- Thickness = relationship strength
- Color = sentiment alignment

### 4. Paul Dashboard
```
🔮 Visionary Paul
Location: Research Lab
Activity: Debating
Energy: ████████░░ 80%
Knowledge: ██████████ 95%
Social: ██████░░░░ 60%

Recent Actions:
- 09:00: Researched ETF data
- 09:15: Asked question about ETH
- 09:17: Moved to Conference Room
- 09:20: Debating with Trader Paul

Relationships:
→ Trader Paul (trust: 0.8)
→ Skeptic Paul (trust: 0.4)
← Whale Paul (trust: 0.9, respects Visionary)
```

---

## Building Your Own World

### World Parameters
```python
# Create custom world
world = PaulWorld()

# Customize
world.time_speed = 60  # 1 hour = 1 minute
world.starting_pauls = 20  # Start small
world.locations = ["Home", "Office", "Cafe", "Trading Floor"]

# Add custom events
@world.on_event("market_crash")
def on_crash(event):
    for paul in world.pauls:
        if paul.risk_tolerance < 0.3:
            paul.activity = "PANIC_SELLING"
```

### Custom Locations
```python
class MyWorld(PaulWorld):
    def _create_locations(self):
        return {
            "Tokyo_Office": Location(capacity=10, type="work"),
            "NYC_Trading_Pit": Location(capacity=50, type="trading"),
            "London_Pub": Location(capacity=20, type="social"),
            "Metaverse_Plaza": Location(capacity=1000, type="virtual"),
        }
```

### Modding
```bash
# worlds/custom/my_world.py
from paul_world import PaulWorld, Location, Activity

class CyberpunkWorld(PaulWorld):
    """Neon-lit future where AI Pauls roam"""
    
    locations = [
        "Neon_Market",
        "Data_Haven", 
        "Underground_Bar",
        "Corp_Tower",
    ]
    
    def spawn_event(self):
        events = [
            "hack_attack",
            "corp_takeover",
            "crypto_pump",
        ]
        return random.choice(events)
```

---

## Mac Mini Upgrade Path

### Phase 1: Local (Now)
- World runs on your laptop
- SQLite storage
- ~50 Pauls
- You control when it's on

### Phase 2: Mac Mini (V2)
- Dedicated hardware
- 500+ Pauls
- 24/7 operation
- Web dashboard
- Real-time market feeds

### Phase 3: World Network (V3)
- Multiple Mac Minis
- Worlds can interact
- Pauls can travel between worlds
- Global Paul economy

---

## CLI Usage

```bash
# Start world
python paul_world.py run

# Check status
python paul_world.py status
# 🌍 World Time: 2026-03-17 14:30
# 👥 8 Pauls active
# 📍 Market Floor: Trader Paul, Whale Paul
# 📍 Cafe: Visionary Paul, Degen Paul

# Advance time
python paul_world.py tick  # +1 hour

# Ask question
python paul_world.py ask "Will BTC hit $100K?"
# 🔮 Visionary Paul: BULLISH (convinced 3 others)
# 📈 Trader Paul: BULLISH (influenced by Visionary)
# 🤨 Skeptic Paul: NEUTRAL (isolated, no influence)

# Export for visualization
python paul_world.py export > world_state.json
```

---

## Technical Architecture

```
Paul World Architecture:

┌─────────────────────────────────────┐
│         Web Dashboard               │
│  (React/Vue visualization)          │
└─────────────┬───────────────────────┘
              │ WebSocket
┌─────────────▼───────────────────────┐
│      Paul World Server              │
│  (Python async, runs on Mac Mini)   │
│                                     │
│  ┌──────────┐  ┌──────────┐        │
│  │  Time    │  │  Event   │        │
│  │  Loop    │  │  System  │        │
│  └────┬─────┘  └────┬─────┘        │
│       │             │               │
│  ┌────▼─────────────▼──────┐       │
│  │    Paul States          │       │
│  │  (8 Pauls × state)      │       │
│  └────┬────────────────────┘       │
│       │                             │
│  ┌────▼────┐  ┌──────────┐        │
│  │SQLite   │  │  World   │        │
│  │Database │  │  Events  │        │
│  └─────────┘  └──────────┘        │
└─────────────────────────────────────┘
```

---

**The dream:** A living, breathing prediction ecosystem that never stops learning. 🦷
