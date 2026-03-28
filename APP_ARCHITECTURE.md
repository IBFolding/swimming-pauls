# Swimming Pauls Local App - Architecture Plan v2
# Saved: 2026-03-28

## Overview
Single-page local web app (`app.html`) that serves as the control center for everything
Swimming Pauls does. Opens when user runs `python start.py`.

## 10 Tabs (Left sidebar navigation)

### 1. 🏠 Home - "Cast the Pool" (default)
- Question textarea
- Paul count slider (10-1000+) with system capacity indicator
- Rounds slider (5-100)
- Domain selector (trading, sports, legal, marketing, weather, custom)
- Paul selector grid with specialty filters
- "Cast the Pool" button → WebSocket
- Live progress bar, streaming Paul responses
- Results appear inline, unlock other tabs

### 2. 📊 Results - Explorer
- Consensus badge (BULLISH/BEARISH/NEUTRAL) + confidence
- Sentiment chart (pie/bar)
- Individual Paul cards with reasoning
- Prediction history sidebar (all past, clickable)
- Filter by domain, date, direction

### 3. 🕸️ Debate - Network
- D3.js interactive graph
- Nodes = Pauls (sized by influence), edges = persuasion
- Color-coded by direction
- Hover tooltips, draggable nodes
- Top influencers sidebar
- Round-by-round playback slider

### 4. 📈 Visualize
- Paul network overview
- Belief distribution histogram per round
- Consensus convergence line chart
- Specialty cluster view

### 5. 🌍 Paul's World
- Start/Pause/Stop controls, speed slider
- World map with locations and Paul counts
- Click location → see Pauls and activities
- Paul inspector (location, mood, energy, reputation, knowledge, memories, relationships)
- World events feed (scrolling log)
- Daily summary, world clock

### 6. 📱 Social
- Feed view (Paul posts about predictions)
- Platform filter (Discord, Twitter, Telegram, Reddit)
- Trending topics
- Paul profiles with social stats
- Auto-post toggle

### 7. 🏆 Leaderboard
- Overall rankings by accuracy
- Domain filter
- Stats: win rate, predictions, confidence, streak
- Domain experts highlighted
- Accuracy over time chart
- Click Paul → prediction history

### 8. 💰 Trading
- Portfolio overview (PnL, win rate, positions)
- Active positions table
- Trade history
- Progression tracker (Training → Proven → Bankr-Ready → Live)
- Auto-trader controls (Start/Stop, model, interval)
- PnL equity curve chart

### 9. 🎬 Creative
- Script input / prompt
- Script Doctor analysis
- Collaborative write mode
- Formatted screenplay output
- History

### 10. ⚙️ Settings
- LLM: Ollama URL, model selector (auto-detect), test connection, model download
- Simulation: default Pauls, rounds, timeout, domain
- Server: WS port, UI port, host
- Learning: toggle, min predictions, weight recent
- Paper Trading: toggle, interval, max positions, symbols
- Auto-Resolver: toggle, interval, symbols
- Price Tracker: toggle, symbols, interval
- Save → config.yaml, Reset defaults
- System info (OS, RAM, Ollama status, disk)

## Technical

### Frontend
- Single `app.html`, no build step
- Tailwind CSS CDN, D3.js CDN
- Vanilla JS, tab routing via hash
- Dark theme (dark bg, cyan/gold accents)

### Backend (local_agent.py new message types)
- config.get / config.save
- ollama.models / ollama.test
- leaderboard.get
- trading.status / trading.start / trading.stop
- world.start / world.stop / world.status / world.tick / world.paul / world.locations
- social.feed / social.trending / social.paul
- history.list / history.get
- creative.analyze / creative.write

### start.py changes
- Auto-open browser to http://localhost:{port}/app.html
- Serve from project root
- Start Paul's World paused by default

### Build Phases
1. Home + Results + Settings (core ask/answer loop)
2. Debate + Visualize + Leaderboard (data viz)
3. Paul's World + Social (living sim)
4. Trading + Creative (specialized)
