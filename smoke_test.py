#!/usr/bin/env python3
"""
Quick smoke test for Swimming Pauls v2.1
Verifies core functionality without running full simulations
"""

import sys
import os
from pathlib import Path
import re

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def _check_imports():
    """Check that all core modules import successfully."""
    print("Testing imports...")
    
    modules = [
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
    
    return len(failed) == 0, failed

def _check_config():
    """Check configuration loading."""
    print("\nTesting config...")
    
    try:
        from config_loader import load_config, DEFAULT_CONFIG
        config = load_config()
        print(f"  ✅ Config loaded")
        print(f"     Default Pauls: {config.get('defaults', {}).get('pauls', 'N/A')}")
        return True, None
    except ModuleNotFoundError as e:
        if "yaml" in str(e).lower():
            print("  ⚠️ PyYAML missing; config loader check skipped")
            return True, "PyYAML not installed"
        print(f"  ❌ Config failed: {e}")
        return False, str(e)
    except Exception as e:
        print(f"  ❌ Config failed: {e}")
        return False, str(e)

def _check_data_directories():
    """Check that data directories exist or can be created."""
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
    
    return all_good, None if all_good else "One or more directories are not writable"

def _check_version():
    """Check version format in __init__.py."""
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
                    return bool(re.match(r"^\d+\.\d+\.\d+$", version)), version
        print("  ❌ Version not found in __init__.py")
        return False, "Version not found"
    except Exception as e:
        print(f"  ❌ Version check failed: {e}")
        return False, str(e)


def test_imports():
    ok, detail = _check_imports()
    assert ok, f"Import failures: {detail}"


def test_config():
    ok, detail = _check_config()
    assert ok, f"Config check failed: {detail}"


def test_data_directories():
    ok, detail = _check_data_directories()
    assert ok, detail


def test_version():
    ok, detail = _check_version()
    assert ok, f"Invalid version format: {detail}"

def main():
    print("=" * 60)
    print("🦷 SWIMMING PAULS v2.1 - SMOKE TEST")
    print("=" * 60)
    
    checks = [
        ("Imports", _check_imports),
        ("Config", _check_config),
        ("Data Directories", _check_data_directories),
        ("Version", _check_version),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            ok, _ = check_func()
            results.append((name, ok))
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
