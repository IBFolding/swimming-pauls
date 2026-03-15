#!/usr/bin/env bash
# Swimming Pauls Skill Runner
# Usage: openclaw run swimming-pauls [--pauls N] [--rounds N] [--connect-only]

set -e

# Default values
PAULS=50
ROUNDS=100
CONNECT_ONLY=false
WORKSPACE="/Users/brain/.openclaw/workspace/swimming_pauls"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --pauls)
            PAULS="$2"
            shift 2
            ;;
        --rounds)
            ROUNDS="$2"
            shift 2
            ;;
        --connect-only)
            CONNECT_ONLY=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# Check if local agent is running
if pgrep -f "local_agent.py" > /dev/null; then
    echo "🦷 Swimming Pauls agent already running!"
    echo "   WebSocket: ws://localhost:8765"
    echo "   UI: http://localhost:3005"
    echo ""
    echo "To connect UI, click 'Connect Local' in the web interface."
    exit 0
fi

if [ "$CONNECT_ONLY" = true ]; then
    echo "❌ No local agent detected."
    echo "   Run without --connect-only to start the agent."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+."
    exit 1
fi

# Check if workspace exists
if [ ! -d "$WORKSPACE" ]; then
    echo "❌ Swimming Pauls not found at $WORKSPACE"
    echo "   Clone from: https://github.com/IBFolding/swimming-pauls"
    exit 1
fi

cd "$WORKSPACE"

# Check/install dependencies
if [ ! -f ".deps_installed" ]; then
    echo "📦 Installing dependencies..."
    pip install -q -r requirements.txt 2>/dev/null || pip install websockets aiohttp
    touch .deps_installed
fi

# Generate connection ID
CONN_ID=$(python3 -c "import uuid; print(str(uuid.uuid4())[:8])")

echo "🦷 Starting Swimming Pauls Local Agent..."
echo "   Pauls: $PAULS"
echo "   Rounds: $ROUNDS"
echo "   WebSocket: ws://localhost:8765"
echo "   Connection ID: $CONN_ID"
echo ""
echo "1. Agent is starting..."
echo "2. Open http://localhost:3005 in your browser"
echo "3. Click 'Connect Local' and enter: $CONN_ID"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start the agent
export PAULS_COUNT=$PAULS
export ROUNDS_COUNT=$ROUNDS
export CONN_ID=$CONN_ID

python3 local_agent.py --ws-port 8765 --ui-port 3005
