#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/brain/.openclaw/workspace/swimming_pauls')

# Simple test to see if we can import and get connection
import asyncio
import websockets
import json

async def test():
    print("Testing WebSocket server...")
    try:
        async with websockets.connect('ws://localhost:8765') as ws:
            await ws.send(json.dumps({"type": "auth", "payload": {"connection_id": "test"}}))
            response = await ws.recv()
            print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
