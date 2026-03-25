#!/usr/bin/env python3
"""
Paul Learning System - Domain-aware accuracy tracking and memory.

Tracks Paul predictions per domain, stores accuracy history,
and enhances LLM prompts with track record.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class PaulLearningSystem:
    """Tracks Paul learning across domains."""
    
    def __init__(self, db_path: str = "data/paul_learning.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize learning database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Predictions with domain tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id TEXT PRIMARY KEY,
                paul_name TEXT NOT NULL,
                domain TEXT NOT NULL,
                symbol TEXT,
                question TEXT,
                prediction TEXT,
                direction TEXT,
                confidence REAL,
                outcome TEXT,
                accuracy REAL,
                created_at TEXT,
                resolved_at TEXT
            )
        ''')
        
        # Paul accuracy per domain
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_accuracy (
                paul_name TEXT,
                domain TEXT,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy_rate REAL DEFAULT 0.0,
                avg_confidence REAL DEFAULT 0.0,
                last_updated TEXT,
                PRIMARY KEY (paul_name, domain)
            )
        ''')
        
        # Domain stats
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domain_stats (
                domain TEXT PRIMARY KEY,
                total_predictions INTEGER DEFAULT 0,
                avg_accuracy REAL DEFAULT 0.0,
                top_paul TEXT,
                last_updated TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def record_prediction(self, paul_name: str, domain: str, symbol: str,
                         prediction: str, direction: str, confidence: float,
                         question: str = "") -> str:
        """Record a new prediction."""
        pred_id = f"{paul_name}_{domain}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO predictions 
            (id, paul_name, domain, symbol, question, prediction, direction, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (pred_id, paul_name, domain, symbol, question, prediction, 
              direction, confidence, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return pred_id
    
    def resolve_prediction(self, pred_id: str, outcome: str, accuracy: float):
        """Mark prediction as resolved with outcome."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE predictions 
            SET outcome = ?, accuracy = ?, resolved_at = ?
            WHERE id = ?
        ''', (outcome, accuracy, datetime.now().isoformat(), pred_id))
        
        # Update Paul accuracy
        cursor.execute('''
            SELECT paul_name, domain FROM predictions WHERE id = ?
        ''', (pred_id,))
        row = cursor.fetchone()
        
        if row:
            self._update_paul_accuracy(cursor, row[0], row[1])
        
        conn.commit()
        conn.close()
    
    def _update_paul_accuracy(self, cursor, paul_name: str, domain: str):
        """Recalculate Paul accuracy for domain."""
        cursor.execute('''
            SELECT COUNT(*), SUM(CASE WHEN accuracy > 0 THEN 1 ELSE 0 END), AVG(confidence)
            FROM predictions 
            WHERE paul_name = ? AND domain = ? AND outcome IS NOT NULL
        ''', (paul_name, domain))
        
        total, correct, avg_conf = cursor.fetchone()
        
        if total and total > 0:
            accuracy_rate = correct / total if correct else 0.0
            
            cursor.execute('''
                INSERT OR REPLACE INTO paul_accuracy
                (paul_name, domain, total_predictions, correct_predictions, 
                 accuracy_rate, avg_confidence, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (paul_name, domain, total, correct or 0, accuracy_rate, 
                  avg_conf or 0.0, datetime.now().isoformat()))
    
    def get_paul_track_record(self, paul_name: str, domain: str, limit: int = 5) -> Dict:
        """Get Paul's recent track record for domain."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get accuracy stats
        cursor.execute('''
            SELECT total_predictions, correct_predictions, accuracy_rate, avg_confidence
            FROM paul_accuracy WHERE paul_name = ? AND domain = ?
        ''', (paul_name, domain))
        
        stats = cursor.fetchone()
        
        # Get recent predictions
        cursor.execute('''
            SELECT symbol, direction, outcome, accuracy, created_at
            FROM predictions 
            WHERE paul_name = ? AND domain = ? AND outcome IS NOT NULL
            ORDER BY created_at DESC LIMIT ?
        ''', (paul_name, domain, limit))
        
        recent = cursor.fetchall()
        conn.close()
        
        return {
            'paul_name': paul_name,
            'domain': domain,
            'total': stats[0] if stats else 0,
            'correct': stats[1] if stats else 0,
            'accuracy_rate': stats[2] if stats else 0.0,
            'avg_confidence': stats[3] if stats else 0.0,
            'recent_predictions': recent
        }
    
    def get_domain_experts(self, domain: str, limit: int = 5) -> List[Tuple]:
        """Get top Pauls for a domain."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT paul_name, accuracy_rate, total_predictions
            FROM paul_accuracy 
            WHERE domain = ? AND total_predictions >= 5
            ORDER BY accuracy_rate DESC LIMIT ?
        ''', (domain, limit))
        
        experts = cursor.fetchall()
        conn.close()
        
        return experts
    
    def format_prompt_with_memory(self, paul_name: str, domain: str, 
                                   symbol: str, price: float) -> str:
        """Format LLM prompt with Paul's track record."""
        record = self.get_paul_track_record(paul_name, domain)
        
        # Build memory context
        memory_lines = [f"You are {paul_name}."]
        
        if record['total'] > 0:
            memory_lines.append(f"Your track record: {record['correct']}/{record['total']} correct ({record['accuracy_rate']*100:.0f}% accuracy)")
            
            # Add recent results
            if record['recent_predictions']:
                memory_lines.append("Recent predictions:")
                for pred in record['recent_predictions'][:3]:
                    symbol, direction, outcome, accuracy, _ = pred
                    result = "✓" if accuracy and accuracy > 0 else "✗"
                    memory_lines.append(f"  - {symbol} {direction}: {result}")
        
        # Add expertise hint
        experts = self.get_domain_experts(domain, 3)
        if any(e[0] == paul_name for e in experts):
            rank = next(i for i, e in enumerate(experts) if e[0] == paul_name) + 1
            memory_lines.append(f"You are ranked #{rank} expert in {domain}.")
        
        memory_lines.append(f"\nAnalyze {symbol} at ${price:,.2f}:")
        memory_lines.append("Respond: SENTIMENT: [bullish/bearish/neutral] | CONFIDENCE: [0-100] | REASONING: [brief]")
        
        return "\n".join(memory_lines)

# Singleton instance
_learning_system = None

def get_learning_system() -> PaulLearningSystem:
    """Get singleton learning system instance."""
    global _learning_system
    if _learning_system is None:
        _learning_system = PaulLearningSystem()
    return _learning_system
