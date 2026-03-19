"""
Temporal Memory System for Swimming Pauls

Allows Pauls to update their beliefs dynamically over simulation time.
Beliefs decay or reinforce based on new evidence and time passed.
Memory has timestamps and provides temporal context to predictions.

Features:
- Belief states with confidence levels that evolve over time
- Decay/reinforcement mechanics based on evidence
- Temporal context in predictions ("3 days ago I thought X, now I think Y")
- Integration with PaulWorld simulation
- Belief change tracking and history

Author: Howard (H.O.W.A.R.D)
"""

import json
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
import sqlite3
from pathlib import Path


class BeliefStatus(Enum):
    """Status of a belief in temporal memory."""
    ACTIVE = "active"           # Currently held belief
    DECAYING = "decaying"       # Losing confidence over time
    REINFORCED = "reinforced"   # Recently strengthened
    CHALLENGED = "challenged"   # Contradicted by new evidence
    ABANDONED = "abandoned"     # No longer held
    REVISED = "revised"         # Updated to a new belief


@dataclass
class Belief:
    """
    A Paul's belief about something with temporal tracking.
    
    Beliefs have confidence that changes over time based on:
    - Time decay (beliefs fade if not reinforced)
    - Evidence (new data can strengthen or weaken)
    - Contradictions (conflicting evidence reduces confidence)
    """
    topic: str                          # What the belief is about
    proposition: str                    # The belief statement
    confidence: float                   # 0.0 to 1.0
    created_at: datetime                # When belief was formed
    last_updated: datetime              # Last modification
    evidence_count: int = 0             # Number of supporting evidence items
    contradiction_count: int = 0        # Number of contradicting evidence items
    status: BeliefStatus = BeliefStatus.ACTIVE
    
    # Temporal tracking
    revision_history: List[Dict] = field(default_factory=list)
    source_reliability: float = 0.5     # How reliable was the source
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert belief to dictionary for storage."""
        return {
            'topic': self.topic,
            'proposition': self.proposition,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'evidence_count': self.evidence_count,
            'contradiction_count': self.contradiction_count,
            'status': self.status.value,
            'revision_history': self.revision_history,
            'source_reliability': self.source_reliability,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Belief':
        """Create belief from dictionary."""
        return cls(
            topic=data['topic'],
            proposition=data['proposition'],
            confidence=data['confidence'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_updated=datetime.fromisoformat(data['last_updated']),
            evidence_count=data.get('evidence_count', 0),
            contradiction_count=data.get('contradiction_count', 0),
            status=BeliefStatus(data.get('status', 'active')),
            revision_history=data.get('revision_history', []),
            source_reliability=data.get('source_reliability', 0.5),
        )
    
    def age_hours(self, current_time: Optional[datetime] = None) -> float:
        """Get age of belief in hours."""
        current = current_time or datetime.now()
        return (current - self.created_at).total_seconds() / 3600
    
    def time_since_update(self, current_time: Optional[datetime] = None) -> float:
        """Get hours since last update."""
        current = current_time or datetime.now()
        return (current - self.last_updated).total_seconds() / 3600


@dataclass
class Evidence:
    """
    Evidence that supports or contradicts a belief.
    """
    belief_topic: str
    content: str
    impact: float                 # -1.0 to 1.0 (negative = contradicts)
    timestamp: datetime
    source: str                   # Where the evidence came from
    reliability: float = 0.5      # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'belief_topic': self.belief_topic,
            'content': self.content[:200],  # Truncate for storage
            'impact': self.impact,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'reliability': self.reliability,
        }


@dataclass
class TemporalContext:
    """
    Temporal context for a prediction, showing belief evolution.
    """
    current_belief: Belief
    previous_beliefs: List[Belief]    # Historical beliefs on same topic
    belief_shift: float               # How much belief changed (-1 to 1)
    time_span_hours: float            # Time covered by history
    evolution_summary: str            # Human-readable summary
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'current_belief': self.current_belief.to_dict(),
            'previous_beliefs': [b.to_dict() for b in self.previous_beliefs],
            'belief_shift': self.belief_shift,
            'time_span_hours': self.time_span_hours,
            'evolution_summary': self.evolution_summary,
        }
    
    def format_temporal_reasoning(self) -> str:
        """Format temporal context as natural language."""
        if not self.previous_beliefs:
            return f"I believe {self.current_belief.proposition} (confidence: {self.current_belief.confidence:.0%})"
        
        newest_old = self.previous_beliefs[0]
        time_ago = self._format_time_ago(self.time_span_hours)
        
        if abs(self.belief_shift) < 0.1:
            return (
                f"{time_ago} I thought {newest_old.proposition} "
                f"(confidence: {newest_old.confidence:.0%}). "
                f"I still hold this belief with {self.current_belief.confidence:.0%} confidence."
            )
        elif self.belief_shift > 0:
            return (
                f"{time_ago} I thought {newest_old.proposition} "
                f"(confidence: {newest_old.confidence:.0%}). "
                f"Now I'm more convinced: {self.current_belief.proposition} "
                f"(confidence: {self.current_belief.confidence:.0%})."
            )
        else:
            return (
                f"{time_ago} I thought {newest_old.proposition} "
                f"(confidence: {newest_old.confidence:.0%}). "
                f"I've changed my view: {self.current_belief.proposition} "
                f"(confidence: {self.current_belief.confidence:.0%})."
            )
    
    def _format_time_ago(self, hours: float) -> str:
        """Format hours as human-readable time phrase."""
        if hours < 1:
            return "Just now"
        elif hours < 24:
            return f"{int(hours)} hour{'s' if hours >= 2 else ''} ago"
        elif hours < 48:
            return "Yesterday"
        elif hours < 168:  # 1 week
            days = int(hours / 24)
            return f"{days} day{'s' if days >= 2 else ''} ago"
        elif hours < 720:  # 30 days
            weeks = int(hours / 168)
            return f"{weeks} week{'s' if weeks >= 2 else ''} ago"
        else:
            months = int(hours / 720)
            return f"{months} month{'s' if months >= 2 else ''} ago"


class TemporalMemory:
    """
    Temporal memory system for managing Paul beliefs over time.
    
    Key features:
    - Belief formation, update, and decay
    - Evidence tracking and weighting
    - Temporal context generation for predictions
    - Belief history and revision tracking
    """
    
    # Configuration constants
    DEFAULT_DECAY_RATE = 0.05          # Confidence decay per hour (5%)
    DEFAULT_REINFORCEMENT_RATE = 0.15  # Confidence gain from evidence
    MAX_BELIEFS_PER_TOPIC = 5          # Keep last N beliefs per topic
    MIN_CONFIDENCE_THRESHOLD = 0.1     # Beliefs below this are abandoned
    MAX_CONFIDENCE = 0.95              # Cap on confidence
    
    def __init__(
        self,
        paul_name: str,
        decay_rate: float = DEFAULT_DECAY_RATE,
        reinforcement_rate: float = DEFAULT_REINFORCEMENT_RATE,
        db_path: Optional[str] = None
    ):
        """
        Initialize temporal memory for a Paul.
        
        Args:
            paul_name: Name of the Paul this memory belongs to
            decay_rate: How fast beliefs decay per hour (0.0-1.0)
            reinforcement_rate: How much evidence reinforces beliefs (0.0-1.0)
            db_path: Optional database path for persistence
        """
        self.paul_name = paul_name
        self.decay_rate = decay_rate
        self.reinforcement_rate = reinforcement_rate
        
        # In-memory storage
        self.beliefs: Dict[str, List[Belief]] = {}  # topic -> list of beliefs
        self.evidence: List[Evidence] = []
        
        # Statistics
        self.beliefs_formed = 0
        self.beliefs_revised = 0
        self.beliefs_abandoned = 0
        
        # Database
        self.db_path = db_path
        if db_path:
            self._init_db()
            self._load_from_db()
    
    def _init_db(self):
        """Initialize SQLite database."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temporal_beliefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paul_name TEXT NOT NULL,
                topic TEXT NOT NULL,
                proposition TEXT NOT NULL,
                confidence REAL NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT NOT NULL,
                evidence_count INTEGER DEFAULT 0,
                contradiction_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                revision_history TEXT,
                source_reliability REAL DEFAULT 0.5
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temporal_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paul_name TEXT NOT NULL,
                belief_topic TEXT NOT NULL,
                content TEXT,
                impact REAL,
                timestamp TEXT NOT NULL,
                source TEXT,
                reliability REAL DEFAULT 0.5
            )
        ''')
        
        # Indexes
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_temporal_beliefs_paul_topic 
            ON temporal_beliefs(paul_name, topic)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_temporal_evidence_paul_topic 
            ON temporal_evidence(paul_name, belief_topic)
        ''')
        
        conn.commit()
        conn.close()
    
    def _load_from_db(self):
        """Load beliefs from database."""
        if not self.db_path:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load beliefs
        cursor.execute('''
            SELECT topic, proposition, confidence, created_at, last_updated,
                   evidence_count, contradiction_count, status, revision_history, source_reliability
            FROM temporal_beliefs
            WHERE paul_name = ? AND status != 'abandoned'
        ''', (self.paul_name,))
        
        for row in cursor.fetchall():
            topic, proposition, confidence, created_at, last_updated, \
            evidence_count, contradiction_count, status, revision_history, source_reliability = row
            
            belief = Belief(
                topic=topic,
                proposition=proposition,
                confidence=confidence,
                created_at=datetime.fromisoformat(created_at),
                last_updated=datetime.fromisoformat(last_updated),
                evidence_count=evidence_count,
                contradiction_count=contradiction_count,
                status=BeliefStatus(status),
                revision_history=json.loads(revision_history) if revision_history else [],
                source_reliability=source_reliability,
            )
            
            if topic not in self.beliefs:
                self.beliefs[topic] = []
            self.beliefs[topic].append(belief)
        
        # Load evidence
        cursor.execute('''
            SELECT belief_topic, content, impact, timestamp, source, reliability
            FROM temporal_evidence
            WHERE paul_name = ?
        ''', (self.paul_name,))
        
        for row in cursor.fetchall():
            self.evidence.append(Evidence(
                belief_topic=row[0],
                content=row[1],
                impact=row[2],
                timestamp=datetime.fromisoformat(row[3]),
                source=row[4],
                reliability=row[5],
            ))
        
        conn.close()
    
    def _save_to_db(self):
        """Save beliefs to database."""
        if not self.db_path:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear and re-insert beliefs
        cursor.execute('DELETE FROM temporal_beliefs WHERE paul_name = ?', (self.paul_name,))
        
        for topic, beliefs in self.beliefs.items():
            for belief in beliefs:
                cursor.execute('''
                    INSERT INTO temporal_beliefs
                    (paul_name, topic, proposition, confidence, created_at, last_updated,
                     evidence_count, contradiction_count, status, revision_history, source_reliability)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.paul_name,
                    belief.topic,
                    belief.proposition,
                    belief.confidence,
                    belief.created_at.isoformat(),
                    belief.last_updated.isoformat(),
                    belief.evidence_count,
                    belief.contradiction_count,
                    belief.status.value,
                    json.dumps(belief.revision_history),
                    belief.source_reliability,
                ))
        
        conn.commit()
        conn.close()
    
    def form_belief(
        self,
        topic: str,
        proposition: str,
        initial_confidence: float = 0.5,
        source_reliability: float = 0.5,
        timestamp: Optional[datetime] = None
    ) -> Belief:
        """
        Form a new belief.
        
        Args:
            topic: What the belief is about
            proposition: The belief statement
            initial_confidence: Starting confidence (0.0-1.0)
            source_reliability: How reliable the source is
            timestamp: Optional timestamp (defaults to now)
        
        Returns:
            The newly formed belief
        """
        now = timestamp or datetime.now()
        
        belief = Belief(
            topic=topic,
            proposition=proposition,
            confidence=min(initial_confidence, self.MAX_CONFIDENCE),
            created_at=now,
            last_updated=now,
            source_reliability=source_reliability,
            revision_history=[{
                'timestamp': now.isoformat(),
                'event': 'belief_formed',
                'confidence': initial_confidence,
            }]
        )
        
        if topic not in self.beliefs:
            self.beliefs[topic] = []
        
        # Archive existing active belief on same topic if exists
        for existing in self.beliefs[topic]:
            if existing.status == BeliefStatus.ACTIVE:
                existing.status = BeliefStatus.REVISED
                existing.revision_history.append({
                    'timestamp': now.isoformat(),
                    'event': 'superseded',
                    'new_proposition': proposition,
                })
        
        self.beliefs[topic].insert(0, belief)
        self.beliefs_formed += 1
        
        # Limit history per topic
        if len(self.beliefs[topic]) > self.MAX_BELIEFS_PER_TOPIC:
            self.beliefs[topic] = self.beliefs[topic][:self.MAX_BELIEFS_PER_TOPIC]
        
        return belief
    
    def add_evidence(
        self,
        topic: str,
        content: str,
        impact: float,
        source: str = "unknown",
        reliability: float = 0.5,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Add evidence that affects beliefs on a topic.
        
        Args:
            topic: Topic the evidence relates to
            content: Description of the evidence
            impact: -1.0 to 1.0 (negative contradicts, positive supports)
            source: Where the evidence came from
            reliability: Source reliability (0.0-1.0)
            timestamp: Optional timestamp
        """
        now = timestamp or datetime.now()
        
        evidence = Evidence(
            belief_topic=topic,
            content=content,
            impact=impact,
            timestamp=now,
            source=source,
            reliability=reliability,
        )
        self.evidence.append(evidence)
        
        # Apply to relevant beliefs
        if topic in self.beliefs:
            for belief in self.beliefs[topic]:
                if belief.status in [BeliefStatus.ACTIVE, BeliefStatus.DECAYING, BeliefStatus.CHALLENGED]:
                    self._apply_evidence_to_belief(belief, evidence)
        
        # Save evidence to DB
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO temporal_evidence
                (paul_name, belief_topic, content, impact, timestamp, source, reliability)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.paul_name, topic, content[:200], impact,
                now.isoformat(), source, reliability
            ))
            conn.commit()
            conn.close()
    
    def _apply_evidence_to_belief(self, belief: Belief, evidence: Evidence) -> None:
        """Apply evidence impact to a belief."""
        # Weight by reliability
        weighted_impact = evidence.impact * evidence.reliability * belief.source_reliability
        
        if weighted_impact > 0:
            # Supporting evidence
            belief.evidence_count += 1
            belief.confidence = min(
                self.MAX_CONFIDENCE,
                belief.confidence + (weighted_impact * self.reinforcement_rate)
            )
            belief.status = BeliefStatus.REINFORCED
            belief.revision_history.append({
                'timestamp': evidence.timestamp.isoformat(),
                'event': 'evidence_supporting',
                'impact': weighted_impact,
                'new_confidence': belief.confidence,
            })
        elif weighted_impact < 0:
            # Contradicting evidence
            belief.contradiction_count += 1
            belief.confidence = max(
                0.0,
                belief.confidence + (weighted_impact * self.reinforcement_rate)
            )
            belief.status = BeliefStatus.CHALLENGED
            belief.revision_history.append({
                'timestamp': evidence.timestamp.isoformat(),
                'event': 'evidence_contradicting',
                'impact': weighted_impact,
                'new_confidence': belief.confidence,
            })
            
            # Check if belief should be abandoned
            if belief.confidence < self.MIN_CONFIDENCE_THRESHOLD:
                belief.status = BeliefStatus.ABANDONED
                belief.revision_history.append({
                    'timestamp': evidence.timestamp.isoformat(),
                    'event': 'belief_abandoned',
                    'reason': 'confidence_below_threshold',
                })
                self.beliefs_abandoned += 1
        
        belief.last_updated = evidence.timestamp
    
    def decay_beliefs(self, current_time: Optional[datetime] = None) -> List[Belief]:
        """
        Apply time-based decay to all active beliefs.
        
        Beliefs lose confidence over time if not reinforced.
        
        Args:
            current_time: Optional current timestamp
        
        Returns:
            List of beliefs that were decayed
        """
        now = current_time or datetime.now()
        decayed = []
        
        for topic, beliefs in self.beliefs.items():
            for belief in beliefs:
                if belief.status not in [BeliefStatus.ACTIVE, BeliefStatus.REINFORCED, BeliefStatus.CHALLENGED]:
                    continue
                
                hours_since_update = belief.time_since_update(now)
                
                if hours_since_update > 24:  # Start decaying after 24 hours
                    decay_amount = self.decay_rate * (hours_since_update / 24)
                    old_confidence = belief.confidence
                    belief.confidence = max(0.0, belief.confidence - decay_amount)
                    
                    if belief.confidence < self.MIN_CONFIDENCE_THRESHOLD:
                        belief.status = BeliefStatus.ABANDONED
                        self.beliefs_abandoned += 1
                    elif belief.confidence < old_confidence:
                        belief.status = BeliefStatus.DECAYING
                        decayed.append(belief)
                        belief.revision_history.append({
                            'timestamp': now.isoformat(),
                            'event': 'time_decay',
                            'hours_elapsed': hours_since_update,
                            'old_confidence': old_confidence,
                            'new_confidence': belief.confidence,
                        })
                    
                    belief.last_updated = now
        
        return decayed
    
    def get_belief(self, topic: str, include_challenged: bool = False) -> Optional[Belief]:
        """
        Get the current active belief on a topic.
        
        Args:
            topic: Topic to query
            include_challenged: Whether to include challenged beliefs
        
        Returns:
            Current belief or None if no active belief
        """
        if topic not in self.beliefs:
            return None
        
        active_statuses = [BeliefStatus.ACTIVE, BeliefStatus.REINFORCED]
        if include_challenged:
            active_statuses.append(BeliefStatus.CHALLENGED)
        
        for belief in self.beliefs[topic]:
            if belief.status in active_statuses:
                return belief
            elif belief.status == BeliefStatus.ABANDONED and include_challenged:
                return belief
        
        # Return the most recent belief even if abandoned (for history tracking)
        if self.beliefs[topic]:
            return self.beliefs[topic][0]
        
        return None
    
    def get_belief_history(self, topic: str, limit: int = 5) -> List[Belief]:
        """
        Get history of beliefs on a topic.
        
        Args:
            topic: Topic to query
            limit: Maximum number of beliefs to return
        
        Returns:
            List of beliefs (newest first)
        """
        if topic not in self.beliefs:
            return []
        
        return self.beliefs[topic][:limit]
    
    def get_temporal_context(
        self,
        topic: str,
        current_time: Optional[datetime] = None
    ) -> Optional[TemporalContext]:
        """
        Get temporal context for a topic.
        
        Args:
            topic: Topic to get context for
            current_time: Optional current timestamp
        
        Returns:
            TemporalContext or None if no beliefs exist
        """
        now = current_time or datetime.now()
        history = self.get_belief_history(topic)
        
        if not history:
            return None
        
        current = history[0]
        previous = history[1:] if len(history) > 1 else []
        
        # Calculate belief shift
        if previous:
            newest_old = previous[0]
            belief_shift = current.confidence - newest_old.confidence
            time_span = (now - newest_old.created_at).total_seconds() / 3600
        else:
            belief_shift = 0.0
            time_span = 0.0
        
        # Generate evolution summary
        if not previous:
            evolution = f"Recently formed belief: {current.proposition}"
        elif abs(belief_shift) < 0.1:
            evolution = f"Stable belief maintained over {self._format_hours(time_span)}"
        elif belief_shift > 0:
            evolution = f"Confidence strengthened by {belief_shift:.0%} over {self._format_hours(time_span)}"
        else:
            evolution = f"Confidence weakened by {abs(belief_shift):.0%} over {self._format_hours(time_span)}"
        
        return TemporalContext(
            current_belief=current,
            previous_beliefs=previous,
            belief_shift=belief_shift,
            time_span_hours=time_span,
            evolution_summary=evolution,
        )
    
    def get_all_active_beliefs(self, include_challenged: bool = False) -> List[Belief]:
        """Get all currently active beliefs across all topics."""
        active = []
        for topic, beliefs in self.beliefs.items():
            for belief in beliefs:
                if belief.status in [BeliefStatus.ACTIVE, BeliefStatus.REINFORCED]:
                    active.append(belief)
                elif include_challenged and belief.status == BeliefStatus.CHALLENGED:
                    active.append(belief)
        return active
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about this temporal memory."""
        total_beliefs = sum(len(b) for b in self.beliefs.values())
        active_beliefs = len(self.get_all_active_beliefs())
        
        topic_confidences = {}
        for topic, beliefs in self.beliefs.items():
            active_in_topic = [b.confidence for b in beliefs 
                             if b.status in [BeliefStatus.ACTIVE, BeliefStatus.REINFORCED]]
            if active_in_topic:
                topic_confidences[topic] = sum(active_in_topic) / len(active_in_topic)
        
        return {
            'paul_name': self.paul_name,
            'total_beliefs_formed': self.beliefs_formed,
            'total_beliefs_revised': self.beliefs_revised,
            'total_beliefs_abandoned': self.beliefs_abandoned,
            'current_total_beliefs': total_beliefs,
            'active_beliefs': active_beliefs,
            'topics_count': len(self.beliefs),
            'evidence_count': len(self.evidence),
            'average_confidence': sum(topic_confidences.values()) / len(topic_confidences) if topic_confidences else 0,
            'topic_confidences': topic_confidences,
        }
    
    def _format_hours(self, hours: float) -> str:
        """Format hours as readable string."""
        if hours < 24:
            return f"{int(hours)}h"
        elif hours < 168:
            return f"{int(hours/24)}d"
        else:
            return f"{int(hours/168)}w"
    
    def save(self) -> None:
        """Save temporal memory to database."""
        self._save_to_db()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export temporal memory as dictionary."""
        return {
            'paul_name': self.paul_name,
            'decay_rate': self.decay_rate,
            'reinforcement_rate': self.reinforcement_rate,
            'beliefs': {
                topic: [b.to_dict() for b in beliefs]
                for topic, beliefs in self.beliefs.items()
            },
            'statistics': self.get_statistics(),
        }


class TemporalMemoryManager:
    """
    Manager for all Pauls' temporal memories.
    
    Coordinates belief updates, decay cycles, and cross-Paul influence.
    """
    
    def __init__(self, db_path: Optional[str] = "data/temporal_memory.db"):
        self.db_path = db_path
        self.memories: Dict[str, TemporalMemory] = {}
        if db_path:
            self._init_db()
    
    def _init_db(self):
        """Initialize database."""
        if not self.db_path:
            return
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temporal_memory_config (
                paul_name TEXT PRIMARY KEY,
                decay_rate REAL DEFAULT 0.05,
                reinforcement_rate REAL DEFAULT 0.15,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_memory(self, paul_name: str) -> TemporalMemory:
        """Get or create temporal memory for a Paul."""
        if paul_name not in self.memories:
            self.memories[paul_name] = TemporalMemory(
                paul_name=paul_name,
                db_path=self.db_path
            )
        return self.memories[paul_name]
    
    def decay_all(self, current_time: Optional[datetime] = None) -> Dict[str, List[Belief]]:
        """Apply decay to all Pauls' beliefs."""
        results = {}
        for paul_name, memory in self.memories.items():
            results[paul_name] = memory.decay_beliefs(current_time)
        return results
    
    def get_cross_paul_consensus(self, topic: str) -> Dict[str, Any]:
        """
        Get consensus across all Pauls on a topic.
        
        Returns statistics about how Pauls' beliefs align or diverge.
        """
        beliefs = []
        for paul_name, memory in self.memories.items():
            belief = memory.get_belief(topic)
            if belief:
                beliefs.append({
                    'paul_name': paul_name,
                    'proposition': belief.proposition,
                    'confidence': belief.confidence,
                    'status': belief.status.value,
                })
        
        if not beliefs:
            return {'topic': topic, 'consensus': 'no_data', 'beliefs': []}
        
        # Calculate consensus metrics
        avg_confidence = sum(b['confidence'] for b in beliefs) / len(beliefs)
        propositions = {}
        for b in beliefs:
            prop = b['proposition']
            propositions[prop] = propositions.get(prop, 0) + 1
        
        most_common = max(propositions.items(), key=lambda x: x[1])
        consensus_strength = most_common[1] / len(beliefs)
        
        return {
            'topic': topic,
            'consensus': 'strong' if consensus_strength > 0.7 else 'moderate' if consensus_strength > 0.5 else 'divergent',
            'consensus_strength': consensus_strength,
            'average_confidence': avg_confidence,
            'pauls_count': len(beliefs),
            'dominant_view': most_common[0],
            'beliefs': beliefs,
        }
    
    def spread_influence(
        self,
        source_paul: str,
        target_paul: str,
        topic: str,
        influence_strength: float = 0.3
    ) -> bool:
        """
        Allow one Paul to influence another's belief.
        
        This simulates social learning and persuasion.
        
        Args:
            source_paul: Paul with the influencing belief
            target_paul: Paul being influenced
            topic: Topic to influence
            influence_strength: How strong the influence is (0.0-1.0)
        
        Returns:
            True if influence was applied
        """
        source_memory = self.get_memory(source_paul)
        target_memory = self.get_memory(target_paul)
        
        source_belief = source_memory.get_belief(topic)
        if not source_belief:
            return False
        
        # Check if target already has a belief
        target_belief = target_memory.get_belief(topic)
        
        if target_belief:
            # Reinforce if similar
            if target_belief.proposition == source_belief.proposition:
                target_memory.add_evidence(
                    topic=topic,
                    content=f"Influenced by {source_paul}",
                    impact=influence_strength * source_belief.confidence,
                    source=f"social:{source_paul}",
                    reliability=source_belief.confidence,
                )
            else:
                # Challenge if different
                target_memory.add_evidence(
                    topic=topic,
                    content=f"Conflicting view from {source_paul}",
                    impact=-influence_strength * source_belief.confidence,
                    source=f"social:{source_paul}",
                    reliability=source_belief.confidence,
                )
        else:
            # Adopt belief if none exists
            target_memory.form_belief(
                topic=topic,
                proposition=source_belief.proposition,
                initial_confidence=source_belief.confidence * influence_strength,
                source_reliability=source_belief.confidence,
            )
        
        return True
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all Pauls."""
        return {
            paul_name: memory.get_statistics()
            for paul_name, memory in self.memories.items()
        }
    
    def save_all(self) -> None:
        """Save all temporal memories."""
        for memory in self.memories.values():
            memory.save()


# ============================================================================
# Integration Helpers
# ============================================================================

def create_temporal_prediction_reasoning(
    temporal_context: TemporalContext,
    base_reasoning: str = ""
) -> str:
    """
    Create prediction reasoning that includes temporal context.
    
    This creates the "3 days ago I thought X, now I think Y" style reasoning.
    
    Args:
        temporal_context: The temporal context for the belief
        base_reasoning: Additional base reasoning to include
    
    Returns:
        Combined reasoning string with temporal narrative
    """
    parts = []
    
    # Add temporal evolution
    temporal_part = temporal_context.format_temporal_reasoning()
    if temporal_part:
        parts.append(temporal_part)
    
    # Add base reasoning
    if base_reasoning:
        parts.append(base_reasoning)
    
    # Add confidence context
    if temporal_context.belief_shift > 0.2:
        parts.append("Recent evidence has strengthened my conviction.")
    elif temporal_context.belief_shift < -0.2:
        parts.append("Recent evidence has made me reconsider my position.")
    
    return " ".join(parts)


def simulate_belief_evolution(
    topic: str,
    initial_proposition: str,
    evidence_sequence: List[Tuple[float, str]],  # (impact, description)
    decay_rate: float = 0.05,
    reinforcement_rate: float = 0.15
) -> List[Dict[str, Any]]:
    """
    Simulate how a belief would evolve given a sequence of evidence.
    
    Useful for testing and demonstrating belief evolution.
    
    Args:
        topic: Topic of the belief
        initial_proposition: Starting belief
        evidence_sequence: List of (impact, description) tuples
        decay_rate: Decay rate to use
        reinforcement_rate: Reinforcement rate to use
    
    Returns:
        List of belief states over time
    """
    memory = TemporalMemory(
        paul_name="simulator",
        decay_rate=decay_rate,
        reinforcement_rate=reinforcement_rate
    )
    
    # Form initial belief
    belief = memory.form_belief(topic, initial_proposition, initial_confidence=0.5)
    
    history = [{
        'step': 0,
        'event': 'initial_belief',
        'confidence': belief.confidence,
        'status': belief.status.value,
    }]
    
    # Apply each piece of evidence
    for i, (impact, description) in enumerate(evidence_sequence, 1):
        memory.add_evidence(topic, description, impact)
        
        # Get updated belief
        updated = memory.get_belief(topic)
        if updated:
            history.append({
                'step': i,
                'event': f'evidence: {description[:30]}...',
                'impact': impact,
                'confidence': updated.confidence,
                'status': updated.status.value,
            })
    
    return history


# ============================================================================
# Exports
# ============================================================================

__all__ = [
    'TemporalMemory',
    'TemporalMemoryManager',
    'Belief',
    'BeliefStatus',
    'Evidence',
    'TemporalContext',
    'create_temporal_prediction_reasoning',
    'simulate_belief_evolution',
]
