"""
Swimming Pauls - Curated Population Evolution

Works with the 1,000 curated Pauls from PAULS.md
Not the 10,233 auto-generated ones.

Author: Howard (H.O.W.A.R.D)
"""

import random
import json
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import sqlite3

from genetic_breeding import GeneticBreedingEngine, PaulDNA, Genotype, calculate_fitness
from paper_trading import PaperTradingManager


class CuratedPaulEvolution:
    """
    Evolves only the 1,000 curated Pauls from the directory.
    """
    
    def __init__(self, db_path: str = "data/curated_evolution.db"):
        self.db_path = Path(db_path)
        self.breeding = GeneticBreedingEngine(db_path="data/genetics.db")
        self.paper_trading = PaperTradingManager(db_path="data/paper_trading.db")
        
        self.curated_pauls = self._load_curated_pauls()
        
        self._init_db()
    
    def _load_curated_pauls(self) -> List[str]:
        """Load the list of 1,000 curated Paul names from PAULS files."""
        pauls = []
        
        # Try to load from PAULS.md (first 160)
        try:
            with open('PAULS.md', 'r') as f:
                content = f.read()
                # Extract Paul names (format: **Name Paul**)
                matches = re.findall(r'\*\*([A-Za-z\s]+Paul)\*\*', content)
                pauls.extend(matches)
        except FileNotFoundError:
            pass
        
        # Try to load from PAULS_EXTENDED.md (rest)
        try:
            with open('PAULS_EXTENDED.md', 'r') as f:
                content = f.read()
                # Extract from table format: | # | **Name Paul** | ...
                matches = re.findall(r'\|\s*\d+\s*\|\s*\*\*([^|]+Paul)\*\*', content)
                pauls.extend(matches)
        except FileNotFoundError:
            pass
        
        # Clean up: remove duplicates, strip whitespace, filter valid
        pauls = list(set(pauls))
        pauls = [p.strip() for p in pauls]
        pauls = [p for p in pauls if p.endswith(' Paul') and len(p) > 5]
        pauls = sorted(pauls)
        
        print(f"📚 Loaded {len(pauls)} curated Pauls from directory")
        return pauls
    
    def _init_db(self):
        """Initialize database for curated Pauls."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Curated Paul DNA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS curated_dna (
                paul_name TEXT PRIMARY KEY,
                dna TEXT NOT NULL,
                archetype TEXT,
                generation INTEGER DEFAULT 1,
                parent_a TEXT,
                parent_b TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Performance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS curated_performance (
                paul_name TEXT PRIMARY KEY,
                fitness_score REAL,
                roi REAL,
                win_rate REAL,
                total_trades INTEGER,
                rank INTEGER,
                elite BOOLEAN,
                updated_at TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def assign_dna_to_curated(self) -> int:
        """
        Assign DNA to all curated Pauls based on their archetype.
        
        Returns:
            Number of Pauls processed
        """
        print(f"🧬 Assigning DNA to {len(self.curated_pauls)} curated Pauls...")
        
        count = 0
        
        for paul_name in self.curated_pauls:
            # Check if already has DNA
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM curated_dna WHERE paul_name = ?', (paul_name,))
            exists = cursor.fetchone()
            conn.close()
            
            if exists:
                continue
            
            # Generate DNA based on Paul name/archetype
            dna = self._generate_dna_from_name(paul_name)
            archetype = self._get_archetype(paul_name)
            
            # Save DNA
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO curated_dna (paul_name, dna, archetype, generation, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                paul_name,
                json.dumps(dna.to_dict()),
                archetype,
                1,
                datetime.now().isoformat(),
            ))
            conn.commit()
            conn.close()
            
            # Ensure paper trading portfolio exists
            if paul_name not in self.paper_trading.portfolios:
                self.paper_trading.create_portfolio(paul_name, initial_balance=10000.0, enabled=True)
            
            count += 1
            
            if count % 100 == 0:
                print(f"  Processed {count}/{len(self.curated_pauls)}...")
        
        print(f"✅ Assigned DNA to {count} curated Pauls")
        return count
    
    def _generate_dna_from_name(self, name: str) -> PaulDNA:
        """Generate appropriate DNA based on Paul name."""
        name_lower = name.lower()
        
        # Default values
        risk = 0.5
        conviction = 0.5
        tech_fund = 0.5
        emotional = 0.5
        time_horiz = 0.5
        adapt = 0.5
        learning = 0.5
        defi = 0.0
        macro = 0.0
        nft = 0.0
        
        # Adjust based on name patterns
        if any(word in name_lower for word in ['conservative', 'cautious', 'safe', 'steady']):
            risk = 0.2
            emotional = 0.7
        
        if any(word in name_lower for word in ['aggressive', 'degen', 'yolo', 'diamond']):
            risk = 0.8
            conviction = 0.9
            emotional = 0.3
        
        if any(word in name_lower for word in ['technical', 'chart', 'pattern']):
            tech_fund = 0.8
        
        if any(word in name_lower for word in ['fundamental', 'value', 'research']):
            tech_fund = 0.2
        
        if any(word in name_lower for word in ['scalp', 'day', 'quick']):
            time_horiz = 0.2
        
        if any(word in name_lower for word in ['hold', 'long', 'investor']):
            time_horiz = 0.8
        
        if any(word in name_lower for word in ['defi', 'defi']):
            defi = 0.8
        
        if any(word in name_lower for word in ['macro', 'fed', 'economy']):
            macro = 0.8
        
        if any(word in name_lower for word in ['nft', 'art', 'jpeg']):
            nft = 0.8
        
        if any(word in name_lower for word in ['adapt', 'flex', 'pivot']):
            adapt = 0.8
        
        if any(word in name_lower for word in ['learn', 'student', 'growth']):
            learning = 0.8
        
        # Add some randomness so similar names aren't identical
        risk = max(0, min(1, risk + random.uniform(-0.1, 0.1)))
        conviction = max(0, min(1, conviction + random.uniform(-0.1, 0.1)))
        emotional = max(0, min(1, emotional + random.uniform(-0.1, 0.1)))
        
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
    
    def _get_archetype(self, name: str) -> str:
        """Determine archetype from Paul name."""
        name_lower = name.lower()
        
        if 'conservative' in name_lower:
            return 'conservative'
        elif 'aggressive' in name_lower or 'degen' in name_lower:
            return 'aggressive'
        elif 'technical' in name_lower:
            return 'technical'
        elif 'fundamental' in name_lower:
            return 'fundamental'
        elif 'defi' in name_lower:
            return 'defi_specialist'
        elif 'macro' in name_lower:
            return 'macro_specialist'
        elif 'nft' in name_lower:
            return 'nft_specialist'
        else:
            return 'balanced'
    
    def evaluate_curated_pauls(self) -> List[Tuple[str, PaulDNA, float]]:
        """
        Evaluate all curated Pauls with paper trading data.
        
        Returns:
            List of (name, dna, fitness) sorted by fitness
        """
        print(f"\n📊 Evaluating {len(self.curated_pauls)} curated Pauls...")
        
        results = []
        
        # Load all DNAs
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT paul_name, dna FROM curated_dna')
        dna_data = {row[0]: json.loads(row[1]) for row in cursor.fetchall()}
        conn.close()
        
        for paul_name in self.curated_pauls:
            # Get DNA
            dna_dict = dna_data.get(paul_name)
            if not dna_dict:
                continue
            
            dna = PaulDNA.from_dict(dna_dict)
            
            # Get paper trading performance
            portfolio = self.paper_trading.portfolios.get(paul_name)
            if portfolio and portfolio.total_trades > 0:
                portfolio_data = {
                    'roi': portfolio.get_roi(),
                    'win_rate': portfolio.get_win_rate(),
                    'max_drawdown': portfolio.max_drawdown,
                    'total_trades': portfolio.total_trades,
                }
                fitness = calculate_fitness(portfolio_data)
            else:
                fitness = 0.0  # No trades yet
            
            results.append((paul_name, dna, fitness))
        
        # Sort by fitness
        results.sort(key=lambda x: x[2], reverse=True)
        
        # Save rankings
        self._save_rankings(results)
        
        print(f"✅ Evaluated {len(results)} curated Pauls")
        
        if results:
            print(f"\n🏆 Top Performer: {results[0][0]} (Fitness: {results[0][2]:.2f})")
            print(f"   DNA: {results[0][1].describe()}")
            print(f"📈 Average Fitness: {sum(r[2] for r in results) / len(results):.2f}")
        
        return results
    
    def _save_rankings(self, results: List[Tuple[str, PaulDNA, float]]):
        """Save performance rankings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        total = len(results)
        
        for i, (paul_name, dna, fitness) in enumerate(results):
            rank = i + 1
            elite = rank <= total * 0.10  # Top 10% are elite
            
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
                INSERT OR REPLACE INTO curated_performance
                (paul_name, fitness_score, roi, win_rate, total_trades, rank, elite, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                paul_name, fitness, roi, win_rate, total_trades,
                rank, elite, datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def get_elite_curated(self, top_n: int = 100) -> List[Tuple[str, PaulDNA, float]]:
        """Get top N curated Pauls by fitness."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT paul_name, fitness_score FROM curated_performance
            ORDER BY rank ASC
            LIMIT ?
        ''', (top_n,))
        
        elite_data = [(row[0], row[1]) for row in cursor.fetchall()]
        conn.close()
        
        # Load DNAs
        elite = []
        for name, fitness in elite_data:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT dna FROM curated_dna WHERE paul_name = ?', (name,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                dna = PaulDNA.from_dict(json.loads(row[0]))
                elite.append((name, dna, fitness))
        
        return elite
    
    def breed_next_generation(self, num_offspring: int = 50) -> List[str]:
        """
        Breed next generation from elite curated Pauls.
        
        Returns:
            List of new Paul names
        """
        elite = self.get_elite_curated(100)
        
        if len(elite) < 2:
            print("❌ Need at least 2 elite Pauls to breed")
            return []
        
        print(f"\n🧬 Breeding {num_offspring} new Pauls from {len(elite)} elite...")
        
        new_pauls = []
        
        for i in range(num_offspring):
            # Select parents
            parent_a = random.choice(elite)
            parent_b = random.choice(elite)
            
            # Create genotypes
            geno_a = Genotype(dna=parent_a[1], generation=1)
            geno_b = Genotype(dna=parent_b[1], generation=1)
            
            # Breed
            child_dna = self.breeding.crossover(geno_a.dna, geno_b.dna)
            
            # Mutate
            for trait_name in child_dna.to_dict().keys():
                old_value = getattr(child_dna, trait_name)
                new_value, _ = self.breeding.mutate_trait(old_value)
                setattr(child_dna, trait_name, new_value)
            
            # Create new Paul
            new_name = f"Paul-Evolved-{i+1:03d}"
            
            # Save
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO curated_dna (paul_name, dna, archetype, generation, parent_a, parent_b, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                new_name,
                json.dumps(child_dna.to_dict()),
                'evolved',
                2,
                parent_a[0],
                parent_b[0],
                datetime.now().isoformat(),
            ))
            conn.commit()
            conn.close()
            
            # Create portfolio
            self.paper_trading.create_portfolio(new_name, initial_balance=10000.0, enabled=True)
            
            new_pauls.append(new_name)
        
        print(f"✅ Created {len(new_pauls)} evolved Pauls")
        return new_pauls
    
    def get_stats(self) -> Dict:
        """Get statistics for curated Pauls."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count with DNA
        cursor.execute('SELECT COUNT(*) FROM curated_dna')
        with_dna = cursor.fetchone()[0]
        
        # Count evaluated
        cursor.execute('SELECT COUNT(*) FROM curated_performance')
        evaluated = cursor.fetchone()[0]
        
        # Elite count
        cursor.execute('SELECT COUNT(*) FROM curated_performance WHERE elite = 1')
        elite = cursor.fetchone()[0]
        
        # Fitness stats
        cursor.execute('''
            SELECT AVG(fitness_score), MAX(fitness_score), MIN(fitness_score)
            FROM curated_performance
        ''')
        avg_fit, max_fit, min_fit = cursor.fetchone()
        
        # Top 10
        cursor.execute('''
            SELECT p.paul_name, p.fitness_score, p.roi, p.win_rate, d.archetype
            FROM curated_performance p
            JOIN curated_dna d ON p.paul_name = d.paul_name
            ORDER BY p.rank ASC
            LIMIT 10
        ''')
        top_10 = []
        for row in cursor.fetchall():
            top_10.append({
                'name': row[0],
                'fitness': row[1],
                'roi': row[2],
                'win_rate': row[3],
                'archetype': row[4],
            })
        
        conn.close()
        
        return {
            'total_curated': len(self.curated_pauls),
            'with_dna': with_dna,
            'evaluated': evaluated,
            'elite_count': elite,
            'avg_fitness': avg_fit or 0,
            'max_fitness': max_fit or 0,
            'min_fitness': min_fit or 0,
            'top_10': top_10,
        }


# CLI Interface
def curated_cli():
    """Command-line interface for curated Paul evolution."""
    import sys
    
    evolution = CuratedPaulEvolution()
    
    if len(sys.argv) < 2:
        print("Curated Paul Evolution System")
        print("Commands:")
        print("  assign                  - Assign DNA to all curated Pauls")
        print("  evaluate                - Evaluate curated Pauls")
        print("  elite                   - Show top 100 elite Pauls")
        print("  breed <n>               - Breed n new Pauls from elite")
        print("  stats                   - Show statistics")
        print("  full                    - Run full cycle")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "assign":
        count = evolution.assign_dna_to_curated()
        print(f"\n✅ Assigned DNA to {count} curated Pauls")
    
    elif command == "evaluate":
        results = evolution.evaluate_curated_pauls()
        print(f"\n✅ Evaluated {len(results)} curated Pauls")
    
    elif command == "elite":
        elite = evolution.get_elite_curated(100)
        print(f"\n🏆 Top 100 Elite Curated Pauls")
        print("=" * 60)
        for i, (name, dna, fitness) in enumerate(elite[:20], 1):
            print(f"{i}. {name}")
            print(f"   Fitness: {fitness:.2f}")
            print(f"   {dna.describe()}")
            print()
    
    elif command == "breed":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        new_pauls = evolution.breed_next_generation(n)
        print(f"\n✅ Created {len(new_pauls)} evolved Pauls")
    
    elif command == "stats":
        stats = evolution.get_stats()
        print("\n📊 Curated Paul Statistics")
        print("=" * 60)
        print(f"Total Curated: {stats['total_curated']}")
        print(f"With DNA: {stats['with_dna']}")
        print(f"Evaluated: {stats['evaluated']}")
        print(f"Elite: {stats['elite_count']}")
        print(f"\nFitness Stats:")
        print(f"  Average: {stats['avg_fitness']:.2f}")
        print(f"  Best: {stats['max_fitness']:.2f}")
        print(f"  Worst: {stats['min_fitness']:.2f}")
        print(f"\nTop 10 by Archetype:")
        for paul in stats['top_10']:
            print(f"  {paul['name']} ({paul['archetype']}): {paul['fitness']:.2f}")
    
    elif command == "full":
        print("\n" + "=" * 60)
        print("🚀 CURATED PAUL EVOLUTION CYCLE")
        print("=" * 60)
        
        evolution.assign_dna_to_curated()
        evolution.evaluate_curated_pauls()
        stats = evolution.get_stats()
        
        print("\n" + "=" * 60)
        print("✅ CYCLE COMPLETE")
        print("=" * 60)
        print(f"Curated Pauls: {stats['total_curated']}")
        print(f"Evaluated: {stats['evaluated']}")
        print(f"Elite: {stats['elite_count']}")
        print(f"Best Fitness: {stats['max_fitness']:.2f}")


if __name__ == "__main__":
    curated_cli()
