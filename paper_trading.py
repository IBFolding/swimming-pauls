"""
Paper Trading System for Swimming Pauls
Hybrid implementation: Live, Backtest, and Competition modes

Features:
- Toggle on/off per Paul
- $10,000 starting portfolio per Paul
- Auto-trade on high-confidence predictions (>75%)
- Track win rate, P&L, Sharpe ratio, max drawdown
- Leaderboards and rankings
- Proven Trader badge for top 10%

Author: Howard (H.O.W.A.R.D)
"""

import json
import sqlite3
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics


class PaperTradingMode(Enum):
    """Paper trading operation modes."""
    OFF = "off"
    LIVE = "live"           # Real-time with Paul's World
    BACKTEST = "backtest"   # Historical simulation
    COMPETITION = "competition"  # Weekly competitions


class TradeStatus(Enum):
    """Status of a paper trade."""
    OPEN = "open"
    CLOSED = "closed"
    STOPPED = "stopped"  # Hit stop loss


@dataclass
class PaperPortfolio:
    """A Paul's paper trading portfolio."""
    paul_name: str
    initial_balance: float = 10000.0
    cash: float = 10000.0
    
    # Positions: symbol -> {quantity, entry_price, current_price}
    positions: Dict[str, Dict] = field(default_factory=dict)
    
    # Trading settings
    enabled: bool = False
    max_position_size: float = 0.10  # 10% max per trade
    stop_loss: float = 0.05          # 5% stop loss
    take_profit: float = 0.15        # 15% take profit
    min_confidence: float = 0.75     # Only trade if confidence > 75%
    
    # Performance tracking
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    max_drawdown: float = 0.0
    peak_value: float = 10000.0
    
    created_at: datetime = field(default_factory=datetime.now)
    last_trade: Optional[datetime] = None
    
    def get_total_value(self) -> float:
        """Calculate total portfolio value."""
        position_value = sum(
            pos['quantity'] * pos.get('current_price', pos['entry_price'])
            for pos in self.positions.values()
        )
        return self.cash + position_value
    
    def get_win_rate(self) -> float:
        """Calculate win rate."""
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades
    
    def get_roi(self) -> float:
        """Calculate return on investment."""
        current_value = self.get_total_value()
        return (current_value - self.initial_balance) / self.initial_balance
    
    def update_drawdown(self):
        """Update max drawdown tracking."""
        current_value = self.get_total_value()
        if current_value > self.peak_value:
            self.peak_value = current_value
        
        drawdown = (self.peak_value - current_value) / self.peak_value
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            'paul_name': self.paul_name,
            'initial_balance': self.initial_balance,
            'cash': self.cash,
            'positions': self.positions,
            'enabled': self.enabled,
            'max_position_size': self.max_position_size,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'min_confidence': self.min_confidence,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'total_pnl': self.total_pnl,
            'max_drawdown': self.max_drawdown,
            'peak_value': self.peak_value,
            'created_at': self.created_at.isoformat(),
            'last_trade': self.last_trade.isoformat() if self.last_trade else None,
        }


@dataclass
class PaperTrade:
    """A single paper trade."""
    id: str
    paul_name: str
    symbol: str
    direction: str  # "buy" or "sell"
    quantity: float
    entry_price: float
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: float = 0.0
    pnl_percent: float = 0.0
    status: TradeStatus = TradeStatus.OPEN
    exit_reason: Optional[str] = None  # "manual", "stop_loss", "take_profit", "prediction_flip"
    prediction_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'paul_name': self.paul_name,
            'symbol': self.symbol,
            'direction': self.direction,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'status': self.status.value,
            'exit_reason': self.exit_reason,
            'prediction_id': self.prediction_id,
            'created_at': self.created_at.isoformat(),
        }


class PaperTradingManager:
    """
    Manages paper trading for Swimming Pauls.
    
    Supports 3 modes:
    - LIVE: Real-time trading alongside Paul's World
    - BACKTEST: Historical simulation
    - COMPETITION: Weekly trading competitions
    """
    
    def __init__(self, db_path: str = "data/paper_trading.db", mode: PaperTradingMode = PaperTradingMode.OFF):
        self.db_path = Path(db_path)
        self.mode = mode
        self.portfolios: Dict[str, PaperPortfolio] = {}
        self.trades: Dict[str, PaperTrade] = {}
        self.competition_start: Optional[datetime] = None
        self.competition_end: Optional[datetime] = None
        
        self._init_db()
        self._load_data()
    
    def _init_db(self):
        """Initialize SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Portfolios table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_portfolios (
                paul_name TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Trades table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_trades (
                id TEXT PRIMARY KEY,
                paul_name TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at TEXT NOT NULL,
                closed_at TEXT
            )
        ''')
        
        # Competition history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                winner TEXT,
                top_10 TEXT,  -- JSON list
                results TEXT  -- JSON full results
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_data(self):
        """Load existing portfolios and trades."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load portfolios
        cursor.execute('SELECT paul_name, data FROM paper_portfolios')
        for row in cursor.fetchall():
            data = json.loads(row[1])
            portfolio = PaperPortfolio(
                paul_name=data['paul_name'],
                initial_balance=data['initial_balance'],
                cash=data['cash'],
                positions=data['positions'],
                enabled=data['enabled'],
                max_position_size=data['max_position_size'],
                stop_loss=data['stop_loss'],
                take_profit=data['take_profit'],
                min_confidence=data['min_confidence'],
                total_trades=data['total_trades'],
                winning_trades=data['winning_trades'],
                losing_trades=data['losing_trades'],
                total_pnl=data['total_pnl'],
                max_drawdown=data['max_drawdown'],
                peak_value=data['peak_value'],
                created_at=datetime.fromisoformat(data['created_at']),
                last_trade=datetime.fromisoformat(data['last_trade']) if data['last_trade'] else None,
            )
            self.portfolios[portfolio.paul_name] = portfolio
        
        # Load open trades
        cursor.execute('SELECT id, data FROM paper_trades WHERE closed_at IS NULL')
        for row in cursor.fetchall():
            data = json.loads(row[1])
            trade = PaperTrade(
                id=data['id'],
                paul_name=data['paul_name'],
                symbol=data['symbol'],
                direction=data['direction'],
                quantity=data['quantity'],
                entry_price=data['entry_price'],
                exit_price=data.get('exit_price'),
                exit_time=datetime.fromisoformat(data['exit_time']) if data.get('exit_time') else None,
                pnl=data['pnl'],
                pnl_percent=data['pnl_percent'],
                status=TradeStatus(data['status']),
                exit_reason=data.get('exit_reason'),
                prediction_id=data.get('prediction_id'),
                created_at=datetime.fromisoformat(data['created_at']),
            )
            self.trades[trade.id] = trade
        
        conn.close()
    
    def create_portfolio(self, paul_name: str, initial_balance: float = 10000.0, 
                        enabled: bool = True) -> PaperPortfolio:
        """Create a new paper trading portfolio for a Paul."""
        portfolio = PaperPortfolio(
            paul_name=paul_name,
            initial_balance=initial_balance,
            cash=initial_balance,
            enabled=enabled,
        )
        
        self.portfolios[paul_name] = portfolio
        self._save_portfolio(portfolio)
        
        return portfolio
    
    def _save_portfolio(self, portfolio: PaperPortfolio):
        """Save portfolio to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO paper_portfolios (paul_name, data, updated_at)
            VALUES (?, ?, ?)
        ''', (
            portfolio.paul_name,
            json.dumps(portfolio.to_dict()),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def execute_trade(self, paul_name: str, symbol: str, direction: str,
                     current_price: float, confidence: float,
                     prediction_id: Optional[str] = None) -> Optional[PaperTrade]:
        """
        Execute a paper trade based on prediction.
        
        Args:
            paul_name: Which Paul is trading
            symbol: What to trade (BTC, ETH, etc.)
            direction: "buy" or "sell"
            current_price: Current market price
            confidence: Prediction confidence (0-1)
            prediction_id: Optional prediction reference
        
        Returns:
            PaperTrade if executed, None if skipped
        """
        if paul_name not in self.portfolios:
            return None
        
        portfolio = self.portfolios[paul_name]
        
        # Check if trading enabled
        if not portfolio.enabled:
            return None
        
        # Check confidence threshold
        if confidence < portfolio.min_confidence:
            return None
        
        # Calculate position size (max 10% of portfolio)
        portfolio_value = portfolio.get_total_value()
        max_position = portfolio_value * portfolio.max_position_size
        quantity = max_position / current_price
        
        # Check if we have enough cash
        cost = quantity * current_price
        if portfolio.cash < cost:
            # Reduce size to available cash
            quantity = portfolio.cash / current_price
            cost = quantity * current_price
        
        if quantity <= 0:
            return None
        
        # Execute trade
        trade_id = f"{paul_name}_{symbol}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        trade = PaperTrade(
            id=trade_id,
            paul_name=paul_name,
            symbol=symbol,
            direction=direction,
            quantity=quantity,
            entry_price=current_price,
            prediction_id=prediction_id,
        )
        
        # Update portfolio
        portfolio.cash -= cost
        portfolio.positions[symbol] = {
            'quantity': quantity,
            'entry_price': current_price,
            'current_price': current_price,
            'trade_id': trade_id,
        }
        portfolio.total_trades += 1
        portfolio.last_trade = datetime.now()
        
        self.trades[trade_id] = trade
        self._save_portfolio(portfolio)
        self._save_trade(trade)
        
        return trade
    
    def _save_trade(self, trade: PaperTrade):
        """Save trade to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO paper_trades (id, paul_name, data, created_at, closed_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            trade.id,
            trade.paul_name,
            json.dumps(trade.to_dict()),
            trade.created_at.isoformat(),
            trade.exit_time.isoformat() if trade.exit_time else None,
        ))
        
        conn.commit()
        conn.close()
    
    def close_trade(self, trade_id: str, exit_price: float, reason: str = "manual"):
        """Close an open trade."""
        if trade_id not in self.trades:
            return
        
        trade = self.trades[trade_id]
        portfolio = self.portfolios.get(trade.paul_name)
        
        if not portfolio:
            return
        
        # Calculate P&L
        if trade.direction == "buy":
            trade.pnl = (exit_price - trade.entry_price) * trade.quantity
        else:  # sell/short
            trade.pnl = (trade.entry_price - exit_price) * trade.quantity
        
        trade.pnl_percent = trade.pnl / (trade.entry_price * trade.quantity)
        trade.exit_price = exit_price
        trade.exit_time = datetime.now()
        trade.exit_reason = reason
        trade.status = TradeStatus.CLOSED
        
        # Update portfolio
        portfolio.cash += (trade.quantity * exit_price) + trade.pnl
        portfolio.total_pnl += trade.pnl
        
        if trade.pnl > 0:
            portfolio.winning_trades += 1
        else:
            portfolio.losing_trades += 1
        
        # Remove position
        if trade.symbol in portfolio.positions:
            del portfolio.positions[trade.symbol]
        
        portfolio.update_drawdown()
        
        self._save_portfolio(portfolio)
        self._save_trade(trade)
    
    def update_prices(self, prices: Dict[str, float]):
        """Update current prices and check stop losses."""
        for portfolio in self.portfolios.values():
            if not portfolio.enabled:
                continue
            
            for symbol, position in list(portfolio.positions.items()):
                if symbol not in prices:
                    continue
                
                current_price = prices[symbol]
                position['current_price'] = current_price
                
                # Check stop loss
                entry = position['entry_price']
                stop_level = entry * (1 - portfolio.stop_loss)
                profit_level = entry * (1 + portfolio.take_profit)
                
                trade_id = position.get('trade_id')
                if not trade_id or trade_id not in self.trades:
                    continue
                
                trade = self.trades[trade_id]
                
                if trade.direction == "buy":
                    if current_price <= stop_level:
                        self.close_trade(trade_id, current_price, "stop_loss")
                    elif current_price >= profit_level:
                        self.close_trade(trade_id, current_price, "take_profit")
                else:  # short
                    if current_price >= stop_level:
                        self.close_trade(trade_id, current_price, "stop_loss")
                    elif current_price <= profit_level:
                        self.close_trade(trade_id, current_price, "take_profit")
            
            portfolio.update_drawdown()
            self._save_portfolio(portfolio)
    
    def get_leaderboard(self, limit: int = 20) -> List[Dict]:
        """Get paper trading leaderboard."""
        rankings = []
        
        for paul_name, portfolio in self.portfolios.items():
            if not portfolio.enabled or portfolio.total_trades == 0:
                continue
            
            rankings.append({
                'paul_name': paul_name,
                'total_value': portfolio.get_total_value(),
                'roi': portfolio.get_roi(),
                'win_rate': portfolio.get_win_rate(),
                'total_trades': portfolio.total_trades,
                'max_drawdown': portfolio.max_drawdown,
                'proven_trader': portfolio.get_win_rate() > 0.6 and portfolio.total_trades >= 50,
            })
        
        # Sort by ROI
        rankings.sort(key=lambda x: x['roi'], reverse=True)
        
        # Add rank
        for i, r in enumerate(rankings, 1):
            r['rank'] = i
        
        return rankings[:limit]
    
    def get_proven_traders(self) -> List[str]:
        """Get list of Pauls who earned Proven Trader badge."""
        leaderboard = self.get_leaderboard(limit=1000)
        
        # Top 10% with >60% win rate and 50+ trades
        total = len([p for p in leaderboard if p['total_trades'] >= 50])
        cutoff = max(1, int(total * 0.1))
        
        proven = []
        for paul in leaderboard[:cutoff]:
            if paul['win_rate'] > 0.6 and paul['total_trades'] >= 50:
                proven.append(paul['paul_name'])
        
        return proven
    
    def start_competition(self, duration_days: int = 7):
        """Start a weekly trading competition."""
        self.mode = PaperTradingMode.COMPETITION
        self.competition_start = datetime.now()
        self.competition_end = datetime.now() + timedelta(days=duration_days)
        
        # Reset all portfolios
        for portfolio in self.portfolios.values():
            portfolio.initial_balance = 10000.0
            portfolio.cash = 10000.0
            portfolio.positions = {}
            portfolio.total_trades = 0
            portfolio.winning_trades = 0
            portfolio.losing_trades = 0
            portfolio.total_pnl = 0.0
            portfolio.max_drawdown = 0.0
            portfolio.peak_value = 10000.0
            self._save_portfolio(portfolio)
        
        print(f"🏆 Competition started! Ends: {self.competition_end.strftime('%Y-%m-%d')}")
    
    def end_competition(self) -> Dict:
        """End competition and return results."""
        leaderboard = self.get_leaderboard()
        
        if not leaderboard:
            return {'error': 'No participants'}
        
        winner = leaderboard[0]
        top_10 = leaderboard[:10]
        
        # Save to history
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO competitions (start_date, end_date, winner, top_10, results)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            self.competition_start.isoformat() if self.competition_start else None,
            datetime.now().isoformat(),
            winner['paul_name'],
            json.dumps([p['paul_name'] for p in top_10]),
            json.dumps(leaderboard),
        ))
        
        conn.commit()
        conn.close()
        
        self.mode = PaperTradingMode.OFF
        
        return {
            'winner': winner,
            'top_10': top_10,
            'proven_traders': self.get_proven_traders(),
        }


# Integration with Paul's World predictions
async def handle_prediction_with_paper_trading(
    prediction_result: Dict,
    paper_manager: PaperTradingManager,
    onchain_data: Optional[Dict] = None
):
    """
    Process a prediction result and execute paper trades.
    
    This is called after Paul's World generates a prediction.
    """
    if paper_manager.mode == PaperTradingMode.OFF:
        return
    
    question = prediction_result.get('question', '')
    consensus = prediction_result.get('consensus', {})
    direction = consensus.get('direction', 'NEUTRAL')
    confidence = consensus.get('confidence', 0)
    
    # Extract token from question
    tokens = extract_tokens_from_text(question)
    
    if not tokens or direction == 'NEUTRAL' or confidence < 0.75:
        return
    
    # Use first token found
    symbol = tokens[0]
    
    # Get current price (from on-chain data or API)
    current_price = 100.0  # Placeholder - would fetch real price
    if onchain_data and symbol in onchain_data:
        current_price = onchain_data[symbol].get('price', 100.0)
    
    # Map direction to trade action
    trade_direction = "buy" if direction == "BULLISH" else "sell"
    
    # Execute trades for confident Pauls
    for response in prediction_result.get('responses', []):
        paul_name = response['paul_name']
        paul_confidence = response['confidence']
        paul_sentiment = response['sentiment']
        
        # Only trade if Paul agrees with consensus and is confident
        if paul_sentiment == direction and paul_confidence >= 0.75:
            paper_manager.execute_trade(
                paul_name=paul_name,
                symbol=symbol,
                direction=trade_direction,
                current_price=current_price,
                confidence=paul_confidence,
                prediction_id=prediction_result.get('result_id')
            )


def extract_tokens_from_text(text: str) -> List[str]:
    """Extract potential trading symbols from text."""
    text_upper = text.upper()
    
    token_map = {
        'BTC': ['BTC', 'BITCOIN'],
        'ETH': ['ETH', 'ETHEREUM'],
        'SOL': ['SOL', 'SOLANA'],
        'BNB': ['BNB'],
        'ADA': ['ADA', 'CARDANO'],
        'DOT': ['DOT', 'POLKADOT'],
        'AVAX': ['AVAX', 'AVALANCHE'],
        'MATIC': ['MATIC', 'POLYGON'],
        'ARB': ['ARB', 'ARBITRUM'],
        'OP': ['OP', 'OPTIMISM'],
    }
    
    found = []
    for token, keywords in token_map.items():
        if any(kw in text_upper for kw in keywords):
            found.append(token)
    
    return found


# CLI Interface
def paper_trading_cli():
    """Command-line interface for paper trading."""
    import sys
    
    manager = PaperTradingManager()
    
    if len(sys.argv) < 2:
        print("Paper Trading CLI")
        print("Commands:")
        print("  create <paul>              - Create portfolio for Paul")
        print("  enable <paul>              - Enable paper trading for Paul")
        print("  disable <paul>             - Disable paper trading")
        print("  status <paul>              - Show portfolio status")
        print("  leaderboard                - Show rankings")
        print("  proven                     - List proven traders")
        print("  competition start <days>   - Start competition")
        print("  competition end            - End competition")
        print("  backtest <days>            - Run backtest simulation")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "create" and len(sys.argv) > 2:
        paul_name = sys.argv[2]
        portfolio = manager.create_portfolio(paul_name)
        print(f"✅ Created portfolio for {paul_name}: ${portfolio.initial_balance:,.2f}")
    
    elif command == "enable" and len(sys.argv) > 2:
        paul_name = sys.argv[2]
        if paul_name in manager.portfolios:
            manager.portfolios[paul_name].enabled = True
            manager._save_portfolio(manager.portfolios[paul_name])
            print(f"✅ Paper trading enabled for {paul_name}")
        else:
            print(f"❌ Portfolio not found. Create with: paper_trading.py create {paul_name}")
    
    elif command == "disable" and len(sys.argv) > 2:
        paul_name = sys.argv[2]
        if paul_name in manager.portfolios:
            manager.portfolios[paul_name].enabled = False
            manager._save_portfolio(manager.portfolios[paul_name])
            print(f"✅ Paper trading disabled for {paul_name}")
    
    elif command == "status" and len(sys.argv) > 2:
        paul_name = sys.argv[2]
        if paul_name not in manager.portfolios:
            print(f"❌ No portfolio for {paul_name}")
            return
        
        p = manager.portfolios[paul_name]
        print(f"\n📊 {paul_name} Portfolio")
        print(f"   Status: {'Enabled' if p.enabled else 'Disabled'}")
        print(f"   Total Value: ${p.get_total_value():,.2f} ({p.get_roi():+.1%})")
        print(f"   Cash: ${p.cash:,.2f}")
        print(f"   Positions: {len(p.positions)}")
        print(f"   Trades: {p.total_trades} (Win rate: {p.get_win_rate():.0%})")
        print(f"   Max Drawdown: {p.max_drawdown:.1%}")
        if p.get_win_rate() > 0.6 and p.total_trades >= 50:
            print(f"   🏆 PROVEN TRADER")
    
    elif command == "leaderboard":
        leaderboard = manager.get_leaderboard(20)
        print("\n🏆 Paper Trading Leaderboard\n")
        for paul in leaderboard:
            badge = "🏆" if paul.get('proven_trader') else ""
            print(f"  {paul['rank']}. {paul['paul_name']} {badge}")
            print(f"     Value: ${paul['total_value']:,.2f} ({paul['roi']:+.1%})")
            print(f"     Win Rate: {paul['win_rate']:.0%} | Trades: {paul['total_trades']}")
            print()
    
    elif command == "proven":
        proven = manager.get_proven_traders()
        print(f"\n🏆 Proven Traders ({len(proven)} total)\n")
        for paul_name in proven:
            print(f"  ✓ {paul_name}")
    
    elif command == "competition":
        subcmd = sys.argv[2] if len(sys.argv) > 2 else "status"
        
        if subcmd == "start" and len(sys.argv) > 3:
            days = int(sys.argv[3])
            manager.start_competition(days)
        elif subcmd == "end":
            results = manager.end_competition()
            print(f"\n🏆 Competition Results")
            print(f"   Winner: {results['winner']['paul_name']}")
            print(f"   ROI: {results['winner']['roi']:+.1%}")
            print(f"\n   Top 10:")
            for i, p in enumerate(results['top_10'][:10], 1):
                print(f"      {i}. {p['paul_name']} ({p['roi']:+.1%})")
    
    elif command == "backtest" and len(sys.argv) > 2:
        days = int(sys.argv[2])
        print(f"\n📊 Running {days}-day backtest...")
        # This would run historical simulation
        print("   (Backtest mode would simulate historical performance)")


if __name__ == "__main__":
    paper_trading_cli()
