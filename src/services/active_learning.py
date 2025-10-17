"""Active Learning module for automatically selecting uncertain examples for feedback."""

import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import torch
from sklearn.cluster import KMeans
from collections import Counter

logger = logging.getLogger(__name__)


class UncertaintyMethod(str, Enum):
    """Methods for measuring uncertainty."""
    ENTROPY = "entropy"
    VARIANCE = "variance"
    MARGIN = "margin"
    LEAST_CONFIDENCE = "least_confidence"
    DIVERSITY = "diversity"


@dataclass
class UncertainExample:
    """Example selected for human feedback."""
    
    example_id: str
    prompt: str
    model_output: str
    uncertainty_score: float
    uncertainty_method: str
    task_type: str
    metadata: Optional[Dict[str, Any]] = None
    priority: int = 1  # 1=high, 2=medium, 3=low


class ActiveLearningSelector:
    """
    Selects uncertain examples for human feedback using various strategies.
    
    Key Features:
    - Entropy-based uncertainty
    - Diversity sampling
    - Task-specific selection
    - Priority ranking
    - Batch selection with redundancy control
    """
    
    def __init__(
        self,
        method: UncertaintyMethod = UncertaintyMethod.ENTROPY,
        batch_size: int = 10,
        diversity_threshold: float = 0.3
    ):
        """Initialize active learning selector.
        
        Args:
            method: Uncertainty measurement method
            batch_size: Number of examples to select per batch
            diversity_threshold: Minimum diversity score for selection
        """
        self.method = method
        self.batch_size = batch_size
        self.diversity_threshold = diversity_threshold
        
        logger.info(f"Active Learning initialized with method: {method}")
    
    def select_uncertain_examples(
        self,
        candidates: List[Dict[str, Any]],
        logits: Optional[np.ndarray] = None,
        embeddings: Optional[np.ndarray] = None,
        previous_selections: Optional[List[str]] = None
    ) -> List[UncertainExample]:
        """
        Select most uncertain examples for human feedback.
        
        Args:
            candidates: List of candidate examples with prompts and outputs
            logits: Model output logits (for entropy/margin calculation)
            embeddings: Example embeddings (for diversity)
            previous_selections: Previously selected example IDs (avoid redundancy)
            
        Returns:
            List of uncertain examples ranked by priority
        """
        if not candidates:
            return []
        
        # Calculate uncertainty scores
        uncertainty_scores = self._calculate_uncertainty(
            candidates,
            logits=logits,
            embeddings=embeddings
        )
        
        # Remove previously selected examples
        if previous_selections:
            valid_indices = [
                i for i, c in enumerate(candidates)
                if c.get('example_id') not in previous_selections
            ]
            candidates = [candidates[i] for i in valid_indices]
            uncertainty_scores = uncertainty_scores[valid_indices]
        
        # Apply diversity filter if embeddings available
        if embeddings is not None:
            selected_indices = self._diverse_sampling(
                uncertainty_scores,
                embeddings,
                k=min(self.batch_size, len(candidates))
            )
        else:
            # Select top-k by uncertainty
            selected_indices = np.argsort(uncertainty_scores)[-self.batch_size:][::-1]
        
        # Create UncertainExample objects
        uncertain_examples = []
        for idx in selected_indices:
            candidate = candidates[idx]
            
            # Determine priority based on uncertainty
            score = uncertainty_scores[idx]
            if score > 0.8:
                priority = 1  # High
            elif score > 0.5:
                priority = 2  # Medium
            else:
                priority = 3  # Low
            
            example = UncertainExample(
                example_id=candidate.get('example_id', f"ex_{idx}"),
                prompt=candidate['prompt'],
                model_output=candidate['output'],
                uncertainty_score=float(score),
                uncertainty_method=self.method.value,
                task_type=candidate.get('task_type', 'unknown'),
                metadata=candidate.get('metadata'),
                priority=priority
            )
            uncertain_examples.append(example)
        
        logger.info(f"Selected {len(uncertain_examples)} uncertain examples")
        
        return uncertain_examples
    
    def _calculate_uncertainty(
        self,
        candidates: List[Dict[str, Any]],
        logits: Optional[np.ndarray] = None,
        embeddings: Optional[np.ndarray] = None
    ) -> np.ndarray:
        """Calculate uncertainty scores for candidates."""
        
        if self.method == UncertaintyMethod.ENTROPY and logits is not None:
            return self._entropy_uncertainty(logits)
        
        elif self.method == UncertaintyMethod.MARGIN and logits is not None:
            return self._margin_uncertainty(logits)
        
        elif self.method == UncertaintyMethod.LEAST_CONFIDENCE and logits is not None:
            return self._least_confidence_uncertainty(logits)
        
        elif self.method == UncertaintyMethod.VARIANCE and logits is not None:
            return self._variance_uncertainty(logits)
        
        elif self.method == UncertaintyMethod.DIVERSITY and embeddings is not None:
            return self._diversity_uncertainty(embeddings)
        
        else:
            # Fallback: random scoring
            logger.warning(f"Insufficient data for {self.method}, using random scores")
            return np.random.rand(len(candidates))
    
    def _entropy_uncertainty(self, logits: np.ndarray) -> np.ndarray:
        """Calculate entropy-based uncertainty from logits."""
        # Convert logits to probabilities
        probs = self._softmax(logits)
        
        # Calculate entropy: -sum(p * log(p))
        epsilon = 1e-10
        entropy = -np.sum(probs * np.log(probs + epsilon), axis=-1)
        
        # Normalize to [0, 1]
        max_entropy = np.log(probs.shape[-1])
        normalized_entropy = entropy / max_entropy
        
        return normalized_entropy
    
    def _margin_uncertainty(self, logits: np.ndarray) -> np.ndarray:
        """Calculate margin uncertainty (difference between top 2 predictions)."""
        probs = self._softmax(logits)
        
        # Sort probabilities descending
        sorted_probs = np.sort(probs, axis=-1)[:, ::-1]
        
        # Margin = difference between top 2
        margin = sorted_probs[:, 0] - sorted_probs[:, 1]
        
        # Invert: lower margin = higher uncertainty
        uncertainty = 1 - margin
        
        return uncertainty
    
    def _least_confidence_uncertainty(self, logits: np.ndarray) -> np.ndarray:
        """Calculate least confidence uncertainty."""
        probs = self._softmax(logits)
        
        # Max probability
        max_prob = np.max(probs, axis=-1)
        
        # Uncertainty = 1 - max_prob
        uncertainty = 1 - max_prob
        
        return uncertainty
    
    def _variance_uncertainty(self, logits: np.ndarray) -> np.ndarray:
        """Calculate variance-based uncertainty."""
        probs = self._softmax(logits)
        
        # Variance across classes
        variance = np.var(probs, axis=-1)
        
        # Normalize
        max_variance = 0.25  # Maximum variance for uniform distribution
        normalized_variance = np.clip(variance / max_variance, 0, 1)
        
        return normalized_variance
    
    def _diversity_uncertainty(self, embeddings: np.ndarray) -> np.ndarray:
        """Calculate diversity-based scores (distance from cluster centers)."""
        if len(embeddings) < 2:
            return np.ones(len(embeddings))
        
        # Cluster embeddings
        k = min(5, len(embeddings) // 2)
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(embeddings)
        
        # Distance to nearest cluster center
        distances = np.min(kmeans.transform(embeddings), axis=1)
        
        # Normalize
        max_dist = np.max(distances) if np.max(distances) > 0 else 1.0
        normalized_distances = distances / max_dist
        
        return normalized_distances
    
    def _diverse_sampling(
        self,
        uncertainty_scores: np.ndarray,
        embeddings: np.ndarray,
        k: int
    ) -> np.ndarray:
        """
        Sample k examples balancing uncertainty and diversity.
        
        Uses a greedy approach:
        1. Select highest uncertainty example
        2. Select next examples maximizing: uncertainty * diversity_from_selected
        """
        selected_indices = []
        remaining_indices = list(range(len(uncertainty_scores)))
        
        # Select first: highest uncertainty
        first_idx = int(np.argmax(uncertainty_scores))
        selected_indices.append(first_idx)
        remaining_indices.remove(first_idx)
        
        # Select remaining k-1 examples
        while len(selected_indices) < k and remaining_indices:
            scores = []
            
            for idx in remaining_indices:
                # Uncertainty component
                uncertainty = uncertainty_scores[idx]
                
                # Diversity component: distance to selected examples
                selected_embeddings = embeddings[selected_indices]
                current_embedding = embeddings[idx:idx+1]
                
                # Cosine distance
                distances = 1 - self._cosine_similarity(
                    current_embedding,
                    selected_embeddings
                )
                min_distance = np.min(distances)
                
                # Combined score: uncertainty * diversity
                score = uncertainty * min_distance
                scores.append(score)
            
            # Select highest combined score
            best_idx = remaining_indices[int(np.argmax(scores))]
            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)
        
        return np.array(selected_indices)
    
    def _softmax(self, logits: np.ndarray) -> np.ndarray:
        """Apply softmax to logits."""
        exp_logits = np.exp(logits - np.max(logits, axis=-1, keepdims=True))
        return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Calculate cosine similarity between vectors."""
        a_norm = a / (np.linalg.norm(a, axis=-1, keepdims=True) + 1e-10)
        b_norm = b / (np.linalg.norm(b, axis=-1, keepdims=True) + 1e-10)
        return np.dot(a_norm, b_norm.T)
    
    def get_task_distribution(
        self,
        uncertain_examples: List[UncertainExample]
    ) -> Dict[str, int]:
        """Get distribution of tasks in selected examples."""
        return Counter([ex.task_type for ex in uncertain_examples])
    
    def prioritize_by_task(
        self,
        uncertain_examples: List[UncertainExample],
        task_priorities: Dict[str, int]
    ) -> List[UncertainExample]:
        """
        Re-prioritize examples based on task importance.
        
        Args:
            uncertain_examples: List of uncertain examples
            task_priorities: Dict mapping task_type to priority (lower = more important)
            
        Returns:
            Re-prioritized list
        """
        for example in uncertain_examples:
            task_priority = task_priorities.get(example.task_type, 3)
            # Combine uncertainty priority with task priority
            example.priority = min(example.priority, task_priority)
        
        # Sort by priority then uncertainty
        return sorted(
            uncertain_examples,
            key=lambda x: (x.priority, -x.uncertainty_score)
        )


# Convenience function for API integration
def select_for_feedback(
    model_outputs: List[Dict[str, Any]],
    method: str = "entropy",
    batch_size: int = 10,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Select uncertain examples for human feedback.
    
    Args:
        model_outputs: List of model outputs with prompts and responses
        method: Uncertainty method to use
        batch_size: Number of examples to select
        **kwargs: Additional arguments for selector
        
    Returns:
        List of selected examples as dicts
    """
    selector = ActiveLearningSelector(
        method=UncertaintyMethod(method),
        batch_size=batch_size
    )
    
    uncertain = selector.select_uncertain_examples(
        model_outputs,
        logits=kwargs.get('logits'),
        embeddings=kwargs.get('embeddings')
    )
    
    return [
        {
            'example_id': ex.example_id,
            'prompt': ex.prompt,
            'output': ex.model_output,
            'uncertainty_score': ex.uncertainty_score,
            'priority': ex.priority,
            'task_type': ex.task_type
        }
        for ex in uncertain
    ]
