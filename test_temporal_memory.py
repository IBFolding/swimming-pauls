"""
Tests for Temporal Memory System

Tests cover:
1. Belief formation and storage
2. Belief decay over time
3. Evidence reinforcement and contradiction
4. Temporal context generation
5. Integration with PaulWorld

Run with: python -m pytest test_temporal_memory.py -v
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from temporal_memory import (
    TemporalMemory,
    TemporalMemoryManager,
    Belief,
    BeliefStatus,
    Evidence,
    TemporalContext,
    create_temporal_prediction_reasoning,
    simulate_belief_evolution,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_memory(tmp_path):
    """Create a temporal memory instance for testing."""
    db_path = tmp_path / "test_temporal.db"
    return TemporalMemory(
        paul_name="TestPaul",
        decay_rate=0.05,
        reinforcement_rate=0.15,
        db_path=str(db_path)
    )


@pytest.fixture
def memory_no_db():
    """Create a temporal memory without database."""
    return TemporalMemory(
        paul_name="TestPaul",
        decay_rate=0.05,
        reinforcement_rate=0.15,
        db_path=None
    )


@pytest.fixture
def manager(tmp_path):
    """Create a temporal memory manager."""
    db_path = tmp_path / "test_manager.db"
    return TemporalMemoryManager(db_path=str(db_path))


# ============================================================================
# Belief Formation Tests
# ============================================================================

class TestBeliefFormation:
    """Tests for forming and retrieving beliefs."""
    
    def test_form_basic_belief(self, memory_no_db):
        """Test forming a simple belief."""
        belief = memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin will rise",
            initial_confidence=0.7
        )
        
        assert belief.topic == "BTC"
        assert belief.proposition == "Bitcoin will rise"
        assert belief.confidence == 0.7
        assert belief.status == BeliefStatus.ACTIVE
        assert belief.evidence_count == 0
        assert belief.contradiction_count == 0
    
    def test_retrieve_belief(self, memory_no_db):
        """Test retrieving a formed belief."""
        memory_no_db.form_belief(
            topic="ETH",
            proposition="Ethereum will increase",
            initial_confidence=0.6
        )
        
        retrieved = memory_no_db.get_belief("ETH")
        
        assert retrieved is not None
        assert retrieved.topic == "ETH"
        assert retrieved.proposition == "Ethereum will increase"
    
    def test_retrieve_nonexistent_belief(self, memory_no_db):
        """Test retrieving a belief that doesn't exist."""
        retrieved = memory_no_db.get_belief("NONEXISTENT")
        assert retrieved is None
    
    def test_belief_history(self, memory_no_db):
        """Test retrieving belief history."""
        # Form initial belief
        memory_no_db.form_belief(
            topic="SOL",
            proposition="Solana is bullish",
            initial_confidence=0.5
        )
        
        # Form revised belief
        memory_no_db.form_belief(
            topic="SOL",
            proposition="Solana is bearish",
            initial_confidence=0.6
        )
        
        history = memory_no_db.get_belief_history("SOL")
        
        assert len(history) == 2
        assert history[0].proposition == "Solana is bearish"  # Newest first
        assert history[1].proposition == "Solana is bullish"
    
    def test_belief_revision_archives_old(self, memory_no_db):
        """Test that forming new belief archives old one."""
        old_belief = memory_no_db.form_belief(
            topic="BTC",
            proposition="Old view",
            initial_confidence=0.5
        )
        
        new_belief = memory_no_db.form_belief(
            topic="BTC",
            proposition="New view",
            initial_confidence=0.6
        )
        
        # Old belief should be marked as revised
        assert old_belief.status == BeliefStatus.REVISED
        # New belief should be active
        assert new_belief.status == BeliefStatus.ACTIVE


# ============================================================================
# Evidence and Reinforcement Tests
# ============================================================================

class TestEvidenceReinforcement:
    """Tests for evidence-based belief updates."""
    
    def test_supporting_evidence_increases_confidence(self, memory_no_db):
        """Test that supporting evidence increases confidence."""
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin will rise",
            initial_confidence=0.5
        )
        
        initial_confidence = memory_no_db.get_belief("BTC").confidence
        
        memory_no_db.add_evidence(
            topic="BTC",
            content="Positive market news",
            impact=0.8,
            reliability=0.9
        )
        
        updated = memory_no_db.get_belief("BTC")
        assert updated.confidence > initial_confidence
        assert updated.evidence_count == 1
        assert updated.status == BeliefStatus.REINFORCED
    
    def test_contradicting_evidence_decreases_confidence(self, memory_no_db):
        """Test that contradicting evidence decreases confidence."""
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin will rise",
            initial_confidence=0.8
        )
        
        initial_confidence = memory_no_db.get_belief("BTC").confidence
        
        memory_no_db.add_evidence(
            topic="BTC",
            content="Negative regulatory news",
            impact=-0.6,
            reliability=0.8
        )
        
        updated = memory_no_db.get_belief("BTC", include_challenged=True)
        assert updated is not None
        assert updated.confidence < initial_confidence
        assert updated.contradiction_count == 1
        assert updated.status in [BeliefStatus.CHALLENGED, BeliefStatus.ABANDONED]
    
    def test_strong_contradiction_abandons_belief(self, memory_no_db):
        """Test that strong contradiction can abandon a belief."""
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin will rise",
            initial_confidence=0.2  # Very low initial confidence
        )
        
        memory_no_db.add_evidence(
            topic="BTC",
            content="Major crash",
            impact=-0.9,
            reliability=0.95
        )
        
        updated = memory_no_db.get_belief("BTC", include_challenged=True)
        assert updated is not None
        # Strong contradiction should either challenge or abandon
        assert updated.status in [BeliefStatus.ABANDONED, BeliefStatus.CHALLENGED]
        assert updated.confidence < 0.2  # Confidence should drop
    
    def test_evidence_tracks_in_history(self, memory_no_db):
        """Test that evidence is tracked in revision history."""
        memory_no_db.form_belief(
            topic="ETH",
            proposition="Ethereum bullish",
            initial_confidence=0.5
        )
        
        memory_no_db.add_evidence(
            topic="ETH",
            content="Upgrade successful",
            impact=0.7,
            reliability=0.8
        )
        
        belief = memory_no_db.get_belief("ETH")
        history = belief.revision_history
        
        # Should have formation event and evidence event
        assert len(history) >= 2
        assert any(e.get('event') == 'evidence_supporting' for e in history)


# ============================================================================
# Decay Tests
# ============================================================================

class TestBeliefDecay:
    """Tests for time-based belief decay."""
    
    def test_belief_decays_over_time(self, memory_no_db):
        """Test that beliefs decay after time passes."""
        # Form belief at specific time
        start_time = datetime(2024, 1, 1, 12, 0)
        belief = memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin will rise",
            initial_confidence=0.8,
            timestamp=start_time
        )
        
        # Update timestamp to 48 hours later
        belief.last_updated = start_time  # Ensure last_updated is set
        
        later_time = start_time + timedelta(hours=48)
        decayed = memory_no_db.decay_beliefs(later_time)
        
        assert len(decayed) > 0
        assert decayed[0].confidence < 0.8
    
    def test_decay_only_after_24_hours(self, memory_no_db):
        """Test that decay only happens after 24 hours."""
        start_time = datetime(2024, 1, 1, 12, 0)
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin will rise",
            initial_confidence=0.8,
            timestamp=start_time
        )
        
        # Only 12 hours later - should not decay
        later_time = start_time + timedelta(hours=12)
        decayed = memory_no_db.decay_beliefs(later_time)
        
        assert len(decayed) == 0
    
    def test_decay_can_abandon_belief(self, memory_no_db):
        """Test that severe decay can abandon a belief."""
        start_time = datetime(2024, 1, 1, 12, 0)
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin will rise",
            initial_confidence=0.2,  # Low initial confidence
            timestamp=start_time
        )
        
        # Much later - severe decay
        much_later = start_time + timedelta(days=30)
        memory_no_db.decay_beliefs(much_later)
        
        belief = memory_no_db.get_belief("BTC")
        if belief:
            assert belief.status == BeliefStatus.ABANDONED


# ============================================================================
# Temporal Context Tests
# ============================================================================

class TestTemporalContext:
    """Tests for temporal context generation."""
    
    def test_temporal_context_creation(self, memory_no_db):
        """Test creating temporal context."""
        start_time = datetime(2024, 1, 1, 12, 0)
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin bullish",
            initial_confidence=0.6,
            timestamp=start_time
        )
        
        context = memory_no_db.get_temporal_context("BTC", current_time=start_time)
        
        assert context is not None
        assert context.current_belief.topic == "BTC"
        assert context.belief_shift == 0.0  # No shift yet
    
    def test_temporal_context_shows_evolution(self, memory_no_db):
        """Test that temporal context captures belief evolution."""
        start_time = datetime(2024, 1, 1, 12, 0)
        
        # Initial belief
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin neutral",
            initial_confidence=0.5,
            timestamp=start_time
        )
        
        initial_confidence = memory_no_db.get_belief("BTC").confidence
        
        # Evidence strengthens it
        later_time = start_time + timedelta(hours=6)
        memory_no_db.add_evidence(
            topic="BTC",
            content="Strong momentum",
            impact=0.8,
            timestamp=later_time
        )
        
        context = memory_no_db.get_temporal_context("BTC", current_time=later_time)
        
        # Context should show updated belief with higher confidence
        assert context.current_belief.confidence > initial_confidence
        # The belief was updated in place, so we check the revision history
        assert len(context.current_belief.revision_history) >= 2  # Formation + evidence
    
    def test_format_temporal_reasoning_recent(self, memory_no_db):
        """Test formatting temporal reasoning for recent belief."""
        now = datetime.now()
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Bitcoin bullish",
            initial_confidence=0.7,
            timestamp=now
        )
        
        context = memory_no_db.get_temporal_context("BTC", now)
        reasoning = context.format_temporal_reasoning()
        
        assert "believe" in reasoning.lower()
        assert "confidence" in reasoning.lower()
    
    def test_format_temporal_reasoning_with_history(self, memory_no_db):
        """Test formatting with historical beliefs."""
        start_time = datetime(2024, 1, 1, 12, 0)
        
        memory_no_db.form_belief(
            topic="BTC",
            proposition="Old view",
            initial_confidence=0.5,
            timestamp=start_time
        )
        
        later_time = start_time + timedelta(days=3)
        memory_no_db.form_belief(
            topic="BTC",
            proposition="New view",
            initial_confidence=0.8,
            timestamp=later_time
        )
        
        context = memory_no_db.get_temporal_context("BTC", later_time)
        reasoning = context.format_temporal_reasoning()
        
        # Should mention the time difference
        assert "3 days ago" in reasoning or "ago" in reasoning


# ============================================================================
# Manager Tests
# ============================================================================

class TestTemporalMemoryManager:
    """Tests for the temporal memory manager."""
    
    def test_get_memory_creates_new(self, manager):
        """Test that get_memory creates memory for new Paul."""
        memory = manager.get_memory("Paul1")
        
        assert memory is not None
        assert memory.paul_name == "Paul1"
        assert "Paul1" in manager.memories
    
    def test_get_memory_returns_existing(self, manager):
        """Test that get_memory returns existing memory."""
        memory1 = manager.get_memory("Paul1")
        memory1.form_belief("BTC", "Bitcoin bullish", 0.7)
        
        memory2 = manager.get_memory("Paul1")
        
        assert memory1 is memory2
        assert memory2.get_belief("BTC") is not None
    
    def test_cross_paul_consensus(self, manager):
        """Test calculating consensus across Pauls."""
        # Paul1 believes one thing
        mem1 = manager.get_memory("Paul1")
        mem1.form_belief("BTC", "Bitcoin will rise", 0.8)
        
        # Paul2 believes the same
        mem2 = manager.get_memory("Paul2")
        mem2.form_belief("BTC", "Bitcoin will rise", 0.7)
        
        consensus = manager.get_cross_paul_consensus("BTC")
        
        assert consensus['consensus'] in ['strong', 'moderate']
        assert consensus['pauls_count'] == 2
        assert consensus['dominant_view'] == "Bitcoin will rise"
    
    def test_cross_paul_consensus_divergent(self, manager):
        """Test consensus when Pauls disagree."""
        mem1 = manager.get_memory("Paul1")
        mem1.form_belief("BTC", "Bitcoin will rise", 0.8)
        
        mem2 = manager.get_memory("Paul2")
        mem2.form_belief("BTC", "Bitcoin will fall", 0.7)
        
        consensus = manager.get_cross_paul_consensus("BTC")
        
        assert consensus['consensus'] == 'divergent'
    
    def test_social_influence_adopts_belief(self, manager):
        """Test that influence can adopt new belief."""
        # Paul1 has a belief
        mem1 = manager.get_memory("Paul1")
        mem1.form_belief("BTC", "Bitcoin will rise", 0.8)
        
        # Paul2 has no belief
        mem2 = manager.get_memory("Paul2")
        
        # Influence
        success = manager.spread_influence("Paul1", "Paul2", "BTC", 0.5)
        
        assert success is True
        adopted = mem2.get_belief("BTC")
        assert adopted is not None
        assert adopted.proposition == "Bitcoin will rise"
    
    def test_social_influence_reinforces_similar(self, manager):
        """Test that influence reinforces similar beliefs."""
        mem1 = manager.get_memory("Paul1")
        mem1.form_belief("BTC", "Bitcoin will rise", 0.9)
        
        mem2 = manager.get_memory("Paul2")
        mem2.form_belief("BTC", "Bitcoin will rise", 0.5)
        
        old_confidence = mem2.get_belief("BTC").confidence
        
        manager.spread_influence("Paul1", "Paul2", "BTC", 0.5)
        
        new_confidence = mem2.get_belief("BTC").confidence
        assert new_confidence > old_confidence
    
    def test_social_influence_challenges_different(self, manager):
        """Test that influence challenges different beliefs."""
        mem1 = manager.get_memory("Paul1")
        mem1.form_belief("BTC", "Bitcoin will rise", 0.9)
        
        mem2 = manager.get_memory("Paul2")
        mem2.form_belief("BTC", "Bitcoin will fall", 0.8)
        
        old_belief = mem2.get_belief("BTC")
        old_confidence = old_belief.confidence
        
        manager.spread_influence("Paul1", "Paul2", "BTC", 0.5)
        
        # Belief should be challenged (lower confidence or status changed)
        new_belief = mem2.get_belief("BTC", include_challenged=True)
        assert new_belief is not None
        # Either confidence decreased or status shows challenge
        assert new_belief.confidence < old_confidence or new_belief.contradiction_count > 0


# ============================================================================
# Utility Function Tests
# ============================================================================

class TestUtilityFunctions:
    """Tests for utility functions."""
    
    def test_create_temporal_prediction_reasoning(self):
        """Test creating prediction reasoning with temporal context."""
        from temporal_memory import Belief
        
        current = Belief(
            topic="BTC",
            proposition="Bitcoin is bullish",
            confidence=0.8,
            created_at=datetime.now(),
            last_updated=datetime.now(),
        )
        
        context = TemporalContext(
            current_belief=current,
            previous_beliefs=[],
            belief_shift=0.0,
            time_span_hours=0,
            evolution_summary="Stable belief",
        )
        
        reasoning = create_temporal_prediction_reasoning(context, "Base reasoning")
        
        assert "bullish" in reasoning or "confidence" in reasoning
        assert "Base reasoning" in reasoning
    
    def test_simulate_belief_evolution(self):
        """Test simulating belief evolution over time."""
        evidence_sequence = [
            (0.5, "Positive news"),
            (0.3, "More positive data"),
            (-0.2, "Minor concern"),
            (0.4, "Strong momentum"),
        ]
        
        history = simulate_belief_evolution(
            topic="BTC",
            initial_proposition="Bitcoin neutral",
            evidence_sequence=evidence_sequence
        )
        
        assert len(history) == len(evidence_sequence) + 1  # +1 for initial
        assert history[0]['event'] == 'initial_belief'
        assert history[0]['confidence'] == 0.5
        
        # Confidence should generally increase with positive evidence
        final_confidence = history[-1]['confidence']
        assert final_confidence != 0.5  # Should have changed
    
    def test_belief_to_dict(self):
        """Test belief serialization."""
        belief = Belief(
            topic="BTC",
            proposition="Bitcoin bullish",
            confidence=0.7,
            created_at=datetime(2024, 1, 1, 12, 0),
            last_updated=datetime(2024, 1, 1, 12, 0),
        )
        
        data = belief.to_dict()
        
        assert data['topic'] == "BTC"
        assert data['proposition'] == "Bitcoin bullish"
        assert data['confidence'] == 0.7
        assert 'created_at' in data
    
    def test_belief_from_dict(self):
        """Test belief deserialization."""
        data = {
            'topic': 'ETH',
            'proposition': 'Ethereum bullish',
            'confidence': 0.8,
            'created_at': '2024-01-01T12:00:00',
            'last_updated': '2024-01-01T12:00:00',
            'evidence_count': 2,
            'contradiction_count': 0,
            'status': 'active',
            'revision_history': [],
            'source_reliability': 0.7,
        }
        
        belief = Belief.from_dict(data)
        
        assert belief.topic == "ETH"
        assert belief.confidence == 0.8
        assert belief.status == BeliefStatus.ACTIVE


# ============================================================================
# Statistics Tests
# ============================================================================

class TestStatistics:
    """Tests for statistics and reporting."""
    
    def test_get_statistics(self, memory_no_db):
        """Test getting memory statistics."""
        memory_no_db.form_belief("BTC", "Bitcoin bullish", 0.7)
        memory_no_db.form_belief("ETH", "Ethereum bullish", 0.6)
        
        stats = memory_no_db.get_statistics()
        
        assert stats['paul_name'] == "TestPaul"
        assert stats['total_beliefs_formed'] == 2
        assert stats['active_beliefs'] == 2
        assert stats['topics_count'] == 2
    
    def test_get_all_active_beliefs(self, memory_no_db):
        """Test retrieving all active beliefs."""
        memory_no_db.form_belief("BTC", "Bitcoin bullish", 0.7)
        memory_no_db.form_belief("ETH", "Ethereum bullish", 0.6)
        
        active = memory_no_db.get_all_active_beliefs()
        
        assert len(active) == 2
        assert all(b.status == BeliefStatus.ACTIVE for b in active)
    
    def test_manager_statistics(self, manager):
        """Test manager-wide statistics."""
        mem1 = manager.get_memory("Paul1")
        mem1.form_belief("BTC", "Bitcoin bullish", 0.7)
        
        mem2 = manager.get_memory("Paul2")
        mem2.form_belief("ETH", "Ethereum bullish", 0.6)
        
        all_stats = manager.get_all_statistics()
        
        assert "Paul1" in all_stats
        assert "Paul2" in all_stats
        assert all_stats["Paul1"]['active_beliefs'] == 1


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_zero_confidence_belief(self, memory_no_db):
        """Test handling of zero confidence belief."""
        belief = memory_no_db.form_belief("BTC", "Neutral", 0.0)
        assert belief.confidence == 0.0
        # Very low confidence beliefs may be immediately abandoned
        assert belief.status in [BeliefStatus.ABANDONED, BeliefStatus.ACTIVE, BeliefStatus.CHALLENGED]
    
    def test_max_confidence_cap(self, memory_no_db):
        """Test that confidence is capped."""
        memory_no_db.form_belief("BTC", "Very bullish", 0.99)
        
        # Add strong supporting evidence
        memory_no_db.add_evidence("BTC", "Amazing news", 1.0, reliability=1.0)
        
        belief = memory_no_db.get_belief("BTC")
        assert belief.confidence <= 0.95  # MAX_CONFIDENCE
    
    def test_evidence_with_zero_reliability(self, memory_no_db):
        """Test evidence with zero reliability."""
        memory_no_db.form_belief("BTC", "Bullish", 0.5)
        
        # Zero reliability evidence should have no effect
        old_confidence = memory_no_db.get_belief("BTC").confidence
        memory_no_db.add_evidence("BTC", "Unreliable rumor", 0.8, reliability=0.0)
        new_confidence = memory_no_db.get_belief("BTC").confidence
        
        assert new_confidence == old_confidence
    
    def test_many_beliefs_same_topic(self, memory_no_db):
        """Test handling many beliefs on same topic."""
        for i in range(10):
            memory_no_db.form_belief("BTC", f"View {i}", 0.5)
        
        history = memory_no_db.get_belief_history("BTC")
        # Should be limited to MAX_BELIEFS_PER_TOPIC
        assert len(history) <= 5


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
