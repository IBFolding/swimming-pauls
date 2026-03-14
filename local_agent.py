#!/usr/bin/env python3
"""
Swimming Pauls - Local Agent Connector (Phase 8)
WebSocket server for local simulation control and Vercel UI pairing.

Usage:
    python local_agent.py

Features:
    - WebSocket server on ws://localhost:8765
    - QR code pairing system
    - Real-time simulation streaming
    - Command interface for pool simulation
"""

import asyncio
import json
import uuid
import argparse
import qrcode
from io import StringIO
from datetime import datetime
from typing import Dict, Optional, Set, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum

import websockets
from websockets.server import WebSocketServerProtocol


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8765


# ============================================================================
# Enums and Data Classes
# ============================================================================

class AgentStatus(Enum):
    IDLE = "idle"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RUNNING = "running"
    ERROR = "error"


class SimulationState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class SimulationResult:
    """Result from a pool simulation run."""
    timestamp: str
    fish_type: str
    bait: str
    water_temp: float
    weather: str
    success: bool
    catches: int
    missed: int
    efficiency: float
    best_spot: str
    duration_seconds: float
    logs: list
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AgentState:
    """Current state of the local agent."""
    connection_id: str
    status: str
    simulation_state: str
    connected_clients: int
    last_activity: Optional[str]
    version: str = "1.0.0"
    
    def to_dict(self) -> dict:
        return {
            "connection_id": self.connection_id,
            "status": self.status,
            "simulation_state": self.simulation_state,
            "connected_clients": self.connected_clients,
            "last_activity": self.last_activity,
            "version": self.version
        }


# ============================================================================
# Message Protocol
# ============================================================================

class MessageType(Enum):
    # Client -> Server
    AUTH = "auth"
    COMMAND = "command"
    PING = "ping"
    
    # Server -> Client
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILED = "auth_failed"
    STATUS = "status"
    RESULTS = "results"
    STREAM = "stream"
    PONG = "pong"
    ERROR = "error"
    INFO = "info"


def create_message(msg_type: MessageType, payload: dict = None, error: str = None) -> dict:
    """Create a standardized message."""
    msg = {
        "type": msg_type.value,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if payload is not None:
        msg["payload"] = payload
    if error is not None:
        msg["error"] = error
    return msg


# ============================================================================
# Pool Simulation Engine
# ============================================================================

class PoolSimulator:
    """Simulates pool fishing scenarios for Pauls."""
    
    def __init__(self):
        self.state = SimulationState.IDLE
        self.current_params: Optional[dict] = None
        self.results: list[SimulationResult] = []
        self._cancelled = False
        
    async def run_simulation(
        self,
        fish_type: str,
        bait: str,
        water_temp: float,
        weather: str,
        duration: int = 60,
        on_progress: Callable[[dict], None] = None
    ) -> SimulationResult:
        """
        Run a pool fishing simulation.
        
        Args:
            fish_type: Type of fish to simulate (carp, bass, trout, etc.)
            bait: Bait type (worm, corn, lure, etc.)
            water_temp: Water temperature in Celsius
            weather: Weather condition (sunny, cloudy, rainy, etc.)
            duration: Simulation duration in seconds (default: 60)
            on_progress: Callback for streaming updates
        """
        self.state = SimulationState.RUNNING
        self._cancelled = False
        self.current_params = {
            "fish_type": fish_type,
            "bait": bait,
            "water_temp": water_temp,
            "weather": weather,
            "duration": duration
        }
        
        start_time = datetime.utcnow()
        logs = []
        catches = 0
        missed = 0
        
        # Simulation logic with streaming updates
        steps = max(10, duration)  # At least 10 update steps
        step_duration = duration / steps
        
        for step in range(steps):
            if self._cancelled:
                self.state = SimulationState.IDLE
                raise asyncio.CancelledError("Simulation cancelled")
            
            # Simulate fishing activity
            progress = (step + 1) / steps
            
            # Random catch logic based on conditions
            catch_chance = self._calculate_catch_chance(fish_type, bait, water_temp, weather)
            
            import random
            if random.random() < catch_chance:
                catches += 1
                log_entry = f"🎣 Step {step+1}/{steps}: Caught a {fish_type}!"
            elif random.random() < catch_chance * 0.5:
                missed += 1
                log_entry = f"😅 Step {step+1}/{steps}: Fish got away..."
            else:
                log_entry = f"⏳ Step {step+1}/{steps}: Waiting for a bite..."
            
            logs.append(log_entry)
            
            # Send progress update
            if on_progress:
                await on_progress({
                    "step": step + 1,
                    "total_steps": steps,
                    "progress": progress,
                    "catches": catches,
                    "missed": missed,
                    "log": log_entry
                })
            
            await asyncio.sleep(step_duration)
        
        # Calculate results
        end_time = datetime.utcnow()
        duration_seconds = (end_time - start_time).total_seconds()
        
        efficiency = catches / (catches + missed) if (catches + missed) > 0 else 0
        best_spot = self._determine_best_spot(fish_type, water_temp)
        
        result = SimulationResult(
            timestamp=start_time.isoformat() + "Z",
            fish_type=fish_type,
            bait=bait,
            water_temp=water_temp,
            weather=weather,
            success=catches > 0,
            catches=catches,
            missed=missed,
            efficiency=round(efficiency, 2),
            best_spot=best_spot,
            duration_seconds=round(duration_seconds, 2),
            logs=logs
        )
        
        self.results.append(result)
        self.state = SimulationState.COMPLETED
        
        return result
    
    def _calculate_catch_chance(self, fish_type: str, bait: str, water_temp: float, weather: str) -> float:
        """Calculate probability of catching a fish based on conditions."""
        import random
        
        # Base probability
        chance = 0.15
        
        # Fish type modifiers
        fish_modifiers = {
            "carp": 0.05,
            "bass": 0.08,
            "trout": 0.03,
            "catfish": 0.06,
            "bluegill": 0.10
        }
        chance += fish_modifiers.get(fish_type.lower(), 0)
        
        # Bait modifiers
        bait_modifiers = {
            "worm": 0.05,
            "corn": 0.08,
            "lure": 0.03,
            "bread": 0.02,
            "shrimp": 0.06
        }
        chance += bait_modifiers.get(bait.lower(), 0)
        
        # Water temperature modifier (optimal around 20-25°C)
        temp_diff = abs(water_temp - 22.5)
        temp_modifier = max(0, 0.05 - (temp_diff * 0.002))
        chance += temp_modifier
        
        # Weather modifiers
        weather_modifiers = {
            "sunny": 0.02,
            "cloudy": 0.05,
            "rainy": 0.08,
            "overcast": 0.06
        }
        chance += weather_modifiers.get(weather.lower(), 0)
        
        # Add some randomness
        chance += random.uniform(-0.02, 0.02)
        
        return max(0.05, min(0.5, chance))  # Clamp between 5% and 50%
    
    def _determine_best_spot(self, fish_type: str, water_temp: float) -> str:
        """Determine the best fishing spot based on conditions."""
        spots = {
            "carp": "Shallow weed beds",
            "bass": "Near structure and drop-offs",
            "trout": "Cooler deep water with oxygen",
            "catfish": "Bottom near channels",
            "bluegill": "Near docks and vegetation"
        }
        return spots.get(fish_type.lower(), "General pool area")
    
    def cancel(self):
        """Cancel the current simulation."""
        self._cancelled = True
        
    def get_results(self) -> list[SimulationResult]:
        """Get all simulation results."""
        return self.results
    
    def clear_results(self):
        """Clear simulation history."""
        self.results = []


# ============================================================================
# Local Agent Server
# ============================================================================

class LocalAgentServer:
    """WebSocket server for local agent control."""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.connection_id = str(uuid.uuid4())[:8]  # Short unique ID
        
        self.state = AgentState(
            connection_id=self.connection_id,
            status=AgentStatus.IDLE.value,
            simulation_state=SimulationState.IDLE.value,
            connected_clients=0,
            last_activity=None
        )
        
        self.clients: Set[WebSocketServerProtocol] = set()
        self.authenticated_clients: Set[WebSocketServerProtocol] = set()
        self.simulator = PoolSimulator()
        self._running = False
        
    def print_qr_code(self):
        """Generate and display QR code for pairing."""
        # Create pairing data
        pairing_data = {
            "type": "swimming_pauls_pairing",
            "connection_id": self.connection_id,
            "host": self.host,
            "port": self.port,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        qr_data = json.dumps(pairing_data)
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=2,
            border=2
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Print to console
        print("\n" + "=" * 60)
        print("🎣 SWIMMING PAULS - LOCAL AGENT CONNECTOR")
        print("=" * 60)
        print(f"\n🔗 Connection ID: {self.connection_id}")
        print(f"🌐 WebSocket: ws://{self.host}:{self.port}")
        print("\n📱 Scan this QR code to pair with the Vercel UI:")
        print("-" * 40)
        
        # Output QR code as ASCII
        qr.print_ascii(invert=True)
        
        print("-" * 40)
        print("\n📝 Or manually enter this Connection ID in the UI:")
        print(f"   {self.connection_id}")
        print("\n⚡ Waiting for connections...")
        print("=" * 60 + "\n")
        
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new WebSocket client connection."""
        self.clients.add(websocket)
        self.state.connected_clients = len(self.clients)
        
        client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"🔌 New connection from {client_info}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Client disconnected: {client_info}")
        finally:
            self.clients.discard(websocket)
            self.authenticated_clients.discard(websocket)
            self.state.connected_clients = len(self.clients)
    
    async def process_message(self, websocket: WebSocketServerProtocol, message: str):
        """Process an incoming message."""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            payload = data.get("payload", {})
            
            self.state.last_activity = datetime.utcnow().isoformat() + "Z"
            
            # Handle authentication
            if msg_type == MessageType.AUTH.value:
                await self.handle_auth(websocket, payload)
                return
            
            # Require authentication for other commands
            if websocket not in self.authenticated_clients:
                await self.send_error(websocket, "Not authenticated. Send auth message first.")
                return
            
            # Handle commands
            if msg_type == MessageType.COMMAND.value:
                await self.handle_command(websocket, payload)
            elif msg_type == MessageType.PING.value:
                await self.handle_ping(websocket)
            else:
                await self.send_error(websocket, f"Unknown message type: {msg_type}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON format")
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            await self.send_error(websocket, f"Internal error: {str(e)}")
    
    async def handle_auth(self, websocket: WebSocketServerProtocol, payload: dict):
        """Handle client authentication."""
        client_connection_id = payload.get("connection_id")
        
        if client_connection_id == self.connection_id:
            self.authenticated_clients.add(websocket)
            self.state.status = AgentStatus.CONNECTED.value
            
            await websocket.send(json.dumps(create_message(
                MessageType.AUTH_SUCCESS,
                {"message": "Authentication successful", "agent_state": self.state.to_dict()}
            )))
            
            client_info = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
            print(f"✅ Client authenticated: {client_info}")
        else:
            await websocket.send(json.dumps(create_message(
                MessageType.AUTH_FAILED,
                error="Invalid connection ID"
            )))
            print(f"❌ Authentication failed: invalid connection ID")
    
    async def handle_command(self, websocket: WebSocketServerProtocol, payload: dict):
        """Handle a command from the client."""
        command = payload.get("command")
        params = payload.get("params", {})
        
        print(f"📥 Command received: {command}")
        
        if command == "cast_pool":
            await self.handle_cast_pool(websocket, params)
        elif command == "get_status":
            await self.handle_get_status(websocket)
        elif command == "get_results":
            await self.handle_get_results(websocket)
        elif command == "ping":
            await self.handle_ping(websocket)
        else:
            await self.send_error(websocket, f"Unknown command: {command}")
    
    async def handle_cast_pool(self, websocket: WebSocketServerProtocol, params: dict):
        """Run a pool simulation with the given parameters."""
        # Validate parameters
        required = ["fish_type", "bait", "water_temp", "weather"]
        missing = [f for f in required if f not in params]
        
        if missing:
            await self.send_error(websocket, f"Missing required parameters: {', '.join(missing)}")
            return
        
        # Send initial status
        self.state.status = AgentStatus.RUNNING.value
        self.state.simulation_state = SimulationState.RUNNING.value
        
        await websocket.send(json.dumps(create_message(
            MessageType.INFO,
            {"message": "Starting pool simulation...", "params": params}
        )))
        
        # Progress callback for streaming
        async def on_progress(update: dict):
            await websocket.send(json.dumps(create_message(
                MessageType.STREAM,
                update
            )))
        
        try:
            # Run simulation
            result = await self.simulator.run_simulation(
                fish_type=params["fish_type"],
                bait=params["bait"],
                water_temp=float(params["water_temp"]),
                weather=params["weather"],
                duration=int(params.get("duration", 60)),
                on_progress=on_progress
            )
            
            # Send final results
            await websocket.send(json.dumps(create_message(
                MessageType.RESULTS,
                {
                    "message": "Simulation completed successfully!",
                    "result": result.to_dict()
                }
            )))
            
            self.state.status = AgentStatus.CONNECTED.value
            self.state.simulation_state = SimulationState.COMPLETED.value
            
        except asyncio.CancelledError:
            await websocket.send(json.dumps(create_message(
                MessageType.INFO,
                {"message": "Simulation was cancelled"}
            )))
            self.state.status = AgentStatus.CONNECTED.value
            self.state.simulation_state = SimulationState.IDLE.value
        except Exception as e:
            self.state.status = AgentStatus.ERROR.value
            self.state.simulation_state = SimulationState.ERROR.value
            await self.send_error(websocket, f"Simulation failed: {str(e)}")
    
    async def handle_get_status(self, websocket: WebSocketServerProtocol):
        """Return the current agent status."""
        await websocket.send(json.dumps(create_message(
            MessageType.STATUS,
            self.state.to_dict()
        )))
    
    async def handle_get_results(self, websocket: WebSocketServerProtocol):
        """Return all simulation results."""
        results = [r.to_dict() for r in self.simulator.get_results()]
        await websocket.send(json.dumps(create_message(
            MessageType.RESULTS,
            {
                "count": len(results),
                "results": results
            }
        )))
    
    async def handle_ping(self, websocket: WebSocketServerProtocol):
        """Respond to ping with pong."""
        await websocket.send(json.dumps(create_message(
            MessageType.PONG,
            {"message": "pong", "connection_id": self.connection_id}
        )))
    
    async def send_error(self, websocket: WebSocketServerProtocol, error_message: str):
        """Send an error message to a client."""
        await websocket.send(json.dumps(create_message(
            MessageType.ERROR,
            error=error_message
        )))
    
    async def start(self):
        """Start the WebSocket server."""
        self._running = True
        self.state.status = AgentStatus.CONNECTING.value
        
        # Print QR code for pairing
        self.print_qr_code()
        
        # Start server
        async with websockets.serve(self.handle_client, self.host, self.port):
            self.state.status = AgentStatus.CONNECTED.value
            print(f"🚀 Server running at ws://{self.host}:{self.port}")
            print("Press Ctrl+C to stop\n")
            
            # Keep running until stopped
            while self._running:
                await asyncio.sleep(1)
    
    def stop(self):
        """Stop the server."""
        self._running = False
        print("\n🛑 Server stopping...")


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Swimming Pauls - Local Agent Connector",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python local_agent.py              # Start with default settings
    python local_agent.py --port 9000  # Use custom port
    python local_agent.py --host 0.0.0.0  # Accept connections from any interface
        """
    )
    
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Host to bind to (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Port to listen on (default: {DEFAULT_PORT})"
    )
    
    args = parser.parse_args()
    
    # Create and start server
    server = LocalAgentServer(host=args.host, port=args.port)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        server.stop()
        print("👋 Goodbye!")


if __name__ == "__main__":
    main()
