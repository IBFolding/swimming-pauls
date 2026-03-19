"""
Graph Memory - Traversable Knowledge Storage for Agents

Stores agent knowledge as a traversable graph structure, enabling:
- Semantic search across agent knowledge
- Relationship-aware reasoning
- Context retrieval for predictions
- Knowledge sharing between agents

Part of Paul's World - Enhanced Knowledge System for Swimming Pauls

Author: Howard (H.O.W.A.R.D)
"""

import json
import uuid
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import sqlite3

from knowledge_graph import KnowledgeGraph, Entity, Relationship, GraphBuilder


@dataclass
class AgentKnowledge:
    """Knowledge entry for a specific agent."""
    agent_id: str
    entity_id: str
    belief_strength: float = 1.0  # How strongly the agent believes this
    source: str = ""  # Where this knowledge came from
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(f"{self.agent_id}_{self.entity_id}")


@dataclass
class KnowledgeQuery:
    """Query parameters for knowledge retrieval."""
    entity_types: Optional[List[str]] = None
    relation_types: Optional[List[str]] = None
    agents: Optional[List[str]] = None
    min_confidence: float = 0.0
    min_belief: float = 0.0
    time_range: Optional[Tuple[datetime, datetime]] = None
    keywords: Optional[List[str]] = None


class GraphMemory:
    """
    Persistent graph-based memory system for agent knowledge.
    
    Features:
    - SQLite-backed storage for durability
    - Multi-agent knowledge sharing
    - Belief-weighted reasoning
    - Temporal knowledge tracking
    - Semantic search capabilities
    """
    
    SCHEMA_SQL = """
    -- Core entities table
    CREATE TABLE IF NOT EXISTS entities (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        aliases TEXT,  -- JSON array
        metadata TEXT,  -- JSON
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Relationships table
    CREATE TABLE IF NOT EXISTS relationships (
        id TEXT PRIMARY KEY,
        source_id TEXT NOT NULL,
        target_id TEXT NOT NULL,
        relation_type TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        evidence TEXT,  -- JSON array
        metadata TEXT,  -- JSON
        timestamp TIMESTAMP,
        FOREIGN KEY (source_id) REFERENCES entities(id),
        FOREIGN KEY (target_id) REFERENCES entities(id)
    );
    
    -- Agent knowledge table (links agents to entities)
    CREATE TABLE IF NOT EXISTS agent_knowledge (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        belief_strength REAL DEFAULT 1.0,
        source TEXT,
        context TEXT,  -- JSON
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (entity_id) REFERENCES entities(id),
        UNIQUE(agent_id, entity_id)
    );
    
    -- Agent relationship knowledge
    CREATE TABLE IF NOT EXISTS agent_relationships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT NOT NULL,
        relationship_id TEXT NOT NULL,
        belief_strength REAL DEFAULT 1.0,
        discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (relationship_id) REFERENCES relationships(id),
        UNIQUE(agent_id, relationship_id)
    );
    
    -- Knowledge observations (what agents have observed/learned)
    CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT NOT NULL,
        observation_type TEXT NOT NULL,
        content TEXT NOT NULL,
        entities_involved TEXT,  -- JSON array of entity IDs
        confidence REAL DEFAULT 1.0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        metadata TEXT  -- JSON
    );
    
    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
    CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
    CREATE INDEX IF NOT EXISTS idx_relations_type ON relationships(relation_type);
    CREATE INDEX IF NOT EXISTS idx_relations_source ON relationships(source_id);
    CREATE INDEX IF NOT EXISTS idx_relations_target ON relationships(target_id);
    CREATE INDEX IF NOT EXISTS idx_agent_knowledge_agent ON agent_knowledge(agent_id);
    CREATE INDEX IF NOT EXISTS idx_agent_knowledge_entity ON agent_knowledge(entity_id);
    CREATE INDEX IF NOT EXISTS idx_observations_agent ON observations(agent_id);
    CREATE INDEX IF NOT EXISTS idx_observations_timestamp ON observations(timestamp);
    """
    
    def __init__(self, db_path: str = "~/.scales/graph_memory.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_database()
        self._cache: Dict[str, Any] = {}
    
    @property
    def _conn(self) -> sqlite3.Connection:
        """Thread-local connection."""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA foreign_keys = ON")
        return self._local.conn
    
    def _init_database(self):
        """Initialize database schema."""
        with self._conn:
            self._conn.executescript(self.SCHEMA_SQL)
    
    def close(self):
        """Close thread-local connection."""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ========================================================================
    # ENTITY OPERATIONS
    # ========================================================================
    
    def add_entity(self, entity: Entity) -> str:
        """Add or update an entity in the graph."""
        with self._conn:
            self._conn.execute(
                """INSERT INTO entities (id, name, entity_type, confidence, aliases, metadata)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                       name = excluded.name,
                       entity_type = excluded.entity_type,
                       confidence = MAX(entities.confidence, excluded.confidence),
                       aliases = excluded.aliases,
                       metadata = excluded.metadata""",
                (
                    entity.id, entity.name, entity.entity_type, entity.confidence,
                    json.dumps(entity.aliases), json.dumps(entity.metadata)
                )
            )
        return entity.id
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Retrieve an entity by ID."""
        row = self._conn.execute(
            "SELECT * FROM entities WHERE id = ?",
            (entity_id,)
        ).fetchone()
        
        if not row:
            return None
        
        return Entity(
            id=row['id'],
            name=row['name'],
            entity_type=row['entity_type'],
            confidence=row['confidence'],
            aliases=json.loads(row['aliases']) if row['aliases'] else [],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def find_entity_by_name(self, name: str) -> Optional[Entity]:
        """Find an entity by exact name or alias."""
        # Try exact match first
        row = self._conn.execute(
            "SELECT * FROM entities WHERE name = ? COLLATE NOCASE",
            (name,)
        ).fetchone()
        
        if row:
            return self._row_to_entity(row)
        
        # Try aliases
        rows = self._conn.execute(
            "SELECT * FROM entities WHERE aliases LIKE ?",
            (f'%"{name}"%',)
        ).fetchall()
        
        for row in rows:
            aliases = json.loads(row['aliases']) if row['aliases'] else []
            if name.lower() in [a.lower() for a in aliases]:
                return self._row_to_entity(row)
        
        return None
    
    def _row_to_entity(self, row: sqlite3.Row) -> Entity:
        return Entity(
            id=row['id'],
            name=row['name'],
            entity_type=row['entity_type'],
            confidence=row['confidence'],
            aliases=json.loads(row['aliases']) if row['aliases'] else [],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def search_entities(self, query: str, entity_type: Optional[str] = None,
                       limit: int = 10) -> List[Entity]:
        """Search entities by name pattern."""
        sql = "SELECT * FROM entities WHERE name LIKE ?"
        params = [f'%{query}%']
        
        if entity_type:
            sql += " AND entity_type = ?"
            params.append(entity_type)
        
        sql += " ORDER BY confidence DESC LIMIT ?"
        params.append(limit)
        
        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_entity(row) for row in rows]
    
    # ========================================================================
    # RELATIONSHIP OPERATIONS
    # ========================================================================
    
    def add_relationship(self, rel: Relationship) -> str:
        """Add or update a relationship in the graph."""
        with self._conn:
            self._conn.execute(
                """INSERT INTO relationships 
                   (id, source_id, target_id, relation_type, confidence, evidence, metadata, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(id) DO UPDATE SET
                       confidence = MAX(relationships.confidence, excluded.confidence),
                       evidence = excluded.evidence,
                       metadata = excluded.metadata""",
                (
                    rel.id, rel.source_id, rel.target_id, rel.relation_type,
                    rel.confidence, json.dumps(rel.evidence), json.dumps(rel.metadata),
                    rel.timestamp or datetime.now()
                )
            )
        return rel.id
    
    def get_relationship(self, rel_id: str) -> Optional[Relationship]:
        """Retrieve a relationship by ID."""
        row = self._conn.execute(
            "SELECT * FROM relationships WHERE id = ?",
            (rel_id,)
        ).fetchone()
        
        if not row:
            return None
        
        return self._row_to_relationship(row)
    
    def _row_to_relationship(self, row: sqlite3.Row) -> Relationship:
        return Relationship(
            id=row['id'],
            source_id=row['source_id'],
            target_id=row['target_id'],
            relation_type=row['relation_type'],
            confidence=row['confidence'],
            evidence=json.loads(row['evidence']) if row['evidence'] else [],
            metadata=json.loads(row['metadata']) if row['metadata'] else {},
            timestamp=row['timestamp']
        )
    
    def get_entity_relationships(self, entity_id: str, 
                                  direction: str = 'both') -> Tuple[List[Relationship], List[Relationship]]:
        """Get relationships where entity is source and/or target."""
        outgoing, incoming = [], []
        
        if direction in ('outgoing', 'both'):
            rows = self._conn.execute(
                "SELECT * FROM relationships WHERE source_id = ?",
                (entity_id,)
            ).fetchall()
            outgoing = [self._row_to_relationship(row) for row in rows]
        
        if direction in ('incoming', 'both'):
            rows = self._conn.execute(
                "SELECT * FROM relationships WHERE target_id = ?",
                (entity_id,)
            ).fetchall()
            incoming = [self._row_to_relationship(row) for row in rows]
        
        return outgoing, incoming
    
    def find_relationships(self, source_id: Optional[str] = None,
                          target_id: Optional[str] = None,
                          relation_type: Optional[str] = None) -> List[Relationship]:
        """Find relationships matching criteria."""
        conditions = []
        params = []
        
        if source_id:
            conditions.append("source_id = ?")
            params.append(source_id)
        if target_id:
            conditions.append("target_id = ?")
            params.append(target_id)
        if relation_type:
            conditions.append("relation_type = ?")
            params.append(relation_type)
        
        sql = "SELECT * FROM relationships"
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_relationship(row) for row in rows]
    
    # ========================================================================
    # AGENT KNOWLEDGE OPERATIONS
    # ========================================================================
    
    def teach_agent(self, agent_id: str, entity_id: str,
                   belief_strength: float = 1.0, source: str = "",
                   context: Optional[Dict] = None) -> bool:
        """Teach an agent about an entity."""
        # Verify entity exists
        if not self.get_entity(entity_id):
            return False
        
        with self._conn:
            self._conn.execute(
                """INSERT INTO agent_knowledge 
                   (agent_id, entity_id, belief_strength, source, context)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(agent_id, entity_id) DO UPDATE SET
                       belief_strength = MAX(agent_knowledge.belief_strength, excluded.belief_strength),
                       source = excluded.source,
                       context = excluded.context,
                       timestamp = CURRENT_TIMESTAMP""",
                (agent_id, entity_id, belief_strength, source, json.dumps(context) if context else None)
            )
        return True
    
    def get_agent_knowledge(self, agent_id: str, 
                           min_belief: float = 0.0) -> List[Tuple[Entity, float]]:
        """Get all entities an agent knows about with belief strengths."""
        rows = self._conn.execute(
            """SELECT e.*, ak.belief_strength 
               FROM entities e
               JOIN agent_knowledge ak ON e.id = ak.entity_id
               WHERE ak.agent_id = ? AND ak.belief_strength >= ?
               ORDER BY ak.belief_strength DESC""",
            (agent_id, min_belief)
        ).fetchall()
        
        results = []
        for row in rows:
            entity = Entity(
                id=row['id'], name=row['name'], entity_type=row['entity_type'],
                confidence=row['confidence'],
                aliases=json.loads(row['aliases']) if row['aliases'] else [],
                metadata=json.loads(row['metadata']) if row['metadata'] else {}
            )
            results.append((entity, row['belief_strength']))
        
        return results
    
    def get_agents_knowing(self, entity_id: str) -> List[Tuple[str, float]]:
        """Get all agents that know about an entity."""
        rows = self._conn.execute(
            "SELECT agent_id, belief_strength FROM agent_knowledge WHERE entity_id = ?",
            (entity_id,)
        ).fetchall()
        
        return [(row['agent_id'], row['belief_strength']) for row in rows]
    
    def forget_entity(self, agent_id: str, entity_id: str) -> bool:
        """Make an agent forget an entity."""
        with self._conn:
            cursor = self._conn.execute(
                "DELETE FROM agent_knowledge WHERE agent_id = ? AND entity_id = ?",
                (agent_id, entity_id)
            )
            return cursor.rowcount > 0
    
    # ========================================================================
    # OBSERVATION OPERATIONS
    # ========================================================================
    
    def add_observation(self, agent_id: str, observation_type: str,
                       content: str, entities_involved: List[str] = None,
                       confidence: float = 1.0, metadata: Dict = None) -> int:
        """Record an observation made by an agent."""
        with self._conn:
            cursor = self._conn.execute(
                """INSERT INTO observations 
                   (agent_id, observation_type, content, entities_involved, confidence, metadata)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (agent_id, observation_type, content,
                 json.dumps(entities_involved) if entities_involved else None,
                 confidence, json.dumps(metadata) if metadata else None)
            )
            return cursor.lastrowid
    
    def get_agent_observations(self, agent_id: str,
                               since: Optional[datetime] = None,
                               observation_type: Optional[str] = None,
                               limit: int = 100) -> List[Dict]:
        """Get observations by an agent."""
        sql = "SELECT * FROM observations WHERE agent_id = ?"
        params = [agent_id]
        
        if since:
            sql += " AND timestamp > ?"
            params.append(since)
        if observation_type:
            sql += " AND observation_type = ?"
            params.append(observation_type)
        
        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        rows = self._conn.execute(sql, params).fetchall()
        
        return [{
            'id': row['id'],
            'type': row['observation_type'],
            'content': row['content'],
            'entities': json.loads(row['entities_involved']) if row['entities_involved'] else [],
            'confidence': row['confidence'],
            'timestamp': row['timestamp'],
            'metadata': json.loads(row['metadata']) if row['metadata'] else {}
        } for row in rows]
    
    # ========================================================================
    # KNOWLEDGE QUERIES
    # ========================================================================
    
    def query(self, query: KnowledgeQuery) -> List[Entity]:
        """Execute a knowledge query."""
        conditions = ["1=1"]
        params = []
        joins = []
        
        # Base query
        sql = "SELECT DISTINCT e.* FROM entities e"
        
        # Apply filters
        if query.entity_types:
            conditions.append(f"e.entity_type IN ({','.join(['?']*len(query.entity_types))})")
            params.extend(query.entity_types)
        
        if query.min_confidence > 0:
            conditions.append("e.confidence >= ?")
            params.append(query.min_confidence)
        
        # Agent knowledge filter
        if query.agents:
            joins.append("JOIN agent_knowledge ak ON e.id = ak.entity_id")
            conditions.append(f"ak.agent_id IN ({','.join(['?']*len(query.agents))})")
            params.extend(query.agents)
            
            if query.min_belief > 0:
                conditions.append("ak.belief_strength >= ?")
                params.append(query.min_belief)
        
        # Keyword search
        if query.keywords:
            keyword_conditions = []
            for kw in query.keywords:
                keyword_conditions.append("e.name LIKE ?")
                params.append(f'%{kw}%')
            conditions.append(f"({' OR '.join(keyword_conditions)})")
        
        # Build final query
        sql += " " + " ".join(joins)
        sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY e.confidence DESC"
        
        rows = self._conn.execute(sql, params).fetchall()
        return [self._row_to_entity(row) for row in rows]
    
    def get_context_for_prediction(self, agent_id: str, 
                                   market_entities: List[str],
                                   depth: int = 2) -> Dict[str, Any]:
        """
        Get relevant knowledge context for making a prediction.
        
        Traverses the graph from market-related entities to find
        connected knowledge the agent has learned.
        """
        context = {
            'direct_knowledge': [],
            'related_entities': [],
            'relationships': [],
            'recent_observations': []
        }
        
        # Get agent's direct knowledge about market entities
        for entity_id in market_entities:
            entity = self.get_entity(entity_id)
            if entity:
                # Check if agent knows this entity
                rows = self._conn.execute(
                    """SELECT belief_strength, source, context FROM agent_knowledge
                       WHERE agent_id = ? AND entity_id = ?""",
                    (agent_id, entity_id)
                ).fetchall()
                
                if rows:
                    context['direct_knowledge'].append({
                        'entity': entity,
                        'belief': rows[0]['belief_strength'],
                        'source': rows[0]['source'],
                        'context': json.loads(rows[0]['context']) if rows[0]['context'] else {}
                    })
                else:
                    # Entity exists but agent doesn't know it
                    context['related_entities'].append({
                        'entity': entity,
                        'known': False
                    })
        
        # Traverse graph to find connected entities
        visited = set(market_entities)
        current_level = set(market_entities)
        
        for _ in range(depth):
            next_level = set()
            for entity_id in current_level:
                outgoing, incoming = self.get_entity_relationships(entity_id)
                
                for rel in outgoing + incoming:
                    other_id = rel.target_id if rel.source_id == entity_id else rel.source_id
                    
                    if other_id not in visited:
                        visited.add(other_id)
                        next_level.add(other_id)
                        
                        entity = self.get_entity(other_id)
                        if entity:
                            # Check agent knowledge
                            rows = self._conn.execute(
                                "SELECT belief_strength FROM agent_knowledge WHERE agent_id = ? AND entity_id = ?",
                                (agent_id, other_id)
                            ).fetchall()
                            
                            belief = rows[0]['belief_strength'] if rows else 0.0
                            
                            context['related_entities'].append({
                                'entity': entity,
                                'known': belief > 0,
                                'belief': belief,
                                'connected_via': rel
                            })
                        
                        context['relationships'].append(rel)
            
            current_level = next_level
        
        # Get recent observations
        since = datetime.now() - timedelta(days=7)
        context['recent_observations'] = self.get_agent_observations(agent_id, since=since, limit=20)
        
        return context
    
    # ========================================================================
    # GRAPH IMPORT/EXPORT
    # ========================================================================
    
    def import_knowledge_graph(self, graph: KnowledgeGraph, 
                               teaching_agents: Optional[List[str]] = None):
        """Import a KnowledgeGraph into memory."""
        # Import entities
        for entity in graph.entities.values():
            self.add_entity(entity)
            
            # Teach to specified agents
            if teaching_agents:
                for agent_id in teaching_agents:
                    self.teach_agent(agent_id, entity.id, belief_strength=0.8,
                                   source=f"imported_from_{graph.name}")
        
        # Import relationships
        for rel in graph.relationships.values():
            self.add_relationship(rel)
    
    def export_knowledge_graph(self, agent_id: Optional[str] = None,
                               min_belief: float = 0.5) -> KnowledgeGraph:
        """Export knowledge as a KnowledgeGraph."""
        graph = KnowledgeGraph(name=f"memory_{agent_id or 'all'}")
        
        if agent_id:
            # Get only entities this agent knows
            knowledge = self.get_agent_knowledge(agent_id, min_belief)
            entity_ids = set(e.id for e, _ in knowledge)
        else:
            # Get all entities
            rows = self._conn.execute("SELECT * FROM entities").fetchall()
            entity_ids = set(row['id'] for row in rows)
        
        # Add entities
        for entity_id in entity_ids:
            entity = self.get_entity(entity_id)
            if entity:
                graph.add_entity(entity)
        
        # Add relationships between known entities
        for entity_id in entity_ids:
            outgoing, incoming = self.get_entity_relationships(entity_id)
            for rel in outgoing + incoming:
                if rel.source_id in entity_ids and rel.target_id in entity_ids:
                    graph.add_relationship(rel)
        
        return graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics."""
        stats = {}
        
        # Entity counts
        row = self._conn.execute(
            "SELECT COUNT(*) as count, entity_type FROM entities GROUP BY entity_type"
        ).fetchall()
        stats['entities_by_type'] = {r['entity_type']: r['count'] for r in row}
        stats['total_entities'] = sum(r['count'] for r in row)
        
        # Relationship counts
        row = self._conn.execute(
            "SELECT COUNT(*) as count, relation_type FROM relationships GROUP BY relation_type"
        ).fetchall()
        stats['relationships_by_type'] = {r['relation_type']: r['count'] for r in row}
        stats['total_relationships'] = sum(r['count'] for r in row)
        
        # Agent knowledge
        row = self._conn.execute(
            "SELECT COUNT(DISTINCT agent_id) as agents, COUNT(*) as knowledge_entries FROM agent_knowledge"
        ).fetchone()
        stats['agents'] = row['agents']
        stats['knowledge_entries'] = row['knowledge_entries']
        
        # Observations
        row = self._conn.execute("SELECT COUNT(*) as count FROM observations").fetchone()
        stats['total_observations'] = row['count']
        
        return stats


# ============================================================================
# MEMORY-AWARE AGENT MIXIN
# ============================================================================

class GraphMemoryMixin:
    """Mixin to add graph memory capabilities to agents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory: Optional[GraphMemory] = None
        self._agent_memory_id: Optional[str] = None
    
    def attach_memory(self, memory: GraphMemory, agent_id: Optional[str] = None):
        """Attach a graph memory to this agent."""
        self.memory = memory
        self._agent_memory_id = agent_id or getattr(self, 'id', str(uuid.uuid4()))
    
    def learn_entity(self, entity: Entity, belief: float = 1.0, source: str = ""):
        """Learn about an entity."""
        if self.memory:
            self.memory.add_entity(entity)
            self.memory.teach_agent(self._agent_memory_id, entity.id, belief, source)
    
    def learn_relationship(self, rel: Relationship, belief: float = 1.0):
        """Learn about a relationship."""
        if self.memory:
            self.memory.add_relationship(rel)
    
    def observe(self, observation_type: str, content: str, 
                entities: List[str] = None, confidence: float = 1.0):
        """Record an observation."""
        if self.memory:
            self.memory.add_observation(
                self._agent_memory_id, observation_type, content,
                entities, confidence
            )
    
    def recall_context(self, market_entities: List[str], depth: int = 2) -> Dict:
        """Recall relevant context for prediction."""
        if self.memory:
            return self.memory.get_context_for_prediction(
                self._agent_memory_id, market_entities, depth
            )
        return {}
    
    def query_knowledge(self, query: KnowledgeQuery) -> List[Entity]:
        """Query the knowledge base."""
        if self.memory:
            if not query.agents:
                query.agents = [self._agent_memory_id]
            return self.memory.query(query)
        return []


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    with GraphMemory() as memory:
        # Create some entities
        eth = Entity(id="eth_123", name="Ethereum", entity_type="TECHNOLOGY")
        vitalik = Entity(id="vitalik_456", name="Vitalik Buterin", entity_type="PERSON")
        a16z = Entity(id="a16z_789", name="Andreessen Horowitz", entity_type="ORGANIZATION")
        
        # Add to memory
        memory.add_entity(eth)
        memory.add_entity(vitalik)
        memory.add_entity(a16z)
        
        # Create relationships
        rel1 = Relationship(
            id="rel_1", source_id="vitalik_456", target_id="eth_123",
            relation_type="founded_by", confidence=0.95
        )
        rel2 = Relationship(
            id="rel_2", source_id="a16z_789", target_id="eth_123",
            relation_type="invested_in", confidence=0.9
        )
        
        memory.add_relationship(rel1)
        memory.add_relationship(rel2)
        
        # Teach an agent
        agent_id = "paul_analyst_001"
        memory.teach_agent(agent_id, "eth_123", belief_strength=0.9, source="market_research")
        memory.teach_agent(agent_id, "vitalik_456", belief_strength=0.8, source="research")
        
        # Add observation
        memory.add_observation(
            agent_id, "price_movement", "ETH up 5% after merge announcement",
            entities=["eth_123"], confidence=0.95
        )
        
        # Query knowledge
        knowledge = memory.get_agent_knowledge(agent_id)
        print(f"Agent knows about {len(knowledge)} entities:")
        for entity, belief in knowledge:
            print(f"  - {entity.name} (belief: {belief:.2f})")
        
        # Get context
        context = memory.get_context_for_prediction(agent_id, ["eth_123"], depth=2)
        print(f"\nContext for prediction:")
        print(f"  Direct knowledge: {len(context['direct_knowledge'])}")
        print(f"  Related entities: {len(context['related_entities'])}")
        print(f"  Recent observations: {len(context['recent_observations'])}")
        
        # Stats
        stats = memory.get_statistics()
        print(f"\nMemory statistics: {stats}")
