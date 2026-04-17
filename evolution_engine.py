"""
Swimming Pauls - Breeding + Paper Trading Integration

Connects genetic breeding system to paper trading performance.
Evolves Pauls based on real trading results.

Author: Howard (H.O.W.A.R.D)
"""

import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import sqlite3

from genetic_breeding import GeneticBreedingEngine, PaulDNA, Genotype, calculate_fitness
from paper_trading import PaperTradingManager, PaperPortfolio


class EvolutionEngine:
    """
    Evolves Swimming Pauls through genetic breeding + paper trading.
    
    Workflow:
    1. Create Generation 1 (random Pauls)
    2. Paper trade for N days
    3. Calculate fitness from performance
    4. Breed top performers -> Generation 2
    5. Repeat
    """
    
    def __init__(self, 
                 generation_size: int = 100,
                 trading_duration_days: int = 30,
                 db_path: str = "data/evolution.db"):
        """
        Initialize evolution engine.
        
        Args:
            generation_size: Number of Pauls per generation
            trading_duration_days: How long to paper trade before breeding
            db_path: SQLite database for evolution tracking
        """
        self.generation_size = generation_size
        self.trading_duration_days = trading_duration_days
        self.db_path = Path(db_path)
        
        # Sub-engines
        self.breeding = GeneticBreedingEngine(db_path="data/genetics.db")
        self.paper_trading = PaperTradingManager(db_path="data/paper_trading.db")
        
        self._init_db()
    
    def _init_db(self):
        """Initialize evolution database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Evolution runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evolution_runs (
                run_id TEXT PRIMARY KEY,
                generation INTEGER NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                status TEXT NOT NULL,  -- 'running', 'completed', 'breeding'
                population TEXT NOT NULL,  -- JSON list of paul_names
                top_performers TEXT,  -- JSON list
                avg_fitness REAL,
                best_fitness REAL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Paul performance history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_performance (
                paul_name TEXT NOT NULL,
                generation INTEGER NOT NULL,
                run_id TEXT NOT NULL,
                fitness_score REAL,
                roi REAL,
                win_rate REAL,
                max_drawdown REAL,
                total_trades INTEGER,
                dna TEXT,  -- JSON
                PRIMARY KEY (paul_name, run_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_generation_one(self) -> List[str]:
        """
        Create Generation 1 with random Pauls.
        
        Returns:
            List of Paul names created
        """
        print(f"🧬 Creating Generation 1 ({self.generation_size} Pauls)...")
        
        paul_names = []
        
        for i in range(self.generation_size):
            # Create random DNA
            dna = self.breeding.create_random_dna()
            genotype = Genotype(dna=dna, generation=1)
            
            # Generate name
            paul_name = f"Paul-G1-{i+1:03d}"
            
            # Save genotype
            self.breeding.save_genotype(paul_name, genotype)
            
            # Create paper trading portfolio
            self.paper_trading.create_portfolio(paul_name, initial_balance=10000.0, enabled=True)
            
            paul_names.append(paul_name)
            
            if (i + 1) % 10 == 0:
                print(f"  Created {i+1}/{self.generation_size}...")
        
        print(f"✅ Generation 1 complete: {len(paul_names)} Pauls")
        return paul_names
    
    def evaluate_generation(self, paul_names: List[str]) -> List[Tuple[str, Genotype, float]]:
        """
        Evaluate performance of a generation.
        
        Args:
            paul_names: List of Paul names to evaluate
        
        Returns:
            List of (name, genotype, fitness_score) sorted by fitness
        """
        print(f"\n📊 Evaluating {len(paul_names)} Pauls...")
        
        results = []
        
        for paul_name in paul_names:
            # Get paper trading portfolio
            if paul_name not in self.paper_trading.portfolios:
                continue
            
            portfolio = self.paper_trading.portfolios[paul_name]
            
            # Skip if no trades
            if portfolio.total_trades == 0:
                continue
            
            # Calculate fitness
            portfolio_data = {
                'roi': portfolio.get_roi(),
                'win_rate': portfolio.get_win_rate(),
                'max_drawdown': portfolio.max_drawdown,
                'total_trades': portfolio.total_trades,
            }
            
            fitness = calculate_fitness(portfolio_data)
            
            # Get genotype
            # (In real implementation, we'd load from DB)
            # For now, create placeholder
            genotype = Genotype(dna=PaulDNA(), generation=1)
            
            results.append((paul_name, genotype, fitness))
        
        # Sort by fitness (descending)
        results.sort(key=lambda x: x[2], reverse=True)
        
        print(f"✅ Evaluated {len(results)} Pauls with trades")
        
        if results:
            print(f"\n🏆 Top Performer: {results[0][0]} (Fitness: {results[0][2]:.2f})")
            print(f"📈 Average Fitness: {sum(r[2] for r in results) / len(results):.2f}")
        
        return results
    
    def breed_next_generation(self, 
                              current_results: List[Tuple[str, Genotype, float]],
                              generation_number: int) -> List[str]:
        """
        Breed next generation from current results.
        
        Args:
            current_results: List of (name, genotype, fitness) from current gen
            generation_number: Next generation number
        
        Returns:
            List of new Paul names
        """
        print(f"\n🧬 Breeding Generation {generation_number}...")
        
        # Create next generation through breeding
        new_generation = self.breeding.create_next_generation(
            current_results,
            target_size=self.generation_size
        )
        
        # Create portfolios for new Pauls
        paul_names = []
        
        for i, (child_name, child_genotype) in enumerate(new_generation):
            # Update generation number
            child_genotype.generation = generation_number
            
            # Rename with generation prefix
            paul_name = f"Paul-G{generation_number}-{i+1:03d}"
            
            # Save genotype
            self.breeding.save_genotype(paul_name, child_genotype)
            
            # Create paper trading portfolio
            self.paper_trading.create_portfolio(paul_name, initial_balance=10000.0, enabled=True)
            
            paul_names.append(paul_name)
        
        print(f"✅ Generation {generation_number} created: {len(paul_names)} Pauls")
        
        # Show sample of new Pauls
        print(f"\n📋 Sample New Pauls:")
        for paul_name in paul_names[:3]:
            # Get description from DNA
            print(f"  - {paul_name}")
        
        return paul_names
    
    def run_evolution_cycle(self, 
                           current_generation: int = 1,
                           paul_names: List[str] = None) -> Tuple[int, List[str]]:
        """
        Run one full evolution cycle.
        
        Args:
            current_generation: Current generation number
            paul_names: Current generation Paul names (if None, creates Gen 1)
        
        Returns:
            (next_generation_number, new_paul_names)
        """
        run_id = f"evolution-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Step 1: Create or use existing generation
        if paul_names is None:
            print(f"\n{'='*60}")
            print(f"🚀 STARTING EVOLUTION - Generation 1")
            print(f"{'='*60}")
            paul_names = self.create_generation_one()
        else:
            print(f"\n{'='*60}")
            print(f"🔄 EVOLUTION CYCLE - Generation {current_generation}")
            print(f"{'='*60}")
        
        # Step 2: Paper trade (simulated duration)
        print(f"\n⏱️  Paper Trading Period: {self.trading_duration_days} days")
        print(f"   (In production: Would wait for real trading period)")
        print(f"   (Simulation: Using existing trades)")
        
        # Step 3: Evaluate performance
        results = self.evaluate_generation(paul_names)
        
        if len(results) < 10:
            print("❌ Not enough Pauls with trades to breed")
            return current_generation, paul_names
        
        # Step 4: Save evolution run data
        self._save_evolution_run(run_id, current_generation, paul_names, results)
        
        # Step 5: Breed next generation
        next_gen = current_generation + 1
        new_paul_names = self.breed_next_generation(results, next_gen)
        
        print(f"\n{'='*60}")
        print(f"✅ EVOLUTION CYCLE COMPLETE")
        print(f"   Generation {current_generation} → {next_gen}")
        print(f"   Best Fitness: {results[0][2]:.2f}")
        print(f"   Top Paul: {results[0][0]}")
        print(f"{'='*60}")
        
        return next_gen, new_paul_names
    
    def _save_evolution_run(self, run_id: str, generation: int, 
                           population: List[str], 
                           results: List[Tuple[str, Genotype, float]]):
        """Save evolution run to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save run
        top_performers = [r[0] for r in results[:10]]
        avg_fitness = sum(r[2] for r in results) / len(results) if results else 0
        best_fitness = results[0][2] if results else 0
        
        cursor.execute('''
            INSERT INTO evolution_runs 
            (run_id, generation, start_date, end_date, status, population, 
             top_performers, avg_fitness, best_fitness, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id,
            generation,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            'completed',
            json.dumps(population),
            json.dumps(top_performers),
            avg_fitness,
            best_fitness,
            datetime.now().isoformat(),
        ))
        
        # Save individual Paul performance
        for paul_name, genotype, fitness in results:
            portfolio = self.paper_trading.portfolios.get(paul_name)
            if portfolio:
                cursor.execute('''
                    INSERT OR REPLACE INTO paul_performance
                    (paul_name, generation, run_id, fitness_score, roi, 
                     win_rate, max_drawdown, total_trades, dna)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    paul_name,
                    generation,
                    run_id,
                    fitness,
                    portfolio.get_roi(),
                    portfolio.get_win_rate(),
                    portfolio.max_drawdown,
                    portfolio.total_trades,
                    json.dumps(genotype.dna.to_dict()),
                ))
        
        conn.commit()
        conn.close()
    
    def get_evolution_stats(self, generations_back: int = 5) -> Dict:
        """Get evolution statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT generation, avg_fitness, best_fitness 
            FROM evolution_runs 
            ORDER BY generation DESC 
            LIMIT ?
        ''', (generations_back,))
        
        stats = {
            'generations': [],
            'avg_fitness_trend': [],
            'best_fitness_trend': [],
        }
        
        for row in cursor.fetchall():
            stats['generations'].append(row[0])
            stats['avg_fitness_trend'].append(row[1])
            stats['best_fitness_trend'].append(row[2])
        
        conn.close()
        
        # Calculate improvement
        if len(stats['best_fitness_trend']) >= 2:
            stats['improvement'] = (
                stats['best_fitness_trend'][0] - stats['best_fitness_trend'][-1]
            )
        
        return stats
    
    def get_best_pauls_all_time(self, n: int = 10) -> List[Dict]:
        """Get best Pauls across all generations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT paul_name, generation, fitness_score, roi, win_rate, dna
            FROM paul_performance
            ORDER BY fitness_score DESC
            LIMIT ?
        ''', (n,))
        
        best = []
        for row in cursor.fetchall():
            dna = json.loads(row[5])
            best.append({
                'name': row[0],
                'generation': row[1],
                'fitness': row[2],
                'roi': row[3],
                'win_rate': row[4],
                'description': PaulDNA.from_dict(dna).describe(),
            })
        
        conn.close()
        return best


def simulate_trades_for_testing(paul_names: List[str], 
                                paper_manager: PaperTradingManager,
                                num_trades: int = 20):
    """
    Simulate trades for testing evolution.
    
    In production, this would be real paper trading over time.
    """
    print(f"\n🎲 Simulating {num_trades} trades per Paul...")
    
    for paul_name in paul_names:
        if paul_name not in paper_manager.portfolios:
            continue
        
        portfolio = paper_manager.portfolios[paul_name]
        if not portfolio.enabled:
            continue
        
        for _ in range(num_trades):
            # Random trade
            symbol = random.choice(["BTC", "ETH", "SOL"])
            direction = random.choice(["buy", "sell"])
            confidence = random.uniform(0.75, 0.95)
            entry_price = random.uniform(100, 500)
            
            trade = paper_manager.execute_trade(
                paul_name=paul_name,
                symbol=symbol,
                direction=direction,
                current_price=entry_price,
                confidence=confidence
            )
            
            if trade and random.random() < 0.7:  # Close 70% of trades
                exit_price = entry_price * random.uniform(0.85, 1.20)
                paper_manager.close_trade(trade.id, exit_price, "simulated")


# CLI Interface
def evolution_cli():
    """Command-line interface for evolution system."""
    import sys
    
    engine = EvolutionEngine()
    
    if len(sys.argv) < 2:
        print("Swimming Pauls Evolution System")
        print("Commands:")
        print("  init                    - Create Generation 1")
        print("  evolve [gen]            - Run evolution cycle")
        print("  stats                   - Show evolution statistics")
        print("  best                    - Show best Pauls all time")
        print("  simulate <n>            - Simulate trades for testing")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "init":
        paul_names = engine.create_generation_one()
        print(f"\n✅ Created {len(paul_names)} Pauls in Generation 1")
        print(f"   Next: Run 'simulate' to add trades, then 'evolve'")
    
    elif command == "simulate" and len(sys.argv) > 2:
        n = int(sys.argv[2])
        # Get current generation Pauls
        conn = sqlite3.connect(engine.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT paul_name FROM paul_performance ORDER BY generation DESC LIMIT 100')
        paul_names = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not paul_names:
            print("No Pauls found. Run 'init' first.")
            sys.exit(1)
        
        simulate_trades_for_testing(paul_names, engine.paper_trading, n)
        print(f"\n✅ Simulated {n} trades for {len(paul_names)} Pauls")
    
    elif command == "evolve":
        gen = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        
        # Get current generation Pauls
        conn = sqlite3.connect(engine.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT paul_name FROM paul_performance 
            WHERE generation = ?
        ''', (gen,))
        paul_names = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if not paul_names:
            print(f"No Pauls found for Generation {gen}. Run 'init' first.")
            sys.exit(1)
        
        next_gen, new_names = engine.run_evolution_cycle(gen, paul_names)
        print(f"\n✅ Evolution complete: Generation {gen} → {next_gen}")
    
    elif command == "stats":
        stats = engine.get_evolution_stats()
        print("\n📊 Evolution Statistics")
        print("=" * 60)
        print(f"Generations tracked: {len(stats['generations'])}")
        if stats.get('improvement'):
            print(f"Fitness improvement: {stats['improvement']:+.2f}")
        print("\nFitness by Generation:")
        for gen, avg, best in zip(stats['generations'], 
                                   stats['avg_fitness_trend'],
                                   stats['best_fitness_trend']):
            print(f"  Gen {gen}: Avg={avg:.2f}, Best={best:.2f}")
    
    elif command == "best":
        best = engine.get_best_pauls_all_time(10)
        print("\n🏆 Best Pauls of All Time")
        print("=" * 60)
        for i, paul in enumerate(best, 1):
            print(f"{i}. {paul['name']} (Gen {paul['generation']})")
            print(f"   Fitness: {paul['fitness']:.2f}")
            print(f"   ROI: {paul['roi']:+.1%} | Win Rate: {paul['win_rate']:.0%}")
            print(f"   {paul['description']}")
            print()


if __name__ == "__main__":
    evolution_cli()
