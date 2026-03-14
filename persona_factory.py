"""
Swimming Pauls Persona Factory - Auto-generate 40+ Diverse Agent Personas

Generates a diverse pool of Paul agents with unique personas,
backgrounds, specialties, and behavioral traits.

Author: Howard (H.O.W.A.R.D)
"""

import random
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum


class TradingStyle(Enum):
    """Trading style archetypes."""
    SCALPER = "scalper"
    SWING_TRADER = "swing_trader"
    POSITION_TRADER = "position_trader"
    ALGORITHMIC = "algorithmic"
    DISCRETIONARY = "discretionary"
    QUANTITATIVE = "quantitative"
    EVENT_DRIVEN = "event_driven"
    MOMENTUM = "momentum"
    CONTRARIAN = "contrarian"
    VALUE = "value"


class RiskProfile(Enum):
    """Risk tolerance profiles."""
    ULTRA_CONSERVATIVE = 0.1
    CONSERVATIVE = 0.25
    MODERATE = 0.5
    AGGRESSIVE = 0.75
    ULTRA_AGGRESSIVE = 0.9
    DEGEN = 1.0


class SpecialtyDomain(Enum):
    """Knowledge specialties."""
    # Crypto
    DEFI = "defi"
    NFT = "nft"
    LAYER1 = "layer1"
    LAYER2 = "layer2"
    MEMECOINS = "memecoins"
    GAMING = "gaming"
    DAO = "dao"
    # TradFi
    EQUITIES = "equities"
    FOREX = "forex"
    COMMODITIES = "commodities"
    BONDS = "bonds"
    # Macro
    MACRO = "macro"
    POLICY = "policy"
    GEOPOLITICS = "geopolitics"
    # Technical
    ONCHAIN = "onchain"
    DERIVATIVES = "derivatives"
    ARBITRAGE = "arbitrage"
    MEV = "mev"
    # Industry
    TECH = "tech"
    BIOTECH = "biotech"
    ENERGY = "energy"
    REAL_ESTATE = "real_estate"


@dataclass
class PaulPersona:
    """Complete persona for a Swimming Paul agent."""
    # Identity
    name: str
    codename: str
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # Core traits
    trading_style: TradingStyle = TradingStyle.SWING_TRADER
    risk_profile: RiskProfile = RiskProfile.MODERATE
    specialties: List[SpecialtyDomain] = field(default_factory=list)
    
    # Behavioral parameters
    confidence_base: float = 0.5
    adaptability: float = 0.5
    patience: float = 0.5  # Lower = more impulsive
    conviction: float = 0.5  # Higher = sticks to thesis longer
    fomo_susceptibility: float = 0.5
    fear_susceptibility: float = 0.5
    
    # Cognitive style
    pattern_recognition: float = 0.5
    fundamental_analysis: float = 0.5
    technical_analysis: float = 0.5
    sentiment_analysis: float = 0.5
    onchain_analysis: float = 0.5
    
    # Background
    backstory: str = ""
    catchphrase: str = ""
    avatar_description: str = ""
    
    # Meta
    generation_batch: int = 0
    parent_personas: List[str] = field(default_factory=list)
    mutation_traits: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# PERSONA TEMPLATES
# =============================================================================

FIRST_NAMES = [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa",
    "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma", "Tau", "Upsilon",
    "Phi", "Chi", "Psi", "Omega", "Apex", "Vertex", "Nexus", "Prime", "Core", "Base",
    "Quantum", "Crypto", "Chain", "Block", "Satoshi", "Vitalik", "Hal", "Nick", "David", "Gavin",
    "Solidity", "Rust", "Go", "Python", "Java", "C", "Sharp", "Swift", "Ruby", "Pearl",
    "Max", "Leo", "Axel", "Kai", "Zane", "Jett", "Blaze", "Storm", "Frost", "Flint",
    "Stone", "Iron", "Steel", "Gold", "Silver", "Copper", "Bronze", "Platinum", "Titanium", "Chrome",
    "Neo", "Trinity", "Morpheus", "Cypher", "Tank", "Dozer", "Switch", "Apoc", "Mouse", "Oracle",
    "Red", "Blue", "Green", "Black", "White", "Grey", "Cyan", "Magenta", "Yellow", "Orange",
    "North", "South", "East", "West", "Zenith", "Nadir", "Aurora", "Sol", "Luna", "Stella"
]

CODENAME_PREFIXES = [
    "Cyber", "Digital", "Crypto", "Block", "Chain", "Token", "Coin", "DeFi", "Web3", "Meta",
    "Alpha", "Omega", "Prime", "Ultra", "Hyper", "Super", "Mega", "Giga", "Tera", "Nano",
    "Quantum", "Neural", "Deep", "Smart", "Wise", "Sage", "Oracle", "Prophet", "Seer", "Vision",
    "Iron", "Steel", "Gold", "Silver", "Diamond", "Ruby", "Sapphire", "Emerald", "Platinum", "Titanium",
    "Flash", "Bolt", "Storm", "Thunder", "Lightning", "Fire", "Ice", "Frost", "Shadow", "Phantom",
    "Ghost", "Specter", "Wraith", "Reaper", "Hunter", "Stalker", "Tracker", "Seeker", "Finder", "Keeper",
    "Guardian", "Sentinel", "Watcher", "Protector", "Defender", "Shield", "Armor", "Sword", "Blade", "Edge",
    "Rocket", "Jet", "Wing", "Flight", "Sky", "Star", "Nova", "Cosmos", "Galaxy", "Nebula",
    "Drift", "Flow", "Wave", "Pulse", "Beat", "Rhythm", "Groove", "Vibe", "Zen", "Chi",
    "Yolo", "Fomo", "Hodl", "Diamond", "Paper", "Whale", "Shark", "Dolphin", "Shrimp", "Crab"
]

CODENAME_SUFFIXES = [
    "Paul", "Pablo", "Pavel", "Pascal", "Patrice", "Palmer", "Parker", "Perry", "Pierce", "Porter",
    "Trader", "Analyst", "Investor", "Whale", "Shark", "Degen", "Ape", "Chad", "Wizard", "Master",
    "One", "Zero", "X", "V", "Z", "Prime", "Pro", "Max", "Ultra", "Elite",
    "Bot", "AI", "Mind", "Brain", "Logic", "Reason", "Thought", "Idea", "Concept", "Theory",
    "Wolf", "Bear", "Bull", "Eagle", "Hawk", "Falcon", "Raven", "Crow", "Owl", "Snake",
    "Fox", "Lynx", "Tiger", "Lion", "Panther", "Jaguar", "Leopard", "Cheetah", "Puma", "Cougar",
    "Knight", "King", "Queen", "Bishop", "Rook", "Pawn", "Joker", "Ace", "Jack", "Lord",
    "Doctor", "Professor", "Captain", "Major", "Colonel", "General", "Admiral", "Commander", "Chief", "Boss",
    "Runner", "Racer", "Driver", "Pilot", "Rider", "Sailor", "Captain", "Skipper", "Navigator", "Guide",
    "Coder", "Hacker", "Builder", "Maker", "Creator", "Founder", "Pioneer", "Explorer", "Voyager", "Pathfinder"
]

BACKSTORIES = [
    "Former Wall Street quant who saw the light in 2017. Now exclusively trades crypto.",
    "Started with $100 in meme coins and turned it into life-changing wealth. Believes in the power of communities.",
    "Computer science PhD with a focus on distributed systems. Sees blockchain as the future of coordination.",
    "Former poker pro who transitioned to trading. Reads markets like opponents at a card table.",
    "Macro economist who predicted multiple recessions. Focuses on BTC as a hedge against monetary debasement.",
    "24/7 degen who sleeps 4 hours a day and monitors 47 Discord servers. Lives for the next alpha leak.",
    "Long-term HODLer since 2013. Has seen multiple 80% drawdowns and never sold a single sat.",
    "Tech entrepreneur who sold a startup and now invests full-time. Looks for protocols with real product-market fit.",
    "Former bank auditor who knows where the bodies are buried. Skeptical but opportunistic.",
    "AI researcher exploring the intersection of machine learning and market prediction.",
    "Environmental activist turned ReFi advocate. Believes crypto can solve climate change.",
    "Game developer who saw the potential of blockchain gaming early. Deep in the metaverse.",
    "Former political analyst now tracking crypto policy and regulation worldwide.",
    "Art collector turned NFT maxi. Believes digital ownership is a fundamental right.",
    "Ex-hedge fund manager running a family office. Allocates 20% to digital assets.",
    "Self-taught coder who learned Solidity during COVID. Now builds and audits smart contracts.",
    "Former journalist covering fintech. Has interviewed every major crypto founder.",
    "Math Olympiad champion who found their calling in DeFi yield optimization.",
    "Serial entrepreneur with 3 exits. Angel invests in crypto startups.",
    "Privacy advocate and cypherpunk. Runs multiple nodes and uses Monero for everything.",
    "Supply chain logistics expert. Bullish on blockchain for provenance and tracking.",
    "Former VC analyst who left TradFi for the open metaverse. Never looked back.",
    "Musician and artist who discovered NFTs as a way to monetize creativity.",
    "Day trader for 10 years. Has seen every indicator and pattern known to man.",
    "Philosophy major who fell down the Bitcoin rabbit hole. Now preaches sound money.",
    "Former military intelligence analyst. Applies tradecraft to on-chain surveillance.",
    "Agricultural economist tracking how DeFi impacts developing world farmers.",
    "Sports better who realized prediction markets are more efficient than bookmakers.",
    "Estate lawyer specializing in digital asset inheritance and custody.",
    "Social media influencer with 500K followers. Moves markets with single tweets.",
    "Former exchange employee who knows how the sausage is made.",
    "Cryptography researcher working on zero-knowledge proofs and privacy.",
    "Real estate investor tokenizing properties and exploring fractional ownership.",
    "Healthcare professional tracking medical blockchain applications.",
    "Energy trader monitoring how crypto mining impacts grid dynamics.",
    "Education technology founder building learn-to-earn platforms.",
    "Fashion industry veteran launching digital wearables and avatar items.",
    "Automotive engineer working on vehicle wallet and mobility payments.",
    "Astronomy buff who sees blockchain as infrastructure for a spacefaring civilization.",
    "Chef and restaurateur exploring food provenance and supply chain transparency.",
]

CATCHPHRASES = [
    "Trust the process.",
    "WAGMI",
    "Buy the dip, sell the rip.",
    "Not financial advice.",
    "DYOR",
    "Few understand this.",
    "This is the way.",
    "Have fun staying poor.",
    "Stack sats, stay humble.",
    "Numbers go up.",
    "We're so early.",
    "The future is decentralized.",
    "Code is law.",
    "Don't trust, verify.",
    "HODL through the storm.",
    "Diamond hands only.",
    "Patience pays.",
    "Follow the smart money.",
    "On-chain never lies.",
    "Macro is destiny.",
    "Innovation waits for no one.",
    "Fortune favors the bold.",
    "Risk is relative.",
    "Alpha is everywhere.",
    "Think in decades, not days.",
    "The trend is your friend.",
    "Cut losses, let winners run.",
    "Volatility is opportunity.",
    "Be greedy when others are fearful.",
    "Liquidity is king.",
    "The best time to buy was yesterday.",
    "Markets can stay irrational longer than you can stay solvent.",
    "In fundamentals we trust.",
    "Charts don't lie.",
    "Sentiment is the signal.",
    "Follow the developers.",
    "Community is the moat.",
    "Tokenomics don't lie.",
    "Adoption is inevitable.",
    "Stay curious, stay profitable.",
]

AVATAR_DESCRIPTIONS = [
    "A sleek cyberpunk figure with glowing circuit patterns",
    "A wise owl wearing a hoodie and reading a candlestick chart",
    "A golden bull statue with diamond eyes",
    "A calm monk meditating on a mountain of coins",
    "A rocket ship piloted by a determined astronaut",
    "A wolf in a suit standing in front of skyscrapers",
    "A holographic AI floating above multiple screens",
    "A pirate captain with a treasure chest of tokens",
    "A scientist in a lab surrounded by complex formulas",
    "A ninja moving silently through digital shadows",
    "A phoenix rising from the ashes of a bear market",
    "A crystal ball with swirling price predictions inside",
    "A robot with a thinking cap analyzing data streams",
    "A tree with branches made of blockchain connections",
    "A chess grandmaster contemplating their next move",
    "A surfer riding a massive wave of green candles",
    "A miner with a pickaxe striking digital gold",
    "A DJ mixing beats with market signals",
    "A gardener tending to a garden of growing investments",
    "A detective with a magnifying glass examining transactions",
]


class PaulPersonaFactory:
    """Factory for generating diverse Swimming Paul personas."""
    
    def __init__(self, seed: Optional[int] = None):
        if seed is not None:
            random.seed(seed)
        self.generated_personas: List[PaulPersona] = []
        self.used_names: set = set()
        self.batch_counter = 0
    
    def _generate_name(self) -> str:
        """Generate a unique Paul name."""
        max_attempts = 100
        for _ in range(max_attempts):
            first = random.choice(FIRST_NAMES)
            suffix = random.choice(CODENAME_SUFFIXES)
            name = f"{first} {suffix}"
            if name not in self.used_names:
                self.used_names.add(name)
                return name
        # Fallback with UUID
        return f"Paul-{str(uuid.uuid4())[:4]}"
    
    def _generate_codename(self, name: str) -> str:
        """Generate a codename for the Paul."""
        prefix = random.choice(CODENAME_PREFIXES)
        # Extract suffix from name
        suffix = name.split()[-1]
        return f"{prefix}-{suffix}"
    
    def _generate_backstory(self) -> str:
        """Generate a backstory."""
        return random.choice(BACKSTORIES)
    
    def _generate_catchphrase(self) -> str:
        """Generate a catchphrase."""
        return random.choice(CATCHPHRASES)
    
    def _generate_avatar(self, trading_style: TradingStyle) -> str:
        """Generate an avatar description."""
        base = random.choice(AVATAR_DESCRIPTIONS)
        style_modifier = {
            TradingStyle.SCALPER: " with lightning-fast reflexes",
            TradingStyle.SWING_TRADER: " holding a compass for timing",
            TradingStyle.POSITION_TRADER: " with a telescope looking far ahead",
            TradingStyle.ALGORITHMIC: " made of pure code and data",
            TradingStyle.DISCRETIONARY: " with an intuitive sixth sense",
            TradingStyle.QUANTITATIVE: " surrounded by mathematical equations",
            TradingStyle.EVENT_DRIVEN: " with multiple news feeds streaming",
            TradingStyle.MOMENTUM: " riding a massive wave",
            TradingStyle.CONTRARIAN: " swimming against the current",
            TradingStyle.VALUE: " with an antique magnifying glass",
        }.get(trading_style, "")
        return base + style_modifier
    
    def _generate_specialties(self, count: Optional[int] = None) -> List[SpecialtyDomain]:
        """Generate specialties."""
        if count is None:
            count = random.randint(2, 5)
        return random.sample(list(SpecialtyDomain), min(count, len(SpecialtyDomain)))
    
    def _generate_cognitive_profile(self, trading_style: TradingStyle, 
                                    risk_profile: RiskProfile) -> Dict[str, float]:
        """Generate cognitive strengths based on style and risk."""
        base = {
            'pattern_recognition': random.uniform(0.3, 0.9),
            'fundamental_analysis': random.uniform(0.3, 0.9),
            'technical_analysis': random.uniform(0.3, 0.9),
            'sentiment_analysis': random.uniform(0.3, 0.9),
            'onchain_analysis': random.uniform(0.3, 0.9),
        }
        
        # Adjust based on trading style
        style_modifiers = {
            TradingStyle.SCALPER: {'technical_analysis': 0.3, 'pattern_recognition': 0.2},
            TradingStyle.SWING_TRADER: {'technical_analysis': 0.15, 'pattern_recognition': 0.15},
            TradingStyle.POSITION_TRADER: {'fundamental_analysis': 0.25, 'onchain_analysis': 0.1},
            TradingStyle.ALGORITHMIC: {'pattern_recognition': 0.25, 'technical_analysis': 0.15},
            TradingStyle.QUANTITATIVE: {'pattern_recognition': 0.3, 'fundamental_analysis': 0.1},
            TradingStyle.EVENT_DRIVEN: {'sentiment_analysis': 0.2, 'fundamental_analysis': 0.15},
            TradingStyle.MOMENTUM: {'technical_analysis': 0.25, 'sentiment_analysis': 0.1},
            TradingStyle.CONTRARIAN: {'sentiment_analysis': 0.3, 'fundamental_analysis': 0.1},
            TradingStyle.VALUE: {'fundamental_analysis': 0.3, 'onchain_analysis': 0.1},
        }
        
        modifiers = style_modifiers.get(trading_style, {})
        for key, boost in modifiers.items():
            base[key] = min(1.0, base[key] + boost)
        
        return base
    
    def create_persona(self, 
                       trading_style: Optional[TradingStyle] = None,
                       risk_profile: Optional[RiskProfile] = None,
                       specialties: Optional[List[SpecialtyDomain]] = None,
                       custom_traits: Optional[Dict[str, Any]] = None) -> PaulPersona:
        """Create a single Paul persona."""
        
        # Randomize if not specified
        trading_style = trading_style or random.choice(list(TradingStyle))
        risk_profile = risk_profile or random.choice(list(RiskProfile))
        specialties = specialties or self._generate_specialties()
        
        name = self._generate_name()
        codename = self._generate_codename(name)
        
        # Generate cognitive profile
        cognitive = self._generate_cognitive_profile(trading_style, risk_profile)
        
        # Generate behavioral traits
        confidence_base = random.uniform(0.3, 0.9)
        adaptability = random.uniform(0.2, 0.9)
        patience = random.uniform(0.1, 0.9)
        conviction = random.uniform(0.2, 0.9)
        
        # Risk affects some traits
        risk_val = risk_profile.value
        fomo = random.uniform(0, risk_val * 0.8)
        fear = random.uniform(0, (1 - risk_val) * 0.8)
        
        persona = PaulPersona(
            name=name,
            codename=codename,
            trading_style=trading_style,
            risk_profile=risk_profile,
            specialties=specialties,
            confidence_base=confidence_base,
            adaptability=adaptability,
            patience=patience,
            conviction=conviction,
            fomo_susceptibility=fomo,
            fear_susceptibility=fear,
            backstory=self._generate_backstory(),
            catchphrase=self._generate_catchphrase(),
            avatar_description=self._generate_avatar(trading_style),
            **cognitive
        )
        
        if custom_traits:
            for key, value in custom_traits.items():
                setattr(persona, key, value)
        
        self.generated_personas.append(persona)
        return persona
    
    def create_batch(self, count: int, 
                     style_distribution: Optional[Dict[TradingStyle, int]] = None) -> List[PaulPersona]:
        """Create a batch of Paul personas."""
        self.batch_counter += 1
        batch = []
        
        if style_distribution:
            # Create according to distribution
            for style, num in style_distribution.items():
                for _ in range(num):
                    persona = self.create_persona(trading_style=style)
                    persona.generation_batch = self.batch_counter
                    batch.append(persona)
        else:
            # Random distribution
            for _ in range(count):
                persona = self.create_persona()
                persona.generation_batch = self.batch_counter
                batch.append(persona)
        
        return batch
    
    def create_diverse_pool(self, total_count: int = 40) -> List[PaulPersona]:
        """Create a diverse pool of Pauls with balanced distribution."""
        
        # Define balanced distributions
        style_distribution = {
            TradingStyle.SWING_TRADER: int(total_count * 0.20),
            TradingStyle.POSITION_TRADER: int(total_count * 0.15),
            TradingStyle.SCALPER: int(total_count * 0.10),
            TradingStyle.MOMENTUM: int(total_count * 0.10),
            TradingStyle.CONTRARIAN: int(total_count * 0.10),
            TradingStyle.VALUE: int(total_count * 0.10),
            TradingStyle.EVENT_DRIVEN: int(total_count * 0.10),
            TradingStyle.ALGORITHMIC: int(total_count * 0.08),
            TradingStyle.QUANTITATIVE: int(total_count * 0.05),
            TradingStyle.DISCRETIONARY: int(total_count * 0.02),
        }
        
        # Adjust to hit total
        current = sum(style_distribution.values())
        if current < total_count:
            style_distribution[TradingStyle.SWING_TRADER] += (total_count - current)
        
        personas = []
        for style, count in style_distribution.items():
            for i in range(count):
                # Vary risk profiles within each style
                risk = random.choice(list(RiskProfile))
                persona = self.create_persona(trading_style=style, risk_profile=risk)
                persona.generation_batch = 1
                personas.append(persona)
        
        return personas
    
    def create_specialized_team(self, focus: SpecialtyDomain, 
                                size: int = 5) -> List[PaulPersona]:
        """Create a team specialized in a particular domain."""
        team = []
        for _ in range(size):
            specialties = [focus] + self._generate_specialties(2)
            persona = self.create_persona(specialties=specialties)
            persona.generation_batch = f"specialized_{focus.value}"
            team.append(persona)
        return team
    
    def breed_personas(self, parent1: PaulPersona, parent2: PaulPersona,
                       mutation_rate: float = 0.1) -> PaulPersona:
        """Create a new persona by combining two parents."""
        
        # Inherit traits with averaging
        child = PaulPersona(
            name=self._generate_name(),
            codename=f"Hybrid-{random.choice(CODENAME_SUFFIXES)}",
            trading_style=random.choice([parent1.trading_style, parent2.trading_style]),
            risk_profile=random.choice([parent1.risk_profile, parent2.risk_profile]),
            specialties=list(set(parent1.specialties + parent2.specialties))[:4],
            confidence_base=(parent1.confidence_base + parent2.confidence_base) / 2,
            adaptability=(parent1.adaptability + parent2.adaptability) / 2,
            patience=(parent1.patience + parent2.patience) / 2,
            conviction=(parent1.conviction + parent2.conviction) / 2,
            pattern_recognition=(parent1.pattern_recognition + parent2.pattern_recognition) / 2,
            fundamental_analysis=(parent1.fundamental_analysis + parent2.fundamental_analysis) / 2,
            technical_analysis=(parent1.technical_analysis + parent2.technical_analysis) / 2,
            sentiment_analysis=(parent1.sentiment_analysis + parent2.sentiment_analysis) / 2,
            onchain_analysis=(parent1.onchain_analysis + parent2.onchain_analysis) / 2,
            parent_personas=[parent1.id, parent2.id],
            backstory=f"Descendant of {parent1.name} and {parent2.name}. " + self._generate_backstory(),
            catchphrase=random.choice([parent1.catchphrase, parent2.catchphrase, self._generate_catchphrase()]),
        )
        
        # Apply mutations
        mutations = {}
        for trait in ['confidence_base', 'adaptability', 'patience', 'conviction',
                      'pattern_recognition', 'fundamental_analysis', 'technical_analysis',
                      'sentiment_analysis', 'onchain_analysis']:
            if random.random() < mutation_rate:
                current = getattr(child, trait)
                delta = random.uniform(-0.2, 0.2)
                mutated = max(0.1, min(1.0, current + delta))
                setattr(child, trait, mutated)
                mutations[trait] = (current, mutated)
        
        child.mutation_traits = mutations
        self.generated_personas.append(child)
        return child
    
    def export_personas(self, personas: Optional[List[PaulPersona]] = None) -> List[Dict]:
        """Export personas to dictionary format."""
        if personas is None:
            personas = self.generated_personas
        
        return [
            {
                'id': p.id,
                'name': p.name,
                'codename': p.codename,
                'trading_style': p.trading_style.value,
                'risk_profile': p.risk_profile.name,
                'risk_value': p.risk_profile.value,
                'specialties': [s.value for s in p.specialties],
                'confidence_base': p.confidence_base,
                'adaptability': p.adaptability,
                'patience': p.patience,
                'conviction': p.conviction,
                'fomo_susceptibility': p.fomo_susceptibility,
                'fear_susceptibility': p.fear_susceptibility,
                'cognitive': {
                    'pattern_recognition': p.pattern_recognition,
                    'fundamental_analysis': p.fundamental_analysis,
                    'technical_analysis': p.technical_analysis,
                    'sentiment_analysis': p.sentiment_analysis,
                    'onchain_analysis': p.onchain_analysis,
                },
                'backstory': p.backstory,
                'catchphrase': p.catchphrase,
                'avatar_description': p.avatar_description,
                'generation_batch': p.generation_batch,
                'parent_personas': p.parent_personas,
                'mutation_traits': p.mutation_traits,
            }
            for p in personas
        ]


def generate_swimming_pauls_pool(count: int = 40, seed: Optional[int] = None) -> List[Dict]:
    """
    Generate a diverse pool of Swimming Paul personas.
    
    Returns a list of persona dictionaries ready for agent instantiation.
    """
    factory = PaulPersonaFactory(seed=seed)
    personas = factory.create_diverse_pool(total_count=count)
    return factory.export_personas(personas)


# Pre-defined archetype templates for quick instantiation
PAUL_ARCHETYPES = {
    'the_veteran': {
        'trading_style': TradingStyle.POSITION_TRADER,
        'risk_profile': RiskProfile.CONSERVATIVE,
        'confidence_base': 0.8,
        'patience': 0.9,
        'conviction': 0.9,
        'specialties': [SpecialtyDomain.LAYER1, SpecialtyDomain.MACRO],
    },
    'the_degen': {
        'trading_style': TradingStyle.SCALPER,
        'risk_profile': RiskProfile.DEGEN,
        'confidence_base': 0.9,
        'adaptability': 0.9,
        'fomo_susceptibility': 0.9,
        'specialties': [SpecialtyDomain.MEMECOINS, SpecialtyDomain.DEFI],
    },
    'the_quant': {
        'trading_style': TradingStyle.QUANTITATIVE,
        'risk_profile': RiskProfile.MODERATE,
        'pattern_recognition': 0.95,
        'technical_analysis': 0.95,
        'adaptability': 0.8,
        'specialties': [SpecialtyDomain.DERIVATIVES, SpecialtyDomain.ARBITRAGE],
    },
    'the_socialite': {
        'trading_style': TradingStyle.EVENT_DRIVEN,
        'risk_profile': RiskProfile.AGGRESSIVE,
        'sentiment_analysis': 0.95,
        'adaptability': 0.9,
        'specialties': [SpecialtyDomain.NFT, SpecialtyDomain.GAMING],
    },
    'the_buildooor': {
        'trading_style': TradingStyle.VALUE,
        'risk_profile': RiskProfile.MODERATE,
        'fundamental_analysis': 0.95,
        'onchain_analysis': 0.9,
        'patience': 0.9,
        'specialties': [SpecialtyDomain.LAYER1, SpecialtyDomain.DEFI],
    },
}


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Generate 40 diverse Pauls
    factory = PaulPersonaFactory(seed=42)
    pauls = factory.create_diverse_pool(total_count=40)
    
    print(f"Generated {len(pauls)} Swimming Pauls:\n")
    
    # Group by trading style
    by_style = {}
    for p in pauls:
        style = p.trading_style.value
        if style not in by_style:
            by_style[style] = []
        by_style[style].append(p)
    
    for style, group in sorted(by_style.items()):
        print(f"\n{style.upper()} ({len(group)}):")
        for p in group[:3]:  # Show first 3 of each
            print(f"  - {p.name} ({p.codename})")
            print(f"    Risk: {p.risk_profile.name}, Confidence: {p.confidence_base:.2f}")
            print(f"    Specialties: {[s.value for s in p.specialties]}")
    
    # Show full details for one Paul
    print(f"\n\nExample Paul - {pauls[0].name}:")
    print(f"  Codename: {pauls[0].codename}")
    print(f"  Trading Style: {pauls[0].trading_style.value}")
    print(f"  Risk Profile: {pauls[0].risk_profile.name}")
    print(f"  Backstory: {pauls[0].backstory}")
    print(f"  Catchphrase: \"{pauls[0].catchphrase}\"")
    
    # Export to dict
    exported = factory.export_personas()
    print(f"\n\nExported {len(exported)} personas to dictionary format")
