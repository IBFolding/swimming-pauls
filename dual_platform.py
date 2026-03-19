"""
Dual Platform Simulation System for Swimming Pauls

Runs parallel simulations across different hardware/configurations for higher 
confidence consensus. Supports multiple agent configurations, parameter variations,
and cross-platform aggregation.

Features:
- Parallel simulation execution across multiple "platforms" (configurations)
- Confidence-weighted consensus aggregation
- Cross-platform result validation
- Integration with chat_interface.py
"""
import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Tuple, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
from enum import Enum

# Import Swimming Pauls modules
from agent import Agent, AgentPrediction, PersonaType, create_agent_team
from simulation import SimulationRunner, SimulationResult, SimulationRound
from prediction import PredictionFormatter, SimulationReporter


class PlatformType(Enum):
    """Types of simulation platforms/configurations."""
    CONSERVATIVE = "conservative"      # Risk-averse Pauls
    AGGRESSIVE = "aggressive"          # Risk-tolerant Pauls
    BALANCED = "balanced"              # Standard balanced team
    FILM_INDUSTRY = "film_industry"    # Film/entertainment personas
    CUSTOM = "custom"                  # User-defined configuration


@dataclass
class PlatformConfig:
    """Configuration for a single simulation platform."""
    name: str
    platform_type: PlatformType
    agent_count: int = 5
    rounds: int = 10
    round_delay: float = 0.1
    consensus_threshold: float = 0.6
    
    # Agent configuration
    agent_configs: Optional[List[Dict[str, Any]]] = None
    custom_agents: Optional[List[Agent]] = None
    
    # Simulation parameters
    market_data_seed: Optional[int] = None
    volatility_bias: float = 0.0  # -1.0 to 1.0
    sentiment_bias: float = 0.0   # -1.0 to 1.0
    
    # Weight in cross-platform consensus
    platform_weight: float = 1.0
    
    def __post_init__(self):
        """Validate configuration."""
        if self.agent_count < 1:
            raise ValueError("agent_count must be at least 1")
        if self.rounds < 1:
            raise ValueError("rounds must be at least 1")
        if not 0 <= self.consensus_threshold <= 1:
            raise ValueError("consensus_threshold must be between 0 and 1")
        if not 0 < self.platform_weight:
            raise ValueError("platform_weight must be positive")


@dataclass
class PlatformResult:
    """Results from a single platform simulation."""
    platform_config: PlatformConfig
    simulation_result: SimulationResult
    platform_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    execution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    
    @property
    def final_consensus(self) -> Dict[str, Any]:
        """Get the final consensus from this platform."""
        return self.simulation_result.final_consensus if self.success else {}
    
    @property
    def direction(self) -> str:
        """Get the consensus direction."""
        if self.success and self.simulation_result.final_consensus:
            return self.simulation_result.final_consensus.get('direction', 'unknown')
        return 'error'
    
    @property
    def confidence(self) -> float:
        """Get the average confidence across rounds."""
        if not self.success or not self.simulation_result.rounds:
            return 0.0
        total_conf = sum(r.consensus.get('confidence', 0) for r in self.simulation_result.rounds)
        return total_conf / len(self.simulation_result.rounds)
    
    @property
    def sentiment(self) -> float:
        """Get the final sentiment score."""
        if self.success and self.simulation_result.final_consensus:
            return self.simulation_result.final_consensus.get('sentiment', 0.0)
        return 0.0


@dataclass
class DualPlatformConsensus:
    """Aggregated consensus across multiple platforms."""
    direction: str
    confidence: float
    sentiment: float
    strength: str
    platform_consensus: Dict[str, Any]
    cross_platform_agreement: float
    platform_count: int
    
    # Detailed breakdown
    bullish_platforms: int = 0
    bearish_platforms: int = 0
    neutral_platforms: int = 0
    
    # Weighted metrics
    weighted_confidence: float = 0.0
    platform_divergence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'direction': self.direction,
            'confidence': round(self.confidence, 4),
            'sentiment': round(self.sentiment, 4),
            'strength': self.strength,
            'cross_platform_agreement': round(self.cross_platform_agreement, 4),
            'platform_count': self.platform_count,
            'bullish_platforms': self.bullish_platforms,
            'bearish_platforms': self.bearish_platforms,
            'neutral_platforms': self.neutral_platforms,
            'weighted_confidence': round(self.weighted_confidence, 4),
            'platform_divergence': round(self.platform_divergence, 4),
            'platform_consensus': self.platform_consensus,
        }


@dataclass
class DualPlatformResult:
    """Complete results from dual platform simulation."""
    platform_results: List[PlatformResult]
    dual_consensus: DualPlatformConsensus
    execution_time: float = 0.0
    run_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    
    @property
    def successful_platforms(self) -> List[PlatformResult]:
        """Get only successful platform results."""
        return [p for p in self.platform_results if p.success]
    
    @property
    def failed_platforms(self) -> List[PlatformResult]:
        """Get failed platform results."""
        return [p for p in self.platform_results if not p.success]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'run_id': self.run_id,
            'timestamp': self.timestamp,
            'execution_time': self.execution_time,
            'dual_consensus': self.dual_consensus.to_dict(),
            'platforms': [
                {
                    'platform_id': p.platform_id,
                    'name': p.platform_config.name,
                    'type': p.platform_config.platform_type.value,
                    'success': p.success,
                    'direction': p.direction,
                    'confidence': round(p.confidence, 4),
                    'sentiment': round(p.sentiment, 4),
                    'execution_time': p.execution_time,
                    'error_message': p.error_message,
                }
                for p in self.platform_results
            ]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, default=str)


class PlatformAgentFactory:
    """Factory for creating agent teams for different platforms."""
    
    @staticmethod
    def create_conservative_team(count: int = 5) -> List[Agent]:
        """Create a conservative, risk-averse team."""
        team = []
        team.append(Agent("Conservative-Analyst", PersonaType.ANALYST, custom_bias=-0.1))
        team.append(Agent("Conservative-Hedgie", PersonaType.HEDGIE, custom_bias=-0.3))
        team.append(Agent("Conservative-Skeptic", PersonaType.SKEPTIC, custom_bias=-0.4))
        team.append(Agent("Conservative-StudioExec", PersonaType.STUDIO_EXEC, custom_bias=-0.2))
        team.append(Agent("Conservative-Producer", PersonaType.PRODUCER, custom_bias=-0.1))
        return team[:count]
    
    @staticmethod
    def create_aggressive_team(count: int = 5) -> List[Agent]:
        """Create an aggressive, risk-tolerant team."""
        team = []
        team.append(Agent("Aggressive-Trader", PersonaType.TRADER, custom_bias=0.3))
        team.append(Agent("Aggressive-Visionary", PersonaType.VISIONARY, custom_bias=0.5))
        team.append(Agent("Aggressive-Director", PersonaType.DIRECTOR, custom_bias=0.4))
        team.append(Agent("Aggressive-Indie", PersonaType.INDIE_FILMMAKER, custom_bias=0.5))
        team.append(Agent("Aggressive-Analyst", PersonaType.ANALYST, custom_bias=0.1))
        return team[:count]
    
    @staticmethod
    def create_balanced_team(count: int = 5) -> List[Agent]:
        """Create a standard balanced team."""
        return create_agent_team(
            analyst_count=1,
            trader_count=1,
            hedgie_count=1,
            visionary_count=1,
            skeptic_count=1
        )[:count]
    
    @staticmethod
    def create_film_industry_team(count: int = 5) -> List[Agent]:
        """Create a film industry specialized team."""
        team = []
        configs = [
            ("Film-Producer", PersonaType.PRODUCER),
            ("Film-Director", PersonaType.DIRECTOR),
            ("Film-Screenwriter", PersonaType.SCREENWRITER),
            ("Film-StudioExec", PersonaType.STUDIO_EXEC),
            ("Film-Indie", PersonaType.INDIE_FILMMAKER),
        ]
        for name, persona in configs[:count]:
            team.append(Agent(name, persona))
        return team
    
    @classmethod
    def create_team(cls, platform_type: PlatformType, count: int = 5) -> List[Agent]:
        """Create an agent team based on platform type."""
        if platform_type == PlatformType.CONSERVATIVE:
            return cls.create_conservative_team(count)
        elif platform_type == PlatformType.AGGRESSIVE:
            return cls.create_aggressive_team(count)
        elif platform_type == PlatformType.FILM_INDUSTRY:
            return cls.create_film_industry_team(count)
        else:
            return cls.create_balanced_team(count)


class DualPlatformSimulator:
    """
    Dual Platform Simulation Runner.
    
    Runs multiple simulation instances in parallel across different
    configurations and aggregates results for higher confidence consensus.
    
    Example:
        # Create platform configurations
        platforms = [
            PlatformConfig(
                name="Conservative View",
                platform_type=PlatformType.CONSERVATIVE,
                agent_count=5,
                rounds=10
            ),
            PlatformConfig(
                name="Aggressive View", 
                platform_type=PlatformType.AGGRESSIVE,
                agent_count=5,
                rounds=10
            ),
        ]
        
        # Run dual platform simulation
        simulator = DualPlatformSimulator(platforms)
        result = await simulator.run()
        
        # Access cross-platform consensus
        print(result.dual_consensus.direction)
        print(result.dual_consensus.confidence)
    """
    
    def __init__(
        self,
        platform_configs: List[PlatformConfig],
        max_workers: Optional[int] = None,
        use_processes: bool = False,
    ):
        """
        Initialize dual platform simulator.
        
        Args:
            platform_configs: List of platform configurations to run
            max_workers: Maximum parallel workers (default: number of platforms)
            use_processes: Use ProcessPoolExecutor instead of ThreadPoolExecutor
        """
        self.platform_configs = platform_configs
        self.max_workers = max_workers or len(platform_configs)
        self.use_processes = use_processes
        
        self.results: List[PlatformResult] = []
        self.is_running = False
        
    async def run(
        self,
        market_data_feed: Optional[Callable[[int, PlatformConfig], Dict[str, Any]]] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
    ) -> DualPlatformResult:
        """
        Run simulations across all platforms in parallel.
        
        Args:
            market_data_feed: Optional custom market data feed function
            progress_callback: Callback(platform_name, current, total) for progress updates
            
        Returns:
            DualPlatformResult with cross-platform consensus
        """
        self.is_running = True
        start_time = time.time()
        
        # Create tasks for each platform
        tasks = []
        for i, config in enumerate(self.platform_configs):
            task = self._run_single_platform(
                config, 
                market_data_feed,
                lambda name, curr, total: progress_callback(name, curr, total) if progress_callback else None
            )
            tasks.append(task)
        
        # Run all platforms concurrently
        try:
            self.results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions
            processed_results = []
            for i, result in enumerate(self.results):
                if isinstance(result, Exception):
                    # Create failed result
                    config = self.platform_configs[i]
                    failed_result = PlatformResult(
                        platform_config=config,
                        simulation_result=SimulationResult(
                            start_time=time.time(),
                            end_time=time.time(),
                            rounds=[],
                            final_consensus={},
                            agent_performances={},
                        ),
                        success=False,
                        error_message=str(result),
                    )
                    processed_results.append(failed_result)
                else:
                    processed_results.append(result)
            
            self.results = processed_results
            
        except asyncio.CancelledError:
            pass
        finally:
            self.is_running = False
        
        execution_time = time.time() - start_time
        
        # Calculate dual consensus
        dual_consensus = self._calculate_dual_consensus()
        
        return DualPlatformResult(
            platform_results=self.results,
            dual_consensus=dual_consensus,
            execution_time=execution_time,
        )
    
    async def _run_single_platform(
        self,
        config: PlatformConfig,
        market_data_feed: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
    ) -> PlatformResult:
        """Run simulation for a single platform."""
        platform_start = time.time()
        
        try:
            # Create agent team
            if config.custom_agents:
                agents = config.custom_agents
            elif config.agent_configs:
                agents = self._create_agents_from_configs(config.agent_configs)
            else:
                agents = PlatformAgentFactory.create_team(
                    config.platform_type, 
                    config.agent_count
                )
            
            # Create runner
            runner = SimulationRunner(
                agents=agents,
                rounds=config.rounds,
                round_delay=config.round_delay,
                consensus_threshold=config.consensus_threshold,
            )
            
            # Run simulation with progress callback
            def round_callback(round_result: SimulationRound):
                if progress_callback:
                    progress_callback(
                        config.name,
                        round_result.round_number,
                        config.rounds
                    )
            
            # Create market data feed with platform-specific biases
            def biased_market_data(round_num: int) -> Dict[str, Any]:
                base_data = self._generate_market_data(round_num, config)
                if market_data_feed:
                    custom_data = market_data_feed(round_num, config)
                    base_data.update(custom_data)
                return base_data
            
            sim_result = await runner.run(
                market_data_feed=biased_market_data,
                callback=round_callback,
            )
            
            execution_time = time.time() - platform_start
            
            return PlatformResult(
                platform_config=config,
                simulation_result=sim_result,
                execution_time=execution_time,
                success=True,
            )
            
        except Exception as e:
            execution_time = time.time() - platform_start
            return PlatformResult(
                platform_config=config,
                simulation_result=SimulationResult(
                    start_time=platform_start,
                    end_time=time.time(),
                    rounds=[],
                    final_consensus={},
                    agent_performances={},
                ),
                execution_time=execution_time,
                success=False,
                error_message=str(e),
            )
    
    def _create_agents_from_configs(self, configs: List[Dict[str, Any]]) -> List[Agent]:
        """Create agents from configuration dictionaries."""
        agents = []
        for config in configs:
            agent = Agent(
                name=config['name'],
                persona=config.get('persona', PersonaType.ANALYST),
                custom_bias=config.get('bias'),
                custom_confidence=config.get('confidence'),
            )
            agents.append(agent)
        return agents
    
    def _generate_market_data(
        self, 
        round_num: int, 
        config: PlatformConfig
    ) -> Dict[str, Any]:
        """Generate market data with platform-specific biases."""
        import random
        
        # Use platform seed if provided
        if config.market_data_seed:
            random.seed(config.market_data_seed + round_num)
        
        base_trend = random.uniform(-0.5, 0.5)
        
        # Apply platform biases
        adjusted_trend = base_trend + config.volatility_bias * 0.3
        adjusted_sentiment = random.uniform(-0.5, 0.5) + config.sentiment_bias * 0.3
        
        return {
            'price_trend': adjusted_trend,
            'volume': random.uniform(0.3, 1.0),
            'sentiment': adjusted_sentiment,
            'volatility': random.uniform(0.1, 0.6) + abs(config.volatility_bias) * 0.2,
            'timestamp': time.time(),
        }
    
    def _calculate_dual_consensus(self) -> DualPlatformConsensus:
        """Calculate confidence-weighted consensus across all platforms."""
        successful = self.successful_platforms
        
        if not successful:
            return DualPlatformConsensus(
                direction="unknown",
                confidence=0.0,
                sentiment=0.0,
                strength="weak",
                platform_consensus={},
                cross_platform_agreement=0.0,
                platform_count=0,
            )
        
        # Count directions weighted by platform weight
        direction_weights = {"bullish": 0.0, "bearish": 0.0, "neutral": 0.0}
        total_weight = 0.0
        
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        weighted_sentiment = 0.0
        weighted_confidence = 0.0
        sentiments = []
        
        for result in successful:
            config = result.platform_config
            direction = result.direction
            weight = config.platform_weight
            
            direction_weights[direction] += weight
            total_weight += weight
            
            if direction == "bullish":
                bullish_count += 1
            elif direction == "bearish":
                bearish_count += 1
            else:
                neutral_count += 1
            
            weighted_sentiment += result.sentiment * weight
            weighted_confidence += result.confidence * weight
            sentiments.append(result.sentiment)
        
        # Normalize direction weights
        if total_weight > 0:
            direction_weights = {k: v / total_weight for k, v in direction_weights.items()}
            weighted_sentiment /= total_weight
            weighted_confidence /= total_weight
        
        # Determine consensus direction
        max_direction = max(direction_weights, key=direction_weights.get)
        max_weight = direction_weights[max_direction]
        
        # Calculate cross-platform agreement (consistency)
        cross_platform_agreement = max(bullish_count, bearish_count, neutral_count) / len(successful)
        
        # Calculate platform divergence (standard deviation of sentiments)
        if len(sentiments) > 1:
            mean_sentiment = sum(sentiments) / len(sentiments)
            variance = sum((s - mean_sentiment) ** 2 for s in sentiments) / len(sentiments)
            platform_divergence = variance ** 0.5
        else:
            platform_divergence = 0.0
        
        # Determine strength
        if max_weight >= 0.7 and cross_platform_agreement >= 0.7:
            strength = "very_strong"
        elif max_weight >= 0.6 or cross_platform_agreement >= 0.6:
            strength = "strong"
        elif max_weight >= 0.5 or cross_platform_agreement >= 0.5:
            strength = "moderate"
        else:
            strength = "weak"
        
        # Calculate overall confidence incorporating cross-platform agreement
        overall_confidence = weighted_confidence * (0.5 + 0.5 * cross_platform_agreement)
        
        return DualPlatformConsensus(
            direction=max_direction,
            confidence=overall_confidence,
            sentiment=weighted_sentiment,
            strength=strength,
            platform_consensus=direction_weights,
            cross_platform_agreement=cross_platform_agreement,
            platform_count=len(successful),
            bullish_platforms=bullish_count,
            bearish_platforms=bearish_count,
            neutral_platforms=neutral_count,
            weighted_confidence=weighted_confidence,
            platform_divergence=platform_divergence,
        )
    
    @property
    def successful_platforms(self) -> List[PlatformResult]:
        """Get successful platform results."""
        return [r for r in self.results if r.success]
    
    def get_platform_by_name(self, name: str) -> Optional[PlatformResult]:
        """Get result for a specific platform by name."""
        for result in self.results:
            if result.platform_config.name == name:
                return result
        return None
    
    def get_consensus_report(self) -> str:
        """Generate a human-readable consensus report."""
        if not hasattr(self, '_cached_consensus'):
            self._cached_consensus = self._calculate_dual_consensus()
        
        consensus = self._cached_consensus
        lines = []
        
        lines.append("=" * 60)
        lines.append("🎯 DUAL PLATFORM CONSENSUS REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        # Overall consensus
        emoji = {"bullish": "🚀", "bearish": "🔻", "neutral": "➖", "unknown": "❓"}
        direction_emoji = emoji.get(consensus.direction, "❓")
        
        lines.append(f"{direction_emoji} DIRECTION: {consensus.direction.upper()}")
        lines.append(f"📊 Confidence: {consensus.confidence:.1%}")
        lines.append(f"📈 Sentiment: {consensus.sentiment:+.3f}")
        lines.append(f"💪 Strength: {consensus.strength.upper()}")
        lines.append(f"🤝 Cross-Platform Agreement: {consensus.cross_platform_agreement:.1%}")
        lines.append("")
        
        # Platform breakdown
        lines.append("-" * 60)
        lines.append("PLATFORM BREAKDOWN")
        lines.append("-" * 60)
        
        for result in self.results:
            config = result.platform_config
            status = "✅" if result.success else "❌"
            
            lines.append(f"\n{status} {config.name} ({config.platform_type.value})")
            if result.success:
                dir_emoji = emoji.get(result.direction, "❓")
                lines.append(f"   {dir_emoji} Direction: {result.direction.upper()}")
                lines.append(f"   📊 Confidence: {result.confidence:.1%}")
                lines.append(f"   📈 Sentiment: {result.sentiment:+.3f}")
                lines.append(f"   ⏱️  Execution Time: {result.execution_time:.2f}s")
                lines.append(f"   ⚖️  Platform Weight: {config.platform_weight}")
            else:
                lines.append(f"   ❌ Error: {result.error_message}")
        
        lines.append("")
        lines.append("-" * 60)
        lines.append("AGGREGATION DETAILS")
        lines.append("-" * 60)
        lines.append(f"Platforms Run: {len(self.results)}")
        lines.append(f"Successful: {len(self.successful_platforms)}")
        lines.append(f"Failed: {len(self.results) - len(self.successful_platforms)}")
        lines.append(f"Weighted Confidence: {consensus.weighted_confidence:.1%}")
        lines.append(f"Platform Divergence: {consensus.platform_divergence:.3f}")
        lines.append("")
        
        # Direction distribution
        lines.append("Direction Distribution:")
        for direction, weight in consensus.platform_consensus.items():
            bar_length = int(weight * 30)
            bar = "█" * bar_length + "░" * (30 - bar_length)
            lines.append(f"  {direction:10} |{bar}| {weight:.1%}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)


class DualPlatformBuilder:
    """Builder pattern for creating dual platform simulations."""
    
    def __init__(self):
        self.platforms: List[PlatformConfig] = []
        self.max_workers: Optional[int] = None
        self.use_processes = False
    
    def add_platform(
        self,
        name: str,
        platform_type: PlatformType = PlatformType.BALANCED,
        agent_count: int = 5,
        rounds: int = 10,
        weight: float = 1.0,
        **kwargs
    ) -> "DualPlatformBuilder":
        """Add a platform configuration."""
        config = PlatformConfig(
            name=name,
            platform_type=platform_type,
            agent_count=agent_count,
            rounds=rounds,
            platform_weight=weight,
            **kwargs
        )
        self.platforms.append(config)
        return self
    
    def add_conservative_platform(
        self,
        name: str = "Conservative",
        agent_count: int = 5,
        rounds: int = 10,
        weight: float = 1.0,
    ) -> "DualPlatformBuilder":
        """Add a conservative platform."""
        return self.add_platform(
            name=name,
            platform_type=PlatformType.CONSERVATIVE,
            agent_count=agent_count,
            rounds=rounds,
            weight=weight,
        )
    
    def add_aggressive_platform(
        self,
        name: str = "Aggressive",
        agent_count: int = 5,
        rounds: int = 10,
        weight: float = 1.0,
    ) -> "DualPlatformBuilder":
        """Add an aggressive platform."""
        return self.add_platform(
            name=name,
            platform_type=PlatformType.AGGRESSIVE,
            agent_count=agent_count,
            rounds=rounds,
            weight=weight,
        )
    
    def add_balanced_platform(
        self,
        name: str = "Balanced",
        agent_count: int = 5,
        rounds: int = 10,
        weight: float = 1.0,
    ) -> "DualPlatformBuilder":
        """Add a balanced platform."""
        return self.add_platform(
            name=name,
            platform_type=PlatformType.BALANCED,
            agent_count=agent_count,
            rounds=rounds,
            weight=weight,
        )
    
    def add_film_industry_platform(
        self,
        name: str = "Film Industry",
        agent_count: int = 5,
        rounds: int = 10,
        weight: float = 1.0,
    ) -> "DualPlatformBuilder":
        """Add a film industry platform."""
        return self.add_platform(
            name=name,
            platform_type=PlatformType.FILM_INDUSTRY,
            agent_count=agent_count,
            rounds=rounds,
            weight=weight,
        )
    
    def with_max_workers(self, max_workers: int) -> "DualPlatformBuilder":
        """Set maximum parallel workers."""
        self.max_workers = max_workers
        return self
    
    def with_processes(self, use_processes: bool = True) -> "DualPlatformBuilder":
        """Use process pool instead of thread pool."""
        self.use_processes = use_processes
        return self
    
    def build(self) -> DualPlatformSimulator:
        """Build and return the dual platform simulator."""
        if not self.platforms:
            raise ValueError("At least one platform must be added")
        
        return DualPlatformSimulator(
            platform_configs=self.platforms,
            max_workers=self.max_workers,
            use_processes=self.use_processes,
        )


# Chat Interface Integration
class DualPlatformChatInterface:
    """Integration with chat_interface.py for dual platform results."""
    
    def __init__(self, chat_interface=None):
        """
        Initialize with optional chat interface.
        
        Args:
            chat_interface: Existing ChatInterface instance or None
        """
        if chat_interface is None:
            # Import here to avoid circular imports
            try:
                from chat_interface import ChatInterface
                self.chat_interface = ChatInterface()
            except ImportError:
                self.chat_interface = None
        else:
            self.chat_interface = chat_interface
    
    def save_dual_result(self, result: DualPlatformResult) -> str:
        """
        Save dual platform result and return shareable ID.
        
        Args:
            result: DualPlatformResult to save
            
        Returns:
            Shareable result ID
        """
        if self.chat_interface is None:
            # Fallback: save to file directly
            import uuid
            from pathlib import Path
            
            result_id = str(uuid.uuid4())[:8]
            results_dir = Path("data/results")
            results_dir.mkdir(parents=True, exist_ok=True)
            
            result_file = results_dir / f"{result_id}.json"
            
            export_data = {
                'result_id': result_id,
                'type': 'dual_platform',
                'timestamp': result.timestamp,
                'data': result.to_dict(),
            }
            
            with open(result_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            return result_id
        
        # Use existing chat interface
        result_id = self.chat_interface.generate_result_id()
        
        export_data = {
            'result_id': result_id,
            'type': 'dual_platform',
            'timestamp': result.timestamp,
            'data': result.to_dict(),
        }
        
        result_file = self.chat_interface.results_dir / f"{result_id}.json"
        with open(result_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return result_id
    
    def format_chat_response(
        self, 
        result: DualPlatformResult, 
        base_url: str = "http://localhost:3005"
    ) -> str:
        """
        Format dual platform result for chat response.
        
        Args:
            result: DualPlatformResult to format
            base_url: Base URL for result links
            
        Returns:
            Formatted chat response string
        """
        consensus = result.dual_consensus
        direction = consensus.direction.upper()
        confidence = int(consensus.confidence * 100)
        
        emoji_map = {
            'BULLISH': '🟢',
            'BEARISH': '🔴',
            'NEUTRAL': '🟡',
            'UNKNOWN': '⚪'
        }
        emoji = emoji_map.get(direction, '⚪')
        
        strength_emoji = {
            'very_strong': '💪💪',
            'strong': '💪',
            'moderate': '📊',
            'weak': '❓'
        }.get(consensus.strength, '❓')
        
        response = f"""🦷 **SWIMMING PAULS - DUAL PLATFORM CONSENSUS**

{emoji} **{direction}** ({confidence}% confidence) {strength_emoji}

📊 **Cross-Platform Stats:**
• Platforms: {consensus.platform_count}
• Agreement: {consensus.cross_platform_agreement:.0%}
• Sentiment: {consensus.sentiment:+.2f}
• Divergence: {consensus.platform_divergence:.2f}

🎯 **Platform Breakdown:**
"""
        
        for platform in result.platform_results:
            p_emoji = emoji_map.get(platform.direction.upper(), '⚪')
            status = "✅" if platform.success else "❌"
            response += f"• {status} {platform.platform_config.name}: {p_emoji} {platform.direction.upper()} ({int(platform.confidence * 100)}%)\n"
        
        # Add direction distribution if informative
        if consensus.platform_count > 2:
            response += f"\n📈 **Direction Distribution:**\n"
            for dir_name, weight in consensus.platform_consensus.items():
                if weight > 0:
                    bar = "█" * int(weight * 10)
                    response += f"• {dir_name.capitalize()}: {bar} {weight:.0%}\n"
        
        # Add view link
        result_id = getattr(result, 'saved_id', '')
        if result_id:
            response += f"\n📊 [View Full Results]({base_url}/explorer.html?id={result_id})"
        
        return response
    
    def get_dual_result(self, result_id: str) -> Optional[DualPlatformResult]:
        """
        Retrieve dual platform result by ID.
        
        Args:
            result_id: Result ID to retrieve
            
        Returns:
            DualPlatformResult if found, None otherwise
        """
        from pathlib import Path
        
        results_dir = Path("data/results")
        result_file = results_dir / f"{result_id}.json"
        
        if not result_file.exists():
            if self.chat_interface:
                # Try through chat interface
                data = self.chat_interface.get_prediction_result(result_id)
                if data and data.get('type') == 'dual_platform':
                    return self._reconstruct_result(data['data'])
            return None
        
        with open(result_file, 'r') as f:
            data = json.load(f)
        
        if data.get('type') == 'dual_platform':
            return self._reconstruct_result(data['data'])
        
        return None
    
    def _reconstruct_result(self, data: Dict) -> Optional[DualPlatformResult]:
        """Reconstruct DualPlatformResult from dictionary data."""
        # Simplified reconstruction - full reconstruction would need more work
        # This is mainly for verification purposes
        try:
            consensus_data = data.get('dual_consensus', {})
            dual_consensus = DualPlatformConsensus(
                direction=consensus_data.get('direction', 'unknown'),
                confidence=consensus_data.get('confidence', 0.0),
                sentiment=consensus_data.get('sentiment', 0.0),
                strength=consensus_data.get('strength', 'weak'),
                platform_consensus=consensus_data.get('platform_consensus', {}),
                cross_platform_agreement=consensus_data.get('cross_platform_agreement', 0.0),
                platform_count=consensus_data.get('platform_count', 0),
                bullish_platforms=consensus_data.get('bullish_platforms', 0),
                bearish_platforms=consensus_data.get('bearish_platforms', 0),
                neutral_platforms=consensus_data.get('neutral_platforms', 0),
                weighted_confidence=consensus_data.get('weighted_confidence', 0.0),
                platform_divergence=consensus_data.get('platform_divergence', 0.0),
            )
            
            # Create minimal platform results (full reconstruction not needed for display)
            platform_results = []
            for p_data in data.get('platforms', []):
                # Minimal reconstruction
                config = PlatformConfig(
                    name=p_data.get('name', 'Unknown'),
                    platform_type=PlatformType(p_data.get('type', 'balanced')),
                )
                sim_result = SimulationResult(
                    start_time=0,
                    end_time=p_data.get('execution_time', 0),
                    rounds=[],
                    final_consensus={'direction': p_data.get('direction', 'unknown')},
                    agent_performances={},
                )
                platform_results.append(PlatformResult(
                    platform_config=config,
                    simulation_result=sim_result,
                    platform_id=p_data.get('platform_id', ''),
                    execution_time=p_data.get('execution_time', 0),
                    success=p_data.get('success', False),
                    error_message=p_data.get('error_message'),
                ))
            
            return DualPlatformResult(
                platform_results=platform_results,
                dual_consensus=dual_consensus,
                execution_time=data.get('execution_time', 0),
                run_id=data.get('run_id', ''),
                timestamp=data.get('timestamp', 0),
            )
        except Exception:
            return None


# Convenience functions
async def quick_dual_simulation(
    platforms: Optional[List[PlatformConfig]] = None,
    verbose: bool = True,
) -> DualPlatformResult:
    """
    Quick dual platform simulation with default settings.
    
    Args:
        platforms: Optional list of platform configs (uses defaults if None)
        verbose: Print results if True
        
    Returns:
        DualPlatformResult
    """
    if platforms is None:
        # Create default platforms
        platforms = [
            PlatformConfig(
                name="Conservative",
                platform_type=PlatformType.CONSERVATIVE,
                agent_count=5,
                rounds=5,
                platform_weight=1.0,
            ),
            PlatformConfig(
                name="Aggressive",
                platform_type=PlatformType.AGGRESSIVE,
                agent_count=5,
                rounds=5,
                platform_weight=1.0,
            ),
            PlatformConfig(
                name="Balanced",
                platform_type=PlatformType.BALANCED,
                agent_count=5,
                rounds=5,
                platform_weight=1.2,  # Slightly higher weight for balanced view
            ),
        ]
    
    simulator = DualPlatformSimulator(platforms)
    result = await simulator.run()
    
    if verbose:
        print(simulator.get_consensus_report())
    
    return result


# Export key classes
__all__ = [
    'PlatformType',
    'PlatformConfig',
    'PlatformResult',
    'DualPlatformConsensus',
    'DualPlatformResult',
    'PlatformAgentFactory',
    'DualPlatformSimulator',
    'DualPlatformBuilder',
    'DualPlatformChatInterface',
    'quick_dual_simulation',
]


# Demo/Example
if __name__ == "__main__":
    """
    Demo script for Dual Platform Simulation.
    
    Run with:
        python dual_platform.py
    """
    import sys
    
    print("=" * 70)
    print("🎯 DUAL PLATFORM SIMULATION DEMO")
    print("=" * 70)
    print()
    print("Running parallel simulations across different configurations...")
    print("- Conservative platform: Risk-averse Pauls")
    print("- Aggressive platform: Risk-tolerant Pauls")
    print("- Balanced platform: Standard balanced team (higher weight)")
    print()
    
    async def run_demo():
        # Build simulator with multiple platforms
        simulator = (DualPlatformBuilder()
            .add_conservative_platform(
                name="🛡️ Conservative",
                agent_count=4,
                rounds=5,
                weight=1.0,
            )
            .add_aggressive_platform(
                name="⚔️ Aggressive",
                agent_count=4,
                rounds=5,
                weight=1.0,
            )
            .add_balanced_platform(
                name="⚖️ Balanced",
                agent_count=5,
                rounds=5,
                weight=1.2,  # Higher weight for balanced view
            )
            .build())
        
        # Progress callback
        def on_progress(name, current, total):
            sys.stdout.write(f"\r   {name}: Round {current}/{total}")
            sys.stdout.flush()
        
        print("Running simulations...")
        result = await simulator.run(progress_callback=on_progress)
        print("\r   All simulations complete!          ")
        print()
        
        # Display results
        print(simulator.get_consensus_report())
        print()
        
        # Show chat-formatted output
        print("-" * 70)
        print("💬 CHAT INTERFACE FORMAT:")
        print("-" * 70)
        chat_interface = DualPlatformChatInterface()
        print(chat_interface.format_chat_response(result))
        print()
        
        # Save result
        result_id = chat_interface.save_dual_result(result)
        print(f"💾 Result saved with ID: {result_id}")
        print()
        
        # Verify retrieval
        retrieved = chat_interface.get_dual_result(result_id)
        if retrieved:
            print(f"✅ Successfully retrieved result: {retrieved.dual_consensus.direction.upper()}")
        
        return result
    
    # Run the demo
    try:
        result = asyncio.run(run_demo())
        print()
        print("=" * 70)
        print("✅ DEMO COMPLETE")
        print("=" * 70)
        print()
        print(f"Run ID: {result.run_id}")
        print(f"Total Execution Time: {result.execution_time:.2f}s")
        print(f"Platforms Run: {result.dual_consensus.platform_count}")
        print(f"Final Consensus: {result.dual_consensus.direction.upper()}")
        print()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()