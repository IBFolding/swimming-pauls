#!/usr/bin/env python3
"""
Pauls Trading Progression System
Manages the path from Paper Trading → Proven Trader → Bankr Live Trading

Progression Stages:
1. TRAINING: Paper trading, learning, building track record
2. PROVEN: >60% win rate + 50+ trades + positive ROI
3. BANKR_READY: Graduated to real trading with API keys
4. LIVE: Actively trading real money via Bankr
"""
import asyncio
import json
import sqlite3
import sys
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')
from paul_world import PaulWorld


class TraderStage(Enum):
    TRAINING = "training"
    PROVEN = "proven"
    BANKR_READY = "bankr_ready"
    LIVE = "live"
    SUSPENDED = "suspended"


@dataclass
class PaulProgression:
    """Tracks a Paul's trading career progression."""
    paul_name: str
    stage: TraderStage = TraderStage.TRAINING
    
    # Paper trading stats (training)
    paper_trades: int = 0
    paper_wins: int = 0
    paper_win_rate: float = 0.0
    paper_roi: float = 0.0
    paper_proven_date: Optional[datetime] = None
    
    # Bankr graduation
    bankr_api_key: Optional[str] = None
    bankr_wallet: Optional[str] = None
    bankr_graduated_date: Optional[datetime] = None
    
    # Live trading stats
    live_trades: int = 0
    live_pnl: float = 0.0
    live_roi: float = 0.0
    
    # Risk management
    max_position_size: float = 100.0  # USD per trade
    daily_loss_limit: float = 50.0    # Stop trading if down $50/day
    current_daily_loss: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'paul_name': self.paul_name,
            'stage': self.stage.value,
            'paper_trades': self.paper_trades,
            'paper_wins': self.paper_wins,
            'paper_win_rate': self.paper_win_rate,
            'paper_roi': self.paper_roi,
            'paper_proven_date': self.paper_proven_date.isoformat() if self.paper_proven_date else None,
            'bankr_wallet': self.bankr_wallet,
            'bankr_graduated_date': self.bankr_graduated_date.isoformat() if self.bankr_graduated_date else None,
            'live_trades': self.live_trades,
            'live_pnl': self.live_pnl,
            'live_roi': self.live_roi,
            'max_position_size': self.max_position_size,
            'created_at': self.created_at.isoformat(),
        }


class ProgressionManager:
    """Manages Pauls progression from training to live trading."""
    
    # Requirements to graduate stages
    PROVEN_REQUIREMENTS = {
        'min_trades': 50,
        'min_win_rate': 0.60,
        'min_roi': 0.01,  # 1% positive ROI
    }
    
    BANKR_REQUIREMENTS = {
        'proven_duration_days': 7,  # Must be proven for 7 days
        'consistent_performance': True,  # No major drawdowns
    }
    
    def __init__(self, db_path: str = "data/progression.db"):
        self.db_path = db_path
        self.pauls: Dict[str, PaulProgression] = {}
        self._init_db()
        self._load_pauls()
        
    def _init_db(self):
        """Initialize progression database."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_progression (
                paul_name TEXT PRIMARY KEY,
                stage TEXT DEFAULT 'training',
                paper_trades INTEGER DEFAULT 0,
                paper_wins INTEGER DEFAULT 0,
                paper_win_rate REAL DEFAULT 0,
                paper_roi REAL DEFAULT 0,
                paper_proven_date TEXT,
                bankr_wallet TEXT,
                bankr_graduated_date TEXT,
                live_trades INTEGER DEFAULT 0,
                live_pnl REAL DEFAULT 0,
                live_roi REAL DEFAULT 0,
                max_position_size REAL DEFAULT 100,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def _load_pauls(self):
        """Load all Paul progression records."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM paul_progression')
        rows = cursor.fetchall()
        
        for row in rows:
            paul = PaulProgression(
                paul_name=row[0],
                stage=TraderStage(row[1]),
                paper_trades=row[2],
                paper_wins=row[3],
                paper_win_rate=row[4],
                paper_roi=row[5],
                paper_proven_date=datetime.fromisoformat(row[6]) if row[6] else None,
                bankr_wallet=row[7],
                bankr_graduated_date=datetime.fromisoformat(row[8]) if row[8] else None,
                live_trades=row[9],
                live_pnl=row[10],
                live_roi=row[11],
                max_position_size=row[12],
            )
            self.pauls[paul.paul_name] = paul
            
        conn.close()
        
    def _save_paul(self, paul: PaulProgression):
        """Save Paul progression to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO paul_progression 
            (paul_name, stage, paper_trades, paper_wins, paper_win_rate, paper_roi,
             paper_proven_date, bankr_wallet, bankr_graduated_date, live_trades, live_pnl, live_roi,
             max_position_size, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            paul.paul_name, paul.stage.value, paul.paper_trades, paul.paper_wins,
            paul.paper_win_rate, paul.paper_roi,
            paul.paper_proven_date.isoformat() if paul.paper_proven_date else None,
            paul.bankr_wallet, 
            paul.bankr_graduated_date.isoformat() if paul.bankr_graduated_date else None,
            paul.live_trades, paul.live_pnl, paul.live_roi,
            paul.max_position_size, datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
    def check_progression(self, paul_name: str, paper_portfolio) -> Optional[str]:
        """Check if a Paul should progress to next stage."""
        if paul_name not in self.pauls:
            self.pauls[paul_name] = PaulProgression(paul_name=paul_name)
            
        paul = self.pauls[paul_name]
        promotions = []
        
        # Update paper stats
        paul.paper_trades = paper_portfolio.total_trades
        paul.paper_wins = paper_portfolio.winning_trades
        paul.paper_win_rate = paper_portfolio.get_win_rate()
        paul.paper_roi = paper_portfolio.get_roi()
        
        # Check for TRAINING → PROVEN
        if paul.stage == TraderStage.TRAINING:
            if (paul.paper_trades >= self.PROVEN_REQUIREMENTS['min_trades'] and
                paul.paper_win_rate >= self.PROVEN_REQUIREMENTS['min_win_rate'] and
                paul.paper_roi >= self.PROVEN_REQUIREMENTS['min_roi']):
                
                paul.stage = TraderStage.PROVEN
                paul.paper_proven_date = datetime.now()
                promotions.append(f"🎓 {paul_name} graduated to PROVEN! ({paul.paper_roi:+.1%} ROI, {paul.paper_win_rate:.0%} win rate)")
        
        # Check for PROVEN → BANKR_READY
        elif paul.stage == TraderStage.PROVEN:
            if paul.paper_proven_date:
                proven_days = (datetime.now() - paul.paper_proven_date).days
                if proven_days >= self.BANKR_REQUIREMENTS['proven_duration_days']:
                    paul.stage = TraderStage.BANKR_READY
                    promotions.append(f"✅ {paul_name} ready for Bankr! (Proven for {proven_days} days)")
        
        if promotions:
            self._save_paul(paul)
            
        return promotions[0] if promotions else None
        
    def graduate_to_bankr(self, paul_name: str, bankr_wallet: str) -> bool:
        """Graduate a Paul to live Bankr trading."""
        if paul_name not in self.pauls:
            return False
            
        paul = self.pauls[paul_name]
        if paul.stage != TraderStage.BANKR_READY:
            print(f"❌ {paul_name} not ready for Bankr (current stage: {paul.stage.value})")
            return False
            
        paul.stage = TraderStage.LIVE
        paul.bankr_wallet = bankr_wallet
        paul.bankr_graduated_date = datetime.now()
        self._save_paul(paul)
        
        print(f"🚀 {paul_name} is now LIVE trading with Bankr!")
        return True
        
    def get_stats(self) -> dict:
        """Get progression statistics."""
        stages = {stage: 0 for stage in TraderStage}
        for paul in self.pauls.values():
            stages[paul.stage] += 1
            
        return {
            'total_pauls': len(self.pauls),
            'by_stage': {k.value: v for k, v in stages.items()},
            'training': stages[TraderStage.TRAINING],
            'proven': stages[TraderStage.PROVEN],
            'bankr_ready': stages[TraderStage.BANKR_READY],
            'live': stages[TraderStage.LIVE],
        }
        
    def get_eligible_for_bankr(self) -> List[str]:
        """Get list of Pauls ready for Bankr graduation."""
        return [p.paul_name for p in self.pauls.values() if p.stage == TraderStage.BANKR_READY]
        
    def get_top_trainees(self, limit: int = 10) -> List[PaulProgression]:
        """Get top performers in training."""
        trainees = [p for p in self.pauls.values() if p.stage == TraderStage.TRAINING]
        trainees.sort(key=lambda x: x.paper_roi, reverse=True)
        return trainees[:limit]


async def check_all_progressions():
    """Check all Pauls for progression opportunities."""
    print("🦷 CHECKING PAUL PROGRESSIONS")
    print("=" * 60)
    
    world = PaulWorld()
    await world.initialize()
    
    pm = ProgressionManager()
    promotions = []
    
    # Check each Paul with paper trading data
    for paul_name, portfolio in world.paper_trading.portfolios.items():
        if not portfolio.enabled:
            continue
            
        result = pm.check_progression(paul_name, portfolio)
        if result:
            promotions.append(result)
    
    # Show results
    stats = pm.get_stats()
    print(f"\n📊 Progression Stats:")
    print(f"   Training:   {stats['training']:,}")
    print(f"   Proven:     {stats['proven']:,}")
    print(f"   Bankr Ready: {stats['bankr_ready']:,}")
    print(f"   Live:       {stats['live']:,}")
    
    if promotions:
        print(f"\n🎉 Promotions:")
        for p in promotions:
            print(f"   {p}")
    else:
        print(f"\n⏳ No promotions yet. Keep training!")
    
    # Show top trainees
    top = pm.get_top_trainees(5)
    if top:
        print(f"\n🏆 Top Trainees:")
        for i, p in enumerate(top, 1):
            trades_remaining = max(0, 50 - p.paper_trades)
            print(f"   {i}. {p.paul_name[:25]:<25} {p.paper_roi:+.2%} ({p.paper_trades} trades, {trades_remaining} to proven)")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(check_all_progressions())
