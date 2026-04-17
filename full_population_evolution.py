"""
Swimming Pauls - Full Population Evolution

Integrates ALL 10,133 Pauls into the breeding system.
Generates DNA for existing Pauls and evolves the full population.

Author: Howard (H.O.W.A.R.D)
"""

import random
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import sqlite3

from genetic_breeding import GeneticBreedingEngine, PaulDNA, Genotype, calculate_fitness
from paper_trading import PaperTradingManager


class FullPopulationEvolution:
    """
    Evolves ALL Swimming Pauls (10,133+), not just a subset.
    """
    
    def __init__(self, db_path: str = "data/full_evolution.db"):
        self.db_path = Path(db_path)
        self.breeding = GeneticBreedingEngine(db_path="data/genetics.db")
        self.paper_trading = PaperTradingManager(db_path="data/paper_trading.db")
        
        self._init_db()
    
    def _init_db(self):
        """Initialize database for full population tracking."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # DNA assignments for all Pauls
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_dna (
                paul_name TEXT PRIMARY KEY,
                dna TEXT NOT NULL,
                generation INTEGER DEFAULT 1,
                parent_a TEXT,
                parent_b TEXT,
                assigned_at TEXT NOT NULL
            )
        ''')
        
        # Performance rankings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_rankings (
                paul_name TEXT PRIMARY KEY,
                fitness_score REAL,
                roi REAL,
                win_rate REAL,
                total_trades INTEGER,
                rank INTEGER,
                percentile REAL,
                elite BOOLEAN,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Evolution cycles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_cycles (
                cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                cycle_number INTEGER NOT NULL,
                total_population INTEGER,
                elite_count INTEGER,
                avg_fitness REAL,
                best_fitness REAL,
                created_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def retrofit_dna_for_all_pauls(self) -> int:
        """
        Generate DNA for all existing Pauls that don't have it.
        
        Returns:
            Number of Pauls processed
        """
        print(f"🧬 Retrofitting DNA for all Pauls...")
        
        count = 0
        
        for paul_name, portfolio in self.paper_trading.portfolios.items():
            # Check if already has DNA
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM paul_dna WHERE paul_name = ?', (paul_name,))
            exists = cursor.fetchone()
            conn.close()
            
            if exists:
                continue
            
            # Generate DNA based on portfolio characteristics
            dna = self._generate_dna_from_portfolio(portfolio)
            
            # Save DNA
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO paul_dna (paul_name, dna, generation, assigned_at)
                VALUES (?, ?, ?, ?)
            ''', (
                paul_name,
                json.dumps(dna.to_dict()),
                1,
                datetime.now().isoformat(),
            ))
            conn.commit()
            conn.close()
            
            count += 1
            
            if count % 1000 == 0:
                print(f"  Processed {count} Pauls...")
        
        print(f"✅ Retrofitted DNA for {count} Pauls")
        return count
    
    def _generate_dna_from_portfolio(self, portfolio) -> PaulDNA:
        """
        Generate plausible DNA based on portfolio behavior.
        
        This creates DNA that matches how the Paul has been trading.
        """
        # Default values
        risk = 0.5
        conviction = 0.5
        tech_fund = 0.5
        emotional = 0.5
        time_horiz = 0.5
        adapt = 0.5
        learning = 0.5
        
        # Infer from trading history if available
        if portfolio.total_trades > 0:
            # Risk tolerance from position sizes (if we tracked them)
            # For now, use random with slight bias from win rate
            win_rate = portfolio.get_win_rate()
            
            # High win rate might indicate good risk management
            if win_rate > 0.6:
                risk = random.uniform(0.6, 0.9)
            elif win_rate < 0.4:
                risk = random.uniform(0.1, 0.4)
            
            # Conviction from holding time (not tracked, use random)
            conviction = random.random()
            
            # Time horizon - can't determine from current data
            time_horiz = random.random()
            
            # Emotional stability - better win rate = more stable
            emotional = win_rate
            
            # Adaptability - random for now
            adapt = random.random()
            
            # Learning rate - random
            learning = random.random()
        
        # Random specialties (30% chance each)
        defi = random.random() if random.random() > 0.7 else 0.0
        macro = random.random() if random.random() > 0.7 else 0.0
        nft = random.random() if random.random() > 0.7 else 0.0
        
        return PaulDNA(
            risk_management=risk,
            conviction=conviction,
            technical_vs_fundamental=tech_fund,
            emotional_stability=emotional,
            time_horizon=time_horiz,
            adaptability=adapt,
            learning_rate=learning,
            defi_specialist=defi,
            macro_specialist=macro,
            nft_specialist=nft,
        )
    
    def evaluate_all_pauls(self) -> List[Tuple[str, PaulDNA, float]]:
        """
        Evaluate ALL Pauls and rank by fitness.
        
        Returns:
            List of (paul_name, dna, fitness) sorted by fitness
        """
        print(f"\n📊 Evaluating ALL {len(self.paper_trading.portfolios)} Pauls...")
        
        results = []
        
        # Load all DNAs
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT paul_name, dna FROM paul_dna')
        dna_data = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
        conn.close()
        
        for paul_name, portfolio in self.paper_trading.portfolios.items():
            # Get DNA
            dna_dict = dna_data.get(paul_name)
            if not dna_dict:
                continue
            
            dna = PaulDNA.from_dict(dna_dict)
            
            # Calculate fitness
            if portfolio.total_trades == 0:
                fitness = 0.0
            else:
                portfolio_data = {
                    'roi': portfolio.get_roi(),
                    'win_rate': portfolio.get_win_rate(),
                    'max_drawdown': portfolio.max_drawdown,
                    'total_trades': portfolio.total_trades,
                }
                fitness = calculate_fitness(portfolio_data)
            
            results.append((paul_name, dna, fitness))
        
        # Sort by fitness
        results.sort(key=lambda x: x[2], reverse=True)
        
        # Save rankings
        self._save_rankings(results)
        
        print(f"✅ Evaluated {len(results)} Pauls")
        
        if results:
            print(f"\n🏆 Top Performer: {results[0][0]} (Fitness: {results[0][2]:.2f})")
            print(f"   DNA: {results[0][1].describe()}")
            print(f"📈 Average Fitness: {sum(r[2] for r in results) / len(results):.2f}")
            print(f"📉 Bottom Performer: {results[-1][0]} (Fitness: {results[-1][2]:.2f})")
        
        return results
    
    def _save_rankings(self, results: List[Tuple[str, PaulDNA, float]]):
        """Save performance rankings to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        total = len(results)
        
        for i, (paul_name, dna, fitness) in enumerate(results):
            rank = i + 1
            percentile = (total - rank) / total * 100
            elite = percentile >= 90  # Top 10% are elite
            
            # Get portfolio data
            portfolio = self.paper_trading.portfolios.get(paul_name)
            if portfolio:
                roi = portfolio.get_roi()
                win_rate = portfolio.get_win_rate()
                total_trades = portfolio.total_trades
            else:
                roi = 0
                win_rate = 0
                total_trades = 0
            
            cursor.execute('''
                INSERT OR REPLACE INTO performance_rankings
                (paul_name, fitness_score, roi, win_rate, total_trades, 
                 rank, percentile, elite, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paul_name, fitness, roi, win_rate, total_trades,
                rank, percentile, elite, datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def get_elite_pauls(self, top_percent: float = 10.0) -> List[Tuple[str, PaulDNA, float]]:
        """
        Get elite Pauls (top N% by fitness).
        
        Args:
            top_percent: Percentage to consider elite (default 10%)
        
        Returns:
            List of (name, dna, fitness) for elite Pauls
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT paul_name, fitness_score FROM performance_rankings
            WHERE elite = 1
            ORDER BY fitness_score DESC
        ''')
        
        elite_names = [(row[0], row[1]) for row in cursor.fetchall()]
        conn.close()
        
        # Load DNAs
        elite = []
        for name, fitness in elite_names:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT dna FROM paul_dna WHERE paul_name = ?', (name,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                dna = PaulDNA.from_dict(json.loads(row[0]))
                elite.append((name, dna, fitness))
        
        return elite
    
    def breed_next_generation(self, elite: List[Tuple[str, PaulDNA, float]]) -> int:
        """
        Breed next generation from elite Pauls.
        
        Creates new Pauls by breeding elite performers.
        
        Returns:
            Number of new Pauls created
        """
        print(f"\n🧬 Breeding next generation from {len(elite)} elite Pauls...")
        
        # Create genotypes from elite
        elite_genotypes = []
        for name, dna, fitness in elite:
            genotype = Genotype(dna=dna, generation=1)  # Will update
            elite_genotypes.append((name, genotype, fitness))
        
        # Breed new Pauls
        new_count = 0
        
        # We'll create new Pauls equal to 10% of population
        target_new = max(100, int(len(self.paper_trading.portfolios) * 0.10))
        
        for i in range(target_new):
            # Select two parents
            parent_a = random.choice(elite_genotypes)
            parent_b = random.choice(elite_genotypes)
            
            # Breed
            child_dna = self.breeding.crossover(parent_a[1].dna, parent_b[1].dna)
            
            # Mutate
            mutations = []
            for trait_name in child_dna.to_dict().keys():
                old_value = getattr(child_dna, trait_name)
                new_value, did_mutate = self.breeding.mutate_trait(old_value)
                setattr(child_dna, trait_name, new_value)
                if did_mutate:
                    mutations.append(f"{trait_name}:{old_value:.2f}->{new_value:.2f}")
            
            # Create new Paul
            new_name = f"Paul-Evolved-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
            
            # Save DNA
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO paul_dna (paul_name, dna, generation, parent_a, parent_b, assigned_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                new_name,
                json.dumps(child_dna.to_dict()),
                2,  # Generation 2
                parent_a[0],
                parent_b[0],
                datetime.now().isoformat(),
            ))
            conn.commit()
            conn.close()
            
            # Create paper trading portfolio
            self.paper_trading.create_portfolio(new_name, initial_balance=10000.0, enabled=True)
            
            new_count += 1
        
        print(f"✅ Created {new_count} new evolved Pauls")
        return new_count
    
    def get_population_stats(self) -> Dict:
        """Get statistics for the full population."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total with DNA
        cursor.execute('SELECT COUNT(*) FROM paul_dna')
        total_with_dna = cursor.fetchone()[0]
        
        # Total evaluated
        cursor.execute('SELECT COUNT(*) FROM performance_rankings')
        total_evaluated = cursor.fetchone()[0]
        
        # Elite count
        cursor.execute('SELECT COUNT(*) FROM performance_rankings WHERE elite = 1')
        elite_count = cursor.fetchone()[0]
        
        # Fitness stats
        cursor.execute('''
            SELECT AVG(fitness_score), MAX(fitness_score), MIN(fitness_score)
            FROM performance_rankings
        ''')
        avg_fit, max_fit, min_fit = cursor.fetchone()
        
        # Top 10
        cursor.execute('''
            SELECT paul_name, fitness_score, roi, win_rate
            FROM performance_rankings
            ORDER BY rank ASC
            LIMIT 10
        ''')
        top_10 = []
        for row in cursor.fetchall():
            top_10.append({
                'name': row[0],
                'fitness': row[1],
                'roi': row[2],
                'win_rate': row[3],
            })
        
        conn.close()
        
        return {
            'total_population': len(self.paper_trading.portfolios),
            'with_dna': total_with_dna,
            'evaluated': total_evaluated,
            'elite_count': elite_count,
            'avg_fitness': avg_fit or 0,
            'max_fitness': max_fit or 0,
            'min_fitness': min_fit or 0,
            'top_10': top_10,
        }


# CLI Interface
def full_population_cli():
    """Command-line interface for full population evolution."""
    import sys
    
    evolution = FullPopulationEvolution()
    
    if len(sys.argv) < 2:
        print("Full Population Evolution System")
        print("Commands:")
        print("  retrofit                - Generate DNA for all existing Pauls")
        print("  evaluate                - Evaluate ALL Pauls")
        print("  elite                   - Show elite (top 10%) Pauls")
        print("  breed                   - Breed next generation from elite")
        print("  stats                   - Show population statistics")
        print("  full                    - Run full cycle: retrofit → evaluate → stats")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "retrofit":
        count = evolution.retrofit_dna_for_all_pauls()
        print(f"\n✅ Retrofitted {count} Pauls with DNA")
    
    elif command == "evaluate":
        results = evolution.evaluate_all_pauls()
        print(f"\n✅ Evaluated {len(results)} Pauls")
    
    elif command == "elite":
        elite = evolution.get_elite_pauls(10.0)
        print(f"\n🏆 Elite Pauls (Top 10%): {len(elite)}")
        for i, (name, dna, fitness) in enumerate(elite[:20], 1):
            print(f"{i}. {name}")
            print(f"   Fitness: {fitness:.2f}")
            print(f"   {dna.describe()}")
            print()
    
    elif command == "breed":
        elite = evolution.get_elite_pauls(10.0)
        if len(elite) < 2:
            print("❌ Need at least 2 elite Pauls to breed")
            print("   Run 'evaluate' first to identify elite")
            sys.exit(1)
        
        new_count = evolution.breed_next_generation(elite)
        print(f"\n✅ Created {new_count} new evolved Pauls")
    
    elif command == "stats":
        stats = evolution.get_population_stats()
        print("\n📊 Full Population Statistics")
        print("=" * 60)
        print(f"Total Pauls: {stats['total_population']:,}")
        print(f"With DNA: {stats['with_dna']:,}")
        print(f"Evaluated: {stats['evaluated']:,}")
        print(f"Elite (top 10%): {stats['elite_count']:,}")
        print(f"\nFitness Stats:")
        print(f"  Average: {stats['avg_fitness']:.2f}")
        print(f"  Best: {stats['max_fitness']:.2f}")
        print(f"  Worst: {stats['min_fitness']:.2f}")
        print(f"\nTop 10 Pauls:")
        for i, paul in enumerate(stats['top_10'], 1):
            print(f"  {i}. {paul['name']} (Fitness: {paul['fitness']:.2f})")
    
    elif command == "full":
        print("\n" + "=" * 60)
        print("🚀 FULL POPULATION EVOLUTION CYCLE")
        print("=" * 60)
        
        # Step 1: Retrofit
        count = evolution.retrofit_dna_for_all_pauls()
        
        # Step 2: Evaluate
        results = evolution.evaluate_all_pauls()
        
        # Step 3: Stats
        stats = evolution.get_population_stats()
        
        print("\n" + "=" * 60)
        print("✅ FULL CYCLE COMPLETE")
        print("=" * 60)
        print(f"Population: {stats['total_population']:,} Pauls")
        print(f"Evaluated: {stats['evaluated']:,} Pauls")
        print(f"Elite: {stats['elite_count']:,} Pauls")
        print(f"Best Fitness: {stats['max_fitness']:.2f}")


if __name__ == "__main__":
    full_population_cli()
