#!/usr/bin/env python3
"""
Swimming Pauls - Prediction Resolver
Automatically checks if predictions came true using market data.

Usage:
    python resolve_predictions.py                    # Check all pending predictions
    python resolve_predictions.py --id abc123       # Resolve specific prediction
    python resolve_predictions.py --auto            # Auto-resolve based on current prices
    python resolve_predictions.py --list            # Show all predictions with status
"""

import json
import argparse
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')
sys.path.insert(0, '/Users/brain/.openclaw/workspace/skills/crypto-price')

from price_tracker import PriceTracker

class PredictionResolver:
    """Resolves predictions against actual market data."""
    
    def __init__(self, results_dir: str = "data/results"):
        self.results_dir = Path(results_dir)
        self.resolved_file = self.results_dir / "_resolved.json"
        self.resolved_cache = self._load_resolved_cache()
        self.price_tracker = PriceTracker(str(self.results_dir.parent))
        
    def _load_resolved_cache(self) -> Dict:
        """Load cache of resolved predictions."""
        if self.resolved_file.exists():
            with open(self.resolved_file) as f:
                return json.load(f)
        return {}
    
    def _save_resolved_cache(self):
        """Save resolved cache."""
        with open(self.resolved_file, 'w') as f:
            json.dump(self.resolved_cache, f, indent=2)
    
    def get_all_predictions(self) -> List[Dict]:
        """Get all predictions from results directory."""
        predictions = []
        
        for f in self.results_dir.glob("*.json"):
            if f.name.startswith('_'):  # Skip cache files
                continue
                
            try:
                with open(f) as file:
                    data = json.load(file)
                    data['file_id'] = f.stem
                    data['resolved'] = self.resolved_cache.get(f.stem, {})
                    predictions.append(data)
            except Exception as e:
                print(f"⚠️  Error loading {f}: {e}")
                
        return sorted(predictions, key=lambda x: x.get('saved_at', ''), reverse=True)
    
    def parse_question(self, question: str) -> Dict:
        """Parse prediction question to extract target and conditions."""
        question_lower = question.lower()
        
        # Extract crypto symbols
        crypto_pattern = r'\b(btc|eth|sol|doge|link|avax|matic|arb|op|uni|aave|comp|bnb|ada|dot)\b'
        cryptos = re.findall(crypto_pattern, question_lower)
        
        # Extract price targets
        price_pattern = r'\$?([\d,]+(?:\.\d+)?)[kK]?'
        prices = re.findall(price_pattern, question)
        prices = [float(p.replace(',', '')) for p in prices]
        
        # Extract timeframes
        timeframe = None
        if 'by end of 2025' in question_lower or '2025' in question_lower:
            timeframe = '2025-12-31'
        elif 'by end of 2026' in question_lower or '2026' in question_lower:
            timeframe = '2026-12-31'
        elif 'this year' in question_lower:
            timeframe = f"{datetime.now().year}-12-31"
        elif 'this month' in question_lower:
            next_month = datetime.now() + timedelta(days=30)
            timeframe = next_month.strftime('%Y-%m-01')
        elif 'next week' in question_lower:
            next_week = datetime.now() + timedelta(days=7)
            timeframe = next_week.strftime('%Y-%m-%d')
        
        # Determine prediction type
        prediction_type = 'unknown'
        if any(word in question_lower for word in ['reach', 'hit', 'go to', 'above']):
            prediction_type = 'price_target'
        elif any(word in question_lower for word in ['buy', 'best', 'top', 'winner']):
            prediction_type = 'top_pick'
        elif any(word in question_lower for word in ['up', 'down', 'bullish', 'bearish', 'crash', 'pump']):
            prediction_type = 'direction'
        
        return {
            'cryptos': list(set(cryptos)),
            'prices': prices,
            'timeframe': timeframe,
            'type': prediction_type,
            'question': question
        }
    
    def fetch_current_price(self, symbol: str) -> Optional[float]:
        """Fetch current price for a symbol."""
        try:
            import subprocess
            result = subprocess.run(
                ['python3', '/Users/brain/.openclaw/workspace/skills/crypto-price/scripts/get_price_chart.py', symbol.upper(), '1h'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get('price')
        except Exception as e:
            print(f"   ⚠️  Could not fetch price for {symbol}: {e}")
        return None
    
    def resolve_prediction(self, prediction: Dict, auto: bool = False) -> Dict:
        """Resolve a single prediction."""
        file_id = prediction.get('file_id', 'unknown')
        question = prediction.get('question', '')
        consensus = prediction.get('consensus', {})
        direction = consensus.get('direction', 'NEUTRAL')
        
        parsed = self.parse_question(question)
        
        print(f"\n🔮 {file_id}")
        print(f"   Q: {question[:60]}...")
        print(f"   Type: {parsed['type']} | Consensus: {direction}")
        
        # Check if already resolved
        if file_id in self.resolved_cache and not auto:
            existing = self.resolved_cache[file_id]
            print(f"   ✅ Already resolved: {existing.get('outcome', 'UNKNOWN')}")
            return existing
        
        # Resolve based on type
        if parsed['type'] == 'price_target' and parsed['cryptos'] and parsed['prices']:
            return self._resolve_price_target(file_id, parsed, direction, prediction)
        elif parsed['type'] == 'top_pick' and parsed['cryptos']:
            return self._resolve_top_pick(file_id, parsed, prediction)
        elif parsed['type'] == 'direction' and parsed['cryptos']:
            return self._resolve_direction(file_id, parsed, direction, prediction)
        else:
            print(f"   ⚠️  Cannot auto-resolve (unknown type or missing data)")
            return {'outcome': 'PENDING', 'reason': 'Cannot parse prediction'}
    
    def _resolve_price_target(self, file_id: str, parsed: Dict, consensus: str, prediction: Dict) -> Dict:
        """Resolve a price target prediction."""
        symbol = parsed['cryptos'][0].upper()
        target = parsed['prices'][0] if parsed['prices'] else None
        
        if not target:
            return {'outcome': 'PENDING', 'reason': 'No price target found'}
        
        # Handle K suffix
        if 'k' in parsed['question'].lower() or target < 100:
            if target < 100:  # Likely means thousands (e.g., "100k")
                target *= 1000
        
        current_price = self.fetch_current_price(symbol)
        if not current_price:
            return {'outcome': 'PENDING', 'reason': f'Could not fetch {symbol} price'}
        
        # Determine if target was reached
        # For bullish predictions: current >= target = CORRECT
        # For bearish predictions: current < target = CORRECT
        if consensus == 'BULLISH':
            outcome = 'CORRECT' if current_price >= target else 'INCORRECT'
        elif consensus == 'BEARISH':
            outcome = 'CORRECT' if current_price < target else 'INCORRECT'
        else:
            outcome = 'PENDING'
        
        result = {
            'outcome': outcome,
            'symbol': symbol,
            'target_price': target,
            'current_price': current_price,
            'consensus': consensus,
            'resolved_at': datetime.now().isoformat(),
            'reason': f'{symbol} at ${current_price:,.2f} vs target ${target:,.2f}'
        }
        
        self.resolved_cache[file_id] = result
        self._save_resolved_cache()
        
        print(f"   ✅ Resolved: {outcome}")
        print(f"      {result['reason']}")
        
        return result
    
    def _resolve_top_pick(self, file_id: str, parsed: Dict, prediction: Dict) -> Dict:
        """Resolve a top pick prediction."""
        top_picks = prediction.get('top_picks', [])
        if not top_picks:
            return {'outcome': 'PENDING', 'reason': 'No top picks recorded'}
        
        # Get current prices for all picks
        performance = {}
        for pick in top_picks:
            price = self.fetch_current_price(pick)
            if price:
                performance[pick] = price
        
        if not performance:
            return {'outcome': 'PENDING', 'reason': 'Could not fetch prices'}
        
        # Compare performance (simplified - just check if any pick went up)
        # In reality, we'd need historical prices at prediction time
        # For now, mark as PENDING until we have better data
        
        result = {
            'outcome': 'PENDING',
            'top_picks': top_picks,
            'current_prices': performance,
            'resolved_at': datetime.now().isoformat(),
            'reason': 'Need historical data for accurate resolution'
        }
        
        print(f"   ⏳ PENDING: Need historical data for {top_picks}")
        
        return result
    
    def _resolve_direction(self, file_id: str, parsed: Dict, consensus: str, prediction: Dict) -> Dict:
        """Resolve a direction prediction (bullish/bearish)."""
        if not parsed['cryptos']:
            return {'outcome': 'PENDING', 'reason': 'No crypto specified'}
        
        symbol = parsed['cryptos'][0].upper()
        
        # Try to get price change from price tracker
        prediction_time = prediction.get('saved_at')
        if not prediction_time:
            # Try file modification time as fallback
            pred_file = self.results_dir / f"{file_id}.json"
            if pred_file.exists():
                import os
                mtime = os.path.getmtime(pred_file)
                prediction_time = datetime.fromtimestamp(mtime).isoformat()
        
        if prediction_time:
            change_data = self.price_tracker.get_price_change(symbol, prediction_time)
            if change_data:
                actual_direction = 'UP' if change_data['change_pct'] > 0 else 'DOWN'
                
                # Determine if prediction was correct
                # Bullish = expected UP, Bearish = expected DOWN
                if consensus == 'BULLISH':
                    outcome = 'CORRECT' if actual_direction == 'UP' else 'INCORRECT'
                elif consensus == 'BEARISH':
                    outcome = 'CORRECT' if actual_direction == 'DOWN' else 'INCORRECT'
                else:  # NEUTRAL
                    outcome = 'CORRECT' if abs(change_data['change_pct']) < 2 else 'INCORRECT'
                
                result = {
                    'outcome': outcome,
                    'symbol': symbol,
                    'start_price': change_data['start_price'],
                    'current_price': change_data['current_price'],
                    'change_pct': change_data['change_pct'],
                    'actual_direction': actual_direction,
                    'predicted_direction': consensus,
                    'resolved_at': datetime.now().isoformat(),
                    'reason': f"{symbol} moved {change_data['change_pct']:+.2f}% ({actual_direction}) vs {consensus} prediction"
                }
                
                self.resolved_cache[file_id] = result
                self._save_resolved_cache()
                
                print(f"   ✅ Resolved: {outcome}")
                print(f"      {result['reason']}")
                
                return result
        
        # Fallback: just get current price
        current_price = self.fetch_current_price(symbol)
        if current_price:
            result = {
                'outcome': 'PENDING',
                'symbol': symbol,
                'current_price': current_price,
                'consensus': consensus,
                'resolved_at': datetime.now().isoformat(),
                'reason': 'Need price history at prediction time - run price_tracker.py'
            }
            print(f"   ⏳ PENDING: Run 'python price_tracker.py' to record historical prices")
            return result
        
        return {'outcome': 'PENDING', 'reason': f'Could not fetch {symbol} price'}
    
    def generate_leaderboard(self) -> List[Dict]:
        """Generate Paul accuracy leaderboard."""
        # Load all predictions
        predictions = self.get_all_predictions()
        
        # Track Paul performance
        paul_stats = {}
        
        for pred in predictions:
            file_id = pred.get('file_id')
            resolved = pred.get('resolved', {})
            outcome = resolved.get('outcome', 'PENDING')
            
            if outcome == 'PENDING':
                continue
            
            # Handle both "agents" and "responses" formats
            agents = pred.get('agents', [])
            if not agents:
                # Try "responses" format (from Paul's World)
                responses = pred.get('responses', [])
                agents = [
                    {
                        'name': r.get('paul_name', 'Unknown'),
                        'specialty': r.get('specialty', 'General'),
                        'reasoning': r.get('reasoning', '')
                    }
                    for r in responses
                ]
            
            consensus = pred.get('consensus', {}).get('direction', 'NEUTRAL')
            
            for agent in agents:
                name = agent.get('name', 'Unknown')
                reasoning = agent.get('reasoning', '').lower()
                
                # Determine if this Paul agreed with consensus
                agreed = self._paul_agreed_with_consensus(reasoning, consensus)
                
                if name not in paul_stats:
                    paul_stats[name] = {
                        'name': name,
                        'specialty': agent.get('specialty', 'General'),
                        'total': 0,
                        'correct': 0,
                        'accuracy': 0.0
                    }
                
                paul_stats[name]['total'] += 1
                if agreed == (outcome == 'CORRECT'):
                    paul_stats[name]['correct'] += 1
        
        # Calculate accuracy
        for stats in paul_stats.values():
            if stats['total'] > 0:
                stats['accuracy'] = stats['correct'] / stats['total']
        
        # Sort by accuracy (min 1 prediction)
        leaderboard = sorted(
            [s for s in paul_stats.values() if s['total'] >= 1],
            key=lambda x: (x['accuracy'], x['total']),
            reverse=True
        )
        
        return leaderboard
    
    def _paul_agreed_with_consensus(self, reasoning: str, consensus: str) -> bool:
        """Determine if a Paul's reasoning aligns with consensus."""
        reasoning_lower = reasoning.lower()
        
        bullish_words = ['bull', 'up', 'growth', 'moon', 'pump', 'breakout', 'accumulate']
        bearish_words = ['bear', 'down', 'crash', 'dump', 'sell', 'cautious', 'correction']
        
        bullish_count = sum(1 for w in bullish_words if w in reasoning_lower)
        bearish_count = sum(1 for w in bearish_words if w in reasoning_lower)
        
        if consensus == 'BULLISH':
            return bullish_count >= bearish_count
        elif consensus == 'BEARISH':
            return bearish_count >= bullish_count
        else:
            return bullish_count == bearish_count
    
    def print_leaderboard(self):
        """Print the Paul accuracy leaderboard."""
        leaderboard = self.generate_leaderboard()
        
        print("\n" + "=" * 70)
        print("🏆 PAUL ACCURACY LEADERBOARD")
        print("=" * 70)
        print(f"{'Rank':<6} {'Name':<20} {'Specialty':<15} {'Correct':<10} {'Total':<8} {'Accuracy':<10}")
        print("-" * 70)
        
        for i, paul in enumerate(leaderboard[:20], 1):
            rank = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:3d}"
            accuracy_str = f"{paul['accuracy']*100:.1f}%"
            print(f"{rank:<6} {paul['name']:<20} {paul['specialty']:<15} {paul['correct']:<10} {paul['total']:<8} {accuracy_str:<10}")
        
        print("=" * 70)
        print(f"\n📊 Total Pauls tracked: {len(leaderboard)}")
        
        # Show specialty breakdown
        specialties = {}
        for paul in leaderboard:
            spec = paul['specialty']
            if spec not in specialties:
                specialties[spec] = {'total': 0, 'correct': 0}
            specialties[spec]['total'] += paul['total']
            specialties[spec]['correct'] += paul['correct']
        
        print("\n📈 By Specialty:")
        for spec, stats in sorted(specialties.items(), key=lambda x: x[1]['correct']/max(x[1]['total'], 1), reverse=True):
            acc = stats['correct'] / max(stats['total'], 1) * 100
            print(f"   {spec}: {acc:.1f}% ({stats['correct']}/{stats['total']})")
    
    def print_status(self):
        """Print status of all predictions."""
        predictions = self.get_all_predictions()
        
        print("\n" + "=" * 80)
        print("📋 PREDICTION STATUS")
        print("=" * 80)
        
        status_counts = {'CORRECT': 0, 'INCORRECT': 0, 'PENDING': 0}
        
        for pred in predictions:
            file_id = pred.get('file_id', 'unknown')
            question = pred.get('question', 'No question')[:50]
            consensus = pred.get('consensus', {}).get('direction', 'NEUTRAL')
            resolved = pred.get('resolved', {})
            outcome = resolved.get('outcome', 'PENDING')
            
            status_counts[outcome] = status_counts.get(outcome, 0) + 1
            
            icon = "✅" if outcome == 'CORRECT' else "❌" if outcome == 'INCORRECT' else "⏳"
            print(f"{icon} {file_id} | {consensus:8} | {outcome:10} | {question}...")
        
        print("=" * 80)
        print(f"\n📊 Summary: {status_counts['CORRECT']} correct, {status_counts['INCORRECT']} incorrect, {status_counts['PENDING']} pending")


def main():
    parser = argparse.ArgumentParser(description="Resolve Swimming Pauls predictions")
    parser.add_argument("--list", action="store_true", help="List all predictions with status")
    parser.add_argument("--id", type=str, help="Resolve specific prediction by ID")
    parser.add_argument("--auto", action="store_true", help="Auto-resolve all pending predictions")
    parser.add_argument("--leaderboard", action="store_true", help="Show Paul accuracy leaderboard")
    parser.add_argument("--results-dir", type=str, default="data/results", help="Results directory")
    
    args = parser.parse_args()
    
    resolver = PredictionResolver(args.results_dir)
    
    if args.leaderboard:
        resolver.print_leaderboard()
    elif args.list:
        resolver.print_status()
    elif args.id:
        predictions = resolver.get_all_predictions()
        target = next((p for p in predictions if p.get('file_id') == args.id), None)
        if target:
            resolver.resolve_prediction(target, auto=True)
        else:
            print(f"❌ Prediction {args.id} not found")
    elif args.auto:
        predictions = resolver.get_all_predictions()
        print(f"🔍 Checking {len(predictions)} predictions...")
        
        pending = [p for p in predictions if p.get('resolved', {}).get('outcome', 'PENDING') == 'PENDING']
        print(f"   {len(pending)} pending resolutions")
        
        for pred in pending:
            resolver.resolve_prediction(pred, auto=True)
        
        resolver._save_resolved_cache()
        print("\n✅ Auto-resolution complete")
    else:
        # Default: show status
        resolver.print_status()


if __name__ == "__main__":
    main()
