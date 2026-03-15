#!/usr/bin/env bash
# Auto-installer for Swimming Pauls
# This runs automatically when user types: openclaw run swimming-pauls

set -e

INSTALL_DIR="$HOME/swimming-pauls"
REPO_URL="https://github.com/IBFolding/swimming-pauls.git"

echo "🦷 Swimming Pauls - Auto Installer"
echo "=================================="

# Check if already installed
if [ -d "$INSTALL_DIR" ]; then
    echo "✅ Swimming Pauls already installed at $INSTALL_DIR"
    echo ""
    echo "Starting local agent..."
    cd "$INSTALL_DIR"
    
    # Check dependencies
    if ! python3 -c "import websockets, httpx" 2>/dev/null; then
        echo "📦 Installing dependencies..."
        pip3 install -q websockets httpx
    fi
    
    # Start the agent
    python3 local_agent.py &
    AGENT_PID=$!
    
    sleep 2
    
    echo ""
    echo "🚀 Swimming Pauls is running!"
    echo "   Web UI: http://localhost:3005"
    echo "   Click '🔌 Connect Local' and use connection ID from above"
    echo ""
    echo "Press Ctrl+C to stop"
    wait $AGENT_PID
    exit 0
fi

# Fresh install
echo "📥 Installing Swimming Pauls..."
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first:"
    echo "   brew install git  # macOS"
    echo "   apt-get install git  # Linux"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+:"
    echo "   brew install python3  # macOS"
    echo "   apt-get install python3  # Linux"
    exit 1
fi

echo "✅ Git and Python 3 found"
echo ""

# Clone repository
echo "📥 Cloning repository..."
git clone "$REPO_URL" "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -q websockets httpx aiohttp

# Make scripts executable
chmod +x run.sh local_agent.py

echo ""
echo "✅ Installation complete!"
echo ""
echo "🚀 Starting Swimming Pauls..."
echo ""

# Start the agent
python3 local_agent.py &
AGENT_PID=$!

sleep 3

echo ""
echo "🎉 Swimming Pauls is now running!"
echo ""
echo "📱 Open your browser to: http://localhost:3005"
echo "🔌 Click 'Connect Local' and paste the Connection ID shown above"
echo ""
echo "Press Ctrl+C to stop the agent"

wait $AGENT_PID
