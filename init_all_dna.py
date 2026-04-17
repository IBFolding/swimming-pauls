#!/usr/bin/env python3
"""
Initialize DNA for all 1000 Pauls.
"""

import json
import random
import sqlite3

from curated_evolution import CuratedPaulEvolution
from genetic_breeding import PaulDNA

evolution = CuratedPaulEvolution()

print("🧬 Initializing DNA for all 1000 Pauls")
print("=" * 60)

# Get current DNA count
conn = sqlite3.connect(evolution.db_path)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM curated_dna')
current_count = cursor.fetchone()[0]
print(f"Current Pauls with DNA: {current_count}")

# Get Pauls without DNA
cursor.execute('SELECT paul_name FROM curated_dna')
existing = {row[0] for row in cursor.fetchall()}

missing = [p for p in evolution.curated_pauls if p not in existing]
print(f"Pauls needing DNA: {len(missing)}")

# Generate diverse DNA for each missing Paul
random.seed(42)  # Reproducible

for i, paul_name in enumerate(missing, 1):
    # Create diverse DNA based on Paul name characteristics
    if 'Conservative' in paul_name or 'Safe' in paul_name:
        dna = PaulDNA(
            risk_management=random.uniform(0.7, 0.9),
            conviction=random.uniform(0.3, 0.6),
            technical_vs_fundamental=random.uniform(0.3, 0.7),
            emotional_stability=random.uniform(0.7, 0.9),
            time_horizon=random.uniform(0.6, 0.9),
            adaptability=random.uniform(0.4, 0.6),
            learning_rate=random.uniform(0.3, 0.5),
            defi_specialist=random.uniform(0, 0.3),
            macro_specialist=random.uniform(0.2, 0.5),
            nft_specialist=random.uniform(0, 0.2),
        )
    elif 'Aggressive' in paul_name or 'Degen' in paul_name or 'Yolo' in paul_name:
        dna = PaulDNA(
            risk_management=random.uniform(0.1, 0.4),
            conviction=random.uniform(0.7, 0.9),
            technical_vs_fundamental=random.uniform(0.5, 0.8),
            emotional_stability=random.uniform(0.2, 0.5),
            time_horizon=random.uniform(0.1, 0.4),
            adaptability=random.uniform(0.6, 0.9),
            learning_rate=random.uniform(0.5, 0.8),
            defi_specialist=random.uniform(0.3, 0.8),
            macro_specialist=random.uniform(0.1, 0.4),
            nft_specialist=random.uniform(0.2, 0.7),
        )
    elif 'Artist' in paul_name or 'Creative' in paul_name or 'Musician' in paul_name:
        dna = PaulDNA(
            risk_management=random.uniform(0.4, 0.7),
            conviction=random.uniform(0.5, 0.8),
            technical_vs_fundamental=random.uniform(0.3, 0.5),
            emotional_stability=random.uniform(0.4, 0.7),
            time_horizon=random.uniform(0.3, 0.6),
            adaptability=random.uniform(0.6, 0.9),
            learning_rate=random.uniform(0.5, 0.8),
            defi_specialist=random.uniform(0.2, 0.5),
            macro_specialist=random.uniform(0.1, 0.3),
            nft_specialist=random.uniform(0.5, 0.9),  # Artists like NFTs
        )
    elif 'Scientist' in paul_name or 'Researcher' in paul_name or 'Analyst' in paul_name:
        dna = PaulDNA(
            risk_management=random.uniform(0.6, 0.8),
            conviction=random.uniform(0.4, 0.7),
            technical_vs_fundamental=random.uniform(0.6, 0.9),
            emotional_stability=random.uniform(0.7, 0.9),
            time_horizon=random.uniform(0.5, 0.8),
            adaptability=random.uniform(0.5, 0.7),
            learning_rate=random.uniform(0.6, 0.9),
            defi_specialist=random.uniform(0.3, 0.6),
            macro_specialist=random.uniform(0.4, 0.8),
            nft_specialist=random.uniform(0.1, 0.3),
        )
    else:
        # Random balanced DNA
        dna = PaulDNA.random()
    
    # Save to database
    cursor.execute('''
        INSERT OR REPLACE INTO curated_dna (paul_name, dna, generation, created_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (paul_name, json.dumps(dna.to_dict()), 1))
    
    if i % 100 == 0:
        print(f"  Processed {i}/{len(missing)}...")

conn.commit()
conn.close()

print(f"\n✅ DNA initialized for {len(missing)} Pauls")
print(f"✅ Total Pauls with DNA: 1000")
