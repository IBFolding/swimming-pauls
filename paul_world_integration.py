"""
Paul's World Integration for Swimming Pauls

Main integration module that connects:
- Knowledge Graph construction from seed data
- Graph Memory for agent knowledge storage
- Persistent agent memory
- 1000+ Paul persona generation

Usage:
    from paul_world_integration import PaulWorldSwimmingPauls
    
    pauls = PaulWorldSwimmingPauls()
    pauls.initialize_knowledge_graph("./seed_data")
    pauls.spawn_paul_pool(count=100)
    pauls.run_simulation()

Author: Howard (H.O.W.A.R.D)
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid

# Import Paul's World components
from knowledge_graph import KnowledgeGraph, GraphBuilder, Entity, Relationship
from graph_memory import GraphMemory, GraphMemoryMixin, KnowledgeQuery
from persona_factory import (
    PaulPersonaFactory, generate_swimming_pauls_pool, 
    PaulPersona, TradingStyle, RiskProfile, SpecialtyDomain
)

# Import existing Swimming Pauls
from agent import Agent, PersonaType, PERSONA_PROFILES


@dataclass
class PaulWorldConfig:
    """Configuration for Paul's World-enhanced Swimming Pauls."""
    # Knowledge graph
    seed_data_path: Optional[str] = None
    auto_build_graph: bool = True
    
    # Agent pool
    paul_count: int = 100
    use_diverse_personas: bool = True
    persona_seed: Optional[int] = None
    
    # Memory
    enable_graph_memory: bool = True
    graph_memory_path: str = "~/.scales/graph_memory.db"
    
    # Simulation
    consensus_threshold: float = 0.6
    min_participation: float = 0.5


class PaulWorldAgent(Agent, GraphMemoryMixin):
    """
    Enhanced Swimming Paul with Paul's World capabilities.
    
    Features:
    - Graph-based knowledge storage
    - Persistent memory integration
    - Persona-based decision making
    - Relationship-aware reasoning
    """
    
    def __init__(self, name: str, persona: PersonaType, 
                 paul_persona: Optional[PaulPersona] = None,
                 **kwargs):
        # Store agent memory before calling mixins
        super().__init__(name, persona, **kwargs)
        
        # Don't call GraphMemoryMixin.__init__ - it overwrites self.memory
        # Instead set our own attributes
        self.graph_memory: Optional[GraphMemory] = None
        self._agent_graph_memory_id: Optional[str] = None
        
        self.paul_persona = paul_persona
        self.specialties: List[str] = []
        
        if paul_persona:
            self.specialties = [s.value for s in paul_persona.specialties]
            self._apply_paul_traits()
    
    def _apply_paul_traits(self):
        """Apply Paul persona traits to the agent."""
        if not self.paul_persona:
            return
        
        pp = self.paul_persona
        
        # Override base confidence
        self.current_confidence = pp.confidence_base
        self.base_confidence = pp.confidence_base
        self.adaptability = pp.adaptability
        
        # Risk affects bias
        risk_val = pp.risk_profile.value
        self.bias = (risk_val - 0.5) * 0.6  # Scale to roughly -0.3 to 0.3
    
    def attach_graph_memory(self, memory: GraphMemory, agent_id: Optional[str] = None):
        """Attach a graph memory to this agent."""
        self.graph_memory = memory
        self._agent_graph_memory_id = agent_id or getattr(self, 'id', str(uuid.uuid4()))
    
    def predict_with_context(self, market_data: Dict[str, Any],
                            context_depth: int = 2) -> Dict[str, Any]:
        """
        Generate prediction with knowledge context.
        
        Uses graph memory to find relevant knowledge and
        incorporates it into the prediction.
        """
        # Get base prediction
        prediction = self.predict(market_data)
        
        # Get knowledge context if memory attached
        knowledge_context = {}
        if self.graph_memory:
            # Extract entities from market data
            market_entities = self._extract_market_entities(market_data)
            knowledge_context = self.graph_memory.get_context_for_prediction(self._agent_graph_memory_id, market_entities, context_depth)
        
        # Enhance prediction with context
        enhanced_reasoning = self._enhance_reasoning(
            prediction.reasoning, knowledge_context
        )
        
        # Store in memories
        if self.graph_memory:
            self.graph_memory.add_observation(self._agent_graph_memory_id, 
                "prediction",
                f"Predicted {prediction.direction} for market with {prediction.confidence:.0%} confidence",
                confidence=prediction.confidence
            )
        
        return {
            'agent_id': prediction.agent_id,
            'agent_name': self.name,
            'direction': prediction.direction,
            'confidence': prediction.confidence,
            'magnitude': prediction.magnitude,
            'reasoning': enhanced_reasoning,
            'timestamp': prediction.timestamp,
            'knowledge_context': knowledge_context,
            'specialties': self.specialties
        }
    
    def _extract_market_entities(self, market_data: Dict) -> List[str]:
        """Extract entity IDs from market data."""
        entities = []
        
        # Look for known assets/entities
        if 'asset' in market_data:
            entities.append(f"asset_{market_data['asset'].lower()}")
        if 'token' in market_data:
            entities.append(f"token_{market_data['token'].lower()}")
        if 'market' in market_data:
            entities.append(f"market_{market_data['market'].lower()}")
        
        return entities
    
    def _enhance_reasoning(self, base_reasoning: str,
                          knowledge_context: Dict) -> str:
        """Enhance reasoning with knowledge context."""
        parts = [base_reasoning]
        
        # Add knowledge-based insights
        if knowledge_context.get('direct_knowledge'):
            parts.append("Drawing from known entities in the market.")
        
        if knowledge_context.get('related_entities'):
            related = knowledge_context['related_entities']
            known = [r for r in related if r.get('known')]
            if known:
                parts.append(f"Considering {len(known)} related entities I know about.")
        
        return " ".join(parts)
    
    def learn_from_market(self, entity: Entity, relationship: Optional[Relationship] = None):
        """Learn about a market entity."""
        self.learn_entity(entity, belief=0.8, source="market_observation")
        if relationship:
            self.learn_relationship(relationship, belief=0.7)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export agent state to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'persona': self.persona.value,
            'paul_persona': {
                'trading_style': self.paul_persona.trading_style.value if self.paul_persona else None,
                'risk_profile': self.paul_persona.risk_profile.name if self.paul_persona else None,
                'specialties': self.specialties,
                'backstory': self.paul_persona.backstory if self.paul_persona else None,
                'catchphrase': self.paul_persona.catchphrase if self.paul_persona else None,
            } if self.paul_persona else None,
            'confidence': self.current_confidence,
            'accuracy': self.memory.accuracy_score if hasattr(self, 'memory') else 0.5,
            'total_predictions': len(self.memory.predictions) if hasattr(self, 'memory') else 0
        }


class PaulWorldSwimmingPauls:
    """
    Main Paul's World integration for Swimming Pauls simulation.
    
    Manages:
    - Knowledge graph construction
    - Agent pool generation
    - Memory systems
    - Simulation execution
    """
    
    def __init__(self, config: Optional[PaulWorldConfig] = None):
        self.config = config or PaulWorldConfig()
        
        # Knowledge systems
        self.knowledge_graph: Optional[KnowledgeGraph] = None
        self.graph_memory: Optional[GraphMemory] = None
        
        # Agents
        self.agents: List[PaulWorldAgent] = []
        self.persona_factory = PaulPersonaFactory(seed=self.config.persona_seed)
        
        # State
        self.initialized = False
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def initialize(self) -> bool:
        """Initialize all Paul's World components."""
        print("🌍 Initializing Paul's World Swimming Pauls...")
        
        # Initialize graph memory
        if self.config.enable_graph_memory:
            self.graph_memory = GraphMemory(db_path=self.config.graph_memory_path)
            print(f"  ✓ Graph memory initialized")
        
        # Build knowledge graph from seed data
        if self.config.auto_build_graph and self.config.seed_data_path:
            self.initialize_knowledge_graph(self.config.seed_data_path)
        
        self.initialized = True
        print("🌍 Paul's World initialization complete!")
        return True
    
    def initialize_knowledge_graph(self, seed_path: str) -> KnowledgeGraph:
        """Build knowledge graph from seed data."""
        print(f"📚 Building knowledge graph from {seed_path}...")
        
        builder = GraphBuilder(name="swimming_pauls_knowledge")
        builder.add_directory(seed_path, extensions=['.txt', '.md', '.json', '.pdf'])
        
        self.knowledge_graph = builder.build()
        
        # Import into graph memory
        if self.graph_memory:
            self.graph_memory.import_knowledge_graph(
                self.knowledge_graph,
                teaching_agents=[]  # Will teach agents as they're created
            )
        
        print(f"  ✓ Knowledge graph: {len(self.knowledge_graph.entities)} entities, "
              f"{len(self.knowledge_graph.relationships)} relationships")
        
        return self.knowledge_graph
    
    def spawn_paul(self, persona_data: Optional[Dict] = None,
                  persona_type: Optional[PersonaType] = None,
                  paul_persona: Optional[PaulPersona] = None) -> PaulWorldAgent:
        """Spawn a single Paul's World-enhanced Paul."""
        
        # Use provided Paul persona or create one
        if paul_persona is None:
            paul_persona = self.persona_factory.create_persona()
        
        # Map Paul trading style to base persona type
        style_to_persona = {
            TradingStyle.SCALPER: PersonaType.TRADER,
            TradingStyle.SWING_TRADER: PersonaType.TRADER,
            TradingStyle.POSITION_TRADER: PersonaType.HEDGIE,
            TradingStyle.ALGORITHMIC: PersonaType.ANALYST,
            TradingStyle.QUANTITATIVE: PersonaType.ANALYST,
            TradingStyle.EVENT_DRIVEN: PersonaType.VISIONARY,
            TradingStyle.MOMENTUM: PersonaType.TRADER,
            TradingStyle.CONTRARIAN: PersonaType.SKEPTIC,
            TradingStyle.VALUE: PersonaType.ANALYST,
        }
        
        base_persona = persona_type or style_to_persona.get(
            paul_persona.trading_style, PersonaType.ANALYST
        )
        
        # Create agent
        agent = PaulWorldAgent(
            name=paul_persona.name,
            persona=base_persona,
            paul_persona=paul_persona,
            custom_bias=(paul_persona.risk_profile.value - 0.5) * 0.5,
            custom_confidence=paul_persona.confidence_base
        )
        
        # Attach memories
        if self.graph_memory:
            agent.attach_graph_memory(self.graph_memory, agent_id=agent.id)
            
            # Teach agent about relevant entities based on specialties
            if self.knowledge_graph:
                for specialty in paul_persona.specialties:
                    relevant = self.knowledge_graph.query_entities(
                        entity_type=specialty.value.upper()
                    )
                    for entity in relevant[:10]:  # Top 10 per specialty
                        self.graph_memory.teach_agent(
                            agent.id, entity.id,
                            belief_strength=0.7,
                            source="specialty_knowledge"
                        )
        
        return agent
    
    def spawn_paul_pool(self, count: Optional[int] = None) -> List[PaulWorldAgent]:
        """Spawn a diverse pool of Pauls."""
        count = count or self.config.paul_count
        print(f"🎣 Spawning {count} Swimming Pauls...")
        
        if self.config.use_diverse_personas:
            # Generate diverse pool
            personas = self.persona_factory.create_diverse_pool(total_count=count)
        else:
            # Generate random pool
            personas = [self.persona_factory.create_persona() for _ in range(count)]
        
        # Spawn agents
        for paul_persona in personas:
            agent = self.spawn_paul(paul_persona=paul_persona)
            self.agents.append(agent)
        
        print(f"  ✓ Spawned {len(self.agents)} agents")
        
        # Print distribution
        self._print_agent_distribution()
        
        return self.agents
    
    def _print_agent_distribution(self):
        """Print statistics about the agent pool."""
        from collections import Counter
        
        styles = Counter(a.paul_persona.trading_style.value for a in self.agents if a.paul_persona)
        risks = Counter(a.paul_persona.risk_profile.name for a in self.agents if a.paul_persona)
        
        print("\n  Agent Distribution:")
        print("  Trading Styles:")
        for style, count in styles.most_common():
            print(f"    - {style}: {count}")
        print("  Risk Profiles:")
        for risk, count in risks.most_common():
            print(f"    - {risk}: {count}")
    
    def run_prediction_round(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run a prediction round with all agents."""
        if not self.agents:
            raise ValueError("No agents spawned. Call spawn_paul_pool() first.")
        
        predictions = []
        
        for agent in self.agents:
            try:
                pred = agent.predict_with_context(market_data)
                predictions.append(pred)
            except Exception as e:
                print(f"Error from {agent.name}: {e}")
        
        # Calculate consensus
        bullish = sum(1 for p in predictions if p['direction'] == 'bullish')
        bearish = sum(1 for p in predictions if p['direction'] == 'bearish')
        neutral = sum(1 for p in predictions if p['direction'] == 'neutral')
        
        total = len(predictions)
        if total == 0:
            return {
                'session_id': self.session_id,
                'timestamp': datetime.now().isoformat(),
                'market_data': market_data,
                'predictions': [],
                'consensus': {'bullish': 0, 'bearish': 0, 'neutral': 0, 'dominant': 'none', 'confidence': 0},
                'average_confidence': 0,
                'participation_rate': 0,
                'agent_count': len(self.agents),
                'error': 'No predictions generated'
            }
        
        consensus = {
            'bullish': bullish / total,
            'bearish': bearish / total,
            'neutral': neutral / total,
            'dominant': max(['bullish', 'bearish', 'neutral'], 
                          key=lambda x: {'bullish': bullish, 'bearish': bearish, 'neutral': neutral}[x]),
            'confidence': max(bullish, bearish, neutral) / total
        }
        
        # Weighted confidence by agent confidence
        avg_confidence = sum(p['confidence'] for p in predictions) / total
        
        return {
            'session_id': self.session_id,
            'timestamp': datetime.now().isoformat(),
            'market_data': market_data,
            'predictions': predictions,
            'consensus': consensus,
            'average_confidence': avg_confidence,
            'participation_rate': len(predictions) / len(self.agents),
            'agent_count': len(self.agents)
        }
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge systems."""
        stats = {
            'agents': len(self.agents),
            'knowledge_graph': None,
            'graph_memory': None
        }
        
        if self.knowledge_graph:
            stats['knowledge_graph'] = {
                'entities': len(self.knowledge_graph.entities),
                'relationships': len(self.knowledge_graph.relationships),
            }
        
        if self.graph_memory:
            stats['graph_memory'] = self.graph_memory.get_statistics()
        
        return stats
    
    def export_agents(self, path: Optional[str] = None) -> List[Dict]:
        """Export all agent data."""
        data = [agent.to_dict() for agent in self.agents]
        
        if path:
            Path(path).write_text(json.dumps(data, indent=2, default=str))
        
        return data
    
    def cleanup(self):
        """Cleanup resources."""
        if self.graph_memory:
            self.graph_memory.close()


# ============================================================================
# QUICK START FUNCTIONS
# ============================================================================

def quick_start(seed_data_path: Optional[str] = None,
               paul_count: int = 100) -> PaulWorldSwimmingPauls:
    """
    Quick start function to get Paul's World Swimming Pauls running.
    
    Args:
        seed_data_path: Path to seed data for knowledge graph
        paul_count: Number of Pauls to spawn
    
    Returns:
        Initialized PaulWorldSwimmingPauls instance
    """
    config = PaulWorldConfig(
        seed_data_path=seed_data_path,
        paul_count=paul_count
    )
    
    paul_world = PaulWorldSwimmingPauls(config)
    paul_world.initialize()
    paul_world.spawn_paul_pool()
    
    return paul_world


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Paul's World Swimming Pauls - Integration Demo")
    print("=" * 60)
    
    # Initialize without seed data for demo
    config = PaulWorldConfig(
        seed_data_path=None,  # Set to a path to load seed data
        paul_count=10,  # Demo with 10 Pauls
        enable_graph_memory=True
    )
    
    paul_world = PaulWorldSwimmingPauls(config)
    paul_world.initialize()
    paul_world.spawn_paul_pool()
    
    # Run a demo prediction
    demo_market = {
        'market_id': 'BTC_USD_2024',
        'asset': 'BTC',
        'price_trend': 0.15,
        'volume': 0.8,
        'sentiment': 0.6,
        'volatility': 0.4
    }
    
    print("\n" + "=" * 60)
    print("Running Demo Prediction Round")
    print("=" * 60)
    
    result = paul_world.run_prediction_round(demo_market)
    
    print(f"\nConsensus: {result['consensus']['dominant'].upper()}")
    print(f"Confidence: {result['consensus']['confidence']:.1%}")
    print(f"Participation: {result['participation_rate']:.1%}")
    
    print("\nTop 5 Predictions:")
    sorted_preds = sorted(
        result['predictions'],
        key=lambda x: x['confidence'],
        reverse=True
    )[:5]
    
    for pred in sorted_preds:
        print(f"  {pred['agent_name']}: {pred['direction'].upper()} "
              f"({pred['confidence']:.0%}) - {pred['reasoning'][:60]}...")
    
    # Show stats
    print("\n" + "=" * 60)
    print("System Statistics")
    print("=" * 60)
    stats = paul_world.get_knowledge_stats()
    print(f"Agents: {stats['agents']}")
    if stats['graph_memory']:
        print(f"Graph Memory Entities: {stats['graph_memory'].get('total_entities', 0)}")
    
    # Cleanup
    paul_world.cleanup()
    
    print("\n✓ Demo complete!")
