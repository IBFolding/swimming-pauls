# OpenClaw Skill: Swimming Pauls

## What is this?

This is an **OpenClaw skill** that lets you run Swimming Pauls directly from the OpenClaw CLI.

## Installation

### Option 1: Copy to your OpenClaw skills folder

```bash
# Clone the repo
git clone https://github.com/IBFolding/swimming-pauls.git

# Copy the skill to your OpenClaw skills folder
cp -r swimming-pauls/skills/openclaw/* ~/.openclaw/workspace/skills/swimming-pauls/

# Or if you want the full project
cp -r swimming-pauls ~/.openclaw/workspace/skills/
```

### Option 2: Manual download

1. Download the `swimming-pauls` folder from GitHub
2. Place it in: `~/.openclaw/workspace/skills/swimming-pauls/`
3. Done!

## Usage

Once installed, you can run:

```bash
openclaw run swimming-pauls
```

Or with options:
```bash
openclaw run swimming-pauls --pauls 100 --rounds 50
```

## What it does

1. Starts the local agent WebSocket server
2. Opens the UI in your browser
3. Connects automatically
4. Ready to cast the pool!

## Requirements

- Python 3.9+
- OpenClaw CLI installed
- `websockets` Python package (`pip install websockets`)

## File Structure

```
~/.openclaw/workspace/skills/swimming-pauls/
├── SKILL.md          # Skill definition
├── run.sh            # Main runner script
├── local_agent.py    # WebSocket agent
├── ui/               # Web UI files
│   └── index.html
└── README.md
```

## Troubleshooting

**"Skill not found"**
- Make sure the folder is named exactly `swimming-pauls`
- Check it's in `~/.openclaw/workspace/skills/`

**"Python not found"**
- Install Python 3.9+ and make sure `python3` is in your PATH

**"Port already in use"**
- Kill any existing local_agent.py processes: `pkill -f local_agent.py`
- Then try again
