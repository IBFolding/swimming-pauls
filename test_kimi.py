#!/usr/bin/env python3
"""
Quick test of Kimi integration without making actual API calls
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm_client import LLMClient

print("🧪 Testing Kimi Integration")
print("=" * 50)

# Test 1: Check if Kimi is in available providers
print("\n1. Checking provider list...")
client = LLMClient()
available = client.list_available_providers()

if "kimi" in available:
    print("   ✅ Kimi is in provider list")
else:
    print("   ❌ Kimi NOT in provider list")

# Test 2: Check auto-selection priority
print("\n2. Testing auto-selection with Kimi available...")
# Temporarily set a fake Kimi key to test auto-selection
os.environ["KIMI_API_KEY"] = "test-key"
client2 = LLMClient()
available2 = client2.list_available_providers()

if available2.get("kimi"):
    print("   ✅ Kimi detected as available")
    provider, model = client2.auto_select_provider()
    if provider == "kimi":
        print(f"   ✅ Auto-selected: {provider} with {model}")
    else:
        print(f"   ⚠️  Auto-selected: {provider} (Kimi should be first priority)")
else:
    print("   ❌ Kimi not detected")

# Test 3: Check Kimi endpoint
print("\n3. Checking Kimi endpoint...")
client3 = LLMClient(provider="kimi", api_key="test")
if "moonshot.cn" in client3.endpoint:
    print(f"   ✅ Kimi endpoint correct: {client3.endpoint}")
else:
    print(f"   ❌ Wrong endpoint: {client3.endpoint}")

# Test 4: Check Kimi model default
print("\n4. Checking default Kimi model...")
client4 = LLMClient(provider="kimi")
if client4.model == "kimi-k2-0714-preview":
    print(f"   ✅ Default model: {client4.model}")
else:
    print(f"   ⚠️  Model: {client4.model}")

# Cleanup
del os.environ["KIMI_API_KEY"]

print("\n" + "=" * 50)
print("✅ Kimi integration tests complete!")
print("\nTo use Kimi, set your API key:")
print("  export KIMI_API_KEY=your-moonshot-api-key")
print("\nGet your API key at: https://platform.moonshot.cn/")
