#!/usr/bin/env python3
"""
Swimming Pauls - OpenClaw Skill
Integration for running local multi-agent predictions via OpenClaw.

This skill:
1. Starts/connects to the local agent if not running
2. Sends the user's question to the simulation
3. Returns formatted results with explorer links
"""

import asyncio
import json
import subprocess
import sys
import os
import websockets
from pathlib import Path
from datetime import datetime

# Configuration
WS_URL = "ws://localhost:8765"
UI_URL = "http://localhost:3005"
MAX_WAIT_TIME = 120  # seconds

class SwimmingPaulsSkill:
    """OpenClaw skill for Swimming Pauls integration."""
    
    def __init__(self):
        self.ws = None
        self.connection_id = None
    
    async def ensure_agent_running(self):
        """Check if local agent is running, start if not."""
        try:
            # Try to connect to existing agent
            self.ws = await asyncio.wait_for(
                websockets.connect(WS_URL),
                timeout=5
            )
            return True
        except:
            # Agent not running, start it
            print("🔌 Starting Swimming Pauls local agent...")
            
            base_dir = Path(__file__).parent.parent
            subprocess.Popen(
                [sys.executable, "local_agent.py"],
                cwd=base_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            
            # Wait for agent to start
            for i in range(10):
                await asyncio.sleep(1)
                try:
                    self.ws = await asyncio.wait_for(
                        websockets.connect(WS_URL),
                        timeout=2
                    )
                    return True
                except:
                    continue
            
            return False
    
    async def authenticate(self):
        """Authenticate with the local agent."""
        if not self.ws:
            return False
        
        # Send auth request
        await self.ws.send(json.dumps({
            "type": "auth",
            "payload": {"connection_id": "openclaw"}
        }))
        
        # Wait for auth response
        response = await asyncio.wait_for(self.ws.recv(), timeout=5)
        data = json.loads(response)
        
        if data.get("type") == "auth_success":
            self.connection_id = data.get("payload", {}).get("agent_state", {}).get("connection_id")
            return True
        
        return False
    
    async def run_prediction(self, question: str, pauls: int = 50, rounds: int = 20):
        """Run a prediction and return the result."""
        
        # Ensure agent is running
        if not await self.ensure_agent_running():
            return {
                "error": "Could not start local agent",
                "message": "Failed to start Swimming Pauls. Check that all dependencies are installed."
            }
        
        # Authenticate
        if not await self.authenticate():
            return {
                "error": "Authentication failed",
                "message": "Could not authenticate with local agent."
            }
        
        # Send cast command
        await self.ws.send(json.dumps({
            "type": "command",
            "payload": {
                "command": "cast_pool",
                "params": {
                    "question": question,
                    "pauls": pauls,
                    "rounds": rounds
                }
            }
        }))
        
        # Collect responses
        result_data = None
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < MAX_WAIT_TIME:
            try:
                response = await asyncio.wait_for(self.ws.recv(), timeout=30)
                data = json.loads(response)
                
                msg_type = data.get("type")
                payload = data.get("payload", {})
                
                if msg_type == "results":
                    result_data = payload
                    break
                elif msg_type == "error":
                    return {
                        "error": data.get("error", "Unknown error"),
                        "message": "Simulation failed"
                    }
                elif msg_type == "info":
                    print(f"ℹ️  {payload.get('message', '')}")
                elif msg_type == "stream":
                    progress = payload.get("progress", 0)
                    print(f"⏳ Progress: {progress*100:.0f}%")
                    
            except asyncio.TimeoutError:
                continue
        
        if not result_data:
            return {
                "error": "Timeout",
                "message": f"Simulation did not complete within {MAX_WAIT_TIME} seconds"
            }
        
        return self.format_result(result_data)
    
    def format_result(self, data):
        """Format prediction result for Telegram response."""
        consensus = data.get("consensus", {})
        direction = consensus.get("direction", "NEUTRAL")
        confidence = int(consensus.get("confidence", 0.5) * 100)
        
        result_id = data.get("result_id", "demo")
        view_urls = data.get("view_urls", {})
        
        # Build explorer links
        explorer_url = view_urls.get("explorer", f"{UI_URL}/explorer.html?id={result_id}")
        visualize_url = view_urls.get("visualize", f"{UI_URL}/visualize.html?id={result_id}")
        debate_url = view_urls.get("debate", f"{UI_URL}/debate_network.html?id={result_id}")
        
        # Emoji map
        emoji_map = {
            "BULLISH": "🟢",
            "BEARISH": "🔴",
            "NEUTRAL": "🟡"
        }
        emoji = emoji_map.get(direction, "⚪")
        
        # Format response
        response = f"""🦷 **SWIMMING PAULS CONSENSUS**

{emoji} **{direction}** ({confidence}% confidence)

📊 **Stats:**
• Pauls: {data.get('pauls_count', 0)}
• Rounds: {data.get('rounds', 0)}
• Question: {data.get('question', 'N/A')[:60]}...

🔗 **View Full Results:**
• [📊 Explorer]({explorer_url})
• [🕸️ Network]({visualize_url})
• [💬 Debate]({debate_url})

💡 Open in browser to see detailed analysis and Paul perspectives.
"""
        
        return {
            "text": response,
            "result_id": result_id,
            "explorer_url": explorer_url,
            "visualize_url": visualize_url,
            "debate_url": debate_url,
            "consensus": direction,
            "confidence": confidence,
            "pauls": data.get("pauls_count", 0),
            "rounds": data.get("rounds", 0)
        }


async def main():
    """Main entry point for OpenClaw skill."""
    
    # Get question from command line or environment
    question = os.environ.get("PAULS_QUESTION", "")
    
    if not question and len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    
    if not question:
        print("Usage: python skill.py [question]")
        print("   or: PAULS_QUESTION='Will BTC hit 100k?' python skill.py")
        sys.exit(1)
    
    # Get optional parameters from environment
    pauls = int(os.environ.get("PAULS_COUNT", "50"))
    rounds = int(os.environ.get("PAULS_ROUNDS", "20"))
    
    print(f"🦷 Running Swimming Pauls...")
    print(f"   Question: {question[:50]}...")
    print(f"   Pauls: {pauls} | Rounds: {rounds}")
    print()
    
    # Run prediction
    skill = SwimmingPaulsSkill()
    result = await skill.run_prediction(question, pauls, rounds)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        print(f"   {result.get('message', '')}")
        sys.exit(1)
    
    # Output result
    print(result["text"])
    
    # Also output JSON for programmatic use
    print()
    print("---JSON---")
    print(json.dumps({
        "result_id": result["result_id"],
        "explorer_url": result["explorer_url"],
        "visualize_url": result["visualize_url"],
        "debate_url": result["debate_url"],
        "consensus": result["consensus"],
        "confidence": result["confidence"],
        "pauls": result["pauls"],
        "rounds": result["rounds"]
    }))


if __name__ == "__main__":
    asyncio.run(main())
