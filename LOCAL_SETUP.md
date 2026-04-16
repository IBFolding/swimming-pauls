# Swimming Pauls - Local Setup Guide

## Quick Start (5 minutes)

### 1. Clone and Navigate
```bash
cd /Users/brain/.openclaw/workspace/swimming_pauls
```

### 2. Install Dependencies
```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies for World V2
cd pauls-world-v2 && npm install && cd ..

# Node.js dependencies for World V3
cd pauls-world-v3 && npm install && cd ..
```

### 3. Configure API Keys (Optional)
```bash
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys
```

### 4. Start All Services

**Terminal 1 - WebSocket Server:**
```bash
python local_agent.py
```

**Terminal 2 - World V2:**
```bash
cd pauls-world-v2 && npm start
```

**Terminal 3 - World V3 (Optional):**
```bash
cd pauls-world-v3 && npm start
```

### 5. Open in Browser
- **Terminal (Main App):** Open `app/index.html` in browser
- **World V2:** http://localhost:3001
- **World V3:** http://localhost:3002

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     SWIMMING PAULS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   TERMINAL   │  │  WORLD V2    │  │  WORLD V3    │      │
│  │              │  │  (Modern)    │  │  (8-Bit)     │      │
│  │  app/        │  │  :3001       │  │  :3002       │      │
│  │  index.html  │  │              │  │              │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │              │
│         └─────────────────┼─────────────────┘              │
│                           │                                │
│              ┌────────────┴────────────┐                  │
│              │   WebSocket Server      │                  │
│              │   python local_agent.py │                  │
│              │   Port 8765             │                  │
│              └────────────┬────────────┘                  │
│                           │                                │
│              ┌────────────┴────────────┐                  │
│              │   Prediction Engine     │                  │
│              │   swimming_pauls.py     │                  │
│              └─────────────────────────┘                  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              DATA LAYER                             │   │
│  │  - SQLite (predictions.db)                         │   │
│  │  - LocalStorage (browser credits)                  │   │
│  │  - File system (logs, cache)                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Terminal (Main App)
**Location:** `app/`
**Entry:** `app/index.html`

Features:
- Ask questions to 1000+ Pauls
- View predictions and consensus
- Track accuracy
- Manage credits

**To run locally:**
```bash
# Just open the HTML file - no server needed
open app/index.html
```

### 2. World V2 (Modern Isometric)
**Location:** `pauls-world-v2/`
**Port:** 3001

Features:
- Real-time 3D isometric world
- 1000 Pauls walking around
- Buildings with activities
- Diary, Social, Create panels
- Chat with Pauls

**To run:**
```bash
cd pauls-world-v2
npm start
# Open http://localhost:3001
```

### 3. World V3 (8-Bit Pixel Art)
**Location:** `pauls-world-v3/`
**Port:** 3002

Features:
- Retro 8-bit aesthetic
- SimCity-style graphics
- Same features as V2
- Grid-based movement

**To run:**
```bash
cd pauls-world-v3
npm start
# Open http://localhost:3002
```

### 4. WebSocket Server
**Location:** `local_agent.py`
**Port:** 8765

Purpose:
- Real-time communication
- Broadcasts predictions
- Syncs world state

**To run:**
```bash
python local_agent.py
```

---

## Testing

### Quick Test
```bash
./run_tests.sh
```

### Full Test Suite
```bash
# Run all tests
python -m pytest tests/ -v

# Test specific components
python test_ws.py              # WebSocket
curl http://localhost:3001/api/stats   # API
python test_capacity.py        # Load testing
```

---

## Local-Only Mode (No Internet)

Swimming Pauls works offline with local LLMs:

```bash
# Install Ollama (if not installed)
brew install ollama

# Pull a model
ollama pull llama2

# Run in local mode
python swimming_pauls.py --local --predict "Your question"
```

---

## Troubleshooting

### Port Already in Use
```bash
# Kill processes on specific ports
lsof -ti:3001 | xargs kill -9
lsof -ti:3002 | xargs kill -9
lsof -ti:8765 | xargs kill -9
```

### Database Issues
```bash
# Reset database (WARNING: deletes all data)
rm data/predictions.db
python -c "from local_memory import init_db; init_db()"
```

### Missing Dependencies
```bash
# Python
pip install -r requirements.txt

# Node.js
cd pauls-world-v2 && npm install
cd pauls-world-v3 && npm install
```

### Permission Errors
```bash
chmod +x *.sh
chmod +x *.py
```

---

## Development Mode

### Hot Reload
```bash
# World V2 with auto-restart
cd pauls-world-v2 && npm run dev

# World V3 with auto-restart
cd pauls-world-v3 && npm run dev
```

### Debug Mode
```bash
# Enable debug logging
DEBUG=1 python local_agent.py
DEBUG=1 npm start  # For World servers
```

---

## Production Deployment

### Build for Production
```bash
# World V2
cd pauls-world-v2 && npm run build

# World V3
cd pauls-world-v3 && npm run build
```

### Environment Variables
```bash
export NODE_ENV=production
export PORT=3001
export DATABASE_URL=sqlite:///data/predictions.db
```

---

## API Reference

### World API Endpoints

```bash
# Get world state
GET http://localhost:3001/api/world

# Get stats
GET http://localhost:3001/api/stats

# Get buildings
GET http://localhost:3001/api/buildings

# Get Pauls in building
GET http://localhost:3001/api/buildings/:id/pauls

# Ask question
POST http://localhost:3001/api/ask
Body: {"question": "Will BTC pump?", "numPauls": 50}

# Trigger event
POST http://localhost:3001/api/events
Body: {"type": "market_crash"}
```

### WebSocket Messages

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8765');

// Receive world updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.type); // 'worldUpdate', 'event', etc.
};

// Send commands
ws.send(JSON.stringify({
  type: 'selectPaul',
  paulId: 123
}));
```

---

## File Structure

```
swimming_pauls/
├── app/                      # Main Terminal UI
│   ├── index.html           # Entry point
│   ├── trading.html         # Trading interface
│   ├── world.html           # World view (old)
│   └── ...
├── pauls-world-v2/          # Modern 3D World
│   ├── public/
│   │   ├── index.html
│   │   └── world.js
│   └── server/
│       ├── index.js
│       └── simulation.js
├── pauls-world-v3/          # 8-Bit World
│   └── (same structure as v2)
├── data/                    # Database & cache
│   └── predictions.db
├── swimming_pauls.py        # Main prediction engine
├── local_agent.py          # WebSocket server
├── skill_bridge.py         # OpenClaw integration
└── config.yaml             # Configuration
```

---

## Support

- **Issues:** Check TEST_PLAN.md for troubleshooting
- **Tests:** Run `./run_tests.sh` to verify setup
- **Docs:** See README.md for full documentation

---

*Last updated: 2026-04-16*
