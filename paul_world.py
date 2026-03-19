"""
Paul's World - Enhanced Persistent Simulation
Swimming Pauls with knowledge, memory, skills, and social dynamics.

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
import random
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
from pathlib import Path
import re

# Import skills system
try:
    from skills import SkillRegistry
    from skill_bridge import get_skill_bridge
    from web_intelligence import WebIntelligence
    SKILLS_AVAILABLE = True
except ImportError:
    SKILLS_AVAILABLE = False
    print("⚠️  Skills system not available")


class Activity(Enum):
    """What a Paul can be doing."""
    IDLE = "idle"
    RESEARCHING = "researching"
    DEBATING = "debating"
    RESTING = "resting"
    SOCIALIZING = "socializing"
    TRADING = "trading"
    ANALYZING = "analyzing"
    TEACHING = "teaching"
    LEARNING = "learning"


class Location(Enum):
    """Virtual world locations - Expanded City Edition."""
    # Original locations
    MARKET_FLOOR = "market_floor"
    RESEARCH_LAB = "research_lab"
    CAFE = "cafe"
    HOME = "home"
    CONFERENCE_ROOM = "conference_room"
    PARK = "park"
    
    # New city locations
    TOWN_HALL = "town_hall"
    BAR = "bar"
    CARD_ROOM = "card_room"
    GYM = "gym"
    LIBRARY = "library"
    RESTAURANT = "restaurant"
    THEATER = "theater"
    HOSPITAL = "hospital"
    POLICE_STATION = "police_station"
    FIRE_STATION = "fire_station"
    SCHOOL = "school"
    UNIVERSITY = "university"
    MUSEUM = "museum"
    ART_GALLERY = "art_gallery"
    NIGHTCLUB = "nightclub"
    COFFEE_SHOP = "coffee_shop"
    BOOKSTORE = "bookstore"
    SHOPPING_MALL = "shopping_mall"
    BEACH = "beach"
    MOUNTAIN = "mountain"
    AIRPORT = "airport"
    TRAIN_STATION = "train_station"
    PORT = "port"
    CONSTRUCTION_SITE = "construction_site"
    FACTORY = "factory"
    FARM = "farm"
    VINEYARD = "vineyard"
    BREWERY = "brewery"
    
    # Digital/Social locations
    DISCORD = "discord"
    TWITTER = "twitter"
    TELEGRAM = "telegram"
    REDDIT = "reddit"
    GITHUB = "github"
    YOUTUBE = "youtube"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"
    
    # Financial locations
    BANK = "bank"
    INVESTMENT_FIRM = "investment_firm"
    INSURANCE_OFFICE = "insurance_office"
    REAL_ESTATE_OFFICE = "real_estate_office"
    LAW_OFFICE = "law_office"
    ACCOUNTING_FIRM = "accounting_firm"


@dataclass
class KnowledgeItem:
    """Something a Paul knows."""
    topic: str
    content: str
    source: str  # "document", "web", "conversation", "prediction"
    confidence: float = 0.5
    learned_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    
    def to_dict(self):
        return {
            'topic': self.topic,
            'content': self.content[:200],  # Truncate for storage
            'source': self.source,
            'confidence': self.confidence,
            'learned_at': self.learned_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'access_count': self.access_count,
        }


@dataclass
class Memory:
    """A Paul's memory of an event."""
    event_type: str  # "prediction", "conversation", "lesson", "market_event"
    description: str
    timestamp: datetime
    sentiment: float = 0.0  # -1 to 1
    accuracy: Optional[float] = None  # For predictions
    
    def to_dict(self):
        return {
            'event_type': self.event_type,
            'description': self.description[:200],
            'timestamp': self.timestamp.isoformat(),
            'sentiment': self.sentiment,
            'accuracy': self.accuracy,
        }


@dataclass
class Relationship:
    """Relationship between two Pauls."""
    trust: float = 0.5
    respect: float = 0.5
    interactions: int = 0
    last_interaction: Optional[datetime] = None
    shared_knowledge: List[str] = field(default_factory=list)  # Topics discussed
    
    def to_dict(self):
        return {
            'trust': self.trust,
            'respect': self.respect,
            'interactions': self.interactions,
            'last_interaction': self.last_interaction.isoformat() if self.last_interaction else None,
            'shared_knowledge': self.shared_knowledge,
        }


@dataclass
class PaulState:
    """Current state of a Paul in the world."""
    # Identity
    name: str
    emoji: str
    specialty: str
    trading_style: str = "swing_trader"  # From persona_factory
    risk_profile: str = "moderate"
    
    # Location & Activity
    location: Location = Location.HOME
    activity: Activity = Activity.IDLE
    
    # Needs (0-100)
    energy: float = 100.0
    hunger: float = 0.0  # New: needs to eat
    knowledge_freshness: float = 50.0  # How up-to-date their knowledge is
    social: float = 50.0
    mood: float = 0.0  # -1 (bad) to 1 (good)
    
    # Knowledge & Memory
    knowledge: List[KnowledgeItem] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)
    max_memories: int = 50  # Pauls forget old memories
    
    # Skills this Paul has access to
    skills: List[str] = field(default_factory=list)
    
    # Reputation
    accuracy_score: float = 0.5
    influence_score: float = 0.5
    reputation: float = 0.5
    teaching_ability: float = 0.5
    learning_speed: float = 0.5
    
    # Personality (evolves)
    risk_tolerance: float = 0.5
    optimism: float = 0.5
    curiosity: float = 0.5
    
    # State tracking
    last_active: datetime = field(default_factory=datetime.now)
    predictions_made: int = 0
    predictions_correct: int = 0
    conversations_had: int = 0
    documents_read: int = 0
    
    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'emoji': self.emoji,
            'specialty': self.specialty,
            'trading_style': self.trading_style,
            'risk_profile': self.risk_profile,
            'location': self.location.value,
            'activity': self.activity.value,
            'energy': self.energy,
            'hunger': self.hunger,
            'knowledge_freshness': self.knowledge_freshness,
            'social': self.social,
            'mood': self.mood,
            'knowledge_count': len(self.knowledge),
            'memories_count': len(self.memories),
            'skills': self.skills,
            'accuracy_score': self.accuracy_score,
            'influence_score': self.influence_score,
            'reputation': self.reputation,
            'risk_tolerance': self.risk_tolerance,
            'optimism': self.optimism,
            'curiosity': self.curiosity,
            'last_active': self.last_active.isoformat(),
            'predictions_made': self.predictions_made,
            'predictions_correct': self.predictions_correct,
            'conversations_had': self.conversations_had,
            'documents_read': self.documents_read,
        }
    
    def add_knowledge(self, topic: str, content: str, source: str, confidence: float = 0.5):
        """Add knowledge, preventing duplicates."""
        # Check if similar knowledge exists
        for k in self.knowledge:
            if k.topic == topic and k.source == source:
                # Update confidence if new info is more confident
                k.confidence = max(k.confidence, confidence)
                k.last_accessed = datetime.now()
                k.access_count += 1
                return
        
        # Add new knowledge
        self.knowledge.append(KnowledgeItem(
            topic=topic,
            content=content,
            source=source,
            confidence=confidence,
        ))
        
        # Limit knowledge size
        if len(self.knowledge) > 100:
            # Remove least accessed knowledge
            self.knowledge.sort(key=lambda k: (k.access_count, k.last_accessed))
            self.knowledge = self.knowledge[-100:]
    
    def get_knowledge_on_topic(self, topic: str) -> List[KnowledgeItem]:
        """Get knowledge related to a topic."""
        relevant = []
        topic_lower = topic.lower()
        for k in self.knowledge:
            if topic_lower in k.topic.lower() or topic_lower in k.content.lower():
                k.last_accessed = datetime.now()
                k.access_count += 1
                relevant.append(k)
        return sorted(relevant, key=lambda k: k.confidence, reverse=True)
    
    def add_memory(self, event_type: str, description: str, sentiment: float = 0.0, accuracy: Optional[float] = None):
        """Add a memory, forgetting old ones if needed."""
        memory = Memory(
            event_type=event_type,
            description=description,
            timestamp=datetime.now(),
            sentiment=sentiment,
            accuracy=accuracy,
        )
        self.memories.insert(0, memory)  # Newest first
        
        # Forget old memories
        if len(self.memories) > self.max_memories:
            self.memories = self.memories[:self.max_memories]
    
    def get_recent_memories(self, event_type: Optional[str] = None, limit: int = 5) -> List[Memory]:
        """Get recent memories, optionally filtered by type."""
        if event_type:
            return [m for m in self.memories if m.event_type == event_type][:limit]
        return self.memories[:limit]
    
    def update_mood(self):
        """Update mood based on current state."""
        # Low energy = bad mood
        if self.energy < 30:
            self.mood -= 0.2
        elif self.energy > 70:
            self.mood += 0.1
        
        # Hungry = bad mood
        if self.hunger > 70:
            self.mood -= 0.3
        
        # Socially fulfilled = good mood
        if self.social > 60:
            self.mood += 0.1
        elif self.social < 20:
            self.mood -= 0.1
        
        # Clamp mood
        self.mood = max(-1.0, min(1.0, self.mood))


@dataclass
class WorldEvent:
    """Something that happens in the world."""
    timestamp: datetime
    event_type: str
    data: dict
    severity: float = 0.5
    affected_pauls: List[str] = field(default_factory=list)


class PaulWorld:
    """
    Enhanced Paul's World with knowledge, memory, skills, and social dynamics.
    """
    
    def __init__(self, db_path: str = "data/paul_world.db"):
        self.db_path = Path(db_path)
        self.knowledge_dir = Path("data/knowledge")
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        self.pauls: Dict[str, PaulState] = {}
        self.relationships: Dict[Tuple[str, str], Relationship] = {}
        self.events: List[WorldEvent] = []
        self.world_time: datetime = datetime.now()
        self.tick_count: int = 0
        self.last_knowledge_scan: datetime = datetime.min
        
        self.time_speed: float = 1.0
        self.active: bool = False
        
        # Skills system
        self.skill_registry = None
        self.web_intel = None
        if SKILLS_AVAILABLE:
            self.skill_registry = SkillRegistry()
            self.web_intel = WebIntelligence()
    
    async def initialize(self):
        """Initialize or load existing world."""
        self._init_db()
        
        if not await self._load_world():
            await self._create_starting_world()
        
        # Scan for knowledge documents
        await self._scan_knowledge_directory()
    
    def _init_db(self):
        """Initialize SQLite database with new schema."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Paul states (enhanced)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_states (
                name TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Paul knowledge
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paul_name TEXT NOT NULL,
                topic TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL,
                learned_at TEXT,
                FOREIGN KEY (paul_name) REFERENCES paul_states(name)
            )
        ''')
        
        # Paul memories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paul_name TEXT NOT NULL,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                timestamp TEXT,
                sentiment REAL,
                accuracy REAL,
                FOREIGN KEY (paul_name) REFERENCES paul_states(name)
            )
        ''')
        
        # Relationships
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                paul_a TEXT NOT NULL,
                paul_b TEXT NOT NULL,
                data TEXT NOT NULL,
                PRIMARY KEY (paul_a, paul_b)
            )
        ''')
        
        # World events
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS world_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                data TEXT NOT NULL,
                severity REAL,
                affected_pauls TEXT
            )
        ''')
        
        # World state
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS world_state (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def _scan_knowledge_directory(self):
        """Scan for new documents and have Pauls read them."""
        if not self.knowledge_dir.exists():
            return
        
        # Only scan every 6 hours
        if (datetime.now() - self.last_knowledge_scan).total_seconds() < 21600:
            return
        
        self.last_knowledge_scan = datetime.now()
        
        # Find all documents
        documents = list(self.knowledge_dir.glob("*.txt")) + \
                   list(self.knowledge_dir.glob("*.md")) + \
                   list(self.knowledge_dir.glob("*.pdf"))
        
        if not documents:
            return
        
        print(f"📚 Found {len(documents)} documents in knowledge directory")
        
        # Have Research Lab Pauls read documents
        researchers = [p for p in self.pauls.values() 
                      if p.location == Location.RESEARCH_LAB or "Professor" in p.name]
        
        for doc_path in documents:
            try:
                content = self._read_document(doc_path)
                if not content:
                    continue
                
                # Extract topic from filename
                topic = doc_path.stem.replace("_", " ").title()
                
                # Have researchers absorb knowledge
                for paul in researchers[:3]:  # Top 3 researchers
                    paul.add_knowledge(topic, content[:1000], f"document:{doc_path.name}")
                    paul.documents_read += 1
                    paul.add_memory("learning", f"Read document on {topic}", sentiment=0.3)
                
                print(f"   ✓ {topic} → {len(researchers)} researchers")
                
            except Exception as e:
                print(f"   ✗ Error reading {doc_path}: {e}")
    
    def _read_document(self, path: Path) -> str:
        """Read content from a document."""
        if path.suffix == '.pdf':
            try:
                import PyPDF2
                with open(path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    return "\n".join(page.extract_text() for page in reader.pages)
            except:
                return ""
        else:
            return path.read_text(encoding='utf-8', errors='ignore')
    
    async def _create_starting_world(self):
        """Create a new world with dynamic Paul count."""
        from persona_factory import generate_swimming_pauls_pool, TradingStyle, RiskProfile, SpecialtyDomain
        
        limits = self._get_system_limits()
        target_pauls = limits["recommended"]
        
        print(f"🌍 Creating Enhanced Paul's World with {target_pauls} Pauls...")
        
        # Core archetypes with full personas
        core_configs = [
            {
                "name": "Visionary Paul", "emoji": "🔮", 
                "specialty": "Disruptive Innovation",
                "trading_style": "POSITION_TRADER", "risk": "AGGRESSIVE",
                "skills": ["news_summarizer", "market_analysis"],
                "curiosity": 0.9, "optimism": 0.8
            },
            {
                "name": "Professor Paul", "emoji": "👨‍🏫",
                "specialty": "Macro Research", 
                "trading_style": "SYSTEMATIC", "risk": "MODERATE",
                "skills": ["yahoo_finance", "news_summarizer", "web_search"],
                "curiosity": 0.9, "teaching_ability": 0.9
            },
            {
                "name": "Trader Paul", "emoji": "📈",
                "specialty": "Market Timing",
                "trading_style": "MOMENTUM", "risk": "AGGRESSIVE", 
                "skills": ["crypto_price", "yahoo_finance"],
                "optimism": 0.7
            },
            {
                "name": "Skeptic Paul", "emoji": "🤨",
                "specialty": "Risk Assessment",
                "trading_style": "CONTRARIAN", "risk": "CONSERVATIVE",
                "skills": ["market_analysis", "news_summarizer"],
                "optimism": 0.3
            },
            {
                "name": "Whale Paul", "emoji": "🐋",
                "specialty": "Institutional Flow",
                "trading_style": "STRATEGIC", "risk": "CONSERVATIVE",
                "skills": ["crypto_price", "base_blockchain", "market_analysis"],
                "influence_score": 0.9
            },
            {
                "name": "Degen Paul", "emoji": "🎰",
                "specialty": "High Risk",
                "trading_style": "SCALPER", "risk": "DEGEN",
                "skills": ["crypto_price", "polymarket"],
                "risk_tolerance": 0.95, "optimism": 0.9
            },
            {
                "name": "Quant Paul", "emoji": "📊",
                "specialty": "Quantitative Analysis",
                "trading_style": "ALGORITHMIC", "risk": "MODERATE",
                "skills": ["yahoo_finance", "crypto_price", "market_analysis"],
                "learning_speed": 0.9
            },
            {
                "name": "Contrarian Paul", "emoji": "🐻",
                "specialty": "Contrarian Views",
                "trading_style": "CONTRARIAN", "risk": "MODERATE",
                "skills": ["news_summarizer", "market_analysis"],
                "optimism": 0.3
            },
        ]
        
        for config in core_configs:
            self.pauls[config["name"]] = PaulState(
                name=config["name"],
                emoji=config["emoji"],
                specialty=config["specialty"],
                trading_style=config.get("trading_style", "SWING_TRADER"),
                risk_profile=config.get("risk", "MODERATE"),
                skills=config.get("skills", []),
                curiosity=config.get("curiosity", 0.5),
                optimism=config.get("optimism", 0.5),
                risk_tolerance=config.get("risk_tolerance", 0.5),
                teaching_ability=config.get("teaching_ability", 0.5),
                learning_speed=config.get("learning_speed", 0.5),
                influence_score=config.get("influence_score", 0.5),
                location=random.choice(list(Location)),
            )
        
        # Generate additional Pauls with full personas
        remaining = target_pauls - len(core_configs)
        if remaining > 0:
            try:
                extra_pauls = generate_swimming_pauls_pool(n=remaining)
                for i, paul_data in enumerate(extra_pauls):
                    name = paul_data.get('name', f'Paul #{i+1}')
                    # Assign random skills based on specialty
                    skills = self._assign_skills_for_specialty(paul_data.get('specialty', 'General'))
                    
                    self.pauls[name] = PaulState(
                        name=name,
                        emoji=paul_data.get('emoji', '🦷'),
                        specialty=paul_data.get('specialty', 'Generalist'),
                        trading_style=paul_data.get('trading_style', 'SWING_TRADER'),
                        risk_profile=paul_data.get('risk_profile', 'MODERATE'),
                        skills=skills,
                        location=random.choice(list(Location)),
                    )
            except Exception as e:
                print(f"⚠️  Could not generate extra Pauls: {e}")
        
        # Initialize relationships
        paul_names = list(self.pauls.keys())
        for i, name_a in enumerate(paul_names):
            for name_b in paul_names[i+1:]:
                if random.random() < 0.3:
                    self.relationships[(name_a, name_b)] = Relationship(
                        trust=random.uniform(0.3, 0.7),
                        respect=random.uniform(0.3, 0.7),
                    )
        
        print(f"✅ World created with {len(self.pauls)} Pauls!")
        await self._save_world()
    
    def _assign_skills_for_specialty(self, specialty: str) -> List[str]:
        """Assign appropriate skills based on specialty."""
        skill_map = {
            "DeFi": ["crypto_price", "base_blockchain", "web_search"],
            "NFT": ["crypto_price", "web_search", "news_summarizer"],
            "Macro": ["yahoo_finance", "news_summarizer", "web_search"],
            "Trading": ["crypto_price", "yahoo_finance", "polymarket"],
            "Tech": ["web_search", "news_summarizer"],
        }
        
        for key, skills in skill_map.items():
            if key.lower() in specialty.lower():
                return skills
        
        return ["web_search", "news_summarizer"]  # Default
    
    def _get_system_limits(self):
        """Detect system capabilities."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            max_pauls = int(available_gb / 0.01)
            
            if max_pauls > 10000:
                max_pauls = 10000
            elif max_pauls < 10:
                max_pauls = 10
                
            return {
                "max_pauls": max_pauls,
                "recommended": min(max_pauls, 100 if max_pauls >= 100 else max_pauls),
                "available_gb": round(available_gb, 1),
                "tier": "small" if max_pauls < 100 else "medium" if max_pauls < 500 else "large"
            }
        except:
            return {"max_pauls": 50, "recommended": 20, "available_gb": "unknown", "tier": "unknown"}
    
    async def _load_world(self) -> bool:
        """Load world from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, data FROM paul_states')
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return False
        
        for name, data_json in rows:
            data = json.loads(data_json)
            paul = PaulState(
                name=data['name'],
                emoji=data['emoji'],
                specialty=data['specialty'],
                trading_style=data.get('trading_style', 'SWING_TRADER'),
                risk_profile=data.get('risk_profile', 'MODERATE'),
                skills=data.get('skills', []),
                location=Location(data['location']),
                activity=Activity(data['activity']),
                energy=data['energy'],
                hunger=data.get('hunger', 0),
                knowledge_freshness=data.get('knowledge_freshness', 50),
                social=data['social'],
                mood=data.get('mood', 0),
                accuracy_score=data['accuracy_score'],
                influence_score=data['influence_score'],
                reputation=data['reputation'],
                curiosity=data.get('curiosity', 0.5),
                risk_tolerance=data['risk_tolerance'],
                optimism=data['optimism'],
                last_active=datetime.fromisoformat(data['last_active']),
                predictions_made=data['predictions_made'],
                predictions_correct=data['predictions_correct'],
                conversations_had=data.get('conversations_had', 0),
                documents_read=data.get('documents_read', 0),
            )
            
            # Load knowledge
            cursor.execute('SELECT topic, content, source, confidence FROM paul_knowledge WHERE paul_name = ?', (name,))
            for row in cursor.fetchall():
                paul.add_knowledge(row[0], row[1], row[2], row[3])
            
            # Load memories
            cursor.execute('SELECT event_type, description, timestamp, sentiment, accuracy FROM paul_memories WHERE paul_name = ? ORDER BY timestamp DESC LIMIT 50', (name,))
            for row in cursor.fetchall():
                paul.memories.append(Memory(
                    event_type=row[0],
                    description=row[1],
                    timestamp=datetime.fromisoformat(row[2]),
                    sentiment=row[3],
                    accuracy=row[4],
                ))
            
            self.pauls[name] = paul
        
        # Load relationships
        cursor.execute('SELECT paul_a, paul_b, data FROM relationships')
        for paul_a, paul_b, data_json in cursor.fetchall():
            data = json.loads(data_json)
            self.relationships[(paul_a, paul_b)] = Relationship(
                trust=data['trust'],
                respect=data['respect'],
                interactions=data['interactions'],
                last_interaction=datetime.fromisoformat(data['last_interaction']) if data['last_interaction'] else None,
                shared_knowledge=data.get('shared_knowledge', []),
            )
        
        cursor.execute("SELECT value FROM world_state WHERE key = 'world_time'")
        row = cursor.fetchone()
        if row:
            self.world_time = datetime.fromisoformat(row[0])
        
        conn.close()
        return True
    
    async def _save_world(self):
        """Save world state."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for name, paul in self.pauls.items():
            cursor.execute('''
                INSERT OR REPLACE INTO paul_states (name, data, updated_at)
                VALUES (?, ?, ?)
            ''', (name, json.dumps(paul.to_dict()), datetime.now().isoformat()))
            
            # Save knowledge
            cursor.execute('DELETE FROM paul_knowledge WHERE paul_name = ?', (name,))
            for k in paul.knowledge:
                cursor.execute('''
                    INSERT INTO paul_knowledge (paul_name, topic, content, source, confidence, learned_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, k.topic, k.content, k.source, k.confidence, k.learned_at.isoformat()))
            
            # Save memories
            cursor.execute('DELETE FROM paul_memories WHERE paul_name = ?', (name,))
            for m in paul.memories:
                cursor.execute('''
                    INSERT INTO paul_memories (paul_name, event_type, description, timestamp, sentiment, accuracy)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, m.event_type, m.description, m.timestamp.isoformat(), m.sentiment, m.accuracy))
        
        cursor.execute('DELETE FROM relationships')
        for (paul_a, paul_b), rel in self.relationships.items():
            cursor.execute('''
                INSERT INTO relationships (paul_a, paul_b, data)
                VALUES (?, ?, ?)
            ''', (paul_a, paul_b, json.dumps(rel.to_dict())))
        
        cursor.execute('INSERT OR REPLACE INTO world_state (key, value) VALUES ("world_time", ?)', 
                      (self.world_time.isoformat(),))
        
        conn.commit()
        conn.close()
    
    async def tick(self):
        """Advance world by one hour."""
        self.tick_count += 1
        self.world_time += timedelta(hours=1)
        
        # Update all Pauls
        for name, paul in self.pauls.items():
            await self._update_paul(paul)
        
        # Process interactions
        await self._process_interactions()
        
        # Scan for new knowledge
        if self.tick_count % 6 == 0:
            await self._scan_knowledge_directory()
        
        # Save periodically
        if self.tick_count % 12 == 0:
            await self._save_world()
    
    async def _update_paul(self, paul: PaulState):
        """Update a single Paul for one hour."""
        # Basic needs
        paul.energy -= 5 if paul.activity not in [Activity.RESTING, Activity.IDLE] else 2
        paul.hunger += 3
        paul.knowledge_freshness -= 1  # Knowledge decays
        paul.social -= 2 if paul.activity != Activity.SOCIALIZING else 0
        
        # Update mood
        paul.update_mood()
        
        # Decide next activity
        if paul.energy < 20 or paul.hunger > 80:
            paul.activity = Activity.RESTING
            paul.location = Location.HOME
            paul.energy = min(100, paul.energy + 20)
            paul.hunger = max(0, paul.hunger - 30)
        elif paul.social < 20:
            paul.activity = Activity.SOCIALIZING
            paul.location = random.choice([Location.CAFE, Location.PARK])
        elif paul.knowledge_freshness < 30 or paul.curiosity > 0.7:
            paul.activity = Activity.RESEARCHING
            paul.location = Location.RESEARCH_LAB
        elif random.random() < 0.1 and paul.teaching_ability > 0.6:
            paul.activity = Activity.TEACHING
            paul.location = Location.CAFE
        else:
            # Based on specialty
            if "Trader" in paul.specialty:
                paul.activity = Activity.TRADING
                paul.location = Location.MARKET_FLOOR
            elif "Professor" in paul.specialty or paul.documents_read > 10:
                paul.activity = Activity.ANALYZING
                paul.location = Location.CONFERENCE_ROOM
            else:
                paul.activity = Activity.IDLE
        
        paul.last_active = self.world_time
    
    async def _process_interactions(self):
        """Process Paul interactions with teaching/learning."""
        location_groups = {}
        for name, paul in self.pauls.items():
            if paul.location not in location_groups:
                location_groups[paul.location] = []
            location_groups[paul.location].append(name)
        
        for location, names in location_groups.items():
            if len(names) < 2:
                continue
            
            random.shuffle(names)
            for i in range(0, min(len(names) - 1, 6), 2):  # Max 3 interactions per location
                name_a, name_b = names[i], names[i + 1]
                await self._interact(name_a, name_b)
    
    async def _interact(self, name_a: str, name_b: str):
        """Two Pauls interact with potential knowledge transfer."""
        paul_a = self.pauls[name_a]
        paul_b = self.pauls[name_b]
        
        key = tuple(sorted([name_a, name_b]))
        if key not in self.relationships:
            self.relationships[key] = Relationship()
        
        rel = self.relationships[key]
        
        # Knowledge transfer if teaching
        if paul_a.activity == Activity.TEACHING and paul_b.activity == Activity.LEARNING:
            if paul_a.knowledge and paul_b.learning_speed > 0.3:
                # Transfer random knowledge item
                knowledge = random.choice(paul_a.knowledge)
                paul_b.add_knowledge(knowledge.topic, knowledge.content, f"learned_from:{name_a}", 
                                   confidence=knowledge.confidence * paul_a.teaching_ability)
                paul_b.add_memory("lesson", f"Learned about {knowledge.topic} from {name_a}", sentiment=0.4)
                paul_a.add_memory("teaching", f"Taught {name_b} about {knowledge.topic}", sentiment=0.3)
                rel.shared_knowledge.append(knowledge.topic)
        
        # Regular social interaction
        if paul_a.activity == Activity.SOCIALIZING and paul_b.activity == Activity.SOCIALIZING:
            # Share recent memories
            if paul_a.memories and random.random() < 0.3:
                memory = random.choice(paul_a.memories[:5])
                paul_b.add_memory("gossip", f"Heard from {name_a}: {memory.description}", 
                                sentiment=memory.sentiment * 0.5)
        
        # Update relationship
        if paul_a.accuracy_score > 0.6 and paul_b.accuracy_score > 0.6:
            rel.respect = min(1.0, rel.respect + 0.02)
        rel.interactions += 1
        rel.last_interaction = self.world_time
        
        # Social satisfaction
        paul_a.social = min(100, paul_a.social + 15)
        paul_b.social = min(100, paul_b.social + 15)
    
    async def ask_pauls(self, question: str, context: Optional[Dict] = None) -> Dict:
        """
        Ask the world's Pauls a question.
        Returns enriched response with reasoning, memories, and view links.
        """
        from chat_interface import ChatInterface
        
        responses = []
        consensus_votes = {"BULLISH": 0, "BEARISH": 0, "NEUTRAL": 0}
        
        # Determine relevant topics
        topics = self._extract_topics(question)
        
        for name, paul in self.pauls.items():
            if paul.energy < 10:  # Too tired to respond
                continue
            
            # Get relevant knowledge
            relevant_knowledge = []
            for topic in topics:
                relevant_knowledge.extend(paul.get_knowledge_on_topic(topic))
            
            # Get relevant memories
            relevant_memories = [m for m in paul.memories 
                               if any(t in m.description.lower() for t in topics)]
            
            # Generate response based on Paul's state
            sentiment, confidence, reasoning = self._generate_response(
                paul, question, relevant_knowledge, relevant_memories, context
            )
            
            consensus_votes[sentiment] += 1
            
            # Use skills if available
            skill_data = {}
            if SKILLS_AVAILABLE and paul.skills and random.random() < 0.3:
                skill_data = await self._use_skills(paul, question)
            
            responses.append({
                "paul_name": name,
                "emoji": paul.emoji,
                "specialty": paul.specialty,
                "location": paul.location.value,
                "activity": paul.activity.value,
                "sentiment": sentiment,
                "confidence": confidence,
                "reasoning": reasoning,
                "energy": paul.energy,
                "mood": paul.mood,
                "relevant_knowledge": [k.topic for k in relevant_knowledge[:3]],
                "recent_memories": [m.description[:50] for m in relevant_memories[:2]],
                "skill_data": skill_data,
            })
            
            # Record prediction
            paul.predictions_made += 1
            paul.add_memory("prediction", f"Predicted {sentiment} on: {question[:50]}...", 
                          sentiment=0.1 if sentiment == "NEUTRAL" else (0.5 if sentiment == "BULLISH" else -0.5))
            paul.energy -= 5  # Predictions cost energy
        
        # Calculate consensus
        total = sum(consensus_votes.values())
        if total > 0:
            max_vote = max(consensus_votes, key=consensus_votes.get)
            consensus_confidence = consensus_votes[max_vote] / total
        else:
            max_vote = "NEUTRAL"
            consensus_confidence = 0.5
        
        # Build result
        result = {
            "question": question,
            "consensus": {
                "direction": max_vote,
                "confidence": round(consensus_confidence, 2),
                "vote_breakdown": consensus_votes,
            },
            "pauls_count": len(responses),
            "world_time": self.world_time.isoformat(),
            "responses": responses,
        }
        
        # Save result for viewing
        chat = ChatInterface()
        result_id = chat.save_prediction_result(result)
        result["result_id"] = result_id
        result["view_urls"] = {
            "explorer": f"http://localhost:3005/explorer.html?id={result_id}",
            "visualize": f"http://localhost:3005/visualize.html?id={result_id}",
            "debate": f"http://localhost:3005/debate_network.html?id={result_id}",
        }
        
        return result
    
    def _extract_topics(self, question: str) -> List[str]:
        """Extract relevant topics from question."""
        # Simple keyword extraction
        keywords = []
        question_lower = question.lower()
        
        topic_map = {
            "btc": ["bitcoin", "btc"],
            "eth": ["ethereum", "eth"],
            "ai": ["ai", "artificial intelligence", "ml"],
            "market": ["market", "price", "trading"],
            "regulation": ["regulation", "sec", "law"],
            "defi": ["defi", "yield", "staking"],
            "nft": ["nft", "collectible"],
        }
        
        for topic, variants in topic_map.items():
            if any(v in question_lower for v in variants):
                keywords.append(topic)
        
        return keywords if keywords else ["general"]
    
    def _generate_response(self, paul: PaulState, question: str, 
                          knowledge: List[KnowledgeItem], 
                          memories: List[Memory],
                          context: Optional[Dict]) -> Tuple[str, float, str]:
        """Generate dynamic response based on Paul's state and knowledge."""
        
        # Base sentiment from personality
        base_optimism = paul.optimism
        
        # Adjust for mood
        base_optimism += paul.mood * 0.3
        
        # Adjust for knowledge confidence
        if knowledge:
            avg_confidence = sum(k.confidence for k in knowledge) / len(knowledge)
            base_optimism += (avg_confidence - 0.5) * 0.2
        
        # Adjust for recent prediction accuracy
        if paul.predictions_made > 0:
            accuracy = paul.predictions_correct / paul.predictions_made
            base_optimism += (accuracy - 0.5) * 0.1
        
        # Determine sentiment
        if base_optimism > 0.6:
            sentiment = "BULLISH"
        elif base_optimism < 0.4:
            sentiment = "BEARISH"
        else:
            sentiment = "NEUTRAL"
        
        # Calculate confidence
        confidence = paul.accuracy_score + (paul.knowledge_freshness / 200)
        if paul.energy < 30:
            confidence *= 0.7  # Tired Pauls are less confident
        if paul.mood < -0.5:
            confidence *= 0.8  # Bad mood reduces confidence
        
        confidence = min(0.95, confidence)
        
        # Generate reasoning
        reasoning_parts = []
        
        # Add knowledge-based reasoning
        if knowledge:
            top_k = knowledge[0]
            reasoning_parts.append(f"Based on my research on {top_k.topic}: {top_k.content[:80]}...")
        
        # Add memory-based reasoning
        if memories:
            recent = memories[0]
            reasoning_parts.append(f"I recall {recent.description[:60]}...")
        
        # Add specialty-based reasoning
        specialty_reasons = {
            "Visionary": "Looking at the long-term trajectory...",
            "Professor": "Historical patterns suggest...",
            "Trader": "Technical indicators show...",
            "Skeptic": "However, considering the risks...",
            "Whale": "Institutional positioning indicates...",
            "Degen": "The vibes are...",
            "Quant": "My models project...",
            "Contrarian": "Going against consensus...",
        }
        
        for key, template in specialty_reasons.items():
            if key in paul.specialty or key in paul.name:
                reasoning_parts.append(template)
                break
        
        # Add state-based reasoning
        if paul.energy < 30:
            reasoning_parts.append("(I'm quite tired, so take this with caution...)")
        if paul.mood > 0.5:
            reasoning_parts.append("I'm feeling optimistic about this!")
        elif paul.mood < -0.5:
            reasoning_parts.append("I'm concerned about the outlook.")
        
        reasoning = " ".join(reasoning_parts) if reasoning_parts else "Based on my analysis..."
        
        return sentiment, confidence, reasoning
    
    async def _use_skills(self, paul: PaulState, question: str) -> Dict:
        """Have Paul use their skills to gather data."""
        results = {}
        
        for skill_name in paul.skills[:2]:  # Use up to 2 skills
            try:
                if skill_name == "crypto_price" and self.web_intel:
                    # Extract coin from question
                    coin = "bitcoin"  # Default
                    if "eth" in question.lower():
                        coin = "ethereum"
                    results[skill_name] = await self.web_intel.get_crypto_price(coin)
                    
                elif skill_name == "yahoo_finance" and self.web_intel:
                    results[skill_name] = await self.web_intel.get_stock_data("SPY")
                    
                elif skill_name == "news_summarizer" and self.web_intel:
                    topic = self._extract_topics(question)[0] if self._extract_topics(question) else "crypto"
                    results[skill_name] = await self.web_intel.get_news_summary(topic)
                    
            except Exception as e:
                results[skill_name] = {"error": str(e)}
        
        return results
    
    async def run_simulation(self):
        """Run continuous simulation."""
        self.active = True
        print(f"🌍 Paul's World simulation running...")
        print(f"   {len(self.pauls)} Pauls living their lives")
        print(f"   Press Ctrl+C to stop\n")
        
        while self.active:
            await self.tick()
            
            # Print status every 24 hours
            if self.tick_count % 24 == 0:
                await self._print_daily_summary()
            
            await asyncio.sleep(1)  # 1 second = 1 hour for testing
    
    async def _print_daily_summary(self):
        """Print daily world summary."""
        print(f"\n📅 Day {self.tick_count // 24} in Paul's World ({self.world_time.strftime('%Y-%m-%d')})")
        
        # Location breakdown
        locations = {}
        for paul in self.pauls.values():
            loc = paul.location.value
            if loc not in locations:
                locations[loc] = []
            locations[loc].append(paul.name)
        
        for loc, names in locations.items():
            print(f"   {loc}: {len(names)} Pauls")
        
        # Most active Paul
        most_active = max(self.pauls.values(), key=lambda p: p.predictions_made)
        print(f"   Most active: {most_active.name} ({most_active.predictions_made} predictions)")
        
        # Average mood
        avg_mood = sum(p.mood for p in self.pauls.values()) / len(self.pauls)
        mood_emoji = "😊" if avg_mood > 0.2 else "😐" if avg_mood > -0.2 else "😔"
        print(f"   Average mood: {mood_emoji} ({avg_mood:.2f})")
        print()
    
    def stop_simulation(self):
        """Stop simulation."""
        self.active = False


# CLI
async def main():
    import sys
    
    world = PaulWorld()
    await world.initialize()
    
    if len(sys.argv) < 2:
        print("Paul's World Commands:")
        print("  status      - Show world status")
        print("  run         - Start simulation")
        print("  ask 'Q'     - Ask the world a question")
        print("  export      - Export world state")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "status":
        print(f"\n🌍 Paul's World Status")
        print(f"Time: {world.world_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"Ticks: {world.tick_count}")
        print(f"Pauls: {len(world.pauls)}")
        
        # Show locations
        locations = {}
        for name, paul in world.pauls.items():
            loc = paul.location.value
            if loc not in locations:
                locations[loc] = []
            locations[loc].append(f"{paul.emoji} {name}")
        
        print(f"\n📍 Locations:")
        for loc, names in locations.items():
            print(f"  {loc}: {', '.join(names[:5])}{'...' if len(names) > 5 else ''}")
        
        # Show sample Paul states
        print(f"\n👥 Sample Pauls:")
        for paul in list(world.pauls.values())[:3]:
            print(f"  {paul.emoji} {paul.name}:")
            print(f"     Energy: {paul.energy:.0f}% | Mood: {paul.mood:+.1f} | Knowledge: {len(paul.knowledge)} topics")
            print(f"     Activity: {paul.activity.value} at {paul.location.value}")
    
    elif command == "run":
        try:
            await world.run_simulation()
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            world.stop_simulation()
            await world._save_world()
    
    elif command == "ask":
        question = sys.argv[2] if len(sys.argv) > 2 else "What will happen?"
        result = await world.ask_pauls(question)
        
        print(f"\n🦷 Paul's World Consensus")
        print(f"Question: {result['question']}")
        print(f"Consensus: {result['consensus']['direction']} ({result['consensus']['confidence']:.0%})")
        print(f"\n💬 Responses ({result['pauls_count']} Pauls):")
        
        for r in result['responses'][:5]:
            mood = "😊" if r['mood'] > 0.2 else "😐" if r['mood'] > -0.2 else "😔"
            energy = "⚡" if r['energy'] > 70 else "🔋" if r['energy'] > 30 else "🪫"
            print(f"\n  {r['emoji']} {r['paul_name']} {mood} {energy}")
            print(f"     {r['sentiment']} ({r['confidence']:.0%})")
            print(f"     \"{r['reasoning'][:100]}...\"")
            if r['relevant_knowledge']:
                print(f"     📚 Knows about: {', '.join(r['relevant_knowledge'])}")
        
        if result['responses']:
            print(f"\n📈 View full results:")
            print(f"   {result['view_urls']['explorer']}")
    
    elif command == "export":
        snapshot = {
            "world_time": world.world_time.isoformat(),
            "pauls": {name: paul.to_dict() for name, paul in world.pauls.items()},
        }
        with open("paul_world_export.json", "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        print("✅ Exported to paul_world_export.json")


if __name__ == "__main__":
    asyncio.run(main())
