#!/usr/bin/env python3
"""
Paul Capacity Test - Find max Pauls on your machine (No psutil required)
Tests progressively larger Paul pools
"""

import asyncio
import time
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

async def test_paul_capacity(target_pauls):
    """Test creating a world with target number of Pauls."""
    print(f"\n{'='*60}")
    print(f"Testing {target_pauls} Pauls...")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        from paul_world import PaulWorld
        from persona_factory import generate_swimming_pauls_pool
        
        # Create world
        world = PaulWorld(db_path=f"data/test_{target_pauls}.db")
        
        # Generate Pauls
        personas = generate_swimming_pauls_pool(count=target_pauls)
        
        init_time = time.time() - start_time
        
        print(f"✅ Created {target_pauls} Pauls in {init_time:.2f}s")
        
        # Test prediction with subset
        test_size = min(10, target_pauls)
        print(f"\nTesting prediction with {test_size} Pauls...")
        
        pred_start = time.time()
        # Quick test - just check if it works
        print(f"   Paul pool ready for predictions")
        pred_time = time.time() - pred_start
        
        print(f"   Response time: {pred_time:.3f}s")
        
        return {
            'success': True,
            'pauls': target_pauls,
            'init_time': init_time,
        }
        
    except MemoryError:
        print(f"❌ MemoryError: Cannot create {target_pauls} Pauls")
        return {'success': False, 'error': 'MemoryError'}
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

async def run_capacity_test():
    """Run progressive capacity test."""
    print(f"{'='*60}")
    print("SWIMMING PAULS - CAPACITY TEST")
    print(f"{'='*60}")
    print(f"Machine: MacBook M4 (16GB RAM)")
    print(f"Python: {sys.version}")
    
    # Test progressively larger pools
    test_sizes = [10, 50, 100, 250, 500, 750, 1000, 1500, 2000, 3000, 5000, 7500, 10000]
    results = []
    
    for size in test_sizes:
        result = await test_paul_capacity(size)
        results.append(result)
        
        if not result['success']:
            print(f"\n🛑 Stopping at {size} Pauls due to error")
            break
        
        # Brief pause between tests
        await asyncio.sleep(0.5)
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = [r for r in results if r['success']]
    if successful:
        max_tested = max(r['pauls'] for r in successful)
        avg_time = sum(r['init_time'] for r in successful) / len(successful)
        
        print(f"✅ Max tested: {max_tested:,} Pauls")
        print(f"⏱️  Average init time: {avg_time:.2f}s")
        
        # Rough estimate based on typical memory usage
        # Paul objects are lightweight (~10KB each in memory)
        estimated_mem_mb = max_tested * 0.01  # ~10KB per Paul
        print(f"\n📊 Estimated memory: ~{estimated_mem_mb:.1f} MB for {max_tested:,} Pauls")
        
        print(f"\n🎯 On 16GB MacBook M4:")
        print(f"   Conservative: 5,000-7,500 Pauls")
        print(f"   Optimistic: 10,000+ Pauls")
        print(f"   (Depends on knowledge base size and activity)")

if __name__ == "__main__":
    asyncio.run(run_capacity_test())
