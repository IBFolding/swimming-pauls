#!/usr/bin/env python3
"""Swimming Pauls - Pre-Launch Test Suite"""
import sqlite3
import json
import subprocess
import sys
import asyncio
from pathlib import Path
from datetime import datetime

print("=" * 70)
print("🦷 SWIMMING PAULS - PRE-LAUNCH TEST SUITE")
print("=" * 70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

results = []

def test(name, status, details=""):
    """Record test result."""
    emoji = "✅" if status else "❌"
    results.append((name, status, details))
    print(f"{emoji} {name}")
    if details:
        print(f"   {details}")

# Test 1: Database Integrity
print("📊 TEST 1: Database Integrity")
print("-" * 40)
try:
    conn = sqlite3.connect('data/paper_trading.db', timeout=5)
    cursor = conn.cursor()
    
    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    
    required_tables = ['paper_trades', 'paper_portfolios', 'competitions']
    missing = [t for t in required_tables if t not in tables]
    
    if missing:
        test("Database Tables", False, f"Missing: {', '.join(missing)}")
    else:
        test("Database Tables", True, f"Found: {', '.join(tables)}")
    
    # Check for corrupt data
    cursor.execute('SELECT COUNT(*) FROM paper_trades')
    trade_count = cursor.fetchone()[0]
    test("Trade Count", trade_count > 0, f"{trade_count:,} trades")
    
    cursor.execute('SELECT COUNT(*) FROM paper_portfolios')
    portfolio_count = cursor.fetchone()[0]
    test("Portfolio Count", portfolio_count > 0, f"{portfolio_count:,} portfolios")
    
    # Check recent activity
    cursor.execute("SELECT MAX(created_at) FROM paper_trades")
    latest = cursor.fetchone()[0]
    test("Recent Activity", latest is not None, f"Latest: {latest[:19] if latest else 'N/A'}")
    
    conn.close()
except Exception as e:
    test("Database Connection", False, str(e))

print()

# Test 2: Active Processes
print("⚙️  TEST 2: Active Processes")
print("-" * 40)
try:
    ps_output = subprocess.run(['ps', 'aux'], capture_output=True, text=True).stdout
    
    auto_trader_running = 'auto_trader.py' in ps_output
    price_feed_running = 'price_feed.py' in ps_output
    
    test("Auto-Trader Running", auto_trader_running)
    test("Price Feed Running", price_feed_running)
    
    if auto_trader_running:
        # Get PID
        for line in ps_output.split('\n'):
            if 'auto_trader.py' in line and 'grep' not in line:
                pid = line.split()[1]
                test("Auto-Trader PID", True, pid)
                break
    
except Exception as e:
    test("Process Check", False, str(e))

print()

# Test 3: Real Price Integration
print("💰 TEST 3: Real Price Integration")
print("-" * 40)
try:
    conn = sqlite3.connect('data/paper_trading.db')
    cursor = conn.cursor()
    
    # Check for trades with price variations
    cursor.execute("SELECT data FROM paper_trades WHERE closed_at IS NOT NULL LIMIT 100")
    variations = 0
    for row in cursor.fetchall():
        data = json.loads(row[0])
        entry = data.get('entry_price', 0)
        exit_p = data.get('exit_price', 0)
        if entry != exit_p and exit_p != 0:
            variations += 1
    
    test("Price Variations in Trades", variations > 0, f"{variations} trades with price movement")
    
    # Check for non-zero PnL
    cursor.execute("SELECT data FROM paper_trades WHERE closed_at IS NOT NULL")
    nonzero_pnl = 0
    for row in cursor.fetchall():
        data = json.loads(row[0])
        if data.get('pnl', 0) != 0:
            nonzero_pnl += 1
    
    test("Non-Zero PnL Trades", nonzero_pnl > 0, f"{nonzero_pnl} trades with calculated PnL")
    
    conn.close()
except Exception as e:
    test("Price Integration", False, str(e))

print()

# Test 4: File Structure
print("📁 TEST 4: File Structure")
print("-" * 40)
required_files = [
    'auto_trader.py',
    'price_feed.py',
    'paper_trading.py',
    'paul_world.py',
    'leaderboard.py',
    'data/paper_trading.db'
]

for file in required_files:
    exists = Path(file).exists()
    test(f"{file}", exists)

print()

# Test 5: Leaderboard Functionality
print("🏆 TEST 5: Leaderboard")
print("-" * 40)
try:
    result = subprocess.run(
        ['python3', 'leaderboard.py'],
        capture_output=True, text=True, timeout=10
    )
    has_output = len(result.stdout) > 0 and 'Leaderboard' in result.stdout
    test("Leaderboard Command", has_output)
except Exception as e:
    test("Leaderboard", False, str(e))

print()

# Test 6: Price Feed Logs
print("📈 TEST 6: Price Feed Health")
print("-" * 40)
try:
    log_path = Path('logs/price_feed.log')
    if log_path.exists():
        # Get last 5 lines
        with open(log_path, 'r') as f:
            lines = f.readlines()
            last_lines = lines[-5:]
        
        # Check for recent activity
        has_updates = any('Updated' in line for line in last_lines)
        test("Recent Updates", has_updates)
        
        # Check for errors
        errors = sum(1 for line in last_lines if 'error' in line.lower() or 'fail' in line.lower())
        test("No Recent Errors", errors == 0, f"{errors} errors in last 5 log lines")
    else:
        test("Price Feed Log", False, "Log file not found")
except Exception as e:
    test("Log Check", False, str(e))

print()

# Test 7: Competition Mode
print("🏁 TEST 7: Competition Mode")
print("-" * 40)
try:
    conn = sqlite3.connect('data/paper_trading.db')
    cursor = conn.cursor()
    
    # Check if competition is active
    cursor.execute('SELECT COUNT(*) FROM competitions')
    comp_count = cursor.fetchone()[0]
    test("Competition Table", True, f"{comp_count} competitions recorded")
    
    # Check portfolios are in competition mode
    cursor.execute('SELECT data FROM paper_portfolios LIMIT 5')
    enabled_count = 0
    for row in cursor.fetchall():
        data = json.loads(row[0])
        if data.get('enabled'):
            enabled_count += 1
    
    test("Portfolios Enabled", enabled_count > 0, f"{enabled_count}/5 sampled portfolios active")
    
    conn.close()
except Exception as e:
    test("Competition Check", False, str(e))

print()

# Test 8: Data Backup Capability
print("💾 TEST 8: Data Export")
print("-" * 40)
try:
    result = subprocess.run(
        ['python3', 'export_data.py', '--predictions', '--format', 'json'],
        capture_output=True, text=True, timeout=10
    )
    test("Export Function", result.returncode == 0)
except Exception as e:
    test("Export", False, str(e))

print()

# Test 9: Skill Integration (if available)
print("🔌 TEST 9: OpenClaw Skill Integration")
print("-" * 40)
try:
    skill_path = Path('openclaw-skill/skill.py')
    test("Skill File Exists", skill_path.exists())
    
    if skill_path.exists():
        content = skill_path.read_text()
        has_bridge = 'skill_bridge' in content
        test("Skill Bridge Import", has_bridge)
except Exception as e:
    test("Skill Check", False, str(e))

print()

# Summary
print("=" * 70)
print("📋 TEST SUMMARY")
print("=" * 70)
passed = sum(1 for _, status, _ in results if status)
total = len(results)
print(f"Passed: {passed}/{total} ({passed/total*100:.0f}%)")
print()

failed = [(name, details) for name, status, details in results if not status]
if failed:
    print("❌ FAILED TESTS:")
    for name, details in failed:
        print(f"   - {name}: {details}")
else:
    print("✅ ALL TESTS PASSED!")

print()
print("=" * 70)
if passed == total:
    print("🚀 READY FOR LAUNCH!")
elif passed / total >= 0.8:
    print("⚠️  MOSTLY READY - Review failed tests")
else:
    print("❌ NOT READY - Fix issues before launch")
print("=" * 70)
