"""
Tests for Dual Platform Simulation System

Run tests with:
    python -m pytest test_dual_platform.py -v
    python test_dual_platform.py  # Run directly
"""
import asyncio
import sys
import os
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dual_platform import (
    PlatformType,
    PlatformConfig,
    PlatformResult,
    DualPlatformConsensus,
    DualPlatformResult,
    PlatformAgentFactory,
    DualPlatformSimulator,
    DualPlatformBuilder,
    DualPlatformChatInterface,
    quick_dual_simulation,
)
from agent import Agent, PersonaType
from simulation import SimulationResult, SimulationRound


class TestPlatformConfig(unittest.TestCase):
    """Test PlatformConfig dataclass."""
    
    def test_valid_config(self):
        """Test creating a valid platform config."""
        config = PlatformConfig(
            name="Test Platform",
            platform_type=PlatformType.BALANCED,
            agent_count=5,
            rounds=10,
        )
        self.assertEqual(config.name, "Test Platform")
        self.assertEqual(config.platform_type, PlatformType.BALANCED)
        self.assertEqual(config.agent_count, 5)
        self.assertEqual(config.rounds, 10)
        self.assertEqual(config.platform_weight, 1.0)
    
    def test_invalid_agent_count(self):
        """Test validation of agent count."""
        with self.assertRaises(ValueError) as context:
            PlatformConfig(
                name="Invalid",
                platform_type=PlatformType.BALANCED,
                agent_count=0,
            )
        self.assertIn("agent_count", str(context.exception).lower())
    
    def test_invalid_rounds(self):
        """Test validation of rounds."""
        with self.assertRaises(ValueError) as context:
            PlatformConfig(
                name="Invalid",
                platform_type=PlatformType.BALANCED,
                rounds=0,
            )
        self.assertIn("rounds", str(context.exception).lower())
    
    def test_invalid_consensus_threshold(self):
        """Test validation of consensus threshold."""
        with self.assertRaises(ValueError) as context:
            PlatformConfig(
                name="Invalid",
                platform_type=PlatformType.BALANCED,
                consensus_threshold=1.5,
            )
        self.assertIn("consensus_threshold", str(context.exception).lower())
    
    def test_invalid_platform_weight(self):
        """Test validation of platform weight."""
        with self.assertRaises(ValueError) as context:
            PlatformConfig(
                name="Invalid",
                platform_type=PlatformType.BALANCED,
                platform_weight=0,
            )
        self.assertIn("platform_weight", str(context.exception).lower())


class TestPlatformAgentFactory(unittest.TestCase):
    """Test PlatformAgentFactory."""
    
    def test_create_conservative_team(self):
        """Test creating conservative agent team."""
        team = PlatformAgentFactory.create_conservative_team(count=3)
        self.assertEqual(len(team), 3)
        self.assertIsInstance(team[0], Agent)
        # Conservative teams should have risk-averse personas
        persona_names = [agent.persona.value for agent in team]
        self.assertIn("hedgie", persona_names)
        self.assertIn("skeptic", persona_names)
    
    def test_create_aggressive_team(self):
        """Test creating aggressive agent team."""
        team = PlatformAgentFactory.create_aggressive_team(count=3)
        self.assertEqual(len(team), 3)
        self.assertIsInstance(team[0], Agent)
        # Aggressive teams should have risk-tolerant personas
        persona_names = [agent.persona.value for agent in team]
        self.assertIn("trader", persona_names)
        self.assertIn("visionary", persona_names)
    
    def test_create_balanced_team(self):
        """Test creating balanced agent team."""
        team = PlatformAgentFactory.create_balanced_team(count=5)
        self.assertEqual(len(team), 5)
        # Balanced team should have diverse personas
        persona_names = set(agent.persona.value for agent in team)
        self.assertGreaterEqual(len(persona_names), 3)
    
    def test_create_film_industry_team(self):
        """Test creating film industry agent team."""
        team = PlatformAgentFactory.create_film_industry_team(count=5)
        self.assertEqual(len(team), 5)
        # All should be film industry personas
        film_personas = [
            "producer", "director", "screenwriter", 
            "studio_exec", "indie_filmmaker"
        ]
        for agent in team:
            self.assertIn(agent.persona.value, film_personas)
    
    def test_create_team_by_type(self):
        """Test create_team method with different types."""
        conservative = PlatformAgentFactory.create_team(PlatformType.CONSERVATIVE, 3)
        aggressive = PlatformAgentFactory.create_team(PlatformType.AGGRESSIVE, 3)
        balanced = PlatformAgentFactory.create_team(PlatformType.BALANCED, 3)
        film = PlatformAgentFactory.create_team(PlatformType.FILM_INDUSTRY, 3)
        
        self.assertEqual(len(conservative), 3)
        self.assertEqual(len(aggressive), 3)
        self.assertEqual(len(balanced), 3)
        self.assertEqual(len(film), 3)


class TestDualPlatformConsensus(unittest.TestCase):
    """Test DualPlatformConsensus."""
    
    def test_to_dict(self):
        """Test converting consensus to dictionary."""
        consensus = DualPlatformConsensus(
            direction="bullish",
            confidence=0.85,
            sentiment=0.6,
            strength="strong",
            platform_consensus={"bullish": 0.7, "bearish": 0.2, "neutral": 0.1},
            cross_platform_agreement=0.8,
            platform_count=3,
            bullish_platforms=2,
            bearish_platforms=1,
            neutral_platforms=0,
            weighted_confidence=0.82,
            platform_divergence=0.15,
        )
        
        d = consensus.to_dict()
        self.assertEqual(d['direction'], 'bullish')
        self.assertEqual(d['confidence'], 0.85)
        self.assertEqual(d['platform_count'], 3)
        self.assertIn('platform_consensus', d)


class TestDualPlatformResult(unittest.TestCase):
    """Test DualPlatformResult."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock platform results
        config1 = PlatformConfig(name="Platform 1", platform_type=PlatformType.BALANCED)
        config2 = PlatformConfig(name="Platform 2", platform_type=PlatformType.BALANCED)
        
        sim_result = SimulationResult(
            start_time=0,
            end_time=1,
            rounds=[],
            final_consensus={'direction': 'bullish'},
            agent_performances={},
        )
        
        self.platform_results = [
            PlatformResult(platform_config=config1, simulation_result=sim_result, success=True),
            PlatformResult(platform_config=config2, simulation_result=sim_result, success=True),
        ]
        
        self.dual_consensus = DualPlatformConsensus(
            direction="bullish",
            confidence=0.8,
            sentiment=0.5,
            strength="strong",
            platform_consensus={"bullish": 1.0, "bearish": 0, "neutral": 0},
            cross_platform_agreement=1.0,
            platform_count=2,
        )
    
    def test_successful_platforms(self):
        """Test filtering successful platforms."""
        result = DualPlatformResult(
            platform_results=self.platform_results,
            dual_consensus=self.dual_consensus,
        )
        
        successful = result.successful_platforms
        self.assertEqual(len(successful), 2)
        
        # Add a failed result
        failed_config = PlatformConfig(name="Failed", platform_type=PlatformType.BALANCED)
        failed_sim = SimulationResult(0, 0, [], {}, {})
        failed_result = PlatformResult(
            platform_config=failed_config,
            simulation_result=failed_sim,
            success=False,
            error_message="Test error",
        )
        
        result.platform_results.append(failed_result)
        self.assertEqual(len(result.successful_platforms), 2)
        self.assertEqual(len(result.failed_platforms), 1)
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        result = DualPlatformResult(
            platform_results=self.platform_results,
            dual_consensus=self.dual_consensus,
            execution_time=1.5,
        )
        
        d = result.to_dict()
        self.assertEqual(d['execution_time'], 1.5)
        self.assertEqual(d['dual_consensus']['direction'], 'bullish')
        self.assertEqual(len(d['platforms']), 2)
    
    def test_to_json(self):
        """Test converting to JSON."""
        result = DualPlatformResult(
            platform_results=self.platform_results,
            dual_consensus=self.dual_consensus,
        )
        
        json_str = result.to_json()
        self.assertIsInstance(json_str, str)
        self.assertIn('bullish', json_str)


class TestDualPlatformSimulator(unittest.TestCase):
    """Test DualPlatformSimulator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.platforms = [
            PlatformConfig(
                name="Test Platform 1",
                platform_type=PlatformType.BALANCED,
                agent_count=3,
                rounds=3,
                round_delay=0.01,
            ),
            PlatformConfig(
                name="Test Platform 2",
                platform_type=PlatformType.BALANCED,
                agent_count=3,
                rounds=3,
                round_delay=0.01,
            ),
        ]
    
    def test_initialization(self):
        """Test simulator initialization."""
        simulator = DualPlatformSimulator(self.platforms)
        self.assertEqual(len(simulator.platform_configs), 2)
        self.assertEqual(simulator.max_workers, 2)
        self.assertFalse(simulator.use_processes)
    
    def test_get_platform_by_name(self):
        """Test getting platform by name."""
        simulator = DualPlatformSimulator(self.platforms)
        
        # Create mock results
        sim_result = SimulationResult(0, 1, [], {}, {})
        simulator.results = [
            PlatformResult(platform_config=self.platforms[0], simulation_result=sim_result),
        ]
        
        result = simulator.get_platform_by_name("Test Platform 1")
        self.assertIsNotNone(result)
        self.assertEqual(result.platform_config.name, "Test Platform 1")
        
        result = simulator.get_platform_by_name("Non-existent")
        self.assertIsNone(result)
    
    def test_consensus_report_format(self):
        """Test consensus report generation."""
        simulator = DualPlatformSimulator(self.platforms)
        
        # Create mock results with proper consensus
        sim_result = SimulationResult(
            start_time=0,
            end_time=1,
            rounds=[],
            final_consensus={
                'direction': 'bullish',
                'sentiment': 0.5,
                'consistency': 0.8,
                'bullish_rounds': 2,
                'bearish_rounds': 0,
                'neutral_rounds': 1,
            },
            agent_performances={'agent1': 0.8},
        )
        
        simulator.results = [
            PlatformResult(
                platform_config=self.platforms[0],
                simulation_result=sim_result,
                execution_time=0.5,
                success=True,
            ),
            PlatformResult(
                platform_config=self.platforms[1],
                simulation_result=sim_result,
                execution_time=0.6,
                success=True,
            ),
        ]
        
        report = simulator.get_consensus_report()
        self.assertIn("DUAL PLATFORM CONSENSUS", report)
        self.assertIn("Test Platform 1", report)
        self.assertIn("Test Platform 2", report)


class TestDualPlatformBuilder(unittest.TestCase):
    """Test DualPlatformBuilder."""
    
    def test_builder_chain(self):
        """Test builder method chaining."""
        builder = DualPlatformBuilder()
        result = builder.add_balanced_platform().add_conservative_platform().add_aggressive_platform()
        self.assertIsInstance(result, DualPlatformBuilder)
        self.assertEqual(len(builder.platforms), 3)
    
    def test_add_platform_with_custom_params(self):
        """Test adding platform with custom parameters."""
        builder = DualPlatformBuilder()
        builder.add_platform(
            name="Custom",
            platform_type=PlatformType.CUSTOM,
            agent_count=10,
            rounds=20,
            weight=2.0,
        )
        
        self.assertEqual(len(builder.platforms), 1)
        config = builder.platforms[0]
        self.assertEqual(config.name, "Custom")
        self.assertEqual(config.agent_count, 10)
        self.assertEqual(config.rounds, 20)
        self.assertEqual(config.platform_weight, 2.0)
    
    def test_build_raises_without_platforms(self):
        """Test that build raises error without platforms."""
        builder = DualPlatformBuilder()
        with self.assertRaises(ValueError) as context:
            builder.build()
        self.assertIn("at least one platform", str(context.exception).lower())
    
    def test_build_creates_simulator(self):
        """Test that build creates a simulator."""
        builder = DualPlatformBuilder()
        builder.add_balanced_platform().add_conservative_platform()
        
        simulator = builder.build()
        self.assertIsInstance(simulator, DualPlatformSimulator)
        self.assertEqual(len(simulator.platform_configs), 2)


class TestDualPlatformChatInterface(unittest.TestCase):
    """Test DualPlatformChatInterface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.chat_interface = DualPlatformChatInterface()
        
        # Create mock result
        config1 = PlatformConfig(name="Conservative", platform_type=PlatformType.CONSERVATIVE)
        config2 = PlatformConfig(name="Aggressive", platform_type=PlatformType.AGGRESSIVE)
        
        sim_result = SimulationResult(0, 1, [], {}, {})
        
        platform_results = [
            PlatformResult(platform_config=config1, simulation_result=sim_result, success=True),
            PlatformResult(platform_config=config2, simulation_result=sim_result, success=True),
        ]
        
        dual_consensus = DualPlatformConsensus(
            direction="bullish",
            confidence=0.85,
            sentiment=0.6,
            strength="strong",
            platform_consensus={"bullish": 1.0, "bearish": 0, "neutral": 0},
            cross_platform_agreement=0.9,
            platform_count=2,
        )
        
        self.dual_result = DualPlatformResult(
            platform_results=platform_results,
            dual_consensus=dual_consensus,
        )
    
    def test_format_chat_response(self):
        """Test formatting response for chat."""
        response = self.chat_interface.format_chat_response(self.dual_result)
        
        self.assertIn("DUAL PLATFORM CONSENSUS", response)
        self.assertIn("BULLISH", response)
        self.assertIn("85%", response)
        self.assertIn("Conservative", response)
        self.assertIn("Aggressive", response)
    
    def test_save_and_get_result(self):
        """Test saving and retrieving result."""
        # Save result
        result_id = self.chat_interface.save_dual_result(self.dual_result)
        self.assertIsInstance(result_id, str)
        self.assertEqual(len(result_id), 8)
        
        # Retrieve result
        retrieved = self.chat_interface.get_dual_result(result_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.dual_consensus.direction, "bullish")


class TestIntegration(unittest.TestCase):
    """Integration tests for dual platform system."""
    
    async def _run_simulation(self):
        """Helper to run async simulation."""
        platforms = [
            PlatformConfig(
                name="Small Test 1",
                platform_type=PlatformType.BALANCED,
                agent_count=2,
                rounds=2,
                round_delay=0.001,
            ),
            PlatformConfig(
                name="Small Test 2",
                platform_type=PlatformType.BALANCED,
                agent_count=2,
                rounds=2,
                round_delay=0.001,
            ),
        ]
        
        simulator = DualPlatformSimulator(platforms)
        return await simulator.run()
    
    def test_full_simulation(self):
        """Test running a full dual platform simulation."""
        result = asyncio.run(self._run_simulation())
        
        self.assertIsInstance(result, DualPlatformResult)
        self.assertEqual(len(result.platform_results), 2)
        self.assertIsNotNone(result.dual_consensus)
        
        # Check consensus structure
        consensus = result.dual_consensus
        self.assertIn(consensus.direction, ['bullish', 'bearish', 'neutral', 'unknown'])
        self.assertGreaterEqual(consensus.confidence, 0)
        self.assertLessEqual(consensus.confidence, 1)
        
        # Check platform results
        for platform in result.platform_results:
            self.assertTrue(platform.success)
            self.assertGreater(platform.execution_time, 0)
    
    def test_quick_dual_simulation(self):
        """Test quick_dual_simulation convenience function."""
        async def run_quick():
            return await quick_dual_simulation(verbose=False)
        
        result = asyncio.run(run_quick())
        
        self.assertIsInstance(result, DualPlatformResult)
        self.assertGreaterEqual(len(result.platform_results), 3)  # Default has 3 platforms
        self.assertIsNotNone(result.dual_consensus)
    
    def test_progress_callback(self):
        """Test progress callback during simulation."""
        progress_calls = []
        
        def progress_callback(name, current, total):
            progress_calls.append((name, current, total))
        
        async def run_with_callback():
            platforms = [
                PlatformConfig(
                    name="Callback Test",
                    platform_type=PlatformType.BALANCED,
                    agent_count=2,
                    rounds=2,
                    round_delay=0.001,
                ),
            ]
            simulator = DualPlatformSimulator(platforms)
            return await simulator.run(progress_callback=progress_callback)
        
        result = asyncio.run(run_with_callback())
        
        # Should have received progress callbacks
        self.assertGreater(len(progress_calls), 0)
        # Check callback format
        for name, current, total in progress_calls:
            self.assertEqual(name, "Callback Test")
            self.assertGreaterEqual(current, 1)
            self.assertEqual(total, 2)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def test_empty_platform_list(self):
        """Test behavior with empty platform list."""
        with self.assertRaises(ValueError):
            DualPlatformBuilder().build()
    
    def test_single_platform(self):
        """Test with single platform."""
        async def run_single():
            platforms = [
                PlatformConfig(
                    name="Single",
                    platform_type=PlatformType.BALANCED,
                    agent_count=2,
                    rounds=2,
                    round_delay=0.001,
                ),
            ]
            simulator = DualPlatformSimulator(platforms)
            return await simulator.run()
        
        result = asyncio.run(run_single())
        self.assertEqual(len(result.platform_results), 1)
        self.assertEqual(result.dual_consensus.platform_count, 1)
        self.assertEqual(result.dual_consensus.cross_platform_agreement, 1.0)
    
    def test_weighted_platforms(self):
        """Test platforms with different weights."""
        platforms = [
            PlatformConfig(
                name="Low Weight",
                platform_type=PlatformType.BALANCED,
                platform_weight=0.5,
            ),
            PlatformConfig(
                name="High Weight",
                platform_type=PlatformType.BALANCED,
                platform_weight=2.0,
            ),
        ]
        
        simulator = DualPlatformSimulator(platforms)
        self.assertEqual(simulator.platform_configs[0].platform_weight, 0.5)
        self.assertEqual(simulator.platform_configs[1].platform_weight, 2.0)
    
    def test_different_round_counts(self):
        """Test platforms with different round counts."""
        platforms = [
            PlatformConfig(name="Few Rounds", platform_type=PlatformType.BALANCED, rounds=2),
            PlatformConfig(name="Many Rounds", platform_type=PlatformType.BALANCED, rounds=10),
        ]
        
        simulator = DualPlatformSimulator(platforms)
        self.assertEqual(simulator.platform_configs[0].rounds, 2)
        self.assertEqual(simulator.platform_configs[1].rounds, 10)


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestPlatformConfig,
        TestPlatformAgentFactory,
        TestDualPlatformConsensus,
        TestDualPlatformResult,
        TestDualPlatformSimulator,
        TestDualPlatformBuilder,
        TestDualPlatformChatInterface,
        TestIntegration,
        TestEdgeCases,
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)