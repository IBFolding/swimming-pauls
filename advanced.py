"""
Scales v1.0 - Advanced Simulation Features
Monte Carlo, sensitivity analysis, scenario comparison, backtesting.
"""
import asyncio
import random
import statistics
import time
from typing import Dict, List, Any, Optional, Callable, Tuple, NamedTuple
from dataclasses import dataclass, field
from collections import defaultdict
import copy

from agent import Agent, AgentPrediction, create_agent_team, PersonaType
from simulation import SimulationRunner, SimulationResult, SimulationRound


@dataclass
class MonteCarloResult:
    """Results from a Monte Carlo simulation run."""
    total_runs: int
    bullish_probability: float
    bearish_probability: float
    neutral_probability: float
    avg_sentiment: float
    sentiment_std: float
    confidence_interval_95: Tuple[float, float]
    confidence_interval_99: Tuple[float, float]
    value_at_risk_95: float  # 5th percentile outcome
    value_at_risk_99: float  # 1st percentile outcome
    expected_outcome: float
    skewness: float
    kurtosis: float
    all_sentiments: List[float] = field(default_factory=list)
    all_outcomes: List[float] = field(default_factory=list)
    run_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "total_runs": self.total_runs,
            "probabilities": {
                "bullish": round(self.bullish_probability, 4),
                "bearish": round(self.bearish_probability, 4),
                "neutral": round(self.neutral_probability, 4),
            },
            "sentiment": {
                "mean": round(self.avg_sentiment, 4),
                "std": round(self.sentiment_std, 4),
            },
            "confidence_intervals": {
                "ci_95": [round(self.confidence_interval_95[0], 4), 
                         round(self.confidence_interval_95[1], 4)],
                "ci_99": [round(self.confidence_interval_99[0], 4),
                         round(self.confidence_interval_99[1], 4)],
            },
            "value_at_risk": {
                "var_95": round(self.value_at_risk_95, 4),
                "var_99": round(self.value_at_risk_99, 4),
            },
            "expected_outcome": round(self.expected_outcome, 4),
            "distribution_stats": {
                "skewness": round(self.skewness, 4),
                "kurtosis": round(self.kurtosis, 4),
            },
        }


@dataclass
class SensitivityResult:
    """Results from sensitivity analysis."""
    variable_name: str
    correlation_with_sentiment: float
    correlation_with_accuracy: float
    impact_score: float  # Normalized 0-1 impact
    rank: int
    
    def __repr__(self) -> str:
        return (f"SensitivityResult({self.variable_name}: "
                f"impact={self.impact_score:.3f}, rank={self.rank})")


@dataclass
class ScenarioComparison:
    """Comparison between two scenarios."""
    scenario_a_name: str
    scenario_b_name: str
    sentiment_diff: float
    win_probability_a: float  # Probability A beats B
    win_probability_b: float
    expected_value_a: float
    expected_value_b: float
    risk_ratio: float  # A risk / B risk
    recommendation: str
    statistical_significance: float  # p-value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_a": self.scenario_a_name,
            "scenario_b": self.scenario_b_name,
            "sentiment_difference": round(self.sentiment_diff, 4),
            "win_probabilities": {
                "a": round(self.win_probability_a, 4),
                "b": round(self.win_probability_b, 4),
            },
            "expected_values": {
                "a": round(self.expected_value_a, 4),
                "b": round(self.expected_value_b, 4),
            },
            "risk_ratio": round(self.risk_ratio, 4),
            "recommendation": self.recommendation,
            "significance": round(self.statistical_significance, 4),
        }


@dataclass
class BacktestResult:
    """Results from backtesting against historical data."""
    total_predictions: int
    correct_predictions: int
    accuracy_rate: float
    precision: Dict[str, float]  # By direction
    recall: Dict[str, float]
    f1_score: Dict[str, float]
    confusion_matrix: Dict[str, Dict[str, int]]
    sharpe_ratio: float
    max_drawdown: float
    profit_factor: float
    equity_curve: List[float] = field(default_factory=list)
    trades: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "performance": {
                "total_predictions": self.total_predictions,
                "correct_predictions": self.correct_predictions,
                "accuracy_rate": round(self.accuracy_rate, 4),
            },
            "classification_metrics": {
                "precision": {k: round(v, 4) for k, v in self.precision.items()},
                "recall": {k: round(v, 4) for k, v in self.recall.items()},
                "f1_score": {k: round(v, 4) for k, v in self.f1_score.items()},
            },
            "confusion_matrix": self.confusion_matrix,
            "trading_metrics": {
                "sharpe_ratio": round(self.sharpe_ratio, 4),
                "max_drawdown": round(self.max_drawdown, 4),
                "profit_factor": round(self.profit_factor, 4),
            },
        }


class MonteCarloSimulator:
    """
    Monte Carlo simulation engine for multi-agent predictions.
    
    Runs thousands of simulations with randomized market conditions
    to generate probability distributions and confidence intervals.
    """
    
    def __init__(
        self,
        agents: Optional[List[Agent]] = None,
        seed: Optional[int] = None,
    ):
        self.agents = agents or create_agent_team()
        self.rng = random.Random(seed)
        if seed is not None:
            random.seed(seed)
            
    async def run(
        self,
        num_simulations: int = 1000,
        market_data_generator: Optional[Callable[[int], Dict[str, Any]]] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> MonteCarloResult:
        """
        Run Monte Carlo simulation.
        
        Args:
            num_simulations: Number of simulation runs (default: 1000)
            market_data_generator: Function to generate random market data
            progress_callback: Called with (completed, total) during runs
            
        Returns:
            MonteCarloResult with statistical analysis
        """
        if num_simulations < 100:
            raise ValueError("Monte Carlo requires at least 100 simulations")
            
        sentiments = []
        outcomes = []
        direction_counts = {"bullish": 0, "bearish": 0, "neutral": 0}
        run_results = []
        
        # Default market data generator
        if market_data_generator is None:
            market_data_generator = self._default_market_data_generator
            
        runner = SimulationRunner(agents=self.agents, rounds=1, round_delay=0)
        
        for i in range(num_simulations):
            # Generate random market conditions
            market_data = market_data_generator(i)
            
            # Reset agents for each run
            for agent in self.agents:
                agent.memory.accuracy_score = 0.5
                agent.memory.predictions = []
                
            # Run single simulation
            result = await runner.run(
                market_data_feed=lambda _: market_data
            )
            
            # Extract sentiment and outcome
            consensus = result.final_consensus
            sentiment = consensus.get("sentiment", 0.0)
            direction = consensus.get("direction", "neutral")
            
            sentiments.append(sentiment)
            outcomes.append(sentiment)  # Use sentiment as proxy for outcome
            direction_counts[direction] += 1
            
            run_results.append({
                "run": i + 1,
                "sentiment": sentiment,
                "direction": direction,
                "market_data": market_data,
            })
            
            # Progress callback
            if progress_callback and (i + 1) % 50 == 0:
                progress_callback(i + 1, num_simulations)
                
        # Calculate statistics
        total = num_simulations
        bullish_prob = direction_counts["bullish"] / total
        bearish_prob = direction_counts["bearish"] / total
        neutral_prob = direction_counts["neutral"] / total
        
        avg_sentiment = statistics.mean(sentiments)
        sentiment_std = statistics.stdev(sentiments) if len(sentiments) > 1 else 0.0
        
        # Confidence intervals
        ci_95 = self._calculate_ci(sentiments, 0.95)
        ci_99 = self._calculate_ci(sentiments, 0.99)
        
        # Value at Risk (percentiles)
        sorted_outcomes = sorted(outcomes)
        var_95 = sorted_outcomes[int(total * 0.05)]  # 5th percentile (worst)
        var_99 = sorted_outcomes[int(total * 0.01)]  # 1st percentile
        
        # Distribution shape metrics
        skewness = self._calculate_skewness(sentiments, avg_sentiment, sentiment_std)
        kurtosis = self._calculate_kurtosis(sentiments, avg_sentiment, sentiment_std)
        
        # Expected outcome (probability-weighted)
        expected = (bullish_prob * 1.0) + (bearish_prob * -1.0) + (neutral_prob * 0.0)
        
        return MonteCarloResult(
            total_runs=num_simulations,
            bullish_probability=bullish_prob,
            bearish_probability=bearish_prob,
            neutral_probability=neutral_prob,
            avg_sentiment=avg_sentiment,
            sentiment_std=sentiment_std,
            confidence_interval_95=ci_95,
            confidence_interval_99=ci_99,
            value_at_risk_95=var_95,
            value_at_risk_99=var_99,
            expected_outcome=expected,
            skewness=skewness,
            kurtosis=kurtosis,
            all_sentiments=sentiments,
            all_outcomes=outcomes,
            run_results=run_results,
        )
    
    def _default_market_data_generator(self, run_index: int) -> Dict[str, Any]:
        """Generate randomized market data for Monte Carlo runs."""
        # Vary parameters randomly to simulate different market conditions
        return {
            "price_trend": self.rng.gauss(0, 0.3),  # Mean 0, std 0.3
            "volume": self.rng.uniform(0.2, 1.0),
            "sentiment": self.rng.gauss(0, 0.4),
            "volatility": self.rng.uniform(0.1, 0.8),
            "momentum": self.rng.uniform(-0.5, 0.5),
            "timestamp": time.time() + run_index,
        }
    
    def _calculate_ci(self, data: List[float], confidence: float) -> Tuple[float, float]:
        """Calculate confidence interval."""
        if len(data) < 2:
            return (0.0, 0.0)
            
        mean = statistics.mean(data)
        std = statistics.stdev(data)
        
        # Z-scores for confidence levels
        z_scores = {0.95: 1.96, 0.99: 2.576}
        z = z_scores.get(confidence, 1.96)
        
        margin = z * (std / (len(data) ** 0.5))
        return (mean - margin, mean + margin)
    
    def _calculate_skewness(self, data: List[float], mean: float, std: float) -> float:
        """Calculate distribution skewness."""
        if std == 0 or len(data) < 3:
            return 0.0
            
        n = len(data)
        skew = sum(((x - mean) / std) ** 3 for x in data) * n / ((n - 1) * (n - 2))
        return skew
    
    def _calculate_kurtosis(self, data: List[float], mean: float, std: float) -> float:
        """Calculate distribution kurtosis (excess kurtosis)."""
        if std == 0 or len(data) < 4:
            return 0.0
            
        n = len(data)
        kurt = sum(((x - mean) / std) ** 4 for x in data) * (n * (n + 1)) / ((n - 1) * (n - 2) * (n - 3))
        kurt -= 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))  # Excess kurtosis
        return kurt


class SensitivityAnalyzer:
    """
    Sensitivity analysis to determine which variables matter most.
    
    Uses correlation analysis and partial derivative approximation
    to rank variables by their impact on outcomes.
    """
    
    def __init__(self, agents: Optional[List[Agent]] = None):
        self.agents = agents or create_agent_team()
        
    async def analyze(
        self,
        variables: Optional[List[str]] = None,
        num_samples: int = 500,
        base_market_data: Optional[Dict[str, Any]] = None,
    ) -> List[SensitivityResult]:
        """
        Perform sensitivity analysis on market variables.
        
        Args:
            variables: List of variable names to analyze
            num_samples: Number of samples per variable
            base_market_data: Base market data to perturb
            
        Returns:
            List of SensitivityResult ranked by impact
        """
        if variables is None:
            variables = ["price_trend", "volume", "sentiment", "volatility", "momentum"]
            
        if base_market_data is None:
            base_market_data = {
                "price_trend": 0.0,
                "volume": 0.5,
                "sentiment": 0.0,
                "volatility": 0.3,
                "momentum": 0.0,
            }
            
        results = []
        
        for var in variables:
            correlation_sentiment, correlation_accuracy = await self._analyze_variable(
                var, num_samples, base_market_data
            )
            
            # Calculate composite impact score
            impact = (abs(correlation_sentiment) + abs(correlation_accuracy)) / 2
            
            results.append(SensitivityResult(
                variable_name=var,
                correlation_with_sentiment=correlation_sentiment,
                correlation_with_accuracy=correlation_accuracy,
                impact_score=impact,
                rank=0,  # Will be set after sorting
            ))
            
        # Sort by impact and assign ranks
        results.sort(key=lambda x: x.impact_score, reverse=True)
        for i, result in enumerate(results, 1):
            result.rank = i
            
        return results
    
    async def _analyze_variable(
        self,
        variable: str,
        num_samples: int,
        base_data: Dict[str, Any],
    ) -> Tuple[float, float]:
        """Analyze sensitivity of a single variable."""
        var_values = []
        sentiments = []
        accuracies = []
        
        runner = SimulationRunner(agents=self.agents, rounds=1, round_delay=0)
        
        for i in range(num_samples):
            # Create perturbed market data
            market_data = copy.deepcopy(base_data)
            
            # Vary this variable while keeping others constant
            if variable == "price_trend":
                value = random.gauss(0, 0.5)
            elif variable == "volume":
                value = random.uniform(0.1, 1.0)
            elif variable == "sentiment":
                value = random.gauss(0, 0.5)
            elif variable == "volatility":
                value = random.uniform(0.05, 0.9)
            elif variable == "momentum":
                value = random.uniform(-0.6, 0.6)
            else:
                value = random.uniform(-1, 1)
                
            market_data[variable] = value
            var_values.append(value)
            
            # Run simulation
            result = await runner.run(
                market_data_feed=lambda _: market_data
            )
            
            sentiment = result.final_consensus.get("sentiment", 0.0)
            sentiments.append(sentiment)
            
            # Calculate average accuracy
            avg_accuracy = sum(a.memory.accuracy_score for a in self.agents) / len(self.agents)
            accuracies.append(avg_accuracy)
            
        # Calculate correlations
        corr_sentiment = self._correlation(var_values, sentiments)
        corr_accuracy = self._correlation(var_values, accuracies)
        
        return corr_sentiment, corr_accuracy
    
    def _correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
            
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denom_x = sum((xi - mean_x) ** 2 for xi in x) ** 0.5
        denom_y = sum((yi - mean_y) ** 2 for yi in y) ** 0.5
        
        if denom_x == 0 or denom_y == 0:
            return 0.0
            
        return numerator / (denom_x * denom_y)


class ScenarioComparator:
    """
    A/B testing for scenario comparison.
    
    Compare two scenarios statistically to determine which is better
    and with what confidence.
    """
    
    def __init__(self, agents: Optional[List[Agent]] = None):
        self.agents = agents or create_agent_team()
        
    async def compare(
        self,
        scenario_a: Dict[str, Any],
        scenario_b: Dict[str, Any],
        scenario_a_name: str = "Scenario A",
        scenario_b_name: str = "Scenario B",
        num_runs: int = 1000,
    ) -> ScenarioComparison:
        """
        Compare two scenarios statistically.
        
        Args:
            scenario_a: Market data for scenario A
            scenario_b: Market data for scenario B
            scenario_a_name: Name for scenario A
            scenario_b_name: Name for scenario B
            num_runs: Number of simulation runs per scenario
            
        Returns:
            ScenarioComparison with statistical analysis
        """
        # Run simulations for both scenarios
        results_a = await self._run_scenario(scenario_a, num_runs)
        results_b = await self._run_scenario(scenario_b, num_runs)
        
        sentiments_a = [r["sentiment"] for r in results_a]
        sentiments_b = [r["sentiment"] for r in results_b]
        
        # Calculate statistics
        mean_a = statistics.mean(sentiments_a)
        mean_b = statistics.mean(sentiments_b)
        sentiment_diff = mean_a - mean_b
        
        # Win probabilities (direct comparison)
        a_wins = sum(1 for a, b in zip(sentiments_a, sentiments_b) if a > b)
        b_wins = sum(1 for a, b in zip(sentiments_a, sentiments_b) if b > a)
        ties = num_runs - a_wins - b_wins
        
        win_prob_a = (a_wins + ties / 2) / num_runs
        win_prob_b = (b_wins + ties / 2) / num_runs
        
        # Risk comparison (standard deviation as risk proxy)
        std_a = statistics.stdev(sentiments_a) if len(sentiments_a) > 1 else 0.01
        std_b = statistics.stdev(sentiments_b) if len(sentiments_b) > 1 else 0.01
        risk_ratio = std_a / std_b
        
        # Statistical significance (Welch's t-test approximation)
        significance = self._welch_ttest(sentiments_a, sentiments_b)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            sentiment_diff, win_prob_a, win_prob_b, risk_ratio, significance
        )
        
        return ScenarioComparison(
            scenario_a_name=scenario_a_name,
            scenario_b_name=scenario_b_name,
            sentiment_diff=sentiment_diff,
            win_probability_a=win_prob_a,
            win_probability_b=win_prob_b,
            expected_value_a=mean_a,
            expected_value_b=mean_b,
            risk_ratio=risk_ratio,
            recommendation=recommendation,
            statistical_significance=significance,
        )
    
    async def _run_scenario(
        self,
        market_data: Dict[str, Any],
        num_runs: int,
    ) -> List[Dict[str, Any]]:
        """Run multiple simulations with given market data."""
        results = []
        runner = SimulationRunner(agents=self.agents, rounds=1, round_delay=0)
        
        for _ in range(num_runs):
            result = await runner.run(
                market_data_feed=lambda _: market_data
            )
            
            results.append({
                "sentiment": result.final_consensus.get("sentiment", 0.0),
                "direction": result.final_consensus.get("direction", "neutral"),
            })
            
        return results
    
    def _welch_ttest(self, a: List[float], b: List[float]) -> float:
        """
        Welch's t-test for unequal variances.
        Returns p-value (lower = more significant).
        """
        if len(a) < 2 or len(b) < 2:
            return 1.0
            
        mean_a = statistics.mean(a)
        mean_b = statistics.mean(b)
        var_a = statistics.variance(a)
        var_b = statistics.variance(b)
        n_a = len(a)
        n_b = len(b)
        
        # Standard error
        se = (var_a / n_a + var_b / n_b) ** 0.5
        
        if se == 0:
            return 1.0 if abs(mean_a - mean_b) < 0.001 else 0.0
            
        # t-statistic
        t = abs(mean_a - mean_b) / se
        
        # Degrees of freedom (Welch-Satterthwaite)
        numerator = (var_a / n_a + var_b / n_b) ** 2
        denominator = (var_a / n_a) ** 2 / (n_a - 1) + (var_b / n_b) ** 2 / (n_b - 1)
        df = numerator / denominator if denominator > 0 else 1
        
        # Approximate p-value (simplified)
        # For df > 30, t > 2 gives p < 0.05
        if df > 30:
            if t > 2.576:
                return 0.01
            elif t > 1.96:
                return 0.05
            elif t > 1.645:
                return 0.10
            else:
                return 0.5
        else:
            return min(1.0, 2 / (1 + t ** 2))  # Rough approximation
    
    def _generate_recommendation(
        self,
        sentiment_diff: float,
        win_prob_a: float,
        win_prob_b: float,
        risk_ratio: float,
        significance: float,
    ) -> str:
        """Generate human-readable recommendation."""
        parts = []
        
        # Winner
        if win_prob_a > 0.6:
            parts.append(f"Scenario A significantly outperforms ({win_prob_a:.0%} win rate)")
        elif win_prob_b > 0.6:
            parts.append(f"Scenario B significantly outperforms ({win_prob_b:.0%} win rate)")
        elif win_prob_a > 0.55:
            parts.append(f"Scenario A has slight edge ({win_prob_a:.0%} win rate)")
        elif win_prob_b > 0.55:
            parts.append(f"Scenario B has slight edge ({win_prob_b:.0%} win rate)")
        else:
            parts.append("Scenarios are statistically similar")
            
        # Risk
        if risk_ratio > 1.3:
            parts.append(f"but A carries {risk_ratio:.1f}x more risk")
        elif risk_ratio < 0.77:  # 1/1.3
            parts.append(f"with A being {1/risk_ratio:.1f}x less risky")
            
        # Significance
        if significance < 0.05:
            parts.append("(statistically significant)")
        elif significance < 0.10:
            parts.append("(marginally significant)")
        else:
            parts.append("(not statistically significant)")
            
        return " ".join(parts)


class Backtester:
    """
    Backtesting engine for historical data validation.
    
    Tests agent predictions against known historical outcomes
    to validate strategy performance.
    """
    
    def __init__(self, agents: Optional[List[Agent]] = None):
        self.agents = agents or create_agent_team()
        
    async def backtest(
        self,
        historical_data: List[Dict[str, Any]],
        outcome_key: str = "actual_outcome",
        position_size: float = 1.0,
    ) -> BacktestResult:
        """
        Run backtest against historical data.
        
        Args:
            historical_data: List of market data dicts with actual outcomes
            outcome_key: Key containing actual outcome (-1, 0, 1)
            position_size: Size of each position for P&L calculation
            
        Returns:
            BacktestResult with performance metrics
        """
        if not historical_data:
            raise ValueError("Historical data cannot be empty")
            
        predictions = []
        actuals = []
        pnl_values = []
        equity = [1.0]  # Start with 1.0 (100%)
        trades = []
        
        runner = SimulationRunner(agents=self.agents, rounds=1, round_delay=0)
        
        for i, data_point in enumerate(historical_data):
            actual = data_point.get(outcome_key, 0)
            
            # Run prediction (remove outcome from input)
            market_data = {k: v for k, v in data_point.items() if k != outcome_key}
            result = await runner.run(market_data_feed=lambda _: market_data)
            
            pred_direction = result.final_consensus.get("direction", "neutral")
            pred_numeric = {"bullish": 1, "bearish": -1, "neutral": 0}.get(pred_direction, 0)
            
            predictions.append(pred_direction)
            actuals.append(actual)
            
            # Calculate P&L
            if pred_direction != "neutral":
                pnl = pred_numeric * actual * position_size
                pnl_values.append(pnl)
                
                trades.append({
                    "index": i,
                    "predicted": pred_direction,
                    "actual": actual,
                    "pnl": pnl,
                    "cumulative_pnl": sum(pnl_values),
                })
                
                # Update equity curve
                equity.append(equity[-1] + pnl)
            else:
                # No position
                equity.append(equity[-1])
                
        # Calculate metrics
        accuracy = self._calculate_accuracy(predictions, actuals)
        precision, recall, f1 = self._calculate_classification_metrics(predictions, actuals)
        confusion = self._calculate_confusion_matrix(predictions, actuals)
        
        sharpe = self._calculate_sharpe(pnl_values)
        max_dd = self._calculate_max_drawdown(equity)
        profit_factor = self._calculate_profit_factor(pnl_values)
        
        return BacktestResult(
            total_predictions=len(predictions),
            correct_predictions=sum(1 for p, a in zip(predictions, actuals) 
                                   if self._is_correct(p, a)),
            accuracy_rate=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            confusion_matrix=confusion,
            sharpe_ratio=sharpe,
            max_drawdown=max_dd,
            profit_factor=profit_factor,
            equity_curve=equity,
            trades=trades,
        )
    
    def _is_correct(self, pred: str, actual: int) -> bool:
        """Check if prediction matches actual outcome."""
        pred_map = {"bullish": 1, "bearish": -1, "neutral": 0}
        return pred_map.get(pred, 0) == actual
    
    def _calculate_accuracy(self, predictions: List[str], actuals: List[int]) -> float:
        """Calculate overall accuracy."""
        correct = sum(1 for p, a in zip(predictions, actuals) if self._is_correct(p, a))
        return correct / len(predictions) if predictions else 0.0
    
    def _calculate_classification_metrics(
        self,
        predictions: List[str],
        actuals: List[int],
    ) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, float]]:
        """Calculate precision, recall, and F1 score per class."""
        classes = ["bullish", "bearish", "neutral"]
        class_map = {1: "bullish", -1: "bearish", 0: "neutral"}
        
        precision = {}
        recall = {}
        f1 = {}
        
        for cls in classes:
            # True positives
            tp = sum(1 for p, a in zip(predictions, actuals) 
                    if p == cls and class_map.get(a) == cls)
            # False positives
            fp = sum(1 for p, a in zip(predictions, actuals)
                    if p == cls and class_map.get(a) != cls)
            # False negatives
            fn = sum(1 for p, a in zip(predictions, actuals)
                    if p != cls and class_map.get(a) == cls)
            
            prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1_score = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
            
            precision[cls] = prec
            recall[cls] = rec
            f1[cls] = f1_score
            
        return precision, recall, f1
    
    def _calculate_confusion_matrix(
        self,
        predictions: List[str],
        actuals: List[int],
    ) -> Dict[str, Dict[str, int]]:
        """Build confusion matrix."""
        class_map = {1: "bullish", -1: "bearish", 0: "neutral"}
        matrix = defaultdict(lambda: defaultdict(int))
        
        for pred, actual in zip(predictions, actuals):
            actual_str = class_map.get(actual, "unknown")
            matrix[pred][actual_str] += 1
            
        return dict(matrix)
    
    def _calculate_sharpe(self, returns: List[float]) -> float:
        """Calculate Sharpe ratio (simplified, assuming 0 risk-free rate)."""
        if len(returns) < 2:
            return 0.0
            
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        return mean_return / std_return if std_return > 0 else 0.0
    
    def _calculate_max_drawdown(self, equity: List[float]) -> float:
        """Calculate maximum drawdown percentage."""
        if not equity or len(equity) < 2:
            return 0.0
            
        peak = equity[0]
        max_dd = 0.0
        
        for value in equity:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak if peak > 0 else 0.0
            max_dd = max(max_dd, drawdown)
            
        return max_dd
    
    def _calculate_profit_factor(self, returns: List[float]) -> float:
        """Calculate profit factor (gross profit / gross loss)."""
        gross_profit = sum(r for r in returns if r > 0)
        gross_loss = abs(sum(r for r in returns if r < 0))
        
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')


class AdvancedSimulationSuite:
    """
    Unified interface for all advanced simulation features.
    
    Provides convenient access to Monte Carlo, sensitivity analysis,
    scenario comparison, and backtesting in a single class.
    """
    
    def __init__(self, agents: Optional[List[Agent]] = None):
        self.agents = agents or create_agent_team()
        self.monte_carlo = MonteCarloSimulator(agents=self.agents)
        self.sensitivity = SensitivityAnalyzer(agents=self.agents)
        self.comparator = ScenarioComparator(agents=self.agents)
        self.backtester = Backtester(agents=self.agents)
        
    async def run_full_analysis(
        self,
        base_market_data: Optional[Dict[str, Any]] = None,
        num_monte_carlo_runs: int = 1000,
    ) -> Dict[str, Any]:
        """
        Run complete advanced analysis suite.
        
        Args:
            base_market_data: Starting market conditions
            num_monte_carlo_runs: Number of Monte Carlo simulations
            
        Returns:
            Dictionary containing all analysis results
        """
        print("🔬 Running Monte Carlo Simulation...")
        mc_result = await self.monte_carlo.run(num_simulations=num_monte_carlo_runs)
        
        print("📊 Running Sensitivity Analysis...")
        sens_results = await self.sensitivity.analyze(num_samples=500)
        
        # Create comparative scenarios based on MC results
        print("⚖️  Running Scenario Comparison...")
        optimistic = {
            "price_trend": 0.5,
            "volume": 0.8,
            "sentiment": 0.6,
            "volatility": 0.2,
            "momentum": 0.4,
        }
        pessimistic = {
            "price_trend": -0.5,
            "volume": 0.4,
            "sentiment": -0.6,
            "volatility": 0.7,
            "momentum": -0.4,
        }
        
        comp_result = await self.comparator.compare(
            optimistic, pessimistic,
            "Optimistic", "Pessimistic",
            num_runs=500
        )
        
        return {
            "monte_carlo": mc_result.to_dict(),
            "sensitivity_analysis": [
                {
                    "variable": r.variable_name,
                    "impact_score": round(r.impact_score, 4),
                    "rank": r.rank,
                    "correlation_sentiment": round(r.correlation_with_sentiment, 4),
                    "correlation_accuracy": round(r.correlation_with_accuracy, 4),
                }
                for r in sens_results
            ],
            "scenario_comparison": comp_result.to_dict(),
            "summary": {
                "dominant_direction": max(
                    [("bullish", mc_result.bullish_probability),
                     ("bearish", mc_result.bearish_probability),
                     ("neutral", mc_result.neutral_probability)],
                    key=lambda x: x[1]
                )[0],
                "confidence": mc_result.bullish_probability 
                              if mc_result.bullish_probability > mc_result.bearish_probability
                              else mc_result.bearish_probability,
                "key_drivers": [r.variable_name for r in sens_results[:3]],
            }
        }


# Convenience functions for quick usage
async def quick_monte_carlo(
    agents: Optional[List[Agent]] = None,
    runs: int = 1000,
    verbose: bool = True,
) -> MonteCarloResult:
    """Quick Monte Carlo simulation."""
    sim = MonteCarloSimulator(agents=agents)
    
    if verbose:
        def progress(completed, total):
            pct = completed / total * 100
            print(f"  Progress: {completed}/{total} ({pct:.0f}%)", end="\r")
        result = await sim.run(num_simulations=runs, progress_callback=progress)
        print()  # New line after progress
    else:
        result = await sim.run(num_simulations=runs)
        
    if verbose:
        print("\n📊 Monte Carlo Results:")
        print(f"  Runs: {result.total_runs}")
        print(f"  Bullish: {result.bullish_probability:.1%}")
        print(f"  Bearish: {result.bearish_probability:.1%}")
        print(f"  Neutral: {result.neutral_probability:.1%}")
        print(f"  Expected: {result.expected_outcome:+.3f}")
        print(f"  95% CI: [{result.confidence_interval_95[0]:+.3f}, {result.confidence_interval_95[1]:+.3f}]")
        print(f"  VaR 95%: {result.value_at_risk_95:.3f}")
        
    return result


async def quick_sensitivity(
    agents: Optional[List[Agent]] = None,
    samples: int = 500,
    verbose: bool = True,
) -> List[SensitivityResult]:
    """Quick sensitivity analysis."""
    analyzer = SensitivityAnalyzer(agents=agents)
    results = await analyzer.analyze(num_samples=samples)
    
    if verbose:
        print("\n📈 Sensitivity Analysis:")
        print(f"  {'Rank':<6}{'Variable':<15}{'Impact':<12}{'Correlation'}")
        print("  " + "-" * 50)
        for r in results:
            print(f"  {r.rank:<6}{r.variable_name:<15}{r.impact_score:<12.3f}{r.correlation_with_sentiment:+.3f}")
            
    return results


async def quick_compare(
    scenario_a: Dict[str, Any],
    scenario_b: Dict[str, Any],
    name_a: str = "A",
    name_b: str = "B",
    agents: Optional[List[Agent]] = None,
    runs: int = 1000,
    verbose: bool = True,
) -> ScenarioComparison:
    """Quick scenario comparison."""
    comparator = ScenarioComparator(agents=agents)
    result = await comparator.compare(scenario_a, scenario_b, name_a, name_b, runs)
    
    if verbose:
        print(f"\n⚖️  Scenario Comparison: {name_a} vs {name_b}")
        print(f"  {name_a} win prob: {result.win_probability_a:.1%}")
        print(f"  {name_b} win prob: {result.win_probability_b:.1%}")
        print(f"  Sentiment diff: {result.sentiment_diff:+.3f}")
        print(f"  Risk ratio (A/B): {result.risk_ratio:.2f}")
        print(f"  Significance: p={result.statistical_significance:.3f}")
        print(f"  → {result.recommendation}")
        
    return result


async def quick_backtest(
    historical_data: List[Dict[str, Any]],
    agents: Optional[List[Agent]] = None,
    verbose: bool = True,
) -> BacktestResult:
    """Quick backtest."""
    backtester = Backtester(agents=agents)
    result = await backtester.backtest(historical_data)
    
    if verbose:
        print("\n📉 Backtest Results:")
        print(f"  Predictions: {result.total_predictions}")
        print(f"  Accuracy: {result.accuracy_rate:.1%}")
        print(f"  Sharpe: {result.sharpe_ratio:.2f}")
        print(f"  Max DD: {result.max_drawdown:.1%}")
        print(f"  Profit Factor: {result.profit_factor:.2f}")
        
    return result


# Example usage
async def demo():
    """Demonstrate advanced simulation features."""
    print("=" * 60)
    print("🔬 SCALES ADVANCED SIMULATION SUITE")
    print("=" * 60)
    
    # Create agents
    agents = create_agent_team()
    print(f"\n🎭 Using {len(agents)} agents")
    
    # 1. Monte Carlo
    print("\n" + "-" * 60)
    print("1️⃣  MONTE CARLO SIMULATION")
    print("-" * 60)
    mc = await quick_monte_carlo(agents=agents, runs=1000)
    
    # 2. Sensitivity Analysis
    print("\n" + "-" * 60)
    print("2️⃣  SENSITIVITY ANALYSIS")
    print("-" * 60)
    sens = await quick_sensitivity(agents=agents, samples=500)
    
    # 3. Scenario Comparison
    print("\n" + "-" * 60)
    print("3️⃣  SCENARIO COMPARISON")
    print("-" * 60)
    
    bull_market = {
        "price_trend": 0.6,
        "volume": 0.9,
        "sentiment": 0.7,
        "volatility": 0.2,
        "momentum": 0.5,
    }
    bear_market = {
        "price_trend": -0.6,
        "volume": 0.5,
        "sentiment": -0.7,
        "volatility": 0.8,
        "momentum": -0.5,
    }
    
    comp = await quick_compare(
        bull_market, bear_market,
        "Bull Market", "Bear Market",
        agents=agents, runs=500
    )
    
    # 4. Backtesting
    print("\n" + "-" * 60)
    print("4️⃣  BACKTESTING")
    print("-" * 60)
    
    # Generate synthetic historical data
    historical = []
    for i in range(100):
        actual = random.choice([-1, 0, 1])
        historical.append({
            "price_trend": actual * 0.5 + random.gauss(0, 0.2),
            "volume": random.uniform(0.3, 1.0),
            "sentiment": actual * 0.4 + random.gauss(0, 0.3),
            "volatility": random.uniform(0.1, 0.6),
            "actual_outcome": actual,
        })
    
    backtest = await quick_backtest(historical, agents=agents)
    
    print("\n" + "=" * 60)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 60)
    
    return {
        "monte_carlo": mc,
        "sensitivity": sens,
        "comparison": comp,
        "backtest": backtest,
    }


if __name__ == "__main__":
    asyncio.run(demo())
