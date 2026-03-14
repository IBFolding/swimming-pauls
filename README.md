# Swimming Pauls - Local Agent Connector

A WebSocket server that connects local pool simulations to the Vercel UI.

## Features

- 🔗 **WebSocket Server** - Real-time bidirectional communication
- 📱 **QR Code Pairing** - Easy mobile/desktop connection setup
- 🎣 **Pool Simulation** - Virtual fishing with customizable parameters
- 📊 **Real-time Streaming** - Live simulation progress updates
- 🔐 **Connection ID Auth** - Secure pairing system

## Installation

```bash
cd swimming_pauls
pip install -r requirements.txt
```

## Usage

### Start the Local Agent

```bash
python local_agent.py
```

Optional arguments:
```bash
python local_agent.py --host 0.0.0.0 --port 9000
```

### Pairing Flow

1. **Start the server** - A QR code and Connection ID will be displayed
2. **Open Vercel UI** - Navigate to the Swimming Pauls web interface
3. **Scan QR code** or manually enter the Connection ID
4. **Connection established** - Ready to trigger simulations

### Commands

| Command | Description |
|---------|-------------|
| `cast_pool` | Run pool simulation with parameters |
| `get_status` | Get current agent status |
| `get_results` | Get all simulation results |
| `ping` | Health check |

## WebSocket Protocol

### Authentication

```json
{
  "type": "auth",
  "payload": {
    "connection_id": "abc12345"
  }
}
```

### Cast Pool Command

```json
{
  "type": "command",
  "payload": {
    "command": "cast_pool",
    "params": {
      "fish_type": "carp",
      "bait": "corn",
      "water_temp": 22.5,
      "weather": "cloudy",
      "duration": 60
    }
  }
}
```

### Get Status

```json
{
  "type": "command",
  "payload": {
    "command": "get_status"
  }
}
```

### Message Types

**Client → Server:**
- `auth` - Authenticate with connection ID
- `command` - Execute a command
- `ping` - Health check

**Server → Client:**
- `auth_success` - Authentication successful
- `auth_failed` - Authentication failed
- `status` - Agent status response
- `results` - Simulation results
- `stream` - Real-time simulation updates
- `pong` - Ping response
- `error` - Error message
- `info` - Informational message

## Development

### Test Client

Use the included test client to verify the connection:

```bash
python test_client.py
```

### Simulation Parameters

- **fish_type**: carp, bass, trout, catfish, bluegill
- **bait**: worm, corn, lure, bread, shrimp
- **water_temp**: Temperature in Celsius (optimal around 20-25°C)
- **weather**: sunny, cloudy, rainy, overcast
- **duration**: Simulation duration in seconds (default: 60)

## Architecture

```
┌─────────────────┐     WebSocket      ┌──────────────────┐
│  Vercel UI      │ ◄────────────────► │  Local Agent     │
│  (Browser)      │    ws://localhost  │  (Python Server) │
└─────────────────┘        :8765       └──────────────────┘
                                                  │
                                                  ▼
                                          ┌──────────────────┐
                                          │  Pool Simulator  │
                                          └──────────────────┘
```

## License

MIT
