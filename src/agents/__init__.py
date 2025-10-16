"""Agent implementations for RMN LoRA system."""

# CrewAI-based agents (new federation-enabled agents)
from .crewai_base import (
    RMNAgent,
    RMNCrew,
    RMNTool,
    FederatedLLM,
    HarmonizerAgent,
    PlannerAgent,
    OptimizerAgent,
    CreativeAgent,
    GovernanceAgent,
    MeasurementAgent
)

# Legacy base agent (for backward compatibility)
from .base_agent import BaseAgent, SimpleAgent

__all__ = [
    # CrewAI agents
    "RMNAgent",
    "RMNCrew",
    "RMNTool",
    "FederatedLLM",
    "HarmonizerAgent",
    "PlannerAgent",
    "OptimizerAgent",
    "CreativeAgent",
    "GovernanceAgent",
    "MeasurementAgent",
    # Legacy
    "BaseAgent",
    "SimpleAgent"
]

# Legacy agents (original implementations)
from .data_harmonizer import DataHarmonizerAgent
from .budget_optimizer import BudgetOptimizerAgent

# Add legacy agents to exports
__all__.extend([
    "DataHarmonizerAgent",
    "BudgetOptimizerAgent",
])
