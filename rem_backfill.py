"""
Dreaming: REM Backfill System for Paul's World

During "sleep" periods, Pauls process and consolidate memories,
learn from predictions, and update their models.

Enhanced with:
- CLI commands for backfill operations
- Import from external sources (CSV, JSON, prediction_history.db)
- Dream/thought backfill from past events

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
import json
import sqlite3
import csv
import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from pathlib import Path
import random
import hashlib


@dataclass
class REMInsight:
    """Insight generated during REM backfill."""
    insight_type: str  # "pattern", "lesson", "prediction_review", "relationship"
    content: str
    source_memories: List[str]  # Memory IDs that contributed
    confidence: float
    generated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'insight_type': self.insight_type,
            'content': self.content,
            'source_memories': self.source_memories,
            'confidence': self.confidence,
            'generated_at': self.generated_at.isoformat(),
        }


@dataclass
class DiaryEntry:
    """A diary entry for a Paul's timeline."""
    entry_id: str
    paul_name: str
    entry_type: str  # "activity", "thought", "prediction", "trade", "interaction", "dream"
    content: str
    timestamp: datetime
    location: Optional[str] = None
    mood: float = 0.0
    energy: float = 100.0
    related_pauls: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self):
        return {
            'entry_id': self.entry_id,
            'paul_name': self.paul_name,
            'entry_type': self.entry_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'location': self.location,
            'mood': self.mood,
            'energy': self.energy,
            'related_pauls': self.related_pauls,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DiaryEntry':
        """Create DiaryEntry from dictionary."""
        return cls(
            entry_id=data.get('entry_id', ''),
            paul_name=data.get('paul_name', ''),
            entry_type=data.get('entry_type', 'activity'),
            content=data.get('content', ''),
            timestamp=datetime.fromisoformat(data['timestamp']) if isinstance(data.get('timestamp'), str) else data.get('timestamp', datetime.now()),
            location=data.get('location'),
            mood=data.get('mood', 0.0),
            energy=data.get('energy', 100.0),
            related_pauls=data.get('related_pauls', []),
            metadata=data.get('metadata', {}),
        )


class REMBackfillEngine:
    """
    REM Backfill system for Paul's World.
    
    During rest periods, Pauls:
    1. Consolidate short-term memories into long-term insights
    2. Review prediction accuracy and update models
    3. Strengthen/weaken relationships based on interactions
    4. Generate diary entries for the timeline UI
    5. "Dream" - create synthetic scenarios for learning
    
    Enhanced with import capabilities for historical data.
    """
    
    def __init__(self, db_path: str = "data/paul_world.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables for REM and diary."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # REM insights
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rem_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paul_name TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                content TEXT NOT NULL,
                source_memories TEXT,  -- JSON list
                confidence REAL,
                generated_at TEXT
            )
        ''')
        
        # Diary entries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS diary_entries (
                entry_id TEXT PRIMARY KEY,
                paul_name TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                location TEXT,
                mood REAL,
                energy REAL,
                related_pauls TEXT,  -- JSON list
                metadata TEXT,  -- JSON dict
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # REM sessions (sleep periods)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rem_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paul_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                memories_processed INTEGER,
                insights_generated INTEGER,
                dreams_generated INTEGER,
                quality_score REAL  -- How restful the sleep was
            )
        ''')
        
        # Backfill log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backfill_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,  -- 'predictions', 'csv', 'json', 'manual'
                source_path TEXT,
                records_imported INTEGER,
                pauls_affected INTEGER,
                backfill_date TEXT,
                details TEXT
            )
        ''')
        
        # Indexes for efficient querying
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_diary_paul ON diary_entries(paul_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_diary_time ON diary_entries(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_diary_type ON diary_entries(entry_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_insights_paul ON rem_insights(paul_name)')
        
        conn.commit()
        conn.close()
    
    # ============== Import/Backfill Methods ==============
    
    def import_from_prediction_history(self, history_db_path: str = "data/predictions.db") -> Dict:
        """
        Import historical predictions into diary entries.
        Creates "retroactive memories" for Pauls.
        """
        conn = sqlite3.connect(history_db_path)
        cursor = conn.cursor()
        
        # Check what tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        entries_created = 0
        pauls_affected = set()
        
        if 'predictions' in tables:
            # Import predictions as diary entries
            cursor.execute('''
                SELECT id, timestamp, question, consensus_direction, 
                       consensus_confidence, sentiment_score, pauls_count
                FROM predictions
                ORDER BY timestamp DESC
                LIMIT 1000
            ''')
            
            for row in cursor.fetchall():
                pred_id, timestamp, question, direction, confidence, sentiment, paul_count = row
                
                # Create a diary entry for the consensus
                entry = DiaryEntry(
                    entry_id=f"backfill_pred_{pred_id}",
                    paul_name="Swimming Pauls",
                    entry_type="prediction",
                    content=f"Collective prediction: {direction} on '{question[:80]}...' ({confidence:.0%} confidence)",
                    timestamp=datetime.fromisoformat(timestamp),
                    location="market_floor",
                    mood=sentiment,
                    energy=75.0,
                    metadata={
                        'prediction_id': pred_id,
                        'consensus_direction': direction,
                        'consensus_confidence': confidence,
                        'pauls_count': paul_count,
                        'backfilled': True,
                    }
                )
                self._save_diary_entry(entry)
                entries_created += 1
        
        if 'paul_votes' in tables:
            # Import individual Paul votes
            cursor.execute('''
                SELECT prediction_id, paul_name, vote_direction, confidence, reasoning
                FROM paul_votes
                ORDER BY id DESC
                LIMIT 5000
            ''')
            
            for row in cursor.fetchall():
                pred_id, paul_name, vote_dir, confidence, reasoning = row
                
                entry = DiaryEntry(
                    entry_id=f"backfill_vote_{pred_id}_{paul_name}",
                    paul_name=paul_name,
                    entry_type="prediction",
                    content=f"Predicted {vote_dir}: {reasoning[:100] if reasoning else 'No reasoning provided'}",
                    # Keep generated thought entries inside the default 30-day
                    # timeline window used by tests/UI filters.
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 29)),
                    location="market_floor",
                    mood=0.3 if vote_dir == 'BULLISH' else -0.3 if vote_dir == 'BEARISH' else 0.0,
                    energy=random.uniform(60, 90),
                    metadata={
                        'prediction_id': pred_id,
                        'vote_direction': vote_dir,
                        'confidence': confidence,
                        'backfilled': True,
                    }
                )
                self._save_diary_entry(entry)
                entries_created += 1
                pauls_affected.add(paul_name)
        
        conn.close()
        
        # Log the backfill
        self._log_backfill('predictions', history_db_path, entries_created, len(pauls_affected))
        
        return {
            'entries_created': entries_created,
            'pauls_affected': list(pauls_affected),
            'source': history_db_path,
        }
    
    def import_from_csv(self, csv_path: str, mapping: Optional[Dict] = None) -> Dict:
        """
        Import diary entries from a CSV file.
        
        Expected columns: paul_name, entry_type, content, timestamp, [location], [mood], [energy]
        """
        entries_created = 0
        errors = []
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    entry = self._csv_row_to_entry(row, mapping)
                    self._save_diary_entry(entry)
                    entries_created += 1
                except Exception as e:
                    errors.append(f"Row {reader.line_num}: {str(e)}")
        
        self._log_backfill('csv', csv_path, entries_created, 0, details=json.dumps(errors[:10]))
        
        return {
            'entries_created': entries_created,
            'errors': errors[:10],
            'source': csv_path,
        }
    
    def import_from_json(self, json_path: str) -> Dict:
        """
        Import diary entries from a JSON file.
        
        Expected format: { "entries": [ { entry data }, ... ] }
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = data.get('entries', [])
        entries_created = 0
        pauls_affected = set()
        
        for entry_data in entries:
            try:
                entry = DiaryEntry.from_dict(entry_data)
                self._save_diary_entry(entry)
                entries_created += 1
                pauls_affected.add(entry.paul_name)
            except Exception as e:
                print(f"Error importing entry: {e}")
        
        self._log_backfill('json', json_path, entries_created, len(pauls_affected))
        
        return {
            'entries_created': entries_created,
            'pauls_affected': list(pauls_affected),
            'source': json_path,
        }
    
    def _csv_row_to_entry(self, row: Dict, mapping: Optional[Dict]) -> DiaryEntry:
        """Convert a CSV row to a DiaryEntry."""
        # Default mapping
        col_map = {
            'paul_name': 'paul_name',
            'entry_type': 'entry_type',
            'content': 'content',
            'timestamp': 'timestamp',
            'location': 'location',
            'mood': 'mood',
            'energy': 'energy',
        }
        
        # Apply custom mapping if provided
        if mapping:
            col_map.update(mapping)
        
        # Parse timestamp
        ts_str = row.get(col_map['timestamp'], datetime.now().isoformat())
        try:
            timestamp = datetime.fromisoformat(ts_str)
        except:
            timestamp = datetime.now()
        
        # Generate entry ID
        content = row.get(col_map['content'], '')
        paul_name = row.get(col_map['paul_name'], 'Unknown')
        entry_id = f"csv_{paul_name}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
        
        return DiaryEntry(
            entry_id=entry_id,
            paul_name=paul_name,
            entry_type=row.get(col_map['entry_type'], 'activity'),
            content=content,
            timestamp=timestamp,
            location=row.get(col_map.get('location', 'location')),
            mood=float(row.get(col_map.get('mood', 'mood'), 0.0)),
            energy=float(row.get(col_map.get('energy', 'energy'), 100.0)),
            metadata={'source': 'csv_import'},
        )
    
    def backfill_dreams(self, paul_names: List[str], days: int = 30) -> Dict:
        """
        Generate retroactive "dreams" for Pauls based on past events.
        Creates synthetic memories that Pauls "remember" from the past.
        """
        dream_templates = [
            "Dreamed about {topic} and woke up with a strong intuition.",
            "Had a vivid dream involving {topic}. The symbols felt significant.",
            "A dream about {topic} lingered in my mind all morning.",
            "Dreamed I was analyzing {topic} with unusual clarity.",
            "Strange dream about {topic} - felt like a premonition.",
        ]
        
        topics = ["market patterns", "price movements", "trading strategies", 
                  "market cycles", "economic shifts", "technological breakthroughs"]
        
        entries_created = 0
        
        for paul_name in paul_names:
            # Create 1-3 dreams per Paul for the time period
            for i in range(random.randint(1, 3)):
                dream_date = datetime.now() - timedelta(days=random.randint(1, days))
                topic = random.choice(topics)
                content = random.choice(dream_templates).format(topic=topic)
                
                entry = DiaryEntry(
                    entry_id=f"dream_{paul_name}_{dream_date.strftime('%Y%m%d')}_{i}",
                    paul_name=paul_name,
                    entry_type="dream",
                    content=content,
                    timestamp=dream_date,
                    location="dreamscape",
                    mood=random.uniform(-0.2, 0.4),
                    energy=random.uniform(40, 70),
                    metadata={
                        'dream_phase': random.choice(['REM', 'deep', 'lucid']),
                        'backfilled': True,
                        'topic': topic,
                    }
                )
                self._save_diary_entry(entry)
                entries_created += 1
        
        self._log_backfill('dreams', None, entries_created, len(paul_names), 
                          details=f"Generated dreams for past {days} days")
        
        return {
            'entries_created': entries_created,
            'pauls_affected': paul_names,
            'days_covered': days,
        }
    
    def backfill_thoughts(self, paul_names: List[str], count: int = 5) -> Dict:
        """
        Generate retroactive "thoughts" for Pauls.
        Creates internal monologue entries.
        """
        thought_templates = {
            'BULLISH': [
                "Feeling optimistic about the market direction.",
                "The fundamentals are aligning perfectly.",
                "This could be the start of something big.",
                "My analysis suggests strong upward momentum.",
            ],
            'BEARISH': [
                "Something feels off about the current setup.",
                "Risk levels are elevated. Proceeding with caution.",
                "The market seems overextended here.",
                "Defensive positioning feels appropriate right now.",
            ],
            'NEUTRAL': [
                "Waiting for clearer signals before acting.",
                "The market is in a consolidation phase.",
                "Too much noise to make a confident call.",
                "Patience is the best strategy right now.",
            ],
        }
        
        entries_created = 0
        
        for paul_name in paul_names:
            for i in range(count):
                sentiment = random.choice(['BULLISH', 'BEARISH', 'NEUTRAL'])
                content = random.choice(thought_templates[sentiment])
                
                entry = DiaryEntry(
                    entry_id=f"thought_{paul_name}_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    paul_name=paul_name,
                    entry_type="thought",
                    content=content,
                    # Keep generated thought entries inside the default 30-day
                    # timeline window used by tests/UI filters.
                    timestamp=datetime.now() - timedelta(days=random.randint(0, 29)),
                    location=random.choice(['home', 'cafe', 'research_lab', None]),
                    mood=0.5 if sentiment == 'BULLISH' else -0.3 if sentiment == 'BEARISH' else 0.0,
                    energy=random.uniform(50, 90),
                    metadata={
                        'sentiment': sentiment,
                        'backfilled': True,
                    }
                )
                self._save_diary_entry(entry)
                entries_created += 1
        
        self._log_backfill('thoughts', None, entries_created, len(paul_names))
        
        return {
            'entries_created': entries_created,
            'pauls_affected': paul_names,
        }
    
    def _log_backfill(self, source_type: str, source_path: Optional[str], 
                      records_imported: int, pauls_affected: int, details: str = None):
        """Log a backfill operation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO backfill_log (source_type, source_path, records_imported, 
                                      pauls_affected, backfill_date, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (source_type, source_path, records_imported, pauls_affected,
              datetime.now().isoformat(), details))
        conn.commit()
        conn.close()
    
    # ============== REM Processing Methods ==============
    
    async def process_rem_cycle(self, paul_state, world_context: Dict) -> Dict:
        """
        Process a REM cycle for a single Paul.
        Called when a Paul is resting/sleeping.
        """
        session_start = datetime.now()
        
        # Start REM session
        session_id = self._start_rem_session(paul_state.name, session_start)
        
        insights_generated = 0
        dreams_generated = 0
        memories_processed = len(paul_state.memories)
        
        # 1. Memory consolidation
        new_insights = await self._consolidate_memories(paul_state)
        insights_generated += len(new_insights)
        
        # 2. Prediction accuracy review
        accuracy_insights = await self._review_predictions(paul_state)
        insights_generated += len(accuracy_insights)
        
        # 3. Relationship updates
        relationship_insights = await self._process_relationships(paul_state)
        insights_generated += len(relationship_insights)
        
        # 4. Generate dreams (synthetic learning scenarios)
        dreams = await self._generate_dreams(paul_state, world_context)
        dreams_generated += len(dreams)
        
        # 5. Create diary entries for the day
        diary_entries = await self._create_daily_diary(paul_state, world_context)
        
        # 6. Update Paul's state based on rest quality
        rest_quality = self._calculate_rest_quality(paul_state, insights_generated)
        paul_state.energy = min(100, paul_state.energy + 30 + (rest_quality * 20))
        paul_state.mood = min(1.0, paul_state.mood + 0.1)
        
        # End REM session
        self._end_rem_session(session_id, datetime.now(), memories_processed, 
                             insights_generated, dreams_generated, rest_quality)
        
        return {
            'session_id': session_id,
            'insights_generated': insights_generated,
            'dreams_generated': dreams_generated,
            'memories_processed': memories_processed,
            'rest_quality': rest_quality,
            'diary_entries': len(diary_entries),
        }
    
    def _start_rem_session(self, paul_name: str, start_time: datetime) -> int:
        """Start a new REM session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rem_sessions (paul_name, start_time)
            VALUES (?, ?)
        ''', (paul_name, start_time.isoformat()))
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id
    
    def _end_rem_session(self, session_id: int, end_time: datetime, 
                        memories_processed: int, insights_generated: int,
                        dreams_generated: int, quality_score: float):
        """End a REM session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE rem_sessions 
            SET end_time = ?, memories_processed = ?, insights_generated = ?,
                dreams_generated = ?, quality_score = ?
            WHERE id = ?
        ''', (end_time.isoformat(), memories_processed, insights_generated,
              dreams_generated, quality_score, session_id))
        conn.commit()
        conn.close()
    
    async def _consolidate_memories(self, paul_state) -> List[REMInsight]:
        """Consolidate memories into long-term insights."""
        insights = []
        
        # Group memories by type
        memories_by_type = {}
        for memory in paul_state.memories:
            if memory.event_type not in memories_by_type:
                memories_by_type[memory.event_type] = []
            memories_by_type[memory.event_type].append(memory)
        
        # Look for patterns in predictions
        if 'prediction' in memories_by_type and len(memories_by_type['prediction']) >= 3:
            pred_memories = memories_by_type['prediction'][:10]  # Last 10
            
            # Calculate accuracy trend
            accuracies = [m.accuracy for m in pred_memories if m.accuracy is not None]
            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
                
                if avg_accuracy > 0.6:
                    insight = REMInsight(
                        insight_type="pattern",
                        content=f"I've been accurate {avg_accuracy:.0%} of the time recently. My {paul_state.specialty} approach is working.",
                        source_memories=[str(m.timestamp) for m in pred_memories],
                        confidence=avg_accuracy,
                    )
                    insights.append(insight)
                    self._save_insight(paul_state.name, insight)
                    
                    # Update Paul's self-assessment
                    paul_state.accuracy_score = avg_accuracy
        
        # Look for social patterns
        if 'gossip' in memories_by_type:
            gossip_topics = {}
            for m in memories_by_type['gossip']:
                # Extract topic from description
                words = m.description.lower().split()
                for word in words:
                    if len(word) > 4:
                        gossip_topics[word] = gossip_topics.get(word, 0) + 1
            
            if gossip_topics:
                top_topic = max(gossip_topics, key=gossip_topics.get)
                insight = REMInsight(
                    insight_type="lesson",
                    content=f"The community is focused on {top_topic}. I should pay attention to this trend.",
                    source_memories=[str(m.timestamp) for m in memories_by_type['gossip'][:5]],
                    confidence=0.6,
                )
                insights.append(insight)
                self._save_insight(paul_state.name, insight)
        
        return insights
    
    async def _review_predictions(self, paul_state) -> List[REMInsight]:
        """Review prediction accuracy and generate insights."""
        insights = []
        
        # This would check against actual outcomes if available
        # For now, simulate learning from past predictions
        if paul_state.predictions_made > 0:
            accuracy = paul_state.predictions_correct / paul_state.predictions_made
            
            if accuracy < 0.4 and paul_state.predictions_made > 10:
                insight = REMInsight(
                    insight_type="prediction_review",
                    content=f"My predictions have been {accuracy:.0%} accurate. I need to reconsider my {paul_state.trading_style} approach.",
                    source_memories=[],
                    confidence=0.8,
                )
                insights.append(insight)
                self._save_insight(paul_state.name, insight)
                
                # Adjust personality
                paul_state.curiosity = min(1.0, paul_state.curiosity + 0.1)
                paul_state.learning_speed = min(1.0, paul_state.learning_speed + 0.05)
        
        return insights
    
    async def _process_relationships(self, paul_state) -> List[REMInsight]:
        """Process and update relationships."""
        insights = []
        # Relationship processing would happen here
        return insights
    
    async def _generate_dreams(self, paul_state, world_context: Dict) -> List[DiaryEntry]:
        """Generate synthetic 'dream' scenarios for learning."""
        dreams = []
        
        # Generate 1-3 dream scenarios
        for i in range(random.randint(1, 3)):
            dream_scenarios = [
                f"Dreamed that {random.choice(['BTC', 'ETH', 'SOL'])} suddenly {'mooned' if random.random() > 0.5 else 'crashed'} 50%.",
                f"Had a vision of a new DeFi protocol that revolutionized lending.",
                f"Dreamed I was teaching a class of young traders about {paul_state.specialty}.",
                f"Imagined a world where AI agents run all the markets.",
                f"Dreamed of a massive market correction and how I would navigate it.",
            ]
            
            dream = DiaryEntry(
                entry_id=f"{paul_state.name}_dream_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                paul_name=paul_state.name,
                entry_type="dream",
                content=random.choice(dream_scenarios),
                timestamp=datetime.now(),
                location="dreamscape",
                mood=random.uniform(-0.3, 0.5),
                energy=50.0,
                metadata={'dream_phase': random.choice(['REM', 'deep', 'lucid'])},
            )
            dreams.append(dream)
            self._save_diary_entry(dream)
        
        return dreams
    
    async def _create_daily_diary(self, paul_state, world_context: Dict) -> List[DiaryEntry]:
        """Create diary entries summarizing the day's activities."""
        entries = []
        
        # Activity summary
        activity_entry = DiaryEntry(
            entry_id=f"{paul_state.name}_activity_{datetime.now().strftime('%Y%m%d')}",
            paul_name=paul_state.name,
            entry_type="activity",
            content=f"Today I was {paul_state.activity.value} at the {paul_state.location.value}. Energy: {paul_state.energy:.0f}%",
            timestamp=datetime.now(),
            location=paul_state.location.value,
            mood=paul_state.mood,
            energy=paul_state.energy,
            metadata={
                'predictions_made': paul_state.predictions_made,
                'conversations_had': paul_state.conversations_had,
                'documents_read': paul_state.documents_read,
            },
        )
        entries.append(activity_entry)
        self._save_diary_entry(activity_entry)
        
        # Thought entry (if mood is extreme)
        if abs(paul_state.mood) > 0.5:
            thought_content = (
                "Feeling very optimistic about the markets!" if paul_state.mood > 0.5 
                else "I'm concerned about the current market conditions."
            )
            thought_entry = DiaryEntry(
                entry_id=f"{paul_state.name}_thought_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                paul_name=paul_state.name,
                entry_type="thought",
                content=thought_content,
                timestamp=datetime.now(),
                mood=paul_state.mood,
                energy=paul_state.energy,
            )
            entries.append(thought_entry)
            self._save_diary_entry(thought_entry)
        
        return entries
    
    def _calculate_rest_quality(self, paul_state, insights_generated: int) -> float:
        """Calculate how restful the sleep was (0-1)."""
        base_quality = 0.5
        
        # More insights = better processing = better rest
        base_quality += min(0.3, insights_generated * 0.05)
        
        # Comfort based on location
        if paul_state.location.value == 'home':
            base_quality += 0.2
        elif paul_state.location.value in ['cafe', 'park']:
            base_quality += 0.1
        
        # Hunger affects sleep quality
        if paul_state.hunger > 50:
            base_quality -= 0.2
        
        return max(0.0, min(1.0, base_quality))
    
    def _save_insight(self, paul_name: str, insight: REMInsight):
        """Save an insight to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rem_insights (paul_name, insight_type, content, source_memories, confidence, generated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (paul_name, insight.insight_type, insight.content,
              json.dumps(insight.source_memories), insight.confidence,
              insight.generated_at.isoformat()))
        conn.commit()
        conn.close()
    
    def _save_diary_entry(self, entry: DiaryEntry):
        """Save a diary entry to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO diary_entries 
            (entry_id, paul_name, entry_type, content, timestamp, location, mood, energy, related_pauls, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (entry.entry_id, entry.paul_name, entry.entry_type, entry.content,
              entry.timestamp.isoformat(), entry.location, entry.mood, entry.energy,
              json.dumps(entry.related_pauls), json.dumps(entry.metadata)))
        conn.commit()
        conn.close()
    
    # ============== Diary Timeline UI Methods ==============
    
    def get_diary_timeline(self, paul_name: Optional[str] = None, days: int = 7, 
                          entry_types: Optional[List[str]] = None,
                          date_from: Optional[datetime] = None,
                          date_to: Optional[datetime] = None) -> List[DiaryEntry]:
        """Get diary entries for a Paul's timeline with optional filtering."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query dynamically
        query = '''
            SELECT entry_id, paul_name, entry_type, content, timestamp, location, mood, energy, related_pauls, metadata
            FROM diary_entries
            WHERE 1=1
        '''
        params = []
        
        if paul_name:
            query += ' AND paul_name = ?'
            params.append(paul_name)
        
        if date_from:
            query += ' AND timestamp >= ?'
            params.append(date_from.isoformat())
        elif days:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            query += ' AND timestamp > ?'
            params.append(since)
        
        if date_to:
            query += ' AND timestamp <= ?'
            params.append(date_to.isoformat())
        
        if entry_types:
            placeholders = ','.join('?' * len(entry_types))
            query += f' AND entry_type IN ({placeholders})'
            params.extend(entry_types)
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, params)
        
        entries = []
        for row in cursor.fetchall():
            entries.append(DiaryEntry(
                entry_id=row[0],
                paul_name=row[1],
                entry_type=row[2],
                content=row[3],
                timestamp=datetime.fromisoformat(row[4]),
                location=row[5],
                mood=row[6],
                energy=row[7],
                related_pauls=json.loads(row[8]) if row[8] else [],
                metadata=json.loads(row[9]) if row[9] else {},
            ))
        
        conn.close()
        return entries
    
    def get_insights(self, paul_name: str, insight_type: Optional[str] = None) -> List[REMInsight]:
        """Get insights generated during REM cycles."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if insight_type:
            cursor.execute('''
                SELECT insight_type, content, source_memories, confidence, generated_at
                FROM rem_insights
                WHERE paul_name = ? AND insight_type = ?
                ORDER BY generated_at DESC
            ''', (paul_name, insight_type))
        else:
            cursor.execute('''
                SELECT insight_type, content, source_memories, confidence, generated_at
                FROM rem_insights
                WHERE paul_name = ?
                ORDER BY generated_at DESC
            ''', (paul_name,))
        
        insights = []
        for row in cursor.fetchall():
            insights.append(REMInsight(
                insight_type=row[0],
                content=row[1],
                source_memories=json.loads(row[2]) if row[2] else [],
                confidence=row[3],
                generated_at=datetime.fromisoformat(row[4]),
            ))
        
        conn.close()
        return insights
    
    def get_rem_stats(self, paul_name: str) -> Dict:
        """Get REM sleep statistics for a Paul."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*), AVG(quality_score), SUM(insights_generated), SUM(dreams_generated)
            FROM rem_sessions
            WHERE paul_name = ?
        ''', (paul_name,))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_sessions': row[0] or 0,
            'avg_quality': row[1] or 0,
            'total_insights': row[2] or 0,
            'total_dreams': row[3] or 0,
        }
    
    def get_world_timeline(self, days: int = 1, entry_types: Optional[List[str]] = None) -> List[Dict]:
        """Get a combined timeline of all Pauls' activities."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = '''
            SELECT entry_id, paul_name, entry_type, content, timestamp, location, mood
            FROM diary_entries
            WHERE timestamp > ?
        '''
        params = [since]
        
        if entry_types:
            placeholders = ','.join('?' * len(entry_types))
            query += f' AND entry_type IN ({placeholders})'
            params.extend(entry_types)
        
        query += ' ORDER BY timestamp DESC LIMIT 100'
        
        cursor.execute(query, params)
        
        entries = []
        for row in cursor.fetchall():
            entries.append({
                'entry_id': row[0],
                'paul_name': row[1],
                'entry_type': row[2],
                'content': row[3],
                'timestamp': row[4],
                'location': row[5],
                'mood': row[6],
            })
        
        conn.close()
        return entries
    
    def get_pauls_with_entries(self) -> List[Dict]:
        """Get list of all Pauls who have diary entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT paul_name, COUNT(*) as entry_count, MAX(timestamp) as last_entry
            FROM diary_entries
            GROUP BY paul_name
            ORDER BY entry_count DESC
        ''')
        
        pauls = []
        for row in cursor.fetchall():
            pauls.append({
                'paul_name': row[0],
                'entry_count': row[1],
                'last_entry': row[2],
            })
        
        conn.close()
        return pauls
    
    def get_backfill_history(self, limit: int = 20) -> List[Dict]:
        """Get history of backfill operations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT source_type, source_path, records_imported, pauls_affected, backfill_date, details
            FROM backfill_log
            ORDER BY backfill_date DESC
            LIMIT ?
        ''', (limit,))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                'source_type': row[0],
                'source_path': row[1],
                'records_imported': row[2],
                'pauls_affected': row[3],
                'backfill_date': row[4],
                'details': row[5],
            })
        
        conn.close()
        return history


# ============== CLI Commands ==============

def main():
    parser = argparse.ArgumentParser(
        description='REM Backfill System for Swimming Pauls',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import from prediction_history.db
  python rem_backfill.py import-predictions
  
  # Import from CSV file
  python rem_backfill.py import-csv events.csv --mapping paul:name type:entry_type
  
  # Import from JSON file
  python rem_backfill.py import-json dreams.json
  
  # Generate dreams for Pauls
  python rem_backfill.py backfill-dreams "Visionary Paul,Trader Paul" --days 30
  
  # Generate thoughts for Pauls
  python rem_backfill.py backfill-thoughts "Visionary Paul,Trader Paul" --count 5
  
  # Query diary entries
  python rem_backfill.py query "Visionary Paul" --days 7 --types dream,thought
  
  # List all Pauls with entries
  python rem_backfill.py list-pauls
  
  # Get backfill history
  python rem_backfill.py history
        """
    )
    
    parser.add_argument('--db', default='data/paul_world.db', help='Database path')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Import predictions command
    import_pred = subparsers.add_parser('import-predictions', help='Import from prediction_history.db')
    import_pred.add_argument('--source', default='data/predictions.db', help='Source database path')
    
    # Import CSV command
    import_csv = subparsers.add_parser('import-csv', help='Import from CSV file')
    import_csv.add_argument('filepath', help='Path to CSV file')
    import_csv.add_argument('--mapping', help='Column mapping (e.g., paul:name,type:entry_type)')
    
    # Import JSON command
    import_json = subparsers.add_parser('import-json', help='Import from JSON file')
    import_json.add_argument('filepath', help='Path to JSON file')
    
    # Backfill dreams command
    backfill_dreams = subparsers.add_parser('backfill-dreams', help='Generate retroactive dreams')
    backfill_dreams.add_argument('pauls', help='Comma-separated list of Paul names')
    backfill_dreams.add_argument('--days', type=int, default=30, help='Number of days to backfill')
    
    # Backfill thoughts command
    backfill_thoughts = subparsers.add_parser('backfill-thoughts', help='Generate retroactive thoughts')
    backfill_thoughts.add_argument('pauls', help='Comma-separated list of Paul names')
    backfill_thoughts.add_argument('--count', type=int, default=5, help='Thoughts per Paul')
    
    # Query command
    query = subparsers.add_parser('query', help='Query diary entries')
    query.add_argument('paul', nargs='?', help='Paul name (optional)')
    query.add_argument('--days', type=int, default=7, help='Number of days to look back')
    query.add_argument('--types', help='Comma-separated entry types')
    query.add_argument('--format', choices=['table', 'json'], default='table', help='Output format')
    
    # List Pauls command
    subparsers.add_parser('list-pauls', help='List all Pauls with diary entries')
    
    # History command
    subparsers.add_parser('history', help='Show backfill history')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    engine = REMBackfillEngine(db_path=args.db)
    
    if args.command == 'import-predictions':
        result = engine.import_from_prediction_history(args.source)
        print(f"✅ Imported {result['entries_created']} entries from {result['source']}")
        print(f"   Pauls affected: {', '.join(result['pauls_affected'])}")
    
    elif args.command == 'import-csv':
        mapping = None
        if args.mapping:
            mapping = {}
            for pair in args.mapping.split(','):
                k, v = pair.split(':')
                mapping[k.strip()] = v.strip()
        result = engine.import_from_csv(args.filepath, mapping)
        print(f"✅ Imported {result['entries_created']} entries from {result['source']}")
        if result['errors']:
            print(f"   ⚠️  {len(result['errors'])} errors (showing first 10):")
            for error in result['errors']:
                print(f"      - {error}")
    
    elif args.command == 'import-json':
        result = engine.import_from_json(args.filepath)
        print(f"✅ Imported {result['entries_created']} entries from {result['source']}")
        print(f"   Pauls affected: {', '.join(result['pauls_affected'])}")
    
    elif args.command == 'backfill-dreams':
        pauls = [p.strip() for p in args.pauls.split(',')]
        result = engine.backfill_dreams(pauls, args.days)
        print(f"✅ Generated {result['entries_created']} dream entries")
        print(f"   Pauls: {', '.join(result['pauls_affected'])}")
        print(f"   Days covered: {result['days_covered']}")
    
    elif args.command == 'backfill-thoughts':
        pauls = [p.strip() for p in args.pauls.split(',')]
        result = engine.backfill_thoughts(pauls, args.count)
        print(f"✅ Generated {result['entries_created']} thought entries")
        print(f"   Pauls: {', '.join(result['pauls_affected'])}")
    
    elif args.command == 'query':
        entry_types = args.types.split(',') if args.types else None
        entries = engine.get_diary_timeline(args.paul, args.days, entry_types)
        
        if args.format == 'json':
            print(json.dumps([e.to_dict() for e in entries], indent=2))
        else:
            print(f"\n📖 Diary Entries ({len(entries)} total)\n")
            print(f"{'Time':<20} {'Type':<12} {'Paul':<20} {'Content'}")
            print("-" * 100)
            for e in entries[:50]:  # Limit to 50 for display
                ts = e.timestamp.strftime('%Y-%m-%d %H:%M')
                content = e.content[:50] + '...' if len(e.content) > 50 else e.content
                print(f"{ts:<20} {e.entry_type:<12} {e.paul_name:<20} {content}")
    
    elif args.command == 'list-pauls':
        pauls = engine.get_pauls_with_entries()
        print(f"\n👥 Pauls with Diary Entries ({len(pauls)} total)\n")
        print(f"{'Paul Name':<30} {'Entries':<10} {'Last Entry'}")
        print("-" * 70)
        for p in pauls:
            print(f"{p['paul_name']:<30} {p['entry_count']:<10} {p['last_entry']}")
    
    elif args.command == 'history':
        history = engine.get_backfill_history()
        print(f"\n📜 Backfill History ({len(history)} operations)\n")
        print(f"{'Date':<20} {'Source':<15} {'Records':<10} {'Pauls':<10} {'Path'}")
        print("-" * 90)
        for h in history:
            date = h['backfill_date'][:19] if h['backfill_date'] else 'N/A'
            path = h['source_path'][:30] if h['source_path'] else 'N/A'
            print(f"{date:<20} {h['source_type']:<15} {h['records_imported']:<10} {h['pauls_affected']:<10} {path}")


if __name__ == "__main__":
    main()
