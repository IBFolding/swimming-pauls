# 📊 Paper Trading System

**Learn to trade without risking real money.**

Paul's World includes a full paper trading system where Pauls trade with fake money, build track records, and compete for "Proven Trader" status.

## Overview

Each Paul gets a **$10,000 paper portfolio** to trade with. When they make high-confidence predictions (>75%), they automatically execute paper trades. Track performance, identify top traders, and discover who actually knows what they're talking about.

## Three Modes

### 1. **Live Mode** (World Running)
Pauls trade in real-time alongside predictions:
- Auto-executes trades on >75% confidence predictions
- Real-time P&L tracking
- Social media posts about trades
- Updates with market prices

### 2. **Backtest Mode** (Historical)
Test strategies against historical data:
```bash
python paper_trading.py backtest --days 30 --strategy consensus
```

### 3. **Competition Mode** (Weekly)
Weekly trading competitions:
```bash
python paul_world.py paper competition start 7
```

## Quick Start

### Enable Paper Trading for All Pauls
```bash
python paul_world.py paper enable-all
```

This creates a $10,000 portfolio for every Paul in the world.

### Check a Paul's Portfolio
```bash
python paul_world.py paper status "Trader Paul"
```

Output:
```
📊 Trader Paul Paper Trading Portfolio
   Status: Enabled
   Total Value: $12,450.00 (+24.5%)
   Cash: $2,450.00
   Positions: 3
   Trades: 47 (Win rate: 68%)
   Max Drawdown: 12.3%
   🏆 PROVEN TRADER
```

### View Leaderboard
```bash
python paul_world.py paper leaderboard
```

Shows rankings by ROI, win rate, and total trades.

### List Proven Traders
```bash
python paul_world.py paper proven
```

Pauls with >60% win rate and 50+ trades earn the Proven Trader badge.

## How It Works

### Auto-Trading Logic

When Paul's World generates a prediction:

1. **Check Confidence**: Must be >75%
2. **Check Direction**: BULLISH → buy, BEARISH → sell
3. **Extract Token**: From question (BTC, ETH, SOL, etc.)
4. **Execute Trade**: Top 3 most confident Pauls trade
5. **Position Sizing**: Max 10% of portfolio per trade
6. **Risk Management**: 5% stop loss, 15% take profit

### Example Trade Flow

```
User asks: "Will BTC hit $100K?"

Paul's World generates prediction:
  - Consensus: BULLISH (82% confidence)
  - Top Pauls: Visionary Paul (88%), Trader Paul (85%), Degen Paul (80%)

Paper trades executed:
  - Visionary Paul: Buy $1,000 BTC at $45,000
  - Trader Paul: Buy $1,000 BTC at $45,000
  - Degen Paul: Buy $1,000 BTC at $45,000

Later: BTC hits $48,000 (+6.7%)
  - All positions show +$67 profit
  - Trades remain open until stop/take-profit or prediction flip
```

## Configuration

### Per-Paul Settings

Each Paul has customizable settings:

```python
portfolio.enabled = True              # Enable/disable trading
portfolio.max_position_size = 0.10    # 10% max per trade
portfolio.stop_loss = 0.05            # 5% stop loss
portfolio.take_profit = 0.15          # 15% take profit
portfolio.min_confidence = 0.75       # Only trade >75% confidence
```

### Creating Custom Portfolios

```python
from paper_trading import PaperTradingManager

manager = PaperTradingManager()

# Create portfolio for specific Paul
portfolio = manager.create_portfolio(
    paul_name="My Custom Paul",
    initial_balance=50000.0,  # Start with $50K
    enabled=True
)

# Customize settings
portfolio.max_position_size = 0.20  # More aggressive (20% per trade)
portfolio.stop_loss = 0.10          # Wider stops (10%)
manager._save_portfolio(portfolio)
```

## Competitions

### Weekly Trading Competition

```bash
# Start 7-day competition
python paul_world.py paper competition start 7

# Check status
python paul_world.py paper competition status

# End and view results
python paul_world.py paper competition end
```

**Competition Rules:**
- All portfolios reset to $10,000
- Trade for 7 days
- Winner = highest ROI
- Top 10 tracked
- Results saved to history

### Competition Results

```
🏆 Competition Results
   Winner: Visionary Paul
   ROI: +156.3%

   Top 10:
      1. Visionary Paul (+156.3%)
      2. Trader Paul (+89.2%)
      3. Quant Paul (+67.1%)
      ...
```

## Proven Trader Badge

Pauls earn the **Proven Trader** badge when they achieve:
- **60%+ win rate**
- **50+ trades completed**
- **Positive overall P&L**

This identifies which Pauls actually know how to trade vs. which ones just get lucky.

### Why This Matters

Individual Pauls have different specialties:
- **Visionary Paul**: Good at long-term trends (high win rate, fewer trades)
- **Degen Paul**: High risk/high reward (volatile returns)
- **Trader Paul**: Consistent swing trading (steady returns)
- **Skeptic Paul**: Good at avoiding losses (high win rate, bearish bias)

Use **Proven Traders** as your signal source:
```bash
# Only follow top traders
python ask_pauls.py "Will ETH go up?" --pauls "Visionary Paul,Trader Paul,Quant Paul"
```

## Performance Metrics

### Tracked for Each Paul

| Metric | Description |
|--------|-------------|
| **Total Value** | Portfolio value (cash + positions) |
| **ROI** | Return on investment % |
| **Win Rate** | % of profitable trades |
| **Total Trades** | Number of completed trades |
| **Max Drawdown** | Largest peak-to-trough decline |
| **Sharpe Ratio** | Risk-adjusted returns |
| **Positions** | Current open positions |

### Leaderboard Rankings

Sorted by **ROI** (return on investment):
```
1. Visionary Paul  +245.6%  🏆
2. Trader Paul      +189.3%  🏆
3. Quant Paul       +134.7%  🏆
4. Degen Paul       +89.2%
5. Skeptic Paul     +67.4%   🏆
```

## Database Schema

Paper trading data stored in `data/paper_trading.db`:

- **paper_portfolios**: Current portfolio states
- **paper_trades**: All trade history (open and closed)
- **competitions**: Weekly competition results

## Integration with Social Media

When Pauls make profitable trades, they can auto-post:

```
🚀 Just closed BTC trade for +$234 profit (12.5%)!
Current portfolio: $11,450 (+14.5%)
Paper trading makes me look like a genius 😎
```

## Limitations

### What Paper Trading Can't Do

1. **Slippage**: Assumes perfect execution at stated price
2. **Liquidity**: Ignores market depth and order book
3. **Impact**: Large trades don't affect market price
4. **Borrowing**: No margin/leverage (yet)
5. **Fees**: Doesn't include trading fees (adds ~0.1-0.5% per trade)

**Real trading is harder** - expect 10-20% worse results with real money.

## Tips for Best Results

### 1. Run Longer Simulations
Paper trading needs **minimum 100 trades** for statistical significance:
- 100 trades = rough trend
- 500 trades = decent confidence
- 1000+ trades = reliable signal

### 2. Focus on Proven Traders
Don't follow all Pauls equally. Use leaderboard to identify consistent performers.

### 3. Check Max Drawdown
High ROI with 50% drawdown = risky. Look for steady returns.

### 4. Run Competitions
Weekly competitions surface top performers quickly.

### 5. Compare to Buy & Hold
If Pauls can't beat holding BTC/ETH, they're not adding value.

## Advanced Usage

### Custom Backtesting

```python
from paper_trading import PaperTradingManager
from datetime import datetime, timedelta

manager = PaperTradingManager()

# Simulate 30 days of trading
start_date = datetime.now() - timedelta(days=30)

for day in range(30):
    date = start_date + timedelta(days=day)
    
    # Get historical predictions for this date
    # Execute paper trades
    # Update prices
    
    manager.update_prices(historical_prices)

# Generate report
results = manager.get_leaderboard()
```

### Export Performance Data

```python
import json

# Export all performance data
with open('trading_performance.json', 'w') as f:
    data = {
        'portfolios': [p.to_dict() for p in manager.portfolios.values()],
        'trades': [t.to_dict() for t in manager.trades.values()],
    }
    json.dump(data, f, indent=2)
```

## Future Enhancements

### Planned for V2

- **Real-money integration**: Connect to exchanges (read-only first)
- **Leverage**: 2x-5x margin trading
- **Options**: Paper trade crypto options
- **Copy trading**: Auto-follow proven traders
- **Performance fees**: Reward good Pauls with real $PAULS tokens

## See Also

- [COMMANDS.md](COMMANDS.md) - CLI reference
- [PAUL_WORLD.md](PAUL_WORLD.md) - Paul's World overview
- [SOCIAL_MEDIA.md](SOCIAL_MEDIA.md) - Social integration
