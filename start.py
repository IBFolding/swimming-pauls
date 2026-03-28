#!/usr/bin/env python3
"""
Swimming Pauls - Unified Launcher
Starts both the WebSocket local agent and the web UI server.

Usage:
    python start.py                    # Start with defaults
    python start.py --pauls 100        # Set default Paul count
    python start.py --port 8766        # Custom WebSocket port
    python start.py --ui-port 3006     # Custom UI port
"""

import subprocess
import sys
import os
import time
import signal
import argparse
from pathlib import Path

# Configuration
DEFAULT_WS_PORT = 8765
DEFAULT_UI_PORT = 3005
WS_HOST = "localhost"

def print_banner():
    print("\n" + "=" * 60)
    print("🦷 SWIMMING PAULS - UNIFIED LAUNCHER")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import websockets
    except ImportError:
        print("❌ Missing dependency: websockets")
        print("   Run: pip install websockets")
        return False
    
    try:
        import psutil
    except ImportError:
        print("⚠️  Optional dependency missing: psutil")
        print("   Run: pip install psutil (for better system monitoring)")
    
    return True

def start_websocket_server(ws_port, pauls, rounds):
    """Start the WebSocket local agent."""
    print(f"🔌 Starting WebSocket server on ws://{WS_HOST}:{ws_port}")
    
    env = os.environ.copy()
    env["PAULS_DEFAULT_COUNT"] = str(pauls)
    env["PAULS_DEFAULT_ROUNDS"] = str(rounds)
    
    process = subprocess.Popen(
        [sys.executable, "local_agent.py", "--port", str(ws_port)],
        cwd=Path(__file__).parent,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Wait a moment and check if process started
    time.sleep(1)
    if process.poll() is not None:
        print("❌ WebSocket server failed to start")
        return None
    
    print(f"   ✅ WebSocket server running (PID: {process.pid})")
    return process

def start_ui_server(ui_port, ws_port):
    """Start the web UI server."""
    # Serve from project root so app.html and ui/ are both accessible
    project_dir = Path(__file__).parent
    
    print(f"🌐 Starting UI server on http://localhost:{ui_port}")
    
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(ui_port)],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait a moment and check if process started
    time.sleep(1)
    if process.poll() is not None:
        print("❌ UI server failed to start")
        return None
    
    print(f"   ✅ UI server running (PID: {process.pid})")
    return process

def print_instructions(ws_port, ui_port):
    """Print instructions for the user."""
    print()
    print("=" * 60)
    print("🚀 SWIMMING PAULS IS RUNNING!")
    print("=" * 60)
    print()
    print("📱 Access Points:")
    print(f"   App:        http://localhost:{ui_port}/app.html")
    print(f"   Landing:    http://localhost:{ui_port}/ui/index.html")
    print(f"   WebSocket:  ws://localhost:{ws_port}")
    print()
    print("📝 Quick Start:")
    print(f"   1. App should open in your browser automatically")
    print("   2. Type a question and Cast the Pool!")
    print("   3. View results in the Explorer tab")
    print()
    print("🛑 To Stop:")
    print("   Press Ctrl+C to stop both servers")
    print()
    print("=" * 60)
    print()

def monitor_processes(ws_process, ui_process):
    """Monitor both processes and restart if needed."""
    try:
        while True:
            # Check WebSocket server
            if ws_process.poll() is not None:
                print("\n⚠️  WebSocket server stopped unexpectedly")
                break
            
            # Check UI server
            if ui_process.poll() is not None:
                print("\n⚠️  UI server stopped unexpectedly")
                break
            
            # Print any output from WebSocket server
            try:
                line = ws_process.stdout.readline()
                if line:
                    print(f"[WS] {line.strip()}")
            except:
                pass
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        
        # Terminate both processes
        for proc, name in [(ws_process, "WebSocket"), (ui_process, "UI")]:
            if proc and proc.poll() is None:
                print(f"   Stopping {name} server...")
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except:
                    proc.kill()
        
        print("✅ All servers stopped")

def main():
    parser = argparse.ArgumentParser(
        description="Start Swimming Pauls local agent and UI server"
    )
    parser.add_argument(
        "--pauls", type=int, default=50,
        help="Default number of Pauls (default: 50)"
    )
    parser.add_argument(
        "--rounds", type=int, default=20,
        help="Default number of rounds (default: 20)"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_WS_PORT,
        help=f"WebSocket port (default: {DEFAULT_WS_PORT})"
    )
    parser.add_argument(
        "--ui-port", type=int, default=DEFAULT_UI_PORT,
        help=f"UI server port (default: {DEFAULT_UI_PORT})"
    )
    parser.add_argument(
        "--no-ui", action="store_true",
        help="Start only the WebSocket server (no UI)"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check if ports are already in use
    import socket
    for port, name in [(args.port, "WebSocket"), (args.ui_port, "UI")]:
        if not args.no_ui or name == "WebSocket":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result == 0:
                print(f"❌ Port {port} is already in use ({name})")
                print(f"   Try: python start.py --port {port+1} --ui-port {args.ui_port+1}")
                sys.exit(1)
    
    # Start WebSocket server
    ws_process = start_websocket_server(args.port, args.pauls, args.rounds)
    if not ws_process:
        sys.exit(1)
    
    # Start UI server (unless --no-ui)
    ui_process = None
    if not args.no_ui:
        ui_process = start_ui_server(args.ui_port, args.port)
        if not ui_process:
            ws_process.terminate()
            sys.exit(1)
    
    # Print instructions
    print_instructions(args.port, args.ui_port)
    
    # Auto-open browser
    if not args.no_ui:
        import webbrowser
        url = f"http://localhost:{args.ui_port}/app.html"
        print(f"🌐 Opening {url} ...")
        webbrowser.open(url)
    
    # Monitor processes
    monitor_processes(ws_process, ui_process)

if __name__ == "__main__":
    main()
