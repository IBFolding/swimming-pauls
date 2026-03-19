"""
SwimmingPauls v2.0 - 100% Local Multi-Agent Simulation Platform

A comprehensive platform for multi-agent prediction and analysis.

✅ 100% LOCAL - NO API KEYS REQUIRED:
- Agent-based predictions with personas
- Simulation orchestration  
- 🎯 Dual Platform: Parallel simulations across configurations for higher confidence
- Local data feeds (RSS, files, web scraping, demo mode)
- Persistent SQLite memory
- Rich terminal visualizations
- Advanced analytics (Monte Carlo, sensitivity, backtesting)
- 🌍 Paul's World: Knowledge graphs, graph memory, 1000+ Paul personas

All functionality works offline with local computation only.
Optional cloud features are truly optional.

Quick Start:
    from swimming_pauls import SwimmingPauls
    
    pauls = SwimmingPauls()
    result = await pauls.run_simulation(rounds=20)
    pauls.visualize()

Dual Platform Quick Start:
    from swimming_pauls import DualPlatformSimulator, DualPlatformBuilder
    
    # Run parallel simulations across different configurations
    simulator = (DualPlatformBuilder()
        .add_conservative_platform()
        .add_aggressive_platform()
        .add_balanced_platform()
        .build())
    
    result = await simulator.run()
    print(result.dual_consensus.direction)
    print(result.dual_consensus.confidence)

Paul's World Quick Start:
    from swimming_pauls import PaulWorldSwimmingPauls
    
    # 100% local - no internet needed
    paul_world = PaulWorldSwimmingPauls.quick_start(paul_count=100)
    result = paul_world.run_prediction_round(market_data)

CLI Usage:
    python -m swimming_pauls --rounds 20
    python -m swimming_pauls --live --market BTC,ETH
    python -m swimming_pauls --monte-carlo --mc-runs 5000
"""

__version__ = "2.0.0"
__author__ = "Howard (H.O.W.A.R.D)"

# Import the unified system
from .swimming_pauls import (
    SwimmingPauls,
    SwimmingPaulsConfig,
    quick_run,
    demo,
)

# Import all agent-related classes
from .agent import (
    Agent,
    AgentPrediction,
    AgentMemory,
    AgentTrait,
    PersonaType,
    PERSONA_PROFILES,
    create_agent_team,
    create_film_industry_team,
)

# Import simulation classes
from .simulation import (
    SimulationRunner,
    SimulationBuilder,
    SimulationResult,
    SimulationRound,
    quick_simulate,
)

# Import data feed classes
from .data_feeds import (
    DataFeedManager,
    DataConnector,
    NewsConnector,
    MarketConnector,
    SentimentConnector,
    FileWatcherConnector,
    NewsArticle,
    MarketPrice,
    SentimentScore,
    FileChange,
    fetch_news,
    fetch_market,
    fetch_sentiment,
    watch_files,
)

# Import 100% LOCAL data feed classes (no API keys needed)
from .local_data_feeds import (
    LocalNewsConnector,
    LocalMarketConnector,
    LocalSentimentConnector,
    LocalDataFeedManager,
    fetch_local_news,
    fetch_local_market,
    fetch_local_sentiment,
    watch_local_files,
)

# Import memory classes
from .memory import (
    ScalesMemory,
    Session,
    Agent as MemoryAgent,
    Prediction,
    AccuracyMetrics,
    ModelAdjustment,
    init_memory,
)

# Import visualization classes
from .visualization import (
    ScalesVisualizer,
    TerminalCharts,
    PlotextCharts,
    MatplotlibCharts,
    HTMLReportGenerator,
    HTMLReportConfig,
    quick_visualize,
    print_confidence_chart,
    print_sentiment_timeline,
    print_agent_ranking,
)

# Import advanced analytics classes
from .advanced import (
    MonteCarloSimulator,
    SensitivityAnalyzer,
    ScenarioComparator,
    Backtester,
    AdvancedSimulationSuite,
    MonteCarloResult,
    SensitivityResult,
    ScenarioComparison,
    BacktestResult,
    quick_monte_carlo,
    quick_sensitivity,
    quick_compare,
    quick_backtest,
)

# Import prediction formatting
from .prediction import (
    PredictionFormatter,
    SimulationReporter,
    SimpleOutput,
    print_report,
    export_json,
)

# 🎯 Dual Platform Simulation
from .dual_platform import (
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

# 🌍 Paul's World Imports - Knowledge Graph & Memory
from .knowledge_graph import (
    KnowledgeGraph,
    Entity,
    Relationship,
    GraphBuilder,
    EntityExtractor,
    create_market_knowledge_graph,
)

from .graph_memory import (
    GraphMemory,
    AgentKnowledge,
    KnowledgeQuery,
    GraphMemoryMixin,
)

from .persona_factory import (
    PaulPersonaFactory,
    PaulPersona,
    TradingStyle,
    RiskProfile,
    SpecialtyDomain,
    generate_swimming_pauls_pool,
    PAUL_ARCHETYPES,
)

from .paul_world_integration import (
    PaulWorldSwimmingPauls,
    PaulWorldConfig,
    PaulWorldAgent,
    quick_start,
)

# Optional memory integrations
try:
    from .zep_memory import (
        ZepMemoryManager,
        ZepMemoryConfig,
        AgentZepSession,
        MemoryFact,
        create_memory_manager,
    )
    ZEP_AVAILABLE = True
except ImportError:
    ZEP_AVAILABLE = False

# ReportAgent - Automated report generation with skill integration
try:
    from .report_agent import (
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
        format_report_markdown,
        format_report_html,
    )
    from .report_api import (
        ReportAPIServer,
        ReportAPIHandler,
        start_report_api,
    )
    REPORT_AGENT_AVAILABLE = True
except ImportError as e:
    REPORT_AGENT_AVAILABLE = False

# 🧠 Temporal Memory - Dynamic belief evolution
try:
    from .temporal_memory import (
        TemporalMemory,
        TemporalMemoryManager,
        Belief,
        BeliefStatus,
        Evidence,
        TemporalContext,
        create_temporal_prediction_reasoning,
        simulate_belief_evolution,
    )
    from .temporal_integration import (
        TemporalPaulState,
        TemporalPaulWorld,
        create_temporal_world,
        quick_temporal_simulation,
    )
    TEMPORAL_MEMORY_AVAILABLE = True
except ImportError as e:
    TEMPORAL_MEMORY_AVAILABLE = False

__all__ = [
    # Version
    "__version__",
    
    # Main unified system
    "SwimmingPauls",
    "SwimmingPaulsConfig",
    "quick_run",
    "demo",
    
    # Agent module
    "Agent",
    "AgentPrediction",
    "AgentMemory",
    "AgentTrait",
    "PersonaType",
    "PERSONA_PROFILES",
    "create_agent_team",
    "create_film_industry_team",
    
    # Simulation module
    "SimulationRunner",
    "SimulationBuilder",
    "SimulationResult",
    "SimulationRound",
    "quick_simulate",
    
    # Data feeds
    "DataFeedManager",
    "DataConnector",
    "NewsConnector",
    "MarketConnector",
    "SentimentConnector",
    "FileWatcherConnector",
    "NewsArticle",
    "MarketPrice",
    "SentimentScore",
    "FileChange",
    "fetch_news",
    "fetch_market",
    "fetch_sentiment",
    "watch_files",
    
    # 100% LOCAL Data feeds (no API keys)
    "LocalNewsConnector",
    "LocalMarketConnector",
    "LocalSentimentConnector",
    "LocalDataFeedManager",
    "fetch_local_news",
    "fetch_local_market",
    "fetch_local_sentiment",
    "watch_local_files",
    
    # Memory
    "ScalesMemory",
    "Session",
    "MemoryAgent",
    "Prediction",
    "AccuracyMetrics",
    "ModelAdjustment",
    "init_memory",
    
    # Visualization
    "ScalesVisualizer",
    "TerminalCharts",
    "PlotextCharts",
    "MatplotlibCharts",
    "HTMLReportGenerator",
    "HTMLReportConfig",
    "quick_visualize",
    "print_confidence_chart",
    "print_sentiment_timeline",
    "print_agent_ranking",
    
    # Advanced analytics
    "MonteCarloSimulator",
    "SensitivityAnalyzer",
    "ScenarioComparator",
    "Backtester",
    "AdvancedSimulationSuite",
    "MonteCarloResult",
    "SensitivityResult",
    "ScenarioComparison",
    "BacktestResult",
    "quick_monte_carlo",
    "quick_sensitivity",
    "quick_compare",
    "quick_backtest",
    
    # 🎯 Dual Platform Simulation
    "PlatformType",
    "PlatformConfig",
    "PlatformResult",
    "DualPlatformConsensus",
    "DualPlatformResult",
    "PlatformAgentFactory",
    "DualPlatformSimulator",
    "DualPlatformBuilder",
    "DualPlatformChatInterface",
    "quick_dual_simulation",
    
    # Prediction formatting
    "PredictionFormatter",
    "SimulationReporter",
    "SimpleOutput",
    "print_report",
    "export_json",
    
    # 🌍 Paul's World - Knowledge Graph
    "KnowledgeGraph",
    "Entity",
    "Relationship",
    "GraphBuilder",
    "EntityExtractor",
    "create_market_knowledge_graph",
    
    # 🌍 Paul's World - Graph Memory
    "GraphMemory",
    "AgentKnowledge",
    "KnowledgeQuery",
    "GraphMemoryMixin",
    
    # 🌍 Paul's World - Persona Factory
    "PaulPersonaFactory",
    "PaulPersona",
    "TradingStyle",
    "RiskProfile",
    "SpecialtyDomain",
    "generate_swimming_pauls_pool",
    "PAUL_ARCHETYPES",
    
    # 🌍 Paul's World - Integration
    "PaulWorldSwimmingPauls",
    "PaulWorldConfig",
    "PaulWorldAgent",
    "quick_start",
    
    # 🧠 Temporal Memory - Dynamic belief evolution
    "TemporalMemory",
    "TemporalMemoryManager",
    "Belief",
    "BeliefStatus",
    "Evidence",
    "TemporalContext",
    "TemporalPaulState",
    "TemporalPaulWorld",
    "create_temporal_world",
    "quick_temporal_simulation",
    "create_temporal_prediction_reasoning",
    "simulate_belief_evolution",
    
    # ReportAgent
    "ReportAgent",
    "ReportCompiler",
    "ReportStorage",
    "SkillIntegrator",
    "ReportFormatter",
    "Report",
    "ReportMetadata",
    "ConsensusSummary",
    "AgentReasoning",
    "SkillData",
    "ReportFormat",
    "quick_report",
    "format_report_markdown",
    "format_report_html",
    "ReportAPIServer",
    "ReportAPIHandler",
    "start_report_api",
]
