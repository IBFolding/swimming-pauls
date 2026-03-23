#!/usr/bin/env python3
"""
Swimming Pauls - Leaderboard Viewer
Display Paul accuracy rankings and statistics.

Usage:
    python leaderboard.py              # Show full leaderboard
    python leaderboard.py --top 10     # Show top 10
    python leaderboard.py --specialty  # Group by specialty
    python leaderboard.py --paul "Visionary Paul"  # Show specific Paul
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from resolve_predictions import PredictionResolver

def main():
    parser = argparse.ArgumentParser(description="View Paul accuracy leaderboard")
    parser.add_argument("--top", type=int, default=20, help="Show top N Pauls")
    parser.add_argument("--specialty", action="store_true", help="Group by specialty")
    parser.add_argument("--paul", type=str, help="Show specific Paul")
    parser.add_argument("--results-dir", type=str, default="data/results", help="Results directory")
    
    args = parser.parse_args()
    
    resolver = PredictionResolver(args.results_dir)
    
    if args.paul:
        # Show specific Paul
        predictions = resolver.get_all_predictions()
        paul_predictions = []
        
        for pred in predictions:
            for agent in pred.get('agents', []):
                if agent.get('name') == args.paul:
                    paul_predictions.append({
                        'question': pred.get('question', 'No question')[:60],
                        'consensus': pred.get('consensus', {}).get('direction', 'NEUTRAL'),
                        'resolved': pred.get('resolved', {}).get('outcome', 'PENDING'),
                        'reasoning': agent.get('reasoning', 'No reasoning')[:100]
                    })
        
        print(f"\n🦷 {args.paul}")
        print("=" * 70)
        print(f"Total predictions: {len(paul_predictions)}")
        
        correct = sum(1 for p in paul_predictions if p['resolved'] == 'CORRECT')
        incorrect = sum(1 for p in paul_predictions if p['resolved'] == 'INCORRECT')
        
        if correct + incorrect > 0:
            accuracy = correct / (correct + incorrect) * 100
            print(f"Accuracy: {accuracy:.1f}% ({correct}/{correct + incorrect})")
        
        print("\n📜 Recent Predictions:")
        for pred in paul_predictions[:10]:
            icon = "✅" if pred['resolved'] == 'CORRECT' else "❌" if pred['resolved'] == 'INCORRECT' else "⏳"
            print(f"\n{icon} {pred['question']}...")
            print(f"   Consensus: {pred['consensus']} | Outcome: {pred['resolved']}")
            print(f"   💭 {pred['reasoning']}...")
    
    elif args.specialty:
        # Group by specialty
        leaderboard = resolver.generate_leaderboard()
        
        from collections import defaultdict
        by_specialty = defaultdict(list)
        
        for paul in leaderboard:
            by_specialty[paul['specialty']].append(paul)
        
        print("\n" + "=" * 70)
        print("🏆 LEADERBOARD BY SPECIALTY")
        print("=" * 70)
        
        for specialty, pauls in sorted(by_specialty.items()):
            total = sum(p['total'] for p in pauls)
            correct = sum(p['correct'] for p in pauls)
            accuracy = correct / total * 100 if total > 0 else 0
            
            print(f"\n📊 {specialty} ({len(pauls)} Pauls)")
            print(f"   Overall: {accuracy:.1f}% ({correct}/{total})")
            print("-" * 50)
            
            for paul in sorted(pauls, key=lambda x: x['accuracy'], reverse=True)[:5]:
                acc = f"{paul['accuracy']*100:.0f}%"
                print(f"   • {paul['name']:<20} {paul['correct']}/{paul['total']:<3} {acc:>6}")
    
    else:
        # Full leaderboard
        leaderboard = resolver.generate_leaderboard()
        
        print("\n" + "=" * 70)
        print("🏆 PAUL ACCURACY LEADERBOARD")
        print("=" * 70)
        
        if not leaderboard:
            print("\n📭 No resolved predictions yet.")
            print("   Run: python resolve_predictions.py --auto")
            return
        
        print(f"{'Rank':<6} {'Name':<22} {'Specialty':<15} {'Correct':<8} {'Total':<6} {'Accuracy':<10}")
        print("-" * 70)
        
        for i, paul in enumerate(leaderboard[:args.top], 1):
            rank = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i:>3}"
            accuracy_str = f"{paul['accuracy']*100:.0f}%"
            name = paul['name'][:20] if len(paul['name']) <= 20 else paul['name'][:18] + ".."
            spec = paul['specialty'][:15] if len(paul['specialty']) <= 15 else paul['specialty'][:13] + ".."
            
            print(f"{rank:<6} {name:<22} {spec:<15} {paul['correct']:<8} {paul['total']:<6} {accuracy_str:<10}")
        
        print("=" * 70)
        print(f"\n📊 Total Pauls tracked: {len(leaderboard)}")
        
        # Summary stats
        total_predictions = sum(p['total'] for p in leaderboard)
        total_correct = sum(p['correct'] for p in leaderboard)
        overall_acc = total_correct / total_predictions * 100 if total_predictions > 0 else 0
        
        print(f"📈 Overall accuracy: {overall_acc:.1f}% ({total_correct}/{total_predictions})")

if __name__ == "__main__":
    main()
