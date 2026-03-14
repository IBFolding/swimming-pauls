"""
SwimmingPauls v2.0 - Unified Multi-Agent Simulation System
100% LOCAL - No cloud dependencies, no API keys required

A comprehensive multi-agent prediction and analysis platform that runs entirely on your machine:
- Agent-based predictions with personas (agent.py)
- Simulation orchestration (simulation.py)
- Local data feeds - RSS, files, web scraping (data_feeds_local.py)
- Persistent memory - SQLite (memory.py, local_memory.py)
- Rich visualizations - Terminal, HTML, PNG (visualization.py)
- Advanced analytics - Monte Carlo, sensitivity (advanced.py)

Usage:
    from swimming_pauls import SwimmingPauls
    
    pauls = SwimmingPauls()
    await pauls.run_simulation(rounds=20)
    pauls.visualize()

Environment Variables:
    SWIMMING_PAULS_LOCAL=1 - Force local-only mode (default)
    SWIMMING_PAULS_USE_APIS=1 - Enable optional API connectors
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Check local mode
FORCE_LOCAL = os.environ.get('SWIMMING_PAULS_LOCAL', '1') == '1'
USE_APIS = os.environ.get('SWIMMING_PAULS_USE_APIS', '0') == '1'

# Import all modules
from .agent import (
    Agent, AgentPrediction, PersonaType, AgentTrait,
    create_agent_team, create_film_industry_team, PERSONA_PROFILES
)
from .simulation import (
    SimulationRunner, SimulationBuilder, SimulationResult, SimulationRound,
    quick_simulate
)

# Use local data feeds by default
if FORCE_LOCAL or not USE_APIS:
    from .local_data_feeds import (
        LocalNewsConnector, LocalMarketConnector, LocalSentimentConnector,
        LocalDataFeedManager, FileWatcherConnector,
        NewsArticle, MarketPrice, SentimentScore, FileChange,
        fetch_local_news, fetch_local_market, fetch_local_sentiment
    )
    # Create aliases for compatibility
    DataFeedManager = LocalDataFeedManager
    NewsConnector = LocalNewsConnector
    MarketConnector = LocalMarketConnector
    SentimentConnector = LocalSentimentConnector
    fetch_news = fetch_local_news
    fetch_market = fetch_local_market
    fetch_sentiment = fetch_local_sentiment
else:
    from .data_feeds import (
        DataFeedManager, NewsConnector, MarketConnector, SentimentConnector,
        FileWatcherConnector, NewsArticle, MarketPrice, SentimentScore, FileChange,
        fetch_news, fetch_market, fetch_sentiment, watch_files
    )

from .memory import (
    ScalesMemory, Session, Agent as MemoryAgent, Prediction,
    AccuracyMetrics, ModelAdjustment, init_memory
)
from .local_memory import (
    LocalMemoryManager, LocalMemory, MemoryEntry
)
from .visualization import (
    ScalesVisualizer, TerminalCharts, PlotextCharts, MatplotlibCharts,
    HTMLReportGenerator, HTMLReportConfig, quick_visualize,
    print_confidence_chart, print_sentiment_timeline, print_agent_ranking
)
from .advanced import (
    MonteCarloSimulator, SensitivityAnalyzer, ScenarioComparator, Backtester,
    AdvancedSimulationSuite, MonteCarloResult, SensitivityResult,
    ScenarioComparison, BacktestResult,
    quick_monte_carlo, quick_sensitivity, quick_compare, quick_backtest
)
from .prediction import (
    PredictionFormatter, SimulationReporter, SimpleOutput,
    print_report, export_json
)

# 🐟 MiroFish Imports - Knowledge Graph, Memory & Personas
try:
    from .knowledge_graph import (
        KnowledgeGraph, Entity, Relationship, GraphBuilder,
        EntityExtractor, create_market_knowledge_graph,
    )
    from .graph_memory import (
        GraphMemory, AgentKnowledge, KnowledgeQuery, GraphMemoryMixin,
    )
    from .persona_factory import (
        PaulPersonaFactory, PaulPersona, TradingStyle,
        RiskProfile, SpecialtyDomain, generate_swimming_pauls_pool,
    )
    from .mirofish_integration import (
        MiroFishSwimmingPauls, MiroFishConfig, MiroFishAgent,
        quick_start as mirofish_quick_start,
    )
    MIROFISH_AVAILABLE = True
except ImportError as e:
    MIROFISH_AVAILABLE = False
    # Log the error for debugging but don't fail
    import warnings
    warnings.warn(f"MiroFish modules not fully available: {e}")


@dataclass
class SwimmingPaulsConfig:
    """Configuration for SwimmingPauls system - LOCAL ONLY by default."""
    # Simulation settings
    default_rounds: int = 10
    default_delay: float = 0.5
    consensus_threshold: float = 0.6
    
    # Data feed settings - LOCAL ONLY (no APIs)
    enable_local_files: bool = True
    enable_rss: bool = True
    enable_web_scraping: bool = True
    watch_dirs: List[str] = field(default_factory=lambda: ["./data", "./documents"])
    
    # Optional API settings (disabled by default)
    enable_news_api: bool = False
    enable_market_api: bool = False
    enable_sentiment_api: bool = False
    news_api_key: Optional[str] = None
    market_api_key: Optional[str] = None
    
    # Memory settings - LOCAL ONLY
    db_path: str = "~/.openclaw/workspace/swimming_pauls/data/swimming_pauls.db"
    local_memory_path: str = "~/.openclaw/workspace/swimming_pauls/data/local_memory.db"
    enable_persistence: bool = True
    use_cloud_memory: bool = False  # Disabled by default
    
    # Visualization settings
    default_output_dir: str = "./pauls_output"
    theme: str = "dark"
    
    # Advanced analysis settings
    monte_carlo_runs: int = 1000
    sensitivity_samples: int = 500
    
    # Mode
    local_only: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "simulation": {
                "default_rounds": self.default_rounds,
                "default_delay": self.default_delay,
                "consensus_threshold": self.consensus_threshold,
            },
            "data_feeds": {
                "local_files": self.enable_local_files,
                "rss": self.enable_rss,
                "web_scraping": self.enable_web_scraping,
                "watch_dirs": self.watch_dirs,
                "news_api": self.enable_news_api,
                "market_api": self.enable_market_api,
            },
            "memory": {
                "enable_persistence": self.enable_persistence,
                "local_only": self.local_only,
                "db_path": self.db_path,
            },
            "visualization": {
                "default_output_dir": self.default_output_dir,
                "theme": self.theme,
            },
            "advanced": {
                "monte_carlo_runs": self.monte_carlo_runs,
                "sensitivity_samples": self.sensitivity_samples,
            },
        }


class SwimmingPauls:
    """
    Unified interface for the SwimmingPauls multi-agent simulation system.
    
    This class coordinates all modules:
    - Creates and manages agents with different personas
    - Runs simulations with real-time data feeds
    - Persists results to memory
    - Generates visualizations
    - Performs advanced analytics (Monte Carlo, sensitivity, backtesting)
    
    Example:
        pauls = SwimmingPauls()
        
        # Run a basic simulation
        result = await pauls.run_simulation(rounds=20)
        
        # Run with live data
        result = await pauls.run_with_data_feeds(
            news_query="bitcoin",
            market_symbols=["BTC", "ETH"],
            sentiment_topic="crypto"
        )
        
        # Advanced analysis
        mc_result = await pauls.monte_carlo(runs=5000)
        sens_result = await pauls.sensitivity_analysis()
        
        # Visualize
        pauls.visualize()
        pauls.generate_html_report("report.html")
    """
    
    def __init__(
        self,
        agents: Optional[List[Agent]] = None,
        config: Optional[SwimmingPaulsConfig] = None,
    ):
        """
        Initialize SwimmingPauls system.
        
        Args:
            agents: Optional list of agents (creates default team if None)
            config: Optional configuration object
        """
        self.config = config or SwimmingPaulsConfig()
        self.agents = agents or create_agent_team()
        
        # Initialize components
        self._simulation_runner: Optional[SimulationRunner] = None
        self._data_manager: Optional[DataFeedManager] = None
        self._memory: Optional[ScalesMemory] = None
        self._visualizer: Optional[ScalesVisualizer] = None
        self._advanced_suite: Optional[AdvancedSimulationSuite] = None
        
        # State
        self.last_result: Optional[SimulationResult] = None
        self.session_uuid: Optional[str] = None
        self.data_cache: Dict[str, Any] = {}
        
        # Initialize persistence if enabled
        if self.config.enable_persistence:
            self._init_memory()
    
    def _init_memory(self) -> None:
        """Initialize memory system."""
        db_path = os.path.expanduser(self.config.db_path)
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._memory = ScalesMemory(db_path=db_path)
        
        # Create session
        session = self._memory.create_session(
            name=f"SwimmingPauls_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            config=self.config.to_dict()
        )
        self.session_uuid = session.session_uuid
        
        # Register agents
        for agent in self.agents:
            self._memory.register_agent(
                agent_id=agent.id,
                name=agent.name,
                model_name="swimming_pauls",
                agent_type=agent.persona.value,
                config={"bias": agent.bias, "confidence": agent.base_confidence}
            )
    
    # ========================================================================
    # Core Simulation Methods
    # ========================================================================
    
    async def run_simulation(
        self,
        rounds: Optional[int] = None,
        delay: Optional[float] = None,
        market_data_feed: Optional[Callable[[int], Dict[str, Any]]] = None,
        progress_callback: Optional[Callable[[SimulationRound], None]] = None,
        use_live_data: bool = False,
        news_query: Optional[str] = None,
        market_symbols: Optional[List[str]] = None,
        sentiment_topic: Optional[str] = None,
    ) -> SimulationResult:
        """
        Run a simulation with optional live data feeds.
        
        Args:
            rounds: Number of rounds (default from config)
            delay: Delay between rounds (default from config)
            market_data_feed: Optional custom data feed function
            progress_callback: Optional callback for round updates
            use_live_data: Whether to use live data feeds
            news_query: News query for data feed
            market_symbols: Market symbols for data feed
            sentiment_topic: Topic for sentiment analysis
            
        Returns:
            SimulationResult with all rounds and consensus
        """
        rounds = rounds or self.config.default_rounds
        delay = delay or self.config.default_delay
        
        # Build runner
        builder = SimulationBuilder()
        self._simulation_runner = (builder
            .with_agents(self.agents)
            .with_rounds(rounds)
            .with_delay(delay)
            .with_consensus_threshold(self.config.consensus_threshold)
            .build())
        
        # Prepare data feed
        if use_live_data:
            feed = await self._create_live_data_feed(
                news_query=news_query,
                market_symbols=market_symbols,
                sentiment_topic=sentiment_topic,
            )
        else:
            feed = market_data_feed
        
        # Run simulation
        result = await self._simulation_runner.run(
            market_data_feed=feed,
            callback=progress_callback or self._default_progress_callback,
        )
        
        self.last_result = result
        
        # Persist to memory
        if self._memory and self.session_uuid:
            await self._persist_simulation_result(result)
        
        return result
    
    async def run_with_data_feeds(
        self,
        news_query: Optional[str] = None,
        market_symbols: Optional[List[str]] = None,
        sentiment_topic: Optional[str] = None,
        rounds: int = 10,
        delay: float = 1.0,
    ) -> SimulationResult:
        """
        Run simulation with live external data feeds.
        
        Args:
            news_query: Query string for news feed
            market_symbols: List of market symbols (e.g., ["BTC", "ETH"])
            sentiment_topic: Topic for sentiment analysis
            rounds: Number of rounds
            delay: Delay between rounds
            
        Returns:
            SimulationResult
        """
        return await self.run_simulation(
            rounds=rounds,
            delay=delay,
            use_live_data=True,
            news_query=news_query,
            market_symbols=market_symbols,
            sentiment_topic=sentiment_topic,
        )
    
    def _default_progress_callback(self, round_result: SimulationRound) -> None:
        """Default progress callback."""
        c = round_result.consensus
        emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(c['direction'], "❓")
        strength_emoji = {"strong": "🟢", "moderate": "🟡", "weak": "🔴"}.get(c['strength'], "⚪")
        
        print(f"  Round {round_result.round_number:2d}: {emoji} {c['direction'].upper():8s} "
              f"| conf: {c['confidence']:.2f} | {strength_emoji} {c['strength']:8s} | "
              f"sentiment: {c['sentiment']:+.2f}")
    
    async def _create_live_data_feed(
        self,
        news_query: Optional[str],
        market_symbols: Optional[List[str]],
        sentiment_topic: Optional[str],
    ) -> Callable[[int], Dict[str, Any]]:
        """Create a data feed function using live data sources."""
        if self._data_manager is None:
            self._data_manager = DataFeedManager()
        
        async def feed(round_num: int) -> Dict[str, Any]:
            # Fetch all data concurrently
            results = await self._data_manager.fetch_all(
                news_query=news_query,
                market_symbols=market_symbols,
                sentiment_topic=sentiment_topic,
            )
            
            # Convert to market data format
            market_data = {
                "round": round_num,
                "timestamp": time.time(),
                "price_trend": 0.0,
                "volume": 0.5,
                "sentiment": 0.0,
                "volatility": 0.3,
            }
            
            # Incorporate market data if available
            if "market" in results and results["market"]:
                prices = results["market"]
                if prices:
                    price = prices[0]
                    market_data["price_trend"] = (price.change_24h or 0) / 100
                    market_data["volume"] = min(1.0, (price.volume_24h or 0) / 1e9)
            
            # Incorporate sentiment if available
            if "sentiment" in results and results["sentiment"]:
                sentiments = results["sentiment"]
                if sentiments:
                    market_data["sentiment"] = sentiments[0].score
            
            # Incorporate news sentiment if available
            if "news" in results and results["news"]:
                news_items = results["news"]
                if news_items:
                    # Simple sentiment from news presence
                    market_data["news_sentiment"] = 0.1 if len(news_items) > 3 else -0.1
            
            self.data_cache[round_num] = results
            return market_data
        
        return feed
    
    async def _persist_simulation_result(self, result: SimulationResult) -> None:
        """Persist simulation result to memory."""
        if not self._memory or not self.session_uuid:
            return
        
        session = self._memory.get_session(self.session_uuid)
        if not session:
            return
        
        # Log performance
        self._memory.log_performance(
            session_id=session.id,
            log_type="simulation_complete",
            message=f"Completed {len(result.rounds)} rounds",
            data={
                "final_consensus": result.final_consensus,
                "duration": result.end_time - result.start_time,
            }
        )
    
    # ========================================================================
    # Data Feed Methods
    # ========================================================================
    
    async def fetch_external_data(
        self,
        news_query: Optional[str] = None,
        market_symbols: Optional[List[str]] = None,
        sentiment_topic: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch external data from all enabled sources.
        
        Args:
            news_query: News query string
            market_symbols: Market symbols for price data
            sentiment_topic: Topic for sentiment analysis
            
        Returns:
            Dictionary with data from all sources
        """
        if self._data_manager is None:
            self._data_manager = DataFeedManager()
        
        return await self._data_manager.fetch_all(
            news_query=news_query,
            market_symbols=market_symbols,
            sentiment_topic=sentiment_topic,
        )
    
    async def get_market_data(
        self,
        symbols: List[str],
        asset_type: str = "crypto",
    ) -> List[MarketPrice]:
        """
        Get market price data for symbols.
        
        Args:
            symbols: List of symbols (e.g., ["BTC", "ETH"])
            asset_type: "crypto" or "stock"
            
        Returns:
            List of MarketPrice objects
        """
        return await fetch_market(symbols, asset_type)
    
    async def get_news(
        self,
        query: Optional[str] = None,
    ) -> List[NewsArticle]:
        """
        Get news articles.
        
        Args:
            query: Search query
            
        Returns:
            List of NewsArticle objects
        """
        return await fetch_news(query)
    
    async def get_sentiment(
        self,
        topic: str,
        platforms: Optional[List[str]] = None,
    ) -> List[SentimentScore]:
        """
        Get social sentiment for a topic.
        
        Args:
            topic: Topic to analyze
            platforms: List of platforms (e.g., ["reddit"])
            
        Returns:
            List of SentimentScore objects
        """
        return await fetch_sentiment(topic, platforms)
    
    # ========================================================================
    # Advanced Analytics Methods
    # ========================================================================
    
    async def monte_carlo(
        self,
        runs: Optional[int] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation for probabilistic analysis.
        
        Args:
            runs: Number of simulations (default from config)
            progress_callback: Optional (completed, total) progress callback
            
        Returns:
            MonteCarloResult with statistical analysis
        """
        runs = runs or self.config.monte_carlo_runs
        simulator = MonteCarloSimulator(agents=self.agents)
        return await simulator.run(
            num_simulations=runs,
            progress_callback=progress_callback,
        )
    
    async def sensitivity_analysis(
        self,
        variables: Optional[List[str]] = None,
        samples: Optional[int] = None,
    ) -> List[SensitivityResult]:
        """
        Perform sensitivity analysis on market variables.
        
        Args:
            variables: List of variable names to analyze
            samples: Number of samples per variable
            
        Returns:
            List of SensitivityResult ranked by impact
        """
        samples = samples or self.config.sensitivity_samples
        analyzer = SensitivityAnalyzer(agents=self.agents)
        return await analyzer.analyze(
            variables=variables,
            num_samples=samples,
        )
    
    async def compare_scenarios(
        self,
        scenario_a: Dict[str, Any],
        scenario_b: Dict[str, Any],
        name_a: str = "Scenario A",
        name_b: str = "Scenario B",
        runs: int = 1000,
    ) -> ScenarioComparison:
        """
        Compare two scenarios statistically.
        
        Args:
            scenario_a: Market data for scenario A
            scenario_b: Market data for scenario B
            name_a: Name for scenario A
            name_b: Name for scenario B
            runs: Number of simulation runs
            
        Returns:
            ScenarioComparison with statistical analysis
        """
        comparator = ScenarioComparator(agents=self.agents)
        return await comparator.compare(
            scenario_a, scenario_b, name_a, name_b, runs
        )
    
    async def backtest(
        self,
        historical_data: List[Dict[str, Any]],
        outcome_key: str = "actual_outcome",
    ) -> BacktestResult:
        """
        Backtest agents against historical data.
        
        Args:
            historical_data: List of market data with actual outcomes
            outcome_key: Key containing actual outcome
            
        Returns:
            BacktestResult with performance metrics
        """
        backtester = Backtester(agents=self.agents)
        return await backtester.backtest(historical_data, outcome_key)
    
    async def run_full_analysis(
        self,
        base_market_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Run complete advanced analysis suite.
        
        Args:
            base_market_data: Starting market conditions
            
        Returns:
            Dictionary with all analysis results
        """
        suite = AdvancedSimulationSuite(agents=self.agents)
        return await suite.run_full_analysis(
            base_market_data=base_market_data,
            num_monte_carlo_runs=self.config.monte_carlo_runs,
        )
    
    # ========================================================================
    # Visualization Methods
    # ========================================================================
    
    def visualize(
        self,
        result: Optional[SimulationResult] = None,
        output_dir: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generate all visualizations.
        
        Args:
            result: Optional result to visualize (uses last_result if None)
            output_dir: Directory to save outputs
            
        Returns:
            Dictionary of exported file paths
        """
        result = result or self.last_result
        if not result:
            raise ValueError("No simulation result to visualize. Run a simulation first.")
        
        output_dir = output_dir or self.config.default_output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        viz = ScalesVisualizer(result, self.agents)
        
        # Print terminal summary
        print("\n" + "=" * 70)
        print("📊 VISUALIZATION SUMMARY")
        print("=" * 70)
        viz.print_terminal_summary()
        
        # Export all formats
        exported = viz.export_all(output_dir, name="swimming_pauls")
        
        print(f"\n📁 Exported to: {output_dir}")
        for key, path in exported.items():
            print(f"   • {key}: {path}")
        
        return exported
    
    def print_terminal_charts(self, result: Optional[SimulationResult] = None) -> None:
        """
        Print ASCII charts to terminal.
        
        Args:
            result: Optional result to visualize
        """
        result = result or self.last_result
        if not result:
            print("No simulation result to visualize.")
            return
        
        viz = ScalesVisualizer(result, self.agents)
        viz.print_terminal_summary()
    
    def generate_html_report(
        self,
        filepath: str,
        result: Optional[SimulationResult] = None,
        title: Optional[str] = None,
    ) -> None:
        """
        Generate interactive HTML report.
        
        Args:
            filepath: Output file path
            result: Optional result to report
            title: Report title
        """
        result = result or self.last_result
        if not result:
            raise ValueError("No simulation result to report.")
        
        viz = ScalesVisualizer(result, self.agents)
        viz.generate_html_report(filepath, title or "SwimmingPauls Report")
    
    def save_charts(
        self,
        output_dir: str,
        result: Optional[SimulationResult] = None,
        prefix: str = "pauls",
    ) -> None:
        """
        Save matplotlib charts to directory.
        
        Args:
            output_dir: Output directory
            result: Optional result to visualize
            prefix: Filename prefix
        """
        result = result or self.last_result
        if not result:
            raise ValueError("No simulation result to visualize.")
        
        viz = ScalesVisualizer(result, self.agents)
        viz.save_all_charts(output_dir, prefix=prefix)
    
    # ========================================================================
    # Agent Management Methods
    # ========================================================================
    
    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the team."""
        self.agents.append(agent)
        
        # Register in memory if enabled
        if self._memory:
            self._memory.register_agent(
                agent_id=agent.id,
                name=agent.name,
                model_name="swimming_pauls",
                agent_type=agent.persona.value,
                config={"bias": agent.bias, "confidence": agent.base_confidence}
            )
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent by ID."""
        for i, agent in enumerate(self.agents):
            if agent.id == agent_id:
                self.agents.pop(i)
                return True
        return False
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents with their stats."""
        return [
            {
                "id": a.id,
                "name": a.name,
                "persona": a.persona.value,
                "accuracy": a.memory.accuracy_score,
                "confidence": a.current_confidence,
                "predictions": len(a.memory.predictions),
            }
            for a in self.agents
        ]
    
    def create_team(
        self,
        analyst: int = 1,
        trader: int = 1,
        hedgie: int = 1,
        visionary: int = 1,
        skeptic: int = 1,
    ) -> None:
        """Create a new team with specified composition."""
        self.agents = create_agent_team(analyst, trader, hedgie, visionary, skeptic)
    
    def create_film_team(
        self,
        producer: int = 1,
        director: int = 1,
        screenwriter: int = 1,
        studio_exec: int = 1,
        indie_filmmaker: int = 1,
    ) -> None:
        """Create a film industry specialized team."""
        self.agents = create_film_industry_team(
            producer, director, screenwriter, studio_exec, indie_filmmaker
        )
    
    # ========================================================================
    # Memory / Persistence Methods
    # ========================================================================
    
    def get_session_history(self) -> List[Session]:
        """Get all simulation sessions from memory."""
        if not self._memory:
            return []
        return self._memory.list_sessions()
    
    def get_accuracy_leaderboard(self) -> List[Dict]:
        """Get agent accuracy leaderboard."""
        if not self._memory:
            return []
        return self._memory.get_leaderboard()
    
    def export_session_data(self, session_uuid: Optional[str] = None) -> Dict:
        """Export all data for a session."""
        if not self._memory:
            return {}
        
        session_uuid = session_uuid or self.session_uuid
        if not session_uuid:
            return {}
        
        return self._memory.export_session_data(session_uuid)
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            "agents": {
                "count": len(self.agents),
                "names": [a.name for a in self.agents],
            },
            "session": {
                "uuid": self.session_uuid,
                "has_result": self.last_result is not None,
            },
            "config": self.config.to_dict(),
            "components": {
                "memory": self._memory is not None,
                "data_manager": self._data_manager is not None,
                "simulation_runner": self._simulation_runner is not None,
            },
        }
    
    def quick_predict(
        self,
        market_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Quick prediction without running full simulation.
        
        Args:
            market_data: Market data dict
            
        Returns:
            Dictionary with consensus and agent predictions
        """
        predictions = []
        for agent in self.agents:
            pred = agent.predict(market_data)
            predictions.append(pred)
        
        # Calculate consensus
        runner = SimulationRunner(agents=self.agents, rounds=1)
        consensus = runner._calculate_consensus(predictions)
        
        return {
            "consensus": consensus,
            "predictions": [
                {
                    "agent": p.agent_id,
                    "direction": p.direction,
                    "confidence": p.confidence,
                    "magnitude": p.magnitude,
                    "reasoning": p.reasoning,
                }
                for p in predictions
            ],
        }
    
    async def close(self) -> None:
        """Close all resources."""
        if self._data_manager:
            await self._data_manager.close()
        if self._memory:
            self._memory.close()


# =============================================================================
# Convenience Functions
# =============================================================================

async def quick_run(
    rounds: int = 10,
    agents: Optional[List[Agent]] = None,
    verbose: bool = True,
) -> Tuple[SimulationResult, SwimmingPauls]:
    """
    Quick run of SwimmingPauls simulation.
    
    Args:
        rounds: Number of rounds
        agents: Optional custom agents
        verbose: Print progress
        
    Returns:
        Tuple of (SimulationResult, SwimmingPauls instance)
    """
    pauls = SwimmingPauls(agents=agents)
    result = await pauls.run_simulation(rounds=rounds)
    
    if verbose:
        pauls.print_terminal_charts()
    
    return result, pauls


async def demo() -> None:
    """Run a comprehensive demo of SwimmingPauls."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║   🏊 SWIMMING PAULS v2.0 - Unified Multi-Agent Simulation        ║
║                                                                   ║
║   The most comprehensive agent-based prediction platform         ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize
    print("\n🚀 Initializing SwimmingPauls...")
    pauls = SwimmingPauls()
    
    print(f"   • Agents: {len(pauls.agents)}")
    print(f"   • Session: {pauls.session_uuid[:8]}...")
    print(f"   • Memory: {'Enabled' if pauls._memory else 'Disabled'}")
    
    # Run basic simulation
    print("\n📊 Running basic simulation...")
    result = await pauls.run_simulation(rounds=10, delay=0.1)
    
    print(f"\n✅ Simulation complete!")
    print(f"   • Duration: {result.end_time - result.start_time:.2f}s")
    print(f"   • Final consensus: {result.final_consensus['direction'].upper()}")
    print(f"   • Sentiment: {result.final_consensus['sentiment']:+.3f}")
    
    # Show terminal visualization
    print("\n" + "=" * 70)
    pauls.print_terminal_charts()
    
    # Run advanced analysis
    print("\n" + "=" * 70)
    print("🔬 Running Monte Carlo analysis...")
    mc_result = await pauls.monte_carlo(runs=1000)
    
    print(f"\n📈 Monte Carlo Results ({mc_result.total_runs} runs):")
    print(f"   • Bullish probability: {mc_result.bullish_probability:.1%}")
    print(f"   • Bearish probability: {mc_result.bearish_probability:.1%}")
    print(f"   • Expected outcome: {mc_result.expected_outcome:+.3f}")
    print(f"   • 95% CI: [{mc_result.confidence_interval_95[0]:+.3f}, {mc_result.confidence_interval_95[1]:+.3f}]")
    
    # Run sensitivity analysis
    print("\n📊 Running sensitivity analysis...")
    sens_results = await pauls.sensitivity_analysis(samples=300)
    
    print("\n🎯 Variable Impact Rankings:")
    for r in sens_results[:5]:
        print(f"   {r.rank}. {r.variable_name}: impact={r.impact_score:.3f}")
    
    # Show final status
    print("\n" + "=" * 70)
    print("📋 Final System Status:")
    status = pauls.get_status()
    print(f"   • Agents: {status['agents']['count']}")
    print(f"   • Session: {status['session']['uuid'][:8]}...")
    print(f"   • Has result: {status['session']['has_result']}")
    
    print("\n✅ Demo complete!")
    
    # Cleanup
    await pauls.close()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Main class
    "SwimmingPauls",
    "SwimmingPaulsConfig",
    
    # Convenience functions
    "quick_run",
    "demo",
    
    # Agent module
    "Agent",
    "AgentPrediction",
    "PersonaType",
    "AgentTrait",
    "create_agent_team",
    "create_film_industry_team",
    "PERSONA_PROFILES",
    
    # Simulation module
    "SimulationRunner",
    "SimulationBuilder",
    "SimulationResult",
    "SimulationRound",
    "quick_simulate",
    
    # Data feeds
    "DataFeedManager",
    "NewsConnector",
    "MarketConnector",
    "SentimentConnector",
    "FileWatcherConnector",
    "NewsArticle",
    "MarketPrice",
    "SentimentScore",
    "FileChange",
    
    # Memory
    "ScalesMemory",
    "Session",
    "Prediction",
    "AccuracyMetrics",
    "init_memory",
    
    # Visualization
    "ScalesVisualizer",
    "TerminalCharts",
    "PlotextCharts",
    "MatplotlibCharts",
    "HTMLReportGenerator",
    "quick_visualize",
    
    # Advanced
    "MonteCarloSimulator",
    "SensitivityAnalyzer",
    "ScenarioComparator",
    "Backtester",
    "AdvancedSimulationSuite",
    "MonteCarloResult",
    "SensitivityResult",
    "ScenarioComparison",
    "BacktestResult",
    
    # Prediction formatting
    "PredictionFormatter",
    "SimulationReporter",
    "SimpleOutput",
]


if __name__ == "__main__":
    asyncio.run(demo())
