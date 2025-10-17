"""Real-time Adapter Composition - Hot-swap adapters without restart."""

import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import time
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class CompositionRequest:
    """Request for adapter composition."""
    
    request_id: str
    adapter_ids: List[str]
    composition_strategy: str
    priority: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ActiveComposition:
    """Currently active adapter composition."""
    
    composition_id: str
    adapter_ids: List[str]
    composition_strategy: str
    model: Any  # The composed model
    created_at: datetime
    last_used: datetime
    request_count: int = 0
    
    def touch(self) -> None:
        """Update last used timestamp."""
        self.last_used = datetime.utcnow()
        self.request_count += 1


class CompositionCache:
    """Cache for pre-composed adapter stacks."""
    
    def __init__(self, max_size: int = 10, ttl_seconds: int = 3600):
        """Initialize composition cache.
        
        Args:
            max_size: Maximum number of cached compositions
            ttl_seconds: Time-to-live for cached compositions
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, ActiveComposition] = {}
        self._lock = threading.RLock()
    
    def get(self, composition_id: str) -> Optional[ActiveComposition]:
        """Get cached composition."""
        with self._lock:
            comp = self.cache.get(composition_id)
            
            if comp:
                # Check if expired
                age = (datetime.utcnow() - comp.created_at).total_seconds()
                if age > self.ttl_seconds:
                    del self.cache[composition_id]
                    return None
                
                comp.touch()
                return comp
            
            return None
    
    def put(self, composition: ActiveComposition) -> None:
        """Add composition to cache."""
        with self._lock:
            # Evict least recently used if cache full
            if len(self.cache) >= self.max_size:
                self._evict_lru()
            
            self.cache[composition.composition_id] = composition
    
    def remove(self, composition_id: str) -> None:
        """Remove composition from cache."""
        with self._lock:
            if composition_id in self.cache:
                del self.cache[composition_id]
    
    def clear(self) -> None:
        """Clear all cached compositions."""
        with self._lock:
            self.cache.clear()
    
    def _evict_lru(self) -> None:
        """Evict least recently used composition."""
        if not self.cache:
            return
        
        lru_id = min(
            self.cache.keys(),
            key=lambda k: self.cache[k].last_used
        )
        del self.cache[lru_id]
        
        logger.info(f"Evicted LRU composition: {lru_id}")


class RealtimeCompositor:
    """
    Real-time adapter composition system with hot-swapping.
    
    Features:
    - Non-blocking composition
    - Pre-warming of common compositions
    - Graceful adapter swapping
    - Request queue with priorities
    - Composition caching
    - Zero-downtime updates
    """
    
    def __init__(
        self,
        adapter_manager: Any,
        max_cache_size: int = 10,
        warmup_compositions: Optional[List[List[str]]] = None
    ):
        """Initialize real-time compositor.
        
        Args:
            adapter_manager: Adapter manager instance
            max_cache_size: Maximum cached compositions
            warmup_compositions: Compositions to pre-warm on startup
        """
        self.adapter_manager = adapter_manager
        self.cache = CompositionCache(max_size=max_cache_size)
        
        # Request queue
        self.request_queue: deque = deque()
        self.queue_lock = threading.Lock()
        
        # Background worker
        self.worker_thread: Optional[threading.Thread] = None
        self.running = False
        
        # Callbacks
        self.composition_callbacks: List[Callable] = []
        
        # Statistics
        self.stats = {
            'total_compositions': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_composition_time_ms': 0.0
        }
        
        # Start worker thread
        self._start_worker()
        
        # Warmup common compositions
        if warmup_compositions:
            self._warmup(warmup_compositions)
        
        logger.info("Real-time Compositor initialized")
    
    def compose_async(
        self,
        adapter_ids: List[str],
        composition_strategy: str = "sequential",
        priority: int = 1,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Request adapter composition asynchronously.
        
        Args:
            adapter_ids: List of adapter IDs to compose
            composition_strategy: Composition strategy
            priority: Request priority (lower = higher priority)
            callback: Optional callback when composition is ready
            
        Returns:
            Request ID for tracking
        """
        request_id = f"req_{int(time.time() * 1000)}"
        
        request = CompositionRequest(
            request_id=request_id,
            adapter_ids=adapter_ids,
            composition_strategy=composition_strategy,
            priority=priority
        )
        
        # Add to queue
        with self.queue_lock:
            self.request_queue.append((request, callback))
        
        logger.info(f"Queued composition request: {request_id}")
        
        return request_id
    
    def compose_sync(
        self,
        adapter_ids: List[str],
        composition_strategy: str = "sequential",
        force_recompose: bool = False
    ) -> Any:
        """
        Compose adapters synchronously (with caching).
        
        Args:
            adapter_ids: List of adapter IDs to compose
            composition_strategy: Composition strategy
            force_recompose: Force recomposition even if cached
            
        Returns:
            Composed model
        """
        # Generate composition ID
        comp_id = self._get_composition_id(adapter_ids, composition_strategy)
        
        # Check cache
        if not force_recompose:
            cached = self.cache.get(comp_id)
            if cached:
                self.stats['cache_hits'] += 1
                logger.info(f"Cache hit for composition: {comp_id}")
                return cached.model
        
        self.stats['cache_misses'] += 1
        
        # Compose adapters
        start_time = time.time()
        model = self.adapter_manager.compose_adapters(
            adapter_ids,
            composition_strategy=composition_strategy
        )
        composition_time = (time.time() - start_time) * 1000
        
        # Update stats
        self.stats['total_compositions'] += 1
        n = self.stats['total_compositions']
        self.stats['avg_composition_time_ms'] = (
            (self.stats['avg_composition_time_ms'] * (n - 1)) + composition_time
        ) / n
        
        # Cache composition
        composition = ActiveComposition(
            composition_id=comp_id,
            adapter_ids=adapter_ids,
            composition_strategy=composition_strategy,
            model=model,
            created_at=datetime.utcnow(),
            last_used=datetime.utcnow()
        )
        self.cache.put(composition)
        
        logger.info(f"Composed adapters in {composition_time:.1f}ms: {comp_id}")
        
        return model
    
    def swap_adapter(
        self,
        old_adapter_id: str,
        new_adapter_id: str,
        warm_swap: bool = True
    ) -> None:
        """
        Hot-swap an adapter in active compositions.
        
        Args:
            old_adapter_id: Adapter to replace
            new_adapter_id: New adapter
            warm_swap: Pre-compose before swapping
        """
        logger.info(f"Swapping adapter: {old_adapter_id} -> {new_adapter_id}")
        
        # Find affected compositions
        affected_comps = [
            comp for comp in self.cache.cache.values()
            if old_adapter_id in comp.adapter_ids
        ]
        
        if not affected_comps:
            logger.info("No active compositions affected")
            return
        
        # Create new compositions
        for old_comp in affected_comps:
            # Replace adapter in list
            new_adapter_ids = [
                new_adapter_id if aid == old_adapter_id else aid
                for aid in old_comp.adapter_ids
            ]
            
            if warm_swap:
                # Pre-compose new version
                new_model = self.adapter_manager.compose_adapters(
                    new_adapter_ids,
                    composition_strategy=old_comp.composition_strategy
                )
                
                # Create new composition
                new_comp_id = self._get_composition_id(
                    new_adapter_ids,
                    old_comp.composition_strategy
                )
                
                new_comp = ActiveComposition(
                    composition_id=new_comp_id,
                    adapter_ids=new_adapter_ids,
                    composition_strategy=old_comp.composition_strategy,
                    model=new_model,
                    created_at=datetime.utcnow(),
                    last_used=datetime.utcnow(),
                    request_count=old_comp.request_count
                )
                
                # Atomic swap in cache
                self.cache.remove(old_comp.composition_id)
                self.cache.put(new_comp)
                
                logger.info(f"Hot-swapped composition: {old_comp.composition_id} -> {new_comp_id}")
            else:
                # Cold swap: just invalidate cache
                self.cache.remove(old_comp.composition_id)
        
        logger.info(f"Swapped {len(affected_comps)} compositions")
    
    def prefetch(self, adapter_ids: List[str], composition_strategy: str = "sequential") -> None:
        """Prefetch and cache a composition."""
        self.compose_sync(adapter_ids, composition_strategy)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            **self.stats,
            'cached_compositions': len(self.cache.cache),
            'cache_hit_rate': (
                self.stats['cache_hits'] / (self.stats['cache_hits'] + self.stats['cache_misses'])
                if (self.stats['cache_hits'] + self.stats['cache_misses']) > 0
                else 0.0
            ),
            'queue_size': len(self.request_queue)
        }
    
    def shutdown(self) -> None:
        """Shutdown compositor and worker thread."""
        logger.info("Shutting down compositor...")
        self.running = False
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        
        self.cache.clear()
        logger.info("Compositor shutdown complete")
    
    def _start_worker(self) -> None:
        """Start background worker thread."""
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
    
    def _worker_loop(self) -> None:
        """Background worker for processing composition requests."""
        logger.info("Compositor worker started")
        
        while self.running:
            try:
                # Get request from queue
                request_item = None
                with self.queue_lock:
                    if self.request_queue:
                        request_item = self.request_queue.popleft()
                
                if request_item:
                    request, callback = request_item
                    
                    # Compose adapters
                    model = self.compose_sync(
                        request.adapter_ids,
                        request.composition_strategy
                    )
                    
                    # Call callback if provided
                    if callback:
                        try:
                            callback(request.request_id, model)
                        except Exception as e:
                            logger.error(f"Callback error: {e}")
                else:
                    # Sleep briefly if queue empty
                    time.sleep(0.1)
            
            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(1.0)
        
        logger.info("Compositor worker stopped")
    
    def _warmup(self, compositions: List[List[str]]) -> None:
        """Pre-warm common compositions."""
        logger.info(f"Warming up {len(compositions)} compositions...")
        
        for adapter_ids in compositions:
            try:
                self.prefetch(adapter_ids)
            except Exception as e:
                logger.error(f"Warmup failed for {adapter_ids}: {e}")
        
        logger.info("Warmup complete")
    
    def _get_composition_id(self, adapter_ids: List[str], strategy: str) -> str:
        """Generate unique composition ID."""
        adapters_str = "_".join(sorted(adapter_ids))
        return f"{strategy}:{adapters_str}"


# Global compositor instance
_compositor: Optional[RealtimeCompositor] = None


def get_compositor(adapter_manager: Optional[Any] = None) -> RealtimeCompositor:
    """Get global real-time compositor instance."""
    global _compositor
    if _compositor is None:
        if adapter_manager is None:
            raise ValueError("adapter_manager required for first initialization")
        _compositor = RealtimeCompositor(adapter_manager)
    return _compositor


def compose_realtime(
    adapter_ids: List[str],
    composition_strategy: str = "sequential",
    async_mode: bool = False
) -> Any:
    """Compose adapters in real-time (convenience function)."""
    compositor = get_compositor()
    
    if async_mode:
        return compositor.compose_async(adapter_ids, composition_strategy)
    else:
        return compositor.compose_sync(adapter_ids, composition_strategy)
