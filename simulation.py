"""
Scales v1.0 - Multi-Agent Simulation Engine
Async simulation runner for coordinating agent predictions.
"""
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import time
import random

from agent import Agent, AgentPrediction, create_agent_team, PersonaType


@dataclass
class SimulationRound:
    """Results from a single simulation round."""
    round_number: int
    timestamp: float
    market_data: Dict[str, Any]
    predictions: List[AgentPrediction]
    consensus: Dict[str, Any]
    
    
@dataclass
class SimulationResult:
    """Complete results from a simulation run."""
    start_time: float
    end_time: float
    rounds: List[SimulationRound]
    final_consensus: Dict[str, Any]
    agent_performances: Dict[str, float]


class SimulationRunner:
    """
    Async simulation runner for multi-agent trend prediction.
    
    Coordinates multiple agents, aggregates predictions, and maintains
    simulation state across rounds.
    """
    
    def __init__(
        self,
        agents: Optional[List[Agent]] = None,
        rounds: int = 10,
        round_delay: float = 0.5,
        consensus_threshold: float = 0.6,
    ):
        """
        Initialize simulation runner.
        
        Args:
            agents: List of agents (creates default team if None)
            rounds: Number of simulation rounds to run
            round_delay: Delay between rounds in seconds
            consensus_threshold: Confidence threshold for strong consensus
        """
        self.agents = agents or create_agent_team()
        self.total_rounds = rounds
        self.round_delay = round_delay
        self.consensus_threshold = consensus_threshold
        
        self.rounds_completed = 0
        self.round_results: List[SimulationRound] = []
        self.is_running = False
        
    async def run(
        self,
        market_data_feed: Optional[Callable[[int], Dict[str, Any]]] = None,
        callback: Optional[Callable[[SimulationRound], None]] = None,
    ) -> SimulationResult:
        """
        Run the simulation asynchronously.
        
        Args:
            market_data_feed: Function that returns market data for each round
            callback: Optional callback called after each round
            
        Returns:
            SimulationResult with all rounds and final consensus
        """
        self.is_running = True
        start_time = time.time()
        
        # Default market data generator if none provided
        if market_data_feed is None:
            market_data_feed = self._default_market_data
            
        try:
            for round_num in range(1, self.total_rounds + 1):
                if not self.is_running:
                    break
                    
                # Get market data for this round
                market_data = market_data_feed(round_num)
                
                # Run agent predictions concurrently
                predictions = await self._run_agents(market_data)
                
                # Calculate consensus
                consensus = self._calculate_consensus(predictions)
                
                # Create round result
                round_result = SimulationRound(
                    round_number=round_num,
                    timestamp=time.time(),
                    market_data=market_data,
                    predictions=predictions,
                    consensus=consensus,
                )
                
                self.round_results.append(round_result)
                self.rounds_completed = round_num
                
                # Update agent accuracy based on "actual" outcome
                self._update_agent_accuracies(market_data, predictions)
                
                # Call callback if provided
                if callback:
                    callback(round_result)
                
                # Delay before next round
                if round_num < self.total_rounds:
                    await asyncio.sleep(self.round_delay)
                    
        except asyncio.CancelledError:
            pass
        finally:
            self.is_running = False
            
        end_time = time.time()
        
        # Calculate final performance metrics
        agent_performances = self._calculate_performances()
        final_consensus = self._calculate_final_consensus()
        
        return SimulationResult(
            start_time=start_time,
            end_time=end_time,
            rounds=self.round_results,
            final_consensus=final_consensus,
            agent_performances=agent_performances,
        )
    
    async def _run_agents(self, market_data: Dict[str, Any]) -> List[AgentPrediction]:
        """Run all agents concurrently and collect predictions."""
        tasks = [self._run_single_agent(agent, market_data) for agent in self.agents]
        predictions = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_predictions = [
            p for p in predictions if isinstance(p, AgentPrediction)
        ]
        
        return valid_predictions
    
    async def _run_single_agent(
        self,
        agent: Agent,
        market_data: Dict[str, Any],
    ) -> AgentPrediction:
        """Run a single agent prediction (with small delay for realism)."""
        # Simulate processing time
        await asyncio.sleep(random.uniform(0.01, 0.05))
        return agent.predict(market_data)
    
    def _calculate_consensus(self, predictions: List[AgentPrediction]) -> Dict[str, Any]:
        """Calculate consensus from agent predictions."""
        if not predictions:
            return {"direction": "neutral", "confidence": 0.0, "strength": "weak"}
            
        # Count directions weighted by confidence
        direction_weights = {"bullish": 0.0, "bearish": 0.0, "neutral": 0.0}
        total_confidence = 0.0
        
        for pred in predictions:
            direction_weights[pred.direction] += pred.confidence
            total_confidence += pred.confidence
            
        # Normalize
        if total_confidence > 0:
            direction_weights = {
                k: v / total_confidence for k, v in direction_weights.items()
            }
            
        # Determine consensus direction
        max_direction = max(direction_weights, key=direction_weights.get)
        max_weight = direction_weights[max_direction]
        
        # Calculate overall confidence
        avg_confidence = total_confidence / len(predictions)
        
        # Determine strength
        if max_weight >= self.consensus_threshold:
            strength = "strong"
        elif max_weight >= 0.5:
            strength = "moderate"
        else:
            strength = "weak"
            
        # Calculate sentiment score (-1.0 to 1.0)
        sentiment = direction_weights["bullish"] - direction_weights["bearish"]
        
        return {
            "direction": max_direction,
            "confidence": avg_confidence,
            "direction_weights": direction_weights,
            "sentiment": sentiment,
            "strength": strength,
            "agreement_ratio": max_weight,
        }
    
    def _calculate_final_consensus(self) -> Dict[str, Any]:
        """Calculate overall consensus across all rounds."""
        if not self.round_results:
            return {}
            
        # Aggregate all round consensus
        sentiment_sum = 0.0
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        for round_result in self.round_results:
            consensus = round_result.consensus
            sentiment_sum += consensus["sentiment"]
            
            if consensus["direction"] == "bullish":
                bullish_count += 1
            elif consensus["direction"] == "bearish":
                bearish_count += 1
            else:
                neutral_count += 1
                
        total_rounds = len(self.round_results)
        avg_sentiment = sentiment_sum / total_rounds
        
        # Determine final direction
        if bullish_count > bearish_count and bullish_count > neutral_count:
            final_direction = "bullish"
        elif bearish_count > bullish_count and bearish_count > neutral_count:
            final_direction = "bearish"
        else:
            final_direction = "neutral"
            
        return {
            "direction": final_direction,
            "sentiment": avg_sentiment,
            "bullish_rounds": bullish_count,
            "bearish_rounds": bearish_count,
            "neutral_rounds": neutral_count,
            "consistency": max(bullish_count, bearish_count, neutral_count) / total_rounds,
        }
    
    def _calculate_performances(self) -> Dict[str, float]:
        """Calculate performance metrics for each agent."""
        performances = {}
        for agent in self.agents:
            performances[agent.id] = agent.memory.accuracy_score
        return performances
    
    def _update_agent_accuracies(
        self,
        market_data: Dict[str, Any],
        predictions: List[AgentPrediction],
    ) -> None:
        """Update agent accuracies based on 'actual' market movement."""
        # Use price_trend as proxy for actual outcome
        actual = market_data.get("price_trend", 0.0)
        
        for agent in self.agents:
            agent.update_accuracy(actual)
    
    def _default_market_data(self, round_num: int) -> Dict[str, Any]:
        """Generate default market data for simulation rounds."""
        # Create some realistic looking market data
        trend = random.uniform(-0.5, 0.5)
        
        # Add some momentum
        if self.round_results:
            last_sentiment = self.round_results[-1].consensus["sentiment"]
            trend += last_sentiment * 0.2
            
        return {
            "price_trend": trend,
            "volume": random.uniform(0.3, 1.0),
            "sentiment": random.uniform(-0.5, 0.5) + trend * 0.3,
            "volatility": random.uniform(0.1, 0.6),
            "timestamp": time.time(),
        }
    
    def stop(self) -> None:
        """Stop the simulation."""
        self.is_running = False
        
    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status."""
        return {
            "is_running": self.is_running,
            "rounds_completed": self.rounds_completed,
            "total_rounds": self.total_rounds,
            "agent_count": len(self.agents),
            "progress": self.rounds_completed / self.total_rounds if self.total_rounds > 0 else 0,
        }


class SimulationBuilder:
    """Builder pattern for creating simulations."""
    
    def __init__(self):
        self.agents: List[Agent] = []
        self.rounds = 10
        self.round_delay = 0.5
        self.consensus_threshold = 0.6
        
    def with_agents(self, agents: List[Agent]) -> "SimulationBuilder":
        """Set the agent list."""
        self.agents = agents
        return self
        
    def with_team(
        self,
        analyst: int = 1,
        trader: int = 1,
        hedgie: int = 1,
        visionary: int = 1,
        skeptic: int = 1,
    ) -> "SimulationBuilder":
        """Create a team with specified persona counts."""
        self.agents = create_agent_team(analyst, trader, hedgie, visionary, skeptic)
        return self
        
    def with_rounds(self, rounds: int) -> "SimulationBuilder":
        """Set number of rounds."""
        self.rounds = rounds
        return self
        
    def with_delay(self, delay: float) -> "SimulationBuilder":
        """Set delay between rounds."""
        self.round_delay = delay
        return self
        
    def with_consensus_threshold(self, threshold: float) -> "SimulationBuilder":
        """Set consensus threshold."""
        self.consensus_threshold = threshold
        return self
        
    def build(self) -> SimulationRunner:
        """Build and return the simulation runner."""
        return SimulationRunner(
            agents=self.agents or create_agent_team(),
            rounds=self.rounds,
            round_delay=self.round_delay,
            consensus_threshold=self.consensus_threshold,
        )


# Convenience function for quick simulations
async def quick_simulate(
    rounds: int = 5,
    agents: Optional[List[Agent]] = None,
    verbose: bool = True,
) -> SimulationResult:
    """
    Quick simulation with default settings.
    
    Args:
        rounds: Number of rounds
        agents: Optional custom agent list
        verbose: Print results if True
        
    Returns:
        SimulationResult
    """
    runner = SimulationRunner(
        agents=agents,
        rounds=rounds,
        round_delay=0.1,
    )
    
    def print_round(round_result: SimulationRound):
        if verbose:
            print(f"\n📊 Round {round_result.round_number}/{rounds}")
            print(f"   Consensus: {round_result.consensus['direction'].upper()} "
                  f"(confidence: {round_result.consensus['confidence']:.2f}, "
                  f"strength: {round_result.consensus['strength']})")
            
    result = await runner.run(callback=print_round)
    
    if verbose:
        print(f"\n{'='*50}")
        print("🏁 FINAL CONSENSUS")
        print(f"{'='*50}")
        print(f"Direction: {result.final_consensus['direction'].upper()}")
        print(f"Sentiment: {result.final_consensus['sentiment']:+.2f}")
        print(f"Consistency: {result.final_consensus['consistency']:.1%}")
        
    return result
