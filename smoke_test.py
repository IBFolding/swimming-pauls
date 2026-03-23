#!/usr/bin/env python3
"""
Quick smoke test for Swimming Pauls v2.1
Verifies core functionality without running full simulations
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules import successfully."""
    print("Testing imports...")
    
    modules = [
        'config_loader',
        'prediction_history',
        'chat_interface',
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except Exception as e:
            print(f"  ❌ {module}: {e}")
            failed.append(module)
    
    return len(failed) == 0

def test_config():
    """Test configuration loading."""
    print("\nTesting config...")
    
    try:
        from config_loader import load_config, DEFAULT_CONFIG
        config = load_config()
        print(f"  ✅ Config loaded")
        print(f"     Default Pauls: {config.get('defaults', {}).get('pauls', 'N/A')}")
        return True
    except Exception as e:
        print(f"  ❌ Config failed: {e}")
        return False

def test_data_directories():
    """Test that data directories exist or can be created."""
    print("\nTesting data directories...")
    
    dirs = ['data', 'data/results', 'logs']
    base = Path(__file__).parent
    
    all_good = True
    for d in dirs:
        path = base / d
        try:
            path.mkdir(parents=True, exist_ok=True)
            # Test writable
            test_file = path / '.write_test'
            test_file.touch()
            test_file.unlink()
            print(f"  ✅ {d}/")
        except Exception as e:
            print(f"  ❌ {d}/: {e}")
            all_good = False
    
    return all_good

def test_version():
    """Test version is correct."""
    print("\nTesting version...")
    
    try:
        # Read version directly from file
        init_file = Path(__file__).parent / '__init__.py'
        with open(init_file) as f:
            content = f.read()
            for line in content.split('\n'):
                if '__version__' in line:
                    version = line.split('=')[1].strip().strip('"\'')
                    print(f"  ✅ Version: {version}")
                    return version == "2.1.0"
        print("  ❌ Version not found in __init__.py")
        return False
    except Exception as e:
        print(f"  ❌ Version check failed: {e}")
        return False

def main():
    print("=" * 60)
    print("🦷 SWIMMING PAULS v2.1 - SMOKE TEST")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Config", test_config),
        ("Data Directories", test_data_directories),
        ("Version", test_version),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(r for _, r in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Ready to run: python start.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Run: python setup.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
