"""
Swimming Pauls - User Treasury System

Single wallet per user with Paul allocation management.
Users control funds, Pauls get trading budgets.

Author: Howard (H.O.W.A.R.D)
"""

import uuid
import json
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from enum import Enum
import sqlite3


class RiskLevel(Enum):
    """Risk levels for Paul budgets."""
    CONSERVATIVE = "conservative"    # Max 5% loss, small positions
    MODERATE = "moderate"             # Max 10% loss, medium positions
    AGGRESSIVE = "aggressive"         # Max 20% loss, larger positions
    DEGEN = "degen"                   # High risk, high reward


@dataclass
class PaulAllocation:
    """Budget allocation for a single Paul."""
    paul_name: str
    max_budget: float               # Max $ this Paul can trade
    current_allocation: float = 0.0  # Currently allocated
    risk_level: RiskLevel = RiskLevel.MODERATE
    stop_loss_percent: float = 0.10   # 10% stop loss
    take_profit_percent: float = 0.20  # 20% take profit
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'paul_name': self.paul_name,
            'max_budget': self.max_budget,
            'current_allocation': self.current_allocation,
            'risk_level': self.risk_level.value,
            'stop_loss_percent': self.stop_loss_percent,
            'take_profit_percent': self.take_profit_percent,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class UserTreasury:
    """
    User's trading treasury.
    
    One wallet per user, multiple Paul allocations.
    """
    user_id: str
    user_email: str
    
    # Treasury
    total_balance: float = 0.0
    available_balance: float = 0.0
    allocated_balance: float = 0.0
    
    # Risk Guardrails
    max_total_exposure: float = 0.80     # Max 80% in trades
    max_daily_loss: float = 0.05          # Stop at 5% daily loss
    circuit_breaker: bool = False         # Emergency stop
    
    # Wallet (for live trading)
    wallet_address: Optional[str] = None
    wallet_type: str = "bankr"            # bankr, metamask, etc.
    
    # Paul Allocations
    paul_allocations: Dict[str, PaulAllocation] = field(default_factory=dict)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'user_email': self.user_email,
            'total_balance': self.total_balance,
            'available_balance': self.available_balance,
            'allocated_balance': self.allocated_balance,
            'max_total_exposure': self.max_total_exposure,
            'max_daily_loss': self.max_daily_loss,
            'circuit_breaker': self.circuit_breaker,
            'wallet_address': self.wallet_address,
            'wallet_type': self.wallet_type,
            'paul_allocations': {
                name: alloc.to_dict() 
                for name, alloc in self.paul_allocations.items()
            },
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
        }


class TreasuryManager:
    """
    Manages user treasuries and Paul allocations.
    
    Key principle: User controls all funds, Pauls get budgets.
    """
    
    def __init__(self, db_path: str = "data/treasury.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize treasury database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # User treasuries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_treasuries (
                user_id TEXT PRIMARY KEY,
                user_email TEXT NOT NULL,
                total_balance REAL DEFAULT 0,
                available_balance REAL DEFAULT 0,
                allocated_balance REAL DEFAULT 0,
                max_total_exposure REAL DEFAULT 0.80,
                max_daily_loss REAL DEFAULT 0.05,
                circuit_breaker BOOLEAN DEFAULT 0,
                wallet_address TEXT,
                wallet_type TEXT DEFAULT 'bankr',
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        # Paul allocations
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_allocations (
                allocation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                paul_name TEXT NOT NULL,
                max_budget REAL NOT NULL,
                current_allocation REAL DEFAULT 0,
                risk_level TEXT DEFAULT 'moderate',
                stop_loss_percent REAL DEFAULT 0.10,
                take_profit_percent REAL DEFAULT 0.20,
                enabled BOOLEAN DEFAULT 1,
                created_at TEXT NOT NULL,
                UNIQUE(user_id, paul_name)
            )
        ''')
        
        # Transaction history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS treasury_transactions (
                transaction_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,  -- 'deposit', 'withdrawal', 'allocation', 'trade_pnl'
                amount REAL NOT NULL,
                paul_name TEXT,
                description TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Daily loss tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_loss_tracking (
                user_id TEXT NOT NULL,
                date TEXT NOT NULL,
                daily_pnl REAL DEFAULT 0,
                circuit_breaker_triggered BOOLEAN DEFAULT 0,
                PRIMARY KEY (user_id, date)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, email: str) -> UserTreasury:
        """
        Create new user treasury.
        
        Args:
            email: User's email address
        
        Returns:
            New UserTreasury
        """
        # Generate user ID from email hash
        user_id = hashlib.sha256(email.encode()).hexdigest()[:16]
        
        treasury = UserTreasury(
            user_id=user_id,
            user_email=email,
        )
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_treasuries
            (user_id, user_email, total_balance, available_balance, allocated_balance,
             max_total_exposure, max_daily_loss, circuit_breaker, wallet_address,
             wallet_type, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, email, 0.0, 0.0, 0.0,
            0.80, 0.05, False, None, 'bankr',
            datetime.now().isoformat(),
            datetime.now().isoformat(),
        ))
        conn.commit()
        conn.close()
        
        print(f"✅ Created treasury for {email}")
        print(f"   User ID: {user_id}")
        
        return treasury
    
    def deposit(self, user_id: str, amount: float, 
                description: str = "Deposit") -> bool:
        """
        Deposit funds into user treasury.
        
        Args:
            user_id: User's ID
            amount: Amount to deposit
            description: Transaction description
        
        Returns:
            True if successful
        """
        if amount <= 0:
            print("❌ Deposit amount must be positive")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current balance
        cursor.execute('SELECT total_balance, available_balance FROM user_treasuries WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"❌ User {user_id} not found")
            conn.close()
            return False
        
        total, available = row
        
        # Update balances
        new_total = total + amount
        new_available = available + amount
        
        cursor.execute('''
            UPDATE user_treasuries 
            SET total_balance = ?, available_balance = ?, last_updated = ?
            WHERE user_id = ?
        ''', (new_total, new_available, datetime.now().isoformat(), user_id))
        
        # Log transaction
        cursor.execute('''
            INSERT INTO treasury_transactions
            (transaction_id, user_id, type, amount, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            user_id,
            'deposit',
            amount,
            description,
            datetime.now().isoformat(),
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Deposited ${amount:,.2f} to user {user_id}")
        print(f"   New balance: ${new_total:,.2f}")
        
        return True
    
    def allocate_to_paul(self, user_id: str, paul_name: str, 
                        amount: float, risk_level: RiskLevel = RiskLevel.MODERATE) -> bool:
        """
        Allocate budget to a Paul.
        
        Args:
            user_id: User's ID
            paul_name: Paul to allocate to
            amount: Budget amount
            risk_level: Risk level for this allocation
        
        Returns:
            True if successful
        """
        if amount <= 0:
            print("❌ Allocation amount must be positive")
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user treasury
        cursor.execute('SELECT available_balance, allocated_balance FROM user_treasuries WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"❌ User {user_id} not found")
            conn.close()
            return False
        
        available, allocated = row
        
        # Check if enough available
        if amount > available:
            print(f"❌ Insufficient funds. Available: ${available:,.2f}, Requested: ${amount:,.2f}")
            conn.close()
            return False
        
        # Check max exposure limit
        cursor.execute('SELECT total_balance FROM user_treasuries WHERE user_id = ?', (user_id,))
        total = cursor.fetchone()[0]
        
        max_exposure = total * 0.80  # 80% max
        if allocated + amount > max_exposure:
            print(f"❌ Would exceed max exposure limit (${max_exposure:,.2f})")
            conn.close()
            return False
        
        # Update allocation
        new_available = available - amount
        new_allocated = allocated + amount
        
        cursor.execute('''
            UPDATE user_treasuries 
            SET available_balance = ?, allocated_balance = ?, last_updated = ?
            WHERE user_id = ?
        ''', (new_available, new_allocated, datetime.now().isoformat(), user_id))
        
        # Create or update Paul allocation
        allocation_id = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT OR REPLACE INTO paul_allocations
            (allocation_id, user_id, paul_name, max_budget, current_allocation,
             risk_level, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            allocation_id,
            user_id,
            paul_name,
            amount,
            0.0,
            risk_level.value,
            datetime.now().isoformat(),
        ))
        
        # Log transaction
        cursor.execute('''
            INSERT INTO treasury_transactions
            (transaction_id, user_id, type, amount, paul_name, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4()),
            user_id,
            'allocation',
            amount,
            paul_name,
            f"Allocated ${amount:,.2f} to {paul_name}",
            datetime.now().isoformat(),
        ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Allocated ${amount:,.2f} to {paul_name}")
        print(f"   Risk level: {risk_level.value}")
        print(f"   Available: ${new_available:,.2f} | Allocated: ${new_allocated:,.2f}")
        
        return True
    
    def get_user_summary(self, user_id: str) -> Optional[Dict]:
        """Get summary of user treasury."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_id, user_email, total_balance, available_balance, 
                   allocated_balance, max_total_exposure, max_daily_loss,
                   circuit_breaker, wallet_address
            FROM user_treasuries WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        # Get Paul allocations
        cursor.execute('''
            SELECT paul_name, max_budget, current_allocation, risk_level, enabled
            FROM paul_allocations WHERE user_id = ?
        ''', (user_id,))
        
        allocations = []
        for alloc_row in cursor.fetchall():
            allocations.append({
                'paul_name': alloc_row[0],
                'max_budget': alloc_row[1],
                'current_allocation': alloc_row[2],
                'risk_level': alloc_row[3],
                'enabled': alloc_row[4],
            })
        
        conn.close()
        
        return {
            'user_id': row[0],
            'email': row[1],
            'total_balance': row[2],
            'available': row[3],
            'allocated': row[4],
            'max_exposure': row[5],
            'max_daily_loss': row[6],
            'circuit_breaker': row[7],
            'wallet': row[8],
            'paul_allocations': allocations,
        }
    
    def trigger_circuit_breaker(self, user_id: str, reason: str = "Manual") -> bool:
        """Emergency stop all trading for user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_treasuries 
            SET circuit_breaker = 1, last_updated = ?
            WHERE user_id = ?
        ''', (datetime.now().isoformat(), user_id))
        
        # Disable all Paul allocations
        cursor.execute('''
            UPDATE paul_allocations 
            SET enabled = 0
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        print(f"🛑 CIRCUIT BREAKER TRIGGERED for {user_id}")
        print(f"   Reason: {reason}")
        print(f"   All trading halted")
        
        return True
    
    def reset_circuit_breaker(self, user_id: str) -> bool:
        """Reset circuit breaker after review."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_treasuries 
            SET circuit_breaker = 0, last_updated = ?
            WHERE user_id = ?
        ''', (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Circuit breaker reset for {user_id}")
        print(f"   Trading resumed (Pauls must be re-enabled manually)")
        
        return True


# CLI Interface
def treasury_cli():
    """Command-line interface for treasury management."""
    import sys
    
    manager = TreasuryManager()
    
    if len(sys.argv) < 2:
        print("User Treasury System")
        print("Commands:")
        print("  create <email>          - Create new user treasury")
        print("  deposit <user_id> <amt> - Deposit funds")
        print("  allocate <user> <paul> <amt> [risk] - Allocate to Paul")
        print("  summary <user_id>       - Show treasury summary")
        print("  circuit <user_id> [on|off] - Circuit breaker")
        print("  list                    - List all users")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "create" and len(sys.argv) > 2:
        email = sys.argv[2]
        treasury = manager.create_user(email)
    
    elif command == "deposit" and len(sys.argv) > 3:
        user_id = sys.argv[2]
        amount = float(sys.argv[3])
        manager.deposit(user_id, amount)
    
    elif command == "allocate" and len(sys.argv) > 4:
        user_id = sys.argv[2]
        paul_name = sys.argv[3]
        amount = float(sys.argv[4])
        risk = sys.argv[5] if len(sys.argv) > 5 else "moderate"
        risk_level = RiskLevel(risk)
        manager.allocate_to_paul(user_id, paul_name, amount, risk_level)
    
    elif command == "summary" and len(sys.argv) > 2:
        user_id = sys.argv[2]
        summary = manager.get_user_summary(user_id)
        if summary:
            print(f"\n📊 Treasury Summary for {summary['email']}")
            print("=" * 60)
            print(f"Total Balance: ${summary['total_balance']:,.2f}")
            print(f"Available: ${summary['available']:,.2f}")
            print(f"Allocated: ${summary['allocated']:,.2f}")
            print(f"Max Exposure: {summary['max_exposure']:.0%}")
            print(f"Max Daily Loss: {summary['max_daily_loss']:.0%}")
            print(f"Circuit Breaker: {'🛑 ON' if summary['circuit_breaker'] else '✅ OFF'}")
            print(f"Wallet: {summary['wallet'] or 'Not connected'}")
            print(f"\nPaul Allocations ({len(summary['paul_allocations'])}):")
            for alloc in summary['paul_allocations']:
                status = "✅" if alloc['enabled'] else "❌"
                print(f"  {status} {alloc['paul_name']}: ${alloc['max_budget']:,.2f} ({alloc['risk_level']})")
        else:
            print(f"❌ User {user_id} not found")
    
    elif command == "circuit" and len(sys.argv) > 3:
        user_id = sys.argv[2]
        action = sys.argv[3]
        if action == "on":
            manager.trigger_circuit_breaker(user_id)
        elif action == "off":
            manager.reset_circuit_breaker(user_id)
    
    elif command == "list":
        conn = sqlite3.connect(manager.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id, user_email, total_balance FROM user_treasuries')
        print("\n📋 All Users:")
        print("=" * 60)
        for row in cursor.fetchall():
            print(f"{row[0][:8]}... | {row[1]} | ${row[2]:,.2f}")
        conn.close()


if __name__ == "__main__":
    treasury_cli()
