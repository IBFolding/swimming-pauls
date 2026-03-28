#!/usr/bin/env python3
"""
Swimming Pauls - Local Agent Connector
WebSocket server connecting UI to local multi-agent simulations.

Expanded with full app API endpoints for the local web UI.
"""

import asyncio
import json
import uuid
import argparse
import os
import sys
import time
import glob
import subprocess
import sqlite3
from datetime import datetime
from typing import Dict, Set, Optional, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    print("❌ Missing websockets. Run: pip install websockets")
    sys.exit(1)

try:
    import yaml
except ImportError:
    yaml = None
    print("⚠️  PyYAML not installed. Config save/load will use JSON fallback.")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

# Optional psutil
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Import Swimming Pauls simulation
try:
    from simulation import quick_simulate
    from agent import Agent, PersonaType
    from skill_bridge import get_skill_bridge
    from prediction_history import PredictionHistoryDB
    from chat_interface import ChatInterface
    SIMULATION_AVAILABLE = True
except ImportError as e:
    SIMULATION_AVAILABLE = False
    print(f"⚠️  Swimming Pauls simulation not found: {e}. Running in demo mode.")

# Import Paul's World
try:
    from paul_world import PaulWorld
    WORLD_AVAILABLE = True
except ImportError:
    WORLD_AVAILABLE = False
    print("⚠️  Paul's World not available")

# Import Social Media
try:
    from social_media import SocialMediaManager, Platform
    SOCIAL_AVAILABLE = True
except ImportError:
    SOCIAL_AVAILABLE = False
    print("⚠️  Social media system not available")

# Import Script Doctor
try:
    from script_doctor import ScriptParser, ScriptDoctor
    SCRIPT_DOCTOR_AVAILABLE = True
except ImportError:
    SCRIPT_DOCTOR_AVAILABLE = False
    print("⚠️  Script Doctor not available")


# Project root (directory containing this file)
PROJECT_ROOT = Path(os.path.dirname(os.path.abspath(__file__)))

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8765

# Default config matching config_loader.py
DEFAULT_CONFIG = {
    'defaults': {'pauls': 50, 'rounds': 20, 'timeout_seconds': 120},
    'server': {'websocket_port': 8765, 'ui_port': 3005, 'host': 'localhost'},
    'auto_resolver': {'enabled': True, 'interval_minutes': 60, 'symbols': ['BTC', 'ETH', 'SOL', 'DOGE', 'LINK']},
    'price_tracker': {'enabled': True, 'interval_minutes': 30, 'symbols': ['BTC', 'ETH', 'SOL', 'DOGE', 'LINK', 'AVAX', 'BNB', 'ADA', 'DOT']},
    'notifications': {'enabled': False},
    'learning': {'track_accuracy': True, 'min_predictions_for_leaderboard': 1, 'weight_recent_predictions': True},
    'paper_trading': {'enabled': True, 'update_interval_seconds': 30, 'max_positions': 10000},
    'ollama': {'url': 'http://localhost:11434', 'model': 'llama3.2'},
}


def get_system_limits():
    """Check system resources and return recommended max Pauls"""
    if PSUTIL_AVAILABLE:
        memory = psutil.virtual_memory()
        available_gb = memory.available / (1024**3)
        total_gb = memory.total / (1024**3)
    else:
        available_gb = 8.0
        total_gb = 16.0

    max_pauls = int(available_gb / 0.05)
    if max_pauls > 10000:
        max_pauls = 10000
    elif max_pauls < 10:
        max_pauls = 10

    return {
        "max_pauls": max_pauls,
        "recommended": min(100, max_pauls),
        "available_gb": round(available_gb, 1),
        "total_gb": round(total_gb, 1)
    }


class MessageType(Enum):
    # Existing types
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

    # New API types
    CONFIG_GET = "config.get"
    CONFIG_SAVE = "config.save"
    OLLAMA_MODELS = "ollama.models"
    OLLAMA_TEST = "ollama.test"
    LEADERBOARD_GET = "leaderboard.get"
    TRADING_STATUS = "trading.status"
    TRADING_START = "trading.start"
    TRADING_STOP = "trading.stop"
    WORLD_START = "world.start"
    WORLD_STOP = "world.stop"
    WORLD_STATUS = "world.status"
    WORLD_PAUL = "world.paul"
    WORLD_LOCATIONS = "world.locations"
    SOCIAL_FEED = "social.feed"
    SOCIAL_TRENDING = "social.trending"
    HISTORY_LIST = "history.list"
    HISTORY_GET = "history.get"
    CREATIVE_ANALYZE = "creative.analyze"

    # Generic response wrapper for new API calls
    RESPONSE = "response"


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


def create_response(request_type: str, payload: dict = None, error: str = None):
    """Create a response message that echoes the request type."""
    msg = {
        "type": request_type,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if payload is not None:
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

        # Subprocess tracking for auto_trader
        self._auto_trader_proc: Optional[subprocess.Popen] = None

        # Paul's World instance
        self._world: Optional[Any] = None
        self._world_task: Optional[asyncio.Task] = None

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

    async def handle_client(self, websocket, path=None):
        """Handle client connection."""
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

            # Auth always allowed
            if msg_type == MessageType.AUTH.value:
                await self.handle_auth(websocket, payload)
                return

            # Check authentication for everything else
            if websocket not in self.authenticated_clients:
                await self.send_error(websocket, "Not authenticated")
                return

            # --- Existing message types ---
            if msg_type == MessageType.COMMAND.value:
                await self.handle_command(websocket, payload)
            elif msg_type == MessageType.PING.value:
                await self.handle_ping(websocket)
            elif msg_type == MessageType.STATUS.value or msg_type == "get_status":
                await self.handle_status(websocket)

            # --- New API message types ---
            elif msg_type == MessageType.CONFIG_GET.value:
                await self.handle_config_get(websocket, payload)
            elif msg_type == MessageType.CONFIG_SAVE.value:
                await self.handle_config_save(websocket, payload)
            elif msg_type == MessageType.OLLAMA_MODELS.value:
                await self.handle_ollama_models(websocket, payload)
            elif msg_type == MessageType.OLLAMA_TEST.value:
                await self.handle_ollama_test(websocket, payload)
            elif msg_type == MessageType.LEADERBOARD_GET.value:
                await self.handle_leaderboard_get(websocket, payload)
            elif msg_type == MessageType.TRADING_STATUS.value:
                await self.handle_trading_status(websocket, payload)
            elif msg_type == MessageType.TRADING_START.value:
                await self.handle_trading_start(websocket, payload)
            elif msg_type == MessageType.TRADING_STOP.value:
                await self.handle_trading_stop(websocket, payload)
            elif msg_type == MessageType.WORLD_START.value:
                await self.handle_world_start(websocket, payload)
            elif msg_type == MessageType.WORLD_STOP.value:
                await self.handle_world_stop(websocket, payload)
            elif msg_type == MessageType.WORLD_STATUS.value:
                await self.handle_world_status(websocket, payload)
            elif msg_type == MessageType.WORLD_PAUL.value:
                await self.handle_world_paul(websocket, payload)
            elif msg_type == MessageType.WORLD_LOCATIONS.value:
                await self.handle_world_locations(websocket, payload)
            elif msg_type == MessageType.SOCIAL_FEED.value:
                await self.handle_social_feed(websocket, payload)
            elif msg_type == MessageType.SOCIAL_TRENDING.value:
                await self.handle_social_trending(websocket, payload)
            elif msg_type == MessageType.HISTORY_LIST.value:
                await self.handle_history_list(websocket, payload)
            elif msg_type == MessageType.HISTORY_GET.value:
                await self.handle_history_get(websocket, payload)
            elif msg_type == MessageType.CREATIVE_ANALYZE.value:
                await self.handle_creative_analyze(websocket, payload)
            else:
                await self.send_error(websocket, f"Unknown type: {msg_type}")

        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON")
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            import traceback
            traceback.print_exc()
            await self.send_error(websocket, str(e))

    # ──────────────────────────────────────────────
    # AUTH
    # ──────────────────────────────────────────────

    async def handle_auth(self, websocket, payload: dict):
        client_id = payload.get("connection_id")

        if client_id == self.connection_id or client_id == "openclaw":
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

    # ──────────────────────────────────────────────
    # EXISTING: COMMAND / STATUS / PING
    # ──────────────────────────────────────────────

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

        limits = get_system_limits()

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
            return

        pauls = int(pauls)

        if pauls > limits['max_pauls']:
            await self.send_error(websocket, f"Too many Pauls! Your system can handle ~{limits['max_pauls']} with {limits['available_gb']}GB available memory.")
            return

        if rounds is None:
            await websocket.send(json.dumps(create_message(
                MessageType.INFO,
                {
                    "prompt": "rounds",
                    "message": f"🔄 How many rounds? (10-1000, recommended: 20-100)",
                    "default": 20
                }
            )))
            return

        rounds = int(rounds)
        await self.run_simulation(websocket, question, pauls, rounds)

    async def run_simulation(self, websocket, question: str, pauls: int, rounds: int):
        """Run the actual simulation with given parameters"""

        await websocket.send(json.dumps(create_message(
            MessageType.INFO,
            {"message": f"🦷 Casting {pauls} Pauls for {rounds} rounds...", "question": question}
        )))

        skill_bridge = get_skill_bridge() if SIMULATION_AVAILABLE else None

        if SIMULATION_AVAILABLE:
            from persona_factory import generate_swimming_pauls_pool

            await websocket.send(json.dumps(create_message(
                MessageType.INFO,
                {"message": f"🎭 Generating {pauls} unique personas..."}
            )))

            agents = generate_swimming_pauls_pool(n=pauls)

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

            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: quick_simulate(rounds=rounds, agents=agents, question=question)
            )

            final = result.rounds[-1] if result.rounds else None

            response_data = {
                "consensus": final.consensus if final else {"direction": "NEUTRAL", "confidence": 0.5},
                "sentiment": final.sentiment if final else 0,
                "rounds_completed": len(result.rounds),
                "pauls_count": pauls,
                "rounds": rounds,
                "question": question,
                "message": f"✅ Simulation complete. {pauls} Pauls reached consensus after {rounds} rounds.",
                "system_limits": get_system_limits(),
                "agents": [{"name": a.name, "specialty": getattr(a, 'specialty', 'General'),
                           "reasoning": getattr(a, 'last_reasoning', 'No reasoning recorded')[:200]}
                          for a in agents[:10]]
            }

            if SIMULATION_AVAILABLE:
                try:
                    chat_interface = ChatInterface()
                    result_id = chat_interface.save_prediction_result(response_data)
                    response_data["result_id"] = result_id
                    response_data["view_urls"] = {
                        "explorer": f"http://localhost:3005/explorer.html?id={result_id}",
                        "visualize": f"http://localhost:3005/visualize.html?id={result_id}",
                        "debate": f"http://localhost:3005/debate_network.html?id={result_id}"
                    }
                    db = PredictionHistoryDB()
                    db.record_prediction(
                        prediction_id=result_id,
                        question=question,
                        consensus_direction=response_data["consensus"]["direction"],
                        consensus_confidence=response_data["consensus"]["confidence"],
                        sentiment_score=response_data["sentiment"],
                        pauls_count=pauls,
                        rounds=rounds,
                        duration_ms=0
                    )
                except Exception as e:
                    print(f"⚠️  Could not save result: {e}")

            await websocket.send(json.dumps(create_message(
                MessageType.RESULTS,
                response_data
            )))
        else:
            await asyncio.sleep(2)

            import random
            directions = ["BULLISH", "BEARISH", "NEUTRAL"]
            direction = random.choice(directions)
            confidence = random.uniform(0.4, 0.9)

            demo_result = {
                "consensus": {"direction": direction, "confidence": round(confidence, 2)},
                "sentiment": random.uniform(-1, 1),
                "pauls_count": pauls,
                "rounds": rounds,
                "question": question,
                "message": f"🎯 Demo result: {pauls} Pauls are {direction} ({confidence:.0%} confidence)",
                "system_limits": get_system_limits(),
                "demo": True,
                "agents": [
                    {"name": "Visionary Paul", "specialty": "Long-term", "reasoning": "Based on pattern recognition..."},
                    {"name": "Skeptic Paul", "specialty": "Risk", "reasoning": "Counter-argument..."},
                    {"name": "Trader Paul", "specialty": "Timing", "reasoning": "Technical analysis suggests..."}
                ]
            }

            try:
                chat_interface = ChatInterface()
                result_id = chat_interface.save_prediction_result(demo_result)
                demo_result["result_id"] = result_id
                demo_result["view_urls"] = {
                    "explorer": f"http://localhost:3005/explorer.html?id={result_id}",
                    "visualize": f"http://localhost:3005/visualize.html?id={result_id}",
                    "debate": f"http://localhost:3005/debate_network.html?id={result_id}"
                }
            except Exception as e:
                print(f"⚠️  Could not save demo result: {e}")

            await websocket.send(json.dumps(create_message(
                MessageType.RESULTS,
                demo_result
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

    # ══════════════════════════════════════════════
    #  NEW API HANDLERS
    # ══════════════════════════════════════════════

    # ──────────────────────────────────────────────
    # CONFIG
    # ──────────────────────────────────────────────

    def _load_config(self) -> dict:
        """Load config from config.yaml, falling back to defaults."""
        config_path = PROJECT_ROOT / "config.yaml"
        if config_path.exists() and yaml:
            try:
                with open(config_path, "r") as f:
                    user_config = yaml.safe_load(f) or {}
                # Deep merge with defaults
                merged = self._deep_merge(DEFAULT_CONFIG, user_config)
                return merged
            except Exception as e:
                print(f"⚠️  Error loading config.yaml: {e}")
        # Try config.example.yaml
        example_path = PROJECT_ROOT / "config.example.yaml"
        if example_path.exists() and yaml:
            try:
                with open(example_path, "r") as f:
                    user_config = yaml.safe_load(f) or {}
                merged = self._deep_merge(DEFAULT_CONFIG, user_config)
                return merged
            except Exception:
                pass
        return DEFAULT_CONFIG.copy()

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Recursively merge override into base."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    async def handle_config_get(self, websocket, payload: dict):
        """Return current config."""
        try:
            config = self._load_config()
            await websocket.send(json.dumps(create_response(
                "config.get",
                {"config": config}
            )))
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "config.get", error=str(e)
            )))

    async def handle_config_save(self, websocket, payload: dict):
        """Write new config to config.yaml."""
        try:
            new_config = payload.get("config", {})
            if not new_config:
                await websocket.send(json.dumps(create_response(
                    "config.save", error="No config data provided"
                )))
                return

            config_path = PROJECT_ROOT / "config.yaml"

            if yaml:
                with open(config_path, "w") as f:
                    yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
            else:
                # Fallback to JSON if PyYAML isn't available
                with open(config_path, "w") as f:
                    json.dump(new_config, f, indent=2)

            await websocket.send(json.dumps(create_response(
                "config.save",
                {"success": True, "message": "Config saved to config.yaml"}
            )))
            print("💾 Config saved to config.yaml")
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "config.save", error=str(e)
            )))

    # ──────────────────────────────────────────────
    # OLLAMA
    # ──────────────────────────────────────────────

    def _get_ollama_url(self) -> str:
        """Get Ollama base URL from config or default."""
        config = self._load_config()
        return config.get("ollama", {}).get("url", "http://localhost:11434")

    async def handle_ollama_models(self, websocket, payload: dict):
        """Proxy GET to Ollama /api/tags to list available models."""
        ollama_url = self._get_ollama_url()
        url = f"{ollama_url}/api/tags"

        if AIOHTTP_AVAILABLE:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            models = []
                            for m in data.get("models", []):
                                models.append({
                                    "name": m.get("name", ""),
                                    "model": m.get("model", m.get("name", "")),
                                    "size": m.get("size", 0),
                                    "modified_at": m.get("modified_at", ""),
                                    "digest": m.get("digest", "")[:12],
                                })
                            await websocket.send(json.dumps(create_response(
                                "ollama.models",
                                {"models": models, "count": len(models)}
                            )))
                        else:
                            await websocket.send(json.dumps(create_response(
                                "ollama.models",
                                error=f"Ollama returned HTTP {resp.status}"
                            )))
            except asyncio.TimeoutError:
                await websocket.send(json.dumps(create_response(
                    "ollama.models", error="Ollama connection timed out"
                )))
            except aiohttp.ClientConnectorError:
                await websocket.send(json.dumps(create_response(
                    "ollama.models", error=f"Cannot connect to Ollama at {ollama_url}"
                )))
            except Exception as e:
                await websocket.send(json.dumps(create_response(
                    "ollama.models", error=str(e)
                )))
        else:
            # Fallback: use urllib
            try:
                import urllib.request
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                    models = []
                    for m in data.get("models", []):
                        models.append({
                            "name": m.get("name", ""),
                            "model": m.get("model", m.get("name", "")),
                            "size": m.get("size", 0),
                            "modified_at": m.get("modified_at", ""),
                        })
                    await websocket.send(json.dumps(create_response(
                        "ollama.models",
                        {"models": models, "count": len(models)}
                    )))
            except Exception as e:
                await websocket.send(json.dumps(create_response(
                    "ollama.models", error=f"Cannot reach Ollama: {e}"
                )))

    async def handle_ollama_test(self, websocket, payload: dict):
        """Test Ollama connection, return status + latency."""
        ollama_url = self._get_ollama_url()
        url = f"{ollama_url}/api/tags"

        start_time = time.time()
        status = "disconnected"
        latency_ms = 0
        model_count = 0
        error_msg = None

        if AIOHTTP_AVAILABLE:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        latency_ms = round((time.time() - start_time) * 1000)
                        if resp.status == 200:
                            data = await resp.json()
                            model_count = len(data.get("models", []))
                            status = "connected"
                        else:
                            status = "error"
                            error_msg = f"HTTP {resp.status}"
            except asyncio.TimeoutError:
                latency_ms = round((time.time() - start_time) * 1000)
                error_msg = "Connection timed out"
            except aiohttp.ClientConnectorError:
                latency_ms = round((time.time() - start_time) * 1000)
                error_msg = f"Cannot connect to {ollama_url}"
            except Exception as e:
                latency_ms = round((time.time() - start_time) * 1000)
                error_msg = str(e)
        else:
            try:
                import urllib.request
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    latency_ms = round((time.time() - start_time) * 1000)
                    data = json.loads(resp.read().decode())
                    model_count = len(data.get("models", []))
                    status = "connected"
            except Exception as e:
                latency_ms = round((time.time() - start_time) * 1000)
                error_msg = str(e)

        result = {
            "status": status,
            "url": ollama_url,
            "latency_ms": latency_ms,
            "models_available": model_count,
        }
        if error_msg:
            result["error_detail"] = error_msg

        await websocket.send(json.dumps(create_response(
            "ollama.test", result, error=error_msg if status != "connected" else None
        )))

    # ──────────────────────────────────────────────
    # LEADERBOARD
    # ──────────────────────────────────────────────

    async def handle_leaderboard_get(self, websocket, payload: dict):
        """Return Paul accuracy rankings from paul_learning.db."""
        domain_filter = payload.get("domain", None)
        limit = payload.get("limit", 50)

        db_path = PROJECT_ROOT / "data" / "paul_learning.db"
        if not db_path.exists():
            await websocket.send(json.dumps(create_response(
                "leaderboard.get",
                {"leaderboard": [], "count": 0, "message": "No learning data yet"}
            )))
            return

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Check which tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

            leaderboard = []

            if "paul_accuracy" in tables:
                # Use the aggregated accuracy table
                if domain_filter:
                    cursor.execute('''
                        SELECT paul_name, domain, total_predictions, correct_predictions,
                               accuracy_rate, avg_confidence
                        FROM paul_accuracy
                        WHERE domain = ?
                        ORDER BY accuracy_rate DESC, total_predictions DESC
                        LIMIT ?
                    ''', (domain_filter, limit))
                else:
                    cursor.execute('''
                        SELECT paul_name, domain, total_predictions, correct_predictions,
                               accuracy_rate, avg_confidence
                        FROM paul_accuracy
                        ORDER BY accuracy_rate DESC, total_predictions DESC
                        LIMIT ?
                    ''', (limit,))

                for row in cursor.fetchall():
                    leaderboard.append({
                        "paul_name": row[0],
                        "domain": row[1],
                        "total_predictions": row[2],
                        "correct_predictions": row[3],
                        "accuracy_rate": round(row[4], 4) if row[4] else 0,
                        "avg_confidence": round(row[5], 4) if row[5] else 0,
                    })

            elif "predictions" in tables:
                # Fall back to computing from raw predictions
                query = '''
                    SELECT paul_name, domain,
                           COUNT(*) as total,
                           SUM(CASE WHEN accuracy > 0 THEN 1 ELSE 0 END) as correct,
                           AVG(CASE WHEN outcome IS NOT NULL THEN
                               CASE WHEN accuracy > 0 THEN 1.0 ELSE 0.0 END
                           END) as acc_rate,
                           AVG(confidence) as avg_conf
                    FROM predictions
                '''
                params: list = []
                if domain_filter:
                    query += ' WHERE domain = ?'
                    params.append(domain_filter)
                query += ' GROUP BY paul_name, domain ORDER BY acc_rate DESC, total DESC LIMIT ?'
                params.append(limit)

                cursor.execute(query, params)
                for row in cursor.fetchall():
                    leaderboard.append({
                        "paul_name": row[0],
                        "domain": row[1],
                        "total_predictions": row[2],
                        "correct_predictions": row[3] or 0,
                        "accuracy_rate": round(row[4], 4) if row[4] else 0,
                        "avg_confidence": round(row[5], 4) if row[5] else 0,
                    })

            conn.close()

            # Add rank
            for i, entry in enumerate(leaderboard):
                entry["rank"] = i + 1

            await websocket.send(json.dumps(create_response(
                "leaderboard.get",
                {"leaderboard": leaderboard, "count": len(leaderboard), "domain": domain_filter}
            )))
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "leaderboard.get", error=str(e)
            )))

    # ──────────────────────────────────────────────
    # TRADING
    # ──────────────────────────────────────────────

    async def handle_trading_status(self, websocket, payload: dict):
        """Return paper trading stats from paper_trading.db."""
        db_path = PROJECT_ROOT / "data" / "paper_trading.db"
        if not db_path.exists():
            await websocket.send(json.dumps(create_response(
                "trading.status",
                {
                    "aggregate_pnl": 0,
                    "total_portfolios": 0,
                    "total_positions": 0,
                    "total_trades": 0,
                    "top_pauls": [],
                    "bottom_pauls": [],
                    "positions": [],
                    "auto_trader_running": self._auto_trader_proc is not None and self._auto_trader_proc.poll() is None,
                    "message": "No paper trading data yet"
                }
            )))
            return

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Load portfolios
            cursor.execute("SELECT paul_name, data, updated_at FROM paper_portfolios")
            portfolios = []
            for row in cursor.fetchall():
                try:
                    data = json.loads(row[1])
                    data["_paul_name"] = row[0]
                    data["_updated_at"] = row[2]
                    portfolios.append(data)
                except json.JSONDecodeError:
                    continue

            # Aggregate stats
            total_pnl = 0.0
            total_positions = 0
            total_trades_count = 0
            portfolio_summaries = []

            for p in portfolios:
                pnl = p.get("total_pnl", 0)
                total_pnl += pnl
                positions = p.get("positions", {})
                total_positions += len(positions)
                trades = p.get("total_trades", 0)
                total_trades_count += trades

                initial = p.get("initial_balance", 10000)
                cash = p.get("cash", 0)
                # Calculate total value
                pos_value = sum(
                    pos.get("quantity", 0) * pos.get("current_price", pos.get("entry_price", 0))
                    for pos in positions.values()
                ) if isinstance(positions, dict) else 0
                total_value = cash + pos_value
                roi = (total_value - initial) / initial if initial > 0 else 0

                winning = p.get("winning_trades", 0)
                losing = p.get("losing_trades", 0)
                win_rate = winning / trades if trades > 0 else 0

                portfolio_summaries.append({
                    "paul_name": p.get("paul_name", p.get("_paul_name", "Unknown")),
                    "total_value": round(total_value, 2),
                    "pnl": round(pnl, 2),
                    "roi": round(roi, 4),
                    "win_rate": round(win_rate, 4),
                    "total_trades": trades,
                    "open_positions": len(positions) if isinstance(positions, dict) else 0,
                    "enabled": p.get("enabled", False),
                    "max_drawdown": round(p.get("max_drawdown", 0), 4),
                })

            # Sort for top/bottom
            sorted_by_roi = sorted(portfolio_summaries, key=lambda x: x["roi"], reverse=True)
            top_pauls = sorted_by_roi[:10]
            bottom_pauls = sorted_by_roi[-10:][::-1] if len(sorted_by_roi) > 10 else []

            # Recent trades
            cursor.execute("""
                SELECT id, paul_name, data, created_at, closed_at
                FROM paper_trades
                ORDER BY created_at DESC
                LIMIT 20
            """)
            recent_trades = []
            for row in cursor.fetchall():
                try:
                    trade_data = json.loads(row[2])
                    trade_data["_id"] = row[0]
                    trade_data["_created_at"] = row[3]
                    trade_data["_closed_at"] = row[4]
                    recent_trades.append(trade_data)
                except json.JSONDecodeError:
                    continue

            # Open positions across all portfolios
            open_positions = []
            for p in portfolios:
                positions = p.get("positions", {})
                if isinstance(positions, dict):
                    for symbol, pos in positions.items():
                        open_positions.append({
                            "paul_name": p.get("paul_name", "Unknown"),
                            "symbol": symbol,
                            "quantity": pos.get("quantity", 0),
                            "entry_price": pos.get("entry_price", 0),
                            "current_price": pos.get("current_price", 0),
                        })

            conn.close()

            auto_running = self._auto_trader_proc is not None and self._auto_trader_proc.poll() is None

            await websocket.send(json.dumps(create_response(
                "trading.status",
                {
                    "aggregate_pnl": round(total_pnl, 2),
                    "total_portfolios": len(portfolios),
                    "total_positions": total_positions,
                    "total_trades": total_trades_count,
                    "top_pauls": top_pauls,
                    "bottom_pauls": bottom_pauls,
                    "recent_trades": recent_trades[:10],
                    "open_positions": open_positions[:20],
                    "auto_trader_running": auto_running,
                }
            )))
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "trading.status", error=str(e)
            )))

    async def handle_trading_start(self, websocket, payload: dict):
        """Start auto_trader.py as subprocess."""
        if self._auto_trader_proc is not None and self._auto_trader_proc.poll() is None:
            await websocket.send(json.dumps(create_response(
                "trading.start",
                {"success": False, "message": "Auto-trader is already running", "pid": self._auto_trader_proc.pid}
            )))
            return

        auto_trader_path = PROJECT_ROOT / "auto_trader.py"
        if not auto_trader_path.exists():
            await websocket.send(json.dumps(create_response(
                "trading.start",
                error="auto_trader.py not found"
            )))
            return

        try:
            self._auto_trader_proc = subprocess.Popen(
                [sys.executable, str(auto_trader_path)],
                cwd=str(PROJECT_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            await websocket.send(json.dumps(create_response(
                "trading.start",
                {"success": True, "message": "Auto-trader started", "pid": self._auto_trader_proc.pid}
            )))
            print(f"📈 Auto-trader started (PID: {self._auto_trader_proc.pid})")
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "trading.start", error=str(e)
            )))

    async def handle_trading_stop(self, websocket, payload: dict):
        """Stop auto_trader.py subprocess."""
        if self._auto_trader_proc is None or self._auto_trader_proc.poll() is not None:
            await websocket.send(json.dumps(create_response(
                "trading.stop",
                {"success": True, "message": "Auto-trader is not running"}
            )))
            self._auto_trader_proc = None
            return

        try:
            pid = self._auto_trader_proc.pid
            self._auto_trader_proc.terminate()
            # Give it 5 seconds to die gracefully
            try:
                self._auto_trader_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._auto_trader_proc.kill()
                self._auto_trader_proc.wait(timeout=3)

            self._auto_trader_proc = None
            await websocket.send(json.dumps(create_response(
                "trading.stop",
                {"success": True, "message": f"Auto-trader stopped (was PID: {pid})"}
            )))
            print(f"📉 Auto-trader stopped (was PID: {pid})")
        except Exception as e:
            self._auto_trader_proc = None
            await websocket.send(json.dumps(create_response(
                "trading.stop", error=str(e)
            )))

    # ──────────────────────────────────────────────
    # WORLD
    # ──────────────────────────────────────────────

    async def _ensure_world(self) -> Optional[Any]:
        """Ensure PaulWorld instance is initialized (but not necessarily running)."""
        if not WORLD_AVAILABLE:
            return None
        if self._world is None:
            self._world = PaulWorld(db_path=str(PROJECT_ROOT / "data" / "paul_world.db"))
            await self._world.initialize()
        return self._world

    async def _world_simulation_loop(self):
        """Background loop that ticks the world simulation."""
        world = self._world
        if not world:
            return
        world.active = True
        print("🌍 World simulation loop started")
        try:
            while world.active:
                await world.tick()
                # Broadcast world status to all authenticated clients
                status = self._build_world_status(world)
                msg = json.dumps(create_response("world.tick", status))
                for client in list(self.authenticated_clients):
                    try:
                        await client.send(msg)
                    except Exception:
                        pass
                await asyncio.sleep(1)  # 1 second per tick
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ World simulation error: {e}")
        finally:
            if world:
                world.active = False
            print("🌍 World simulation loop stopped")

    def _build_world_status(self, world) -> dict:
        """Build a summary dict of the world state."""
        if world is None:
            return {"active": False, "pauls": 0}

        # Location breakdown
        locations: Dict[str, int] = {}
        for paul in world.pauls.values():
            loc = paul.location.value
            locations[loc] = locations.get(loc, 0) + 1

        # Average mood & energy
        paul_count = len(world.pauls)
        avg_mood = sum(p.mood for p in world.pauls.values()) / paul_count if paul_count else 0
        avg_energy = sum(p.energy for p in world.pauls.values()) / paul_count if paul_count else 0

        # Sample pauls (first 5)
        sample_pauls = []
        for paul in list(world.pauls.values())[:5]:
            sample_pauls.append({
                "name": paul.name,
                "emoji": paul.emoji,
                "specialty": paul.specialty,
                "location": paul.location.value,
                "activity": paul.activity.value,
                "energy": round(paul.energy, 1),
                "mood": round(paul.mood, 2),
                "reputation": round(paul.reputation, 2),
            })

        return {
            "active": world.active,
            "pauls_count": paul_count,
            "tick_count": world.tick_count,
            "world_time": world.world_time.isoformat(),
            "locations": locations,
            "avg_mood": round(avg_mood, 2),
            "avg_energy": round(avg_energy, 1),
            "sample_pauls": sample_pauls,
            "events_count": len(world.events),
        }

    async def handle_world_start(self, websocket, payload: dict):
        """Start Paul's World simulation."""
        if not WORLD_AVAILABLE:
            await websocket.send(json.dumps(create_response(
                "world.start", error="Paul's World module not available"
            )))
            return

        world = await self._ensure_world()
        if world is None:
            await websocket.send(json.dumps(create_response(
                "world.start", error="Failed to initialize world"
            )))
            return

        if self._world_task and not self._world_task.done():
            await websocket.send(json.dumps(create_response(
                "world.start",
                {"success": False, "message": "World simulation is already running"}
            )))
            return

        self._world_task = asyncio.create_task(self._world_simulation_loop())

        await websocket.send(json.dumps(create_response(
            "world.start",
            {"success": True, "message": f"World simulation started with {len(world.pauls)} Pauls"}
        )))
        print(f"🌍 World simulation started ({len(world.pauls)} Pauls)")

    async def handle_world_stop(self, websocket, payload: dict):
        """Stop Paul's World simulation."""
        if self._world:
            self._world.active = False

        if self._world_task and not self._world_task.done():
            self._world_task.cancel()
            try:
                await self._world_task
            except asyncio.CancelledError:
                pass

        self._world_task = None

        # Save world state
        if self._world:
            try:
                await self._world._save_world()
            except Exception as e:
                print(f"⚠️  Could not save world state: {e}")

        await websocket.send(json.dumps(create_response(
            "world.stop",
            {"success": True, "message": "World simulation stopped"}
        )))
        print("🌍 World simulation stopped")

    async def handle_world_status(self, websocket, payload: dict):
        """Return current world state."""
        world = await self._ensure_world()
        status = self._build_world_status(world)
        await websocket.send(json.dumps(create_response("world.status", status)))

    async def handle_world_paul(self, websocket, payload: dict):
        """Get individual Paul state by name."""
        paul_name = payload.get("name", "")
        if not paul_name:
            await websocket.send(json.dumps(create_response(
                "world.paul", error="Missing 'name' parameter"
            )))
            return

        world = await self._ensure_world()
        if world is None or paul_name not in world.pauls:
            await websocket.send(json.dumps(create_response(
                "world.paul", error=f"Paul '{paul_name}' not found"
            )))
            return

        paul = world.pauls[paul_name]
        paul_data = paul.to_dict()

        # Add relationships
        relationships = []
        for (a, b), rel in world.relationships.items():
            if a == paul_name or b == paul_name:
                other = b if a == paul_name else a
                relationships.append({
                    "paul": other,
                    "trust": round(rel.trust, 2),
                    "respect": round(rel.respect, 2),
                    "interactions": rel.interactions,
                })
        paul_data["relationships"] = relationships

        # Add recent memories
        paul_data["recent_memories"] = [m.to_dict() for m in paul.get_recent_memories(limit=10)]

        # Add knowledge topics
        paul_data["knowledge_topics"] = [k.topic for k in paul.knowledge[:20]]

        await websocket.send(json.dumps(create_response("world.paul", paul_data)))

    async def handle_world_locations(self, websocket, payload: dict):
        """Get all locations with Paul counts and details."""
        world = await self._ensure_world()

        if world is None:
            await websocket.send(json.dumps(create_response(
                "world.locations",
                {"locations": []}
            )))
            return

        # Build location map
        location_map: Dict[str, List[dict]] = {}
        for paul in world.pauls.values():
            loc = paul.location.value
            if loc not in location_map:
                location_map[loc] = []
            location_map[loc].append({
                "name": paul.name,
                "emoji": paul.emoji,
                "activity": paul.activity.value,
                "energy": round(paul.energy, 1),
                "mood": round(paul.mood, 2),
            })

        locations = []
        for loc_name, pauls_list in sorted(location_map.items()):
            locations.append({
                "location": loc_name,
                "paul_count": len(pauls_list),
                "pauls": pauls_list,
            })

        await websocket.send(json.dumps(create_response(
            "world.locations",
            {"locations": locations, "total_locations": len(locations)}
        )))

    # ──────────────────────────────────────────────
    # SOCIAL
    # ──────────────────────────────────────────────

    async def handle_social_feed(self, websocket, payload: dict):
        """Get recent social posts from social_media.db."""
        platform_filter = payload.get("platform", None)
        limit = min(payload.get("limit", 50), 200)

        db_path = PROJECT_ROOT / "data" / "social_media.db"
        if not db_path.exists():
            await websocket.send(json.dumps(create_response(
                "social.feed",
                {"posts": [], "count": 0, "message": "No social data yet"}
            )))
            return

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            if platform_filter:
                cursor.execute('''
                    SELECT id, author, platform, content, post_type, timestamp,
                           likes, replies, shares, views, topic, sentiment, is_viral, parent_id
                    FROM social_posts
                    WHERE platform = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (platform_filter, limit))
            else:
                cursor.execute('''
                    SELECT id, author, platform, content, post_type, timestamp,
                           likes, replies, shares, views, topic, sentiment, is_viral, parent_id
                    FROM social_posts
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (limit,))

            posts = []
            for row in cursor.fetchall():
                posts.append({
                    "id": row[0],
                    "author": row[1],
                    "platform": row[2],
                    "content": row[3],
                    "post_type": row[4],
                    "timestamp": row[5],
                    "likes": row[6],
                    "replies": row[7],
                    "shares": row[8],
                    "views": row[9],
                    "topic": row[10],
                    "sentiment": row[11],
                    "is_viral": bool(row[12]),
                    "parent_id": row[13],
                })

            conn.close()

            await websocket.send(json.dumps(create_response(
                "social.feed",
                {"posts": posts, "count": len(posts), "platform": platform_filter}
            )))
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "social.feed", error=str(e)
            )))

    async def handle_social_trending(self, websocket, payload: dict):
        """Get trending topics from social media."""
        limit = min(payload.get("limit", 20), 50)

        db_path = PROJECT_ROOT / "data" / "social_media.db"
        if not db_path.exists():
            await websocket.send(json.dumps(create_response(
                "social.trending",
                {"trending": [], "count": 0}
            )))
            return

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Get trending by counting topic occurrences in recent posts
            cursor.execute('''
                SELECT topic, COUNT(*) as post_count,
                       SUM(likes) as total_likes,
                       SUM(shares) as total_shares,
                       AVG(sentiment) as avg_sentiment
                FROM social_posts
                WHERE topic IS NOT NULL AND topic != ''
                GROUP BY topic
                ORDER BY post_count DESC, total_likes DESC
                LIMIT ?
            ''', (limit,))

            trending = []
            for row in cursor.fetchall():
                trending.append({
                    "topic": row[0],
                    "post_count": row[1],
                    "total_likes": row[2] or 0,
                    "total_shares": row[3] or 0,
                    "avg_sentiment": round(row[4], 3) if row[4] else 0,
                })

            conn.close()

            await websocket.send(json.dumps(create_response(
                "social.trending",
                {"trending": trending, "count": len(trending)}
            )))
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "social.trending", error=str(e)
            )))

    # ──────────────────────────────────────────────
    # HISTORY
    # ──────────────────────────────────────────────

    async def handle_history_list(self, websocket, payload: dict):
        """List all past prediction results from data/results/ JSON files."""
        results_dir = PROJECT_ROOT / "data" / "results"
        if not results_dir.exists():
            await websocket.send(json.dumps(create_response(
                "history.list",
                {"results": [], "count": 0}
            )))
            return

        try:
            results = []
            for filepath in sorted(results_dir.glob("*.json"), reverse=True):
                result_id = filepath.stem
                # Skip special files
                if result_id.startswith("_"):
                    continue
                try:
                    with open(filepath, "r") as f:
                        data = json.load(f)
                    results.append({
                        "id": result_id,
                        "question": data.get("question", "Unknown")[:100],
                        "consensus": data.get("consensus", {}),
                        "pauls_count": data.get("pauls_count", 0),
                        "rounds": data.get("rounds", 0),
                        "saved_at": data.get("saved_at", ""),
                        "demo": data.get("demo", False),
                    })
                except (json.JSONDecodeError, IOError):
                    continue

            # Sort by saved_at descending
            results.sort(key=lambda x: x.get("saved_at", ""), reverse=True)

            limit = min(payload.get("limit", 50), 200)
            offset = payload.get("offset", 0)
            page = results[offset:offset + limit]

            await websocket.send(json.dumps(create_response(
                "history.list",
                {"results": page, "count": len(results), "offset": offset, "limit": limit}
            )))
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "history.list", error=str(e)
            )))

    async def handle_history_get(self, websocket, payload: dict):
        """Get specific prediction result by ID."""
        result_id = payload.get("id", "")
        if not result_id:
            await websocket.send(json.dumps(create_response(
                "history.get", error="Missing 'id' parameter"
            )))
            return

        # Sanitize: only allow alphanumeric and hyphens
        safe_id = "".join(c for c in result_id if c.isalnum() or c in "-_")
        filepath = PROJECT_ROOT / "data" / "results" / f"{safe_id}.json"

        if not filepath.exists():
            await websocket.send(json.dumps(create_response(
                "history.get", error=f"Result '{safe_id}' not found"
            )))
            return

        try:
            with open(filepath, "r") as f:
                data = json.load(f)
            await websocket.send(json.dumps(create_response(
                "history.get",
                {"result": data}
            )))
        except Exception as e:
            await websocket.send(json.dumps(create_response(
                "history.get", error=str(e)
            )))

    # ──────────────────────────────────────────────
    # CREATIVE
    # ──────────────────────────────────────────────

    async def handle_creative_analyze(self, websocket, payload: dict):
        """Run script doctor analysis on submitted text."""
        text = payload.get("text", "")
        if not text:
            await websocket.send(json.dumps(create_response(
                "creative.analyze", error="Missing 'text' parameter"
            )))
            return

        if SCRIPT_DOCTOR_AVAILABLE:
            try:
                # Run analysis in executor to avoid blocking
                def do_analysis():
                    parser = ScriptParser()
                    parsed = parser.parse(text)
                    doctor = ScriptDoctor()
                    analysis = doctor.analyze(parsed)
                    return analysis

                analysis = await asyncio.get_event_loop().run_in_executor(None, do_analysis)

                # Convert analysis to JSON-serializable format
                if hasattr(analysis, 'to_dict'):
                    result = analysis.to_dict()
                elif isinstance(analysis, dict):
                    result = analysis
                else:
                    result = {"analysis": str(analysis)}

                await websocket.send(json.dumps(create_response(
                    "creative.analyze",
                    {"analysis": result, "text_length": len(text)}
                )))
            except Exception as e:
                await websocket.send(json.dumps(create_response(
                    "creative.analyze", error=f"Script Doctor error: {e}"
                )))
        else:
            # Basic fallback analysis without the full ScriptDoctor
            try:
                analysis = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: self._basic_script_analysis(text)
                )
                await websocket.send(json.dumps(create_response(
                    "creative.analyze",
                    {"analysis": analysis, "text_length": len(text), "mode": "basic"}
                )))
            except Exception as e:
                await websocket.send(json.dumps(create_response(
                    "creative.analyze", error=str(e)
                )))

    def _basic_script_analysis(self, text: str) -> dict:
        """Basic script analysis fallback when ScriptDoctor isn't available."""
        import re

        lines = text.strip().split("\n")
        word_count = len(text.split())
        char_count = len(text)

        # Detect scene headings
        scene_pattern = re.compile(r'^(INT\.|EXT\.)', re.IGNORECASE | re.MULTILINE)
        scenes = scene_pattern.findall(text)

        # Detect dialogue (ALL CAPS name followed by content)
        dialogue_pattern = re.compile(r'^[A-Z][A-Z\s]{2,}$', re.MULTILINE)
        dialogue_cues = dialogue_pattern.findall(text)

        # Detect parentheticals
        paren_pattern = re.compile(r'\(.*?\)')
        parentheticals = paren_pattern.findall(text)

        return {
            "summary": {
                "lines": len(lines),
                "words": word_count,
                "characters": char_count,
                "scenes_detected": len(scenes),
                "dialogue_cues": len(dialogue_cues),
                "parentheticals": len(parentheticals),
            },
            "notes": [
                "Script Doctor module not available — showing basic analysis.",
                f"Detected {len(scenes)} scene headings.",
                f"Found {len(dialogue_cues)} potential dialogue cues.",
                f"Text is approximately {word_count / 250:.1f} pages (250 words/page).",
            ],
            "issues": [],
        }

    # ──────────────────────────────────────────────
    # SERVER LIFECYCLE
    # ──────────────────────────────────────────────

    async def start(self):
        self._running = True
        self.print_startup()

        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"🚀 Server running at ws://{self.host}:{self.port}")
            while self._running:
                await asyncio.sleep(1)

    def stop(self):
        self._running = False

        # Stop auto trader if running
        if self._auto_trader_proc and self._auto_trader_proc.poll() is None:
            self._auto_trader_proc.terminate()
            try:
                self._auto_trader_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._auto_trader_proc.kill()
            self._auto_trader_proc = None

        # Stop world simulation
        if self._world:
            self._world.active = False
        if self._world_task and not self._world_task.done():
            self._world_task.cancel()

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
