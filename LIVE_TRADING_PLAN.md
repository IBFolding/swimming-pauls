# Swimming Pauls - Live Trading Infrastructure Plan

## Overview
Transition from paper trading to live trading requires secure wallet management, exchange integration, risk controls, and gradual deployment.

---

## Phase 1: Wallet Infrastructure

### 1.1 Wallet Generation & Security
```python
# wallets/wallet_manager.py
class WalletManager:
    """Secure wallet generation and management."""
    
    def create_paul_wallet(self, paul_name: str) -> Dict:
        """
        Create a dedicated wallet for each Paul or group of Pauls.
        
        Options:
        1. Individual wallets: Each Paul has their own wallet (high security, complex)
        2. Strategy wallets: Wallets by strategy type (conservative, aggressive, etc.)
        3. Single treasury: One main wallet with internal accounting (simplest)
        
        Recommended: Strategy wallets with 2-of-3 multisig
        """
        pass
    
    def store_encrypted_keys(self, wallet_data: Dict):
        """
        Store private keys encrypted with:
        - Hardware Security Module (HSM) or
        - AWS KMS / GCP KMS or
        - Local encrypted storage with strong passphrase
        """
        pass
```

### 1.2 Supported Wallets
- **EOAs (Externally Owned Accounts)**: Standard wallets for most trading
- **Smart Contract Wallets**: Gnosis Safe, Argent for multisig
- **Hardware Wallets**: Ledger/Trezor for cold storage of treasury
- **MPC Wallets**: Fireblocks, Coinbase Custody for institutional

### 1.3 Security Levels
```
Level 1 - Hot Wallets (small amounts for active trading)
  └── Limit: $1,000 per wallet
  └── Auto-refill from treasury
  └── 2FA required

Level 2 - Warm Wallets (medium amounts, daily limits)
  └── Limit: $10,000 per wallet
  └── Multisig (2-of-3)
  └── Daily spending caps

Level 3 - Cold Storage (treasury, majority of funds)
  └── Hardware wallet
  └── Multisig (3-of-5)
  └── Time-delayed withdrawals
  └── Geographic distribution of keys
```

---

## Phase 2: Exchange Integration

### 2.1 Supported Exchanges
```python
# exchanges/exchange_manager.py
EXCHANGES = {
    'hyperliquid': {
        'type': 'perp_dex',
        'requires_api_key': True,
        'supports': ['spot', 'perps'],
        'chains': ['arbitrum'],
    },
    'binance': {
        'type': 'cex',
        'requires_api_key': True,
        'supports': ['spot', 'futures', 'margin'],
        'kyc_required': True,
    },
    'coinbase': {
        'type': 'cex',
        'requires_api_key': True,
        'supports': ['spot'],
        'kyc_required': True,
        'institutional': True,
    },
    'jupiter': {
        'type': 'dex_aggregator',
        'requires_api_key': False,
        'supports': ['spot'],
        'chains': ['solana'],
    },
    'uniswap': {
        'type': 'dex',
        'requires_api_key': False,
        'supports': ['spot'],
        'chains': ['ethereum', 'arbitrum', 'base'],
    }
}
```

### 2.2 API Key Management
```python
# config/exchange_config.yaml
exchanges:
  hyperliquid:
    api_key: ${HYPERLIQUID_API_KEY}  # Environment variable
    api_secret: ${HYPERLIQUID_SECRET}
    wallet_address: ${HYPERLIQUID_WALLET}
    testnet: false
    
  binance:
    api_key: ${BINANCE_API_KEY}
    api_secret: ${BINANCE_SECRET}
    # IP whitelist required
    # Withdrawal whitelist required
    
jupiter:
  # No API key needed
  slippage_bps: 50  # 0.5%
  
risk_limits:
  max_position_size_usd: 10000
  max_daily_volume_usd: 50000
  max_drawdown_pct: 10
```

### 2.3 Paper Trading → Live Trading Graduation
```python
# trading/graduation_criteria.py
GRADUATION_CRITERIA = {
    'min_paper_trades': 100,
    'min_accuracy_rate': 0.55,  # Beat random
    'min_sharpe_ratio': 1.0,
    'max_drawdown_pct': 15,
    'min_trading_days': 30,
    'consistency_score': 0.7,  # Not just lucky streaks
}

def should_graduate_to_live(paul_stats: Dict) -> bool:
    """
    Determine if a Paul is ready for live trading.
    """
    checks = [
        paul_stats['total_trades'] >= GRADUATION_CRITERIA['min_paper_trades'],
        paul_stats['accuracy_rate'] >= GRADUATION_CRITERIA['min_accuracy_rate'],
        paul_stats['sharpe_ratio'] >= GRADUATION_CRITERIA['min_sharpe_ratio'],
        paul_stats['max_drawdown'] <= GRADUATION_CRITERIA['max_drawdown_pct'],
        paul_stats['trading_days'] >= GRADUATION_CRITERIA['min_trading_days'],
    ]
    return all(checks)
```

---

## Phase 3: Risk Management System

### 3.1 Position Sizing
```python
# risk/position_sizing.py
class PositionSizer:
    """Calculate safe position sizes."""
    
    def kelly_criterion(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Kelly formula: f* = (bp - q) / b
        where b = avg_win/avg_loss, p = win_rate, q = 1-p
        """
        b = avg_win / avg_loss
        p = win_rate
        q = 1 - p
        kelly = (b * p - q) / b
        return min(kelly * 0.25, 0.05)  # Quarter Kelly, max 5%
    
    def fixed_fraction(self, confidence: float, bankroll: float, max_risk: float = 0.02) -> float:
        """
        Risk fixed percentage of bankroll per trade.
        """
        base_risk = bankroll * max_risk
        # Scale by confidence (higher confidence = slightly larger position)
        confidence_multiplier = 0.5 + (confidence * 0.5)  # 0.5x to 1.0x
        return base_risk * confidence_multiplier
```

### 3.2 Risk Limits
```python
# risk/risk_manager.py
RISK_RULES = {
    # Per-trade limits
    'max_position_size_pct': 0.05,  # 5% of portfolio max
    'max_position_size_usd': 10000,  # $10k max per trade
    'max_leverage': 3,  # 3x max
    
    # Daily limits
    'max_daily_trades': 20,
    'max_daily_volume_usd': 50000,
    'max_daily_loss_pct': 5,  # Stop trading after 5% daily loss
    
    # Portfolio limits
    'max_drawdown_pct': 15,  # Pause all trading at 15% drawdown
    'max_correlation': 0.8,  # Don't hold correlated positions
    'min_cash_buffer_pct': 20,  # Keep 20% in cash/stablecoins
    
    # Paul-specific
    'max_trades_per_paul_per_day': 5,
    'paul_cooldown_minutes': 30,  # Between trades
}
```

### 3.3 Circuit Breakers
```python
# risk/circuit_breakers.py
class CircuitBreakers:
    """Emergency stops for trading."""
    
    def check_all(self, portfolio: Dict, market_conditions: Dict) -> Dict:
        """
        Check all circuit breakers.
        """
        breaks = []
        
        # 1. Portfolio drawdown
        if portfolio['drawdown_pct'] > RISK_RULES['max_drawdown_pct']:
            breaks.append({
                'type': 'DRAWDOWN',
                'severity': 'CRITICAL',
                'action': 'STOP_ALL_TRADING',
                'message': f"Drawdown {portfolio['drawdown_pct']}% exceeds limit"
            })
        
        # 2. Daily loss limit
        if portfolio['daily_pnl_pct'] < -RISK_RULES['max_daily_loss_pct']:
            breaks.append({
                'type': 'DAILY_LOSS',
                'severity': 'HIGH',
                'action': 'STOP_NEW_POSITIONS',
                'message': f"Daily loss {portfolio['daily_pnl_pct']}% exceeds limit"
            })
        
        # 3. Market volatility
        if market_conditions['vix'] > 40:  # High fear
            breaks.append({
                'type': 'HIGH_VOLATILITY',
                'severity': 'MEDIUM',
                'action': 'REDUCE_POSITION_SIZES',
                'message': "Market volatility too high"
            })
        
        # 4. Exchange issues
        if market_conditions['exchange_status'] != 'normal':
            breaks.append({
                'type': 'EXCHANGE_ISSUE',
                'severity': 'HIGH',
                'action': 'HALT_TRADING',
                'message': f"Exchange issue: {market_conditions['exchange_status']}"
            })
        
        # 5. Liquidity check
        if portfolio['cash_ratio'] < RISK_RULES['min_cash_buffer_pct']:
            breaks.append({
                'type': 'LOW_LIQUIDITY',
                'severity': 'MEDIUM',
                'action': 'STOP_NEW_POSITIONS',
                'message': f"Cash buffer {portfolio['cash_ratio']}% below minimum"
            })
        
        return {
            'should_trade': len(breaks) == 0,
            'breaks': breaks,
            'highest_severity': max([b['severity'] for b in breaks], default='NONE')
        }
```

---

## Phase 4: Trade Execution

### 4.1 Order Types & Execution
```python
# trading/order_executor.py
class OrderExecutor:
    """Execute trades with safety checks."""
    
    async def execute_trade(self, signal: Dict, wallet: Dict) -> Dict:
        """
        Execute a trade with multiple safety layers.
        """
        # 1. Pre-trade checks
        risk_check = self.risk_manager.check_trade(signal)
        if not risk_check['approved']:
            return {'status': 'REJECTED', 'reason': risk_check['reason']}
        
        # 2. Get best price
        quote = await self.get_best_quote(signal)
        
        # 3. Confirm with user (for large trades)
        if signal['size_usd'] > 1000:
            confirmed = await self.confirm_with_user(signal, quote)
            if not confirmed:
                return {'status': 'CANCELLED', 'reason': 'User cancelled'}
        
        # 4. Submit order
        order = await self.submit_order(signal, quote, wallet)
        
        # 5. Monitor execution
        filled = await self.monitor_execution(order)
        
        # 6. Record in database
        await self.record_trade(signal, order, filled)
        
        return filled
    
    async def get_best_quote(self, signal: Dict) -> Dict:
        """
        Compare quotes across exchanges for best price.
        """
        quotes = await asyncio.gather(*[
            self.get_quote(exchange, signal)
            for exchange in self.exchanges
        ])
        
        # Filter for liquidity
        valid_quotes = [q for q in quotes if q['liquidity_sufficient']]
        
        # Sort by total cost including fees
        best = min(valid_quotes, key=lambda x: x['total_cost'])
        return best
```

### 4.2 Trade Confirmation Flow
```python
# Large trades require confirmation
CONFIRMATION_THRESHOLDS = {
    'telegram_notification': 500,    # $500+ notify
    'user_confirmation': 2000,       # $2000+ require confirm
    'multisig_required': 10000,      # $10k+ require multisig
    'time_delay': 50000,             # $50k+ 24h time delay
}

async def confirm_trade(signal: Dict) -> bool:
    """
    Get confirmation for large trades.
    """
    size = signal['size_usd']
    
    if size >= CONFIRMATION_THRESHOLDS['time_delay']:
        # Schedule for delayed execution
        await schedule_delayed_execution(signal, delay_hours=24)
        return False
    
    if size >= CONFIRMATION_THRESHOLDS['multisig_required']:
        # Require multisig approval
        approval = await request_multisig_approval(signal)
        return approval
    
    if size >= CONFIRMATION_THRESHOLDS['user_confirmation']:
        # Send Telegram notification with confirm/cancel buttons
        response = await send_telegram_confirmation(signal)
        return response == 'CONFIRM'
    
    if size >= CONFIRMATION_THRESHOLDS['telegram_notification']:
        # Just notify, no confirmation needed
        await send_telegram_notification(signal)
        return True
    
    # Small trade, auto-execute
    return True
```

---

## Phase 5: Monitoring & Alerting

### 5.1 Real-Time Monitoring
```python
# monitoring/trade_monitor.py
class TradeMonitor:
    """Monitor live trading in real-time."""
    
    async def monitor_loop(self):
        while True:
            # Check positions every 30 seconds
            positions = await self.get_all_positions()
            
            for position in positions:
                # Check stop loss
                if position['unrealized_pnl_pct'] < -5:
                    await self.alert_stop_loss_approaching(position)
                
                # Check take profit
                if position['unrealized_pnl_pct'] > 20:
                    await self.alert_take_profit_opportunity(position)
                
                # Check if thesis invalidated
                if await self.is_thesis_invalidated(position):
                    await self.alert_exit_recommendation(position)
            
            # Check portfolio health
            portfolio = await self.get_portfolio_summary()
            if portfolio['drawdown_pct'] > 10:
                await self.alert_drawdown_warning(portfolio)
            
            await asyncio.sleep(30)
```

### 5.2 Alert Channels
```yaml
# config/alerts.yaml
alerts:
  telegram:
    enabled: true
    bot_token: ${TELEGRAM_BOT_TOKEN}
    chat_id: ${TELEGRAM_CHAT_ID}
    
  discord:
    enabled: true
    webhook_url: ${DISCORD_WEBHOOK_URL}
    
  email:
    enabled: false
    smtp_server: smtp.gmail.com
    smtp_port: 587
    username: ${EMAIL_USER}
    password: ${EMAIL_PASS}
    
  sms:
    enabled: false
    twilio_sid: ${TWILIO_SID}
    twilio_token: ${TWILIO_TOKEN}
    phone_number: ${PHONE_NUMBER}

alert_levels:
  info: ['telegram']
  warning: ['telegram', 'discord']
  critical: ['telegram', 'discord', 'email', 'sms']
```

---

## Phase 6: Deployment Strategy

### 6.1 Gradual Rollout
```
Week 1-2: Single Paul, $100 allocation
  └── Verify execution, wallet management, reporting

Week 3-4: Top 5 Pauls, $100 each ($500 total)
  └── Test multi-agent coordination, position sizing

Week 5-8: Top 20 Pauls, $250 each ($5,000 total)
  └── Stress test risk management, circuit breakers

Month 3+: Full deployment
  └── All qualified Pauls, up to $100k total allocation
```

### 6.2 Environments
```python
ENVIRONMENTS = {
    'paper': {
        'trades_are_real': False,
        'prices_are_real': True,
        'allocation': 'unlimited',
        'purpose': 'Training and strategy validation'
    },
    'testnet': {
        'trades_are_real': True,
        'prices_are_real': True,
        'blockchain_is_test': True,
        'allocation': '$1,000',
        'purpose': 'Test real execution with fake money'
    },
    'live_small': {
        'trades_are_real': True,
        'allocation': '$5,000',
        'max_position': '$500',
        'purpose': 'Limited live trading'
    },
    'live_full': {
        'trades_are_real': True,
        'allocation': '$100,000+',
        'purpose': 'Full production trading'
    }
}
```

### 6.3 Emergency Procedures
```python
EMERGENCY_PROCEDURES = {
    'HACK_DETECTED': {
        'immediate_actions': [
            'STOP_ALL_TRADING',
            'REVOKE_ALL_API_KEYS',
            'TRANSFER_FUNDS_TO_COLD_STORAGE',
            'ALERT_TEAM'
        ],
        'within_1_hour': [
            'AUDIT_ALL_TRANSACTIONS',
            'CHECK_ALL_WALLET_BALANCES',
            'DOCUMENT_INCIDENT'
        ],
        'within_24_hours': [
            'FULL_SECURITY_AUDIT',
            'ROTATE_ALL_KEYS',
            'IMPLEMENT_ADDITIONAL_SECURITY'
        ]
    },
    'EXCHANGE_DOWN': {
        'immediate_actions': [
            'HALT_TRADING_ON_AFFECTED_EXCHANGE',
            'DIVERT_TRADES_TO_BACKUP_EXCHANGE',
            'NOTIFY_TEAM'
        ]
    },
    'MAJOR_BUG': {
        'immediate_actions': [
            'STOP_ALL_TRADING',
            'ROLLBACK_TO_LAST_STABLE_VERSION',
            'NOTIFY_TEAM'
        ]
    }
}
```

---

## Phase 7: Compliance & Legal

### 7.1 Required Disclosures
- All trades are algorithmic/automated
- Past performance doesn't guarantee future results
- Users control their own funds at all times
- System may experience downtime or bugs
- Maximum allocation recommendations based on risk tolerance

### 7.2 Regulatory Considerations
- **US**: Register as exempt adviser if managing >$25M for others
- **EU**: MiFID II compliance for algorithmic trading
- **Global**: Maintain audit logs for 7 years
- **Tax**: Automated tax reporting (1099, etc.)

### 7.3 Insurance
- **Cyber insurance**: Cover hacks and breaches
- **E&O insurance**: Errors and omissions
- **Custody insurance**: For funds held with third parties

---

## Implementation Priority

### Must Have (Before Live Trading)
1. ✅ Wallet generation and secure storage
2. ✅ Exchange API integration (at least 2 exchanges)
3. ✅ Position sizing and risk limits
4. ✅ Circuit breakers
5. ✅ Trade confirmation for large orders
6. ✅ Real-time monitoring and alerting
7. ✅ Emergency stop button
8. ✅ Audit logging

### Should Have (First Month Live)
9. Multi-exchange price comparison
10. Smart order routing
11. Advanced risk metrics (VaR, etc.)
12. Automated tax reporting
13. Performance attribution analysis

### Nice to Have (Ongoing)
14. Machine learning for execution optimization
15. Cross-chain arbitrage
16. Options/strategies support
17. Institutional custody integration

---

## Budget Estimate

| Component | Cost (Monthly) |
|-----------|----------------|
| VPS/Server | $50-200 |
| Exchange API fees | 0.05-0.1% of volume |
| Security audit (one-time) | $10,000-50,000 |
| Insurance | $500-2,000 |
| Monitoring tools | $100-500 |
| **Total (Small Scale)** | **$650-2,700/month + audit** |
| **Total (Institutional)** | **$5,000-20,000/month + audit** |

---

## Summary

**Phase 1**: Secure wallet infrastructure (2 weeks)
**Phase 2**: Exchange integration (2 weeks)
**Phase 3**: Risk management system (2 weeks)
**Phase 4**: Execution engine (2 weeks)
**Phase 5**: Monitoring (1 week)
**Phase 6**: Gradual rollout (3 months)

**Total to first live trade**: ~2 months
**Total to full deployment**: ~4 months

**Next steps**:
1. Choose wallet strategy (recommend: Gnosis Safe multisig)
2. Set up testnet environment
3. Implement wallet manager
4. Connect first exchange (recommend: Hyperliquid for perps)
5. Run paper trading with real execution logic
6. Graduate to testnet
7. Gradual live rollout
