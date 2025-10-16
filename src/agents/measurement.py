"""Measurement Agent - Designs and analyzes lift experiments."""

import logging
import numpy as np
from typing import Dict, Any, List, Optional
from scipy import stats
from dataclasses import dataclass

from ..schemas.tools import (
    DesignExperimentInput,
    DesignExperimentOutput,
    ExperimentCell,
)

logger = logging.getLogger(__name__)


@dataclass
class PowerAnalysis:
    """Power analysis results."""
    required_sample_size: int
    power: float
    alpha: float
    effect_size: float
    variance_estimate: float


class ExperimentDesigner:
    """Designs experiments for causal lift measurement."""
    
    @staticmethod
    def design_geo_experiment(
        input_data: DesignExperimentInput,
        available_geos: Optional[List[str]] = None
    ) -> DesignExperimentOutput:
        """Design a geo-based randomized experiment.
        
        Args:
            input_data: Experiment design input
            available_geos: List of available geographic units
            
        Returns:
            Experiment design output
        """
        # Power analysis
        power_analysis = ExperimentDesigner._power_analysis(
            effect_size=input_data.min_detectable_effect,
            power=input_data.power,
            alpha=0.05
        )
        
        sample_size = power_analysis.required_sample_size
        
        # Generate or use available geos
        if available_geos is None:
            available_geos = [f"geo_{i:03d}" for i in range(sample_size)]
        
        # Randomize assignment
        np.random.shuffle(available_geos)
        
        control_size = sample_size // 2
        treatment_size = sample_size - control_size
        
        cells = [
            ExperimentCell(
                cell_id="control",
                assignment="control",
                units=available_geos[:control_size],
                expected_size=control_size
            ),
            ExperimentCell(
                cell_id="treatment",
                assignment="treatment",
                units=available_geos[control_size:control_size + treatment_size],
                expected_size=treatment_size
            )
        ]
        
        # Success criteria
        success_criteria = [
            f"Detect minimum {input_data.min_detectable_effect:.1%} lift in {input_data.goal}",
            f"Statistical significance at p < 0.05",
            f"Statistical power >= {input_data.power:.0%}",
            "Balanced covariates between control and treatment",
            "No spillover effects detected"
        ]
        
        if input_data.covariates:
            success_criteria.append(f"Adjust for covariates: {', '.join(input_data.covariates)}")
        
        return DesignExperimentOutput(
            design="randomized_geo",
            sample_size=sample_size,
            cells=cells,
            success_criteria=success_criteria,
            expected_runtime_weeks=input_data.duration_weeks,
            power_analysis={
                "power": power_analysis.power,
                "alpha": power_analysis.alpha,
                "effect_size": power_analysis.effect_size,
                "required_sample_size": power_analysis.required_sample_size,
                "variance_estimate": power_analysis.variance_estimate
            }
        )
    
    @staticmethod
    def design_switchback_experiment(
        input_data: DesignExperimentInput,
        available_units: Optional[List[str]] = None
    ) -> DesignExperimentOutput:
        """Design a time-based switchback experiment.
        
        Args:
            input_data: Experiment design input
            available_units: List of available units (stores, regions)
            
        Returns:
            Experiment design output
        """
        # For switchback, we need fewer units but more time periods
        power_analysis = ExperimentDesigner._power_analysis(
            effect_size=input_data.min_detectable_effect,
            power=input_data.power,
            alpha=0.05
        )
        
        # Switchback typically needs fewer units
        num_units = max(10, power_analysis.required_sample_size // 10)
        num_periods = input_data.duration_weeks * 7  # Daily switchbacks
        
        if available_units is None:
            available_units = [f"unit_{i:03d}" for i in range(num_units)]
        
        # Create switchback schedule
        cells = []
        for i, unit in enumerate(available_units[:num_units]):
            # Alternate assignment by day
            assignment = "control" if i % 2 == 0 else "treatment"
            cells.append(
                ExperimentCell(
                    cell_id=f"{assignment}_{i}",
                    assignment=assignment,
                    units=[unit],
                    expected_size=num_periods // 2
                )
            )
        
        success_criteria = [
            f"Detect minimum {input_data.min_detectable_effect:.1%} lift in {input_data.goal}",
            "Account for time-of-week effects",
            "No carryover effects between periods",
            f"Minimum {num_periods} time periods for stable estimates"
        ]
        
        return DesignExperimentOutput(
            design="time_switchback",
            sample_size=num_units * num_periods,
            cells=cells,
            success_criteria=success_criteria,
            expected_runtime_weeks=input_data.duration_weeks,
            power_analysis={
                "power": power_analysis.power,
                "alpha": power_analysis.alpha,
                "effect_size": power_analysis.effect_size,
                "num_units": num_units,
                "num_periods": num_periods
            }
        )
    
    @staticmethod
    def _power_analysis(
        effect_size: float,
        power: float,
        alpha: float,
        variance_ratio: float = 1.0
    ) -> PowerAnalysis:
        """Perform power analysis for sample size calculation.
        
        Args:
            effect_size: Minimum detectable effect size
            power: Desired statistical power
            alpha: Significance level
            variance_ratio: Ratio of treatment to control variance
            
        Returns:
            Power analysis results
        """
        # Using two-sample t-test power calculation
        # Simplified - assumes equal variance and normal distribution
        
        z_alpha = stats.norm.ppf(1 - alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        # Assumed variance (would be estimated from historical data)
        assumed_variance = 1.0
        
        # Sample size per group
        n_per_group = (
            (z_alpha + z_beta) ** 2 *
            2 * assumed_variance *
            (1 + variance_ratio) /
            (effect_size ** 2)
        )
        
        n_per_group = int(np.ceil(n_per_group))
        total_sample_size = n_per_group * 2
        
        return PowerAnalysis(
            required_sample_size=total_sample_size,
            power=power,
            alpha=alpha,
            effect_size=effect_size,
            variance_estimate=assumed_variance
        )


class LiftAnalyzer:
    """Analyzes experiment results to estimate causal lift."""
    
    @staticmethod
    def analyze_experiment(
        control_outcomes: np.ndarray,
        treatment_outcomes: np.ndarray,
        covariates_control: Optional[np.ndarray] = None,
        covariates_treatment: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Analyze experiment results.
        
        Args:
            control_outcomes: Outcomes for control group
            treatment_outcomes: Outcomes for treatment group
            covariates_control: Covariates for control group
            covariates_treatment: Covariates for treatment group
            
        Returns:
            Analysis results with lift estimate and confidence intervals
        """
        # Simple difference-in-means
        control_mean = np.mean(control_outcomes)
        treatment_mean = np.mean(treatment_outcomes)
        
        ate = treatment_mean - control_mean
        relative_lift = ate / control_mean if control_mean > 0 else 0
        
        # Standard errors
        control_se = np.std(control_outcomes, ddof=1) / np.sqrt(len(control_outcomes))
        treatment_se = np.std(treatment_outcomes, ddof=1) / np.sqrt(len(treatment_outcomes))
        ate_se = np.sqrt(control_se**2 + treatment_se**2)
        
        # Confidence interval
        ci_95 = stats.norm.interval(0.95, loc=ate, scale=ate_se)
        
        # P-value
        t_stat = ate / ate_se if ate_se > 0 else 0
        p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
        
        return {
            "control_mean": float(control_mean),
            "treatment_mean": float(treatment_mean),
            "ate": float(ate),
            "relative_lift": float(relative_lift),
            "ate_se": float(ate_se),
            "ci_95_lower": float(ci_95[0]),
            "ci_95_upper": float(ci_95[1]),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
            "n_control": len(control_outcomes),
            "n_treatment": len(treatment_outcomes)
        }


class MeasurementAgent:
    """Agent for experiment design and lift measurement."""
    
    def __init__(self):
        """Initialize Measurement Agent."""
        logger.info("Measurement Agent initialized")
    
    def design_experiment(self, input_data: DesignExperimentInput) -> DesignExperimentOutput:
        """Design an experiment based on input specification.
        
        Args:
            input_data: Experiment design input
            
        Returns:
            Experiment design output
        """
        logger.info(f"Designing {input_data.units} experiment for {input_data.goal}")
        
        if input_data.units in ["geo", "store", "region"]:
            return ExperimentDesigner.design_geo_experiment(input_data)
        elif input_data.units == "time_switchback":
            return ExperimentDesigner.design_switchback_experiment(input_data)
        else:
            raise ValueError(f"Unsupported experiment unit type: {input_data.units}")
    
    def analyze_lift(
        self,
        control_data: np.ndarray,
        treatment_data: np.ndarray,
        covariates_control: Optional[np.ndarray] = None,
        covariates_treatment: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Analyze experiment results to estimate lift.
        
        Args:
            control_data: Control group outcomes
            treatment_data: Treatment group outcomes
            covariates_control: Control group covariates
            covariates_treatment: Treatment group covariates
            
        Returns:
            Lift analysis results
        """
        logger.info(f"Analyzing lift: {len(control_data)} control, {len(treatment_data)} treatment")
        
        results = LiftAnalyzer.analyze_experiment(
            control_data,
            treatment_data,
            covariates_control,
            covariates_treatment
        )
        
        logger.info(
            f"Lift: {results['relative_lift']:.2%}, "
            f"p-value: {results['p_value']:.4f}, "
            f"significant: {results['significant']}"
        )
        
        return results


def main():
    """CLI entry point for Measurement Agent."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Measurement Agent")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Design experiment
    design_parser = subparsers.add_parser("design", help="Design an experiment")
    design_parser.add_argument("--input", type=Path, required=True, help="Input JSON file")
    design_parser.add_argument("--output", type=Path, help="Output JSON file")
    
    # Analyze lift
    analyze_parser = subparsers.add_parser("analyze", help="Analyze experiment results")
    analyze_parser.add_argument("--control", type=Path, required=True, help="Control data CSV")
    analyze_parser.add_argument("--treatment", type=Path, required=True, help="Treatment data CSV")
    analyze_parser.add_argument("--output", type=Path, help="Output JSON file")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    agent = MeasurementAgent()
    
    if args.command == "design":
        # Load input
        with open(args.input, 'r') as f:
            input_dict = json.load(f)
        
        input_data = DesignExperimentInput(**input_dict)
        
        # Design experiment
        output = agent.design_experiment(input_data)
        
        # Print results
        print("\n=== Experiment Design ===")
        print(f"Design: {output.design}")
        print(f"Sample Size: {output.sample_size}")
        print(f"Duration: {output.expected_runtime_weeks} weeks")
        print(f"\nCells:")
        for cell in output.cells:
            print(f"  {cell.assignment}: {len(cell.units)} units")
        print(f"\nSuccess Criteria:")
        for criterion in output.success_criteria:
            print(f"  - {criterion}")
        
        # Save output
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(output.model_dump(), f, indent=2)
            print(f"\nOutput saved to {args.output}")
    
    elif args.command == "analyze":
        import pandas as pd
        
        # Load data
        control_df = pd.read_csv(args.control)
        treatment_df = pd.read_csv(args.treatment)
        
        # Analyze
        results = agent.analyze_lift(
            control_df['outcome'].values,
            treatment_df['outcome'].values
        )
        
        # Print results
        print("\n=== Lift Analysis ===")
        print(f"Control Mean: {results['control_mean']:.2f}")
        print(f"Treatment Mean: {results['treatment_mean']:.2f}")
        print(f"Absolute Lift: {results['ate']:.2f}")
        print(f"Relative Lift: {results['relative_lift']:.2%}")
        print(f"95% CI: [{results['ci_95_lower']:.2f}, {results['ci_95_upper']:.2f}]")
        print(f"P-value: {results['p_value']:.4f}")
        print(f"Significant: {results['significant']}")
        
        # Save output
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nOutput saved to {args.output}")


if __name__ == "__main__":
    from pathlib import Path
    main()
