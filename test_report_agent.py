"""
Tests for ReportAgent System
"""

import os
import sys
import json
import asyncio
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import unittest
from unittest.mock import Mock, patch, AsyncMock

# Import with proper handling for both module and direct execution
try:
    from report_agent import (
        ReportAgent,
        ReportCompiler,
        ReportStorage,
        SkillIntegrator,
        ReportFormatter,
        Report,
        ReportMetadata,
        ConsensusSummary,
        AgentReasoning,
        SkillData,
        ReportFormat,
        quick_report,
    )
    from simulation import SimulationResult, SimulationRound, SimulationRunner
    from agent import Agent, AgentPrediction, PersonaType, create_agent_team
except ImportError:
    # Fallback for when running as script
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    exec(open("report_agent.py").read())
    exec(open("simulation.py").read())
    exec(open("agent.py").read())


class TestSkillIntegrator(unittest.TestCase):
    """Test SkillIntegrator functionality."""
    
    def setUp(self):
        self.integrator = SkillIntegrator()
    
    def test_detect_relevant_skills(self):
        """Test skill detection based on topic."""
        # Crypto topic
        skills = self.integrator.detect_relevant_skills("bitcoin price prediction")
        self.assertIn("crypto-price", skills)
        
        # Stock topic
        skills = self.integrator.detect_relevant_skills("stock market analysis")
        self.assertIn("yahoo-finance", skills)
        
        # News topic
        skills = self.integrator.detect_relevant_skills("latest news headlines")
        self.assertIn("news-summarizer", skills)
    
    async def test_mock_skill_call(self):
        """Test mock skill calls."""
        result = await self.integrator._mock_skill_call("crypto-price", "BTC")
        
        self.assertIn("symbol", result)
        self.assertIn("price", result)
        self.assertIn("change_24h", result)
    
    async def test_enrich_topic(self):
        """Test topic enrichment."""
        results = await self.integrator.enrich_topic("crypto market analysis")
        
        self.assertIsInstance(results, list)
        # Should have at least one skill result
        if results:
            self.assertIsInstance(results[0], SkillData)


class TestReportCompiler(unittest.TestCase):
    """Test ReportCompiler functionality."""
    
    def setUp(self):
        self.compiler = ReportCompiler()
        
        # Create mock simulation result
        self.mock_result = Mock(spec=SimulationResult)
        self.mock_result.start_time = 1000.0
        self.mock_result.end_time = 1100.0
        self.mock_result.final_consensus = {
            "direction": "bullish",
            "sentiment": 0.65,
            "consistency": 0.75,
            "bullish_rounds": 7,
            "bearish_rounds": 2,
            "neutral_rounds": 1,
        }
        self.mock_result.agent_performances = {}
        
        # Create mock rounds
        mock_round = Mock(spec=SimulationRound)
        mock_round.round_number = 1
        mock_round.timestamp = 1000.0
        mock_round.market_data = {"price_trend": 0.5}
        mock_round.consensus = {
            "direction": "bullish",
            "confidence": 0.8,
            "sentiment": 0.6,
            "strength": "strong",
            "agreement_ratio": 0.75,
        }
        
        mock_prediction = Mock(spec=AgentPrediction)
        mock_prediction.agent_id = "agent1"
        mock_prediction.direction = "bullish"
        mock_prediction.confidence = 0.85
        mock_prediction.magnitude = 0.5
        mock_prediction.reasoning = "Test reasoning"
        mock_prediction.timestamp = 1000.0
        
        mock_round.predictions = [mock_prediction]
        self.mock_result.rounds = [mock_round]
        
        # Create mock agents
        self.mock_agent = Mock(spec=Agent)
        self.mock_agent.id = "agent1"
        self.mock_agent.name = "Test Agent"
        self.mock_agent.persona = PersonaType.ANALYST
        self.mock_agent.memory = Mock()
        self.mock_agent.memory.accuracy_score = 0.75
        
        self.agents = [self.mock_agent]
    
    def test_extract_consensus(self):
        """Test consensus extraction."""
        consensus = self.compiler.extract_consensus(self.mock_result)
        
        self.assertIsInstance(consensus, ConsensusSummary)
        self.assertEqual(consensus.direction, "bullish")
        self.assertEqual(consensus.bullish_rounds, 7)
        self.assertEqual(consensus.bearish_rounds, 2)
    
    def test_calculate_strength(self):
        """Test strength calculation."""
        self.assertEqual(
            self.compiler._calculate_strength({"consistency": 0.8}),
            "strong"
        )
        self.assertEqual(
            self.compiler._calculate_strength({"consistency": 0.5}),
            "moderate"
        )
        self.assertEqual(
            self.compiler._calculate_strength({"consistency": 0.3}),
            "weak"
        )
    
    def test_extract_agent_reasonings(self):
        """Test agent reasoning extraction."""
        reasonings = self.compiler.extract_agent_reasonings(self.mock_result, self.agents)
        
        self.assertEqual(len(reasonings), 1)
        self.assertEqual(reasonings[0].agent_name, "Test Agent")
        self.assertEqual(reasonings[0].direction, "bullish")
    
    def test_generate_insights(self):
        """Test insight generation."""
        consensus = ConsensusSummary(
            direction="bullish",
            confidence=0.75,
            sentiment=0.65,
            strength="strong",
            consistency=0.75,
            bullish_rounds=7,
            bearish_rounds=2,
            neutral_rounds=1,
            total_rounds=10,
            agreement_ratio=0.75,
        )
        
        reasonings = [
            AgentReasoning(
                agent_id="agent1",
                agent_name="Test Agent",
                persona="analyst",
                direction="bullish",
                confidence=0.85,
                magnitude=0.5,
                reasoning="Test",
                accuracy_score=0.75,
            )
        ]
        
        insights = self.compiler.generate_insights(consensus, reasonings, [])
        
        self.assertIsInstance(insights, list)
        self.assertTrue(len(insights) > 0)


class TestReportFormatter(unittest.TestCase):
    """Test ReportFormatter functionality."""
    
    def setUp(self):
        # Create a sample report
        self.report = Report(
            metadata=ReportMetadata(
                report_id="test123",
                title="Test Report",
                created_at=datetime.utcnow().isoformat(),
                format="report",
                simulation_duration=10.5,
                num_agents=5,
                num_rounds=10,
                topic="Test Topic",
                tags=["bullish", "strong"],
            ),
            consensus=ConsensusSummary(
                direction="bullish",
                confidence=0.75,
                sentiment=0.65,
                strength="strong",
                consistency=0.75,
                bullish_rounds=7,
                bearish_rounds=2,
                neutral_rounds=1,
                total_rounds=10,
                agreement_ratio=0.75,
            ),
            agent_reasonings=[
                AgentReasoning(
                    agent_id="agent1",
                    agent_name="Test Agent",
                    persona="analyst",
                    direction="bullish",
                    confidence=0.85,
                    magnitude=0.5,
                    reasoning="Strong bullish signals detected",
                    accuracy_score=0.75,
                )
            ],
            skill_data=[
                SkillData(
                    skill_name="crypto-price",
                    query="BTC",
                    result={"price": 45000, "change_24h": 5.2},
                    timestamp=1000.0,
                    success=True,
                )
            ],
            visualizations={"chart": "path/to/chart.png"},
            insights=["Test insight"],
            raw_data={},
        )
    
    def test_to_markdown(self):
        """Test Markdown formatting."""
        md = ReportFormatter.to_markdown(self.report)
        
        self.assertIn("# Test Report", md)
        self.assertIn("test123", md)
        self.assertIn("BULLISH", md)
        self.assertIn("Strong bullish signals detected", md)
        self.assertIn("crypto-price", md)
    
    def test_to_html(self):
        """Test HTML formatting."""
        html = ReportFormatter.to_html(self.report)
        
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("Test Report", html)
        self.assertIn("bullish", html)
    
    def test_to_json(self):
        """Test JSON formatting."""
        json_str = ReportFormatter.to_json(self.report)
        
        data = json.loads(json_str)
        self.assertEqual(data["metadata"]["report_id"], "test123")
        self.assertEqual(data["consensus"]["direction"], "bullish")


class TestReportStorage(unittest.TestCase):
    """Test ReportStorage functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.storage = ReportStorage(base_dir=self.temp_dir)
        
        # Create sample report
        self.report = Report(
            metadata=ReportMetadata(
                report_id="test456",
                title="Storage Test",
                created_at=datetime.utcnow().isoformat(),
                format="report",
                simulation_duration=5.0,
                num_agents=3,
                num_rounds=5,
                topic="Test",
            ),
            consensus=ConsensusSummary(
                direction="bearish",
                confidence=0.6,
                sentiment=-0.4,
                strength="moderate",
                consistency=0.6,
                bullish_rounds=1,
                bearish_rounds=3,
                neutral_rounds=1,
                total_rounds=5,
                agreement_ratio=0.6,
            ),
            agent_reasonings=[],
            skill_data=[],
            visualizations={},
            insights=[],
            raw_data={},
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_save_report(self):
        """Test saving a report."""
        paths = self.storage.save_report(self.report)
        
        self.assertIn("report_id", paths)
        self.assertIn("markdown", paths)
        self.assertIn("html", paths)
        self.assertIn("json", paths)
        
        # Check files exist
        self.assertTrue(Path(paths["markdown"]).exists())
        self.assertTrue(Path(paths["html"]).exists())
        self.assertTrue(Path(paths["json"]).exists())
    
    def test_get_report(self):
        """Test retrieving a report."""
        self.storage.save_report(self.report)
        
        # Get markdown
        md_content = self.storage.get_report("test456", "markdown")
        self.assertIsNotNone(md_content)
        self.assertIn("Storage Test", md_content)
        
        # Get HTML
        html_content = self.storage.get_report("test456", "html")
        self.assertIsNotNone(html_content)
        
        # Get JSON
        json_content = self.storage.get_report("test456", "json")
        self.assertIsNotNone(json_content)
    
    def test_list_reports(self):
        """Test listing reports."""
        self.storage.save_report(self.report)
        
        reports = self.storage.list_reports()
        self.assertEqual(len(reports), 1)
        self.assertEqual(reports[0]["report_id"], "test456")
    
    def test_delete_report(self):
        """Test deleting a report."""
        paths = self.storage.save_report(self.report)
        
        # Delete
        success = self.storage.delete_report("test456")
        self.assertTrue(success)
        
        # Check files removed
        self.assertFalse(Path(paths["markdown"]).exists())


class TestReportAgent(unittest.TestCase):
    """Test ReportAgent main functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.agent = ReportAgent(storage_dir=self.temp_dir)
        
        # Create mock simulation
        self.mock_agents = create_agent_team()
        
        # Create simple simulation result
        self.mock_result = Mock(spec=SimulationResult)
        self.mock_result.start_time = 1000.0
        self.mock_result.end_time = 1010.0
        self.mock_result.final_consensus = {
            "direction": "bullish",
            "sentiment": 0.6,
            "consistency": 0.7,
            "bullish_rounds": 5,
            "bearish_rounds": 2,
            "neutral_rounds": 3,
        }
        self.mock_result.agent_performances = {}
        
        mock_round = Mock(spec=SimulationRound)
        mock_round.round_number = 1
        mock_round.timestamp = 1000.0
        mock_round.market_data = {}
        mock_round.consensus = {
            "direction": "bullish",
            "confidence": 0.8,
            "sentiment": 0.6,
            "strength": "strong",
        }
        
        # Create actual predictions with AgentPrediction
        predictions = []
        for agent in self.mock_agents[:3]:
            pred = AgentPrediction(
                agent_id=agent.id,
                direction="bullish",
                confidence=0.8,
                magnitude=0.5,
                reasoning=f"{agent.name} sees bullish momentum",
                timestamp=1000.0,
            )
            predictions.append(pred)
        
        mock_round.predictions = predictions
        self.mock_result.rounds = [mock_round]
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    async def test_generate_report(self):
        """Test report generation."""
        report = await self.agent.generate_report(
            self.mock_result, self.mock_agents, topic="BTC"
        )
        
        self.assertIsInstance(report, Report)
        self.assertEqual(report.consensus.direction, "bullish")
        self.assertTrue(len(report.agent_reasonings) > 0)
        self.assertIsNotNone(report.metadata.report_id)
    
    def test_save_report(self):
        """Test saving a generated report."""
        # First generate the report
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(
            self.agent.generate_report(self.mock_result, self.mock_agents)
        )
        
        # Save it
        paths = self.agent.save_report(report)
        
        self.assertIn("report_id", paths)
        self.assertIn("html", paths)
    
    def test_get_report(self):
        """Test report retrieval."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(
            self.agent.generate_report(self.mock_result, self.mock_agents)
        )
        paths = self.agent.save_report(report)
        report_id = paths["report_id"]
        
        # Retrieve
        content = self.agent.get_report(report_id, "markdown")
        self.assertIsNotNone(content)
    
    def test_list_reports(self):
        """Test listing generated reports."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(
            self.agent.generate_report(self.mock_result, self.mock_agents)
        )
        self.agent.save_report(report)
        
        reports = self.agent.list_reports()
        self.assertTrue(len(reports) >= 1)
    
    def test_export_report(self):
        """Test report export."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        report = loop.run_until_complete(
            self.agent.generate_report(self.mock_result, self.mock_agents)
        )
        
        # Export as Markdown
        md = self.agent.export_report(report, ReportFormat.MARKDOWN)
        self.assertIn(report.metadata.report_id, md)
        
        # Export as HTML
        html = self.agent.export_report(report, ReportFormat.HTML)
        self.assertIn("<!DOCTYPE html>", html)
        
        # Export as JSON
        json_str = self.agent.export_report(report, ReportFormat.JSON)
        data = json.loads(json_str)
        self.assertEqual(data["metadata"]["report_id"], report.metadata.report_id)


class TestIntegration(unittest.TestCase):
    """Integration tests with actual Swimming Pauls."""
    
    async def async_test_full_workflow(self):
        """Test complete workflow from simulation to report."""
        # Create agents and run simulation
        agents = create_agent_team()
        runner = SimulationRunner(agents=agents, rounds=3, round_delay=0.01)
        result = await runner.run()
        
        # Create temporary storage
        temp_dir = tempfile.mkdtemp()
        try:
            agent = ReportAgent(storage_dir=temp_dir)
            
            # Generate and save report
            report, paths = await agent.generate_and_save(
                result, agents, topic="Test Integration"
            )
            
            # Verify report
            self.assertIsNotNone(report.metadata.report_id)
            self.assertEqual(report.metadata.num_agents, len(agents))
            self.assertEqual(report.metadata.num_rounds, 3)
            
            # Verify files exist
            self.assertTrue(Path(paths["html"]).exists())
            self.assertTrue(Path(paths["markdown"]).exists())
            
            # Retrieve and verify
            html_content = agent.get_report(report.metadata.report_id, "html")
            self.assertIsNotNone(html_content)
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_full_workflow(self):
        """Synchronous wrapper for async test."""
        asyncio.run(self.async_test_full_workflow())


class TestAPIEndpoints(unittest.TestCase):
    """Test API endpoints."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_api_handler_init(self):
        """Test API handler initialization."""
        from report_api import ReportAPIHandler, ReportAPIServer
        
        server = ReportAPIServer(port=0, storage_dir=self.temp_dir)
        self.assertIsNotNone(server.report_agent)


def run_async_tests():
    """Run async tests."""
    loop = asyncio.get_event_loop()
    
    # Test skill integrator
    integrator = SkillIntegrator()
    
    async def test_skills():
        result = await integrator._mock_skill_call("crypto-price", "BTC")
        assert "price" in result
        print("✓ Skill integrator test passed")
    
    loop.run_until_complete(test_skills())


if __name__ == "__main__":
    # Run async tests first
    run_async_tests()
    
    # Run unittest suite
    unittest.main(verbosity=2)