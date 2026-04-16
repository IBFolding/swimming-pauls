# Swimming Pauls - Comprehensive Test Plan

## Overview
This test plan covers all components of Swimming Pauls: Terminal, World (V2 & V3), Trading, and Payments.

---

## 1. TERMINAL (Main App)

### 1.1 Core Prediction Engine
```bash
# Test basic prediction
python swimming_pauls.py --predict "Will BTC hit $100K by end of month?"

# Test batch prediction
python swimming_pauls.py --batch --file test_questions.txt

# Test with specific Pauls
python swimming_pauls.py --predict "ETH price?" --pauls 50
```

**Expected Results:**
- [ ] Returns consensus prediction
- [ ] Shows confidence level
- [ ] Lists individual Paul responses
- [ ] Completes in < 30 seconds

### 1.2 WebSocket Server
```bash
# Start WebSocket server
cd /Users/brain/.openclaw/workspace/swimming_pauls
python local_agent.py

# Test connection
python test_ws.py
```

**Expected Results:**
- [ ] Server starts on port 8765
- [ ] Accepts WebSocket connections
- [ ] Broadcasts predictions to all clients
- [ ] Handles disconnections gracefully

### 1.3 Database/SQLite
```bash
# Check database integrity
python -c "import sqlite3; conn = sqlite3.connect('data/predictions.db'); print('OK')"

# Verify tables exist
python -c "
import sqlite3
conn = sqlite3.connect('data/predictions.db')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")
print(cursor.fetchall())
"
```

**Expected Tables:**
- [ ] predictions
- [ ] pauls
- [ ] consensus
- [ ] accuracy_tracking

---

## 2. WORLD SIMULATION

### 2.1 Paul's World V2 (Modern)
```bash
# Start V2 server
cd /Users/brain/.openclaw/workspace/swimming_pauls/pauls-world-v2
npm start

# Test API endpoints
curl http://localhost:3001/api/world
curl http://localhost:3001/api/stats
curl http://localhost:3001/api/leaderboard
```

**Expected Results:**
- [ ] Server runs on port 3001
- [ ] WebSocket accepts connections
- [ ] 1000 Pauls simulated
- [ ] Real-time updates every 100ms
- [ ] All UI panels functional (Diary, Social, Create, Chat)

### 2.2 Paul's World V3 (8-Bit)
```bash
# Start V3 server
cd /Users/brain/.openclaw/workspace/swimming_pauls/pauls-world-v3
npm start

# Test API
curl http://localhost:3002/api/world
curl http://localhost:3002/api/stats
```

**Expected Results:**
- [ ] Server runs on port 3002
- [ ] 8-bit pixel art renders correctly
- [ ] Grid-based movement
- [ ] Same features as V2

### 2.3 World Integration Tests
```bash
# Test cross-communication between Terminal and World
curl -X POST http://localhost:3001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Will BTC pump?", "numPauls": 50}'
```

---

## 3. TRADING SYSTEM

### 3.1 Paper Trading
```bash
# Run paper trading test
python paper_trading.py --test

# Check P&L report
python pnl_report.py --paper
```

**Expected Results:**
- [ ] Simulates trades without real money
- [ ] Tracks P&L accurately
- [ ] Logs all transactions
- [ ] Generates reports

### 3.2 Live Trading (if enabled)
```bash
# WARNING: Only run with small amounts
python auto_trader.py --mode paper --test

# Verify no real trades executed
python check_pnl.py --verify-test-mode
```

**Expected Results:**
- [ ] Test mode doesn't execute real trades
- [ ] All trades logged
- [ ] Risk limits enforced

### 3.3 Trading API
```bash
# Test trading endpoints
curl http://localhost:3001/api/trades
curl http://localhost:3001/api/positions
curl http://localhost:3001/api/balance
```

---

## 4. PAYMENTS/CREDITS SYSTEM

### 4.1 Credit System
```bash
# Test credit deduction
curl -X POST http://localhost:3001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Test", "credits": 1}'

# Check credit balance
curl http://localhost:3001/api/credits
```

**Expected Results:**
- [ ] Credits deducted per question
- [ ] Balance tracked correctly
- [ ] Free credits replenished daily
- [ ] Premium credits purchased correctly

### 4.2 Payment Integration (if applicable)
```bash
# Test payment webhook (if Stripe/similar integrated)
curl -X POST http://localhost:3001/webhook/payment \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

---

## 5. LOCAL-ONLY MODE

### 5.1 Offline Functionality
```bash
# Test without internet
# Disconnect wifi, then:
python swimming_pauls.py --local --predict "Test question"
```

**Expected Results:**
- [ ] Uses local LLM (Ollama if available)
- [ ] Falls back to cached Pauls
- [ ] Works without API calls
- [ ] Data saved locally

### 5.2 Local Data Feeds
```bash
# Test local data sources
python local_data_feeds.py --test

# Verify data caching
ls -la data/cache/
```

---

## 6. INTEGRATION TESTS

### 6.1 End-to-End Flow
```bash
# 1. Start all services
./start_all.sh

# 2. Run full test suite
python test_full_integration.py

# 3. Verify all components talk to each other
python test_cross_component.py
```

### 6.2 Load Testing
```bash
# Test with many concurrent users
python test_capacity.py --users 100 --duration 60

# Monitor resource usage
htop / activity monitor
```

**Expected Results:**
- [ ] Handles 100+ concurrent connections
- [ ] Memory usage stable
- [ ] No crashes under load
- [ ] Response time < 2s

---

## 7. UI/UX TESTS

### 7.1 Browser Compatibility
Test these URLs in Chrome, Firefox, Safari, Edge:
- http://localhost:3001 (World V2)
- http://localhost:3002 (World V3)
- file:///.../swimming_pauls/app/index.html (Terminal)

**Check:**
- [ ] Layout renders correctly
- [ ] WebSocket connections work
- [ ] Responsive design on mobile
- [ ] No console errors

### 7.2 Mobile Responsiveness
```bash
# Use Chrome DevTools to test:
# - iPhone 12 Pro
# - iPad Air
# - Pixel 5
```

---

## 8. DATA INTEGRITY TESTS

### 8.1 Prediction Accuracy Tracking
```bash
# Verify accuracy calculations
python resolve_predictions.py --verify-only

# Check historical data
python prediction_history.py --stats
```

### 8.2 Backup/Recovery
```bash
# Test database backup
cp data/predictions.db data/predictions.db.backup

# Test restore
rm data/predictions.db
cp data/predictions.db.backup data/predictions.db
```

---

## 9. SECURITY TESTS

### 9.1 API Security
```bash
# Test rate limiting
curl -X POST http://localhost:3001/api/ask -d '{}' # 100 times

# Test authentication (if enabled)
curl http://localhost:3001/api/admin # Should fail without auth
```

### 9.2 Input Validation
```bash
# Test SQL injection protection
curl -X POST http://localhost:3001/api/ask \
  -d '{"question": "\'; DROP TABLE predictions; --"}'

# Test XSS protection
python swimming_pauls.py --predict "<script>alert('xss')</script>"
```

---

## 10. DEPLOYMENT TESTS

### 10.1 Fresh Install
```bash
# Simulate fresh install
rm -rf node_modules data/*.db __pycache__
./install-and-run.sh
```

### 10.2 Update Process
```bash
# Test update from previous version
git pull
pip install -r requirements.txt
npm install
python migrate_db.py
```

---

## QUICK TEST SCRIPT

Save this as `run_all_tests.sh`:

```bash
#!/bin/bash
set -e

echo "=== Swimming Pauls Test Suite ==="

# 1. Unit Tests
echo "Running unit tests..."
python -m pytest tests/ -v || true

# 2. API Tests
echo "Testing API endpoints..."
curl -s http://localhost:3001/api/stats > /dev/null && echo "✓ V2 API OK" || echo "✗ V2 API FAIL"
curl -s http://localhost:3002/api/stats > /dev/null && echo "✓ V3 API OK" || echo "✗ V3 API FAIL"

# 3. WebSocket Test
echo "Testing WebSocket..."
python test_ws.py && echo "✓ WebSocket OK" || echo "✗ WebSocket FAIL"

# 4. Database Test
echo "Testing database..."
python -c "import sqlite3; conn = sqlite3.connect('data/predictions.db'); conn.close()" && echo "✓ DB OK" || echo "✗ DB FAIL"

# 5. Prediction Test
echo "Testing prediction engine..."
python swimming_pauls.py --predict "Test" --quick && echo "✓ Predictions OK" || echo "✗ Predictions FAIL"

echo "=== Tests Complete ==="
```

---

## TROUBLESHOOTING

### Common Issues:

1. **Port already in use**
   ```bash
   lsof -ti:3001 | xargs kill -9
   lsof -ti:3002 | xargs kill -9
   lsof -ti:8765 | xargs kill -9
   ```

2. **Database locked**
   ```bash
   rm data/*.db-journal data/*.db-wal
   ```

3. **Missing dependencies**
   ```bash
   pip install -r requirements.txt
   cd pauls-world-v2 && npm install
   cd pauls-world-v3 && npm install
   ```

4. **Permission errors**
   ```bash
   chmod +x *.sh
   chmod +x *.py
   ```

---

## TEST CHECKLIST

Before release, verify:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] API endpoints respond correctly
- [ ] WebSocket connections stable
- [ ] Database operations work
- [ ] UI renders in all major browsers
- [ ] Mobile responsive
- [ ] No memory leaks (monitor for 1 hour)
- [ ] Load test passed (100 concurrent users)
- [ ] Security tests passed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated

---

## RUNNING TESTS

### Quick Test (2 minutes):
```bash
./run_all_tests.sh
```

### Full Test Suite (10 minutes):
```bash
python -m pytest tests/ -v
python test_capacity.py
python test_security.py
```

### Manual Testing:
1. Open http://localhost:3001 - verify World V2
2. Open http://localhost:3002 - verify World V3
3. Ask a prediction question
4. Check diary entries appear
5. Check social feed updates
6. Create a new Paul (costs 2 credits)
7. Ask chat question (costs 1 credit)
8. Verify credit deduction

---

*Last updated: 2026-04-16*
