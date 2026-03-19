"""
Temporal Memory Integration for PaulWorld

Integrates the TemporalMemory system with PaulWorld simulation.
Allows Pauls to have dynamic beliefs that evolve over simulation time.

Author: Howard (H.O.W.A.R.D)
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

# Import temporal memory
from temporal_memory import (
    TemporalMemory,
    TemporalMemoryManager,
    TemporalContext,
    BeliefStatus,
    create_temporal_prediction_reasoning,
)

# Import PaulWorld components
from paul_world import PaulState, PaulWorld, Activity, Location


class TemporalPaulState:
    """
    Wrapper that adds temporal memory capabilities to a PaulState.
    
    This extends PaulState with:
    - Dynamic beliefs that evolve over time
    - Temporal context in predictions
    - Belief formation from knowledge and experiences
    """
    
    def __init__(self, paul_state: PaulState, temporal_memory: TemporalMemory):
        self.paul = paul_state
        self.memory = temporal_memory
        self.last_decay_time = datetime.now()
        self.decay_interval_hours = 24  # Decay beliefs every 24 sim hours
    
    @property
    def name(self) -> str:
        return self.paul.name
    
    @property
    def emoji(self) -> str:
        return self.paul.emoji
    
    @property
    def specialty(self) -> str:
        return self.paul.specialty
    
    def form_beliefs_from_knowledge(self) -> List[str]:
        """
        Convert knowledge into temporal beliefs.
        
        When Paul learns something, it becomes a belief that can evolve.
        """
        formed_topics = []
        
        for knowledge in self.paul.knowledge:
            # Check if we already have an active belief on this topic
            existing = self.memory.get_belief(knowledge.topic)
            if existing and existing.status == BeliefStatus.ACTIVE:
                # Reinforce existing belief with this knowledge
                self.memory.add_evidence(
                    topic=knowledge.topic,
                    content=knowledge.content[:100],
                    impact=knowledge.confidence * 0.5,
                    source=f"knowledge:{knowledge.source}",
                    reliability=knowledge.confidence,
                )
            else:
                # Form new belief from knowledge
                proposition = self._knowledge_to_proposition(knowledge.topic, knowledge.content)
                self.memory.form_belief(
                    topic=knowledge.topic,
                    proposition=proposition,
                    initial_confidence=knowledge.confidence,
                    source_reliability=0.7,
                )
                formed_topics.append(knowledge.topic)
        
        return formed_topics
    
    def _knowledge_to_proposition(self, topic: str, content: str) -> str:
        """Convert knowledge content to a belief proposition."""
        # Extract a simple proposition from knowledge content
        # In a real implementation, this might use LLM summarization
        
        content_lower = content.lower()
        
        # Pattern matching for common belief types
        if any(word in content_lower for word in ['bullish', 'up', 'growth', 'increase', 'rise']):
            return f"{topic} will perform positively"
        elif any(word in content_lower for word in ['bearish', 'down', 'decline', 'fall', 'crash']):
            return f"{topic} will perform negatively"
        elif any(word in content_lower for word in ['stable', 'neutral', 'flat', 'sideways']):
            return f"{topic} will remain stable"
        elif any(word in content_lower for word in ['volatile', 'uncertain', 'risky']):
            return f"{topic} will be volatile"
        else:
            return f"{topic} shows interesting patterns"
    
    def process_memory_to_beliefs(self) -> List[str]:
        """
        Convert experiences (memories) into beliefs and evidence.
        
        Past predictions and experiences shape beliefs.
        """
        updated_topics = []
        
        for mem in self.paul.memories[:10]:  # Process recent memories
            # Convert memory to potential evidence
            if mem.event_type == "prediction":
                # Extract topic from memory description
                topic = self._extract_topic_from_memory(mem.description)
                if topic:
                    # Successful predictions reinforce beliefs
                    if mem.accuracy and mem.accuracy > 0.6:
                        self.memory.add_evidence(
                            topic=topic,
                            content=mem.description,
                            impact=mem.accuracy * 0.5,
                            source="memory:prediction",
                            reliability=mem.accuracy,
                        )
                        updated_topics.append(topic)
                    # Failed predictions challenge beliefs
                    elif mem.accuracy and mem.accuracy < 0.4:
                        self.memory.add_evidence(
                            topic=topic,
                            content=mem.description,
                            impact=-0.3,
                            source="memory:prediction",
                            reliability=1.0 - mem.accuracy,
                        )
                        updated_topics.append(topic)
            
            elif mem.event_type == "market_event":
                topic = self._extract_topic_from_memory(mem.description)
                if topic:
                    impact = mem.sentiment * 0.3
                    self.memory.add_evidence(
                        topic=topic,
                        content=mem.description,
                        impact=impact,
                        source="memory:market",
                        reliability=0.6,
                    )
                    updated_topics.append(topic)
        
        return updated_topics
    
    def _extract_topic_from_memory(self, description: str) -> Optional[str]:
        """Extract topic from memory description."""
        # Simple keyword extraction
        topic_keywords = {
            'bitcoin': 'BTC',
            'btc': 'BTC',
            'ethereum': 'ETH',
            'eth': 'ETH',
            'market': 'market',
            'defi': 'DeFi',
            'nft': 'NFT',
            'ai': 'AI',
            'regulation': 'regulation',
        }
        
        desc_lower = description.lower()
        for keyword, topic in topic_keywords.items():
            if keyword in desc_lower:
                return topic
        
        return 'general'
    
    def update_beliefs_from_activity(self, world_time: datetime) -> Dict[str, Any]:
        """
        Update beliefs based on current activity and world state.
        
        Called during each simulation tick.
        """
        results = {
            'decayed': [],
            'reinforced': [],
            'abandoned': [],
        }
        
        # Apply time decay periodically
        hours_since_decay = (world_time - self.last_decay_time).total_seconds() / 3600
        if hours_since_decay >= self.decay_interval_hours:
            decayed = self.memory.decay_beliefs(world_time)
            for belief in decayed:
                if belief.status == BeliefStatus.ABANDONED:
                    results['abandoned'].append(belief.topic)
                else:
                    results['decayed'].append(belief.topic)
            self.last_decay_time = world_time
        
        # Activity-specific belief updates
        if self.paul.activity == Activity.RESEARCHING:
            # Research reinforces curiosity-driven beliefs
            for belief in self.memory.get_all_active_beliefs():
                if self.paul.curiosity > 0.7:
                    self.memory.add_evidence(
                        topic=belief.topic,
                        content="Additional research findings",
                        impact=0.1 * self.paul.curiosity,
                        source="activity:research",
                        reliability=0.6,
                    )
                    results['reinforced'].append(belief.topic)
        
        elif self.paul.activity == Activity.TRADING:
            # Trading activity creates market beliefs
            market_belief = self.memory.get_belief("market")
            if market_belief and self.paul.accuracy_score > 0.6:
                self.memory.add_evidence(
                    topic="market",
                    content="Trading experience",
                    impact=0.1 * self.paul.accuracy_score,
                    source="activity:trading",
                    reliability=self.paul.accuracy_score,
                )
                results['reinforced'].append("market")
        
        elif self.paul.activity == Activity.ANALYZING:
            # Analysis validates existing beliefs
            for belief in self.memory.get_all_active_beliefs():
                self.memory.add_evidence(
                    topic=belief.topic,
                    content="Analysis validation",
                    impact=0.05,
                    source="activity:analysis",
                    reliability=0.5,
                )
                results['reinforced'].append(belief.topic)
        
        return results
    
    def get_temporal_prediction(
        self,
        topic: str,
        base_sentiment: str,
        base_confidence: float,
        base_reasoning: str
    ) -> Dict[str, Any]:
        """
        Generate a prediction with temporal context.
        
        Creates the "3 days ago I thought X, now I think Y" style output.
        """
        # Get or create temporal context
        temporal_context = self.memory.get_temporal_context(topic)
        
        if not temporal_context:
            # No prior belief, form one now
            proposition = f"{topic} is looking {base_sentiment}"
            self.memory.form_belief(
                topic=topic,
                proposition=proposition,
                initial_confidence=base_confidence,
                source_reliability=0.5,
            )
            temporal_context = self.memory.get_temporal_context(topic)
        
        # Adjust confidence based on belief evolution
        adjusted_confidence = base_confidence
        if temporal_context:
            # Recent reinforcement increases confidence
            if temporal_context.belief_shift > 0:
                adjusted_confidence = min(0.95, base_confidence + temporal_context.belief_shift * 0.2)
            # Recent challenges decrease confidence
            elif temporal_context.belief_shift < -0.2:
                adjusted_confidence = base_confidence * 0.8
        
        # Create temporal reasoning
        temporal_reasoning = ""
        if temporal_context:
            temporal_reasoning = create_temporal_prediction_reasoning(
                temporal_context,
                base_reasoning
            )
        
        return {
            'sentiment': base_sentiment,
            'confidence': adjusted_confidence,
            'reasoning': temporal_reasoning or base_reasoning,
            'temporal_context': temporal_context.to_dict() if temporal_context else None,
            'belief_age_hours': temporal_context.time_span_hours if temporal_context else 0,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Export temporal Paul state."""
        return {
            'paul': self.paul.to_dict(),
            'temporal_memory': self.memory.to_dict(),
        }


class TemporalPaulWorld:
    """
    Extension of PaulWorld that integrates TemporalMemory.
    
    Manages temporal memory for all Pauls and coordinates belief evolution.
    """
    
    def __init__(self, paul_world: PaulWorld, db_path: str = "data/temporal_memory.db"):
        self.world = paul_world
        self.memory_manager = TemporalMemoryManager(db_path=db_path)
        self.temporal_pauls: Dict[str, TemporalPaulState] = {}
        
        # Initialize temporal memory for each Paul
        self._initialize_temporal_pauls()
    
    def _initialize_temporal_pauls(self):
        """Create temporal memory wrappers for all Pauls."""
        for name, paul_state in self.world.pauls.items():
            temporal_memory = self.memory_manager.get_memory(name)
            self.temporal_pauls[name] = TemporalPaulState(paul_state, temporal_memory)
    
    async def tick(self):
        """
        Advance world by one tick with temporal memory updates.
        """
        # Run normal world tick
        await self.world.tick()
        
        # Update temporal memories
        for name, temporal_paul in self.temporal_pauls.items():
            # Form beliefs from new knowledge
            temporal_paul.form_beliefs_from_knowledge()
            
            # Process memories into beliefs
            temporal_paul.process_memory_to_beliefs()
            
            # Update beliefs based on activity
            temporal_paul.update_beliefs_from_activity(self.world.world_time)
        
        # Apply decay to all beliefs periodically
        if self.world.tick_count % 24 == 0:  # Daily decay
            self.memory_manager.decay_all(self.world.world_time)
        
        # Social influence between Pauls
        if self.world.tick_count % 6 == 0:  # Every 6 hours
            await self._process_social_influence()
    
    async def _process_social_influence(self):
        """
        Process social influence between Pauls at the same location.
        
        Pauls can influence each other's beliefs.
        """
        # Group Pauls by location
        location_groups: Dict[Location, List[str]] = {}
        for name, paul in self.world.pauls.items():
            if paul.location not in location_groups:
                location_groups[paul.location] = []
            location_groups[paul.location].append(name)
        
        # Process influence within each group
        for location, names in location_groups.items():
            if len(names) < 2:
                continue
            
            # Random pairs for influence
            random.shuffle(names)
            for i in range(0, min(len(names) - 1, 4), 2):
                source = names[i]
                target = names[i + 1]
                
                # Get source's strongest belief
                source_memory = self.temporal_pauls[source].memory
                active_beliefs = source_memory.get_all_active_beliefs()
                
                if active_beliefs:
                    # Influence target with source's highest confidence belief
                    strongest = max(active_beliefs, key=lambda b: b.confidence)
                    
                    # Calculate influence strength based on relationship
                    rel_key = tuple(sorted([source, target]))
                    relationship = self.world.relationships.get(rel_key)
                    
                    influence_strength = 0.2  # Base influence
                    if relationship:
                        influence_strength += relationship.trust * 0.3
                        influence_strength += relationship.respect * 0.2
                    
                    # Apply influence
                    self.memory_manager.spread_influence(
                        source_paul=source,
                        target_paul=target,
                        topic=strongest.topic,
                        influence_strength=influence_strength,
                    )
                    
                    # Record in world
                    self.world.pauls[target].add_memory(
                        "learning",
                        f"Influenced by {source} regarding {strongest.topic}",
                        sentiment=0.2,
                    )
    
    async def ask_pauls(self, question: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Ask Pauls a question with temporal context in responses.
        """
        # Get base response from world
        result = await self.world.ask_pauls(question, context)
        
        # Enhance with temporal context
        topics = self._extract_topics(question)
        
        for response in result.get('responses', []):
            paul_name = response.get('paul_name')
            if paul_name not in self.temporal_pauls:
                continue
            
            temporal_paul = self.temporal_pauls[paul_name]
            
            # Add temporal context for relevant topics
            temporal_contexts = []
            for topic in topics:
                tc = temporal_paul.memory.get_temporal_context(topic)
                if tc:
                    temporal_contexts.append(tc.to_dict())
            
            if temporal_contexts:
                response['temporal_contexts'] = temporal_contexts
                
                # Enhance reasoning with temporal narrative
                if temporal_contexts:
                    main_context = temporal_contexts[0]
                    temporal_narrative = self._format_temporal_narrative(main_context)
                    if temporal_narrative:
                        response['reasoning'] = f"{temporal_narrative} {response.get('reasoning', '')}"
        
        return result
    
    def _extract_topics(self, question: str) -> List[str]:
        """Extract topics from question."""
        return self.world._extract_topics(question)
    
    def _format_temporal_narrative(self, context: Dict) -> str:
        """Format temporal context as narrative."""
        if not context.get('previous_beliefs'):
            return ""
        
        time_span = context.get('time_span_hours', 0)
        shift = context.get('belief_shift', 0)
        
        if time_span < 1:
            time_phrase = "Recently"
        elif time_span < 24:
            time_phrase = f"{int(time_span)} hours ago"
        elif time_span < 48:
            time_phrase = "Yesterday"
        else:
            days = int(time_span / 24)
            time_phrase = f"{days} days ago"
        
        if abs(shift) < 0.1:
            return f"{time_phrase}, I held this view, and I maintain it."
        elif shift > 0:
            return f"{time_phrase}, I was less certain, but recent developments have strengthened my conviction."
        else:
            return f"{time_phrase}, I saw things differently, but I've since revised my position."
    
    def get_belief_consensus(self, topic: str) -> Dict[str, Any]:
        """Get cross-Paul consensus on a topic."""
        return self.memory_manager.get_cross_paul_consensus(topic)
    
    def get_paul_beliefs(self, paul_name: str) -> List[Dict[str, Any]]:
        """Get all beliefs for a specific Paul."""
        if paul_name not in self.temporal_pauls:
            return []
        
        memory = self.temporal_pauls[paul_name].memory
        beliefs = []
        
        for topic in memory.beliefs.keys():
            belief = memory.get_belief(topic)
            if belief:
                beliefs.append({
                    'topic': topic,
                    'proposition': belief.proposition,
                    'confidence': belief.confidence,
                    'status': belief.status.value,
                    'evidence_count': belief.evidence_count,
                    'contradictions': belief.contradiction_count,
                })
        
        return beliefs
    
    def get_temporal_statistics(self) -> Dict[str, Any]:
        """Get statistics about temporal memory usage."""
        return {
            'pauls': self.memory_manager.get_all_statistics(),
            'world_time': self.world.world_time.isoformat(),
            'tick_count': self.world.tick_count,
        }
    
    async def run_simulation(self):
        """Run world simulation with temporal memory."""
        self.world.active = True
        print(f"🧠 Temporal Paul's World simulation running...")
        print(f"   {len(self.temporal_pauls)} Pauls with evolving beliefs")
        print(f"   Press Ctrl+C to stop\n")
        
        while self.world.active:
            await self.tick()
            
            # Print status every 24 hours
            if self.world.tick_count % 24 == 0:
                await self._print_daily_summary()
            
            await self._async_sleep(1)
    
    async def _async_sleep(self, seconds: float):
        """Async sleep helper."""
        import asyncio
        await asyncio.sleep(seconds)
    
    async def _print_daily_summary(self):
        """Print daily summary with temporal information."""
        await self.world._print_daily_summary()
        
        # Add temporal stats
        stats = self.get_temporal_statistics()
        total_beliefs = sum(s['active_beliefs'] for s in stats['pauls'].values())
        
        print(f"   Total active beliefs across all Pauls: {total_beliefs}")
        
        # Show sample beliefs from most confident Paul
        most_beliefs = max(stats['pauls'].items(), key=lambda x: x[1]['active_beliefs'])
        print(f"   Most beliefs: {most_beliefs[0]} ({most_beliefs[1]['active_beliefs']} beliefs)")
    
    def stop_simulation(self):
        """Stop simulation and save state."""
        self.world.stop_simulation()
        self.memory_manager.save_all()


# ============================================================================
# Factory Functions
# ============================================================================

def create_temporal_world(
    db_path: str = "data/paul_world.db",
    temporal_db_path: str = "data/temporal_memory.db"
) -> TemporalPaulWorld:
    """
    Create a new TemporalPaulWorld with all Pauls having temporal memory.
    
    Args:
        db_path: Path to PaulWorld database
        temporal_db_path: Path to temporal memory database
    
    Returns:
        TemporalPaulWorld instance ready to run
    """
    # Create base world
    world = PaulWorld(db_path=db_path)
    
    # Wrap with temporal capabilities
    temporal_world = TemporalPaulWorld(world, db_path=temporal_db_path)
    
    return temporal_world


async def quick_temporal_simulation(ticks: int = 48) -> TemporalPaulWorld:
    """
    Quick run of temporal world simulation.
    
    Args:
        ticks: Number of simulation ticks (hours) to run
    
    Returns:
        TemporalPaulWorld after simulation
    """
    temporal_world = create_temporal_world()
    await temporal_world.world.initialize()
    
    print(f"🚀 Running temporal simulation for {ticks} hours...")
    
    for i in range(ticks):
        await temporal_world.tick()
        
        if (i + 1) % 24 == 0:
            print(f"   Completed day {(i + 1) // 24}")
    
    print("\n✅ Simulation complete!")
    
    # Show final stats
    stats = temporal_world.get_temporal_statistics()
    print(f"\n📊 Final Statistics:")
    for paul_name, paul_stats in stats['pauls'].items():
        if paul_stats['active_beliefs'] > 0:
            print(f"   {paul_name}: {paul_stats['active_beliefs']} active beliefs")
    
    return temporal_world


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'TemporalPaulState',
    'TemporalPaulWorld',
    'create_temporal_world',
    'quick_temporal_simulation',
]
