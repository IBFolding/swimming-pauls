"""
ReportAgent API Server for Swimming Pauls
HTTP API for generating, retrieving, and managing reports.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, Optional
import threading

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from .report_agent import ReportAgent, Report, ReportFormat
    from .simulation import SimulationResult, SimulationRunner
    from .agent import create_agent_team
except ImportError:
    from report_agent import ReportAgent, Report, ReportFormat
    from simulation import SimulationResult, SimulationRunner
    from agent import create_agent_team


class ReportAPIHandler(BaseHTTPRequestHandler):
    """HTTP handler for ReportAgent API."""
    
    report_agent: Optional[ReportAgent] = None
    active_simulations: Dict[str, Any] = {}
    
    def _send_json(self, status_code: int, data: Dict[str, Any]) -> None:
        """Send JSON response with CORS headers."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def _send_html(self, status_code: int, html: str) -> None:
        """Send HTML response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def _send_error(self, status_code: int, message: str) -> None:
        """Send error response."""
        self._send_json(status_code, {"error": message})
    
    def _parse_body(self) -> Dict[str, Any]:
        """Parse JSON body from request."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {}
    
    def do_OPTIONS(self) -> None:
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self) -> None:
        """Handle GET requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)
        
        # GET /api/health - Health check
        if path == '/api/health':
            self._send_json(200, {
                "status": "ok",
                "service": "ReportAgent API",
                "version": "1.0.0"
            })
        
        # GET /api/reports - List all reports
        elif path == '/api/reports':
            if self.report_agent:
                limit = int(query.get('limit', [100])[0])
                reports = self.report_agent.list_reports(limit)
                self._send_json(200, {
                    "reports": reports,
                    "count": len(reports)
                })
            else:
                self._send_error(500, "ReportAgent not initialized")
        
        # GET /api/reports/{id} - Get report by ID
        elif path.startswith('/api/reports/') and len(path.split('/')) == 4:
            report_id = path.split('/')[-1]
            format = query.get('format', ['json'])[0]
            
            if self.report_agent:
                content = self.report_agent.get_report(report_id, format)
                if content:
                    if format == 'html':
                        self._send_html(200, content)
                    else:
                        self._send_json(200, {
                            "report_id": report_id,
                            "format": format,
                            "content": content if format != 'json' else json.loads(content)
                        })
                else:
                    self._send_error(404, f"Report {report_id} not found")
            else:
                self._send_error(500, "ReportAgent not initialized")
        
        # GET /api/reports/{id}/html - Get HTML report directly
        elif path.startswith('/api/reports/') and path.endswith('/html'):
            report_id = path.split('/')[-2]
            
            if self.report_agent:
                content = self.report_agent.get_report(report_id, 'html')
                if content:
                    self._send_html(200, content)
                else:
                    self._send_error(404, f"Report {report_id} not found")
            else:
                self._send_error(500, "ReportAgent not initialized")
        
        # GET /api/skills - List available skills
        elif path == '/api/skills':
            from report_agent import SkillIntegrator
            integrator = SkillIntegrator()
            skills = []
            for name, config in integrator.SKILL_PATTERNS.items():
                skills.append({
                    "name": name,
                    "description": config["description"],
                    "emoji": config["emoji"]
                })
            self._send_json(200, {"skills": skills})
        
        # GET / - API info
        elif path == '/':
            self._send_json(200, {
                "service": "Swimming Pauls ReportAgent API",
                "version": "1.0.0",
                "endpoints": {
                    "GET /api/health": "Health check",
                    "GET /api/reports": "List all reports",
                    "GET /api/reports/{id}": "Get report by ID",
                    "GET /api/reports/{id}/html": "Get HTML report",
                    "POST /api/reports/generate": "Generate new report from simulation",
                    "POST /api/simulate": "Run simulation and generate report",
                    "GET /api/skills": "List available skills",
                }
            })
        
        else:
            self._send_error(404, "Endpoint not found")
    
    def do_POST(self) -> None:
        """Handle POST requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._parse_body()
        
        # POST /api/reports/generate - Generate report from simulation result
        if path == '/api/reports/generate':
            if not self.report_agent:
                self._send_error(500, "ReportAgent not initialized")
                return
            
            # Parse simulation result from body
            sim_data = body.get('simulation_result')
            agents_data = body.get('agents', [])
            topic = body.get('topic')
            title = body.get('title')
            
            if not sim_data:
                self._send_error(400, "Missing simulation_result")
                return
            
            try:
                # Reconstruct simulation result (simplified)
                from simulation import SimulationResult, SimulationRound
                from agent import AgentPrediction
                
                rounds = []
                for r in sim_data.get('rounds', []):
                    predictions = [
                        AgentPrediction(**p) for p in r.get('predictions', [])
                    ]
                    rounds.append(SimulationRound(
                        round_number=r['round_number'],
                        timestamp=r.get('timestamp', 0),
                        market_data=r.get('market_data', {}),
                        predictions=predictions,
                        consensus=r.get('consensus', {}),
                    ))
                
                result = SimulationResult(
                    start_time=sim_data.get('start_time', 0),
                    end_time=sim_data.get('end_time', 0),
                    rounds=rounds,
                    final_consensus=sim_data.get('final_consensus', {}),
                    agent_performances=sim_data.get('agent_performances', {}),
                )
                
                # Create agents (simplified)
                agents = create_agent_team()
                
                # Generate report
                async def generate():
                    return await self.report_agent.generate_and_save(
                        result, agents, topic, title
                    )
                
                report, paths = asyncio.run(generate())
                
                self._send_json(200, {
                    "success": True,
                    "report_id": report.metadata.report_id,
                    "title": report.metadata.title,
                    "consensus": report.consensus.to_dict(),
                    "paths": paths,
                    "urls": {
                        "json": f"/api/reports/{report.metadata.report_id}",
                        "html": f"/api/reports/{report.metadata.report_id}/html",
                        "markdown": f"/api/reports/{report.metadata.report_id}?format=markdown",
                    }
                })
                
            except Exception as e:
                self._send_error(500, f"Report generation failed: {str(e)}")
        
        # POST /api/simulate - Run simulation and generate report
        elif path == '/api/simulate':
            if not self.report_agent:
                self._send_error(500, "ReportAgent not initialized")
                return
            
            topic = body.get('topic', 'General')
            title = body.get('title', f'Swimming Pauls Report - {topic}')
            rounds = body.get('rounds', 10)
            delay = body.get('delay', 0.5)
            
            try:
                async def run_and_report():
                    # Create agents and run simulation
                    agents = create_agent_team()
                    runner = SimulationRunner(agents=agents, rounds=rounds, round_delay=delay)
                    result = await runner.run()
                    
                    # Generate and save report
                    report, paths = await self.report_agent.generate_and_save(
                        result, agents, topic, title
                    )
                    
                    return report, paths, result
                
                report, paths, result = asyncio.run(run_and_report())
                
                self._send_json(200, {
                    "success": True,
                    "report_id": report.metadata.report_id,
                    "title": report.metadata.title,
                    "consensus": report.consensus.to_dict(),
                    "simulation": {
                        "rounds": len(result.rounds),
                        "duration": result.end_time - result.start_time,
                    },
                    "paths": paths,
                    "urls": {
                        "json": f"/api/reports/{report.metadata.report_id}",
                        "html": f"/api/reports/{report.metadata.report_id}/html",
                        "markdown": f"/api/reports/{report.metadata.report_id}?format=markdown",
                    }
                })
                
            except Exception as e:
                self._send_error(500, f"Simulation failed: {str(e)}")
        
        else:
            self._send_error(404, "Endpoint not found")
    
    def do_DELETE(self) -> None:
        """Handle DELETE requests."""
        parsed = urlparse(self.path)
        path = parsed.path
        
        # DELETE /api/reports/{id} - Delete report
        if path.startswith('/api/reports/') and len(path.split('/')) == 4:
            report_id = path.split('/')[-1]
            
            if self.report_agent:
                success = self.report_agent.storage.delete_report(report_id)
                if success:
                    self._send_json(200, {
                        "success": True,
                        "message": f"Report {report_id} deleted"
                    })
                else:
                    self._send_error(404, f"Report {report_id} not found")
            else:
                self._send_error(500, "ReportAgent not initialized")
        
        else:
            self._send_error(404, "Endpoint not found")
    
    def log_message(self, format, *args) -> None:
        """Suppress default logging."""
        pass


class ReportAPIServer:
    """
    HTTP API server for ReportAgent.
    
    Provides endpoints for:
    - Generating reports from simulations
    - Retrieving reports in various formats
    - Listing and managing reports
    
    Example:
        server = ReportAPIServer(port=8080)
        server.start()
        # Access API at http://localhost:8080
    """
    
    def __init__(
        self,
        port: int = 8080,
        host: str = 'localhost',
        storage_dir: Optional[str] = None,
    ):
        self.port = port
        self.host = host
        self.storage_dir = storage_dir
        self.server: Optional[HTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.report_agent = ReportAgent(storage_dir=storage_dir)
        self._running = False
    
    def start(self, blocking: bool = False) -> None:
        """
        Start the API server.
        
        Args:
            blocking: If True, block until server stops
        """
        # Set up handler with report agent
        ReportAPIHandler.report_agent = self.report_agent
        
        self.server = HTTPServer((self.host, self.port), ReportAPIHandler)
        self._running = True
        
        if blocking:
            print(f"📊 ReportAgent API server running at http://{self.host}:{self.port}")
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.stop()
        else:
            self.thread = threading.Thread(target=self._serve)
            self.thread.daemon = True
            self.thread.start()
            print(f"📊 ReportAgent API server started at http://{self.host}:{self.port}")
    
    def _serve(self) -> None:
        """Run server in thread."""
        try:
            self.server.serve_forever()
        except Exception:
            pass
    
    def stop(self) -> None:
        """Stop the API server."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self._running = False
            print("📊 ReportAgent API server stopped")
    
    def is_running(self) -> bool:
        """Check if server is running."""
        return self._running


def start_report_api(
    port: int = 8080,
    host: str = 'localhost',
    storage_dir: Optional[str] = None,
) -> ReportAPIServer:
    """
    Start the ReportAgent API server.
    
    Args:
        port: Port to listen on
        host: Host to bind to
        storage_dir: Directory for report storage
        
    Returns:
        ReportAPIServer instance
    """
    server = ReportAPIServer(port=port, host=host, storage_dir=storage_dir)
    server.start()
    return server


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Swimming Pauls ReportAgent API Server')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on')
    parser.add_argument('--host', type=str, default='localhost', help='Host to bind to')
    parser.add_argument('--storage', type=str, default=None, help='Storage directory')
    
    args = parser.parse_args()
    
    server = start_report_api(port=args.port, host=args.host, storage_dir=args.storage)
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        server.stop()
        print("\n👋 Goodbye!")