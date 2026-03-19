# ReportAgent System for Swimming Pauls

Automated report generation with integrated OpenClaw skill outputs.

## Overview

The ReportAgent system provides comprehensive report generation for Swimming Pauls simulations, featuring:

- 📊 **Consensus Summary** - Aggregate prediction findings
- 🎭 **Individual Reasoning** - Each Paul's perspective
- 🔧 **Skill Integration** - Real-time data from OpenClaw skills (crypto prices, news, etc.)
- 📈 **Visualizations** - Charts and interactive HTML
- 💾 **Persistent Storage** - Reports saved with unique IDs
- 🌐 **REST API** - HTTP endpoints for report management

## Quick Start

```python
from swimming_pauls import SwimmingPauls, ReportAgent
import asyncio

async def main():
    # Run simulation
    pauls = SwimmingPauls()
    result = await pauls.run_simulation(rounds=10)
    
    # Generate report
    agent = ReportAgent()
    report, paths = await agent.generate_and_save(
        result, 
        pauls.agents,
        topic="BTC price prediction"
    )
    
    print(f"Report saved: {paths['html']}")

asyncio.run(main())
```

## Components

### 1. ReportAgent
Main class for report generation.

```python
agent = ReportAgent(storage_dir="./reports")

# Generate report
report = await agent.generate_report(
    result=simulation_result,
    agents=agents,
    topic="market analysis",
    title="My Report"
)

# Save report
paths = agent.save_report(report)

# Retrieve report
html_content = agent.get_report(report_id, format="html")
markdown_content = agent.get_report(report_id, format="markdown")
json_content = agent.get_report(report_id, format="json")

# List all reports
reports = agent.list_reports()
```

### 2. SkillIntegrator
Integrates OpenClaw skills for real-time data enrichment.

Supported skills:
- `crypto-price` - Cryptocurrency prices and charts
- `yahoo-finance` - Stock prices and financial data
- `polymarket` - Prediction market odds
- `news-summarizer` - Latest news with sentiment
- `weather` - Weather forecasts
- `base` - Base blockchain data

```python
integrator = SkillIntegrator()

# Detect relevant skills for a topic
skills = integrator.detect_relevant_skills("crypto market")

# Enrich topic with skill data
skill_data = await integrator.enrich_topic("bitcoin price")
```

### 3. ReportFormatter
Format reports as Markdown, HTML, or JSON.

```python
from swimming_pauls import format_report_markdown, format_report_html

# Export to Markdown
markdown = format_report_markdown(report)

# Export to HTML
html = format_report_html(report)
```

### 4. API Server
HTTP API for report management.

```python
from swimming_pauls.report_api import start_report_api

# Start server
server = start_report_api(port=8080)

# Server runs until stopped
```

#### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/reports` | List all reports |
| GET | `/api/reports/{id}` | Get report by ID |
| GET | `/api/reports/{id}/html` | Get HTML report |
| POST | `/api/simulate` | Run simulation + generate report |
| GET | `/api/skills` | List available skills |

Example API usage:

```bash
# Generate report via API
curl -X POST http://localhost:8080/api/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "BTC analysis",
    "rounds": 10,
    "title": "Bitcoin Report"
  }'

# Get report
curl http://localhost:8080/api/reports/{id}/html
```

## Report Structure

Reports contain:

```json
{
  "metadata": {
    "report_id": "abc123",
    "title": "Report Title",
    "created_at": "2024-01-01T00:00:00",
    "num_agents": 5,
    "num_rounds": 10
  },
  "consensus": {
    "direction": "bullish",
    "confidence": 0.75,
    "sentiment": 0.65,
    "strength": "strong"
  },
  "agent_reasonings": [
    {
      "agent_name": "Analyst-1",
      "persona": "analyst",
      "direction": "bullish",
      "confidence": 0.85,
      "reasoning": "..."
    }
  ],
  "skill_data": [
    {
      "skill_name": "crypto-price",
      "query": "BTC",
      "result": {...}
    }
  ],
  "insights": [
    "Strong bullish consensus..."
  ]
}
```

## Storage

Reports are saved to:

```
~/.openclaw/workspace/swimming_pauls/reports/
├── markdown/
│   └── {report_id}.md
├── html/
│   └── {report_id}.html
├── json/
│   └── {report_id}.json
└── report_index.json
```

## Examples

Run the example script:

```bash
# Basic example
python example_report_agent.py basic

# Skill-enriched report
python example_report_agent.py skills

# Start API server
python example_report_agent.py api

# Quick report
python example_report_agent.py quick

# Markdown export
python example_report_agent.py markdown
```

## Testing

Run the test suite:

```bash
python test_report_agent.py
```

Tests cover:
- Skill detection and integration
- Report compilation
- Formatting (Markdown, HTML, JSON)
- Storage operations
- API endpoints
- Full workflow integration

## Configuration

```python
from swimming_pauls import ReportAgent

agent = ReportAgent(
    storage_dir="./my_reports",  # Custom storage location
    enable_skills=True           # Enable skill integration
)
```

## License

MIT License - See LICENSE file