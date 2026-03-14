"""
Swimming Pauls - Memory System
Works WITHOUT cloud - uses local SQLite by default
Optional Zep Cloud integration if API key provided
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Import local memory fallback
from local_memory import LocalMemoryManager, MemoryEntry, LocalMemory

# Optional Zep import
try:
    from zep_cloud import ZepClient
    from zep_cloud.types import Message, Session, Entity, Edge
    ZEP_AVAILABLE = True
except ImportError:
    ZEP_AVAILABLE = False

# Check if user wants to force local mode
FORCE_LOCAL = os.environ.get('SWIMMING_PAULS_LOCAL', '1') == '1'


@dataclass
class ZepMemoryConfig:
    """Configuration for memory system. Uses local by default, Zep optional."""
    # Local mode settings (default)
    use_local: bool = True
    local_db_path: str = "~/.openclaw/workspace/swimming_pauls/data/local_memory.db"
    
    # Optional Zep Cloud settings
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    
    # Memory settings
    max_context_messages: int = 20
    search_top_k: int = 5
    min_relevance_score: float = 0.7
    
    def __post_init__(self):
        if FORCE_LOCAL or not self.api_key:
            self.use_local = True


@dataclass
class MemoryFact:
    """A fact extracted from agent interactions."""
    fact_type: str  # semantic, episodic, procedural
    content: str
    confidence: float = 1.0
    entities: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentZepSession:
    """A Zep session for an agent."""
    agent_id: str
    session_id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    memory_count: int = 0


class ZepMemoryManager:
    """
    Manages Zep Cloud memory integration for Swimming Pauls.
    
    Features:
    - Persistent agent memory across sessions
    - Semantic search through agent experiences
    - Automatic fact extraction
    - Entity tracking and relationship building
    - Conversation history management
    """
    
    def __init__(self, config: Optional[ZepMemoryConfig] = None):
        if not ZEP_AVAILABLE:
            raise ImportError(
                "Zep Cloud integration requires 'zep-cloud'. "
                "Install with: pip install zep-cloud"
            )
        
        self.config = config or self._load_config_from_env()
        self.client: Optional[ZepClient] = None
        self._sessions: Dict[str, AgentZepSession] = {}
        self._initialized = False
    
    def _load_config_from_env(self) -> ZepMemoryConfig:
        """Load configuration from environment variables."""
        api_key = os.getenv('ZEP_API_KEY')
        if not api_key:
            raise ValueError(
                "ZEP_API_KEY environment variable not set. "
                "Get your API key from https://getzep.com"
            )
        
        return ZepMemoryConfig(
            api_key=api_key,
            base_url=os.getenv('ZEP_BASE_URL'),
            user_id=os.getenv('ZEP_USER_ID', 'swimming_pauls'),
            max_context_messages=int(os.getenv('ZEP_MAX_CONTEXT', '20')),
            search_top_k=int(os.getenv('ZEP_SEARCH_TOP_K', '5')),
            min_relevance_score=float(os.getenv('ZEP_MIN_RELEVANCE', '0.7'))
        )
    
    def initialize(self) -> bool:
        """Initialize the Zep client."""
        try:
            kwargs = {'api_key': self.config.api_key}
            if self.config.base_url:
                kwargs['base_url'] = self.config.base_url
            
            self.client = ZepClient(**kwargs)
            self._initialized = True
            return True
        except Exception as e:
            print(f"Failed to initialize Zep client: {e}")
            return False
    
    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================
    
    def create_agent_session(self, agent_id: str, 
                            metadata: Optional[Dict] = None) -> Optional[AgentZepSession]:
        """Create a new Zep session for an agent."""
        if not self._initialized:
            if not self.initialize():
                return None
        
        try:
            session_id = f"paul_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create user if not exists
            try:
                self.client.user.add(
                    user_id=self.config.user_id or f"agent_{agent_id}",
                    metadata={
                        'agent_id': agent_id,
                        'type': 'swimming_paul',
                        **(metadata or {})
                    }
                )
            except Exception:
                pass  # User may already exist
            
            # Create session
            self.client.memory.add_session(
                session_id=session_id,
                user_id=self.config.user_id or f"agent_{agent_id}",
                metadata={
                    'agent_id': agent_id,
                    'created_at': datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
            session = AgentZepSession(
                agent_id=agent_id,
                session_id=session_id,
                user_id=self.config.user_id or f"agent_{agent_id}"
            )
            
            self._sessions[agent_id] = session
            return session
            
        except Exception as e:
            print(f"Failed to create Zep session for {agent_id}: {e}")
            return None
    
    def get_agent_session(self, agent_id: str) -> Optional[AgentZepSession]:
        """Get or create an agent's Zep session."""
        if agent_id in self._sessions:
            return self._sessions[agent_id]
        
        # Try to find existing session
        try:
            sessions = self.client.memory.get_sessions(
                user_id=self.config.user_id or f"agent_{agent_id}"
            )
            if sessions:
                # Use most recent session
                session_data = sessions[0]
                session = AgentZepSession(
                    agent_id=agent_id,
                    session_id=session_data.uuid,
                    user_id=session_data.user_id,
                    created_at=session_data.created_at,
                    last_active=session_data.updated_at
                )
                self._sessions[agent_id] = session
                return session
        except Exception:
            pass
        
        # Create new session
        return self.create_agent_session(agent_id)
    
    # ========================================================================
    # MEMORY OPERATIONS
    # ========================================================================
    
    def remember(self, agent_id: str, content: str, 
                 role: str = "assistant",
                 metadata: Optional[Dict] = None) -> bool:
        """
        Store a memory for an agent.
        
        Args:
            agent_id: The agent's ID
            content: The content to remember
            role: 'assistant' (agent), 'user' (external input), or 'system'
            metadata: Additional context
        """
        session = self.get_agent_session(agent_id)
        if not session:
            return False
        
        try:
            message = Message(
                role=role,
                content=content,
                metadata=metadata or {}
            )
            
            self.client.memory.add(
                session_id=session.session_id,
                messages=[message]
            )
            
            session.memory_count += 1
            session.last_active = datetime.now()
            return True
            
        except Exception as e:
            print(f"Failed to store memory for {agent_id}: {e}")
            return False
    
    def recall(self, agent_id: str, query: str = None,
               last_n: int = None) -> List[Dict]:
        """
        Retrieve memories for an agent.
        
        Args:
            agent_id: The agent's ID
            query: Optional search query for semantic search
            last_n: Number of recent memories to retrieve
        """
        session = self.get_agent_session(agent_id)
        if not session:
            return []
        
        try:
            if query:
                # Semantic search
                results = self.client.memory.search(
                    session_id=session.session_id,
                    text=query,
                    limit=self.config.search_top_k
                )
                
                memories = []
                for result in results:
                    if result.score >= self.config.min_relevance_score:
                        memories.append({
                            'content': result.message.content,
                            'role': result.message.role,
                            'score': result.score,
                            'timestamp': result.message.created_at,
                            'metadata': result.message.metadata
                        })
                return memories
            
            else:
                # Get recent context
                memory = self.client.memory.get(
                    session_id=session.session_id,
                    lastn=last_n or self.config.max_context_messages
                )
                
                return [
                    {
                        'content': msg.content,
                        'role': msg.role,
                        'timestamp': msg.created_at,
                        'metadata': msg.metadata
                    }
                    for msg in (memory.messages or [])
                ]
                
        except Exception as e:
            print(f"Failed to retrieve memories for {agent_id}: {e}")
            return []
    
    def search_facts(self, agent_id: str, query: str,
                    fact_type: Optional[str] = None) -> List[MemoryFact]:
        """
        Search extracted facts about the agent or their experiences.
        
        Args:
            agent_id: The agent's ID
            query: Search query
            fact_type: Optional filter by fact type
        """
        session = self.get_agent_session(agent_id)
        if not session:
            return []
        
        try:
            # Get extracted data
            extracted = self.client.memory.get(
                session_id=session.session_id
            )
            
            facts = []
            
            # Process entities as facts
            if extracted.extracted_entities:
                for entity in extracted.extracted_entities:
                    if query.lower() in entity.name.lower() or \
                       any(query.lower() in attr.name.lower() 
                           for attr in (entity.attributes or [])):
                        facts.append(MemoryFact(
                            fact_type='entity',
                            content=f"{entity.name}: {entity.description or 'No description'}",
                            entities=[entity.name],
                            metadata={'entity_type': entity.entity_type}
                        ))
            
            # Process edges (relationships) as facts
            if extracted.extracted_edges:
                for edge in extracted.extracted_edges:
                    if query.lower() in edge.fact.lower():
                        facts.append(MemoryFact(
                            fact_type='relationship',
                            content=edge.fact,
                            entities=[edge.source, edge.target],
                            metadata={'relation': edge.relation_type}
                        ))
            
            return facts
            
        except Exception as e:
            print(f"Failed to search facts for {agent_id}: {e}")
            return []
    
    # ========================================================================
    # AGENT LEARNING
    # ========================================================================
    
    def record_prediction(self, agent_id: str, market_id: str,
                         prediction: Dict[str, Any],
                         outcome: Optional[Dict] = None) -> bool:
        """
        Record a prediction in the agent's memory.
        
        Args:
            agent_id: The agent's ID
            market_id: Market identifier
            prediction: Prediction details
            outcome: Optional outcome details
        """
        content = f"Made prediction for {market_id}: {prediction.get('direction')} " \
                  f"with {prediction.get('confidence', 0):.0%} confidence. " \
                  f"Reasoning: {prediction.get('reasoning', 'N/A')}"
        
        metadata = {
            'type': 'prediction',
            'market_id': market_id,
            'prediction': prediction,
            'outcome': outcome
        }
        
        return self.remember(agent_id, content, role="assistant", metadata=metadata)
    
    def record_observation(self, agent_id: str, observation_type: str,
                          content: str, entities: List[str] = None,
                          confidence: float = 1.0) -> bool:
        """
        Record an observation in the agent's memory.
        
        Args:
            agent_id: The agent's ID
            observation_type: Type of observation (price_movement, news, etc.)
            content: Observation content
            entities: Related entities
            confidence: Confidence in the observation
        """
        memory_content = f"Observed ({observation_type}): {content}"
        
        metadata = {
            'type': 'observation',
            'observation_type': observation_type,
            'entities': entities or [],
            'confidence': confidence
        }
        
        return self.remember(agent_id, memory_content, role="assistant", metadata=metadata)
    
    def record_learning(self, agent_id: str, lesson: str,
                       context: Dict[str, Any]) -> bool:
        """
        Record a learned lesson in the agent's memory.
        
        Args:
            agent_id: The agent's ID
            lesson: The lesson learned
            context: Context about when/why this was learned
        """
        content = f"Learned: {lesson}"
        
        metadata = {
            'type': 'learning',
            'context': context
        }
        
        return self.remember(agent_id, content, role="assistant", metadata=metadata)
    
    # ========================================================================
    # CONTEXT FOR PREDICTIONS
    # ========================================================================
    
    def get_prediction_context(self, agent_id: str, market_context: Dict) -> Dict[str, Any]:
        """
        Get relevant memory context for making a prediction.
        
        Args:
            agent_id: The agent's ID
            market_context: Current market context
        """
        # Get recent memories
        recent = self.recall(agent_id, last_n=10)
        
        # Search for relevant past experiences
        market_keywords = ' '.join([
            market_context.get('asset', ''),
            market_context.get('market_type', ''),
            ' '.join(market_context.get('factors', []))
        ])
        
        relevant = self.recall(agent_id, query=market_keywords) if market_keywords.strip() else []
        
        # Get extracted facts
        facts = self.search_facts(agent_id, market_context.get('asset', ''))
        
        # Get past predictions
        past_predictions = [
            m for m in recent + relevant
            if m.get('metadata', {}).get('type') == 'prediction'
        ]
        
        return {
            'recent_memories': recent,
            'relevant_experiences': relevant,
            'known_facts': [{'content': f.content, 'type': f.fact_type} for f in facts],
            'past_predictions': past_predictions,
            'summary': self._generate_memory_summary(recent, relevant, facts)
        }
    
    def _generate_memory_summary(self, recent: List[Dict], 
                                  relevant: List[Dict],
                                  facts: List[MemoryFact]) -> str:
        """Generate a natural language summary of memories."""
        parts = []
        
        if recent:
            parts.append(f"Recently made {len(recent)} observations/decisions.")
        
        if relevant:
            parts.append(f"Found {len(relevant)} relevant past experiences.")
        
        if facts:
            parts.append(f"Knows {len(facts)} related facts.")
        
        return " ".join(parts) if parts else "No relevant memories found."
    
    # ========================================================================
    # SYNTHESIS OPERATIONS
    # ========================================================================
    
    def synthesize_agent_profile(self, agent_id: str) -> Dict[str, Any]:
        """
        Synthesize a comprehensive profile from an agent's memories.
        
        This extracts patterns, preferences, and learned behaviors.
        """
        session = self.get_agent_session(agent_id)
        if not session:
            return {}
        
        try:
            # Get all memory
            memory = self.client.memory.get(session_id=session.session_id)
            
            # Get facts
            extracted = self.client.memory.get(session_id=session.session_id)
            
            # Analyze prediction accuracy
            predictions = [
                msg for msg in (memory.messages or [])
                if msg.metadata.get('type') == 'prediction'
            ]
            
            correct = sum(1 for p in predictions 
                         if p.metadata.get('outcome', {}).get('correct', False))
            total = len(predictions)
            
            accuracy = correct / total if total > 0 else 0
            
            # Extract common entities
            entities = {}
            if extracted.extracted_entities:
                for entity in extracted.extracted_entities:
                    entities[entity.name] = {
                        'type': entity.entity_type,
                        'mentions': entity.metadata.get('mention_count', 1) if entity.metadata else 1
                    }
            
            return {
                'agent_id': agent_id,
                'total_memories': len(memory.messages or []),
                'prediction_accuracy': accuracy,
                'total_predictions': total,
                'known_entities': entities,
                'top_entities': sorted(entities.items(), 
                                      key=lambda x: x[1]['mentions'], 
                                      reverse=True)[:10],
                'session_age_days': (datetime.now() - session.created_at).days
            }
            
        except Exception as e:
            print(f"Failed to synthesize profile for {agent_id}: {e}")
            return {}
    
    # ========================================================================
    # CLEANUP
    # ========================================================================
    
    def end_session(self, agent_id: str) -> bool:
        """End an agent's Zep session."""
        session = self._sessions.get(agent_id)
        if not session:
            return False
        
        try:
            self.client.memory.end_session(session_id=session.session_id)
            del self._sessions[agent_id]
            return True
        except Exception as e:
            print(f"Failed to end session for {agent_id}: {e}")
            return False
    
    def delete_session(self, agent_id: str) -> bool:
        """Delete an agent's Zep session and memories."""
        session = self._sessions.get(agent_id)
        if not session:
            return False
        
        try:
            self.client.memory.delete_session(session_id=session.session_id)
            del self._sessions[agent_id]
            return True
        except Exception as e:
            print(f"Failed to delete session for {agent_id}: {e}")
            return False


# ============================================================================
# FALLBACK IMPLEMENTATION
# ============================================================================

class LocalMemoryFallback:
    """
    Local-only memory implementation when Zep is unavailable.
    
    Provides similar API but stores everything locally in JSON files.
    """
    
    def __init__(self, storage_path: str = "~/.scales/agent_memories"):
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._memories: Dict[str, List[Dict]] = {}
    
    def _get_memory_file(self, agent_id: str) -> Path:
        return self.storage_path / f"{agent_id}_memory.json"
    
    def _load_memories(self, agent_id: str):
        if agent_id not in self._memories:
            memory_file = self._get_memory_file(agent_id)
            if memory_file.exists():
                self._memories[agent_id] = json.loads(memory_file.read_text())
            else:
                self._memories[agent_id] = []
    
    def _save_memories(self, agent_id: str):
        memory_file = self._get_memory_file(agent_id)
        memory_file.write_text(json.dumps(self._memories[agent_id], indent=2, default=str))
    
    def remember(self, agent_id: str, content: str, 
                 role: str = "assistant", metadata: Dict = None) -> bool:
        self._load_memories(agent_id)
        
        memory = {
            'content': content,
            'role': role,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self._memories[agent_id].append(memory)
        self._save_memories(agent_id)
        return True
    
    def recall(self, agent_id: str, query: str = None, 
               last_n: int = None) -> List[Dict]:
        self._load_memories(agent_id)
        memories = self._memories[agent_id]
        
        if last_n:
            memories = memories[-last_n:]
        
        if query:
            # Simple keyword search
            memories = [
                m for m in memories 
                if query.lower() in m['content'].lower()
            ]
        
        return memories
    
    def get_prediction_context(self, agent_id: str, market_context: Dict) -> Dict:
        self._load_memories(agent_id)
        
        recent = self.recall(agent_id, last_n=10)
        
        # Search for predictions
        predictions = [
            m for m in self._memories[agent_id]
            if m.get('metadata', {}).get('type') == 'prediction'
        ]
        
        return {
            'recent_memories': recent,
            'past_predictions': predictions[-5:],
            'summary': f"Using local memory with {len(self._memories[agent_id])} total entries"
        }


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_memory_manager(use_zep: bool = True, 
                         config: Optional[ZepMemoryConfig] = None) -> Union[ZepMemoryManager, LocalMemoryFallback]:
    """
    Create an appropriate memory manager.
    
    Args:
        use_zep: Try to use Zep Cloud if available
        config: Zep configuration (or loaded from env)
    
    Returns:
        ZepMemoryManager if available and requested, otherwise LocalMemoryFallback
    """
    if use_zep and ZEP_AVAILABLE:
        try:
            return ZepMemoryManager(config)
        except Exception as e:
            print(f"Zep initialization failed, falling back to local: {e}")
    
    return LocalMemoryFallback()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example with local fallback
    memory = create_memory_manager(use_zep=False)
    
    agent_id = "paul_test_001"
    
    # Store memories
    memory.remember(agent_id, "Observed BTC breaking above $50k resistance", 
                   role="assistant", 
                   metadata={'type': 'observation', 'asset': 'BTC'})
    
    memory.remember(agent_id, "Predicted bullish continuation with 75% confidence",
                   role="assistant",
                   metadata={'type': 'prediction', 'direction': 'bullish'})
    
    # Recall
    recent = memory.recall(agent_id, last_n=5)
    print(f"Recent memories: {len(recent)}")
    for m in recent:
        print(f"  - {m['content'][:50]}...")
    
    # Get prediction context
    context = memory.get_prediction_context(agent_id, {'asset': 'BTC'})
    print(f"\nContext summary: {context['summary']}")
