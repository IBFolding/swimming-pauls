#!/usr/bin/env python3
"""
Swimming Pauls - Local Agent Connector
WebSocket server connecting UI to local multi-agent simulations.
"""

import asyncio
import json
import uuid
import argparse
import os
import sys
import psutil
from datetime import datetime
from typing import Dict, Set, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    print("❌ Missing websockets. Run: pip install websockets")
    sys.exit(1)

# Import Swimming Pauls simulation
try:
    from simulation import quick_simulate
    from agent import Agent, PersonaType
    from skill_bridge import get_skill_bridge
    SIMULATION_AVAILABLE = True
except ImportError:
    SIMULATION_AVAILABLE = False
    print("⚠️  Swimming Pauls simulation not found. Running in demo mode.")


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8765


def get_system_limits():
    """Check system resources and return recommended max Pauls"""
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    
    # Rough estimate: ~50MB per Paul with LLM context
    max_pauls = int(available_gb / 0.05)
    
    # Cap at reasonable limits
    if max_pauls > 10000:
        max_pauls = 10000
    elif max_pauls < 10:
        max_pauls = 10
    
    return {
        "max_pauls": max_pauls,
        "recommended": min(100, max_pauls),
        "available_gb": round(available_gb, 1),
        "total_gb": round(memory.total / (1024**3), 1)
    }


class MessageType(Enum):
    AUTH = "auth"
    COMMAND = "command"
    PING = "ping"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILED = "auth_failed"
    STATUS = "status"
    RESULTS = "results"
    STREAM = "stream"
    PONG = "pong"
    ERROR = "error"
    INFO = "info"


@dataclass
class AgentState:
    connection_id: str
    status: str
    connected_clients: int
    last_activity: Optional[str]
    version: str = "1.0.0"
    
    def to_dict(self):
        return asdict(self)


def create_message(msg_type: MessageType, payload: dict = None, error: str = None):
    msg = {
        "type": msg_type.value,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if payload:
        msg["payload"] = payload
    if error:
        msg["error"] = error
    return msg


class LocalAgentServer:
    """WebSocket server for local agent control."""
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self.host = host
        self.port = port
        self.connection_id = str(uuid.uuid4())[:8]
        
        self.state = AgentState(
            connection_id=self.connection_id,
            status="idle",
            connected_clients=0,
            last_activity=None
        )
        
        self.clients: Set[WebSocketServerProtocol] = set()
        self.authenticated_clients: Set[WebSocketServerProtocol] = set()
        self._running = False
        
    def print_startup(self):
        print("\n" + "=" * 60)
        print("🦷 SWIMMING PAULS - LOCAL AGENT")
        print("=" * 60)
        print(f"\n🔗 Connection ID: {self.connection_id}")
        print(f"🌐 WebSocket: ws://{self.host}:{self.port}")
        print("\n📝 To connect:")
        print("   1. Open http://localhost:3005")
        print("   2. Click 'Connect Local'")
        print(f"   3. Enter: {self.connection_id}")
        print("\n⚡ Waiting for connections...")
        print("=" * 60 + "\n")
        
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        self.clients.add(websocket)
        self.state.connected_clients = len(self.clients)
        
        client = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"🔌 New connection: {client}")
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 Disconnected: {client}")
        finally:
            self.clients.discard(websocket)
            self.authenticated_clients.discard(websocket)
            self.state.connected_clients = len(self.clients)
    
    async def process_message(self, websocket, message: str):
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            payload = data.get("payload", {})
            
            self.state.last_activity = datetime.utcnow().isoformat() + "Z"
            
            if msg_type == MessageType.AUTH.value:
                await self.handle_auth(websocket, payload)
                return
            
            if websocket not in self.authenticated_clients:
                await self.send_error(websocket, "Not authenticated")
                return
            
            if msg_type == MessageType.COMMAND.value:
                await self.handle_command(websocket, payload)
            elif msg_type == MessageType.PING.value:
                await self.handle_ping(websocket)
            else:
                await self.send_error(websocket, f"Unknown type: {msg_type}")
                
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON")
        except Exception as e:
            print(f"❌ Error: {e}")
            await self.send_error(websocket, str(e))
    
    async def handle_auth(self, websocket, payload: dict):
        client_id = payload.get("connection_id")
        
        if client_id == self.connection_id:
            self.authenticated_clients.add(websocket)
            self.state.status = "connected"
            
            await websocket.send(json.dumps(create_message(
                MessageType.AUTH_SUCCESS,
                {"agent_state": self.state.to_dict()}
            )))
            print("✅ Client authenticated")
        else:
            await websocket.send(json.dumps(create_message(
                MessageType.AUTH_FAILED,
                error="Invalid connection ID"
            )))
            print(f"❌ Auth failed: {client_id}")
    
    async def handle_command(self, websocket, payload: dict):
        command = payload.get("command")
        params = payload.get("params", {})
        
        print(f"📥 Command: {command}")
        
        if command == "cast_pool":
            await self.handle_cast(websocket, params)
        elif command == "get_status":
            await self.handle_status(websocket)
        else:
            await self.send_error(websocket, f"Unknown: {command}")
    
    async def handle_cast(self, websocket, params: dict):
        question = params.get("question", "What will happen?")
        pauls = params.get("pauls")
        rounds = params.get("rounds")
        
        # Get system limits
        limits = get_system_limits()
        
        # If pauls not provided, prompt user
        if pauls is None:
            await websocket.send(json.dumps(create_message(
                MessageType.INFO,
                {
                    "prompt": "pauls",
                    "message": f"🐟 How many Pauls? (10-{limits['max_pauls']}, recommended: {limits['recommended']})",
                    "max_pauls": limits['max_pauls'],
                    "recommended": limits['recommended'],
                    "available_memory_gb": limits['available_gb']
                }
            )))
            return  # Wait for client to respond with pauls count
        
        pauls = int(pauls)
        
        # Validate pauls count
        if pauls > limits['max_pauls']:
            await self.send_error(websocket, f"Too many Pauls! Your system can handle ~{limits['max_pauls']} with {limits['available_gb']}GB available memory.")
            return
        
        # If rounds not provided, prompt user
        if rounds is None:
            await websocket.send(json.dumps(create_message(
                MessageType.INFO,
                {
                    "prompt": "rounds",
                    "message": f"🔄 How many rounds? (10-1000, recommended: 20-100)",
                    "default": 20
                }
            )))
            return  # Wait for client to respond with rounds count
        
        rounds = int(rounds)
        
        # Now we have both values, run simulation
        await self.run_simulation(websocket, question, pauls, rounds)
    
    async def run_simulation(self, websocket, question: str, pauls: int, rounds: int):
        """Run the actual simulation with given parameters"""
        
        await websocket.send(json.dumps(create_message(
            MessageType.INFO,
            {"message": f"🦷 Casting {pauls} Pauls for {rounds} rounds...", "question": question}
        )))
        
        # Initialize skill bridge for enriched predictions
        skill_bridge = get_skill_bridge() if SIMULATION_AVAILABLE else None
        
        if SIMULATION_AVAILABLE:
            # Generate diverse Pauls based on count
            from persona_factory import generate_swimming_pauls_pool
            
            await websocket.send(json.dumps(create_message(
                MessageType.INFO,
                {"message": f"🎭 Generating {pauls} unique personas..."}
            )))
            
            agents = generate_swimming_pauls_pool(n=pauls)
            
            # Stream progress
            for i in range(min(rounds, 20)):
                await asyncio.sleep(0.2)
                await websocket.send(json.dumps(create_message(
                    MessageType.STREAM,
                    {
                        "round": i + 1,
                        "total": rounds,
                        "progress": (i + 1) / rounds,
                        "status": f"Round {i+1}: {pauls} Pauls deliberating..."
                    }
                )))
            
            # Get final result with skill enrichment
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: quick_simulate(rounds=rounds, agents=agents, question=question)
            )
            
            final = result.rounds[-1] if result.rounds else None
            
            # Build enriched response
            response_data = {
                "consensus": final.consensus if final else {"direction": "NEUTRAL", "confidence": 0.5},
                "sentiment": final.sentiment if final else 0,
                "rounds_completed": len(result.rounds),
                "pauls_count": pauls,
                "question": question,
                "message": f"✅ Simulation complete. {pauls} Pauls reached consensus after {rounds} rounds.",
                "system_limits": get_system_limits()
            }
            
            await websocket.send(json.dumps(create_message(
                MessageType.RESULTS,
                response_data
            )))
        else:
            # Demo mode
            await asyncio.sleep(2)
            
            import random
            directions = ["BULLISH", "BEARISH", "NEUTRAL"]
            direction = random.choice(directions)
            confidence = random.uniform(0.4, 0.9)
            
            await websocket.send(json.dumps(create_message(
                MessageType.RESULTS,
                {
                    "consensus": {"direction": direction, "confidence": round(confidence, 2)},
                    "sentiment": random.uniform(-1, 1),
                    "pauls_count": pauls,
                    "rounds": rounds,
                    "question": question,
                    "message": f"🎯 Demo result: {pauls} Pauls are {direction} ({confidence:.0%} confidence)",
                    "system_limits": get_system_limits()
                }
            )))
    async def handle_status(self, websocket):
        await websocket.send(json.dumps(create_message(
            MessageType.STATUS,
            self.state.to_dict()
        )))
    
    async def handle_ping(self, websocket):
        await websocket.send(json.dumps(create_message(
            MessageType.PONG,
            {"connection_id": self.connection_id}
        )))
    
    async def send_error(self, websocket, error: str):
        await websocket.send(json.dumps(create_message(
            MessageType.ERROR,
            error=error
        )))
    
    async def start(self):
        self._running = True
        self.print_startup()
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"🚀 Server running at ws://{self.host}:{self.port}")
            while self._running:
                await asyncio.sleep(1)
    
    def stop(self):
        self._running = False
        print("\n🛑 Stopping...")


def main():
    parser = argparse.ArgumentParser(description="Swimming Pauls Local Agent")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = parser.parse_args()
    
    server = LocalAgentServer(host=args.host, port=args.port)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        server.stop()
        print("👋 Bye!")


if __name__ == "__main__":
    main()
