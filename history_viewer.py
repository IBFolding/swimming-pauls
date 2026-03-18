#!/usr/bin/env python3
"""
Swimming Pauls History Viewer
View prediction history and Paul leaderboards from the terminal.
"""

import sys
import argparse
from datetime import datetime
from prediction_history import PredictionHistoryDB


def format_confidence(conf):
    """Format confidence as percentage with color indicator."""
    pct = conf * 100
    if pct >= 70:
        return f"\033[92m{pct:.0f}%\033[0m"  # Green
    elif pct >= 50:
        return f"\033[93m{pct:.0f}%\033[0m"  # Yellow
    else:
        return f"\033[91m{pct:.0f}%\033[0m"  # Red


def format_direction(direction):
    """Format direction with color."""
    if direction == 'BULLISH':
        return "\033[92m▲ BULLISH\033[0m"
    elif direction == 'BEARISH':
        return "\033[91m▼ BEARISH\033[0m"
    else:
        return "\033[93m◆ NEUTRAL\033[0m"


def format_outcome(outcome):
    """Format outcome with color."""
    if outcome == 'CORRECT':
        return "\033[92m✓ CORRECT\033[0m"
    elif outcome == 'INCORRECT':
        return "\033[91m✗ INCORRECT\033[0m"
    else:
        return "\033[90m○ PENDING\033[0m"


def show_leaderboard(db, limit=20):
    """Display Paul leaderboard."""
    print("\n" + "="*70)
    print("🏆 PAUL PERFORMANCE LEADERBOARD")
    print("="*70)
    
    leaderboard = db.get_leaderboard(limit=limit)
    
    if not leaderboard:
        print("\nNo Pauls with enough predictions yet (minimum 5).")
        return
    
    print(f"\n{'Rank':<6} {'Paul Name':<25} {'Accuracy':<12} {'Preds':<8} {'Streak':<10}")
    print("-"*70)
    
    for i, paul in enumerate(leaderboard, 1):
        rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        accuracy_str = f"{paul.accuracy_rate:.1%}"
        streak_str = f"{paul.current_streak} (best: {paul.best_streak})"
        
        print(f"{rank_emoji:<6} {paul.paul_name:<25} {accuracy_str:<12} {paul.total_predictions:<8} {streak_str:<10}")
    
    print("-"*70)
    print(f"\n💡 Tip: Use 'python history_viewer.py paul \"Paul Name\"' to see individual history")


def show_recent_predictions(db, limit=10, outcome=None):
    """Display recent predictions."""
    print("\n" + "="*80)
    if outcome:
        print(f"📊 RECENT PREDICTIONS - {outcome}")
    else:
        print("📊 RECENT PREDICTIONS")
    print("="*80)
    
    predictions = db.get_recent_predictions(limit=limit, outcome_filter=outcome)
    
    if not predictions:
        print("\nNo predictions recorded yet.")
        return
    
    print(f"\n{'ID':<14} {'Date':<12} {'Question':<30} {'Consensus':<12} {'Outcome':<12}")
    print("-"*80)
    
    for pred in predictions:
        date_str = pred.timestamp.strftime("%m/%d")
        question_short = pred.question[:28] + "..." if len(pred.question) > 30 else pred.question
        consensus_str = format_direction(pred.consensus_direction)
        outcome_str = format_outcome(pred.outcome)
        
        print(f"{pred.id:<14} {date_str:<12} {question_short:<30} {consensus_str:<20} {outcome_str:<12}")
    
    print("-"*80)
    print(f"\n💡 Tip: Use 'python history_viewer.py resolve \u003cid\gt; CORRECT' to mark outcomes")


def show_paul_history(db, paul_name, limit=20):
    """Display history for a specific Paul."""
    print(f"\n" + "="*80)
    print(f"📈 {paul_name.upper()} HISTORY")
    print("="*80)
    
    history = db.get_paul_history(paul_name, limit=limit)
    
    if not history:
        print(f"\nNo history found for {paul_name}")
        return
    
    # Get stats
    total = len(history)
    correct = sum(1 for h in history if h['was_correct'])
    accuracy = correct / total if total > 0 else 0
    
    print(f"\nStats: {accuracy:.1%} accuracy ({correct}/{total} correct)")
    print()
    
    print(f"{'Date':<12} {'Question':<35} {'Vote':<12} {'Result':<12}")
    print("-"*80)
    
    for h in history:
        date_str = datetime.fromisoformat(h['timestamp']).strftime("%m/%d")
        question_short = h['question'][:33] + "..." if len(h['question']) > 35 else h['question']
        vote_str = format_direction(h['paul_vote'])
        
        if h['was_correct'] is None:
            result_str = "⏳ PENDING"
        elif h['was_correct']:
            result_str = "\033[92m✓ RIGHT\033[0m"
        else:
            result_str = "\033[91m✗ WRONG\033[0m"
        
        print(f"{date_str:<12} {question_short:<35} {vote_str:<20} {result_str:<12}")
    
    print("-"*80)


def show_stats(db):
    """Display overall statistics."""
    print("\n" + "="*60)
    print("📊 OVERALL STATISTICS")
    print("="*60)
    
    stats = db.get_stats_summary()
    
    print(f"\nTotal Predictions: {stats.get('total_predictions', 0)}")
    print(f"Unique Pauls: {stats.get('unique_pauls', 0)}")
    print(f"Avg Consensus Confidence: {stats.get('avg_consensus_confidence', 0):.1%}")
    print(f"Predictions This Week: {stats.get('predictions_this_week', 0)}")
    
    print("\nBy Outcome:")
    by_outcome = stats.get('by_outcome', {})
    for outcome, count in by_outcome.items():
        outcome_str = format_outcome(outcome)
        print(f"  {outcome_str}: {count}")
    
    print("-"*60)


def resolve_prediction(db, prediction_id, outcome, notes=None):
    """Mark a prediction as resolved."""
    if outcome.upper() not in ('CORRECT', 'INCORRECT', 'PENDING'):
        print("❌ Outcome must be: CORRECT, INCORRECT, or PENDING")
        return
    
    db.mark_outcome(prediction_id, outcome.upper(), notes)
    print(f"✅ Prediction {prediction_id} marked as {outcome.upper()}")


def main():
    parser = argparse.ArgumentParser(
        description='Swimming Pauls History Viewer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python history_viewer.py leaderboard        # Show top Pauls
  python history_viewer.py recent             # Show recent predictions
  python history_viewer.py recent --pending   # Show pending predictions
  python history_viewer.py paul "Visionary Paul"  # Show Paul's history
  python history_viewer.py stats              # Show overall stats
  python history_viewer.py resolve abc123 CORRECT  # Mark outcome
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Leaderboard command
    subparsers.add_parser('leaderboard', help='Show Paul performance leaderboard')
    
    # Recent command
    recent_parser = subparsers.add_parser('recent', help='Show recent predictions')
    recent_parser.add_argument('--limit', type=int, default=10, help='Number of predictions to show')
    recent_parser.add_argument('--outcome', choices=['CORRECT', 'INCORRECT', 'PENDING'], 
                               help='Filter by outcome')
    
    # Paul command
    paul_parser = subparsers.add_parser('paul', help='Show specific Paul history')
    paul_parser.add_argument('name', help='Paul name (use quotes for names with spaces)')
    paul_parser.add_argument('--limit', type=int, default=20, help='Number of records to show')
    
    # Stats command
    subparsers.add_parser('stats', help='Show overall statistics')
    
    # Resolve command
    resolve_parser = subparsers.add_parser('resolve', help='Mark prediction outcome')
    resolve_parser.add_argument('id', help='Prediction ID')
    resolve_parser.add_argument('outcome', choices=['CORRECT', 'INCORRECT', 'PENDING'],
                               help='Outcome to set')
    resolve_parser.add_argument('--notes', help='Optional notes about the outcome')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    db = PredictionHistoryDB()
    
    if args.command == 'leaderboard':
        show_leaderboard(db)
    elif args.command == 'recent':
        show_recent_predictions(db, limit=args.limit, outcome=args.outcome)
    elif args.command == 'paul':
        show_paul_history(db, args.name, limit=args.limit)
    elif args.command == 'stats':
        show_stats(db)
    elif args.command == 'resolve':
        resolve_prediction(db, args.id, args.outcome, args.notes)


if __name__ == "__main__":
    main()
