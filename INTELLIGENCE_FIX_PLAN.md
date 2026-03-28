# Swimming Pauls Intelligence Fix Plan
# Created: 2026-03-28
# Execute after app build is complete

## Root Cause Analysis

### Problem 1: 100% Neutral Predictions
**Root cause:** Ollama `qwen2.5:14b` takes ~55 seconds per inference on this MacBook Air. 
The auto_trader.py has a 45-second timeout on the curl call to Ollama. Most calls timeout, 
returning empty string. The parsing logic defaults to `neutral` with 0.75 confidence.

**Fix:**
- Increase curl timeout to 120 seconds in auto_trader.py
- OR switch to a smaller/faster model (qwen2.5:7b or qwen2.5:3b)
- Better: Use Ollama's Python library (httpx async) with proper streaming instead of subprocess curl
- Make the prompt shorter/more constrained to reduce token generation time
- Add `num_predict: 30` (currently 60) — we only need "SENTIMENT: bullish | CONFIDENCE: 80"

### Problem 2: 87% Flat Trades ($0 PnL)
**Root cause:** Both entry and exit prices come from DEFAULT_PRICES fallback dict.
The crypto-price skill is failing (subprocess timeout or script error), so everything 
falls back to stale hardcoded prices. Entry at $180 (AAPL default), exit at $180 = $0.

**Fix:**
- Update DEFAULT_PRICES to current real prices (BTC ~$87K, ETH ~$2050, etc.)
- Fix the price fetching — use CoinGecko API directly via httpx instead of shelling out to a skill script
- Add price staleness detection: if price hasn't changed in 10+ fetches, flag it
- For stocks (AAPL, TSLA, NVDA, SPY, QQQ): use Yahoo Finance or remove them from crypto trading symbols
- Separate crypto symbols from stock symbols in config

### Problem 3: 0 Predictions Resolved
**Root cause:** The auto_resolver.py daemon wasn't running. It needs to be started separately.
Also, resolve_predictions.py resolves against data/results/ JSON files (from the WebSocket 
simulation), not against paul_learning.db predictions. These are two different systems.

**Fix:**
- Make auto_trader.py self-resolving: after a trade closes, automatically call 
  `learning.resolve_prediction(pred_id, outcome, accuracy)` using the trade's actual PnL
- Store pred_id with each trade so we can link predictions to outcomes
- Add a batch resolver that goes through closed trades and resolves their linked predictions
- Start auto_resolver as part of `start.py`

### Problem 4: Portfolios All Show $0
**Root cause:** The paper_portfolios table stores JSON data, but the portfolio objects 
aren't being updated when trades close. The close_trade() method in paper_trading.py 
updates the in-memory portfolio, but it's saving via _save_portfolio() which stores the 
JSON. The issue is that portfolios were mass-reset during the cleanup on March 24.

**Fix:**
- Build a portfolio reconciliation script that recalculates portfolio stats from 
  actual closed trades in paper_trades table
- Run it once to fix existing data
- Ensure close_trade() properly persists portfolio updates

### Problem 5: AAPL $819K PnL Anomaly  
**Root cause:** Some AAPL trades entered at extremely low prices (near $0) due to 
corrupted data, then exited at $180 (default price), creating massive fake profits.
This is the same class of bug as the trillion-dollar PnL we fixed before.

**Fix:**
- Run data cleanup: invalidate trades where entry_price < reasonable minimum for the symbol
- Add symbol-specific price ranges (BTC: $10K-$500K, ETH: $500-$20K, AAPL: $50-$500, etc.)
- Reject trades outside these ranges

## Execution Order

### Step 1: Quick Fixes (15 min)
1. Update DEFAULT_PRICES to current market prices
2. Increase Ollama timeout to 120s
3. Reduce num_predict to 30
4. Update SYMBOLS list — separate crypto from stocks

### Step 2: Price Feed Fix (20 min)
1. Replace subprocess crypto-price calls with direct CoinGecko httpx calls
2. Add Yahoo Finance fallback for stock symbols
3. Add price staleness detection
4. Test price_feed.py actually gets real prices

### Step 3: LLM Response Fix (15 min)
1. Improve the prompt to be more directive (force a non-neutral response)
2. Add response validation — if response doesn't contain bullish/bearish, retry once
3. Consider using qwen2.5:7b for speed (test quality first)
4. Switch from subprocess curl to httpx async

### Step 4: Prediction Resolution (20 min)
1. Link trade IDs to prediction IDs in auto_trader.py
2. Auto-resolve predictions when trades close
3. Build batch resolver for existing unresolved predictions
4. Wire into paul_accuracy and domain_stats tables

### Step 5: Data Cleanup (10 min)
1. Invalidate anomalous AAPL trades
2. Reconcile portfolios from actual trade data
3. Reset paul_accuracy from resolved predictions

### Step 6: Restart Everything (5 min)
1. Start price_feed.py
2. Start auto_trader.py (with fixes)
3. Start auto_resolver.py --daemon
4. Verify predictions are non-neutral
5. Verify prices are updating
6. Verify predictions resolve after trades close

## Expected Outcome
- Predictions: Mix of bullish/bearish/neutral (not 100% neutral)
- Trades: Real PnL based on actual price movements
- Learning: Predictions resolve, accuracy tracks, Pauls improve
- Portfolios: Accurate balance/PnL reflecting trade history
