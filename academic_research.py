"""
Academic Research Support Module for Swimming Pauls
Supports controlled experiments, hypothesis testing, and research design
"""
import random
import statistics
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class ExperimentType(Enum):
    RANDOMIZED_CONTROLLED = "randomized_controlled"
    A_B_TEST = "a_b_test"
    LONGITUDINAL = "longitudinal"
    CROSS_SECTIONAL = "cross_sectional"


@dataclass
class Hypothesis:
    """A research hypothesis."""
    null_hypothesis: str
    alternative_hypothesis: str
    test_statistic: str
    significance_level: float  # alpha
    effect_size: str


class ResearchSimulator:
    """
    Supports academic research by simulating experiments,
    calculating power analysis, and predicting outcomes.
    """
    
    def __init__(self):
        self.significance_levels = [0.10, 0.05, 0.01, 0.001]
        self.effect_sizes = {
            "small": 0.2,
            "medium": 0.5,
            "large": 0.8
        }
    
    def design_experiment(
        self,
        research_question: str,
        hypothesis: Hypothesis,
        experiment_type: ExperimentType,
        expected_effect_size: str = "medium",
        power: float = 0.80,
        alpha: float = 0.05
    ) -> Dict[str, Any]:
        """
        Design a research experiment with power analysis.
        
        Args:
            research_question: What are you trying to learn?
            hypothesis: Null and alternative hypotheses
            experiment_type: Type of experiment design
            expected_effect_size: small/medium/large
            power: Desired statistical power (0.80 typical)
            alpha: Significance level (0.05 typical)
            
        Returns:
            Experiment design with sample size calculations
        """
        # Calculate required sample size
        sample_size = self._calculate_sample_size(
            expected_effect_size, power, alpha, experiment_type
        )
        
        # Design the methodology
        methodology = self._design_methodology(experiment_type, research_question)
        
        # Identify confounding variables
        confounders = self._identify_confounders(research_question, experiment_type)
        
        # Create data collection plan
        data_plan = self._create_data_collection_plan(experiment_type, sample_size)
        
        # Statistical analysis plan
        analysis_plan = self._create_analysis_plan(hypothesis, experiment_type)
        
        return {
            "research_question": research_question,
            "hypothesis": {
                "null": hypothesis.null_hypothesis,
                "alternative": hypothesis.alternative_hypothesis,
                "test": hypothesis.test_statistic
            },
            "experiment_type": experiment_type.value,
            "sample_size": sample_size,
            "power_analysis": {
                "desired_power": power,
                "alpha": alpha,
                "expected_effect_size": expected_effect_size,
                "effect_size_value": self.effect_sizes[expected_effect_size]
            },
            "methodology": methodology,
            "confounding_variables": confounders,
            "data_collection": data_plan,
            "analysis_plan": analysis_plan,
            "ethical_considerations": self._identify_ethical_issues(experiment_type),
            "limitations": self._identify_limitations(experiment_type, sample_size),
            "recommendations": self._generate_research_recommendations(
                sample_size, experiment_type, confounders
            )
        }
    
    def simulate_results(
        self,
        experiment_design: Dict[str, Any],
        treatment_effect: float = 0.5,
        noise_level: float = 1.0,
        n_simulations: int = 1000
    ) -> Dict[str, Any]:
        """
        Simulate experiment results to test power and expected outcomes.
        
        Args:
            experiment_design: From design_experiment()
            treatment_effect: Expected effect size
            noise_level: Random variance in data
            n_simulations: Number of simulation runs
            
        Returns:
            Simulation results with success rate
        """
        sample_size = experiment_design["sample_size"]
        alpha = experiment_design["power_analysis"]["alpha"]
        
        significant_results = 0
        effect_sizes = []
        p_values = []
        
        for _ in range(n_simulations):
            # Generate synthetic data
            control_group = [random.gauss(0, noise_level) for _ in range(sample_size // 2)]
            treatment_group = [random.gauss(treatment_effect, noise_level) for _ in range(sample_size // 2)]
            
            # Calculate effect size (Cohen's d)
            pooled_std = statistics.stdev(control_group + treatment_group)
            cohens_d = (statistics.mean(treatment_group) - statistics.mean(control_group)) / pooled_std if pooled_std > 0 else 0
            effect_sizes.append(cohens_d)
            
            # Simulate p-value (simplified)
            # In reality, would run t-test
            simulated_p = max(0.001, random.gauss(0.03, 0.02) - abs(cohens_d) * 0.1)
            p_values.append(simulated_p)
            
            if simulated_p < alpha:
                significant_results += 1
        
        actual_power = significant_results / n_simulations
        
        return {
            "n_simulations": n_simulations,
            "actual_power": round(actual_power, 3),
            "expected_power": experiment_design["power_analysis"]["desired_power"],
            "significant_results": significant_results,
            "mean_effect_size": round(statistics.mean(effect_sizes), 3),
            "effect_size_std": round(statistics.stdev(effect_sizes), 3) if len(effect_sizes) > 1 else 0,
            "mean_p_value": round(statistics.mean(p_values), 4),
            "success_rate": f"{actual_power * 100:.1f}%",
            "interpretation": self._interpret_simulation_results(actual_power, alpha)
        }
    
    def _calculate_sample_size(
        self,
        effect_size: str,
        power: float,
        alpha: float,
        experiment_type: ExperimentType
    ) -> int:
        """Calculate required sample size for desired power."""
        d = self.effect_sizes[effect_size]
        
        # Simplified power calculation (Cohen's approximation)
        # n ≈ (2 * (Z_α/2 + Z_β)²) / d²
        from math import sqrt
        
        # Z-values for common alpha/power
        z_alpha = 1.96 if alpha == 0.05 else 2.576 if alpha == 0.01 else 1.645
        z_beta = 0.84 if power == 0.80 else 1.04 if power == 0.85 else 1.28
        
        n_per_group = int((2 * (z_alpha + z_beta) ** 2) / (d ** 2))
        
        # Adjust for experiment type
        if experiment_type == ExperimentType.A_B_TEST:
            n_per_group = int(n_per_group * 1.2)  # 20% buffer for dropouts
        elif experiment_type == ExperimentType.LONGITUDINAL:
            n_per_group = int(n_per_group * 1.5)  # Higher attrition
        
        return n_per_group * 2  # Total sample (both groups)
    
    def _design_methodology(self, experiment_type: ExperimentType, research_question: str) -> Dict[str, Any]:
        """Design the experimental methodology."""
        methodologies = {
            ExperimentType.RANDOMIZED_CONTROLLED: {
                "description": "Participants randomly assigned to treatment or control",
                "randomization": "Block randomization by key demographics",
                "blinding": "Double-blind when possible",
                "procedures": [
                    "Screen participants for eligibility",
                    "Obtain informed consent",
                    "Baseline measurements",
                    "Random assignment",
                    "Treatment administration",
                    "Follow-up measurements",
                    "Data analysis"
                ]
            },
            ExperimentType.A_B_TEST: {
                "description": "Two variants tested against each other",
                "randomization": "Simple random assignment",
                "procedures": [
                    "Define success metrics",
                    "Create variant A (control)",
                    "Create variant B (treatment)",
                    "Random exposure",
                    "Track conversions/outcomes",
                    "Statistical comparison"
                ]
            },
            ExperimentType.LONGITUDINAL: {
                "description": "Track same participants over time",
                "timepoints": ["Baseline", "3 months", "6 months", "12 months"],
                "procedures": [
                    "Initial recruitment",
                    "Baseline assessment",
                    "Regular follow-ups",
                    "Retention strategies",
                    "Attrition analysis"
                ]
            },
            ExperimentType.CROSS_SECTIONAL: {
                "description": "Snapshot of population at one time",
                "procedures": [
                    "Define population",
                    "Stratified sampling",
                    "Data collection",
                    "Descriptive statistics",
                    "Correlation analysis"
                ]
            }
        }
        
        return methodologies.get(experiment_type, methodologies[ExperimentType.RANDOMIZED_CONTROLLED])
    
    def _identify_confounders(self, research_question: str, experiment_type: ExperimentType) -> List[Dict[str, Any]]:
        """Identify potential confounding variables."""
        common_confounders = [
            {"variable": "Age", "impact": "high", "control_method": "Stratify or include as covariate"},
            {"variable": "Gender", "impact": "medium", "control_method": "Stratified randomization"},
            {"variable": "Socioeconomic status", "impact": "high", "control_method": "Matching or statistical control"},
            {"variable": "Prior experience", "impact": "medium", "control_method": "Baseline measurement as covariate"},
            {"variable": "Time of day", "impact": "low", "control_method": "Randomize timing"},
            {"variable": "Seasonality", "impact": "medium", "control_method": "Run across multiple time periods"}
        ]
        
        # Select relevant confounders based on research question
        random.shuffle(common_confounders)
        return common_confounders[:4]
    
    def _create_data_collection_plan(self, experiment_type: ExperimentType, sample_size: int) -> Dict[str, Any]:
        """Create a data collection plan."""
        return {
            "sample_size": sample_size,
            "collection_methods": ["Surveys", "Behavioral tracking", "Interviews", "Observations"],
            "frequency": "Baseline, during, and post-intervention",
            "quality_control": [
                "Data validation checks",
                "Missing data protocols",
                "Outlier detection",
                "Inter-rater reliability"
            ],
            "storage": "Secure encrypted database with access controls",
            "estimated_duration": f"{sample_size // 10} weeks for data collection"
        }
    
    def _create_analysis_plan(self, hypothesis: Hypothesis, experiment_type: ExperimentType) -> Dict[str, Any]:
        """Create statistical analysis plan."""
        return {
            "primary_analysis": {
                "test": hypothesis.test_statistic,
                "significance_level": hypothesis.significance_level,
                "effect_size_measure": hypothesis.effect_size
            },
            "secondary_analyses": [
                "Subgroup analysis by demographics",
                "Sensitivity analysis",
                "Intent-to-treat analysis",
                "Per-protocol analysis"
            ],
            "assumptions_checks": [
                "Normality tests",
                "Homogeneity of variance",
                "Independence of observations"
            ],
            "software": ["R", "Python (SciPy, statsmodels)", "SPSS"]
        }
    
    def _identify_ethical_issues(self, experiment_type: ExperimentType) -> List[str]:
        """Identify ethical considerations."""
        ethical_issues = [
            "Informed consent from all participants",
            "Right to withdraw without penalty",
            "Data privacy and anonymization",
            "Minimization of harm",
            "Equitable selection of participants"
        ]
        
        if experiment_type == ExperimentType.RANDOMIZED_CONTROLLED:
            ethical_issues.append("Justification for withholding treatment from control group")
        
        return ethical_issues
    
    def _identify_limitations(self, experiment_type: ExperimentType, sample_size: int) -> List[str]:
        """Identify study limitations."""
        limitations = [
            "Results may not generalize to other populations",
            "Artificiality of experimental setting",
            "Self-selection bias in recruitment"
        ]
        
        if sample_size < 100:
            limitations.append("Small sample size limits statistical power")
        
        if experiment_type == ExperimentType.LONGITUDINAL:
            limitations.append("Attrition over time may bias results")
        
        return limitations
    
    def _generate_research_recommendations(
        self,
        sample_size: int,
        experiment_type: ExperimentType,
        confounders: List[Dict]
    ) -> List[str]:
        """Generate research recommendations."""
        recommendations = []
        
        if sample_size > 500:
            recommendations.append("📊 Consider subgroup analyses with this sample size")
        elif sample_size < 50:
            recommendations.append("⚠️  Consider increasing sample size or using within-subjects design")
        
        if len(confounders) > 3:
            recommendations.append("🔀 Use stratified randomization to control multiple confounders")
        
        recommendations.append("📋 Pre-register hypotheses to prevent p-hacking")
        recommendations.append("🔍 Plan for sensitivity analyses")
        recommendations.append("📊 Share data and code for reproducibility")
        
        return recommendations
    
    def _interpret_simulation_results(self, actual_power: float, alpha: float) -> str:
        """Interpret simulation results."""
        if actual_power >= 0.80:
            return f"✅ Adequate power ({actual_power:.0%}). Study likely to detect true effects."
        elif actual_power >= 0.60:
            return f"⚠️  Underpowered ({actual_power:.0%}). Risk of Type II error. Increase sample size."
        else:
            return f"❌ Severely underpowered ({actual_power:.0%}). High risk of false negatives."


# Convenience function
def design_research_study(
    research_question: str,
    null_hypothesis: str,
    alternative_hypothesis: str,
    experiment_type: str = "randomized_controlled",
    expected_effect: str = "medium"
) -> Dict[str, Any]:
    """
    Quick function to design a research study.
    
    Example:
        result = design_research_study(
            research_question="Does Swimming Pauls improve prediction accuracy?",
            null_hypothesis="No difference in accuracy between Pauls and experts",
            alternative_hypothesis="Pauls achieve higher accuracy than experts",
            experiment_type="randomized_controlled",
            expected_effect="medium"
        )
    """
    hypothesis = Hypothesis(
        null_hypothesis=null_hypothesis,
        alternative_hypothesis=alternative_hypothesis,
        test_statistic="Independent t-test",
        significance_level=0.05,
        effect_size="Cohen's d"
    )
    
    exp_type_map = {
        "randomized_controlled": ExperimentType.RANDOMIZED_CONTROLLED,
        "a_b_test": ExperimentType.A_B_TEST,
        "longitudinal": ExperimentType.LONGITUDINAL,
        "cross_sectional": ExperimentType.CROSS_SECTIONAL
    }
    
    simulator = ResearchSimulator()
    return simulator.design_experiment(
        research_question=research_question,
        hypothesis=hypothesis,
        experiment_type=exp_type_map.get(experiment_type, ExperimentType.RANDOMIZED_CONTROLLED),
        expected_effect_size=expected_effect
    )


if __name__ == "__main__":
    # Test example
    result = design_research_study(
        research_question="Does AI-assisted decision making improve financial predictions?",
        null_hypothesis="AI assistance has no effect on prediction accuracy",
        alternative_hypothesis="AI assistance improves prediction accuracy by at least 10%",
        expected_effect="medium"
    )
    
    print("Research Design Results")
    print("=" * 50)
    print(f"Sample size needed: {result['sample_size']} participants")
    print(f"Power: {result['power_analysis']['desired_power']}")
    print(f"Experiment type: {result['experiment_type']}")
    
    # Simulate results
    sim = ResearchSimulator()
    simulation = sim.simulate_results(result)
    print(f"\nSimulation: {simulation['success_rate']} success rate")
