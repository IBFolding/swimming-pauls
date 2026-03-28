#!/usr/bin/env python3
"""Trading API Server - Exposes paper trading data for web dashboard."""
import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from paul_world import PaulWorld

# Global state
world = None
pt = None

def get_trading_data():
    """Get current trading data."""
    if not pt:
        return {"error": "Not initialized"}
    
    # Get leaderboard
    leaderboard = pt.get_leaderboard(20)
    
    # Get recent trades
    recent_trades = []
    for trade in list(pt.trades.values())[-20:]:
        recent_trades.append({
            'id': trade.id,
            'paul_name': trade.paul_name,
            'symbol': trade.symbol,
            'direction': trade.direction,
            'entry_price': trade.entry_price,
            'exit_price': trade.exit_price,
            'pnl': trade.pnl,
            'pnl_percent': trade.pnl_percent,
            'status': trade.status.value,
            'created_at': trade.created_at.isoformat(),
        })
    
    # Calculate stats
    total_trades = len(pt.trades)
    total_pauls = len(pt.portfolios)
    active_pauls = sum(1 for p in pt.portfolios.values() if p.enabled)
    open_positions = sum(len(p.positions) for p in pt.portfolios.values())
    
    # Get top performer
    top_performer = leaderboard[0] if leaderboard else None
    
    return {
        'timestamp': datetime.now().isoformat(),
        'competition': {
            'mode': pt.mode.value,
            'end_date': pt.competition_end.isoformat() if pt.competition_end else None,
        },
        'stats': {
            'total_trades': total_trades,
            'total_pauls': total_pauls,
            'active_pauls': active_pauls,
            'open_positions': open_positions,
        },
        'leaderboard': leaderboard,
        'recent_trades': recent_trades,
        'top_performer': top_performer,
    }

def get_positions_data():
    """Get open positions data."""
    if not pt:
        return {'positions': []}
    
    positions = []
    for paul_name, portfolio in pt.portfolios.items():
        if not portfolio.enabled:
            continue
        for symbol, pos in portfolio.positions.items():
            positions.append({
                'paul_name': paul_name,
                'symbol': symbol,
                'quantity': pos.get('quantity', 0),
                'entry_price': pos.get('entry_price', 0),
                'current_price': pos.get('current_price', pos.get('entry_price', 0)),
                'value': pos.get('quantity', 0) * pos.get('current_price', pos.get('entry_price', 0)),
                'pnl': (pos.get('current_price', pos.get('entry_price', 0)) - pos.get('entry_price', 0)) * pos.get('quantity', 0),
                'pnl_percent': ((pos.get('current_price', pos.get('entry_price', 0)) - pos.get('entry_price', 0)) / pos.get('entry_price', 0) * 100) if pos.get('entry_price', 0) > 0 else 0,
            })
    
    # Sort by value
    positions.sort(key=lambda x: x['value'], reverse=True)
    return {'positions': positions, 'count': len(positions)}


class TradingHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logs
    
    def do_GET(self):
        if self.path == '/api/trading':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = get_trading_data()
            self.wfile.write(json.dumps(data, default=str).encode())
        
        elif self.path == '/api/leaderboard':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = {'leaderboard': pt.get_leaderboard(50) if pt else []}
            self.wfile.write(json.dumps(data, default=str).encode())
        
        elif self.path == '/api/positions':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            data = get_positions_data()
            self.wfile.write(json.dumps(data, default=str).encode())
        
        elif self.path == '/' or self.path == '/demo':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            # Serve the demo page with live data
            try:
                with open('/Users/brain/.openclaw/workspace/swimming_pauls/demo_trading_live.html', 'r') as f:
                    self.wfile.write(f.read().encode())
            except Exception as e:
                self.send_error(500, str(e))
        
        else:
            self.send_response(404)
            self.end_headers()

DASHBOARD_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Swimming Pauls - Live Trading</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #fff;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 2rem;
            text-align: center;
            border-bottom: 2px solid #00d4aa;
        }
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #00d4aa, #00a8e8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .header p { color: #888; }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        .stat-card {
            background: #151520;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #252535;
            text-align: center;
        }
        .stat-card h3 {
            color: #888;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 0.5rem;
        }
        .stat-card .value {
            font-size: 2rem;
            font-weight: bold;
            color: #00d4aa;
        }
        .content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            padding: 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }
        @media (max-width: 900px) {
            .content { grid-template-columns: 1fr; }
        }
        .panel {
            background: #151520;
            border-radius: 12px;
            border: 1px solid #252535;
            overflow: hidden;
        }
        .panel-header {
            background: #1a1a2e;
            padding: 1rem 1.5rem;
            border-bottom: 1px solid #252535;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .panel-header span {
            color: #00d4aa;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        .panel-content {
            padding: 1rem;
            max-height: 500px;
            overflow-y: auto;
        }
        .leaderboard-item {
            display: flex;
            align-items: center;
            padding: 0.75rem;
            border-bottom: 1px solid #252535;
            transition: background 0.2s;
        }
        .leaderboard-item:hover { background: #1a1a2e; }
        .rank {
            width: 30px;
            font-weight: bold;
            color: #888;
        }
        .rank.top3 { color: #ffd700; }
        .paul-info { flex: 1; }
        .paul-name {
            font-weight: 600;
            color: #fff;
        }
        .paul-stats {
            font-size: 0.75rem;
            color: #666;
        }
        .pnl {
            text-align: right;
            font-weight: bold;
        }
        .pnl.positive { color: #00d4aa; }
        .pnl.negative { color: #ff4757; }
        .pnl.neutral { color: #888; }
        .trade-item {
            display: flex;
            align-items: center;
            padding: 0.75rem;
            border-bottom: 1px solid #252535;
            font-size: 0.875rem;
        }
        .trade-direction {
            width: 50px;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            text-align: center;
            font-weight: bold;
            font-size: 0.75rem;
        }
        .trade-direction.buy {
            background: rgba(0, 212, 170, 0.2);
            color: #00d4aa;
        }
        .trade-direction.sell {
            background: rgba(255, 71, 87, 0.2);
            color: #ff4757;
        }
        .trade-symbol {
            width: 80px;
            text-align: center;
            font-weight: bold;
        }
        .trade-paul {
            flex: 1;
            color: #aaa;
        }
        .trade-price {
            color: #888;
            font-family: monospace;
        }
        .live-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.75rem;
            color: #00d4aa;
        }
        .live-dot {
            width: 8px;
            height: 8px;
            background: #00d4aa;
            border-radius: 50%;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.3; }
        }
        .loading {
            text-align: center;
            padding: 2rem;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🦷 Swimming Pauls</h1>
        <p>Live Paper Trading Competition • 10,000 Pauls • Real Market Data</p>
    </div>
    
    <div class="stats-grid">
        <div class="stat-card">
            <h3>Total Trades</h3>
            <div class="value" id="total-trades">-</div>
        </div>
        <div class="stat-card">
            <h3>Active Traders</h3>
            <div class="value" id="active-pauls">-</div>
        </div>
        <div class="stat-card">
            <h3>Open Positions</h3>
            <div class="value" id="open-positions">-</div>
        </div>
        <div class="stat-card">
            <h3>Top ROI</h3>
            <div class="value" id="top-roi">-</div>
        </div>
    </div>
    
    <div class="content">
        <div class="panel">
            <div class="panel-header">
                🏆 Leaderboard
                <div class="live-indicator">
                    <span class="live-dot"></span>
                    LIVE
                </div>
            </div>
            <div class="panel-content" id="leaderboard">
                <div class="loading">Loading...</div>
            </div>
        </div>
        
        <div class="panel">
            <div class="panel-header">
                📈 Recent Trades
                <span>Last 20</span>
            </div>
            <div class="panel-content" id="recent-trades">
                <div class="loading">Loading...</div>
            </div>
        </div>
    </div>
    
    <script>
        let lastData = null;
        
        async function fetchData() {
            try {
                const response = await fetch('/api/trading');
                const data = await response.json();
                updateDashboard(data);
                lastData = data;
            } catch (err) {
                console.error('Failed to fetch:', err);
            }
        }
        
        function updateDashboard(data) {
            // Update stats
            document.getElementById('total-trades').textContent = data.stats.total_trades.toLocaleString();
            document.getElementById('active-pauls').textContent = data.stats.active_pauls.toLocaleString();
            document.getElementById('open-positions').textContent = data.stats.open_positions;
            
            const topRoi = data.top_performer ? (data.top_performer.roi * 100).toFixed(2) + '%' : '-';
            document.getElementById('top-roi').textContent = topRoi;
            
            // Update leaderboard
            const lbHtml = data.leaderboard.slice(0, 20).map((p, i) => {
                const rankClass = i < 3 ? 'top3' : '';
                const pnlClass = p.roi > 0 ? 'positive' : p.roi < 0 ? 'negative' : 'neutral';
                const roi = (p.roi * 100).toFixed(2) + '%';
                return `
                    <div class="leaderboard-item">
                        <div class="rank ${rankClass}">${i + 1}</div>
                        <div class="paul-info">
                            <div class="paul-name">${p.paul_name}</div>
                            <div class="paul-stats">${p.total_trades} trades • $${p.total_value.toLocaleString()}</div>
                        </div>
                        <div class="pnl ${pnlClass}">${roi}</div>
                    </div>
                `;
            }).join('');
            document.getElementById('leaderboard').innerHTML = lbHtml || '<div class="loading">No data</div>';
            
            // Update recent trades
            const tradesHtml = data.recent_trades.slice().reverse().map(t => {
                const dirClass = t.direction === 'buy' ? 'buy' : 'sell';
                return `
                    <div class="trade-item">
                        <div class="trade-direction ${dirClass}">${t.direction.toUpperCase()}</div>
                        <div class="trade-symbol">${t.symbol}</div>
                        <div class="trade-paul">${t.paul_name}</div>
                        <div class="trade-price">$${t.entry_price.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    </div>
                `;
            }).join('');
            document.getElementById('recent-trades').innerHTML = tradesHtml || '<div class="loading">No trades</div>';
        }
        
        // Initial load and refresh
        fetchData();
        setInterval(fetchData, 5000); // Refresh every 5 seconds
    </script>
</body>
</html>
'''

async def main():
    global world, pt
    
    print("🦷 Starting Trading API Server...")
    
    # Initialize world
    world = PaulWorld()
    await world.initialize()
    pt = world.paper_trading
    
    # Ensure competition mode
    if pt.mode.value != 'competition':
        pt.start_competition(7)
    for p in pt.portfolios.values():
        p.enabled = True
    
    # Start HTTP server
    server = HTTPServer(('localhost', 8080), TradingHandler)
    print(f"✅ Trading API running at http://localhost:8080")
    print(f"📊 API endpoint: http://localhost:8080/api/trading")
    print(f"🏆 {len(pt.portfolios):,} Pauls ready")
    
    # Run server in thread
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Keep alive
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        server.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
