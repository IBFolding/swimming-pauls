#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect('data/paper_trading.db', timeout=10)
cursor = conn.cursor()

# Get ALL trades and analyze
cursor.execute('SELECT data FROM paper_trades')
all_rows = cursor.fetchall()
print(f'Total records in DB: {len(all_rows)}')

# Parse and analyze
open_trades = []
closed_trades = []
errors = 0

for row in all_rows:
    try:
        data = json.loads(row[0])
        if data.get('exit_price') is not None or data.get('status') == 'closed':
            closed_trades.append(data)
        else:
            open_trades.append(data)
    except Exception as e:
        errors += 1

print(f'Open trades: {len(open_trades)}')
print(f'Closed trades: {len(closed_trades)}')
print(f'Parse errors: {errors}')

# Analyze closed trades
total_pnl = 0
winners = 0
losers = 0
by_side = {'buy': {'count': 0, 'pnl': 0}, 'sell': {'count': 0, 'pnl': 0}}
by_asset = {}

for trade in closed_trades:
    pnl = trade.get('pnl', 0) or 0
    side = trade.get('direction', '').lower()
    asset = trade.get('symbol', 'UNKNOWN')
    
    total_pnl += pnl
    
    if pnl > 0:
        winners += 1
    elif pnl < 0:
        losers += 1
    
    if side in by_side:
        by_side[side]['count'] += 1
        by_side[side]['pnl'] += pnl
    
    if asset not in by_asset:
        by_asset[asset] = {'pnl': 0, 'count': 0, 'buy_pnl': 0, 'sell_pnl': 0, 'buy_count': 0, 'sell_count': 0}
    by_asset[asset]['pnl'] += pnl
    by_asset[asset]['count'] += 1
    if side == 'buy':
        by_asset[asset]['buy_pnl'] += pnl
        by_asset[asset]['buy_count'] += 1
    else:
        by_asset[asset]['sell_pnl'] += pnl
        by_asset[asset]['sell_count'] += 1

print('\n=== CLOSED TRADE ANALYSIS ===')
print(f'Total closed with valid PnL: {len(closed_trades)}')
print(f'Total PnL: ${total_pnl:,.2f}')
print(f'Winners: {winners} | Losers: {losers}')
if winners + losers > 0:
    print(f'Win Rate: {winners/(winners+losers)*100:.1f}%')

print('\nBY SIDE:')
for side, data in by_side.items():
    if data['count'] > 0:
        emoji = '🟢' if data['pnl'] >= 0 else '🔴'
        print(f"  {side.upper()}: {data['count']} trades | PnL: ${data['pnl']:,.2f} {emoji}")

print('\nTOP ASSETS:')
sorted_assets = sorted(by_asset.items(), key=lambda x: x[1]['pnl'], reverse=True)
for asset, data in sorted_assets[:10]:
    emoji = '🟢' if data['pnl'] >= 0 else '🔴'
    print(f"  {asset:10s} {data['count']:3d} trades | PnL: ${data['pnl']:12,.2f} {emoji}")

# Check open positions unrealized PnL
print('\n=== OPEN POSITIONS (Unrealized) ===')
total_unrealized = 0
for trade in open_trades[:100]:  # Sample
    unrealized = trade.get('unrealized_pnl', 0) or 0
    total_unrealized += unrealized

print(f'Sample of 100 open positions unrealized PnL: ${total_unrealized:,.2f}')

# Check date ranges
print('\n=== DATE RANGE ===')
cursor.execute('SELECT MIN(created_at), MAX(created_at) FROM paper_trades')
min_date, max_date = cursor.fetchone()
print(f'First trade: {min_date}')
print(f'Last trade: {max_date}')

# Check if there's a pattern by date
print('\n=== TRADES BY DATE (Closed) ===')
cursor.execute("SELECT data FROM paper_trades WHERE closed_at IS NOT NULL")
from datetime import datetime
dates = {}
for row in cursor.fetchall():
    data = json.loads(row[0])
    created = data.get('created_at', '')
    if created:
        day = created[:10]  # YYYY-MM-DD
        if day not in dates:
            dates[day] = {'count': 0, 'pnl': 0}
        dates[day]['count'] += 1
        dates[day]['pnl'] += data.get('pnl', 0) or 0

for day in sorted(dates.keys())[-7:]:  # Last 7 days
    d = dates[day]
    emoji = '🟢' if d['pnl'] >= 0 else '🔴'
    print(f"  {day}: {d['count']:4d} trades | PnL: ${d['pnl']:10,.2f} {emoji}")

# Check portfolio totals
print('\n=== PORTFOLIO TOTALS ===')
cursor.execute('SELECT data FROM paper_portfolios LIMIT 10')
portfolios = []
for row in cursor.fetchall():
    try:
        data = json.loads(row[0])
        portfolios.append(data)
    except:
        pass

total_portfolio_value = sum(p.get('cash', 0) for p in portfolios)
total_pnl_from_portfolios = sum(p.get('total_pnl', 0) for p in portfolios)
total_trades_from_portfolios = sum(p.get('total_trades', 0) for p in portfolios)

print(f"Total portfolios sampled: {len(portfolios)}")
print(f"Total cash: ${total_portfolio_value:,.2f}")
print(f"Total PnL (from portfolios): ${total_pnl_from_portfolios:,.2f}")
print(f"Total trades (from portfolios): {total_trades_from_portfolios}")

# Check for duplicate Pauls (same Paul, multiple trades)
print('\n=== TRADE CLOSURE ANALYSIS ===')
cursor.execute('SELECT paul_name, COUNT(*) as cnt FROM paper_trades GROUP BY paul_name ORDER BY cnt DESC LIMIT 10')
print('Top 10 most active Pauls:')
for paul, cnt in cursor.fetchall():
    print(f"  {paul[:25]:25s}: {cnt:4d} trades")

# Check what's happening with closed trades with $0 PnL
print('\n=== INVESTIGATING $0 PnL CLOSED TRADES ===')
cursor.execute("SELECT data FROM paper_trades WHERE closed_at IS NOT NULL")
zero_pnl_count = 0
nonzero_pnl_count = 0
for row in cursor.fetchall():
    data = json.loads(row[0])
    pnl = data.get('pnl', 0)
    if pnl == 0:
        zero_pnl_count += 1
    else:
        nonzero_pnl_count += 1

print(f"Closed trades with $0 PnL: {zero_pnl_count}")
print(f"Closed trades with non-$0 PnL: {nonzero_pnl_count}")

# Sample some non-zero PnL trades
if nonzero_pnl_count > 0:
    print("\n=== NON-ZERO PnL TRADES ===")
    cursor.execute("SELECT data FROM paper_trades WHERE closed_at IS NOT NULL")
    count = 0
    total_nonzero_pnl = 0
    for row in cursor.fetchall():
        data = json.loads(row[0])
        pnl = data.get('pnl', 0)
        if pnl != 0:
            total_nonzero_pnl += pnl
            count += 1
            if count <= 5:
                print(f"  {data.get('symbol')} {data.get('direction')}: ${pnl:,.2f} (Entry: {data.get('entry_price')} -> Exit: {data.get('exit_price')})")
    print(f"\nTotal non-zero PnL: ${total_nonzero_pnl:,.2f} across {count} trades")

# Compare entry vs exit prices for $0 PnL trades
print("\n=== SAMPLE $0 PnL TRADE ===")
cursor.execute("SELECT data FROM paper_trades WHERE closed_at IS NOT NULL LIMIT 1")
sample = cursor.fetchone()
if sample:
    data = json.loads(sample[0])
    print(f"  Symbol: {data.get('symbol')}")
    print(f"  Direction: {data.get('direction')}")
    print(f"  Entry: {data.get('entry_price')}")
    print(f"  Exit: {data.get('exit_price')}")
    print(f"  Quantity: {data.get('quantity')}")
    print(f"  PnL: {data.get('pnl')}")
    print(f"  Status: {data.get('status')}")
    print(f"  Exit reason: {data.get('exit_reason')}")

# Check ALL portfolios
print("\n=== ALL PORTFOLIOS ANALYSIS ===")
cursor.execute('SELECT data FROM paper_portfolios')
portfolios = []
for row in cursor.fetchall():
    try:
        portfolios.append(json.loads(row[0]))
    except:
        pass

total_cash = sum(p.get('cash', 0) for p in portfolios)
total_pnl = sum(p.get('total_pnl', 0) for p in portfolios)
total_trades = sum(p.get('total_trades', 0) for p in portfolios)
total_wins = sum(p.get('winning_trades', 0) for p in portfolios)
total_losses = sum(p.get('losing_trades', 0) for p in portfolios)

print(f"Total portfolios: {len(portfolios)}")
print(f"Total cash held: ${total_cash:,.2f}")
print(f"Total PnL (from portfolio tracking): ${total_pnl:,.2f}")
print(f"Total trades completed: {total_trades}")
print(f"Winners: {total_wins} | Losers: {total_losses}")
if total_trades > 0:
    print(f"Win rate: {total_wins/total_trades*100:.1f}%")

conn.close()
