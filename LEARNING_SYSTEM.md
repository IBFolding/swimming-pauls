# 🎓 Learning System Documentation

> **"Pauls don't just predict — they learn."**

The Swimming Pauls Learning System tracks prediction accuracy per domain, enabling Pauls to improve over time through memory-enhanced LLM prompts.

---

## Overview

The learning system consists of:

- **`paul_learning.py`** - Core learning engine with SQLite backend
- **`auto_trader.py`** - Integration with LLM for memory-enhanced trading
- **`setup.py`** - Domain selection during initialization
- **`paper_trading.py`** - Price validation and trade recording

---

## Architecture

### Database Schema

The learning system uses SQLite (`data/paul_learning.db`) with three main tables:

#### 1. predictions
Stores every prediction made by every Paul.

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT (PK) | Unique prediction ID |
| `paul_name` | TEXT | Which Paul made the prediction |
| `domain` | TEXT | Domain (trading, sports, legal, etc.) |
| `symbol` | TEXT | Asset/symbol being predicted |
| `question` | TEXT | The prediction question |
| `prediction` | TEXT | Paul's prediction text |
| `direction` | TEXT | bullish/bearish/neutral |
| `confidence` | REAL | 0-100 confidence score |
| `outcome` | TEXT | Result after resolution |
| `accuracy` | REAL | 0-1 accuracy score |
| `created_at` | TEXT | ISO timestamp |
| `resolved_at` | TEXT | ISO timestamp when resolved |

#### 2. paul_accuracy
Aggregated accuracy stats per Paul per domain.

| Column | Type | Description |
|--------|------|-------------|
| `paul_name` | TEXT (PK) | Paul's name |
| `domain` | TEXT (PK) | Prediction domain |
| `total_predictions` | INTEGER | Total predictions made |
| `correct_predictions` | INTEGER | Number correct |
| `accuracy_rate` | REAL | Correct / Total |
| `avg_confidence` | REAL | Average confidence |
| `last_updated` | TEXT | ISO timestamp |

#### 3. domain_stats
Domain-wide statistics.

| Column | Type | Description |
|--------|------|-------------|
| `domain` | TEXT (PK) | Domain name |
| `total_predictions` | INTEGER | Total across all Pauls |
| `avg_accuracy` | REAL | Domain average accuracy |
| `top_paul` | TEXT | Best performing Paul |
| `last_updated` | TEXT | ISO timestamp |

---

## Domain-Aware Learning

### Supported Domains

The system supports any prediction domain:

- **`trading`** - Crypto/stock price predictions
- **`sports`** - Game outcomes, player performance
- **`legal`** - Case settlements, verdicts
- **`marketing`** - Campaign performance
- **`weather`** - Forecasts
- **Custom** - Any domain you define

### Domain Selection

During setup (`python setup.py`), users select their domain:

```
🎯 Select your prediction domain:
1. Crypto/Trading
2. Sports
3. Legal outcomes
4. Product launches
5. Marketing campaigns
6. Weather
7. Custom (enter your own)

Choice: 7
Enter your custom domain: Lawyer stuff
✅ Custom domain: Lawyer stuff
```

The domain is stored and used for all predictions in that session.

---

## Memory-Enhanced LLM Prompts

### How It Works

When a Paul makes a prediction, the system:

1. **Retrieves track record** from `paul_learning.db`
2. **Formats memory context** with recent predictions
3. **Injects into LLM prompt** so Paul sees their history

### Example Prompt

```
You are Paul the Quant.
Your track record: 67/100 correct (67% accuracy)
Recent predictions:
  - BTC long: ✓
  - ETH short: ✗
  - SOL long: ✓
You are ranked #2 expert in trading.

Analyze BTC at $85,420.00:
Respond: SENTIMENT: [bullish/bearish/neutral] | CONFIDENCE: [0-100] | REASONING: [brief]
```

### Code Implementation

```python
from paul_learning import get_learning_system

learning = get_learning_system()

# Record a prediction
pred_id = learning.record_prediction(
    paul_name="Paul the Quant",
    domain="trading",
    symbol="BTC",
    prediction="Bullish, targeting $90k",
    direction="bullish",
    confidence=75,
    question="Will BTC hit $90k?"
)

# Later, resolve it
learning.resolve_prediction(pred_id, outcome="hit_target", accuracy=1.0)

# Get track record for LLM prompt
record = learning.get_paul_track_record("Paul the Quant", "trading")
prompt = learning.format_prompt_with_memory("Paul the Quant", "trading", "BTC", 85420.00)
```

---

## API Reference

### PaulLearningSystem Class

#### `__init__(db_path="data/paul_learning.db")`
Initialize the learning system. Creates database if doesn't exist.

#### `record_prediction(paul_name, domain, symbol, prediction, direction, confidence, question="") -> str`
Record a new prediction. Returns prediction ID.

**Parameters:**
- `paul_name` (str): Paul's name
- `domain` (str): Prediction domain
- `symbol` (str): Asset/symbol
- `prediction` (str): Prediction text
- `direction` (str): bullish/bearish/neutral
- `confidence` (float): 0-100
- `question` (str, optional): Full question text

**Returns:** Prediction ID string

#### `resolve_prediction(pred_id, outcome, accuracy)`
Mark a prediction as resolved with outcome.

**Parameters:**
- `pred_id` (str): Prediction ID from record_prediction
- `outcome` (str): Result description
- `accuracy` (float): 0-1 accuracy score

#### `get_paul_track_record(paul_name, domain, limit=5) -> dict`
Get Paul's recent track record.

**Returns:**
```python
{
    'paul_name': str,
    'domain': str,
    'total': int,
    'correct': int,
    'accuracy_rate': float,
    'avg_confidence': float,
    'recent_predictions': list  # [(symbol, direction, outcome, accuracy, created_at), ...]
}
```

#### `get_domain_experts(domain, limit=5) -> list`
Get top-performing Pauls for a domain.

**Returns:** List of tuples `(paul_name, accuracy_rate, total_predictions)`

#### `format_prompt_with_memory(paul_name, domain, symbol, price) -> str`
Generate LLM prompt with memory context.

**Returns:** Formatted prompt string

### Singleton Access

```python
from paul_learning import get_learning_system

learning = get_learning_system()  # Same instance everywhere
```

---

## Integration Points

### auto_trader.py

The auto-trader integrates learning for intelligent trade decisions:

```python
# In auto_trader.py
from paul_learning import get_learning_system

def get_paul_prediction(paul, symbol, price, domain="trading"):
    learning = get_learning_system()
    
    # Get memory-enhanced prompt
    prompt = learning.format_prompt_with_memory(
        paul['name'], domain, symbol, price
    )
    
    # Query LLM with context
    response = query_llm(prompt, model="qwen2.5:14b")
    
    # Record prediction for later resolution
    pred_id = learning.record_prediction(
        paul_name=paul['name'],
        domain=domain,
        symbol=symbol,
        prediction=response['sentiment'],
        direction=response['sentiment'],
        confidence=response['confidence'],
        question=f"{symbol} at ${price}"
    )
    
    return response, pred_id
```

### setup.py

Domain selection during initialization:

```python
# In setup.py
from paul_learning import get_learning_system

def setup_domain():
    print("\n🎯 Select your prediction domain:")
    domains = [
        ("1", "trading", "Crypto/Trading"),
        ("2", "sports", "Sports"),
        ("3", "legal", "Legal outcomes"),
        ("4", "marketing", "Product launches"),
        ("5", "marketing", "Marketing campaigns"),
        ("6", "weather", "Weather"),
        ("7", None, "Custom (enter your own)")
    ]
    
    # ... user selection logic ...
    
    domain = selected_domain
    print(f"✅ Domain set to: {domain}")
    return domain
```

### paper_trading.py

Price validation and trade recording:

```python
# In paper_trading.py
from paul_learning import get_learning_system

def execute_trade(symbol, direction, confidence, paul_name, domain="trading"):
    # Validate price (> $0.01 to prevent corruption)
    price = get_price(symbol)
    if price < 0.01:
        logger.error(f"Invalid price for {symbol}: ${price}")
        return None
    
    # Record prediction
    learning = get_learning_system()
    pred_id = learning.record_prediction(
        paul_name=paul_name,
        domain=domain,
        symbol=symbol,
        prediction=f"{direction} with {confidence}% confidence",
        direction=direction,
        confidence=confidence
    )
    
    # Execute trade...
    
    return trade_id, pred_id
```

---

## Price Validation

Critical protection against data corruption:

```python
# In auto_trader.py, paper_trading.py, price_feed.py
MIN_VALID_PRICE = 0.01

def validate_price(price):
    """Ensure price is valid to prevent extreme PnL values."""
    if price is None or price < MIN_VALID_PRICE:
        logger.error(f"Invalid price: {price}")
        return False
    return True
```

This prevents the trillion-dollar PnL bug from corrupted price data.

---

## Best Practices

### 1. Always Record Predictions
Every prediction should be recorded for learning:

```python
pred_id = learning.record_prediction(...)
# Store pred_id with trade for later resolution
```

### 2. Resolve Predictions
Mark predictions as resolved when outcome is known:

```python
# When trade closes or outcome is known
learning.resolve_prediction(pred_id, outcome, accuracy)
```

### 3. Use Domain Consistently
Stick to one domain per Paul session for accurate tracking.

### 4. Minimum Sample Size
Accuracy rankings require at least 5 predictions:

```python
# In get_domain_experts()
WHERE total_predictions >= 5
```

---

## Database Location

```
data/
├── paul_learning.db      # Learning system database
├── paper_trading.db      # Paper trading records
└── price_history.db      # Historical prices
```

All SQLite, all local. No cloud dependencies.

---

## Troubleshooting

### Empty Track Records
New Pauls start with empty track records. This is normal — they build history over time.

### Accuracy Not Updating
Ensure `resolve_prediction()` is called after outcomes are known.

### Database Locked
SQLite can only handle one writer at a time. The system uses connection-per-operation to minimize this.

### Custom Domain Not Working
Check that domain name is consistent between `record_prediction()` and `get_paul_track_record()`.

---

## Future Enhancements

- **Time-decay weighting** - Recent predictions weighted more heavily
- **Cross-domain transfer** - Pauls with skills in multiple domains
- **Confidence calibration** - Track if Pauls are over/under-confident
- **Leaderboard API** - HTTP endpoint for top Pauls

---

## Summary

The Learning System makes Pauls smarter over time by:

1. **Tracking every prediction** in SQLite
2. **Calculating accuracy** per Paul per domain
3. **Injecting track records** into LLM prompts
4. **Ranking experts** by performance
5. **Validating data** to prevent corruption

The longer you run it, the smarter the Pauls get.

> **"Let the Pauls learn."**