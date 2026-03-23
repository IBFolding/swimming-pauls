#!/usr/bin/env python3
"""
Swimming Pauls - Data Export
Export predictions, Paul performance, and configuration

Usage:
    python export_data.py                    # Export everything
    python export_data.py --predictions      # Export predictions only
    python export_data.py --leaderboard      # Export leaderboard
    python export_data.py --format csv       # CSV format
"""

import json
import csv
import argparse
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

from resolve_predictions import PredictionResolver

def export_predictions(format='json', output=None):
    """Export all predictions."""
    resolver = PredictionResolver()
    predictions = resolver.get_all_predictions()
    
    if not predictions:
        print("ℹ️  No predictions to export")
        return
    
    if format == 'json':
        output_file = output or f"predictions_export_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(predictions, f, indent=2, default=str)
        print(f"✅ Exported {len(predictions)} predictions to {output_file}")
    
    elif format == 'csv':
        output_file = output or f"predictions_export_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Question', 'Consensus', 'Confidence', 'Pauls', 'Rounds', 'Outcome', 'Resolved'])
            
            for pred in predictions:
                resolved = pred.get('resolved', {})
                writer.writerow([
                    pred.get('file_id', ''),
                    pred.get('question', '')[:100],
                    pred.get('consensus', {}).get('direction', ''),
                    pred.get('consensus', {}).get('confidence', ''),
                    pred.get('pauls_count', ''),
                    pred.get('rounds', ''),
                    resolved.get('outcome', 'PENDING'),
                    'Yes' if resolved.get('outcome') else 'No'
                ])
        
        print(f"✅ Exported {len(predictions)} predictions to {output_file}")

def export_leaderboard(format='json', output=None):
    """Export Paul leaderboard."""
    resolver = PredictionResolver()
    leaderboard = resolver.generate_leaderboard()
    
    if not leaderboard:
        print("ℹ️  No leaderboard data to export")
        return
    
    if format == 'json':
        output_file = output or f"leaderboard_export_{datetime.now().strftime('%Y%m%d')}.json"
        with open(output_file, 'w') as f:
            json.dump(leaderboard, f, indent=2)
        print(f"✅ Exported {len(leaderboard)} Pauls to {output_file}")
    
    elif format == 'csv':
        output_file = output or f"leaderboard_export_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Rank', 'Name', 'Specialty', 'Correct', 'Total', 'Accuracy'])
            
            for i, paul in enumerate(leaderboard, 1):
                writer.writerow([
                    i,
                    paul['name'],
                    paul['specialty'],
                    paul['correct'],
                    paul['total'],
                    f"{paul['accuracy']*100:.1f}%"
                ])
        
        print(f"✅ Exported {len(leaderboard)} Pauls to {output_file}")

def export_all():
    """Export everything."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    export_dir = Path(f"export_{timestamp}")
    export_dir.mkdir(exist_ok=True)
    
    print(f"📦 Exporting all data to {export_dir}/")
    
    export_predictions('json', export_dir / 'predictions.json')
    export_predictions('csv', export_dir / 'predictions.csv')
    export_leaderboard('json', export_dir / 'leaderboard.json')
    export_leaderboard('csv', export_dir / 'leaderboard.csv')
    
    # Copy config
    config = Path('config.yaml')
    if config.exists():
        import shutil
        shutil.copy(config, export_dir / 'config.yaml')
        print(f"✅ Copied config.yaml")
    
    print(f"\n✅ Export complete: {export_dir}/")

def main():
    parser = argparse.ArgumentParser(description="Export Swimming Pauls data")
    parser.add_argument("--predictions", action="store_true", help="Export predictions")
    parser.add_argument("--leaderboard", action="store_true", help="Export leaderboard")
    parser.add_argument("--all", action="store_true", help="Export everything")
    parser.add_argument("--format", choices=['json', 'csv'], default='json', help="Export format")
    parser.add_argument("--output", type=str, help="Output file")
    
    args = parser.parse_args()
    
    if args.all:
        export_all()
    elif args.predictions:
        export_predictions(args.format, args.output)
    elif args.leaderboard:
        export_leaderboard(args.format, args.output)
    else:
        # Default: export all
        export_all()

if __name__ == "__main__":
    main()
