"""Enhanced RLHF module with CrewAI and LangChain integration.

This module provides:
- Synthetic feedback generation using CrewAI agents
- Multi-agent RLHF orchestration for comprehensive evaluation
- LangSmith tracing and observability
- Automated end-to-end RLHF pipelines
"""

from .synthetic_feedback import (
    SyntheticFeedbackGenerator,
    SyntheticFeedback,
    DPODatasetBuilder,
    FeedbackDimension
)

from .multi_agent_rlhf import (
    MultiAgentRLHF,
    MultiDimensionalFeedback
)

from .langsmith_integration import (
    LangSmithTracer,
    RLHFMonitor
)

from .automated_pipeline import (
    AutomatedRLHFPipeline,
    PipelineConfig
)

__all__ = [
    # Synthetic Feedback
    "SyntheticFeedbackGenerator",
    "SyntheticFeedback",
    "DPODatasetBuilder",
    "FeedbackDimension",
    
    # Multi-Agent RLHF
    "MultiAgentRLHF",
    "MultiDimensionalFeedback",
    
    # LangSmith Integration
    "LangSmithTracer",
    "RLHFMonitor",
    
    # Automated Pipeline
    "AutomatedRLHFPipeline",
    "PipelineConfig"
]
