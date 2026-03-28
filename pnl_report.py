#!/usr/bin/env python3
"""Comprehensive PnL Investigation Report for Swimming Pauls"""
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('data/paper_trading.db')
cursor = conn.cursor()

print("=" * 60)
print("🦷 SWIMMING PAULS - PnL INVESTIGATION REPORT")
print("=" * 60)
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Database Overview
cursor.execute("SELECT COUNT(*) FROM paper_trades")
total_trades = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE closed_at IS NULL")
open_trades = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE closed_at IS NOT NULL")
closed_trades = cursor.fetchone()[0]

print("📊 DATABASE OVERVIEW")
print("-" * 40)
print(f"Total trade records: {total_trades:,}")
print(f"Open positions: {open_trades:,}")
print(f"Closed trades: {closed_trades:,}")
print()

# PnL Analysis
print("💰 PnL ANALYSIS")
print("-" * 40)

cursor.execute("SELECT data FROM paper_trades WHERE closed_at IS NOT NULL")
zero_pnl = 0
nonzero_pnl = 0
total_pnl = 0
winners = 0
losers = 0
by_side = {'buy': {'count': 0, 'pnl': 0}, 'sell': {'count': 0, 'pnl': 0}}

for row in cursor.fetchall():
    data = json.loads(row[0])
    pnl = data.get('pnl', 0) or 0
    side = data.get('direction', '').lower()
    
    if pnl == 0:
        zero_pnl += 1
    else:
        nonzero_pnl += 1
        total_pnl += pnl
        if pnl > 0:
            winners += 1
        else:
            losers += 1
    
    if side in by_side:
        by_side[side]['count'] += 1
        by_side[side]['pnl'] += pnl

print(f"Closed trades with $0 PnL: {zero_pnl:,} ({zero_pnl/closed_trades*100:.1f}%)")
print(f"Closed trades with real PnL: {nonzero_pnl:,} ({nonzero_pnl/closed_trades*100:.1f}%)")
print()
print(f"Total PnL (from non-zero trades): ${total_pnl:,.2f}")
print(f"Winners: {winners} | Losers: {losers}")
if nonzero_pnl > 0:
    print(f"Win Rate (excluding $0): {winners/nonzero_pnl*100:.1f}%")
print()

print("BY SIDE (all closed trades):")
for side, data in by_side.items():
    emoji = '🟢' if data['pnl'] >= 0 else '🔴'
    print(f"  {side.upper():4s}: {data['count']:,} trades | PnL: ${data['pnl']:,.2f} {emoji}")
print()

# The Problem
print("🐛 THE PROBLEM IDENTIFIED")
print("-" * 40)
print("""
Most trades (91.5%) are being closed with $0 PnL because:

1. Entry price = Exit price in the database
2. This happens when trades are closed via stop_loss/take_profit
   but the exit price recorded equals the entry price

Example from data:
  Symbol: NVDA
  Direction: sell  
  Entry: 900
  Exit: 900
  PnL: $0.00
  Exit reason: stop_loss

This suggests either:
- Prices aren't moving enough to trigger real stop losses
- The auto-trader's simulated prices differ from price_feed's real prices
- There's a bug where exit_price is being set incorrectly
""")

# Portfolio Analysis
print()
print("📈 PORTFOLIO ANALYSIS")
print("-" * 40)

cursor.execute('SELECT COUNT(*) FROM paper_portfolios')
portfolio_count = cursor.fetchone()[0]
print(f"Total portfolios: {portfolio_count:,}")

cursor.execute('SELECT data FROM paper_portfolios')
total_cash = 0
total_portfolio_pnl = 0
total_completed_trades = 0

for row in cursor.fetchall():
    try:
        data = json.loads(row[0])
        total_cash += data.get('cash', 0)
        total_portfolio_pnl += data.get('total_pnl', 0)
        total_completed_trades += data.get('total_trades', 0)
    except:
        pass

print(f"Total cash held: ${total_cash:,.2f}")
print(f"Total PnL (from portfolio records): ${total_portfolio_pnl:,.2f}")
print(f"Total completed trades (from portfolios): {total_completed_trades:,}")
print()

# Check date ranges
cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM paper_trades')
min_date, max_date = cursor.fetchone()
print("📅 DATE RANGE")
print("-" * 40)
print(f"First trade: {min_date}")
print(f"Last trade: {max_date}")
print()

# Active processes
print("⚙️  ACTIVE PROCESSES")
print("-" * 40)
import subprocess
try:
    result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
    if 'auto_trader.py' in result.stdout:
        print("✅ auto_trader.py: RUNNING")
    else:
        print("❌ auto_trader.py: NOT RUNNING")
    
    if 'price_feed.py' in result.stdout:
        print("✅ price_feed.py: RUNNING")
    else:
        print("❌ price_feed.py: NOT RUNNING")
except:
    print("Could not check processes")

print()
print("=" * 60)
print("CONCLUSION")
print("=" * 60)
print(f"""
The PnL data shows:
- Realized PnL: ${total_pnl:,.2f} (from {nonzero_pnl} properly closed trades)
- Most trades ({zero_pnl:,}) show $0 PnL due to exit_price = entry_price
- This is likely a bug in the auto-trader's price simulation vs reality

The previous report showing +$10,695 shorts vs -$110,118 longs
was likely from a different time period or before a database reset.

RECOMMENDATION:
1. Fix the auto_trader to properly calculate PnL on close
2. Ensure price_feed and auto_trader use consistent price sources
3. Consider backfilling PnL for the $0 trades if entry/exit data is correct
""")

conn.close()
