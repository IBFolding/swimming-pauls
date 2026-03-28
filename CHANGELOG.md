# Changelog

All notable changes to Swimming Pauls will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2026-03-28

### Added

#### Domain-Aware Learning System
- `paul_learning.py` - Core learning engine with SQLite backend (`data/paul_learning.db`)
- Memory-enhanced LLM prompts — Pauls see their own track record during predictions
- Per-domain accuracy tracking (trading, sports, legal, marketing, weather, custom)
- Domain expert rankings — top-performing Pauls per domain
- Setup wizard domain selection with custom domain support
- `LEARNING_SYSTEM.md` - Comprehensive documentation for the learning system

#### Trading Intelligence Suite
- `trading_intelligence.py` - RSI, MACD, Bollinger Bands, ATR, volume analysis
- `auto_trader_intelligent.py` - Smart auto-trader using technical signals + LLM
- `trading_api.py` - API server for live trading dashboard
- `trading_engine.py` - Core trading execution engine
- `demo_trading_live.html` - Real-time dark-themed trading dashboard
- `trading_dashboard.html` - Alternative trading UI

#### Paul Progression System
- `progression_manager.py` - Career pipeline: Training → Proven → Bankr-Ready → Live
- Promotion criteria: 50+ trades, >60% win rate, >1% ROI, 7+ day track record
- Designed for future Bankr integration (only proven Pauls get real money)

#### Paper Trading Improvements
- `auto_trader.py` - Updated with LLM integration (qwen2.5:14b) and learning
- `price_feed.py` - Live price feed with validation (> $0.01 minimum)
- `check_pnl.py` / `pnl_report.py` - PnL reporting and analysis tools
- `fix_entry_prices.py` - Data cleanup utility
- `pre_launch_test.py` - Pre-launch verification suite

#### Creative Pauls
- 50 new creative Pauls (#1001-1050) for script writing
- First collaborative screenplay: "THE PACKAGE" (12 pages, 2,847 words)
- `script_doctor.py` - Collaborative screenplay writing engine

#### Other Additions
- `high_scale_mode.py` - LightweightPaul (~64 bytes) for 1M+ agents at ~64MB RAM
- `INTEGRATION.md` - Full documentation for connecting external apps
- `LIVE_TRADING_PLAN.md` - Roadmap for live trading rollout
- `spawn_mass_pauls.py` - Mass Paul instantiation utility
- `pump_fun_tracker.py` - Pump.fun monitoring (shelved — SSL issues)
- UI updates: `connect-modal.html`, `explorer.html`, `paul-section.html`, `visualize.html`

### Fixed
- **Critical: PnL data corruption** — Cleaned 1,084 corrupted trades with trillion-dollar values
- Added price validation (> $0.01) across `auto_trader.py`, `paper_trading.py`, `price_feed.py`
- Reset 21 portfolios with extreme values
- Fixed `local_agent.py` WebSocket auth (accepts "openclaw" connection_id)
- Made `psutil` optional in `local_agent.py`
- Fixed WebSocket handler signature for newer `websockets` library

### Changed
- Auto-trader now uses `qwen2.5:14b` model with learning context
- Landing page updated: "1K-1M" Pauls range, integration section, Bankr/Solana logos
- Deleted `qwen3-coder:latest` (18GB) and `gpt-oss:20b` (13GB) to free disk space

## [2.1.0] - 2026-03-23

### Added

#### Core Infrastructure
- `setup.py` - First-time setup wizard with dependency checks and diagnostics
- `start.py` - Unified launcher that starts both WebSocket agent and UI server
- `config.example.yaml` and `config_loader.py` - User configuration system
- `health_check.py` - System diagnostics and troubleshooting tool
- `export_data.py` - Data backup and export to JSON/CSV formats
- `generate_demo_data.py` - Generate demo predictions for new users to explore

#### Learning System
- `resolve_predictions.py` - Mark predictions as CORRECT/INCORRECT against market data
- `auto_resolver.py` - Daemon that automatically checks prediction outcomes hourly
- `leaderboard.py` - Paul accuracy rankings with specialty breakdowns
- `price_tracker.py` - Historical price recording for direction prediction resolution
- SQLite storage for persistent prediction history and Paul performance tracking

#### OpenClaw Integration
- `openclaw-skill/skill.py` - Telegram/Discord bot integration
- Auto-starts local agent if not running
- Formatted responses with explorer links
- One-command launcher: `python start.py`

#### Visualizations
- `ui/debate_network.html` - Interactive D3.js debate network visualization
- Hover tooltips with Paul details and reasoning
- Draggable nodes and top influencer rankings

### Changed
- Updated `.gitignore` to include UI HTML files
- Updated `README.md` with v2.1 features and quick start guide
- Updated `SKILL.md` with new commands and usage instructions

### Fixed
- Version bump from 2.0.0 to 2.1.0 in `__init__.py`

## [2.0.0] - 2026-03-17

### Added
- Initial release of Swimming Pauls v2.0
- 1000+ Paul personas with unique expertise
- Multi-agent prediction engine
- WebSocket local agent for real-time simulations
- Web UI with explorer and visualization
- Knowledge graph with 26+ market entities
- OpenClaw skill bridge for external tool integration
- Custom skills API framework
- Prediction history tracking in SQLite
- Debate tracker for persuasion flow
- Web intelligence for research
- Paper trading simulation

### Features
- 100% local execution (no cloud required)
- No API keys needed
- Support for 10,000+ Pauls on consumer hardware
- Real-time consensus building
- Individual Paul reasoning transparency
