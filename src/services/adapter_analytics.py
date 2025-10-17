"""Adapter Analytics - Track per-adapter performance metrics."""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import json
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AdapterMetrics:
    """Performance metrics for a single adapter."""
    
    adapter_id: str
    adapter_type: str
    
    # Usage metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    # Performance metrics
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    
    # Quality metrics
    avg_user_rating: Optional[float] = None
    thumbs_up_count: int = 0
    thumbs_down_count: int = 0
    feedback_count: int = 0
    
    # Task-specific metrics
    task_accuracy: Dict[str, float] = field(default_factory=dict)
    task_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Composition metrics
    composition_count: int = 0
    avg_composition_time_ms: float = 0.0
    
    # Resource metrics
    memory_mb: Optional[float] = None
    model_size_mb: Optional[float] = None
    
    # Temporal
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    
    # Error tracking
    error_types: Dict[str, int] = field(default_factory=dict)
    
    def update_latency(self, latency_ms: float) -> None:
        """Update latency statistics."""
        # Simple moving average update
        n = self.successful_requests
        self.avg_latency_ms = ((self.avg_latency_ms * n) + latency_ms) / (n + 1)
    
    def add_feedback(self, rating: Optional[float] = None, thumbs: Optional[str] = None) -> None:
        """Add user feedback."""
        self.feedback_count += 1
        
        if rating is not None:
            if self.avg_user_rating is None:
                self.avg_user_rating = rating
            else:
                # Moving average
                self.avg_user_rating = (
                    (self.avg_user_rating * (self.feedback_count - 1)) + rating
                ) / self.feedback_count
        
        if thumbs == "up":
            self.thumbs_up_count += 1
        elif thumbs == "down":
            self.thumbs_down_count += 1
    
    def get_success_rate(self) -> float:
        """Calculate success rate."""
        total = self.total_requests
        return (self.successful_requests / total) if total > 0 else 0.0
    
    def get_thumbs_up_rate(self) -> float:
        """Calculate thumbs up rate."""
        total_thumbs = self.thumbs_up_count + self.thumbs_down_count
        return (self.thumbs_up_count / total_thumbs) if total_thumbs > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert datetime to ISO string
        data['first_seen'] = self.first_seen.isoformat()
        data['last_used'] = self.last_used.isoformat()
        return data


@dataclass
class CompositionMetrics:
    """Metrics for a specific adapter composition."""
    
    composition_id: str
    adapter_ids: List[str]
    composition_strategy: str
    
    # Performance
    total_requests: int = 0
    avg_latency_ms: float = 0.0
    composition_time_ms: float = 0.0
    
    # Quality
    avg_rating: Optional[float] = None
    feedback_count: int = 0
    
    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)


class AdapterAnalytics:
    """
    Track and analyze adapter performance metrics.
    
    Features:
    - Per-adapter metrics tracking
    - Composition analysis
    - Performance trends
    - Quality monitoring
    - Resource usage
    - Export capabilities
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize analytics tracker.
        
        Args:
            storage_path: Path to store metrics (optional)
        """
        self.adapter_metrics: Dict[str, AdapterMetrics] = {}
        self.composition_metrics: Dict[str, CompositionMetrics] = {}
        self.storage_path = storage_path
        
        # In-memory latency buffers for percentile calculation
        self.latency_buffers: Dict[str, List[float]] = defaultdict(list)
        self.max_buffer_size = 1000
        
        # Load existing metrics if storage path provided
        if storage_path and storage_path.exists():
            self._load_metrics()
        
        logger.info("Adapter Analytics initialized")
    
    def record_request(
        self,
        adapter_id: str,
        adapter_type: str,
        latency_ms: float,
        success: bool = True,
        task_type: Optional[str] = None,
        error_type: Optional[str] = None
    ) -> None:
        """
        Record a request for an adapter.
        
        Args:
            adapter_id: Adapter identifier
            adapter_type: Type of adapter (retailer, task, etc.)
            latency_ms: Request latency in milliseconds
            success: Whether request succeeded
            task_type: Optional task type
            error_type: Optional error type if failed
        """
        # Get or create metrics
        if adapter_id not in self.adapter_metrics:
            self.adapter_metrics[adapter_id] = AdapterMetrics(
                adapter_id=adapter_id,
                adapter_type=adapter_type
            )
        
        metrics = self.adapter_metrics[adapter_id]
        
        # Update counts
        metrics.total_requests += 1
        metrics.last_used = datetime.utcnow()
        
        if success:
            metrics.successful_requests += 1
            metrics.update_latency(latency_ms)
            
            # Update latency buffer for percentiles
            self.latency_buffers[adapter_id].append(latency_ms)
            if len(self.latency_buffers[adapter_id]) > self.max_buffer_size:
                self.latency_buffers[adapter_id].pop(0)
            
            # Update percentiles
            self._update_percentiles(adapter_id)
        else:
            metrics.failed_requests += 1
            if error_type:
                metrics.error_types[error_type] = metrics.error_types.get(error_type, 0) + 1
        
        # Update task distribution
        if task_type:
            metrics.task_distribution[task_type] = metrics.task_distribution.get(task_type, 0) + 1
    
    def record_composition(
        self,
        composition_id: str,
        adapter_ids: List[str],
        composition_strategy: str,
        composition_time_ms: float
    ) -> None:
        """Record an adapter composition."""
        if composition_id not in self.composition_metrics:
            self.composition_metrics[composition_id] = CompositionMetrics(
                composition_id=composition_id,
                adapter_ids=adapter_ids,
                composition_strategy=composition_strategy,
                composition_time_ms=composition_time_ms
            )
        
        # Update individual adapter composition counts
        for adapter_id in adapter_ids:
            if adapter_id in self.adapter_metrics:
                self.adapter_metrics[adapter_id].composition_count += 1
                
                # Update average composition time
                m = self.adapter_metrics[adapter_id]
                n = m.composition_count
                m.avg_composition_time_ms = (
                    (m.avg_composition_time_ms * (n - 1)) + composition_time_ms
                ) / n
    
    def record_feedback(
        self,
        adapter_id: str,
        rating: Optional[float] = None,
        thumbs: Optional[str] = None,
        task_type: Optional[str] = None,
        accuracy: Optional[float] = None
    ) -> None:
        """Record user feedback for an adapter."""
        if adapter_id not in self.adapter_metrics:
            logger.warning(f"Feedback for unknown adapter: {adapter_id}")
            return
        
        metrics = self.adapter_metrics[adapter_id]
        metrics.add_feedback(rating, thumbs)
        
        # Update task-specific accuracy
        if task_type and accuracy is not None:
            current = metrics.task_accuracy.get(task_type, accuracy)
            count = metrics.task_distribution.get(task_type, 1)
            metrics.task_accuracy[task_type] = (
                (current * (count - 1)) + accuracy
            ) / count
    
    def get_adapter_metrics(self, adapter_id: str) -> Optional[AdapterMetrics]:
        """Get metrics for a specific adapter."""
        return self.adapter_metrics.get(adapter_id)
    
    def get_top_adapters(
        self,
        metric: str = "success_rate",
        limit: int = 10
    ) -> List[AdapterMetrics]:
        """
        Get top performing adapters by specified metric.
        
        Args:
            metric: Metric to rank by (success_rate, avg_rating, total_requests)
            limit: Number of adapters to return
            
        Returns:
            List of top adapter metrics
        """
        adapters = list(self.adapter_metrics.values())
        
        if metric == "success_rate":
            adapters.sort(key=lambda x: x.get_success_rate(), reverse=True)
        elif metric == "avg_rating":
            adapters.sort(
                key=lambda x: x.avg_user_rating if x.avg_user_rating else 0,
                reverse=True
            )
        elif metric == "total_requests":
            adapters.sort(key=lambda x: x.total_requests, reverse=True)
        elif metric == "thumbs_up_rate":
            adapters.sort(key=lambda x: x.get_thumbs_up_rate(), reverse=True)
        else:
            logger.warning(f"Unknown metric: {metric}")
        
        return adapters[:limit]
    
    def get_adapter_comparison(
        self,
        adapter_ids: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compare multiple adapters across key metrics.
        
        Args:
            adapter_ids: List of adapter IDs to compare
            
        Returns:
            Dict mapping adapter_id to metrics dict
        """
        comparison = {}
        
        for adapter_id in adapter_ids:
            metrics = self.adapter_metrics.get(adapter_id)
            if metrics:
                comparison[adapter_id] = {
                    'success_rate': metrics.get_success_rate(),
                    'avg_latency_ms': metrics.avg_latency_ms,
                    'p95_latency_ms': metrics.p95_latency_ms,
                    'avg_rating': metrics.avg_user_rating,
                    'thumbs_up_rate': metrics.get_thumbs_up_rate(),
                    'total_requests': metrics.total_requests,
                    'composition_count': metrics.composition_count
                }
        
        return comparison
    
    def get_usage_trends(
        self,
        adapter_id: str,
        days: int = 7
    ) -> Dict[str, List[Any]]:
        """
        Get usage trends for an adapter over time.
        
        Note: This is a simplified version. In production, you'd
        store time-series data in a proper database.
        """
        metrics = self.adapter_metrics.get(adapter_id)
        if not metrics:
            return {}
        
        # Placeholder for time-series data
        # In production, query from time-series DB
        return {
            'dates': [],
            'requests': [],
            'success_rate': [],
            'avg_latency': []
        }
    
    def export_metrics(self, output_path: Path) -> None:
        """Export all metrics to JSON file."""
        data = {
            'adapter_metrics': {
                adapter_id: metrics.to_dict()
                for adapter_id, metrics in self.adapter_metrics.items()
            },
            'composition_metrics': {
                comp_id: asdict(comp)
                for comp_id, comp in self.composition_metrics.items()
            },
            'exported_at': datetime.utcnow().isoformat()
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Metrics exported to {output_path}")
    
    def _update_percentiles(self, adapter_id: str) -> None:
        """Update latency percentiles for an adapter."""
        buffer = self.latency_buffers.get(adapter_id, [])
        if not buffer:
            return
        
        metrics = self.adapter_metrics[adapter_id]
        sorted_buffer = sorted(buffer)
        
        metrics.p50_latency_ms = np.percentile(sorted_buffer, 50)
        metrics.p95_latency_ms = np.percentile(sorted_buffer, 95)
        metrics.p99_latency_ms = np.percentile(sorted_buffer, 99)
    
    def _load_metrics(self) -> None:
        """Load metrics from storage."""
        if not self.storage_path or not self.storage_path.exists():
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Load adapter metrics
            for adapter_id, metrics_dict in data.get('adapter_metrics', {}).items():
                # Convert datetime strings back
                metrics_dict['first_seen'] = datetime.fromisoformat(metrics_dict['first_seen'])
                metrics_dict['last_used'] = datetime.fromisoformat(metrics_dict['last_used'])
                
                self.adapter_metrics[adapter_id] = AdapterMetrics(**metrics_dict)
            
            logger.info(f"Loaded metrics for {len(self.adapter_metrics)} adapters")
        
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
    
    def save_metrics(self) -> None:
        """Save current metrics to storage."""
        if self.storage_path:
            self.export_metrics(self.storage_path)


# Global analytics instance
_analytics: Optional[AdapterAnalytics] = None


def get_analytics() -> AdapterAnalytics:
    """Get global analytics instance."""
    global _analytics
    if _analytics is None:
        _analytics = AdapterAnalytics()
    return _analytics


def record_adapter_request(
    adapter_id: str,
    adapter_type: str,
    latency_ms: float,
    success: bool = True,
    **kwargs
) -> None:
    """Record an adapter request (convenience function)."""
    analytics = get_analytics()
    analytics.record_request(adapter_id, adapter_type, latency_ms, success, **kwargs)
