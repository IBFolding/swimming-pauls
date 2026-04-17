#!/usr/bin/env python3
"""
Scale the User Treasury System for multiple users.
Creates demo users with various allocations.
"""

import hashlib

from treasury_system import TreasuryManager, RiskLevel

import hashlib

from treasury_system import TreasuryManager, RiskLevel

manager = TreasuryManager()

print("🏦 SCALING USER TREASURY")
print("=" * 60)

# Create demo users
demo_users = [
    ("alice@example.com", 50000),
    ("bob@example.com", 25000),
    ("charlie@example.com", 100000),
    ("diana@example.com", 75000),
    ("eve@example.com", 15000),
]

for email, deposit in demo_users:
    print(f"\n👤 Creating user: {email}")
    
    # Create user
    treasury = manager.create_user(email)
    user_id = treasury.user_id
    
    # Deposit funds
    manager.deposit(user_id, deposit)
    
    # Allocate to top Pauls with different risk levels
    allocations = [
        ("Economy Paul", deposit * 0.20, RiskLevel.AGGRESSIVE),
        ("AI Paul", deposit * 0.15, RiskLevel.MODERATE),
        ("Visionary Paul", deposit * 0.10, RiskLevel.CONSERVATIVE),
        ("Quant Paul", deposit * 0.15, RiskLevel.MODERATE),
        ("Whale Paul", deposit * 0.10, RiskLevel.CONSERVATIVE),
    ]
    
    for paul_name, amount, risk in allocations:
        if amount > 0:
            manager.allocate_to_paul(user_id, paul_name, amount, risk)
    
    print(f"   💰 Deposited: ${deposit:,.2f}")
    print(f"   📊 Allocated to {len(allocations)} Pauls")

print("\n" + "=" * 60)
print("✅ Treasury scaled to 5 demo users")
print("")

# Show all users
print("📋 USER SUMMARIES:")
print("-" * 60)

for email, _ in demo_users:
    user_id = hashlib.sha256(email.encode()).hexdigest()[:16]
    summary = manager.get_user_summary(user_id)
    if summary:
        print(f"\n{email}")
        print(f"  Balance: ${summary['total_balance']:,.2f}")
        print(f"  Available: ${summary['available']:,.2f}")
        print(f"  Allocated: ${summary['allocated']:,.2f} ({len(summary['paul_allocations'])} Pauls)")

import hashlib
