"""
Scales Memory System - Persistence & Learning for Prediction Market Simulations

SQLite-based persistence layer for:
- Simulation history tracking
- Agent accuracy metrics per prediction type
- Model improvement from past results
- Session resume capability

Author: Howard (H.O.W.A.R.D)
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from contextlib import contextmanager
import threading


# ============================================================================
# DATABASE SCHEMA
# ============================================================================

SCHEMA_SQL = """
-- Core simulation sessions (for resume capability)
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_uuid TEXT UNIQUE NOT NULL,
    name TEXT,
    config_json TEXT NOT NULL,           -- Full simulation config
    status TEXT DEFAULT 'active',        -- active, paused, completed, error
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resumed_at TIMESTAMP,                -- Last resume time
    checkpoint_data TEXT                 -- JSON for full state restoration
);

-- Agent registry
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    model_name TEXT NOT NULL,            -- e.g., 'claude-3-opus', 'gpt-4'
    agent_type TEXT NOT NULL,            -- 'analyst', 'researcher', 'consensus', etc.
    config_json TEXT,                    -- Agent-specific configuration
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_predictions INTEGER DEFAULT 0,
    overall_accuracy REAL DEFAULT 0.0    -- Weighted average across all types
);

-- Predictions made by agents
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prediction_uuid TEXT UNIQUE NOT NULL,
    session_id INTEGER REFERENCES sessions(id),
    agent_id INTEGER REFERENCES agents(id),
    market_id TEXT NOT NULL,             -- External market identifier
    market_question TEXT,                -- Human-readable question
    prediction_type TEXT NOT NULL,       -- 'binary', 'scalar', 'multiple_choice'
    predicted_probability REAL NOT NULL,
    confidence_score REAL,               -- Agent's confidence 0-1
    reasoning_hash TEXT,                 -- Hash of reasoning for deduplication
    reasoning_summary TEXT,              -- Brief reasoning (truncated)
    full_reasoning TEXT,                 -- Complete reasoning text
    metadata_json TEXT,                  -- Extra context (news used, factors, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    actual_outcome REAL,                 -- 0 or 1 for binary, value for scalar
    outcome_correct BOOLEAN,             -- Whether prediction was correct
    brier_score REAL,                    -- Brier score for this prediction
    log_score REAL                       -- Logarithmic scoring
);

-- Accuracy metrics per agent per prediction type
CREATE TABLE IF NOT EXISTS accuracy_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER REFERENCES agents(id),
    prediction_type TEXT NOT NULL,
    market_category TEXT,                -- Optional categorization
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    avg_brier_score REAL DEFAULT 1.0,    -- Lower is better (0=perfect, 1=worst)
    avg_log_score REAL DEFAULT 0.0,
    calibration_error REAL,              -- Expected calibration error
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, prediction_type, market_category)
);

-- Trend analysis - rolling windows for improvement tracking
CREATE TABLE IF NOT EXISTS accuracy_trends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER REFERENCES agents(id),
    prediction_type TEXT NOT NULL,
    window_days INTEGER NOT NULL,        -- Size of rolling window
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    predictions_count INTEGER DEFAULT 0,
    avg_brier_score REAL,
    accuracy_rate REAL,                  -- % correct for binary
    improvement_delta REAL,              -- Change from previous window
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model improvements / calibration adjustments
CREATE TABLE IF NOT EXISTS model_adjustments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER REFERENCES agents(id),
    adjustment_type TEXT NOT NULL,       -- 'calibration', 'confidence', 'weighting'
    trigger_reason TEXT,                 -- Why adjustment was made
    before_value REAL,
    after_value REAL,
    evidence_json TEXT,                  -- Supporting data
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reverted_at TIMESTAMP,               -- If adjustment was undone
    success_metric REAL                  -- Result of adjustment
);

-- Market data cache (for replay/analysis)
CREATE TABLE IF NOT EXISTS market_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    market_data_json TEXT NOT NULL,      -- Full market state
    price_history_json TEXT,             -- Historical prices
    news_digest TEXT,                    -- Relevant news at time
    resolution_status TEXT               -- open, resolved, void
);

-- Performance logging for debugging/analysis
CREATE TABLE IF NOT EXISTS performance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER REFERENCES sessions(id),
    log_type TEXT NOT NULL,
    message TEXT,
    data_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_predictions_agent ON predictions(agent_id);
CREATE INDEX IF NOT EXISTS idx_predictions_market ON predictions(market_id);
CREATE INDEX IF NOT EXISTS idx_predictions_type ON predictions(prediction_type);
CREATE INDEX IF NOT EXISTS idx_predictions_resolved ON predictions(resolved_at);
CREATE INDEX IF NOT EXISTS idx_accuracy_agent_type ON accuracy_metrics(agent_id, prediction_type);
CREATE INDEX IF NOT EXISTS idx_trends_agent_window ON accuracy_trends(agent_id, window_days);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
"""


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Session:
    """Represents a simulation session"""
    session_uuid: str
    name: Optional[str] = None
    config: Dict[str, Any] = None
    status: str = 'active'
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    checkpoint_data: Optional[Dict] = None
    id: Optional[int] = None


@dataclass
class Agent:
    """Represents an agent in the system"""
    agent_id: str
    name: str
    model_name: str
    agent_type: str
    config: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    total_predictions: int = 0
    overall_accuracy: float = 0.0
    id: Optional[int] = None


@dataclass
class Prediction:
    """Represents a single prediction"""
    prediction_uuid: str
    session_id: int
    agent_id: int
    market_id: str
    market_question: Optional[str] = None
    prediction_type: str = 'binary'
    predicted_probability: float = 0.5
    confidence_score: Optional[float] = None
    reasoning_hash: Optional[str] = None
    reasoning_summary: Optional[str] = None
    full_reasoning: Optional[str] = None
    metadata: Optional[Dict] = None
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    actual_outcome: Optional[float] = None
    outcome_correct: Optional[bool] = None
    brier_score: Optional[float] = None
    log_score: Optional[float] = None
    id: Optional[int] = None


@dataclass
class AccuracyMetrics:
    """Accuracy tracking per agent per type"""
    agent_id: int
    prediction_type: str
    market_category: Optional[str] = None
    total_predictions: int = 0
    correct_predictions: int = 0
    avg_brier_score: float = 1.0
    avg_log_score: float = 0.0
    calibration_error: Optional[float] = None
    last_updated: Optional[datetime] = None
    id: Optional[int] = None
    
    @property
    def accuracy_rate(self) -> float:
        if self.total_predictions == 0:
            return 0.0
        return self.correct_predictions / self.total_predictions


@dataclass
class ModelAdjustment:
    """Tracks model improvements/calibrations"""
    agent_id: int
    adjustment_type: str
    trigger_reason: str
    before_value: float
    after_value: float
    evidence: Optional[Dict] = None
    applied_at: Optional[datetime] = None
    reverted_at: Optional[datetime] = None
    success_metric: Optional[float] = None
    id: Optional[int] = None


# ============================================================================
# MAIN MEMORY CLASS
# ============================================================================

class ScalesMemory:
    """
    Persistence and learning system for Scales prediction market simulations.
    
    Features:
    - SQLite-based storage with thread-safe connections
    - Session resume capability via checkpoints
    - Agent accuracy tracking with trend analysis
    - Model improvement through calibration tracking
    - Performance logging and debugging support
    """
    
    def __init__(self, db_path: str = "~/.scales/scales_memory.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_database()
    
    @property
    def _conn(self) -> sqlite3.Connection:
        """Thread-local connection"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False
            )
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA foreign_keys = ON")
        return self._local.conn
    
    def _init_database(self):
        """Initialize database schema"""
        with self._conn:
            self._conn.executescript(SCHEMA_SQL)
    
    def close(self):
        """Close thread-local connection"""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._conn.close()
            self._local.conn = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # ========================================================================
    # SESSION MANAGEMENT (Resume Capability)
    # ========================================================================
    
    def create_session(self, name: str, config: Dict[str, Any]) -> Session:
        """Create a new simulation session"""
        import uuid
        session_uuid = str(uuid.uuid4())
        
        with self._conn:
            cursor = self._conn.execute(
                """INSERT INTO sessions (session_uuid, name, config_json, status)
                   VALUES (?, ?, ?, 'active')""",
                (session_uuid, name, json.dumps(config))
            )
            session_id = cursor.lastrowid
        
        return self.get_session(session_uuid)
    
    def get_session(self, session_uuid: str) -> Optional[Session]:
        """Get session by UUID"""
        row = self._conn.execute(
            "SELECT * FROM sessions WHERE session_uuid = ?",
            (session_uuid,)
        ).fetchone()
        
        if not row:
            return None
        
        return Session(
            id=row['id'],
            session_uuid=row['session_uuid'],
            name=row['name'],
            config=json.loads(row['config_json']) if row['config_json'] else {},
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            resumed_at=row['resumed_at'],
            checkpoint_data=json.loads(row['checkpoint_data']) if row['checkpoint_data'] else None
        )
    
    def list_sessions(self, status: Optional[str] = None) -> List[Session]:
        """List all sessions, optionally filtered by status"""
        if status:
            rows = self._conn.execute(
                "SELECT * FROM sessions WHERE status = ? ORDER BY created_at DESC",
                (status,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM sessions ORDER BY created_at DESC"
            ).fetchall()
        
        return [self._row_to_session(row) for row in rows]
    
    def _row_to_session(self, row: sqlite3.Row) -> Session:
        return Session(
            id=row['id'],
            session_uuid=row['session_uuid'],
            name=row['name'],
            config=json.loads(row['config_json']) if row['config_json'] else {},
            status=row['status'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            resumed_at=row['resumed_at'],
            checkpoint_data=json.loads(row['checkpoint_data']) if row['checkpoint_data'] else None
        )
    
    def update_session_status(self, session_uuid: str, status: str):
        """Update session status"""
        with self._conn:
            self._conn.execute(
                """UPDATE sessions SET status = ?, updated_at = CURRENT_TIMESTAMP
                   WHERE session_uuid = ?""",
                (status, session_uuid)
            )
    
    def save_checkpoint(self, session_uuid: str, checkpoint_data: Dict[str, Any]):
        """Save checkpoint for session resume"""
        with self._conn:
            self._conn.execute(
                """UPDATE sessions 
                   SET checkpoint_data = ?, 
                       resumed_at = CURRENT_TIMESTAMP,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE session_uuid = ?""",
                (json.dumps(checkpoint_data), session_uuid)
            )
    
    def load_checkpoint(self, session_uuid: str) -> Optional[Dict[str, Any]]:
        """Load checkpoint data for session resume"""
        session = self.get_session(session_uuid)
        return session.checkpoint_data if session else None
    
    # ========================================================================
    # AGENT MANAGEMENT
    # ========================================================================
    
    def register_agent(self, agent_id: str, name: str, model_name: str,
                       agent_type: str, config: Optional[Dict] = None) -> Agent:
        """Register a new agent"""
        with self._conn:
            try:
                cursor = self._conn.execute(
                    """INSERT INTO agents (agent_id, name, model_name, agent_type, config_json)
                       VALUES (?, ?, ?, ?, ?)""",
                    (agent_id, name, model_name, agent_type, json.dumps(config) if config else None)
                )
            except sqlite3.IntegrityError:
                # Agent already exists, return existing
                return self.get_agent(agent_id)
        
        return self.get_agent(agent_id)
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        row = self._conn.execute(
            "SELECT * FROM agents WHERE agent_id = ?",
            (agent_id,)
        ).fetchone()
        
        if not row:
            return None
        
        return self._row_to_agent(row)
    
    def list_agents(self) -> List[Agent]:
        """List all registered agents"""
        rows = self._conn.execute(
            "SELECT * FROM agents ORDER BY created_at DESC"
        ).fetchall()
        
        return [self._row_to_agent(row) for row in rows]
    
    def _row_to_agent(self, row: sqlite3.Row) -> Agent:
        return Agent(
            id=row['id'],
            agent_id=row['agent_id'],
            name=row['name'],
            model_name=row['model_name'],
            agent_type=row['agent_type'],
            config=json.loads(row['config_json']) if row['config_json'] else None,
            created_at=row['created_at'],
            total_predictions=row['total_predictions'],
            overall_accuracy=row['overall_accuracy']
        )
    
    def update_agent_stats(self, agent_id: str):
        """Recalculate and update agent overall stats"""
        agent = self.get_agent(agent_id)
        if not agent:
            return
        
        # Calculate overall accuracy from predictions
        row = self._conn.execute(
            """SELECT COUNT(*) as total,
                       SUM(CASE WHEN outcome_correct = 1 THEN 1 ELSE 0 END) as correct,
                       AVG(brier_score) as avg_brier
                FROM predictions 
                WHERE agent_id = ? AND resolved_at IS NOT NULL""",
            (agent.id,)
        ).fetchone()
        
        total = row['total'] or 0
        correct = row['correct'] or 0
        avg_brier = row['avg_brier'] or 1.0
        accuracy = correct / total if total > 0 else 0.0
        
        with self._conn:
            self._conn.execute(
                """UPDATE agents 
                   SET total_predictions = ?, overall_accuracy = ?
                   WHERE id = ?""",
                (total, accuracy, agent.id)
            )
    
    # ========================================================================
    # PREDICTION RECORDING
    # ========================================================================
    
    def record_prediction(self, prediction: Prediction) -> str:
        """Record a new prediction"""
        import uuid
        
        if not prediction.prediction_uuid:
            prediction.prediction_uuid = str(uuid.uuid4())
        
        # Hash reasoning for deduplication
        if prediction.full_reasoning and not prediction.reasoning_hash:
            prediction.reasoning_hash = hashlib.sha256(
                prediction.full_reasoning.encode()
            ).hexdigest()[:32]
        
        with self._conn:
            self._conn.execute(
                """INSERT INTO predictions 
                   (prediction_uuid, session_id, agent_id, market_id, market_question,
                    prediction_type, predicted_probability, confidence_score,
                    reasoning_hash, reasoning_summary, full_reasoning, metadata_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    prediction.prediction_uuid,
                    prediction.session_id,
                    prediction.agent_id,
                    prediction.market_id,
                    prediction.market_question,
                    prediction.prediction_type,
                    prediction.predicted_probability,
                    prediction.confidence_score,
                    prediction.reasoning_hash,
                    prediction.reasoning_summary,
                    prediction.full_reasoning,
                    json.dumps(prediction.metadata) if prediction.metadata else None
                )
            )
        
        return prediction.prediction_uuid
    
    def get_prediction(self, prediction_uuid: str) -> Optional[Prediction]:
        """Get prediction by UUID"""
        row = self._conn.execute(
            "SELECT * FROM predictions WHERE prediction_uuid = ?",
            (prediction_uuid,)
        ).fetchone()
        
        if not row:
            return None
        
        return self._row_to_prediction(row)
    
    def _row_to_prediction(self, row: sqlite3.Row) -> Prediction:
        return Prediction(
            id=row['id'],
            prediction_uuid=row['prediction_uuid'],
            session_id=row['session_id'],
            agent_id=row['agent_id'],
            market_id=row['market_id'],
            market_question=row['market_question'],
            prediction_type=row['prediction_type'],
            predicted_probability=row['predicted_probability'],
            confidence_score=row['confidence_score'],
            reasoning_hash=row['reasoning_hash'],
            reasoning_summary=row['reasoning_summary'],
            full_reasoning=row['full_reasoning'],
            metadata=json.loads(row['metadata_json']) if row['metadata_json'] else None,
            created_at=row['created_at'],
            resolved_at=row['resolved_at'],
            actual_outcome=row['actual_outcome'],
            outcome_correct=row['outcome_correct'],
            brier_score=row['brier_score'],
            log_score=row['log_score']
        )
    
    def resolve_prediction(self, prediction_uuid: str, actual_outcome: float,
                          correct_threshold: float = 0.5):
        """
        Mark prediction as resolved with actual outcome.
        Automatically calculates brier score and correctness.
        """
        prediction = self.get_prediction(prediction_uuid)
        if not prediction:
            raise ValueError(f"Prediction {prediction_uuid} not found")
        
        # Calculate Brier score: (predicted - actual)^2
        brier = (prediction.predicted_probability - actual_outcome) ** 2
        
        # Determine correctness for binary predictions
        if prediction.prediction_type == 'binary':
            # Predicted > 0.5 means predicted YES
            predicted_yes = prediction.predicted_probability > correct_threshold
            actual_yes = actual_outcome > correct_threshold
            correct = predicted_yes == actual_yes
        else:
            # For scalar, use a tolerance-based approach
            correct = brier < 0.25  # Within reasonable range
        
        # Log score (handle edge cases)
        eps = 1e-10
        prob = max(min(prediction.predicted_probability, 1 - eps), eps)
        log_score = actual_outcome * (prob) + (1 - actual_outcome) * (1 - prob)
        log_score = log_score if log_score > 0 else eps
        log_score = log_score  # Raw probability, can be transformed to log if needed
        
        with self._conn:
            self._conn.execute(
                """UPDATE predictions 
                   SET resolved_at = CURRENT_TIMESTAMP,
                       actual_outcome = ?,
                       outcome_correct = ?,
                       brier_score = ?,
                       log_score = ?
                   WHERE prediction_uuid = ?""",
                (actual_outcome, correct, brier, log_score, prediction_uuid)
            )
        
        # Update accuracy metrics
        self._update_accuracy_metrics(prediction.agent_id, prediction.prediction_type)
        
        # Update agent overall stats
        agent_row = self._conn.execute(
            "SELECT agent_id FROM agents WHERE id = ?",
            (prediction.agent_id,)
        ).fetchone()
        if agent_row:
            self.update_agent_stats(agent_row['agent_id'])
        
        return brier, correct
    
    def get_unresolved_predictions(self, agent_id: Optional[int] = None) -> List[Prediction]:
        """Get all unresolved predictions, optionally filtered by agent"""
        if agent_id:
            rows = self._conn.execute(
                """SELECT * FROM predictions 
                   WHERE resolved_at IS NULL AND agent_id = ?
                   ORDER BY created_at DESC""",
                (agent_id,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT * FROM predictions 
                   WHERE resolved_at IS NULL
                   ORDER BY created_at DESC"""
            ).fetchall()
        
        return [self._row_to_prediction(row) for row in rows]
    
    # ========================================================================
    # ACCURACY TRACKING
    # ========================================================================
    
    def _update_accuracy_metrics(self, agent_id: int, prediction_type: str,
                                  market_category: Optional[str] = None):
        """Recalculate accuracy metrics for agent/type combination"""
        
        query = """SELECT 
                       COUNT(*) as total,
                       SUM(CASE WHEN outcome_correct = 1 THEN 1 ELSE 0 END) as correct,
                       AVG(brier_score) as avg_brier,
                       AVG(log_score) as avg_log
                   FROM predictions 
                   WHERE agent_id = ? AND prediction_type = ? AND resolved_at IS NOT NULL"""
        params = [agent_id, prediction_type]
        
        if market_category:
            query += " AND json_extract(metadata_json, '$.category') = ?"
            params.append(market_category)
        
        row = self._conn.execute(query, params).fetchone()
        
        total = row['total'] or 0
        correct = row['correct'] or 0
        avg_brier = row['avg_brier'] or 1.0
        avg_log = row['avg_log'] or 0.0
        
        # Simple calibration error estimate (expected vs observed)
        calibration_error = self._calculate_calibration_error(agent_id, prediction_type)
        
        with self._conn:
            self._conn.execute(
                """INSERT INTO accuracy_metrics 
                   (agent_id, prediction_type, market_category, total_predictions,
                    correct_predictions, avg_brier_score, avg_log_score, calibration_error)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(agent_id, prediction_type, market_category) 
                   DO UPDATE SET
                       total_predictions = excluded.total_predictions,
                       correct_predictions = excluded.correct_predictions,
                       avg_brier_score = excluded.avg_brier_score,
                       avg_log_score = excluded.avg_log_score,
                       calibration_error = excluded.calibration_error,
                       last_updated = CURRENT_TIMESTAMP""",
                (agent_id, prediction_type, market_category, total, correct,
                 avg_brier, avg_log, calibration_error)
            )
    
    def _calculate_calibration_error(self, agent_id: int, prediction_type: str) -> float:
        """Calculate expected calibration error (ECE)"""
        # Bin predictions by confidence and compare to actual outcomes
        rows = self._conn.execute(
            """SELECT predicted_probability, actual_outcome
               FROM predictions 
               WHERE agent_id = ? AND prediction_type = ? 
               AND resolved_at IS NOT NULL""",
            (agent_id, prediction_type)
        ).fetchall()
        
        if len(rows) < 10:
            return None  # Not enough data
        
        # Simple 5-bin ECE
        bins = {i: {'pred': [], 'actual': []} for i in range(5)}
        for row in rows:
            bin_idx = min(int(row['predicted_probability'] * 5), 4)
            bins[bin_idx]['pred'].append(row['predicted_probability'])
            bins[bin_idx]['actual'].append(row['actual_outcome'])
        
        ece = 0.0
        total = len(rows)
        for bin_data in bins.values():
            if bin_data['pred']:
                bin_size = len(bin_data['pred'])
                avg_conf = sum(bin_data['pred']) / bin_size
                avg_actual = sum(bin_data['actual']) / bin_size
                ece += (bin_size / total) * abs(avg_conf - avg_actual)
        
        return ece
    
    def get_accuracy_metrics(self, agent_id: int, 
                             prediction_type: Optional[str] = None) -> List[AccuracyMetrics]:
        """Get accuracy metrics for an agent"""
        if prediction_type:
            rows = self._conn.execute(
                """SELECT * FROM accuracy_metrics 
                   WHERE agent_id = ? AND prediction_type = ?""",
                (agent_id, prediction_type)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT * FROM accuracy_metrics WHERE agent_id = ?",
                (agent_id,)
            ).fetchall()
        
        return [self._row_to_accuracy_metrics(row) for row in rows]
    
    def _row_to_accuracy_metrics(self, row: sqlite3.Row) -> AccuracyMetrics:
        return AccuracyMetrics(
            id=row['id'],
            agent_id=row['agent_id'],
            prediction_type=row['prediction_type'],
            market_category=row['market_category'],
            total_predictions=row['total_predictions'],
            correct_predictions=row['correct_predictions'],
            avg_brier_score=row['avg_brier_score'],
            avg_log_score=row['avg_log_score'],
            calibration_error=row['calibration_error'],
            last_updated=row['last_updated']
        )
    
    def get_leaderboard(self, prediction_type: Optional[str] = None,
                       min_predictions: int = 5) -> List[Dict]:
        """Get agent leaderboard sorted by accuracy"""
        if prediction_type:
            rows = self._conn.execute(
                """SELECT a.name, a.model_name, a.agent_type,
                          am.total_predictions, am.correct_predictions,
                          am.avg_brier_score, am.calibration_error
                   FROM agents a
                   JOIN accuracy_metrics am ON a.id = am.agent_id
                   WHERE am.prediction_type = ? AND am.total_predictions >= ?
                   ORDER BY am.avg_brier_score ASC""",
                (prediction_type, min_predictions)
            ).fetchall()
        else:
            rows = self._conn.execute(
                """SELECT a.name, a.model_name, a.agent_type,
                          a.total_predictions, a.overall_accuracy as correct_predictions,
                          NULL as avg_brier_score, NULL as calibration_error
                   FROM agents a
                   WHERE a.total_predictions >= ?
                   ORDER BY a.overall_accuracy DESC""",
                (min_predictions,)
            ).fetchall()
        
        return [dict(row) for row in rows]
    
    # ========================================================================
    # TREND ANALYSIS
    # ========================================================================
    
    def calculate_trends(self, agent_id: int, window_days: int = 7) -> List[Dict]:
        """Calculate rolling window trends for agent accuracy"""
        
        # Get date range
        row = self._conn.execute(
            """SELECT MIN(created_at) as start, MAX(created_at) as end
               FROM predictions WHERE agent_id = ? AND resolved_at IS NOT NULL""",
            (agent_id,)
        ).fetchone()
        
        if not row or not row['start']:
            return []
        
        start_date = datetime.fromisoformat(row['start']) if isinstance(row['start'], str) else row['start']
        end_date = datetime.fromisoformat(row['end']) if isinstance(row['end'], str) else row['end']
        
        trends = []
        current = start_date
        
        while current + timedelta(days=window_days) <= end_date + timedelta(days=1):
            window_end = current + timedelta(days=window_days)
            
            row = self._conn.execute(
                """SELECT 
                       COUNT(*) as total,
                       AVG(brier_score) as avg_brier,
                       AVG(CASE WHEN outcome_correct = 1 THEN 1.0 ELSE 0.0 END) as accuracy
                   FROM predictions 
                   WHERE agent_id = ? 
                   AND resolved_at BETWEEN ? AND ?""",
                (agent_id, current, window_end)
            ).fetchone()
            
            if row and row['total'] > 0:
                trends.append({
                    'period_start': current,
                    'period_end': window_end,
                    'predictions_count': row['total'],
                    'avg_brier_score': row['avg_brier'],
                    'accuracy_rate': row['accuracy']
                })
            
            current += timedelta(days=window_days)
        
        # Calculate improvement deltas
        for i in range(1, len(trends)):
            trends[i]['improvement_delta'] = (
                trends[i-1]['avg_brier_score'] - trends[i]['avg_brier_score']
            )
        
        return trends
    
    def save_trend(self, agent_id: int, prediction_type: str, window_days: int,
                   trend_data: Dict):
        """Save calculated trend to database"""
        with self._conn:
            self._conn.execute(
                """INSERT INTO accuracy_trends 
                   (agent_id, prediction_type, window_days, period_start, period_end,
                    predictions_count, avg_brier_score, accuracy_rate, improvement_delta)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    agent_id, prediction_type, window_days,
                    trend_data['period_start'], trend_data['period_end'],
                    trend_data['predictions_count'], trend_data['avg_brier_score'],
                    trend_data['accuracy_rate'], trend_data.get('improvement_delta')
                )
            )
    
    # ========================================================================
    # MODEL IMPROVEMENT TRACKING
    # ========================================================================
    
    def record_adjustment(self, agent_id: int, adjustment_type: str,
                         trigger_reason: str, before_value: float,
                         after_value: float, evidence: Optional[Dict] = None) -> int:
        """Record a model adjustment for tracking improvement"""
        with self._conn:
            cursor = self._conn.execute(
                """INSERT INTO model_adjustments 
                   (agent_id, adjustment_type, trigger_reason, before_value,
                    after_value, evidence_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (agent_id, adjustment_type, trigger_reason, before_value,
                 after_value, json.dumps(evidence) if evidence else None)
            )
            return cursor.lastrowid
    
    def update_adjustment_success(self, adjustment_id: int, success_metric: float):
        """Update the success metric for an adjustment"""
        with self._conn:
            self._conn.execute(
                """UPDATE model_adjustments 
                   SET success_metric = ? WHERE id = ?""",
                (success_metric, adjustment_id)
            )
    
    def get_adjustments(self, agent_id: Optional[int] = None,
                       adjustment_type: Optional[str] = None) -> List[ModelAdjustment]:
        """Get model adjustment history"""
        query = "SELECT * FROM model_adjustments WHERE 1=1"
        params = []
        
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        if adjustment_type:
            query += " AND adjustment_type = ?"
            params.append(adjustment_type)
        
        query += " ORDER BY applied_at DESC"
        
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_adjustment(row) for row in rows]
    
    def _row_to_adjustment(self, row: sqlite3.Row) -> ModelAdjustment:
        return ModelAdjustment(
            id=row['id'],
            agent_id=row['agent_id'],
            adjustment_type=row['adjustment_type'],
            trigger_reason=row['trigger_reason'],
            before_value=row['before_value'],
            after_value=row['after_value'],
            evidence=json.loads(row['evidence_json']) if row['evidence_json'] else None,
            applied_at=row['applied_at'],
            reverted_at=row['reverted_at'],
            success_metric=row['success_metric']
        )
    
    def get_improvement_summary(self, agent_id: int) -> Dict:
        """Get summary of model improvements over time"""
        # Get baseline and current performance
        baseline = self._conn.execute(
            """SELECT AVG(brier_score) as score
               FROM predictions WHERE agent_id = ? 
               AND resolved_at IS NOT NULL
               ORDER BY resolved_at LIMIT 10""",
            (agent_id,)
        ).fetchone()
        
        recent = self._conn.execute(
            """SELECT AVG(brier_score) as score
               FROM predictions WHERE agent_id = ? 
               AND resolved_at IS NOT NULL
               ORDER BY resolved_at DESC LIMIT 10""",
            (agent_id,)
        ).fetchone()
        
        adjustments = self._conn.execute(
            """SELECT COUNT(*) as count,
                       AVG(success_metric) as avg_success
               FROM model_adjustments WHERE agent_id = ?""",
            (agent_id,)
        ).fetchone()
        
        return {
            'baseline_brier': baseline['score'] if baseline else None,
            'recent_brier': recent['score'] if recent else None,
            'improvement': (baseline['score'] - recent['score']) if baseline and recent else None,
            'total_adjustments': adjustments['count'] or 0,
            'avg_adjustment_success': adjustments['avg_success']
        }
    
    # ========================================================================
    # PERFORMANCE LOGGING
    # ========================================================================
    
    def log_performance(self, log_type: str, message: str,
                       session_id: Optional[int] = None,
                       data: Optional[Dict] = None):
        """Log performance data for debugging/analysis"""
        with self._conn:
            self._conn.execute(
                """INSERT INTO performance_log (session_id, log_type, message, data_json)
                   VALUES (?, ?, ?, ?)""",
                (session_id, log_type, message, json.dumps(data) if data else None)
            )
    
    def get_logs(self, session_id: Optional[int] = None,
                log_type: Optional[str] = None,
                limit: int = 100) -> List[Dict]:
        """Get performance logs"""
        query = "SELECT * FROM performance_log WHERE 1=1"
        params = []
        
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
        if log_type:
            query += " AND log_type = ?"
            params.append(log_type)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        rows = self._conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    
    # ========================================================================
    # ANALYTICS QUERIES
    # ========================================================================
    
    def get_prediction_distribution(self, agent_id: Optional[int] = None) -> Dict:
        """Get distribution of prediction probabilities"""
        query = """SELECT 
                       CASE 
                           WHEN predicted_probability < 0.2 THEN '0-20%'
                           WHEN predicted_probability < 0.4 THEN '20-40%'
                           WHEN predicted_probability < 0.6 THEN '40-60%'
                           WHEN predicted_probability < 0.8 THEN '60-80%'
                           ELSE '80-100%'
                       END as bucket,
                       COUNT(*) as count
                   FROM predictions WHERE 1=1"""
        params = []
        
        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)
        
        query += " GROUP BY bucket"
        
        rows = self._conn.execute(query, params).fetchall()
        return {row['bucket']: row['count'] for row in rows}
    
    def get_calibration_data(self, agent_id: int, bins: int = 10) -> List[Dict]:
        """Get calibration data for plotting reliability diagrams"""
        rows = self._conn.execute(
            """SELECT predicted_probability, actual_outcome, outcome_correct
               FROM predictions 
               WHERE agent_id = ? AND resolved_at IS NOT NULL""",
            (agent_id,)
        ).fetchall()
        
        # Bin the predictions
        bin_data = {i: {'pred': [], 'actual': [], 'correct': 0, 'total': 0} 
                   for i in range(bins)}
        
        for row in rows:
            bin_idx = min(int(row['predicted_probability'] * bins), bins - 1)
            bin_data[bin_idx]['pred'].append(row['predicted_probability'])
            bin_data[bin_idx]['actual'].append(row['actual_outcome'])
            bin_data[bin_idx]['total'] += 1
            if row['outcome_correct']:
                bin_data[bin_idx]['correct'] += 1
        
        result = []
        for i, data in bin_data.items():
            if data['total'] > 0:
                result.append({
                    'bin_center': (i + 0.5) / bins,
                    'bin_range': f"{i/bins:.1%}-{(i+1)/bins:.1%}",
                    'avg_confidence': sum(data['pred']) / len(data['pred']),
                    'avg_outcome': sum(data['actual']) / len(data['actual']),
                    'accuracy': data['correct'] / data['total'],
                    'count': data['total']
                })
        
        return result
    
    def export_session_data(self, session_uuid: str) -> Dict:
        """Export all data for a session"""
        session = self.get_session(session_uuid)
        if not session:
            return {}
        
        predictions = self._conn.execute(
            """SELECT p.*, a.agent_id as agent_uuid, a.name as agent_name
               FROM predictions p
               JOIN agents a ON p.agent_id = a.id
               WHERE p.session_id = ?""",
            (session.id,)
        ).fetchall()
        
        return {
            'session': asdict(session),
            'predictions': [dict(row) for row in predictions],
            'export_time': datetime.now().isoformat()
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def init_memory(db_path: str = "~/.scales/scales_memory.db") -> ScalesMemory:
    """Initialize and return a ScalesMemory instance"""
    return ScalesMemory(db_path)


def migrate_from_json(memory: ScalesMemory, json_path: str):
    """Migrate data from old JSON format to SQLite"""
    import json as json_lib
    
    path = Path(json_path).expanduser()
    if not path.exists():
        return
    
    with open(path) as f:
        data = json_lib.load(f)
    
    # Migrate agents
    for agent_data in data.get('agents', []):
        memory.register_agent(
            agent_id=agent_data['id'],
            name=agent_data['name'],
            model_name=agent_data.get('model', 'unknown'),
            agent_type=agent_data.get('type', 'general'),
            config=agent_data.get('config')
        )
    
    # Migrate predictions
    for pred_data in data.get('predictions', []):
        agent = memory.get_agent(pred_data['agent_id'])
        if agent:
            pred = Prediction(
                prediction_uuid=pred_data.get('uuid'),
                session_id=pred_data.get('session_id', 0),
                agent_id=agent.id,
                market_id=pred_data['market_id'],
                market_question=pred_data.get('question'),
                prediction_type=pred_data.get('type', 'binary'),
                predicted_probability=pred_data['probability'],
                confidence_score=pred_data.get('confidence'),
                full_reasoning=pred_data.get('reasoning'),
                metadata=pred_data.get('metadata'),
                actual_outcome=pred_data.get('actual_outcome'),
                outcome_correct=pred_data.get('correct'),
                brier_score=pred_data.get('brier_score')
            )
            memory.record_prediction(pred)
    
    print(f"Migration complete: {json_path}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example usage
    with ScalesMemory() as memory:
        # Create a session
        session = memory.create_session(
            name="Test Simulation",
            config={"markets": ["politics", "sports"], "budget": 1000}
        )
        print(f"Created session: {session.session_uuid}")
        
        # Register an agent
        agent = memory.register_agent(
            agent_id="analyst_001",
            name="Alpha Analyst",
            model_name="claude-3-opus",
            agent_type="researcher",
            config={"temperature": 0.7}
        )
        print(f"Registered agent: {agent.agent_id}")
        
        # Record a prediction
        pred = Prediction(
            session_id=session.id,
            agent_id=agent.id,
            market_id="market_123",
            market_question="Will it rain tomorrow?",
            prediction_type="binary",
            predicted_probability=0.75,
            confidence_score=0.8,
            full_reasoning="Based on weather patterns...",
            metadata={"source": "weather_api", "temperature": 22}
        )
        pred_uuid = memory.record_prediction(pred)
        print(f"Recorded prediction: {pred_uuid}")
        
        # Resolve the prediction
        brier, correct = memory.resolve_prediction(pred_uuid, actual_outcome=1.0)
        print(f"Resolved: Brier={brier:.4f}, Correct={correct}")
        
        # Check accuracy metrics
        metrics = memory.get_accuracy_metrics(agent.id)
        print(f"Accuracy metrics: {metrics}")
        
        # Get leaderboard
        leaderboard = memory.get_leaderboard()
        print(f"Leaderboard: {leaderboard}")
