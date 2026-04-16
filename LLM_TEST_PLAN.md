# Swimming Pauls - LLM Integration Test Plan

## Overview
Test plan for verifying Swimming Pauls works with multiple LLM providers:
- **Ollama** (local, free)
- **OpenAI** (cloud, API key)
- **Anthropic** (cloud, API key)
- **OpenClaw's configured LLM** (inherits from user's OpenClaw setup)

---

## 1. LLM Provider Detection Tests

### Test 1.1: Check Available Providers
```bash
cd /Users/brain/.openclaw/workspace/swimming_pauls
python3 check_llm.py
```

**Expected Output:**
```
🔍 Swimming Pauls - LLM Provider Check
==================================================

📊 Available Providers:
------------------------------
  OLLAMA       ✅ Ready (if installed) / ❌ Not Available
  LMSTUDIO     ✅ Ready (if running) / ❌ Not Available
  OPENAI       ✅ Ready (if API key set) / ❌ Not Available
  ANTHROPIC    ✅ Ready (if API key set) / ❌ Not Available

🎯 Auto-Selected Provider:
------------------------------
  Provider: openai/anthropic/ollama (best available)
  Model: gpt-4o-mini/claude-3-haiku/llama3

🔧 Client Status:
------------------------------
  ✅ LLM Client is ready to use
  OR
  ⚠️  LLM Client not ready
```

### Test 1.2: Verify API Key Detection
```bash
# Test 1: No API keys set
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
python3 -c "from llm_client import LLMClient; c = LLMClient('openai'); print('API Key:', c.api_key)"
# Expected: API Key: None

# Test 2: OpenAI API key from env
export OPENAI_API_KEY="sk-test123"
python3 -c "from llm_client import LLMClient; c = LLMClient('openai'); print('API Key:', c.api_key[:10] + '...')"
# Expected: API Key: sk-test123...

# Test 3: Auto-detection
python3 -c "from llm_client import LLMClient; c = LLMClient(); print('Auto-selected:', c.auto_select_provider())"
# Expected: Best available provider
```

---

## 2. Individual LLM Provider Tests

### Test 2.1: Ollama (Local)
```bash
# Check if Ollama is installed and running
curl http://localhost:11434/api/tags 2>/dev/null | head -20

# Test with Swimming Pauls
python3 swimming_pauls.py \
  --predict "Will Bitcoin go up tomorrow?" \
  --provider ollama \
  --model llama3 \
  --pauls 5
```

**Expected:**
- [ ] Ollama responds within 30 seconds
- [ ] Returns prediction from Pauls
- [ ] No API errors

### Test 2.2: OpenAI (Cloud)
```bash
# Set API key
export OPENAI_API_KEY="your-key-here"

# Test with Swimming Pauls
python3 swimming_pauls.py \
  --predict "Will Ethereum hit $4000 this month?" \
  --provider openai \
  --model gpt-4o-mini \
  --pauls 10
```

**Expected:**
- [ ] Fast response (< 10 seconds)
- [ ] High-quality predictions
- [ ] Costs ~$0.002 per prediction

### Test 2.3: Anthropic (Cloud)
```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Test with Swimming Pauls
python3 swimming_pauls.py \
  --predict "Is Solana a good buy right now?" \
  --provider anthropic \
  --model claude-3-haiku-20240307 \
  --pauls 10
```

**Expected:**
- [ ] Fast response (< 10 seconds)
- [ ] Good reasoning in responses
- [ ] Costs ~$0.001 per prediction

---

## 3. OpenClaw Integration Tests

### Test 3.1: Read OpenClaw Config
```bash
# Check if OpenClaw config exists
ls -la ~/.openclaw/config.yaml 2>/dev/null || echo "No OpenClaw config found"

# Test reading API keys from OpenClaw config
python3 -c "
from llm_client import LLMClient
client = LLMClient(provider='openai')
key = client._get_openclaw_api_key()
print('Found OpenClaw API key:', 'Yes' if key else 'No')
"
```

### Test 3.2: Auto-Detect from OpenClaw
```bash
# If OpenClaw has API keys configured, Swimming Pauls should use them
python3 -c "
from llm_client import LLMClient

# Create client without explicit API key
client = LLMClient(provider='openai')

# Should auto-detect from OpenClaw config
print('Provider:', client.provider)
print('API Key present:', client.api_key is not None)
print('Is ready:', client.is_ready())
"
```

---

## 4. Auto-Selection Tests

### Test 4.1: Auto-Select Best Provider
```bash
# With multiple providers available
export OPENAI_API_KEY="sk-test"
# Ollama running locally

python3 -c "
from llm_client import LLMClient
client = LLMClient()
provider, model = client.auto_select_provider()
print(f'Selected: {provider} with {model}')
"

# Expected: openai with gpt-4o-mini (cloud is faster)
```

### Test 4.2: Fallback to Local
```bash
# Without cloud API keys
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
# Ollama running locally

python3 -c "
from llm_client import LLMClient
client = LLMClient()
provider, model = client.auto_select_provider()
print(f'Selected: {provider} with {model}')
"

# Expected: ollama with llama3 (local fallback)
```

---

## 5. Integration with Paul's World

### Test 5.1: World V2 with LLM
```bash
# Start World V2 server
cd pauls-world-v2 && npm start &

# Ask a question through the World API
curl -X POST http://localhost:3001/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Will BTC hit $100K?",
    "numPauls": 20,
    "provider": "auto"
  }'

# Expected: Returns consensus prediction using best available LLM
```

### Test 5.2: World V3 with LLM
```bash
# Start World V3 server
cd pauls-world-v3 && npm start &

# Ask a question through the World API
curl -X POST http://localhost:3002/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Is ETH bullish?",
    "numPauls": 20,
    "provider": "ollama"
  }'

# Expected: Returns prediction using Ollama
```

---

## 6. Error Handling Tests

### Test 6.1: No Providers Available
```bash
# Ensure no LLMs are available
unset OPENAI_API_KEY
unset ANTHROPIC_API_KEY
# Stop Ollama if running

python3 swimming_pauls.py --predict "Test" --pauls 3

# Expected: Graceful error message suggesting to:
# - Install Ollama, OR
# - Set OPENAI_API_KEY, OR
# - Configure OpenClaw with API keys
```

### Test 6.2: Invalid API Key
```bash
export OPENAI_API_KEY="invalid-key"

python3 swimming_pauls.py \
  --predict "Test" \
  --provider openai \
  --pauls 3

# Expected: Error message about invalid API key
# Should fallback to next available provider if configured
```

### Test 6.3: Ollama Not Running
```bash
# Ensure Ollama is not running
# Try to use it

python3 swimming_pauls.py \
  --predict "Test" \
  --provider ollama \
  --pauls 3

# Expected: Error message that Ollama is not running
# Suggestion to start Ollama
```

---

## 7. Performance Tests

### Test 7.1: Response Time Comparison
```bash
# Time each provider

echo "Testing Ollama (local)..."
time python3 swimming_pauls.py --predict "Test" --provider ollama --pauls 10

echo "Testing OpenAI (cloud)..."
time python3 swimming_pauls.py --predict "Test" --provider openai --pauls 10

echo "Testing Anthropic (cloud)..."
time python3 swimming_pauls.py --predict "Test" --provider anthropic --pauls 10
```

**Expected Results:**
- Ollama: 10-30 seconds (depends on hardware)
- OpenAI: 2-5 seconds
- Anthropic: 2-5 seconds

### Test 7.2: Concurrent Requests
```bash
# Test multiple simultaneous predictions
for i in {1..5}; do
  python3 swimming_pauls.py --predict "Test $i" --pauls 5 &
done
wait

# Expected: All complete without errors
```

---

## 8. Configuration Tests

### Test 8.1: Config File Priority
```bash
# Test 1: Config file sets provider
echo "llm:
  provider: openai
  providers:
    openai:
      model: gpt-4" > /tmp/test_config.yaml

# Test 2: Environment variable overrides
export SWIMMING_PAULS_PROVIDER=ollama

# Test 3: CLI flag overrides everything
python3 swimming_pauls.py --predict "Test" --provider anthropic

# Expected: CLI flag wins, then env var, then config file
```

### Test 8.2: Model Selection
```bash
# Test different models per provider

# OpenAI models
python3 swimming_pauls.py --predict "Test" --provider openai --model gpt-4o
python3 swimming_pauls.py --predict "Test" --provider openai --model gpt-4o-mini
python3 swimming_pauls.py --predict "Test" --provider openai --model gpt-3.5-turbo

# Anthropic models
python3 swimming_pauls.py --predict "Test" --provider anthropic --model claude-3-opus
python3 swimming_pauls.py --predict "Test" --provider anthropic --model claude-3-sonnet
python3 swimming_pauls.py --predict "Test" --provider anthropic --model claude-3-haiku

# Ollama models
python3 swimming_pauls.py --predict "Test" --provider ollama --model llama3
python3 swimming_pauls.py --predict "Test" --provider ollama --model qwen2.5:14b
```

---

## 9. End-to-End Integration Test

### Test 9.1: Full Workflow
```bash
#!/bin/bash
# full_integration_test.sh

echo "🧪 Swimming Pauls LLM Integration Test"
echo "======================================"

# 1. Check LLM availability
echo "1. Checking LLM providers..."
python3 check_llm.py

# 2. Test prediction with auto-selected provider
echo "2. Testing auto-selected provider..."
python3 swimming_pauls.py \
  --predict "Will Bitcoin go up tomorrow?" \
  --pauls 5 \
  --output /tmp/test_prediction.json

# 3. Verify output
echo "3. Verifying prediction output..."
if [ -f /tmp/test_prediction.json ]; then
  echo "✅ Prediction saved successfully"
  cat /tmp/test_prediction.json | head -20
else
  echo "❌ Prediction failed"
  exit 1
fi

# 4. Test with specific provider (if available)
echo "4. Testing specific providers..."

# Try Ollama
if curl -s http://localhost:11434 > /dev/null; then
  echo "Testing Ollama..."
  python3 swimming_pauls.py --predict "Test" --provider ollama --pauls 3
fi

# Try OpenAI (if key set)
if [ -n "$OPENAI_API_KEY" ]; then
  echo "Testing OpenAI..."
  python3 swimming_pauls.py --predict "Test" --provider openai --pauls 3
fi

echo "======================================"
echo "✅ All integration tests passed!"
```

---

## 10. Quick Verification Commands

```bash
# Check what's available
python3 check_llm.py

# Test with auto-selected provider
python3 swimming_pauls.py --predict "Will BTC pump?" --pauls 10

# Test specific providers
python3 swimming_pauls.py --predict "Will ETH hit $4K?" --provider ollama
python3 swimming_pauls.py --predict "Is SOL bullish?" --provider openai
python3 swimming_pauls.py --predict "Market sentiment?" --provider anthropic

# Check API endpoints
curl http://localhost:3001/api/stats
curl http://localhost:3002/api/stats

# Test World integration
curl -X POST http://localhost:3001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Test", "numPauls": 5}'
```

---

## Summary Checklist

Before releasing LLM integration:

- [ ] `check_llm.py` runs without errors
- [ ] Auto-detection works (picks best available provider)
- [ ] Ollama integration works (if installed)
- [ ] OpenAI integration works (with valid API key)
- [ ] Anthropic integration works (with valid API key)
- [ ] OpenClaw config is read correctly
- [ ] Graceful fallback when no providers available
- [ ] Error messages are helpful
- [ ] World V2 can use LLM for predictions
- [ ] World V3 can use LLM for predictions
- [ ] Response times are acceptable
- [ ] Concurrent requests work
- [ ] Configuration priority works (CLI > env > config)

---

*Last updated: 2026-04-16*
