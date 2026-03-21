# 🦷 Swimming Pauls Integration Guide

**Connect any app to the 1000+ Paul swarm intelligence system.**

## Quick Start (3 Lines of Code)

```python
from swimming_pauls import Simulation, PersonaFactory

# Create Pauls for your domain
pauls = PersonaFactory.generate_pauls(count=100, context="your_app_domain")

# Ask anything
result = Simulation.run(
    question="Will this feature succeed?",
    agents=pauls,
    rounds=10
)

print(result.consensus)  # {direction: "BULLISH", confidence: 0.73}
```

---

## Installation

```bash
git clone https://github.com/IBFolding/swimming-pauls.git
cd swimming-pauls
pip install -r requirements.txt
```

---

## Integration Methods

### Method 1: Python Import (Recommended)

```python
from swimming_pauls import (
    Simulation,
    PersonaFactory,
    PredictionHistory,
    SkillBridge
)

class MyApp:
    def __init__(self):
        self.pauls = PersonaFactory.generate_pauls(
            count=50,  # How many Pauls to simulate
            specialties=["analyst", "researcher", "creative"]
        )
    
    def predict_outcome(self, question: str, context: dict):
        """Get Paul swarm prediction for any question."""
        result = Simulation.run(
            question=question,
            agents=self.pauls,
            rounds=5,
            context=context
        )
        return {
            "direction": result.consensus.direction,
            "confidence": result.consensus.confidence,
            "sentiment": result.sentiment,
            "reasoning": [a.reasoning for a in result.agents[:3]]
        }
```

### Method 2: HTTP API

**Start the API server:**
```bash
python chat_interface.py
# Server runs on http://localhost:8080
```

**Make requests from any language:**

```javascript
// JavaScript/TypeScript
const response = await fetch('http://localhost:8080/api/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: "Will users love this feature?",
    context: {
      user_feedback: feedback_data,
      market_trends: trend_data
    },
    pauls: 50,
    rounds: 5
  })
});

const prediction = await response.json();
// { consensus: { direction: "BULLISH", confidence: 0.73 }, ... }
```

```bash
# cURL
curl -X POST http://localhost:8080/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Should we launch now?",
    "pauls": 100,
    "rounds": 10
  }'
```

### Method 3: Custom Skills

Add domain-specific capabilities:

```python
from swimming_pauls.skills import Skill, SkillResult

@Skill.register("my_app_data")
class MyAppDataSkill(Skill):
    """Fetch data from your app."""
    
    async def execute(self, query: str, **kwargs) -> SkillResult:
        data = await my_database.fetch(query)
        return SkillResult(
            success=True,
            data=data,
            message=f"Found {len(data)} records"
        )

# Pauls can now use this skill
result = Simulation.run(
    question="Analyze our user data",
    agents=pauls,
    skills=["my_app_data"]  # Enable skill
)
```

---

## Use Cases by Industry

### Content/Creative Apps
```python
# Will this script succeed?
pauls = PersonaFactory.generate_pauls(
    count=50,
    specialties=["screenwriter", "audience_rep", "market_analyst"]
)

result = Simulation.run(
    question="Will audiences love this screenplay?",
    context={
        "genre": "sci-fi",
        "page_count": 120,
        "similar_hits": ["Inception", "Arrival"]
    }
)
```

### Fintech/Trading
```python
# Market prediction
pauls = PersonaFactory.generate_pauls(
    count=100,
    specialties=["trader", "analyst", "macro"]
)

result = Simulation.run(
    question="Will BTC break $100K this month?",
    context={
        "price_data": get_price_feed(),
        "onchain_data": get_onchain_metrics()
    }
)
```

### Product/Marketing
```python
# Feature success prediction
pauls = PersonaFactory.generate_pauls(
    count=50,
    specialties=["product_manager", "user_researcher", "growth_hacker"]
)

result = Simulation.run(
    question="Will users adopt this new feature?",
    context={
        "user_feedback": feedback_data,
        "competitor_features": competitor_data
    }
)
```

### Healthcare
```python
# Treatment outcome prediction
pauls = PersonaFactory.generate_pauls(
    count=30,
    specialties=["physician", "researcher", "data_scientist"]
)

result = Simulation.run(
    question="Will this treatment protocol improve outcomes?",
    context={
        "patient_data": anonymized_records,
        "clinical_trials": trial_data
    }
)
```

---

## Configuration Options

```python
Simulation.run(
    question="Your question here",
    
    # Core settings
    agents=pauls,           # List of Paul personas
    rounds=10,              # Debate rounds (3-20 recommended)
    
    # Context & data
    context={
        "market_data": {...},
        "user_feedback": {...},
        "historical_performance": {...}
    },
    
    # Skills (optional)
    skills=["market_data", "on_chain", "social_sentiment"],
    
    # Advanced
    min_confidence=0.6,     # Minimum to return result
    timeout=30,             # Seconds before timeout
    save_to_history=True    # Persist prediction
)
```

---

## Response Format

```json
{
  "consensus": {
    "direction": "BULLISH",      // BULLISH, BEARISH, NEUTRAL
    "confidence": 0.73            // 0.0 to 1.0
  },
  "sentiment": 0.45,              // -1.0 (negative) to 1.0 (positive)
  "agents": [
    {
      "name": "Visionary Paul",
      "specialty": "Long-term",
      "reasoning": "Based on pattern recognition...",
      "confidence": 0.85
    }
  ],
  "metadata": {
    "pauls_count": 50,
    "rounds": 10,
    "duration_ms": 2450
  }
}
```

---

## Performance Tips

| Pauls | Rounds | Time | Use Case |
|-------|--------|------|----------|
| 20 | 3 | ~2s | Quick checks |
| 50 | 5 | ~5s | Standard predictions |
| 100 | 10 | ~15s | Deep analysis |
| 1000 | 20 | ~60s | Maximum insight |

---

## Example: Full Integration

```python
# my_app/pauls_integration.py

from swimming_pauls import Simulation, PersonaFactory
from my_app.models import Script, Prediction

class CriticPauls:
    """Swimming Pauls integration for script analysis."""
    
    def __init__(self):
        self.pauls = PersonaFactory.generate_pauls(
            count=50,
            specialties=[
                "screenwriter",
                "character_developer",
                "audience_rep",
                "market_analyst"
            ]
        )
    
    async def predict_script_success(self, script: Script) -> dict:
        """Predict if a screenplay will succeed."""
        
        result = Simulation.run(
            question=f"Will '{script.title}' succeed with audiences?",
            context={
                "genre": script.genre,
                "page_count": len(script.pages),
                "logline": script.logline,
                "similar_hits": self.get_comparable_hits(script.genre),
                "market_trends": self.get_trending_genres()
            },
            agents=self.pauls,
            rounds=10
        )
        
        # Save prediction
        Prediction.objects.create(
            script=script,
            direction=result.consensus.direction,
            confidence=result.consensus.confidence,
            reasoning=result.agents[0].reasoning
        )
        
        return {
            "success_probability": result.consensus.confidence,
            "direction": result.consensus.direction,
            "key_insights": [a.reasoning for a in result.agents[:3]],
            "recommendations": self.generate_recommendations(result)
        }
```

---

## Support

- **GitHub:** https://github.com/IBFolding/swimming-pauls
- **Docs:** https://docs.openclaw.ai/swimming-pauls
- **Community:** https://discord.gg/clawd

**Remember:** The swarm is only as good as the context you feed it. Give Pauls rich data for better predictions! 🦷
