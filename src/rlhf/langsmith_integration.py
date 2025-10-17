"""LangSmith integration for RLHF tracing and observability.

This module provides comprehensive tracing of RLHF workflows, enabling
visual debugging, performance analysis, and quality monitoring.
"""

import logging
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)


class LangSmithTracer:
    """LangSmith tracing for RLHF workflows."""
    
    def __init__(
        self,
        project_name: str = "rmn-rlhf",
        api_key: Optional[str] = None
    ):
        """Initialize LangSmith tracer.
        
        Args:
            project_name: LangSmith project name
            api_key: LangSmith API key (or use LANGCHAIN_API_KEY env var)
        """
        self.project_name = project_name
        self.enabled = False
        self.client = None
        
        try:
            from langsmith import Client
            import os
            
            # Use provided key or env var
            api_key = api_key or os.getenv("LANGCHAIN_API_KEY")
            
            if api_key:
                self.client = Client(api_key=api_key)
                self.enabled = True
                logger.info(f"LangSmith tracing enabled for project: {project_name}")
            else:
                logger.warning("LangSmith API key not found. Tracing disabled.")
                
        except ImportError:
            logger.warning("LangSmith not installed. Run: pip install langsmith")
    
    @contextmanager
    def trace_feedback_collection(
        self,
        user_id: str,
        task_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Trace a feedback collection session.
        
        Args:
            user_id: User providing feedback
            task_type: Type of task
            metadata: Additional metadata
            
        Yields:
            Tracer context
        """
        if not self.enabled:
            yield None
            return
        
        try:
            with self.client.tracing_context(
                project_name=self.project_name,
                tags=["feedback-collection", task_type],
                metadata={
                    "user_id": user_id,
                    "task_type": task_type,
                    "timestamp": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            ):
                yield self.client
                
        except Exception as e:
            logger.error(f"LangSmith tracing error: {e}")
            yield None
    
    @contextmanager
    def trace_synthetic_generation(
        self,
        generator_type: str,
        num_examples: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Trace synthetic feedback generation.
        
        Args:
            generator_type: Type of generator (CrewAI, etc.)
            num_examples: Number of examples to generate
            metadata: Additional metadata
            
        Yields:
            Tracer context
        """
        if not self.enabled:
            yield None
            return
        
        try:
            with self.client.tracing_context(
                project_name=self.project_name,
                tags=["synthetic-feedback", generator_type],
                metadata={
                    "generator": generator_type,
                    "num_examples": num_examples,
                    "timestamp": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            ):
                yield self.client
                
        except Exception as e:
            logger.error(f"LangSmith tracing error: {e}")
            yield None
    
    @contextmanager
    def trace_training(
        self,
        training_method: str,
        adapter_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Trace a training run.
        
        Args:
            training_method: SFT, DPO, PPO, etc.
            adapter_name: Name of adapter being trained
            metadata: Additional metadata
            
        Yields:
            Tracer context
        """
        if not self.enabled:
            yield None
            return
        
        try:
            with self.client.tracing_context(
                project_name=self.project_name,
                tags=["training", training_method, adapter_name],
                metadata={
                    "method": training_method,
                    "adapter": adapter_name,
                    "timestamp": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
            ):
                yield self.client
                
        except Exception as e:
            logger.error(f"LangSmith tracing error: {e}")
            yield None
    
    def log_feedback(
        self,
        run_id: str,
        feedback_type: str,
        score: float,
        comment: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log feedback for a traced run.
        
        Args:
            run_id: Run ID from LangSmith
            feedback_type: Type of feedback (rating, preference, etc.)
            score: Numeric score
            comment: Optional comment
            metadata: Additional metadata
        """
        if not self.enabled:
            return
        
        try:
            self.client.create_feedback(
                run_id=run_id,
                key=feedback_type,
                score=score,
                comment=comment,
                **(metadata or {})
            )
            logger.debug(f"Logged feedback for run {run_id}")
            
        except Exception as e:
            logger.error(f"Failed to log feedback: {e}")
    
    def log_evaluation_metrics(
        self,
        run_id: str,
        metrics: Dict[str, float]
    ):
        """Log evaluation metrics for a run.
        
        Args:
            run_id: Run ID from LangSmith
            metrics: Dictionary of metric_name -> value
        """
        if not self.enabled:
            return
        
        try:
            for metric_name, value in metrics.items():
                self.client.create_feedback(
                    run_id=run_id,
                    key=f"metric_{metric_name}",
                    score=value
                )
            logger.debug(f"Logged {len(metrics)} metrics for run {run_id}")
            
        except Exception as e:
            logger.error(f"Failed to log metrics: {e}")
    
    def get_project_stats(self) -> Optional[Dict[str, Any]]:
        """Get statistics for the RLHF project.
        
        Returns:
            Dictionary with project statistics or None if disabled
        """
        if not self.enabled:
            return None
        
        try:
            # Get runs from last 30 days
            from datetime import timedelta
            
            runs = self.client.list_runs(
                project_name=self.project_name,
                start_time=datetime.utcnow() - timedelta(days=30)
            )
            
            run_list = list(runs)
            
            # Calculate stats
            total_runs = len(run_list)
            
            # Count by tag
            tag_counts = {}
            for run in run_list:
                for tag in run.tags or []:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            return {
                "total_runs": total_runs,
                "tag_distribution": tag_counts,
                "project_name": self.project_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get project stats: {e}")
            return None


class RLHFMonitor:
    """Monitor RLHF performance over time."""
    
    def __init__(self, tracer: LangSmithTracer):
        """Initialize RLHF monitor.
        
        Args:
            tracer: LangSmith tracer
        """
        self.tracer = tracer
    
    def track_feedback_quality(
        self,
        feedback_batch: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Track quality metrics for a batch of feedback.
        
        Args:
            feedback_batch: List of feedback dictionaries
            
        Returns:
            Quality metrics
        """
        if not feedback_batch:
            return {}
        
        # Calculate metrics
        total = len(feedback_batch)
        
        # Rating distribution
        ratings = [f.get("rating", 0) for f in feedback_batch]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Feedback types
        type_counts = {}
        for f in feedback_batch:
            ftype = f.get("feedback_type", "unknown")
            type_counts[ftype] = type_counts.get(ftype, 0) + 1
        
        # Task types
        task_counts = {}
        for f in feedback_batch:
            task = f.get("task_type", "unknown")
            task_counts[task] = task_counts.get(task, 0) + 1
        
        metrics = {
            "total_feedback": total,
            "average_rating": avg_rating,
            "rating_distribution": {
                "1_star": ratings.count(1),
                "2_star": ratings.count(2),
                "3_star": ratings.count(3),
                "4_star": ratings.count(4),
                "5_star": ratings.count(5)
            },
            "feedback_types": type_counts,
            "task_types": task_counts
        }
        
        logger.info(f"Quality metrics: avg_rating={avg_rating:.2f}, total={total}")
        
        return metrics
    
    def compare_model_versions(
        self,
        version_a: str,
        version_b: str,
        feedback_a: List[Dict[str, Any]],
        feedback_b: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare two model versions based on feedback.
        
        Args:
            version_a: Name of version A
            version_b: Name of version B
            feedback_a: Feedback for version A
            feedback_b: Feedback for version B
            
        Returns:
            Comparison results
        """
        metrics_a = self.track_feedback_quality(feedback_a)
        metrics_b = self.track_feedback_quality(feedback_b)
        
        # Calculate deltas
        avg_a = metrics_a.get("average_rating", 0)
        avg_b = metrics_b.get("average_rating", 0)
        delta = avg_b - avg_a
        
        # Determine winner
        if abs(delta) < 0.1:
            winner = "tie"
        elif delta > 0:
            winner = version_b
        else:
            winner = version_a
        
        comparison = {
            "version_a": {
                "name": version_a,
                "metrics": metrics_a
            },
            "version_b": {
                "name": version_b,
                "metrics": metrics_b
            },
            "rating_delta": delta,
            "winner": winner,
            "confidence": abs(delta) / 5.0  # Normalized confidence
        }
        
        logger.info(f"Model comparison: {winner} wins with delta={delta:.2f}")
        
        return comparison


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize tracer
    tracer = LangSmithTracer(project_name="rmn-rlhf-demo")
    
    if tracer.enabled:
        print("✅ LangSmith enabled!")
        
        # Example: Trace feedback collection
        with tracer.trace_feedback_collection(
            user_id="user123",
            task_type="budgeting",
            metadata={"brand": "Acme Foods"}
        ):
            print("Collecting feedback (traced)...")
            # Feedback collection code here
        
        # Example: Get project stats
        stats = tracer.get_project_stats()
        if stats:
            print(f"\nProject Stats:")
            print(f"  Total runs: {stats['total_runs']}")
            print(f"  Tags: {stats['tag_distribution']}")
    else:
        print("⚠️  LangSmith not enabled. Set LANGCHAIN_API_KEY to enable.")
