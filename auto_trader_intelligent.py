#!/usr/bin/env python3
"""
Enhanced Auto-Trader with Trading Intelligence
Pauls use technical analysis, news, and market context to make smarter trades.
"""
import asyncio
import random
import time
import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from paul_world import PaulWorld
from trading_intelligence import TradingIntelligence

# Market symbols to trade
TRADING_SYMBOLS = ['BTC', 'ETH', 'SOL', 'DOGE', 'LINK']

async def intelligent_trading_loop():
    """Pauls trade using technical analysis and market intelligence."""
    print("🦷 PAUL'S WORLD - INTELLIGENT TRADING")
    print("=" * 60)
    print("Pauls now use technical analysis (RSI, MACD, Volume)")
    print("Data from CoinGecko real-time feeds")
    print()

    world = PaulWorld()
    await world.initialize()
    pt = world.paper_trading

    # Start competition
    if pt.mode.value != 'competition':
        pt.start_competition(7)
    for p in pt.portfolios.values():
        p.enabled = True

    pauls_list = list(world.pauls.keys())

    print(f"✅ {len(pauls_list):,} Pauls ready with intelligence")
    print(f"📊 Analyzing {len(TRADING_SYMBOLS)} markets")
    print(f"🏆 Competition ends: {pt.competition_end.strftime('%Y-%m-%d') if pt.competition_end else 'N/A'}")
    print("\n💰 Intelligent trading started...\n")

    trade_count = len(pt.trades)
    last_status = time.time()
    last_analysis = 0

    # Trading intelligence
    intel = TradingIntelligence()
    signals = {}

    async with intel:
        while True:
            # Refresh technical analysis every 5 minutes
            if time.time() - last_analysis > 300:
                print("📊 Updating technical analysis...")
                for symbol in TRADING_SYMBOLS:
                    try:
                        signal = await intel.analyze_technicals(symbol)
                        signals[symbol] = signal
                        print(f"   {symbol}: {signal.recommendation} (Score: {signal.technical_score:+.0f})")
                    except Exception as e:
                        print(f"   ⚠️ {symbol} analysis failed: {e}")
                print()
                last_analysis = time.time()

            # Random Paul analyzes opportunity every 2-5 seconds
            await asyncio.sleep(random.uniform(2, 5))

            paul_name = random.choice(pauls_list)

            # Pick symbol with best signal if available
            if signals:
                # Weight by technical score - higher score = more likely to trade
                weights = []
                for sym in TRADING_SYMBOLS:
                    if sym in signals:
                        score = signals[sym].technical_score
                        # Convert -100 to +100 score into positive weight
                        weight = max(1, score + 100)
                        weights.append(weight)
                    else:
                        weights.append(50)  # Neutral

                symbol = random.choices(TRADING_SYMBOLS, weights=weights, k=1)[0]
                signal = signals.get(symbol)
            else:
                symbol = random.choice(TRADING_SYMBOLS)
                signal = None

            # Get current price from signal or fallback
            if signal and signal.price > 0:
                price = signal.price
                
                # Adjust confidence based on technical score
                base_confidence = random.uniform(0.70, 0.95)
                
                # Strong signals get higher confidence
                if signal.technical_score > 50:
                    confidence = min(0.98, base_confidence + 0.1)
                    sentiment = 'bullish'
                elif signal.technical_score < -50:
                    confidence = min(0.98, base_confidence + 0.1)
                    sentiment = 'bearish'
                else:
                    confidence = base_confidence
                    sentiment = random.choice(['bullish', 'bearish'])
                
                # ATR-based position sizing (smaller positions on volatile assets)
                if signal.atr_percent > 5:  # Very volatile
                    confidence *= 0.8  # Reduce confidence
                    reason = f"High volatility ({signal.atr_percent:.1f}% ATR)"
                elif signal.volume_ratio < 0.5:  # Low volume
                    confidence *= 0.7
                    reason = "Low volume confirmation"
                else:
                    reason = f"Technical score: {signal.technical_score:+.0f}"
            else:
                # Fallback to random
                price = 100  # Will be updated
                confidence = random.uniform(0.75, 0.95)
                sentiment = random.choice(['bullish', 'bearish'])
                reason = "No signal available"

            direction = 'buy' if sentiment == 'bullish' else 'sell'

            # Execute trade
            trade = pt.execute_trade(
                paul_name=paul_name,
                symbol=symbol,
                direction=direction,
                current_price=price,
                confidence=confidence
            )

            if trade:
                trade_count += 1
                emoji = "🚀" if sentiment == 'bullish' else "🔻"
                score_str = f"[{signal.technical_score:+.0f}]" if signal else ""
                print(f"{emoji} {paul_name[:15]:<15} {direction.upper():4} {symbol:<6} @ ${price:>10,.2f} {score_str} | {reason}")

            # Status every 30 seconds
            if time.time() - last_status > 30:
                print("\n" + "=" * 60)
                print("📊 STATUS")
                print(f"   Total trades: {trade_count}")
                print(f"   Open positions: {sum(len(p.positions) for p in pt.portfolios.values())}")

                # Show best signal
                if signals:
                    best = max(signals.values(), key=lambda x: x.technical_score)
                    print(f"\n🎯 Best Signal: {best.symbol} {best.recommendation} ({best.technical_score:+.0f})")

                lb = pt.get_leaderboard(3)
                if lb:
                    print("\n🏆 Top 3:")
                    for e in lb[:3]:
                        emoji = "🚀" if e['roi'] > 0.05 else "📈" if e['roi'] > 0 else "📉"
                        print(f"   {emoji} {e['paul_name'][:20]:<20} ${e['total_value']:>9,.0f} ({e['roi']:+5.1%})")

                print("=" * 60 + "\n")
                await world._save_world()
                last_status = time.time()

if __name__ == "__main__":
    random.seed(int(time.time()))
    try:
        asyncio.run(intelligent_trading_loop())
    except KeyboardInterrupt:
        print("\n\n👋 Stopping intelligent trading...")
