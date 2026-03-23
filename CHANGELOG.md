# Changelog

All notable changes to Swimming Pauls will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
