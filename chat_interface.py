"""
Swimming Pauls - Chat Bot Integration
Handles Telegram/chat interactions and serves prediction results.

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
import json
import uuid
import os
import sys
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prediction_history import PredictionHistoryDB

class ChatInterface:
    """Interface for chat-based Swimming Pauls interactions."""
    
    def __init__(self, db_path: str = "data/predictions.db"):
        self.db = PredictionHistoryDB(db_path)
        self.results_dir = Path("data/results")
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_result_id(self) -> str:
        """Generate unique result ID for sharing."""
        return str(uuid.uuid4())[:8]
    
    def save_prediction_result(self, result: Dict) -> str:
        """Save full prediction result and return shareable ID."""
        result_id = self.generate_result_id()
        result_file = self.results_dir / f"{result_id}.json"
        
        # Add metadata
        result['result_id'] = result_id
        result['saved_at'] = datetime.utcnow().isoformat()
        
        # Save to file
        with open(result_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result_id
    
    def get_prediction_result(self, result_id: str) -> Optional[Dict]:
        """Retrieve prediction result by ID."""
        result_file = self.results_dir / f"{result_id}.json"
        if result_file.exists():
            with open(result_file, 'r') as f:
                return json.load(f)
        return None
    
    def format_chat_response(self, result: Dict, base_url: str = "http://localhost:3005") -> str:
        """Format prediction result for chat response."""
        consensus = result.get('consensus', {})
        direction = consensus.get('direction', 'NEUTRAL')
        confidence = int(consensus.get('confidence', 0.5) * 100)
        
        # Get key Paul quotes
        paul_quotes = result.get('paul_quotes', [])
        if not paul_quotes and 'agents' in result:
            # Extract from agents data
            for agent in result.get('agents', [])[:3]:
                if 'reasoning' in agent:
                    paul_quotes.append({
                        'name': agent.get('name', 'Unknown Paul'),
                        'quote': agent.get('reasoning', '')[:100] + '...'
                    })
        
        # Build response
        emoji_map = {
            'BULLISH': '🟢',
            'BEARISH': '🔴', 
            'NEUTRAL': '🟡'
        }
        emoji = emoji_map.get(direction, '⚪')
        
        response = f"""🦷 **SWIMMING PAULS CONSENSUS**

{emoji} **{direction}** ({confidence}% confidence)

📊 **Stats:**
• Pauls: {result.get('pauls_count', 0)}
• Rounds: {result.get('rounds', 0)}
• Question: {result.get('question', 'N/A')[:60]}...

"""
        
        # Add key quotes
        if paul_quotes:
            response += "💬 **Key Perspectives:**\n\n"
            for quote in paul_quotes[:3]:
                name = quote.get('name', 'Paul')
                text = quote.get('quote', '')[:80]
                response += f"• **{name}**: \"{text}\"\n"
        
        # Add view links
        result_id = result.get('result_id', '')
        if result_id:
            response += f"""
📈 **View Full Results:**
• [Explorer]({base_url}/explorer.html?id={result_id})
• [Visualization]({base_url}/visualize.html?id={result_id})
• [Debate Network]({base_url}/debate_network.html?id={result_id})
"""
        
        return response
    
    def get_all_results(self) -> list:
        """Get all saved result IDs."""
        results = []
        for f in self.results_dir.glob("*.json"):
            result_id = f.stem
            data = self.get_prediction_result(result_id)
            if data:
                results.append({
                    'id': result_id,
                    'question': data.get('question', 'Unknown')[:50],
                    'timestamp': data.get('saved_at', ''),
                    'consensus': data.get('consensus', {})
                })
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)


# Simple HTTP server for serving results
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class ResultsHandler(BaseHTTPRequestHandler):
    """HTTP handler for serving prediction results."""
    
    chat_interface = None
    
    def do_GET(self):
        """Handle GET requests."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)
        
        if path == '/api/result':
            # Serve prediction result by ID
            result_id = query.get('id', [None])[0]
            if result_id and self.chat_interface:
                result = self.chat_interface.get_prediction_result(result_id)
                if result:
                    self._send_json(200, result)
                else:
                    self._send_json(404, {'error': 'Result not found'})
            else:
                self._send_json(400, {'error': 'Missing result ID'})
        
        elif path == '/api/results':
            # List all results
            if self.chat_interface:
                results = self.chat_interface.get_all_results()
                self._send_json(200, {'results': results})
            else:
                self._send_json(500, {'error': 'Interface not initialized'})
        
        elif path == '/api/social/feed':
            # Get social media feed
            try:
                from social_media import SocialMediaManager, Platform
                social = SocialMediaManager()
                platform = query.get('platform', ['twitter'])[0]
                limit = int(query.get('limit', [20])[0])
                
                posts = social.get_feed(Platform(platform), limit)
                self._send_json(200, {
                    'platform': platform,
                    'posts': [p.to_dict() for p in posts]
                })
            except Exception as e:
                self._send_json(500, {'error': str(e)})
        
        elif path == '/api/social/paul':
            # Get Paul's social stats
            try:
                from social_media import SocialMediaManager
                social = SocialMediaManager()
                paul_name = query.get('name', [None])[0]
                
                if paul_name:
                    stats = social.get_paul_social_stats(paul_name)
                    posts = social.get_paul_posts(paul_name, limit=10)
                    self._send_json(200, {
                        'paul': paul_name,
                        'stats': stats,
                        'posts': [p.to_dict() for p in posts]
                    })
                else:
                    self._send_json(400, {'error': 'Missing Paul name'})
            except Exception as e:
                self._send_json(500, {'error': str(e)})
        
        elif path == '/api/social/trending':
            # Get trending topics
            try:
                from social_media import SocialMediaManager
                social = SocialMediaManager()
                limit = int(query.get('limit', [10])[0])
                
                trends = social.get_trending(limit)
                self._send_json(200, {'trending': trends})
            except Exception as e:
                self._send_json(500, {'error': str(e)})
        
        else:
            self._send_json(404, {'error': 'Not found'})
    
    def do_POST(self):
        """Handle POST requests."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        if path == '/api/predict':
            # Receive prediction result and save it
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body)
                if self.chat_interface:
                    result_id = self.chat_interface.save_prediction_result(data)
                    self._send_json(200, {
                        'success': True,
                        'result_id': result_id,
                        'urls': {
                            'explorer': f'/explorer.html?id={result_id}',
                            'visualize': f'/visualize.html?id={result_id}',
                            'debate': f'/debate_network.html?id={result_id}'
                        }
                    })
                else:
                    self._send_json(500, {'error': 'Interface not initialized'})
            except json.JSONDecodeError:
                self._send_json(400, {'error': 'Invalid JSON'})
        else:
            self._send_json(404, {'error': 'Not found'})
    
    def _send_json(self, status_code: int, data: Dict):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def start_results_server(port: int = 8080, db_path: str = "data/predictions.db"):
    """Start HTTP server for serving results."""
    ResultsHandler.chat_interface = ChatInterface(db_path)
    server = HTTPServer(('localhost', port), ResultsHandler)
    print(f"📊 Results server started at http://localhost:{port}")
    print(f"   API endpoints:")
    print(f"   - GET  /api/result?id=xxx")
    print(f"   - GET  /api/results")
    print(f"   - POST /api/predict")
    return server


if __name__ == "__main__":
    server = start_results_server()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Results server stopped")
