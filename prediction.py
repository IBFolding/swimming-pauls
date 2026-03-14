"""
Scales v1.0 - Multi-Agent Simulation Engine
Prediction output formatting and export.
"""
import json
from typing import Dict, List, Any, Optional
from dataclasses import asdict
from datetime import datetime

from agent import AgentPrediction, Agent
from simulation import SimulationResult, SimulationRound


class PredictionFormatter:
    """Format predictions for various output formats."""
    
    @staticmethod
    def to_dict(prediction: AgentPrediction) -> Dict[str, Any]:
        """Convert prediction to dictionary."""
        return {
            "agent_id": prediction.agent_id,
            "direction": prediction.direction,
            "confidence": round(prediction.confidence, 3),
            "magnitude": round(prediction.magnitude, 3),
            "reasoning": prediction.reasoning,
            "timestamp": prediction.timestamp,
        }
    
    @staticmethod
    def to_json(prediction: AgentPrediction, indent: int = 2) -> str:
        """Convert prediction to JSON string."""
        return json.dumps(PredictionFormatter.to_dict(prediction), indent=indent)
    
    @staticmethod
    def format_simple(prediction: AgentPrediction, agent_name: str = "") -> str:
        """Format prediction as simple readable string."""
        emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(
            prediction.direction, "❓"
        )
        name = f"{agent_name} " if agent_name else ""
        return (
            f"{emoji} {name}{prediction.direction.upper()} "
            f"(conf: {prediction.confidence:.0%}, mag: {prediction.magnitude:.2f})"
        )


class SimulationReporter:
    """Generate comprehensive reports from simulation results."""
    
    def __init__(self, result: SimulationResult, agents: List[Agent]):
        self.result = result
        self.agents = agents
        self.agent_map = {a.id: a for a in agents}
        
    def generate_text_report(self) -> str:
        """Generate human-readable text report."""
        lines = []
        
        # Header
        lines.append("=" * 60)
        lines.append("📊 SCALES V1.0 SIMULATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Generated: {datetime.fromtimestamp(self.result.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Duration: {self.result.end_time - self.result.start_time:.2f}s")
        lines.append(f"Rounds: {len(self.result.rounds)}")
        lines.append(f"Agents: {len(self.agents)}")
        lines.append("")
        
        # Final Consensus
        consensus = self.result.final_consensus
        lines.append("-" * 60)
        lines.append("🏁 FINAL CONSENSUS")
        lines.append("-" * 60)
        
        direction_emoji = {"bullish": "🚀", "bearish": "🔻", "neutral": "➖"}.get(
            consensus.get("direction", "neutral"), "❓"
        )
        
        lines.append(f"{direction_emoji} Direction: {consensus['direction'].upper()}")
        lines.append(f"📊 Sentiment: {consensus['sentiment']:+.3f} (range: -1.0 to +1.0)")
        lines.append(f"🎯 Consistency: {consensus['consistency']:.1%}")
        lines.append("")
        lines.append(f"   Bullish rounds: {consensus['bullish_rounds']}")
        lines.append(f"   Bearish rounds: {consensus['bearish_rounds']}")
        lines.append(f"   Neutral rounds: {consensus['neutral_rounds']}")
        lines.append("")
        
        # Round-by-round breakdown
        lines.append("-" * 60)
        lines.append("📈 ROUND-BY-ROUND BREAKDOWN")
        lines.append("-" * 60)
        
        for round_result in self.result.rounds:
            c = round_result.consensus
            emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(c['direction'])
            
            lines.append(f"\nRound {round_result.round_number}:")
            lines.append(f"  {emoji} Consensus: {c['direction'].upper()}")
            lines.append(f"     Confidence: {c['confidence']:.2f} | "
                        f"Strength: {c['strength']} | "
                        f"Sentiment: {c['sentiment']:+.2f}")
            
            # Show top predictions
            sorted_preds = sorted(
                round_result.predictions,
                key=lambda p: p.confidence,
                reverse=True
            )[:3]
            
            lines.append(f"  Top predictions:")
            for pred in sorted_preds:
                agent = self.agent_map.get(pred.agent_id)
                agent_name = agent.name if agent else pred.agent_id[:8]
                pred_emoji = {"bullish": "▲", "bearish": "▼", "neutral": "—"}.get(pred.direction)
                lines.append(f"    {pred_emoji} {agent_name}: {pred.direction} ({pred.confidence:.0%})")
        
        # Agent Performance
        lines.append("")
        lines.append("-" * 60)
        lines.append("🎭 AGENT PERFORMANCE")
        lines.append("-" * 60)
        
        sorted_agents = sorted(
            self.agents,
            key=lambda a: a.memory.accuracy_score,
            reverse=True
        )
        
        for i, agent in enumerate(sorted_agents, 1):
            accuracy = agent.memory.accuracy_score
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            bar = "█" * int(accuracy * 20) + "░" * (20 - int(accuracy * 20))
            lines.append(f"{medal} {agent.name:12} ({agent.persona.value:10}) | "
                        f"{bar} {accuracy:.1%}")
        
        # Strategic Insights
        lines.append("")
        lines.append("-" * 60)
        lines.append("💡 STRATEGIC INSIGHTS")
        lines.append("-" * 60)
        lines.extend(self._generate_insights())
        
        lines.append("")
        lines.append("=" * 60)
        lines.append("END OF REPORT")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def _generate_insights(self) -> List[str]:
        """Generate strategic insights from simulation."""
        insights = []
        
        consensus = self.result.final_consensus
        
        # Direction insight
        if consensus['direction'] == "bullish":
            if consensus['consistency'] > 0.7:
                insights.append("• Strong bullish consensus across rounds suggests momentum")
            else:
                insights.append("• Mixed bullish signals — proceed with caution")
        elif consensus['direction'] == "bearish":
            if consensus['consistency'] > 0.7:
                insights.append("• Strong bearish consensus — defensive positioning advised")
            else:
                insights.append("• Weak bearish signals — may be temporary pullback")
        else:
            insights.append("• Neutral consensus indicates indecision or consolidation")
            
        # Sentiment insight
        sentiment = consensus['sentiment']
        if abs(sentiment) > 0.5:
            insights.append(f"• Extreme sentiment ({sentiment:+.2f}) suggests potential reversal zone")
        elif abs(sentiment) < 0.2:
            insights.append("• Low sentiment dispersion indicates balanced market")
            
        # Agent performance insight
        best_agent = max(self.agents, key=lambda a: a.memory.accuracy_score)
        insights.append(f"• {best_agent.name} ({best_agent.persona.value}) showed highest accuracy — "
                       f"consider weighting their signals higher")
        
        return insights
    
    def to_json(self, indent: int = 2) -> str:
        """Export simulation result as JSON."""
        export_data = {
            "metadata": {
                "start_time": self.result.start_time,
                "end_time": self.result.end_time,
                "duration_seconds": round(self.result.end_time - self.result.start_time, 3),
                "total_rounds": len(self.result.rounds),
                "agent_count": len(self.agents),
            },
            "final_consensus": self.result.final_consensus,
            "agent_performances": self.result.agent_performances,
            "rounds": [
                {
                    "round_number": r.round_number,
                    "timestamp": r.timestamp,
                    "consensus": r.consensus,
                    "predictions": [PredictionFormatter.to_dict(p) for p in r.predictions],
                    "market_data": r.market_data,
                }
                for r in self.result.rounds
            ],
        }
        return json.dumps(export_data, indent=indent, default=str)
    
    def to_csv(self) -> str:
        """Export predictions as CSV."""
        lines = ["round,agent_id,agent_name,direction,confidence,magnitude,timestamp"]
        
        for round_result in self.result.rounds:
            for pred in round_result.predictions:
                agent = self.agent_map.get(pred.agent_id)
                agent_name = agent.name if agent else "unknown"
                lines.append(
                    f"{round_result.round_number},"
                    f"{pred.agent_id},"
                    f"{agent_name},"
                    f"{pred.direction},"
                    f"{pred.confidence:.4f},"
                    f"{pred.magnitude:.4f},"
                    f"{pred.timestamp}"
                )
        
        return "\n".join(lines)
    
    def save_report(self, filepath: str, format: str = "text") -> None:
        """Save report to file."""
        if format == "text":
            content = self.generate_text_report()
        elif format == "json":
            content = self.to_json()
        elif format == "csv":
            content = self.to_csv()
        else:
            raise ValueError(f"Unknown format: {format}")
            
        with open(filepath, "w") as f:
            f.write(content)


class SimpleOutput:
    """Simple one-line prediction output for quick use."""
    
    @staticmethod
    def print_prediction(prediction: AgentPrediction, agent_name: str = "") -> None:
        """Print a single prediction."""
        print(PredictionFormatter.format_simple(prediction, agent_name))
    
    @staticmethod
    def print_consensus(consensus: Dict[str, Any]) -> None:
        """Print consensus result."""
        direction = consensus.get("direction", "unknown")
        confidence = consensus.get("confidence", 0)
        strength = consensus.get("strength", "weak")
        
        emoji = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(direction, "❓")
        
        print(f"\n{emoji} CONSENSUS: {direction.upper()}")
        print(f"   Confidence: {confidence:.1%}")
        print(f"   Strength: {strength}")
        print(f"   Sentiment: {consensus.get('sentiment', 0):+.2f}")
    
    @staticmethod
    def print_summary(result: SimulationResult, agents: List[Agent]) -> None:
        """Print quick summary of simulation."""
        consensus = result.final_consensus
        
        print("\n" + "=" * 40)
        print("📊 SIMULATION COMPLETE")
        print("=" * 40)
        
        direction = consensus.get("direction", "unknown")
        emoji = {"bullish": "🚀", "bearish": "🔻", "neutral": "➖"}.get(direction, "❓")
        
        print(f"\n{emoji} {direction.upper()}")
        print(f"   Sentiment: {consensus.get('sentiment', 0):+.2f}")
        print(f"   Consistency: {consensus.get('consistency', 0):.0%}")
        
        print(f"\n🎭 Agents: {len(agents)}")
        print(f"📈 Rounds: {len(result.rounds)}")
        
        # Best performer
        best = max(agents, key=lambda a: a.memory.accuracy_score)
        print(f"\n🏆 Best: {best.name} ({best.memory.accuracy_score:.0%} accuracy)")
        
        print("\n" + "=" * 40)


# Quick export functions
def export_json(result: SimulationResult, agents: List[Agent]) -> str:
    """Quick JSON export."""
    return SimulationReporter(result, agents).to_json()


def export_csv(result: SimulationResult, agents: List[Agent]) -> str:
    """Quick CSV export."""
    return SimulationReporter(result, agents).to_csv()


def print_report(result: SimulationResult, agents: List[Agent]) -> None:
    """Print full text report."""
    print(SimulationReporter(result, agents).generate_text_report())
