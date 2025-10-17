"""A/B Testing Framework for comparing adapter versions in production."""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
from collections import defaultdict
import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


class AssignmentStrategy(str, Enum):
    """Strategy for assigning users to variants."""
    RANDOM = "random"
    HASH_BASED = "hash_based"
    WEIGHTED = "weighted"


class ExperimentStatus(str, Enum):
    """Experiment lifecycle status."""
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


@dataclass
class Variant:
    """A/B test variant configuration."""
    
    variant_id: str
    adapter_ids: List[str]
    composition_strategy: str = "sequential"
    traffic_percentage: float = 0.5
    description: str = ""
    
    # Metrics
    impressions: int = 0
    successes: int = 0
    failures: int = 0
    total_latency_ms: float = 0.0
    feedback_scores: List[float] = field(default_factory=list)
    
    def get_success_rate(self) -> float:
        """Calculate success rate."""
        total = self.impressions
        return (self.successes / total) if total > 0 else 0.0
    
    def get_avg_latency(self) -> float:
        """Calculate average latency."""
        return (self.total_latency_ms / self.successes) if self.successes > 0 else 0.0
    
    def get_avg_feedback(self) -> Optional[float]:
        """Calculate average feedback score."""
        return np.mean(self.feedback_scores) if self.feedback_scores else None


@dataclass
class ABExperiment:
    """A/B test experiment configuration."""
    
    experiment_id: str
    name: str
    description: str
    variants: Dict[str, Variant]
    
    # Configuration
    assignment_strategy: AssignmentStrategy = AssignmentStrategy.HASH_BASED
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Targeting
    target_tasks: Optional[List[str]] = None
    target_retailers: Optional[List[str]] = None
    
    # Duration
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Statistical settings
    confidence_level: float = 0.95
    min_sample_size: int = 100
    
    # Tracking
    total_assignments: int = 0
    user_assignments: Dict[str, str] = field(default_factory=dict)
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_active(self) -> bool:
        """Check if experiment is currently active."""
        if self.status != ExperimentStatus.RUNNING:
            return False
        
        now = datetime.utcnow()
        
        if self.start_time and now < self.start_time:
            return False
        
        if self.end_time and now > self.end_time:
            return False
        
        return True
    
    def has_sufficient_data(self) -> bool:
        """Check if experiment has sufficient data for analysis."""
        for variant in self.variants.values():
            if variant.impressions < self.min_sample_size:
                return False
        return True


class ABTestingFramework:
    """
    A/B testing framework for comparing adapter versions.
    
    Features:
    - Multiple variants support
    - Hash-based consistent assignment
    - Statistical significance testing
    - Traffic splitting
    - Experiment lifecycle management
    - Real-time metrics collection
    """
    
    def __init__(self):
        """Initialize A/B testing framework."""
        self.experiments: Dict[str, ABExperiment] = {}
        self.active_experiments: List[str] = []
        
        logger.info("A/B Testing Framework initialized")
    
    def create_experiment(
        self,
        experiment_id: str,
        name: str,
        description: str,
        variant_configs: List[Dict[str, Any]],
        **kwargs
    ) -> ABExperiment:
        """
        Create a new A/B test experiment.
        
        Args:
            experiment_id: Unique experiment identifier
            name: Experiment name
            description: Experiment description
            variant_configs: List of variant configurations
            **kwargs: Additional experiment settings
            
        Returns:
            Created experiment
        """
        # Create variants
        variants = {}
        for config in variant_configs:
            variant_id = config['variant_id']
            variants[variant_id] = Variant(
                variant_id=variant_id,
                adapter_ids=config['adapter_ids'],
                composition_strategy=config.get('composition_strategy', 'sequential'),
                traffic_percentage=config.get('traffic_percentage', 1.0 / len(variant_configs)),
                description=config.get('description', '')
            )
        
        # Normalize traffic percentages
        total_traffic = sum(v.traffic_percentage for v in variants.values())
        if abs(total_traffic - 1.0) > 0.01:
            for variant in variants.values():
                variant.traffic_percentage /= total_traffic
        
        experiment = ABExperiment(
            experiment_id=experiment_id,
            name=name,
            description=description,
            variants=variants,
            **kwargs
        )
        
        self.experiments[experiment_id] = experiment
        
        logger.info(f"Created experiment: {experiment_id} with {len(variants)} variants")
        
        return experiment
    
    def start_experiment(self, experiment_id: str) -> None:
        """Start an experiment."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.RUNNING
        experiment.start_time = datetime.utcnow()
        
        if experiment_id not in self.active_experiments:
            self.active_experiments.append(experiment_id)
        
        logger.info(f"Started experiment: {experiment_id}")
    
    def stop_experiment(self, experiment_id: str) -> None:
        """Stop an experiment."""
        if experiment_id not in self.experiments:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        experiment = self.experiments[experiment_id]
        experiment.status = ExperimentStatus.COMPLETED
        experiment.end_time = datetime.utcnow()
        
        if experiment_id in self.active_experiments:
            self.active_experiments.remove(experiment_id)
        
        logger.info(f"Stopped experiment: {experiment_id}")
    
    def assign_variant(
        self,
        experiment_id: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Assign a user to a variant.
        
        Args:
            experiment_id: Experiment identifier
            user_id: User identifier
            context: Optional context (task, retailer, etc.)
            
        Returns:
            Variant ID or None if experiment not active
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment or not experiment.is_active():
            return None
        
        # Check targeting criteria
        if context:
            if experiment.target_tasks and context.get('task') not in experiment.target_tasks:
                return None
            if experiment.target_retailers and context.get('retailer') not in experiment.target_retailers:
                return None
        
        # Check if user already assigned
        if user_id in experiment.user_assignments:
            return experiment.user_assignments[user_id]
        
        # Assign based on strategy
        if experiment.assignment_strategy == AssignmentStrategy.HASH_BASED:
            variant_id = self._hash_based_assignment(experiment, user_id)
        elif experiment.assignment_strategy == AssignmentStrategy.WEIGHTED:
            variant_id = self._weighted_assignment(experiment)
        else:  # RANDOM
            variant_id = self._random_assignment(experiment)
        
        # Store assignment
        experiment.user_assignments[user_id] = variant_id
        experiment.total_assignments += 1
        
        return variant_id
    
    def record_impression(
        self,
        experiment_id: str,
        variant_id: str,
        success: bool,
        latency_ms: float,
        feedback_score: Optional[float] = None
    ) -> None:
        """Record an impression for a variant."""
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            logger.warning(f"Experiment not found: {experiment_id}")
            return
        
        variant = experiment.variants.get(variant_id)
        if not variant:
            logger.warning(f"Variant not found: {variant_id}")
            return
        
        variant.impressions += 1
        
        if success:
            variant.successes += 1
            variant.total_latency_ms += latency_ms
        else:
            variant.failures += 1
        
        if feedback_score is not None:
            variant.feedback_scores.append(feedback_score)
    
    def get_experiment_results(
        self,
        experiment_id: str
    ) -> Dict[str, Any]:
        """
        Get experiment results with statistical analysis.
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            Results dictionary with metrics and statistical tests
        """
        experiment = self.experiments.get(experiment_id)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_id}")
        
        results = {
            'experiment_id': experiment_id,
            'name': experiment.name,
            'status': experiment.status.value,
            'variants': {},
            'statistical_tests': {},
            'has_sufficient_data': experiment.has_sufficient_data(),
            'winner': None
        }
        
        # Collect variant metrics
        for variant_id, variant in experiment.variants.items():
            results['variants'][variant_id] = {
                'adapter_ids': variant.adapter_ids,
                'impressions': variant.impressions,
                'success_rate': variant.get_success_rate(),
                'avg_latency_ms': variant.get_avg_latency(),
                'avg_feedback': variant.get_avg_feedback(),
                'traffic_percentage': variant.traffic_percentage
            }
        
        # Perform statistical tests if sufficient data
        if experiment.has_sufficient_data():
            results['statistical_tests'] = self._run_statistical_tests(experiment)
            results['winner'] = self._determine_winner(experiment)
        
        return results
    
    def _hash_based_assignment(
        self,
        experiment: ABExperiment,
        user_id: str
    ) -> str:
        """Assign variant using consistent hashing."""
        # Hash user_id + experiment_id for consistency
        hash_input = f"{experiment.experiment_id}:{user_id}".encode()
        hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)
        
        # Map to [0, 1]
        normalized = (hash_value % 10000) / 10000.0
        
        # Assign to variant based on traffic percentages
        cumulative = 0.0
        for variant_id, variant in experiment.variants.items():
            cumulative += variant.traffic_percentage
            if normalized < cumulative:
                return variant_id
        
        # Fallback to last variant
        return list(experiment.variants.keys())[-1]
    
    def _weighted_assignment(self, experiment: ABExperiment) -> str:
        """Assign variant using weighted random selection."""
        variant_ids = list(experiment.variants.keys())
        weights = [experiment.variants[v].traffic_percentage for v in variant_ids]
        
        return random.choices(variant_ids, weights=weights, k=1)[0]
    
    def _random_assignment(self, experiment: ABExperiment) -> str:
        """Assign variant uniformly at random."""
        return random.choice(list(experiment.variants.keys()))
    
    def _run_statistical_tests(
        self,
        experiment: ABExperiment
    ) -> Dict[str, Any]:
        """Run statistical significance tests."""
        tests = {}
        
        variant_list = list(experiment.variants.items())
        
        # Pairwise tests for success rate (proportions test)
        for i in range(len(variant_list)):
            for j in range(i + 1, len(variant_list)):
                var_a_id, var_a = variant_list[i]
                var_b_id, var_b = variant_list[j]
                
                # Chi-square test for success rates
                contingency_table = [
                    [var_a.successes, var_a.failures],
                    [var_b.successes, var_b.failures]
                ]
                
                try:
                    chi2, p_value, _, _ = stats.chi2_contingency(contingency_table)
                    
                    test_key = f"{var_a_id}_vs_{var_b_id}"
                    tests[test_key] = {
                        'metric': 'success_rate',
                        'p_value': float(p_value),
                        'statistically_significant': p_value < (1 - experiment.confidence_level),
                        'variant_a': var_a_id,
                        'variant_b': var_b_id,
                        'variant_a_rate': var_a.get_success_rate(),
                        'variant_b_rate': var_b.get_success_rate()
                    }
                except Exception as e:
                    logger.error(f"Statistical test failed: {e}")
        
        return tests
    
    def _determine_winner(self, experiment: ABExperiment) -> Optional[str]:
        """Determine winning variant based on success rate."""
        if not experiment.has_sufficient_data():
            return None
        
        # Find variant with highest success rate
        best_variant = max(
            experiment.variants.items(),
            key=lambda x: x[1].get_success_rate()
        )
        
        return best_variant[0]
    
    def get_active_experiments(self) -> List[ABExperiment]:
        """Get list of active experiments."""
        return [
            self.experiments[exp_id]
            for exp_id in self.active_experiments
            if exp_id in self.experiments and self.experiments[exp_id].is_active()
        ]


# Global framework instance
_ab_framework: Optional[ABTestingFramework] = None


def get_ab_framework() -> ABTestingFramework:
    """Get global A/B testing framework instance."""
    global _ab_framework
    if _ab_framework is None:
        _ab_framework = ABTestingFramework()
    return _ab_framework


def assign_user_to_variant(
    experiment_id: str,
    user_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """Assign user to variant (convenience function)."""
    framework = get_ab_framework()
    return framework.assign_variant(experiment_id, user_id, context)
