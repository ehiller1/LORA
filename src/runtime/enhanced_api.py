"""Enhanced API endpoints for new services."""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from src.services import (
    get_analytics,
    get_ab_framework,
    get_compositor,
    ActiveLearningSelector,
    UncertaintyMethod
)

logger = logging.getLogger(__name__)


# ============================================================================
# Request/Response Models
# ============================================================================

class SelectUncertainRequest(BaseModel):
    """Request for selecting uncertain examples."""
    candidates: List[Dict[str, Any]]
    method: str = "entropy"
    batch_size: int = 10
    logits: Optional[List[List[float]]] = None
    embeddings: Optional[List[List[float]]] = None


class UncertainExampleResponse(BaseModel):
    """Uncertain example response."""
    example_id: str
    prompt: str
    model_output: str
    uncertainty_score: float
    priority: int
    task_type: str


class AdapterMetricsResponse(BaseModel):
    """Adapter metrics response."""
    adapter_id: str
    adapter_type: str
    total_requests: int
    success_rate: float
    avg_latency_ms: float
    p95_latency_ms: float
    avg_user_rating: Optional[float]
    thumbs_up_rate: float


class CreateExperimentRequest(BaseModel):
    """Request to create A/B experiment."""
    experiment_id: str
    name: str
    description: str
    variants: List[Dict[str, Any]]
    confidence_level: float = 0.95
    min_sample_size: int = 100


class AssignVariantRequest(BaseModel):
    """Request to assign variant."""
    experiment_id: str
    user_id: str
    context: Optional[Dict[str, Any]] = None


class RecordImpressionRequest(BaseModel):
    """Request to record experiment impression."""
    experiment_id: str
    variant_id: str
    success: bool
    latency_ms: float
    feedback_score: Optional[float] = None


class HotSwapRequest(BaseModel):
    """Request to hot-swap adapter."""
    old_adapter_id: str
    new_adapter_id: str
    warm_swap: bool = True


# ============================================================================
# Active Learning Endpoints
# ============================================================================

active_learning_router = APIRouter(prefix="/active-learning", tags=["active-learning"])


@active_learning_router.post("/select", response_model=List[UncertainExampleResponse])
async def select_uncertain_examples(request: SelectUncertainRequest):
    """
    Select uncertain examples for human feedback.
    
    Uses active learning to identify examples where the model is most uncertain.
    """
    try:
        import numpy as np
        
        selector = ActiveLearningSelector(
            method=UncertaintyMethod(request.method),
            batch_size=request.batch_size
        )
        
        # Convert logits and embeddings if provided
        logits = np.array(request.logits) if request.logits else None
        embeddings = np.array(request.embeddings) if request.embeddings else None
        
        uncertain = selector.select_uncertain_examples(
            candidates=request.candidates,
            logits=logits,
            embeddings=embeddings
        )
        
        return [
            UncertainExampleResponse(
                example_id=ex.example_id,
                prompt=ex.prompt,
                model_output=ex.model_output,
                uncertainty_score=ex.uncertainty_score,
                priority=ex.priority,
                task_type=ex.task_type
            )
            for ex in uncertain
        ]
    
    except Exception as e:
        logger.error(f"Error selecting uncertain examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Adapter Analytics Endpoints
# ============================================================================

analytics_router = APIRouter(prefix="/analytics", tags=["analytics"])


@analytics_router.get("/adapters/{adapter_id}", response_model=AdapterMetricsResponse)
async def get_adapter_metrics(adapter_id: str):
    """Get metrics for a specific adapter."""
    analytics = get_analytics()
    metrics = analytics.get_adapter_metrics(adapter_id)
    
    if not metrics:
        raise HTTPException(status_code=404, detail=f"Adapter not found: {adapter_id}")
    
    return AdapterMetricsResponse(
        adapter_id=metrics.adapter_id,
        adapter_type=metrics.adapter_type,
        total_requests=metrics.total_requests,
        success_rate=metrics.get_success_rate(),
        avg_latency_ms=metrics.avg_latency_ms,
        p95_latency_ms=metrics.p95_latency_ms,
        avg_user_rating=metrics.avg_user_rating,
        thumbs_up_rate=metrics.get_thumbs_up_rate()
    )


@analytics_router.get("/top-performers")
async def get_top_performers(
    metric: str = Query("success_rate", description="Metric to rank by"),
    limit: int = Query(10, ge=1, le=50)
):
    """Get top performing adapters."""
    analytics = get_analytics()
    top = analytics.get_top_adapters(metric=metric, limit=limit)
    
    return [
        {
            "adapter_id": metrics.adapter_id,
            "adapter_type": metrics.adapter_type,
            "success_rate": metrics.get_success_rate(),
            "avg_latency_ms": metrics.avg_latency_ms,
            "total_requests": metrics.total_requests,
            "avg_rating": metrics.avg_user_rating
        }
        for metrics in top
    ]


@analytics_router.get("/comparison")
async def compare_adapters(adapter_ids: List[str] = Query(...)):
    """Compare multiple adapters."""
    analytics = get_analytics()
    comparison = analytics.get_adapter_comparison(adapter_ids)
    return comparison


@analytics_router.post("/record")
async def record_request(
    adapter_id: str,
    adapter_type: str,
    latency_ms: float,
    success: bool = True,
    task_type: Optional[str] = None
):
    """Record a request for analytics."""
    analytics = get_analytics()
    analytics.record_request(
        adapter_id=adapter_id,
        adapter_type=adapter_type,
        latency_ms=latency_ms,
        success=success,
        task_type=task_type
    )
    return {"status": "recorded"}


# ============================================================================
# A/B Testing Endpoints
# ============================================================================

ab_testing_router = APIRouter(prefix="/ab-testing", tags=["ab-testing"])


@ab_testing_router.post("/experiments")
async def create_experiment(request: CreateExperimentRequest):
    """Create a new A/B test experiment."""
    framework = get_ab_framework()
    
    try:
        experiment = framework.create_experiment(
            experiment_id=request.experiment_id,
            name=request.name,
            description=request.description,
            variant_configs=request.variants,
            confidence_level=request.confidence_level,
            min_sample_size=request.min_sample_size
        )
        
        return {
            "experiment_id": experiment.experiment_id,
            "name": experiment.name,
            "status": experiment.status.value,
            "variants": list(experiment.variants.keys())
        }
    
    except Exception as e:
        logger.error(f"Error creating experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ab_testing_router.post("/experiments/{experiment_id}/start")
async def start_experiment(experiment_id: str):
    """Start an experiment."""
    framework = get_ab_framework()
    
    try:
        framework.start_experiment(experiment_id)
        return {"status": "started", "experiment_id": experiment_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@ab_testing_router.post("/experiments/{experiment_id}/stop")
async def stop_experiment(experiment_id: str):
    """Stop an experiment."""
    framework = get_ab_framework()
    
    try:
        framework.stop_experiment(experiment_id)
        return {"status": "stopped", "experiment_id": experiment_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@ab_testing_router.post("/assign", response_model=Dict[str, str])
async def assign_variant(request: AssignVariantRequest):
    """Assign a user to a variant."""
    framework = get_ab_framework()
    
    variant_id = framework.assign_variant(
        experiment_id=request.experiment_id,
        user_id=request.user_id,
        context=request.context
    )
    
    if not variant_id:
        raise HTTPException(
            status_code=404,
            detail=f"Experiment not active: {request.experiment_id}"
        )
    
    return {
        "experiment_id": request.experiment_id,
        "user_id": request.user_id,
        "variant_id": variant_id
    }


@ab_testing_router.post("/impressions")
async def record_impression(request: RecordImpressionRequest):
    """Record an experiment impression."""
    framework = get_ab_framework()
    
    framework.record_impression(
        experiment_id=request.experiment_id,
        variant_id=request.variant_id,
        success=request.success,
        latency_ms=request.latency_ms,
        feedback_score=request.feedback_score
    )
    
    return {"status": "recorded"}


@ab_testing_router.get("/experiments/{experiment_id}/results")
async def get_experiment_results(experiment_id: str):
    """Get experiment results with statistical analysis."""
    framework = get_ab_framework()
    
    try:
        results = framework.get_experiment_results(experiment_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@ab_testing_router.get("/experiments")
async def list_experiments():
    """List all experiments."""
    framework = get_ab_framework()
    active = framework.get_active_experiments()
    
    return {
        "active_experiments": [
            {
                "experiment_id": exp.experiment_id,
                "name": exp.name,
                "status": exp.status.value,
                "variants": list(exp.variants.keys())
            }
            for exp in active
        ]
    }


# ============================================================================
# Real-time Composition Endpoints
# ============================================================================

composition_router = APIRouter(prefix="/composition", tags=["composition"])


@composition_router.post("/swap")
async def hot_swap_adapter(request: HotSwapRequest, adapter_manager=Depends()):
    """Hot-swap an adapter without restart."""
    try:
        # Get or initialize compositor
        compositor = get_compositor(adapter_manager)
        
        compositor.swap_adapter(
            old_adapter_id=request.old_adapter_id,
            new_adapter_id=request.new_adapter_id,
            warm_swap=request.warm_swap
        )
        
        return {
            "status": "swapped",
            "old_adapter": request.old_adapter_id,
            "new_adapter": request.new_adapter_id,
            "method": "warm" if request.warm_swap else "cold"
        }
    
    except Exception as e:
        logger.error(f"Error swapping adapter: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@composition_router.get("/stats")
async def get_composition_stats():
    """Get composition cache statistics."""
    try:
        compositor = get_compositor()
        stats = compositor.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@composition_router.post("/prefetch")
async def prefetch_composition(
    adapter_ids: List[str],
    composition_strategy: str = "sequential"
):
    """Prefetch and cache a composition."""
    try:
        compositor = get_compositor()
        compositor.prefetch(adapter_ids, composition_strategy)
        
        return {
            "status": "prefetched",
            "adapter_ids": adapter_ids,
            "strategy": composition_strategy
        }
    except Exception as e:
        logger.error(f"Error prefetching: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Combined Router
# ============================================================================

def create_enhanced_api_router() -> APIRouter:
    """Create combined router with all enhanced endpoints."""
    router = APIRouter()
    
    router.include_router(active_learning_router)
    router.include_router(analytics_router)
    router.include_router(ab_testing_router)
    router.include_router(composition_router)
    
    return router
