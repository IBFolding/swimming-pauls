"""
Prediction History Database for Swimming Pauls
Tracks all predictions, Paul performance, and outcomes.
SQLite-based, 100% local.

Author: Howard (H.O.W.A.R.D)
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PredictionRecord:
    """Single prediction record."""
    id: str
    timestamp: datetime
    question: str
    consensus_direction: str  # BULLISH, BEARISH, NEUTRAL
    consensus_confidence: float
    sentiment_score: float
    pauls_count: int
    rounds: int
    duration_ms: int
    outcome: Optional[str] = None  # CORRECT, INCORRECT, PENDING
    outcome_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None


@dataclass
class PaulPerformance:
    """Individual Paul performance stats."""
    paul_name: str
    total_predictions: int
    correct_predictions: int
    accuracy_rate: float
    avg_confidence: float
    best_streak: int
    current_streak: int
    specialty_domains: List[str]
    last_active: datetime


class PredictionHistoryDB:
    """
    Local SQLite database for tracking all predictions and Paul performance.
    100% local - no cloud, no API calls.
    """
    
    def __init__(self, db_path: str = "data/predictions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                question TEXT NOT NULL,
                question_hash TEXT NOT NULL,
                consensus_direction TEXT NOT NULL,
                consensus_confidence REAL NOT NULL,
                sentiment_score REAL NOT NULL,
                pauls_count INTEGER NOT NULL,
                rounds INTEGER NOT NULL,
                duration_ms INTEGER,
                outcome TEXT DEFAULT 'PENDING',
                outcome_notes TEXT,
                resolved_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Individual Paul votes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id TEXT NOT NULL,
                paul_name TEXT NOT NULL,
                paul_specialty TEXT,
                vote_direction TEXT NOT NULL,
                confidence REAL NOT NULL,
                reasoning TEXT,
                was_correct INTEGER,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            )
        ''')
        
        # Paul performance stats (auto-updated)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paul_performance (
                paul_name TEXT PRIMARY KEY,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy_rate REAL DEFAULT 0.0,
                avg_confidence REAL DEFAULT 0.0,
                best_streak INTEGER DEFAULT 0,
                current_streak INTEGER DEFAULT 0,
                specialty_domains TEXT,
                last_active TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Knowledge graph snapshots
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id TEXT NOT NULL,
                entities TEXT,  -- JSON
                relationships TEXT,  -- JSON
                timestamp TEXT,
                FOREIGN KEY (prediction_id) REFERENCES predictions(id)
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON predictions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_outcome ON predictions(outcome)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_paul_votes_name ON paul_votes(paul_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_paul_performance_accuracy ON paul_performance(accuracy_rate)')
        
        conn.commit()
        conn.close()
    
    def record_prediction(self, 
                         question: str,
                         consensus: Dict,
                         paul_votes: List[Dict],
                         pauls_count: int,
                         rounds: int,
                         duration_ms: int = None) -> str:
        """
        Record a new prediction to the database.
        
        Args:
            question: The question asked
            consensus: Dict with direction, confidence, sentiment
            paul_votes: List of individual Paul votes
            pauls_count: Number of Pauls in simulation
            rounds: Number of rounds
            duration_ms: Time taken in milliseconds
            
        Returns:
            prediction_id: Unique ID for this prediction
        """
        # Generate unique ID from question + timestamp
        timestamp = datetime.now()
        id_base = f"{question}_{timestamp.isoformat()}"
        prediction_id = hashlib.md5(id_base.encode()).hexdigest()[:12]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert main prediction
        cursor.execute('''
            INSERT INTO predictions 
            (id, timestamp, question, question_hash, consensus_direction, 
             consensus_confidence, sentiment_score, pauls_count, rounds, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            prediction_id,
            timestamp.isoformat(),
            question,
            hashlib.md5(question.encode()).hexdigest()[:8],
            consensus.get('direction', 'NEUTRAL'),
            consensus.get('confidence', 0.5),
            consensus.get('sentiment', 0.0),
            pauls_count,
            rounds,
            duration_ms
        ))
        
        # Insert individual Paul votes
        for vote in paul_votes:
            cursor.execute('''
                INSERT INTO paul_votes 
                (prediction_id, paul_name, paul_specialty, vote_direction, confidence, reasoning)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                prediction_id,
                vote.get('name', 'Unknown Paul'),
                vote.get('specialty', ''),
                vote.get('direction', 'NEUTRAL'),
                vote.get('confidence', 0.5),
                vote.get('reasoning', '')[:500]  # Limit length
            ))
        
        # Update Paul performance stats
        self._update_paul_stats(cursor, paul_votes)
        
        conn.commit()
        conn.close()
        
        return prediction_id
    
    def _update_paul_stats(self, cursor, paul_votes: List[Dict]):
        """Update performance stats for each Paul."""
        for vote in paul_votes:
            paul_name = vote.get('name', 'Unknown Paul')
            confidence = vote.get('confidence', 0.5)
            
            # Check if Paul exists
            cursor.execute('SELECT * FROM paul_performance WHERE paul_name = ?', (paul_name,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute('''
                    UPDATE paul_performance 
                    SET total_predictions = total_predictions + 1,
                        avg_confidence = (avg_confidence * total_predictions + ?) / (total_predictions + 1),
                        last_active = ?
                    WHERE paul_name = ?
                ''', (confidence, datetime.now().isoformat(), paul_name))
            else:
                # Insert new Paul
                cursor.execute('''
                    INSERT INTO paul_performance 
                    (paul_name, total_predictions, avg_confidence, last_active, specialty_domains)
                    VALUES (?, 1, ?, ?, ?)
                ''', (paul_name, confidence, datetime.now().isoformat(), 
                      json.dumps([vote.get('specialty', '')])))
    
    def mark_outcome(self, prediction_id: str, outcome: str, notes: str = None):
        """
        Mark the outcome of a prediction.
        
        Args:
            prediction_id: ID of prediction
            outcome: 'CORRECT', 'INCORRECT', or 'PENDING'
            notes: Optional notes about the outcome
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        resolved_at = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE predictions 
            SET outcome = ?, outcome_notes = ?, resolved_at = ?
            WHERE id = ?
        ''', (outcome, notes, resolved_at, prediction_id))
        
        # If resolved, update Paul stats with correctness
        if outcome in ('CORRECT', 'INCORRECT'):
            was_correct = 1 if outcome == 'CORRECT' else 0
            
            # Get prediction details
            cursor.execute('SELECT consensus_direction FROM predictions WHERE id = ?', (prediction_id,))
            result = cursor.fetchone()
            if result:
                consensus_dir = result[0]
                
                # Update each Paul's correctness
                cursor.execute('''
                    SELECT id, paul_name, vote_direction FROM paul_votes WHERE prediction_id = ?
                ''', (prediction_id,))
                
                for row in cursor.fetchall():
                    vote_id, paul_name, vote_dir = row
                    vote_correct = 1 if vote_dir == consensus_dir and outcome == 'CORRECT' else 0
                    
                    cursor.execute('''
                        UPDATE paul_votes SET was_correct = ? WHERE id = ?
                    ''', (vote_correct, vote_id))
                    
                    # Update Paul streaks and accuracy
                    self._update_paul_correctness(cursor, paul_name, vote_correct)
        
        conn.commit()
        conn.close()
    
    def _update_paul_correctness(self, cursor, paul_name: str, was_correct: int):
        """Update Paul correctness stats."""
        cursor.execute('SELECT * FROM paul_performance WHERE paul_name = ?', (paul_name,))
        row = cursor.fetchone()
        
        if row:
            total = row[1] + 1
            correct = row[2] + was_correct
            accuracy = correct / total if total > 0 else 0
            
            # Update streaks
            current_streak = row[6]
            best_streak = row[5]
            
            if was_correct:
                current_streak = current_streak + 1 if current_streak > 0 else 1
                best_streak = max(best_streak, current_streak)
            else:
                current_streak = 0
            
            cursor.execute('''
                UPDATE paul_performance 
                SET correct_predictions = ?,
                    accuracy_rate = ?,
                    current_streak = ?,
                    best_streak = ?,
                    updated_at = ?
                WHERE paul_name = ?
            ''', (correct, accuracy, current_streak, best_streak, 
                  datetime.now().isoformat(), paul_name))
    
    def get_leaderboard(self, limit: int = 20) -> List[PaulPerformance]:
        """Get top performing Pauls."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT paul_name, total_predictions, correct_predictions, 
                   accuracy_rate, avg_confidence, best_streak, current_streak,
                   specialty_domains, last_active
            FROM paul_performance
            WHERE total_predictions >= 5  -- Minimum sample size
            ORDER BY accuracy_rate DESC, total_predictions DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(PaulPerformance(
                paul_name=row[0],
                total_predictions=row[1],
                correct_predictions=row[2],
                accuracy_rate=row[3],
                avg_confidence=row[4],
                best_streak=row[5],
                current_streak=row[6],
                specialty_domains=json.loads(row[7]) if row[7] else [],
                last_active=datetime.fromisoformat(row[8]) if row[8] else datetime.now()
            ))
        
        conn.close()
        return results
    
    def get_paul_history(self, paul_name: str, limit: int = 50) -> List[Dict]:
        """Get prediction history for a specific Paul."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.question, p.consensus_direction, p.timestamp, p.outcome,
                   v.vote_direction, v.confidence, v.was_correct
            FROM predictions p
            JOIN paul_votes v ON p.id = v.prediction_id
            WHERE v.paul_name = ?
            ORDER BY p.timestamp DESC
            LIMIT ?
        ''', (paul_name, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'question': row[0],
                'consensus': row[1],
                'timestamp': row[2],
                'outcome': row[3],
                'paul_vote': row[4],
                'paul_confidence': row[5],
                'was_correct': row[6]
            })
        
        conn.close()
        return results
    
    def get_recent_predictions(self, limit: int = 20, outcome_filter: str = None) -> List[PredictionRecord]:
        """Get recent predictions with optional outcome filter."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if outcome_filter:
            cursor.execute('''
                SELECT id, timestamp, question, consensus_direction, consensus_confidence,
                       sentiment_score, pauls_count, rounds, outcome, resolved_at
                FROM predictions
                WHERE outcome = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (outcome_filter, limit))
        else:
            cursor.execute('''
                SELECT id, timestamp, question, consensus_direction, consensus_confidence,
                       sentiment_score, pauls_count, rounds, outcome, resolved_at
                FROM predictions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            results.append(PredictionRecord(
                id=row[0],
                timestamp=datetime.fromisoformat(row[1]),
                question=row[2],
                consensus_direction=row[3],
                consensus_confidence=row[4],
                sentiment_score=row[5],
                pauls_count=row[6],
                rounds=row[7],
                outcome=row[8],
                resolved_at=datetime.fromisoformat(row[9]) if row[9] else None
            ))
        
        conn.close()
        return results
    
    def get_stats_summary(self) -> Dict:
        """Get overall database statistics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total predictions
        cursor.execute('SELECT COUNT(*) FROM predictions')
        stats['total_predictions'] = cursor.fetchone()[0]
        
        # By outcome
        cursor.execute('''
            SELECT outcome, COUNT(*) FROM predictions GROUP BY outcome
        ''')
        stats['by_outcome'] = dict(cursor.fetchall())
        
        # Total unique Pauls
        cursor.execute('SELECT COUNT(DISTINCT paul_name) FROM paul_votes')
        stats['unique_pauls'] = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute('SELECT AVG(consensus_confidence) FROM predictions')
        stats['avg_consensus_confidence'] = cursor.fetchone()[0] or 0
        
        # This week's predictions
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM predictions WHERE timestamp > ?', (week_ago,))
        stats['predictions_this_week'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
    
    def export_to_json(self, filepath: str = "data/predictions_export.json"):
        """Export all predictions to JSON for backup/analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM predictions ORDER BY timestamp DESC')
        predictions = []
        
        columns = [description[0] for description in cursor.description]
        for row in cursor.fetchall():
            predictions.append(dict(zip(columns, row)))
        
        conn.close()
        
        with open(filepath, 'w') as f:
            json.dump(predictions, f, indent=2, default=str)
        
        return filepath


# CLI for testing
if __name__ == "__main__":
    db = PredictionHistoryDB()
    
    # Test recording a prediction
    test_id = db.record_prediction(
        question="Will ETH reach $10K by 2025?",
        consensus={
            'direction': 'BULLISH',
            'confidence': 0.74,
            'sentiment': 0.65
        },
        paul_votes=[
            {'name': 'Visionary Paul', 'specialty': 'Disruptive Innovation', 
             'direction': 'BULLISH', 'confidence': 0.82, 'reasoning': 'Layer 2 scaling...'},
            {'name': 'Skeptic Paul', 'specialty': 'Risk Assessment',
             'direction': 'NEUTRAL', 'confidence': 0.55, 'reasoning': 'Macro headwinds...'},
        ],
        pauls_count=100,
        rounds=20,
        duration_ms=3500
    )
    
    print(f"Recorded prediction: {test_id}")
    
    # Show stats
    stats = db.get_stats_summary()
    print(f"\nStats: {json.dumps(stats, indent=2, default=str)}")
    
    # Show leaderboard
    leaderboard = db.get_leaderboard(limit=5)
    print(f"\nTop Pauls:")
    for paul in leaderboard:
        print(f"  {paul.paul_name}: {paul.accuracy_rate:.1%} accuracy ({paul.total_predictions} preds)")
