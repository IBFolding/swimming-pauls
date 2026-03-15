#!/bin/bash
# Install Swimming Pauls OpenClaw Skill
# Usage: curl -sSL https://raw.githubusercontent.com/IBFolding/swimming-pauls/main/install-skill.sh | bash

echo "🦷 Installing Swimming Pauls OpenClaw Skill..."

# Check if OpenClaw is installed
if [ ! -d "$HOME/.openclaw" ]; then
    echo "❌ OpenClaw not found. Please install OpenClaw first."
    echo "   Visit: https://docs.openclaw.ai/installation"
    exit 1
fi

# Create skills directory if it doesn't exist
SKILL_DIR="$HOME/.openclaw/workspace/skills/swimming-pauls"
mkdir -p "$SKILL_DIR"

# Download skill files
echo "📥 Downloading skill files..."
curl -sSL https://raw.githubusercontent.com/IBFolding/swimming-pauls/main/openclaw-skill/SKILL.md -o "$SKILL_DIR/SKILL.md"
curl -sSL https://raw.githubusercontent.com/IBFolding/swimming-pauls/main/openclaw-skill/run.sh -o "$SKILL_DIR/run.sh"
chmod +x "$SKILL_DIR/run.sh"

# Clone the main project if not exists
PROJECT_DIR="$HOME/swimming-pauls"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "📥 Cloning Swimming Pauls project..."
    git clone https://github.com/IBFolding/swimming-pauls.git "$PROJECT_DIR"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Usage:"
echo "  openclaw run swimming-pauls"
echo ""
echo "Or with custom settings:"
echo "  openclaw run swimming-pauls --pauls 100 --rounds 50"
