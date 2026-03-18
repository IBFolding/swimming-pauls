"""
Paul World - Persistent Simulation Environment
Swimming Pauls living in a virtual world, evolving over time.

Author: Howard (H.O.W.A.R.D)
"""

import asyncio
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
from pathlib import Path


class Activity(Enum):
    """What a Paul can be doing."""
    IDLE = "idle"
    RESEARCHING = "researching"
    DEBATING = "debating"
    RESTING = "resting"
    SOCIALIZING = "socializing"
    TRADING = "trading"
    ANALYZING = "analyzing"


class Location(Enum):
    """Virtual world locations."""
    MARKET_FLOOR = "market_floor"
    RESEARCH_LAB = "research_lab"
    CAFE = "cafe"
    HOME = "home"
    CONFERENCE_ROOM = "conference_room"
    PARK = "park"


@dataclass
class Relationship:
    """Relationship between two Pauls."""
    trust: float = 0.5  # 0-1, how much they trust each other
    respect: float = 0.5  # 0-1, professional respect
    interactions: int = 0  # Number of past interactions
    last_interaction: Optional[datetime] = None
    

@dataclass
class PaulState:
    """Current state of a Paul in the world."""
    # Identity
    name: str
    emoji: str
    specialty: str
    
    # Location & Activity
    location: Location = Location.HOME
    activity: Activity = Activity.IDLE
    
    # Needs (0-100)
    energy: float = 100.0
    knowledge: float = 50.0  # Current knowledge freshness
    social: float = 50.0  # Need for social interaction
    
    # Reputation
    accuracy_score: float = 0.5  # Track record (0-1)
    influence_score: float = 0.5  # How persuasive they are
    reputation: float = 0.5  # Overall standing in community
    
    # Personality drift (evolves over time)
    risk_tolerance: float = 0.5
    optimism: float = 0.5
    
    # State tracking
    last_active: datetime = field(default_factory=datetime.now)
    predictions_made: int = 0
    predictions_correct: int = 0
    
    def to_dict(self) -> dict:
        return {
            **asdict(self),
            'location': self.location.value,
            'activity': self.activity.value,
            'last_active': self.last_active.isoformat(),
        }


@dataclass
class WorldEvent:
    """Something that happens in the world."""
    timestamp: datetime
    event_type: str  # "market_move", "news", "prediction_request", "social"
    data: dict
    severity: float = 0.5  # 0-1, how much it affects the world


class PaulWorld:
    """
    Persistent virtual world where Pauls live, work, and evolve.
    
    Features:
    - Pauls have daily routines (research, debate, rest)
    - Form relationships (trust, respect)
    - React to world events
    - Evolve based on accuracy
    - Can run 24/7 locally or on Mac Mini
    
    Usage:
        world = PaulWorld()
        await world.initialize()  # Load or create world
        
        # Start simulation loop
        await world.run_simulation()
        
        # Or tick manually
        await world.tick()  # One hour passes
    """
    
    def __init__(self, db_path: str = "data/paul_world.db"):
        self.db_path = Path(db_path)
        self.pauls: Dict[str, PaulState] = {}
        self.relationships: Dict[Tuple[str, str], Relationship] = {}
        self.events: List[WorldEvent] = []
        self.world_time: datetime = datetime.now()
        self.tick_count: int = 0
        
        # World parameters
        self.time_speed: float = 1.0  # 1.0 = real-time, 60.0 = 1 min = 1 hour
        self.active: bool = False
        
    async def initialize(self):
        """Initialize or load existing world."""
        self._init_db()
        
        # Try to load existing world
        if not await self._load_world():
            # Create new world with starting Pauls
            await self._create_starting_world()
            
    def _init_db(self):
        """Initialize SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Paul states
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_states (
                name TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                updated_at TEXT NOT NULL
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
                severity REAL
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
        
    async def _load_world(self) -> bool:
        """Load world from database. Returns True if successful."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Load Pauls
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
                location=Location(data['location']),
                activity=Activity(data['activity']),
                energy=data['energy'],
                knowledge=data['knowledge'],
                social=data['social'],
                accuracy_score=data['accuracy_score'],
                influence_score=data['influence_score'],
                reputation=data['reputation'],
                risk_tolerance=data['risk_tolerance'],
                optimism=data['optimism'],
                last_active=datetime.fromisoformat(data['last_active']),
                predictions_made=data['predictions_made'],
                predictions_correct=data['predictions_correct'],
            )
            self.pauls[name] = paul
            
        # Load relationships
        cursor.execute('SELECT paul_a, paul_b, data FROM relationships')
        for paul_a, paul_b, data_json in cursor.fetchall():
            data = json.loads(data_json)
            rel = Relationship(
                trust=data['trust'],
                respect=data['respect'],
                interactions=data['interactions'],
                last_interaction=datetime.fromisoformat(data['last_interaction']) if data['last_interaction'] else None
            )
            self.relationships[(paul_a, paul_b)] = rel
            
        # Load world time
        cursor.execute("SELECT value FROM world_state WHERE key = 'world_time'")
        row = cursor.fetchone()
        if row:
            self.world_time = datetime.fromisoformat(row[0])
            
        conn.close()
        return True
        
    async def _create_starting_world(self):
        """Create a new world with starting Pauls."""
        from persona_factory import generate_swimming_pauls_pool
        
        # Generate initial Pauls
        initial_pauls = [
            {"name": "Visionary Paul", "emoji": "🔮", "specialty": "Disruptive Innovation"},
            {"name": "Professor Paul", "emoji": "👨‍🏫", "specialty": "Macro Research"},
            {"name": "Trader Paul", "emoji": "📈", "specialty": "Market Timing"},
            {"name": "Skeptic Paul", "emoji": "🤨", "specialty": "Risk Assessment"},
            {"name": "Whale Paul", "emoji": "🐋", "specialty": "Institutional Flow"},
            {"name": "Degen Paul", "emoji": "🎰", "specialty": "High Risk"},
            {"name": "Quant Paul", "emoji": "📊", "specialty": "Quantitative Analysis"},
            {"name": "Contrarian Paul", "emoji": "🐻", "specialty": "Contrarian Views"},
        ]
        
        for p in initial_pauls:
            self.pauls[p["name"]] = PaulState(
                name=p["name"],
                emoji=p["emoji"],
                specialty=p["specialty"],
                location=random.choice(list(Location)),
                activity=Activity.IDLE,
            )
            
        # Initialize random relationships
        paul_names = list(self.pauls.keys())
        for i, name_a in enumerate(paul_names):
            for name_b in paul_names[i+1:]:
                if random.random() < 0.3:  # 30% chance of relationship
                    self.relationships[(name_a, name_b)] = Relationship(
                        trust=random.uniform(0.3, 0.7),
                        respect=random.uniform(0.3, 0.7),
                    )
                    
        await self._save_world()
        
    async def _save_world(self):
        """Save world state to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save Pauls
        for name, paul in self.pauls.items():
            cursor.execute('''
                INSERT OR REPLACE INTO paul_states (name, data, updated_at)
                VALUES (?, ?, ?)
            ''', (name, json.dumps(paul.to_dict()), datetime.now().isoformat()))
            
        # Save relationships
        for (paul_a, paul_b), rel in self.relationships.items():
            cursor.execute('''
                INSERT OR REPLACE INTO relationships (paul_a, paul_b, data)
                VALUES (?, ?, ?)
            ''', (paul_a, paul_b, json.dumps(asdict(rel))))
            
        # Save world time
        cursor.execute('''
            INSERT OR REPLACE INTO world_state (key, value)
            VALUES ('world_time', ?)
        ''', (self.world_time.isoformat(),))
        
        conn.commit()
        conn.close()
        
    async def tick(self):
        """
        Advance world by one hour.
        This is the core simulation loop.
        """
        self.tick_count += 1
        self.world_time += timedelta(hours=1)
        
        # Each Paul decides what to do
        for name, paul in self.pauls.items():
            await self._update_paul(paul)
            
        # Random world events
        if random.random() < 0.1:  # 10% chance per hour
            await self._spawn_world_event()
            
        # Paul interactions
        await self._process_interactions()
        
        # Save state periodically
        if self.tick_count % 6 == 0:  # Every 6 hours
            await self._save_world()
            
    async def _update_paul(self, paul: PaulState):
        """Update a single Paul's state for one hour."""
        # Energy decreases with activity
        if paul.activity in [Activity.DEBATING, Activity.RESEARCHING, Activity.TRADING]:
            paul.energy -= 10
        else:
            paul.energy = min(100, paul.energy + 5)  # Resting recovers
            
        # Decide next activity based on needs
        if paul.energy < 20:
            paul.activity = Activity.RESTING
            paul.location = Location.HOME
        elif paul.social < 30:
            paul.activity = Activity.SOCIALIZING
            paul.location = random.choice([Location.CAFE, Location.PARK])
        elif paul.knowledge < 40:
            paul.activity = Activity.RESEARCHING
            paul.location = Location.RESEARCH_LAB
        else:
            # Based on specialty
            if "Trader" in paul.specialty:
                paul.activity = random.choice([Activity.TRADING, Activity.ANALYZING])
                paul.location = Location.MARKET_FLOOR
            elif "Professor" in paul.specialty or "Research" in paul.specialty:
                paul.activity = Activity.RESEARCHING
                paul.location = Location.RESEARCH_LAB
            else:
                paul.activity = random.choice(list(Activity))
                
        # Update needs
        paul.knowledge -= 2  # Knowledge decays
        paul.social -= 3 if paul.activity != Activity.SOCIALIZING else 0
        
        paul.last_active = self.world_time
        
    async def _process_interactions(self):
        """Process random Paul interactions."""
        # Find Pauls in same location
        location_groups: Dict[Location, List[str]] = {}
        for name, paul in self.pauls.items():
            if paul.location not in location_groups:
                location_groups[paul.location] = []
            location_groups[paul.location].append(name)
            
        # Process interactions in each location
        for location, names in location_groups.items():
            if len(names) < 2:
                continue
                
            # Random pairs interact
            random.shuffle(names)
            for i in range(0, len(names) - 1, 2):
                name_a, name_b = names[i], names[i + 1]
                await self._interact(name_a, name_b)
                
    async def _interact(self, name_a: str, name_b: str):
        """Two Pauls interact."""
        paul_a = self.pauls[name_a]
        paul_b = self.pauls[name_b]
        
        # Get or create relationship
        key = tuple(sorted([name_a, name_b]))
        if key not in self.relationships:
            self.relationships[key] = Relationship()
            
        rel = self.relationships[key]
        
        # Interaction affects relationship
        if paul_a.activity == paul_b.activity == Activity.DEBATING:
            # Debating - respect increases if both knowledgeable
            if paul_a.knowledge > 70 and paul_b.knowledge > 70:
                rel.respect = min(1.0, rel.respect + 0.05)
            # Trust increases if accuracy is good
            if paul_a.accuracy_score > 0.6 and paul_b.accuracy_score > 0.6:
                rel.trust = min(1.0, rel.trust + 0.03)
                
        rel.interactions += 1
        rel.last_interaction = self.world_time
        
        # Both gain social satisfaction
        paul_a.social = min(100, paul_a.social + 10)
        paul_b.social = min(100, paul_b.social + 10)
        
    async def _spawn_world_event(self):
        """Create a random world event."""
        events = [
            ("market_move", {"asset": "BTC", "change": random.uniform(-0.1, 0.1)}, 0.7),
            ("news", {"topic": "ETF", "sentiment": random.choice(["positive", "negative"])}, 0.5),
            ("social", {"event": "conference", "topic": "DeFi"}, 0.3),
        ]
        
        event_type, data, severity = random.choice(events)
        
        event = WorldEvent(
            timestamp=self.world_time,
            event_type=event_type,
            data=data,
            severity=severity
        )
        self.events.append(event)
        
        # Events affect Pauls
        for paul in self.pauls.values():
            if event_type == "market_move" and paul.location == Location.MARKET_FLOOR:
                paul.activity = Activity.ANALYZING
                paul.knowledge = min(100, paul.knowledge + 10)  # Learn from event
                
    async def run_simulation(self):
        """Run continuous simulation."""
        self.active = True
        
        while self.active:
            await self.tick()
            
            # Sleep based on time speed
            # time_speed = 1.0: 1 hour = 1 real hour
            # time_speed = 60.0: 1 hour = 1 real minute
            sleep_seconds = 3600 / self.time_speed
            await asyncio.sleep(min(sleep_seconds, 10))  # Cap at 10s for testing
            
    def stop_simulation(self):
        """Stop the simulation loop."""
        self.active = False
        
    def get_world_snapshot(self) -> dict:
        """Get current world state for visualization."""
        return {
            "world_time": self.world_time.isoformat(),
            "tick_count": self.tick_count,
            "pauls": {name: paul.to_dict() for name, paul in self.pauls.items()},
            "location_groups": self._get_location_groups(),
            "recent_events": [asdict(e) for e in self.events[-10:]],
        }
        
    def _get_location_groups(self) -> Dict[str, List[str]]:
        """Group Pauls by location."""
        groups = {}
        for name, paul in self.pauls.items():
            loc = paul.location.value
            if loc not in groups:
                groups[loc] = []
            groups[loc].append(name)
        return groups
        
    def spawn_prediction_request(self, question: str) -> List[dict]:
        """
        When user asks a question, Pauls in the world respond.
        Returns list of Paul opinions.
        """
        responses = []
        
        for name, paul in self.pauls.items():
            # Only active Pauls respond
            if paul.energy > 30:
                # Influence by location (Pauls in same location influence each other)
                location_bonus = 0
                others_here = [p for n, p in self.pauls.items() 
                              if p.location == paul.location and n != name]
                for other in others_here:
                    key = tuple(sorted([name, other.name]))
                    if key in self.relationships:
                        location_bonus += self.relationships[key].trust * 0.1
                        
                # Generate opinion based on Paul's state
                sentiment = self._generate_sentiment(paul, location_bonus)
                
                responses.append({
                    "paul_name": name,
                    "emoji": paul.emoji,
                    "sentiment": sentiment,
                    "confidence": paul.accuracy_score + (paul.knowledge / 200),
                    "location": paul.location.value,
                    "reasoning": self._generate_reasoning(paul, question),
                })
                
                paul.predictions_made += 1
                
        return responses
        
    def _generate_sentiment(self, paul: PaulState, location_bonus: float) -> str:
        """Generate sentiment based on Paul's state."""
        # Optimistic Pauls lean bullish
        base_optimism = paul.optimism + location_bonus
        
        if base_optimism > 0.6:
            return "BULLISH"
        elif base_optimism < 0.4:
            return "BEARISH"
        return "NEUTRAL"
        
    def _generate_reasoning(self, paul: PaulState, question: str) -> str:
        """Generate reasoning based on specialty."""
        reasonings = {
            "Visionary": "The long-term trend indicates...",
            "Professor": "Historical data suggests...",
            "Trader": "Technical analysis shows...",
            "Skeptic": "However, we must consider risks...",
            "Whale": "Institutional flow indicates...",
        }
        
        for key, template in reasonings.items():
            if key in paul.specialty or key in paul.name:
                return template
                
        return "Based on my analysis..."


# CLI for managing Paul World
async def main():
    import sys
    
    world = PaulWorld()
    await world.initialize()
    
    if len(sys.argv) < 2:
        print("Paul World Commands:")
        print("  status      - Show world status")
        print("  run         - Start simulation (runs until Ctrl+C)")
        print("  tick        - Advance one hour")
        print("  ask         - Ask the world a question")
        print("  export      - Export world state to JSON")
        sys.exit(0)
        
    command = sys.argv[1]
    
    if command == "status":
        snapshot = world.get_world_snapshot()
        print(f"\n🌍 Paul World Status")
        print(f"World Time: {snapshot['world_time']}")
        print(f"Ticks: {snapshot['tick_count']}")
        print(f"\n📍 Locations:")
        for loc, pauls in snapshot['location_groups'].items():
            print(f"  {loc}: {', '.join(pauls)}")
        print(f"\n👥 Pauls ({len(snapshot['pauls'])}):")
        for name, paul in snapshot['pauls'].items():
            print(f"  {paul['emoji']} {name}: {paul['activity']} at {paul['location']}")
            
    elif command == "run":
        print("🌍 Starting Paul World simulation...")
        print("Press Ctrl+C to stop")
        try:
            await world.run_simulation()
        except KeyboardInterrupt:
            print("\nStopping...")
            world.stop_simulation()
            
    elif command == "tick":
        await world.tick()
        print(f"⏰ Advanced to {world.world_time}")
        
    elif command == "ask":
        question = sys.argv[2] if len(sys.argv) > 2 else "What will happen?"
        responses = world.spawn_prediction_request(question)
        print(f"\n🗣️ Responses to: '{question}'\n")
        for r in responses:
            print(f"{r['emoji']} {r['paul_name']}: {r['sentiment']} ({r['confidence']:.0%})")
            print(f"   {r['reasoning']}")
            print()
            
    elif command == "export":
        snapshot = world.get_world_snapshot()
        with open("paul_world_export.json", "w") as f:
            json.dump(snapshot, f, indent=2, default=str)
        print("✅ Exported to paul_world_export.json")


if __name__ == "__main__":
    asyncio.run(main())
