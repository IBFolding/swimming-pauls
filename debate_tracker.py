"""
Debate Influence Tracker for Swimming Pauls
Tracks who convinced whom during multi-round simulations.
Generates clean, readable flow data for visualization.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class OpinionChange:
    """Record of a Paul changing their opinion."""
    round_num: int
    paul_name: str
    from_sentiment: str  # BULLISH, NEUTRAL, BEARISH
    to_sentiment: str
    influenced_by: str  # Which Paul convinced them
    argument: str  # The reasoning that changed their mind
    confidence_delta: float  # How much confidence changed


@dataclass
class PaulInfluence:
    """Influence statistics for a single Paul."""
    name: str
    specialty: str
    final_sentiment: str
    total_influenced: int = 0
    influenced_list: List[str] = field(default_factory=list)
    key_arguments: List[str] = field(default_factory=list)
    isolation_score: float = 0.0  # 0 = connected, 1 = isolated
    consistency: float = 1.0  # Did they stick to their guns?


@dataclass
class DebateFlow:
    """Complete flow of a debate across rounds."""
    prediction_id: str
    question: str
    total_rounds: int
    initial_distribution: Dict[str, int]  # {BULLISH: 30, NEUTRAL: 40...}
    final_distribution: Dict[str, int]
    opinion_changes: List[OpinionChange] = field(default_factory=list)
    influencers: List[PaulInfluence] = field(default_factory=list)
    consensus_former: Optional[str] = None  # Who tipped the scales?


class DebateTracker:
    """
    Tracks the flow of persuasion across debate rounds.
    
    Usage:
        tracker = DebateTracker(prediction_id="abc123", question="Will ETH hit $10K?")
        
        # Each round, record changes
        tracker.record_round(
            round_num=1,
            changes=[
                ("Trader Paul", "NEUTRAL", "BULLISH", "Visionary Paul", "ETF approval likely"),
                ("Skeptic Paul", "BEARISH", "NEUTRAL", "Professor Paul", "Macro data improving"),
            ]
        )
        
        # Get final flow
        flow = tracker.get_debate_flow()
    """
    
    def __init__(self, prediction_id: str, question: str, total_pauls: int = 100):
        self.prediction_id = prediction_id
        self.question = question
        self.total_pauls = total_pauls
        self.rounds: List[List[OpinionChange]] = []
        self.initial_distribution: Optional[Dict[str, int]] = None
        self.final_distribution: Optional[Dict[str, int]] = None
        
    def set_initial_distribution(self, distribution: Dict[str, int]):
        """Record the starting sentiment distribution."""
        self.initial_distribution = distribution
        
    def record_round(self, round_num: int, changes: List[Tuple]):
        """
        Record opinion changes for a round.
        
        Args:
            changes: List of (paul_name, from_sent, to_sent, influenced_by, argument)
        """
        round_changes = []
        for change in changes:
            paul_name, from_sent, to_sent, influencer, argument = change
            
            # Calculate confidence delta (simplified)
            confidence_delta = 0.15 if to_sent in ["BULLISH", "BEARISH"] else 0.05
            
            round_changes.append(OpinionChange(
                round_num=round_num,
                paul_name=paul_name,
                from_sentiment=from_sent,
                to_sentiment=to_sent,
                influenced_by=influencer,
                argument=argument[:200],  # Truncate for storage
                confidence_delta=confidence_delta
            ))
        
        self.rounds.append(round_changes)
        
    def set_final_distribution(self, distribution: Dict[str, int]):
        """Record the final sentiment distribution."""
        self.final_distribution = distribution
        
    def get_influencer_rankings(self) -> List[PaulInfluence]:
        """Calculate influence rankings from recorded changes."""
        influence_counts: Dict[str, List] = {}
        arguments_used: Dict[str, List] = {}
        final_positions: Dict[str, str] = {}
        
        # Aggregate changes
        for round_changes in self.rounds:
            for change in round_changes:
                influencer = change.influenced_by
                influenced = change.paul_name
                
                if influencer not in influence_counts:
                    influence_counts[influencer] = []
                    arguments_used[influencer] = []
                    
                influence_counts[influencer].append(influenced)
                arguments_used[influencer].append(change.argument)
                final_positions[influenced] = change.to_sentiment
                
        # Build PaulInfluence objects
        rankings = []
        for paul_name, influenced_list in influence_counts.items():
            # Get unique influenced Pauls
            unique_influenced = list(set(influenced_list))
            
            # Get most common argument
            if arguments_used[paul_name]:
                from collections import Counter
                most_common = Counter(arguments_used[paul_name]).most_common(1)[0][0]
                key_args = [most_common]
            else:
                key_args = []
                
            rankings.append(PaulInfluence(
                name=paul_name,
                specialty="",  # Would be filled from persona data
                final_sentiment=final_positions.get(paul_name, "NEUTRAL"),
                total_influenced=len(unique_influenced),
                influenced_list=unique_influenced,
                key_arguments=key_args,
                isolation_score=0.0,  # Calculated separately
                consistency=1.0
            ))
            
        # Sort by influence
        rankings.sort(key=lambda x: x.total_influenced, reverse=True)
        
        # Mark isolated Pauls (those who influenced no one)
        all_pauls = set()
        for round_changes in self.rounds:
            for change in round_changes:
                all_pauls.add(change.paul_name)
                all_pauls.add(change.influenced_by)
                
        influencers = set(influence_counts.keys())
        isolated = all_pauls - influencers
        
        for paul_name in isolated:
            rankings.append(PaulInfluence(
                name=paul_name,
                specialty="",
                final_sentiment=final_positions.get(paul_name, "NEUTRAL"),
                total_influenced=0,
                influenced_list=[],
                key_arguments=[],
                isolation_score=1.0,
                consistency=1.0
            ))
            
        return rankings
        
    def get_consensus_former(self) -> Optional[str]:
        """Identify who tipped the scales to consensus."""
        if not self.rounds:
            return None
            
        # Look at last round - who had the most impact?
        last_round = self.rounds[-1]
        if not last_round:
            return None
            
        # Count changes in final round
        influencer_counts = {}
        for change in last_round:
            influencer_counts[change.influenced_by] = \
                influencer_counts.get(change.influenced_by, 0) + 1
                
        if influencer_counts:
            return max(influencer_counts, key=influencer_counts.get)
        return None
        
    def get_debate_flow(self) -> DebateFlow:
        """Generate complete debate flow object."""
        return DebateFlow(
            prediction_id=self.prediction_id,
            question=self.question,
            total_rounds=len(self.rounds),
            initial_distribution=self.initial_distribution or {},
            final_distribution=self.final_distribution or {},
            opinion_changes=[
                change for round_changes in self.rounds for change in round_changes
            ],
            influencers=self.get_influencer_rankings(),
            consensus_former=self.get_consensus_former()
        )
        
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        flow = self.get_debate_flow()
        return {
            "prediction_id": flow.prediction_id,
            "question": flow.question,
            "total_rounds": flow.total_rounds,
            "initial_distribution": flow.initial_distribution,
            "final_distribution": flow.final_distribution,
            "opinion_changes": [
                {
                    "round": c.round_num,
                    "paul": c.paul_name,
                    "from": c.from_sentiment,
                    "to": c.to_sentiment,
                    "influenced_by": c.influenced_by,
                    "argument": c.argument
                }
                for c in flow.opinion_changes
            ],
            "top_influencers": [
                {
                    "name": inf.name,
                    "final_position": inf.final_sentiment,
                    "influenced_count": inf.total_influenced,
                    "key_argument": inf.key_arguments[0] if inf.key_arguments else "",
                    "isolated": inf.isolation_score > 0.5
                }
                for inf in flow.influencers[:10]  # Top 10
            ],
            "consensus_former": flow.consensus_former
        }


def format_influence_report(flow: DebateFlow) -> str:
    """Generate a clean text report of the debate flow."""
    lines = []
    lines.append("="*70)
    lines.append("🗣️  DEBATE FLOW REPORT")
    lines.append("="*70)
    lines.append(f"Question: {flow.question}")
    lines.append(f"Rounds: {flow.total_rounds}")
    lines.append("")
    
    # Distribution change
    lines.append("📊 SENTIMENT SHIFT")
    lines.append("-"*70)
    init = flow.initial_distribution
    final = flow.final_distribution
    
    for sentiment in ["BULLISH", "NEUTRAL", "BEARISH"]:
        init_count = init.get(sentiment, 0)
        final_count = final.get(sentiment, 0)
        delta = final_count - init_count
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        lines.append(f"  {sentiment:10} {init_count:3} → {final_count:3} ({delta_str:>+3})")
    lines.append("")
    
    # Top influencers
    lines.append("🏆 TOP INFLUENCERS")
    lines.append("-"*70)
    
    for i, inf in enumerate(flow.influencers[:5], 1):
        if inf.total_influenced > 0:
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            lines.append(f"{emoji} {inf.name}")
            lines.append(f"   Convinced: {inf.total_influenced} Pauls → {inf.final_sentiment}")
            if inf.key_arguments:
                lines.append(f"   Key argument: \"{inf.key_arguments[0][:60]}...\"")
            lines.append("")
        elif inf.isolation_score > 0.5:
            lines.append(f"⚠️  {inf.name} - Isolated (convinced no one)")
            lines.append("")
            
    # Consensus former
    if flow.consensus_former:
        lines.append("🎯 CONSENSUS FORMER")
        lines.append("-"*70)
        lines.append(f"{flow.consensus_former} tipped the scales in the final round")
        lines.append("")
        
    lines.append("="*70)
    return "\n".join(lines)


# Demo
if __name__ == "__main__":
    tracker = DebateTracker(
        prediction_id="demo123",
        question="Will ETH reach $10K by 2025?",
        total_pauls=100
    )
    
    tracker.set_initial_distribution({"BULLISH": 30, "NEUTRAL": 40, "BEARISH": 30})
    
    # Round 1
    tracker.record_round(1, [
        ("Trader Paul", "NEUTRAL", "BULLISH", "Visionary Paul", "ETF approval is imminent"),
        ("Degen Paul", "BEARISH", "NEUTRAL", "Professor Paul", "Macro environment stabilizing"),
        ("Analyst Paul", "NEUTRAL", "BULLISH", "Visionary Paul", "Layer 2 adoption accelerating"),
    ])
    
    # Round 3
    tracker.record_round(3, [
        ("Whale Paul", "NEUTRAL", "BULLISH", "Trader Paul", "Institutional inflows confirmed"),
        ("Value Paul", "BEARISH", "NEUTRAL", "Professor Paul", "Valuation looking reasonable"),
    ])
    
    # Round 5 (final)
    tracker.record_round(5, [
        ("Skeptic Paul", "BEARISH", "NEUTRAL", "Whale Paul", "Too much momentum to ignore"),
    ])
    
    tracker.set_final_distribution({"BULLISH": 55, "NEUTRAL": 30, "BEARISH": 15})
    
    flow = tracker.get_debate_flow()
    print(format_influence_report(flow))
    print("\n📋 JSON export:")
    print(json.dumps(tracker.to_dict(), indent=2))
