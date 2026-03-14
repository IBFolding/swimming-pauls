"""
Scales v1.0 - Multi-Agent Simulation Engine
Core agent implementation with personas and traits.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import random
import uuid


class AgentTrait(Enum):
    """Core personality traits affecting agent behavior."""
    # General traits
    OPTIMISTIC = "optimistic"
    PESSIMISTIC = "pessimistic"
    AGGRESSIVE = "aggressive"
    CONSERVATIVE = "conservative"
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    # Film/Entertainment industry traits
    CREATIVE = "creative"           # Vision-driven, artistic perspective
    BUDGET_CONSCIOUS = "budget_conscious"  # Cost-focused, ROI-minded
    NARRATIVE_DRIVEN = "narrative_driven"  # Story-focused, audience-centric
    RISK_AVERSE = "risk_averse"     # Cautious, seeks guarantees
    INNOVATIVE = "innovative"       # Early adopter, experimental


class PersonaType(Enum):
    """Predefined agent personas."""
    # Financial personas
    ANALYST = "analyst"             # Data-driven, analytical
    TRADER = "trader"               # Risk-tolerant, aggressive
    HEDGIE = "hedgie"               # Conservative, risk-aware
    VISIONARY = "visionary"         # Intuitive, forward-looking
    SKEPTIC = "skeptic"             # Pessimistic, cautious
    # Film/Entertainment industry personas
    PRODUCER = "producer"           # Budget-focused, ROI-driven
    DIRECTOR = "director"           # Creative/vision-driven
    SCREENWRITER = "screenwriter"   # Narrative-driven, story-first
    STUDIO_EXEC = "studio_exec"     # Risk-averse, franchise-focused
    INDIE_FILMMAKER = "indie_filmmaker"  # Innovation-focused, artistic


PERSONA_PROFILES = {
    # Financial personas
    PersonaType.ANALYST: {
        "traits": [AgentTrait.ANALYTICAL, AgentTrait.CONSERVATIVE],
        "bias": 0.0,
        "confidence": 0.8,
        "adaptability": 0.4,
    },
    PersonaType.TRADER: {
        "traits": [AgentTrait.AGGRESSIVE, AgentTrait.OPTIMISTIC],
        "bias": 0.3,
        "confidence": 0.9,
        "adaptability": 0.8,
    },
    PersonaType.HEDGIE: {
        "traits": [AgentTrait.CONSERVATIVE, AgentTrait.PESSIMISTIC],
        "bias": -0.2,
        "confidence": 0.7,
        "adaptability": 0.3,
    },
    PersonaType.VISIONARY: {
        "traits": [AgentTrait.INTUITIVE, AgentTrait.OPTIMISTIC],
        "bias": 0.5,
        "confidence": 0.6,
        "adaptability": 0.7,
    },
    PersonaType.SKEPTIC: {
        "traits": [AgentTrait.PESSIMISTIC, AgentTrait.ANALYTICAL],
        "bias": -0.4,
        "confidence": 0.6,
        "adaptability": 0.2,
    },
    # Film/Entertainment industry personas
    PersonaType.PRODUCER: {
        "traits": [AgentTrait.BUDGET_CONSCIOUS, AgentTrait.ANALYTICAL],
        "bias": -0.1,
        "confidence": 0.75,
        "adaptability": 0.5,
    },
    PersonaType.DIRECTOR: {
        "traits": [AgentTrait.CREATIVE, AgentTrait.INTUITIVE],
        "bias": 0.4,
        "confidence": 0.85,
        "adaptability": 0.6,
    },
    PersonaType.SCREENWRITER: {
        "traits": [AgentTrait.NARRATIVE_DRIVEN, AgentTrait.INTUITIVE],
        "bias": 0.2,
        "confidence": 0.7,
        "adaptability": 0.65,
    },
    PersonaType.STUDIO_EXEC: {
        "traits": [AgentTrait.RISK_AVERSE, AgentTrait.CONSERVATIVE],
        "bias": -0.3,
        "confidence": 0.8,
        "adaptability": 0.25,
    },
    PersonaType.INDIE_FILMMAKER: {
        "traits": [AgentTrait.INNOVATIVE, AgentTrait.CREATIVE],
        "bias": 0.5,
        "confidence": 0.6,
        "adaptability": 0.9,
    },
}


@dataclass
class AgentPrediction:
    """Prediction output from an agent."""
    agent_id: str
    direction: str  # "bullish", "bearish", "neutral"
    confidence: float  # 0.0 to 1.0
    magnitude: float  # Expected magnitude of change
    reasoning: str
    timestamp: float


@dataclass
class AgentMemory:
    """Agent's memory of past predictions and outcomes."""
    predictions: List[AgentPrediction] = field(default_factory=list)
    accuracy_score: float = 0.5  # Track historical accuracy
    recent_signals: List[Dict[str, Any]] = field(default_factory=list)


class Agent:
    """
    Core agent class with persona-based decision making.
    
    Each agent has:
    - A persona that defines its behavioral traits
    - Memory of past predictions
    - Adjustable confidence based on performance
    """
    
    def __init__(
        self,
        name: str,
        persona: PersonaType,
        custom_bias: Optional[float] = None,
        custom_confidence: Optional[float] = None,
    ):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.persona = persona
        self.profile = PERSONA_PROFILES[persona]
        
        # Override with custom values if provided
        self.bias = custom_bias if custom_bias is not None else self.profile["bias"]
        self.base_confidence = custom_confidence if custom_confidence is not None else self.profile["confidence"]
        self.adaptability = self.profile["adaptability"]
        self.traits = self.profile["traits"]
        
        self.memory = AgentMemory()
        self.current_confidence = self.base_confidence
        
    def predict(self, market_data: Dict[str, Any]) -> AgentPrediction:
        """
        Generate a prediction based on market data and persona.
        
        Args:
            market_data: Dictionary containing market signals (price, volume, sentiment, etc.)
            
        Returns:
            AgentPrediction with direction, confidence, and reasoning
        """
        import time
        
        # Extract signals
        price_trend = market_data.get("price_trend", 0.0)
        volume = market_data.get("volume", 0.0)
        sentiment = market_data.get("sentiment", 0.0)
        volatility = market_data.get("volatility", 0.5)
        
        # Film/entertainment specific signals
        box_office_trend = market_data.get("box_office_trend", 0.0)
        audience_score = market_data.get("audience_score", 0.5)
        critic_score = market_data.get("critic_score", 0.5)
        franchise_potential = market_data.get("franchise_potential", 0.5)
        
        # Weight signals based on traits
        signal_strength = self._calculate_signal_strength(
            price_trend, volume, sentiment, volatility,
            box_office_trend, audience_score, critic_score, franchise_potential
        )
        
        # Apply persona bias
        adjusted_signal = signal_strength + self.bias
        
        # Determine direction
        if adjusted_signal > 0.2:
            direction = "bullish"
        elif adjusted_signal < -0.2:
            direction = "bearish"
        else:
            direction = "neutral"
            
        # Calculate magnitude and confidence
        magnitude = abs(adjusted_signal) * (1 + self.current_confidence)
        confidence = self._adjust_confidence(volatility)
        
        # Generate reasoning based on persona
        reasoning = self._generate_reasoning(
            direction, signal_strength, market_data
        )
        
        prediction = AgentPrediction(
            agent_id=self.id,
            direction=direction,
            confidence=confidence,
            magnitude=magnitude,
            reasoning=reasoning,
            timestamp=time.time(),
        )
        
        # Store in memory
        self.memory.predictions.append(prediction)
        if len(self.memory.predictions) > 100:
            self.memory.predictions.pop(0)
            
        return prediction
    
    def _calculate_signal_strength(
        self,
        price_trend: float,
        volume: float,
        sentiment: float,
        volatility: float,
        box_office_trend: float = 0.0,
        audience_score: float = 0.5,
        critic_score: float = 0.5,
        franchise_potential: float = 0.5,
    ) -> float:
        """Calculate weighted signal strength from market data."""
        # Base weights
        weights = {
            "price": 0.4,
            "volume": 0.2,
            "sentiment": 0.3,
            "volatility": 0.1,
        }
        
        # Adjust weights based on traits
        if AgentTrait.ANALYTICAL in self.traits:
            weights["price"] += 0.1
            weights["volume"] += 0.1
        if AgentTrait.INTUITIVE in self.traits:
            weights["sentiment"] += 0.15
        if AgentTrait.AGGRESSIVE in self.traits:
            weights["volatility"] += 0.1
            
        # Film/entertainment specific weight adjustments
        if AgentTrait.BUDGET_CONSCIOUS in self.traits:
            # Producers care more about box office and volume
            weights["volume"] += 0.1
        if AgentTrait.CREATIVE in self.traits:
            # Directors weigh critical reception
            weights["sentiment"] += 0.1
        if AgentTrait.NARRATIVE_DRIVEN in self.traits:
            # Screenwriters focus on audience connection
            weights["sentiment"] += 0.15
        if AgentTrait.RISK_AVERSE in self.traits:
            # Studio execs want stability and franchise potential
            weights["volatility"] -= 0.05
        if AgentTrait.INNOVATIVE in self.traits:
            # Indie filmmakers are contrarian signal seekers
            weights["sentiment"] += 0.1
            weights["price"] -= 0.05
            
        # Normalize weights
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}
        
        signal = (
            price_trend * weights["price"] +
            volume * weights["volume"] +
            sentiment * weights["sentiment"] +
            (volatility - 0.5) * weights["volatility"]
        )
        
        # Apply film-specific signal modifiers
        if box_office_trend != 0.0:
            signal += box_office_trend * 0.1
        if AgentTrait.NARRATIVE_DRIVEN in self.traits and audience_score != 0.5:
            signal += (audience_score - 0.5) * 0.15
        if AgentTrait.CREATIVE in self.traits and critic_score != 0.5:
            signal += (critic_score - 0.5) * 0.1
        if AgentTrait.RISK_AVERSE in self.traits and franchise_potential != 0.5:
            signal += (franchise_potential - 0.5) * 0.2
            
        return max(-1.0, min(1.0, signal))
    
    def _adjust_confidence(self, volatility: float) -> float:
        """Adjust confidence based on market conditions and history."""
        # Reduce confidence in high volatility
        vol_adjustment = 1.0 - (volatility * 0.5)
        
        # Risk-averse personas are less confident in volatile markets
        if AgentTrait.RISK_AVERSE in self.traits:
            vol_adjustment *= 0.8
            
        # Innovative personas maintain confidence despite volatility
        if AgentTrait.INNOVATIVE in self.traits:
            vol_adjustment = min(1.0, vol_adjustment * 1.2)
        
        # Adjust based on recent accuracy
        accuracy_boost = (self.memory.accuracy_score - 0.5) * 0.2
        
        adjusted = self.current_confidence * vol_adjustment + accuracy_boost
        return max(0.1, min(1.0, adjusted))
    
    def _generate_reasoning(
        self,
        direction: str,
        signal_strength: float,
        market_data: Dict[str, Any],
    ) -> str:
        """Generate human-readable reasoning for the prediction."""
        templates = {
            # Financial personas
            PersonaType.ANALYST: [
                "Data indicates {direction} momentum based on price action and volume analysis.",
                "Technical signals suggest {direction} bias with {confidence:.0%} confidence.",
                "Quantitative analysis favors {direction} positioning.",
            ],
            PersonaType.TRADER: [
                "The tape is showing {direction} flows. I'm leaning {direction}.",
                "Momentum is {direction} — time to ride it.",
                "Smart money positioning suggests {direction} move incoming.",
            ],
            PersonaType.HEDGIE: [
                "Risk-adjusted view favors {direction} with hedges in place.",
                "Downside protection warranted; {direction} bias with tight stops.",
                "Conservative read: {direction} with limited exposure.",
            ],
            PersonaType.VISIONARY: [
                "Pattern recognition suggests {direction} inflection point.",
                "The narrative is shifting {direction} — early signal.",
                "Intuition plus structure points {direction}.",
            ],
            PersonaType.SKEPTIC: [
                "Contrary to consensus, seeing {direction} signals.",
                "Froth indicates {direction} reversal likely.",
                "Skeptical of rallies; {direction} positioning preferred.",
            ],
            # Film/Entertainment industry personas
            PersonaType.PRODUCER: [
                "ROI analysis favors {direction} — we need to protect the budget.",
                "Production costs vs. projected returns indicate {direction} positioning.",
                "From a financing standpoint, the smart money is {direction}.",
                "Can we make the numbers work? Data says {direction}.",
            ],
            PersonaType.DIRECTOR: [
                "I have a vision, and it's telling me {direction}.",
                "The creative momentum is undeniable — I'm feeling {direction}.",
                "This story arc points {direction}. Trust the process.",
                "The zeitgeist is shifting {direction}. I can feel it.",
            ],
            PersonaType.SCREENWRITER: [
                "The narrative structure supports a {direction} outcome.",
                "Character development suggests we're heading {direction}.",
                "The third act is going to be {direction} — the setup is clear.",
                "Story beats align with {direction} momentum.",
            ],
            PersonaType.STUDIO_EXEC: [
                "Franchise potential analysis shows {direction} trajectory.",
                "Board wants risk mitigation; {direction} positioning protects shareholder value.",
                "Market research indicates {direction} is the safe bet.",
                "We can't afford a bomb — {direction} minimizes downside.",
            ],
            PersonaType.INDIE_FILMMAKER: [
                "Mainstream is missing the signal — I'm betting {direction}.",
                "This is disruptive. The established players won't see {direction} coming.",
                "Innovation requires conviction. I'm {direction} despite the noise.",
                "The auteur's perspective: {direction} is where the art is.",
            ],
        }
        
        template = random.choice(templates[self.persona])
        confidence_str = "high" if self.current_confidence > 0.7 else "moderate" if self.current_confidence > 0.4 else "low"
        
        return template.format(
            direction=direction,
            confidence=self.current_confidence,
        )
    
    def update_accuracy(self, actual_outcome: float) -> None:
        """
        Update agent's accuracy based on actual market outcome.
        
        Args:
            actual_outcome: Actual price change (-1.0 to 1.0)
        """
        if not self.memory.predictions:
            return
            
        last_prediction = self.memory.predictions[-1]
        
        # Check if prediction matched outcome
        if actual_outcome > 0.1 and last_prediction.direction == "bullish":
            correct = True
        elif actual_outcome < -0.1 and last_prediction.direction == "bearish":
            correct = True
        elif abs(actual_outcome) <= 0.1 and last_prediction.direction == "neutral":
            correct = True
        else:
            correct = False
            
        # Update accuracy score with exponential moving average
        alpha = 0.3  # Learning rate
        if correct:
            self.memory.accuracy_score = (1 - alpha) * self.memory.accuracy_score + alpha
        else:
            self.memory.accuracy_score = (1 - alpha) * self.memory.accuracy_score
            
        # Adjust confidence based on adaptability
        if self.adaptability > 0.5:
            if correct:
                self.current_confidence = min(1.0, self.current_confidence + 0.05)
            else:
                self.current_confidence = max(0.1, self.current_confidence - 0.1)
    
    def __repr__(self) -> str:
        return f"Agent({self.name}, {self.persona.value}, conf={self.current_confidence:.2f})"


def create_agent_team(
    analyst_count: int = 1,
    trader_count: int = 1,
    hedgie_count: int = 1,
    visionary_count: int = 1,
    skeptic_count: int = 1,
    producer_count: int = 0,
    director_count: int = 0,
    screenwriter_count: int = 0,
    studio_exec_count: int = 0,
    indie_filmmaker_count: int = 0,
) -> List[Agent]:
    """Create a balanced team of agents with different personas."""
    team = []
    
    # Financial personas
    for i in range(analyst_count):
        team.append(Agent(f"Analyst-{i+1}", PersonaType.ANALYST))
    for i in range(trader_count):
        team.append(Agent(f"Trader-{i+1}", PersonaType.TRADER))
    for i in range(hedgie_count):
        team.append(Agent(f"Hedgie-{i+1}", PersonaType.HEDGIE))
    for i in range(visionary_count):
        team.append(Agent(f"Visionary-{i+1}", PersonaType.VISIONARY))
    for i in range(skeptic_count):
        team.append(Agent(f"Skeptic-{i+1}", PersonaType.SKEPTIC))
    
    # Film/Entertainment industry personas
    for i in range(producer_count):
        team.append(Agent(f"Producer-{i+1}", PersonaType.PRODUCER))
    for i in range(director_count):
        team.append(Agent(f"Director-{i+1}", PersonaType.DIRECTOR))
    for i in range(screenwriter_count):
        team.append(Agent(f"Screenwriter-{i+1}", PersonaType.SCREENWRITER))
    for i in range(studio_exec_count):
        team.append(Agent(f"StudioExec-{i+1}", PersonaType.STUDIO_EXEC))
    for i in range(indie_filmmaker_count):
        team.append(Agent(f"IndieFilmmaker-{i+1}", PersonaType.INDIE_FILMMAKER))
        
    return team


def create_film_industry_team(
    producer_count: int = 1,
    director_count: int = 1,
    screenwriter_count: int = 1,
    studio_exec_count: int = 1,
    indie_filmmaker_count: int = 1,
) -> List[Agent]:
    """
    Create a team specialized for film/entertainment industry analysis.
    
    This team configuration brings together the key stakeholders in film production
    and distribution for entertainment market analysis.
    """
    return create_agent_team(
        analyst_count=0,
        trader_count=0,
        hedgie_count=0,
        visionary_count=0,
        skeptic_count=0,
        producer_count=producer_count,
        director_count=director_count,
        screenwriter_count=screenwriter_count,
        studio_exec_count=studio_exec_count,
        indie_filmmaker_count=indie_filmmaker_count,
    )
