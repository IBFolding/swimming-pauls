"""Test individual tools properly."""
import asyncio
import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls/skills')

from data_tools import TOOLS

async def test_all_tools():
    print("Testing all 18+ Swimming Pauls data tools...\n")
    
    test_cases = {
        "web_search": {"query": "bitcoin", "limit": 5},
        "crypto_price": {"symbol": "BTC"},
        "stock_price": {"symbol": "AAPL"},
        "news": {"query": "crypto"},
        "social_sentiment": {"keyword": "bitcoin"},
        "onchain": {"token": "ETH"},
        "dex_volume": {"token": "ETH"},
        "whale_tracking": {"token": "ETH"},
        "gas_price": {"chain": "ethereum"},
        "token_unlocks": {"token": "ARB"},
        "options_flow": {"symbol": "AAPL"},
        "futures": {"symbol": "BTC"},
        "forex": {"base": "USD", "quote": "EUR"},
        "google_trends": {"keyword": "bitcoin"},
        "sec_filings": {"ticker": "AAPL"},
        "weather": {"location": "New York"},
        "election_polls": {"race": "president"},
        "sports_odds": {"sport": "nfl"},
        "economic_calendar": {"country": "US"},
    }
    
    passed = 0
    failed = 0
    
    for name, kwargs in test_cases.items():
        tool = TOOLS.get(name)
        if not tool:
            print(f"❌ {name}: Tool not found in registry")
            failed += 1
            continue
            
        # Find the correct method
        method = None
        for attr in dir(tool):
            if attr.startswith('get_') or attr == 'search':
                method = getattr(tool, attr)
                break
        
        if not method:
            print(f"❌ {name}: No execution method found")
            failed += 1
            continue
        
        try:
            result = await method(**kwargs)
            if result.success:
                print(f"✅ {name}: {result.source}")
                passed += 1
            else:
                print(f"❌ {name}: {result.error}")
                failed += 1
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
            failed += 1
    
    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"Total tools tested: {len(test_cases)}")
    
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(test_all_tools())
    sys.exit(0 if success else 1)
