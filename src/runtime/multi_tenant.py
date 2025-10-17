"""Multi-tenant runtime for serving LoRA adapters."""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from pathlib import Path
import uuid

from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uvicorn

from .adapter_manager import AdapterManager
from src.services import (
    get_analytics,
    get_ab_framework,
    get_compositor,
)

logger = logging.getLogger(__name__)


# Request/Response models
class InferenceRequest(BaseModel):
    """Request for inference."""
    messages: List[Dict[str, str]]
    retailer_id: Optional[str] = None
    brand_id: Optional[str] = None
    task: Optional[str] = None
    max_tokens: int = 1024
    temperature: float = 0.7


class InferenceResponse(BaseModel):
    """Response from inference."""
    request_id: str
    response: str
    adapters_used: List[str]
    metadata: Dict[str, Any]


@dataclass
class TenantConfig:
    """Configuration for a tenant."""
    tenant_id: str
    allowed_adapters: List[str]
    rate_limit: int  # requests per minute
    max_tokens: int
    enabled: bool = True


class MultiTenantRuntime:
    """Multi-tenant runtime for serving LoRA adapters."""
    
    def __init__(
        self,
        base_model_path: str,
        adapters_dir: Path,
        device: str = "auto",
        enable_analytics: bool = True,
        enable_ab_testing: bool = True,
        enable_realtime_composition: bool = True
    ):
        """Initialize multi-tenant runtime.
        
        Args:
            base_model_path: Path to base model
            adapters_dir: Directory containing adapters
            device: Device to run on
            enable_analytics: Enable analytics tracking
            enable_ab_testing: Enable A/B testing
            enable_realtime_composition: Enable real-time composition
        """
        self.adapter_manager = AdapterManager(
            base_model_path,
            adapters_dir,
            device
        )
        
        # Tenant registry
        self.tenants: Dict[str, TenantConfig] = {}
        
        # Request tracking
        self.request_counts: Dict[str, int] = {}
        
        # Enhanced services
        self.analytics = get_analytics() if enable_analytics else None
        self.ab_framework = get_ab_framework() if enable_ab_testing else None
        self.compositor = get_compositor(self.adapter_manager) if enable_realtime_composition else None
        
        logger.info(f"Multi-tenant runtime initialized (analytics={enable_analytics}, "
                   f"ab_testing={enable_ab_testing}, realtime_composition={enable_realtime_composition})")
    
    def register_tenant(
        self,
        tenant_id: str,
        allowed_adapters: List[str],
        rate_limit: int = 100,
        max_tokens: int = 2048
    ) -> None:
        """Register a new tenant.
        
        Args:
            tenant_id: Tenant identifier
            allowed_adapters: List of adapter IDs tenant can use
            rate_limit: Requests per minute
            max_tokens: Maximum tokens per request
        """
        config = TenantConfig(
            tenant_id=tenant_id,
            allowed_adapters=allowed_adapters,
            rate_limit=rate_limit,
            max_tokens=max_tokens
        )
        
        self.tenants[tenant_id] = config
        logger.info(f"Registered tenant: {tenant_id}")
    
    def check_tenant_access(
        self,
        tenant_id: str,
        adapter_ids: List[str]
    ) -> bool:
        """Check if tenant has access to adapters.
        
        Args:
            tenant_id: Tenant identifier
            adapter_ids: Adapter IDs to check
            
        Returns:
            Whether tenant has access
        """
        if tenant_id not in self.tenants:
            return False
        
        tenant = self.tenants[tenant_id]
        
        if not tenant.enabled:
            return False
        
        # Check if all requested adapters are allowed
        for adapter_id in adapter_ids:
            if adapter_id not in tenant.allowed_adapters:
                return False
        
        return True
    
    def check_rate_limit(self, tenant_id: str) -> bool:
        """Check if tenant is within rate limit.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            Whether request is allowed
        """
        # Simplified rate limiting - would need proper implementation
        # with time windows and distributed state
        
        if tenant_id not in self.tenants:
            return False
        
        tenant = self.tenants[tenant_id]
        current_count = self.request_counts.get(tenant_id, 0)
        
        if current_count >= tenant.rate_limit:
            return False
        
        self.request_counts[tenant_id] = current_count + 1
        return True
    
    async def inference(
        self,
        request: InferenceRequest,
        tenant_id: str,
        user_id: Optional[str] = None
    ) -> InferenceResponse:
        """Run inference with tenant isolation.
        
        Args:
            request: Inference request
            tenant_id: Tenant identifier
            user_id: Optional user ID for A/B testing
            
        Returns:
            Inference response
        """
        request_id = str(uuid.uuid4())
        start_time = time.time()
        success = False
        
        try:
            logger.info(f"Processing request {request_id} for tenant {tenant_id}")
            
            # Check rate limit
            if not self.check_rate_limit(tenant_id):
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Select adapters
            adapter_ids = self.adapter_manager.select_adapters_for_request(
                retailer_id=request.retailer_id,
                brand_id=request.brand_id,
                task=request.task
            )
            
            # Check tenant access
            if not self.check_tenant_access(tenant_id, adapter_ids):
                raise HTTPException(status_code=403, detail="Access denied to requested adapters")
            
            # A/B Testing: Check for active experiments
            variant_used = None
            if self.ab_framework and user_id:
                active_experiments = self.ab_framework.get_active_experiments()
                for exp in active_experiments:
                    variant_id = self.ab_framework.assign_variant(
                        experiment_id=exp.experiment_id,
                        user_id=user_id,
                        context={
                            'task': request.task,
                            'retailer': request.retailer_id
                        }
                    )
                    if variant_id:
                        variant_used = (exp.experiment_id, variant_id)
                        # Use variant's adapter IDs if specified
                        variant = exp.variants.get(variant_id)
                        if variant and variant.adapter_ids:
                            adapter_ids = variant.adapter_ids
                        break
            
            # Load model with adapters (using compositor if available)
            if adapter_ids:
                if self.compositor:
                    # Use real-time composition with caching
                    model = self.compositor.compose_sync(adapter_ids)
                else:
                    # Fallback to standard composition
                    model = self.adapter_manager.compose_adapters(adapter_ids)
            else:
                self.adapter_manager.load_base_model()
                model = self.adapter_manager.base_model
            
            # Generate response
            tokenizer = self.adapter_manager.tokenizer
            
            # Format messages
            if hasattr(tokenizer, "apply_chat_template"):
                prompt = tokenizer.apply_chat_template(
                    request.messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
            else:
                prompt = "\n\n".join([f"{m['role']}: {m['content']}" for m in request.messages])
                prompt += "\n\nassistant:"
            
            # Tokenize
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            
            # Generate
            import torch
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=min(request.max_tokens, self.tenants[tenant_id].max_tokens),
                    temperature=request.temperature,
                    do_sample=request.temperature > 0,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode
            response_text = tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )
            
            success = True
            latency_ms = (time.time() - start_time) * 1000
            
            # Record analytics
            if self.analytics:
                for adapter_id in adapter_ids:
                    adapter_type = self.adapter_manager.adapter_registry.get(adapter_id)
                    adapter_type_str = adapter_type.adapter_type if adapter_type else "unknown"
                    
                    self.analytics.record_request(
                        adapter_id=adapter_id,
                        adapter_type=adapter_type_str,
                        latency_ms=latency_ms / len(adapter_ids),  # Distribute latency
                        success=True,
                        task_type=request.task
                    )
            
            # Record A/B testing impression
            if self.ab_framework and variant_used:
                exp_id, variant_id = variant_used
                self.ab_framework.record_impression(
                    experiment_id=exp_id,
                    variant_id=variant_id,
                    success=True,
                    latency_ms=latency_ms
                )
            
            return InferenceResponse(
                request_id=request_id,
                response=response_text.strip(),
                adapters_used=adapter_ids,
                metadata={
                    "tenant_id": tenant_id,
                    "retailer_id": request.retailer_id,
                    "brand_id": request.brand_id,
                    "task": request.task,
                    "latency_ms": latency_ms,
                    "variant": variant_used[1] if variant_used else None
                }
            )
        
        except Exception as e:
            # Record failure in analytics
            latency_ms = (time.time() - start_time) * 1000
            if self.analytics:
                for adapter_id in adapter_ids if 'adapter_ids' in locals() else []:
                    self.analytics.record_request(
                        adapter_id=adapter_id,
                        adapter_type="unknown",
                        latency_ms=latency_ms,
                        success=False,
                        error_type=type(e).__name__
                    )
            
            raise


# FastAPI application
def create_app(
    base_model_path: str,
    adapters_dir: Path,
    device: str = "auto",
    enable_enhanced_features: bool = True
) -> FastAPI:
    """Create FastAPI application for multi-tenant runtime.
    
    Args:
        base_model_path: Path to base model
        adapters_dir: Directory containing adapters
        device: Device to run on
        enable_enhanced_features: Enable enhanced API endpoints
        
    Returns:
        FastAPI application
    """
    app = FastAPI(title="RMN LoRA Multi-Tenant Runtime")
    
    # Initialize runtime with enhanced features
    runtime = MultiTenantRuntime(
        base_model_path,
        adapters_dir,
        device,
        enable_analytics=enable_enhanced_features,
        enable_ab_testing=enable_enhanced_features,
        enable_realtime_composition=enable_enhanced_features
    )
    
    # Include enhanced API endpoints
    if enable_enhanced_features:
        try:
            from .enhanced_api import create_enhanced_api_router
            enhanced_router = create_enhanced_api_router()
            app.include_router(enhanced_router)
            logger.info("Enhanced API endpoints enabled")
        except ImportError:
            logger.warning("Enhanced API not available")
    
    @app.post("/inference", response_model=InferenceResponse)
    async def inference_endpoint(
        request: InferenceRequest,
        x_tenant_id: str = Header(..., alias="X-Tenant-ID")
    ):
        """Inference endpoint."""
        try:
            return await runtime.inference(request, x_tenant_id)
        except Exception as e:
            logger.error(f"Inference error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    @app.get("/adapters")
    async def list_adapters(
        x_tenant_id: str = Header(..., alias="X-Tenant-ID")
    ):
        """List available adapters for tenant."""
        if x_tenant_id not in runtime.tenants:
            raise HTTPException(status_code=403, detail="Unknown tenant")
        
        tenant = runtime.tenants[x_tenant_id]
        allowed_adapters = [
            {
                "adapter_id": adapter_id,
                "metadata": runtime.adapter_manager.adapter_registry.get(adapter_id)
            }
            for adapter_id in tenant.allowed_adapters
            if adapter_id in runtime.adapter_manager.adapter_registry
        ]
        
        return {"adapters": allowed_adapters}
    
    # Store runtime on app for access in startup
    app.state.runtime = runtime
    
    return app


def main():
    """CLI entry point for multi-tenant runtime."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Tenant Runtime Server")
    parser.add_argument("--base-model", required=True, help="Base model path")
    parser.add_argument("--adapters-dir", type=Path, required=True, help="Adapters directory")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--device", default="auto", help="Device (auto, cuda, cpu)")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create app
    app = create_app(args.base_model, args.adapters_dir, args.device)
    
    # Register example tenant (in production, would be from config/database)
    runtime = app.state.runtime
    runtime.register_tenant(
        "tenant_example",
        allowed_adapters=["retailer_ABC", "brand_XYZ", "task_budgeting"],
        rate_limit=100,
        max_tokens=2048
    )
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    
    # Run server
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
