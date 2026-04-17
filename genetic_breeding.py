"""
Swimming Pauls - Genetic Breeding System

Evolves Paul personas using genetic algorithms.
10-trait DNA: 7 core + 3 specialty

Author: Howard (H.O.W.A.R.D)
"""

import random
import json
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from pathlib import Path
import sqlite3


@dataclass
class PaulDNA:
    """
    Genetic code for a Swimming Paul.
    
    7 Core Traits (0.0 to 1.0):
    - risk_management: 0=reckless, 1=disciplined
    - conviction: 0=weak hands, 1=diamond hands  
    - technical_vs_fundamental: 0=100% fundamental, 1=100% technical
    - emotional_stability: 0=panic/FOMO, 1=stoic/robotic
    - time_horizon: 0=scalper (minutes), 1=investor (months)
    - adaptability: 0=one strategy, 1=chameleon
    - learning_rate: 0=slow learner, 1=fast learner
    
    3 Specialty Genes (0.0 to 1.0 each):
    - defi_specialist, macro_specialist, nft_specialist
    """
    
    # Core Traits
    risk_management: float = 0.5
    conviction: float = 0.5
    technical_vs_fundamental: float = 0.5
    emotional_stability: float = 0.5
    time_horizon: float = 0.5
    adaptability: float = 0.5
    learning_rate: float = 0.5
    
    # Specialty Genes
    defi_specialist: float = 0.0
    macro_specialist: float = 0.0
    nft_specialist: float = 0.0
    
    def __post_init__(self):
        """Ensure all traits are clamped to 0-1 range."""
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            setattr(self, field_name, max(0.0, min(1.0, value)))
    
    def to_dict(self) -> Dict:
        """Convert DNA to dictionary."""
        return {
            'risk_management': self.risk_management,
            'conviction': self.conviction,
            'technical_vs_fundamental': self.technical_vs_fundamental,
            'emotional_stability': self.emotional_stability,
            'time_horizon': self.time_horizon,
            'adaptability': self.adaptability,
            'learning_rate': self.learning_rate,
            'defi_specialist': self.defi_specialist,
            'macro_specialist': self.macro_specialist,
            'nft_specialist': self.nft_specialist,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'PaulDNA':
        """Create DNA from dictionary."""
        return cls(**data)
    
    def get_core_traits(self) -> Dict[str, float]:
        """Get the 7 core traits."""
        return {
            'risk_management': self.risk_management,
            'conviction': self.conviction,
            'technical_vs_fundamental': self.technical_vs_fundamental,
            'emotional_stability': self.emotional_stability,
            'time_horizon': self.time_horizon,
            'adaptability': self.adaptability,
            'learning_rate': self.learning_rate,
        }
    
    def get_specialty_traits(self) -> Dict[str, float]:
        """Get the 3 specialty traits."""
        return {
            'defi_specialist': self.defi_specialist,
            'macro_specialist': self.macro_specialist,
            'nft_specialist': self.nft_specialist,
        }
    
    def get_dominant_specialty(self) -> Optional[str]:
        """Get the dominant specialty (if any > 0.6)."""
        specialties = self.get_specialty_traits()
        max_specialty = max(specialties, key=specialties.get)
        if specialties[max_specialty] > 0.6:
            return max_specialty.replace('_specialist', '')
        return None
    
    def describe(self) -> str:
        """Generate human-readable description of this DNA."""
        parts = []
        
        # Risk style
        if self.risk_management > 0.7:
            parts.append("disciplined risk manager")
        elif self.risk_management < 0.3:
            parts.append("risk-tolerant")
        
        # Conviction
        if self.conviction > 0.7:
            parts.append("strong conviction")
        elif self.conviction < 0.3:
            parts.append("flexible")
        
        # Analysis style
        if self.technical_vs_fundamental > 0.7:
            parts.append("technical analyst")
        elif self.technical_vs_fundamental < 0.3:
            parts.append("fundamental investor")
        else:
            parts.append("balanced analyst")
        
        # Emotional
        if self.emotional_stability > 0.7:
            parts.append("emotionally stable")
        elif self.emotional_stability < 0.3:
            parts.append("reactive")
        
        # Time horizon
        if self.time_horizon < 0.3:
            parts.append("scalper")
        elif self.time_horizon > 0.7:
            parts.append("long-term investor")
        else:
            parts.append("swing trader")
        
        # Specialty
        specialty = self.get_dominant_specialty()
        if specialty:
            parts.append(f"{specialty} specialist")
        
        return ", ".join(parts) if parts else "balanced generalist"


@dataclass
class Genotype:
    """
    Complete genetic profile for a Paul including lineage.
    """
    dna: PaulDNA
    generation: int = 1
    parent_a: Optional[str] = None
    parent_b: Optional[str] = None
    mutations: List[str] = field(default_factory=list)
    birth_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        return {
            'dna': self.dna.to_dict(),
            'generation': self.generation,
            'parent_a': self.parent_a,
            'parent_b': self.parent_b,
            'mutations': self.mutations,
            'birth_date': self.birth_date.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Genotype':
        return cls(
            dna=PaulDNA.from_dict(data['dna']),
            generation=data['generation'],
            parent_a=data.get('parent_a'),
            parent_b=data.get('parent_b'),
            mutations=data.get('mutations', []),
            birth_date=datetime.fromisoformat(data['birth_date']),
        )


class GeneticBreedingEngine:
    """
    Genetic algorithm engine for evolving Swimming Pauls.
    """
    
    def __init__(self, 
                 mutation_rate: float = 0.15,
                 mutation_strength: float = 0.20,
                 crossover_rate: float = 0.70,
                 elite_percentage: float = 0.10,
                 db_path: str = "data/genetics.db"):
        """
        Initialize breeding engine.
        
        Args:
            mutation_rate: Probability of mutation per trait (15%)
            mutation_strength: Max magnitude of mutation (±20%)
            crossover_rate: Probability of crossover vs clone (70%)
            elite_percentage: Top % that get to breed (10%)
            db_path: SQLite database for lineage tracking
        """
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.crossover_rate = crossover_rate
        self.elite_percentage = elite_percentage
        self.db_path = Path(db_path)
        
        self._init_db()
    
    def _init_db(self):
        """Initialize genetics database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Genotypes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS genotypes (
                paul_id TEXT PRIMARY KEY,
                paul_name TEXT NOT NULL,
                generation INTEGER NOT NULL,
                dna TEXT NOT NULL,
                parent_a TEXT,
                parent_b TEXT,
                mutations TEXT,
                birth_date TEXT NOT NULL,
                performance_score REAL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Lineage table for family trees
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lineage (
                child_id TEXT NOT NULL,
                parent_id TEXT NOT NULL,
                generation INTEGER NOT NULL,
                contribution REAL,
                PRIMARY KEY (child_id, parent_id)
            )
        ''')
        
        # Generations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generations (
                generation INTEGER PRIMARY KEY,
                population_size INTEGER,
                avg_fitness REAL,
                best_fitness REAL,
                avg_dna TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_random_dna(self) -> PaulDNA:
        """Generate completely random DNA."""
        return PaulDNA(
            risk_management=random.random(),
            conviction=random.random(),
            technical_vs_fundamental=random.random(),
            emotional_stability=random.random(),
            time_horizon=random.random(),
            adaptability=random.random(),
            learning_rate=random.random(),
            defi_specialist=random.random() if random.random() > 0.7 else 0.0,
            macro_specialist=random.random() if random.random() > 0.7 else 0.0,
            nft_specialist=random.random() if random.random() > 0.7 else 0.0,
        )
    
    def mutate_trait(self, value: float) -> Tuple[float, bool]:
        """
        Mutate a single trait.
        
        Returns:
            (new_value, did_mutate)
        """
        if random.random() > self.mutation_rate:
            return value, False
        
        # Gaussian mutation centered on current value
        mutation = random.gauss(0, self.mutation_strength)
        new_value = value + mutation
        
        # Clamp to 0-1
        new_value = max(0.0, min(1.0, new_value))
        
        return new_value, True
    
    def crossover(self, parent_a: PaulDNA, parent_b: PaulDNA) -> PaulDNA:
        """
        Perform genetic crossover between two parents.
        
        Uses weighted average with some traits from each parent.
        """
        child_traits = {}
        
        for trait_name in parent_a.to_dict().keys():
            value_a = getattr(parent_a, trait_name)
            value_b = getattr(parent_b, trait_name)
            
            # Weighted average (random weight per trait)
            weight = random.random()
            child_traits[trait_name] = weight * value_a + (1 - weight) * value_b
        
        return PaulDNA(**child_traits)
    
    def breed(self, 
              parent_a: Tuple[str, Genotype], 
              parent_b: Tuple[str, Genotype]) -> Tuple[str, Genotype]:
        """
        Breed two Pauls to create offspring.
        
        Args:
            parent_a: (name, genotype) of first parent
            parent_b: (name, genotype) of second parent
        
        Returns:
            (child_name, child_genotype)
        """
        name_a, geno_a = parent_a
        name_b, geno_b = parent_b
        
        # Determine if crossover happens
        if random.random() < self.crossover_rate:
            # Crossover: blend DNA
            child_dna = self.crossover(geno_a.dna, geno_b.dna)
        else:
            # Clone: pick one parent randomly
            child_dna = PaulDNA(**(geno_a.dna.to_dict() if random.random() < 0.5 else geno_b.dna.to_dict()))
        
        # Apply mutations
        mutations = []
        for trait_name in child_dna.to_dict().keys():
            old_value = getattr(child_dna, trait_name)
            new_value, did_mutate = self.mutate_trait(old_value)
            setattr(child_dna, trait_name, new_value)
            
            if did_mutate:
                mutations.append(f"{trait_name}:{old_value:.2f}->{new_value:.2f}")
        
        # Create child genotype
        child_generation = max(geno_a.generation, geno_b.generation) + 1
        child_genotype = Genotype(
            dna=child_dna,
            generation=child_generation,
            parent_a=name_a,
            parent_b=name_b,
            mutations=mutations,
        )
        
        # Generate child name
        child_name = f"Paul-{child_generation}-{uuid.uuid4().hex[:6]}"
        
        return child_name, child_genotype
    
    def select_elite(self, 
                     population: List[Tuple[str, Genotype, float]], 
                     n: int) -> List[Tuple[str, Genotype]]:
        """
        Select top performers for breeding.
        
        Args:
            population: List of (name, genotype, fitness_score)
            n: Number to select
        
        Returns:
            List of (name, genotype) for breeding
        """
        # Sort by fitness score (descending)
        sorted_pop = sorted(population, key=lambda x: x[2], reverse=True)
        
        # Take top n
        elite = [(name, genotype) for name, genotype, _ in sorted_pop[:n]]
        
        return elite
    
    def create_next_generation(self, 
                               current_population: List[Tuple[str, Genotype, float]],
                               target_size: int = 100) -> List[Tuple[str, Genotype]]:
        """
        Create next generation through breeding.
        
        Args:
            current_population: List of (name, genotype, fitness_score)
            target_size: Desired population size
        
        Returns:
            List of (name, genotype) for new generation
        """
        # Select elite breeders
        elite_count = max(2, int(len(current_population) * self.elite_percentage))
        elite = self.select_elite(current_population, elite_count)
        
        if len(elite) < 2:
            raise ValueError("Need at least 2 elite Pauls to breed")
        
        # Create new generation
        new_generation = []
        
        # Keep elite in next generation (elitism)
        new_generation.extend(elite)
        
        # Breed until we reach target size
        while len(new_generation) < target_size:
            # Select two parents (can be same parent twice)
            parent_a = random.choice(elite)
            parent_b = random.choice(elite)
            
            # Breed
            child_name, child_genotype = self.breed(parent_a, parent_b)
            new_generation.append((child_name, child_genotype))
        
        return new_generation[:target_size]
    
    def save_genotype(self, paul_name: str, genotype: Genotype, performance_score: float = None):
        """Save genotype to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO genotypes 
            (paul_id, paul_name, generation, dna, parent_a, parent_b, mutations, birth_date, performance_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            str(uuid.uuid4())[:8],
            paul_name,
            genotype.generation,
            json.dumps(genotype.dna.to_dict()),
            genotype.parent_a,
            genotype.parent_b,
            json.dumps(genotype.mutations),
            genotype.birth_date.isoformat(),
            performance_score,
            datetime.now().isoformat(),
        ))
        
        # Save lineage
        if genotype.parent_a:
            cursor.execute('''
                INSERT OR REPLACE INTO lineage (child_id, parent_id, generation, contribution)
                VALUES (?, ?, ?, ?)
            ''', (paul_name, genotype.parent_a, genotype.generation, 0.5))
        
        if genotype.parent_b:
            cursor.execute('''
                INSERT OR REPLACE INTO lineage (child_id, parent_id, generation, contribution)
                VALUES (?, ?, ?, ?)
            ''', (paul_name, genotype.parent_b, genotype.generation, 0.5))
        
        conn.commit()
        conn.close()
    
    def get_lineage(self, paul_name: str, generations_back: int = 3) -> Dict:
        """Get family tree for a Paul."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        lineage = {
            'name': paul_name,
            'ancestors': [],
            'descendants': [],
        }
        
        # Get ancestors
        cursor.execute('''
            SELECT g.paul_name, g.generation, g.parent_a, g.parent_b
            FROM genotypes g
            JOIN lineage l ON g.paul_name = l.parent_id
            WHERE l.child_id = ?
            ORDER BY g.generation DESC
            LIMIT ?
        ''', (paul_name, generations_back))
        
        for row in cursor.fetchall():
            lineage['ancestors'].append({
                'name': row[0],
                'generation': row[1],
                'parents': [row[2], row[3]] if row[2] or row[3] else [],
            })
        
        conn.close()
        return lineage
    
    def get_generation_stats(self, generation: int) -> Dict:
        """Get statistics for a generation."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT dna, performance_score FROM genotypes WHERE generation = ?
        ''', (generation,))
        
        rows = cursor.fetchall()
        if not rows:
            return {}
        
        # Calculate average DNA
        dna_sums = {k: 0.0 for k in PaulDNA().to_dict().keys()}
        scores = []
        
        for row in rows:
            dna = json.loads(row[0])
            for k, v in dna.items():
                dna_sums[k] += v
            if row[1]:
                scores.append(row[1])
        
        count = len(rows)
        avg_dna = {k: v / count for k, v in dna_sums.items()}
        
        stats = {
            'generation': generation,
            'population_size': count,
            'avg_dna': avg_dna,
        }
        
        if scores:
            stats['avg_fitness'] = sum(scores) / len(scores)
            stats['best_fitness'] = max(scores)
            stats['worst_fitness'] = min(scores)
        
        conn.close()
        return stats


def calculate_fitness(paper_portfolio) -> float:
    """
    Calculate fitness score from paper trading performance.
    
    Combines:
    - ROI (40%)
    - Win rate (30%)
    - Risk-adjusted (Sharpe proxy) (20%)
    - Consistency (low drawdown) (10%)
    """
    roi = paper_portfolio.get('roi', 0)
    win_rate = paper_portfolio.get('win_rate', 0)
    max_drawdown = paper_portfolio.get('max_drawdown', 0)
    total_trades = paper_portfolio.get('total_trades', 0)
    
    # Penalize if too few trades
    if total_trades < 10:
        return 0.0
    
    # Calculate components
    roi_score = max(0, roi) * 100  # Convert to percentage points
    win_rate_score = win_rate * 100
    risk_score = max(0, 1 - max_drawdown) * 100
    
    # Weighted combination
    fitness = (
        roi_score * 0.40 +
        win_rate_score * 0.30 +
        risk_score * 0.20 +
        (100 if total_trades >= 50 else total_trades * 2) * 0.10
    )
    
    return max(0, fitness)


# CLI Interface
def breeding_cli():
    """Command-line interface for breeding system."""
    import sys
    
    engine = GeneticBreedingEngine()
    
    if len(sys.argv) < 2:
        print("Genetic Breeding System")
        print("Commands:")
        print("  random <n>              - Generate n random Pauls")
        print("  breed <gen> <n>         - Create generation from parents")
        print("  stats <gen>             - Show generation statistics")
        print("  lineage <name>          - Show family tree")
        print("  describe <dna_json>     - Describe DNA traits")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "random" and len(sys.argv) > 2:
        n = int(sys.argv[2])
        print(f"\n🧬 Generating {n} Random Pauls\n")
        for i in range(n):
            dna = engine.create_random_dna()
            genotype = Genotype(dna=dna, generation=1)
            name = f"Paul-Gen1-{uuid.uuid4().hex[:6]}"
            engine.save_genotype(name, genotype)
            print(f"  {i+1}. {name}")
            print(f"     {dna.describe()}")
            print()
    
    elif command == "describe" and len(sys.argv) > 2:
        dna_json = sys.argv[2]
        dna = PaulDNA.from_dict(json.loads(dna_json))
        print(f"\n🧬 DNA Description\n")
        print(f"  Traits: {dna.to_dict()}")
        print(f"  Description: {dna.describe()}")
        print(f"  Dominant Specialty: {dna.get_dominant_specialty() or 'None'}")
    
    elif command == "stats" and len(sys.argv) > 2:
        gen = int(sys.argv[2])
        stats = engine.get_generation_stats(gen)
        if stats:
            print(f"\n📊 Generation {gen} Statistics\n")
            print(f"  Population: {stats['population_size']}")
            if 'avg_fitness' in stats:
                print(f"  Avg Fitness: {stats['avg_fitness']:.2f}")
                print(f"  Best Fitness: {stats['best_fitness']:.2f}")
            print(f"\n  Average DNA:")
            for trait, value in stats['avg_dna'].items():
                print(f"    {trait}: {value:.3f}")
        else:
            print(f"No data for generation {gen}")
    
    elif command == "lineage" and len(sys.argv) > 2:
        name = sys.argv[2]
        lineage = engine.get_lineage(name)
        print(f"\n🌳 Lineage for {name}\n")
        if lineage['ancestors']:
            print("  Ancestors:")
            for ancestor in lineage['ancestors']:
                print(f"    Gen {ancestor['generation']}: {ancestor['name']}")
        else:
            print("  No ancestors (Gen 1)")


if __name__ == "__main__":
    breeding_cli()
