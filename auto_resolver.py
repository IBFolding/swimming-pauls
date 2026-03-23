#!/usr/bin/env python3
"""
Swimming Pauls - Auto Resolver Scheduler
Runs periodically to check and resolve predictions.

Usage:
    python auto_resolver.py                    # Run once
    python auto_resolver.py --daemon           # Run as daemon (every hour)
    python auto_resolver.py --interval 3600    # Custom interval (seconds)
"""

import argparse
import time
import sys
from pathlib import Path
from datetime import datetime
import subprocess

sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

def run_resolver():
    """Run the prediction resolver."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running auto-resolver...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'resolve_predictions.py', '--auto'],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"⚠️  Errors: {result.stderr}")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Resolver timed out")
        return False
    except Exception as e:
        print(f"❌ Error running resolver: {e}")
        return False

def run_leaderboard_update():
    """Update and save leaderboard."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updating leaderboard...")
    
    try:
        result = subprocess.run(
            [sys.executable, 'resolve_predictions.py', '--leaderboard'],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Save leaderboard to file
        leaderboard_file = Path(__file__).parent / 'data' / 'leaderboard.txt'
        leaderboard_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(leaderboard_file, 'w') as f:
            f.write(result.stdout)
        
        print(f"   ✅ Leaderboard saved to {leaderboard_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating leaderboard: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Auto-resolve predictions")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--interval", type=int, default=3600, help="Interval in seconds (default: 3600 = 1 hour)")
    parser.add_argument("--leaderboard", action="store_true", help="Update leaderboard only")
    
    args = parser.parse_args()
    
    if args.leaderboard:
        run_leaderboard_update()
        return
    
    if args.daemon:
        print(f"🤖 Auto-resolver daemon started")
        print(f"   Interval: {args.interval} seconds ({args.interval/60:.1f} minutes)")
        print(f"   Press Ctrl+C to stop\n")
        
        try:
            while True:
                run_resolver()
                run_leaderboard_update()
                
                print(f"\n⏳ Sleeping for {args.interval} seconds...")
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Daemon stopped")
    else:
        # Run once
        run_resolver()
        run_leaderboard_update()

if __name__ == "__main__":
    main()
