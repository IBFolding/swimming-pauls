#!/usr/bin/env python3
"""
Swimming Pauls - Health Check
Check system status and diagnose issues

Usage:
    python health_check.py              # Full health check
    python health_check.py --quick      # Quick status
    python health_check.py --fix        # Auto-fix common issues
"""

import subprocess
import sys
import os
import socket
from pathlib import Path
import json

def check_port(port):
    """Check if port is in use."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0

def check_process(name, cmd_pattern):
    """Check if process is running."""
    try:
        result = subprocess.run(
            ['pgrep', '-f', cmd_pattern],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except:
        return False

def check_file_exists(path):
    """Check if file exists."""
    return Path(path).exists()

def check_directory_writable(path):
    """Check if directory is writable."""
    try:
        test_file = Path(path) / '.write_test'
        test_file.touch()
        test_file.unlink()
        return True
    except:
        return False

def health_check():
    """Run full health check."""
    print("\n" + "=" * 60)
    print("🦷 SWIMMING PAULS - HEALTH CHECK")
    print("=" * 60)
    
    issues = []
    warnings = []
    
    # Check Python version
    print("\n📋 Python:")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"  ✅ {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"  ❌ {version.major}.{version.minor}.{version.micro} (need 3.9+)")
        issues.append("Python version too old")
    
    # Check dependencies
    print("\n📦 Dependencies:")
    required = {
        'websockets': 'WebSocket support',
        'httpx': 'HTTP client',
        'numpy': 'Data processing',
        'pandas': 'Data analysis'
    }
    
    for module, purpose in required.items():
        try:
            __import__(module)
            print(f"  ✅ {module} ({purpose})")
        except ImportError:
            print(f"  ❌ {module} ({purpose}) - run: pip install {module}")
            issues.append(f"Missing dependency: {module}")
    
    # Check directories
    print("\n📁 Directories:")
    dirs = ['data', 'data/results', 'logs', 'config']
    base = Path(__file__).parent
    
    for d in dirs:
        path = base / d
        if path.exists():
            if check_directory_writable(path):
                print(f"  ✅ {d}/")
            else:
                print(f"  ⚠️  {d}/ (not writable)")
                warnings.append(f"{d}/ not writable")
        else:
            print(f"  ❌ {d}/ (missing)")
            issues.append(f"Missing directory: {d}/")
    
    # Check files
    print("\n📄 Key Files:")
    files = [
        ('local_agent.py', 'WebSocket server'),
        ('start.py', 'Launcher'),
        ('config.example.yaml', 'Example config'),
        ('requirements.txt', 'Dependencies list')
    ]
    
    for filename, purpose in files:
        if check_file_exists(base / filename):
            print(f"  ✅ {filename} ({purpose})")
        else:
            print(f"  ❌ {filename} ({purpose})")
            issues.append(f"Missing file: {filename}")
    
    # Check ports
    print("\n🔌 Ports:")
    ws_port = 8765
    ui_port = 3005
    
    ws_in_use = check_port(ws_port)
    ui_in_use = check_port(ui_port)
    
    if ws_in_use:
        print(f"  ⚠️  {ws_port} (WebSocket) - in use (agent may be running)")
    else:
        print(f"  ✅ {ws_port} (WebSocket) - available")
    
    if ui_in_use:
        print(f"  ⚠️  {ui_port} (UI) - in use (server may be running)")
    else:
        print(f"  ✅ {ui_port} (UI) - available")
    
    # Check data
    print("\n💾 Data:")
    results_dir = base / 'data' / 'results'
    if results_dir.exists():
        result_count = len(list(results_dir.glob('*.json')))
        print(f"  ✅ {result_count} prediction results")
    else:
        print(f"  ℹ️  No results yet")
    
    db_file = base / 'data' / 'predictions.db'
    if db_file.exists():
        size_mb = db_file.stat().st_size / (1024 * 1024)
        print(f"  ✅ predictions.db ({size_mb:.1f} MB)")
    else:
        print(f"  ℹ️  No database yet")
    
    # Summary
    print("\n" + "=" * 60)
    if not issues and not warnings:
        print("✅ ALL CHECKS PASSED")
        print("\nReady to run: python start.py")
    elif not issues:
        print("⚠️  WARNINGS FOUND")
        for w in warnings:
            print(f"   - {w}")
        print("\nCan still run, but some features may not work")
    else:
        print(f"❌ {len(issues)} ISSUES FOUND")
        for i in issues:
            print(f"   - {i}")
        print("\nFix issues before running")
    
    print("=" * 60)
    
    return len(issues) == 0

def quick_status():
    """Quick status check."""
    print("\n🦷 Swimming Pauls Status")
    print("-" * 40)
    
    # Check if running
    ws_running = check_process('local_agent', 'local_agent.py')
    ui_running = check_process('http.server', 'http.server 3005')
    
    if ws_running:
        print("🔌 WebSocket agent: RUNNING")
    else:
        print("🔌 WebSocket agent: STOPPED")
    
    if ui_running:
        print("🌐 UI server: RUNNING (http://localhost:3005)")
    else:
        print("🌐 UI server: STOPPED")
    
    # Quick data count
    results_dir = Path(__file__).parent / 'data' / 'results'
    if results_dir.exists():
        count = len(list(results_dir.glob('*.json')))
        print(f"💾 Predictions: {count}")
    
    if ws_running and ui_running:
        print("\n✅ System ready")
    elif ws_running:
        print("\n⚠️  UI not running - run: cd ui && python -m http.server 3005")
    else:
        print("\n❌ Not running - start with: python start.py")

def auto_fix():
    """Auto-fix common issues."""
    print("\n🔧 AUTO-FIX")
    print("-" * 40)
    
    base = Path(__file__).parent
    
    # Create directories
    dirs = ['data', 'data/results', 'logs', 'config']
    for d in dirs:
        path = base / d
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created {d}/")
    
    # Copy config if missing
    config = base / 'config.yaml'
    example = base / 'config.example.yaml'
    if not config.exists() and example.exists():
        import shutil
        shutil.copy(example, config)
        print("✅ Created config.yaml")
    
    print("\n✅ Auto-fix complete")
    print("Run health_check.py again to verify")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Health check for Swimming Pauls")
    parser.add_argument("--quick", action="store_true", help="Quick status only")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues")
    
    args = parser.parse_args()
    
    if args.quick:
        quick_status()
    elif args.fix:
        auto_fix()
    else:
        health_check()

if __name__ == "__main__":
    main()
