"""
Swimming Pauls - Local Memory (No Cloud)
Pure local memory system using SQLite - no Zep Cloud required
"""

import json
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class MemoryEntry:
    """A single memory entry for a Paul."""
    agent_id: str
    content: str
    timestamp: datetime
    importance: float = 1.0
    context: Optional[str] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "context": self.context,
            "metadata": self.metadata or {}
        }


class LocalMemory:
    """Local-only memory storage using SQLite."""
    
    def __init__(self, db_path: str = "~/.openclaw/workspace/swimming_pauls/data/local_memory.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    importance REAL DEFAULT 1.0,
                    context TEXT,
                    metadata TEXT,
                    content_hash TEXT UNIQUE
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent ON memories(agent_id)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
            """)
            
            conn.commit()
    
    def _hash_content(self, content: str) -> str:
        """Generate hash for deduplication."""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def add_memory(self, entry: MemoryEntry) -> bool:
        """Add a memory entry."""
        content_hash = self._hash_content(entry.content)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO memories 
                    (agent_id, content, timestamp, importance, context, metadata, content_hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    entry.agent_id,
                    entry.content,
                    entry.timestamp.isoformat(),
                    entry.importance,
                    entry.context,
                    json.dumps(entry.metadata) if entry.metadata else None,
                    content_hash
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error adding memory: {e}")
            return False
    
    def get_memories(
        self,
        agent_id: Optional[str] = None,
        context: Optional[str] = None,
        limit: int = 100,
        min_importance: float = 0.0
    ) -> List[MemoryEntry]:
        """Retrieve memories with filtering."""
        query = "SELECT * FROM memories WHERE importance >= ?"
        params = [min_importance]
        
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        
        if context:
            query += " AND context = ?"
            params.append(context)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        entries = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            
            for row in rows:
                entries.append(MemoryEntry(
                    agent_id=row["agent_id"],
                    content=row["content"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    importance=row["importance"],
                    context=row["context"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                ))
        
        return entries
    
    def search_memories(self, query: str, limit: int = 20) -> List[MemoryEntry]:
        """Simple text search in memories."""
        entries = []
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """SELECT * FROM memories 
                   WHERE content LIKE ? 
                   ORDER BY importance DESC, timestamp DESC 
                   LIMIT ?""",
                (f"%{query}%", limit)
            ).fetchall()
            
            for row in rows:
                entries.append(MemoryEntry(
                    agent_id=row["agent_id"],
                    content=row["content"],
                    timestamp=datetime.fromisoformat(row["timestamp"]),
                    importance=row["importance"],
                    context=row["context"],
                    metadata=json.loads(row["metadata"]) if row["metadata"] else None
                ))
        
        return entries
    
    def get_agent_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get memory summary for an agent."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM memories WHERE agent_id = ?",
                (agent_id,)
            ).fetchone()[0]
            
            avg_importance = conn.execute(
                "SELECT AVG(importance) FROM memories WHERE agent_id = ?",
                (agent_id,)
            ).fetchone()[0] or 0.0
            
            contexts = conn.execute(
                """SELECT context, COUNT(*) as count 
                   FROM memories 
                   WHERE agent_id = ? AND context IS NOT NULL
                   GROUP BY context
                   ORDER BY count DESC""",
                (agent_id,)
            ).fetchall()
            
            return {
                "agent_id": agent_id,
                "total_memories": total,
                "avg_importance": round(avg_importance, 3),
                "top_contexts": {row[0]: row[1] for row in contexts[:5]}
            }
    
    def forget_old_memories(self, days: int = 30, min_importance: float = 0.5):
        """Remove old, low-importance memories."""
        cutoff = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """DELETE FROM memories 
                   WHERE datetime(timestamp) < datetime('now', '-{} days')
                   AND importance < ?""".format(days),
                (min_importance,)
            )
            conn.commit()
    
    def clear_all(self, agent_id: Optional[str] = None):
        """Clear memories (optionally for specific agent)."""
        with sqlite3.connect(self.db_path) as conn:
            if agent_id:
                conn.execute("DELETE FROM memories WHERE agent_id = ?", (agent_id,))
            else:
                conn.execute("DELETE FROM memories")
            conn.commit()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            agents = conn.execute(
                "SELECT COUNT(DISTINCT agent_id) FROM memories"
            ).fetchone()[0]
            
            return {
                "total_memories": total,
                "unique_agents": agents,
                "db_path": str(self.db_path),
                "db_size_mb": round(self.db_path.stat().st_size / (1024 * 1024), 2) if self.db_path.exists() else 0
            }


class LocalMemoryManager:
    """High-level memory manager for Swimming Pauls."""
    
    def __init__(self, db_path: str = "~/.openclaw/workspace/swimming_pauls/data/local_memory.db"):
        self.memory = LocalMemory(db_path)
    
    def remember_prediction(
        self,
        agent_id: str,
        prediction: str,
        confidence: float,
        outcome: Optional[str] = None,
        context: Optional[str] = None
    ):
        """Store a prediction in memory."""
        content = f"Predicted: {prediction} (confidence: {confidence:.2f})"
        if outcome:
            content += f" | Outcome: {outcome}"
        
        entry = MemoryEntry(
            agent_id=agent_id,
            content=content,
            timestamp=datetime.now(),
            importance=confidence,
            context=context or "prediction",
            metadata={"confidence": confidence, "outcome": outcome}
        )
        
        return self.memory.add_memory(entry)
    
    def get_relevant_context(
        self,
        agent_id: str,
        topic: str,
        limit: int = 10
    ) -> List[str]:
        """Get relevant memories for a topic."""
        # Search for topic in memories
        memories = self.memory.search_memories(topic, limit=limit)
        
        # Also get recent memories from this agent
        agent_memories = self.memory.get_memories(agent_id=agent_id, limit=limit)
        
        # Combine and deduplicate
        seen = set()
        combined = []
        
        for m in memories + agent_memories:
            if m.content not in seen:
                seen.add(m.content)
                combined.append(m.content)
        
        return combined[:limit]
    
    def get_learning_summary(self, agent_id: str) -> Dict[str, Any]:
        """Get what an agent has learned."""
        return self.memory.get_agent_summary(agent_id)


# Drop-in replacement for ZepMemoryManager
class ZepMemoryManager:
    """
    Compatibility wrapper that uses LocalMemory instead of Zep Cloud.
    This allows the system to work without any cloud dependencies.
    """
    
    def __init__(self, *args, **kwargs):
        # Ignore Zep-specific args, use local memory
        self.local_memory = LocalMemoryManager()
    
    def add_memory(self, agent_id: str, content: str, **kwargs):
        """Add memory (delegates to local)."""
        entry = MemoryEntry(
            agent_id=agent_id,
            content=content,
            timestamp=datetime.now(),
            metadata=kwargs
        )
        return self.local_memory.memory.add_memory(entry)
    
    def get_memories(self, agent_id: str, **kwargs):
        """Get memories (delegates to local)."""
        return self.local_memory.memory.get_memories(agent_id=agent_id, **kwargs)
    
    def search(self, query: str, **kwargs):
        """Search memories (delegates to local)."""
        return self.local_memory.memory.search_memories(query, **kwargs)


def demo():
    """Demo local memory system."""
    print("=" * 60)
    print("SWIMMING PAULS - Local Memory Demo (No Cloud)")
    print("=" * 60)
    
    # Create memory manager
    memory = LocalMemoryManager()
    
    # Add some memories
    print("\n📝 Adding memories...")
    
    pauls = ["Producer Paul", "Director Paul", "Analyst Paul"]
    
    for paul in pauls:
        memory.remember_prediction(
            agent_id=paul,
            prediction="Netflix stock up 15%",
            confidence=0.75,
            context="earnings_q4"
        )
        print(f"  ✓ {paul} remembered prediction")
    
    # Retrieve memories
    print("\n🔍 Retrieving memories for Producer Paul...")
    memories = memory.memory.get_memories(agent_id="Producer Paul")
    for m in memories:
        print(f"  - {m.content}")
    
    # Search
    print("\n🔎 Searching for 'Netflix'...")
    results = memory.memory.search_memories("Netflix")
    print(f"  Found {len(results)} memories")
    
    # Stats
    print("\n📊 Memory Stats:")
    stats = memory.memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    print("Demo complete - all local, no cloud required!")
    print("=" * 60)


if __name__ == "__main__":
    demo()
