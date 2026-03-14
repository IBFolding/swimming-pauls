#!/usr/bin/env python3
"""
Test Client for Swimming Pauls Local Agent

Usage:
    python test_client.py --id YOUR_CONNECTION_ID
"""

import asyncio
import argparse
import json

import websockets


async def test_client(connection_id: str, host: str = "localhost", port: int = 8765):
    """Test WebSocket connection to local agent."""
    uri = f"ws://{host}:{port}"
    
    print(f"🔌 Connecting to {uri}...")
    
    async with websockets.connect(uri) as websocket:
        print("✅ Connected!\n")
        
        # 1. Authenticate
        print("📤 Sending authentication...")
        await websocket.send(json.dumps({
            "type": "auth",
            "payload": {"connection_id": connection_id}
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        print(f"📥 Response: {json.dumps(data, indent=2)}\n")
        
        if data.get("type") == "auth_failed":
            print("❌ Authentication failed!")
            return
        
        # 2. Get status
        print("📤 Getting status...")
        await websocket.send(json.dumps({
            "type": "command",
            "payload": {"command": "get_status"}
        }))
        
        response = await websocket.recv()
        print(f"📥 Status: {json.dumps(json.loads(response), indent=2)}\n")
        
        # 3. Ping
        print("📤 Sending ping...")
        await websocket.send(json.dumps({
            "type": "ping"
        }))
        
        response = await websocket.recv()
        print(f"📥 Pong: {json.dumps(json.loads(response), indent=2)}\n")
        
        # 4. Run simulation
        print("📤 Starting pool simulation...")
        await websocket.send(json.dumps({
            "type": "command",
            "payload": {
                "command": "cast_pool",
                "params": {
                    "fish_type": "carp",
                    "bait": "corn",
                    "water_temp": 22.5,
                    "weather": "cloudy",
                    "duration": 10  # Short duration for testing
                }
            }
        }))
        
        print("⏳ Receiving simulation updates...")
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=15)
                data = json.loads(response)
                
                if data.get("type") == "stream":
                    payload = data.get("payload", {})
                    print(f"   Step {payload.get('step')}/{payload.get('total_steps')}: {payload.get('log')}")
                elif data.get("type") == "results":
                    print(f"\n📥 Final Results: {json.dumps(data, indent=2)}")
                    break
                elif data.get("type") == "error":
                    print(f"❌ Error: {data.get('error')}")
                    break
                    
            except asyncio.TimeoutError:
                print("⏱️ Timeout waiting for response")
                break
        
        # 5. Get all results
        print("\n📤 Getting all results...")
        await websocket.send(json.dumps({
            "type": "command",
            "payload": {"command": "get_results"}
        }))
        
        response = await websocket.recv()
        data = json.loads(response)
        print(f"📥 Results count: {data.get('payload', {}).get('count', 0)}")
        
    print("\n✅ Test completed!")


def main():
    parser = argparse.ArgumentParser(description="Test Swimming Pauls Local Agent")
    parser.add_argument("--id", "--connection-id", required=True, help="Connection ID from server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8765, help="Server port")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(test_client(args.id, args.host, args.port))
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
