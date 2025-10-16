"""CrewAI-based agent system with LoRA Federation integration."""

import logging
from typing import Dict, Any, Optional, List, Callable
from abc import ABC, abstractmethod

from crewai import Agent, Task, Crew, Process
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..services.llm_federation import LoRAFederation

logger = logging.getLogger(__name__)


class FederatedLLM:
    """
    Custom LLM wrapper that uses our LoRA Federation service.
    
    This allows CrewAI agents to use our federated LoRA adapters
    instead of standard LLM APIs.
    """
    
    def __init__(
        self,
        federation: LoRAFederation,
        task_name: str,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None
    ):
        """Initialize federated LLM.
        
        Args:
            federation: Federation service instance
            task_name: Task identifier for adapter selection
            retailer_id: Retailer context
            brand_id: Brand context
        """
        self.federation = federation
        self.task_name = task_name
        self.retailer_id = retailer_id
        self.brand_id = brand_id
        
        # CrewAI compatibility attributes
        self.model_name = f"federated-lora-{task_name}"
        self.temperature = 0.7
        self.max_tokens = 2048
    
    def __call__(self, prompt: str, **kwargs) -> str:
        """Call the LLM with a prompt (CrewAI interface)."""
        result = self.federation.infer(
            prompt=prompt,
            task=self.task_name,
            retailer_id=self.retailer_id,
            brand_id=self.brand_id,
            system_prompt=kwargs.get("system_prompt")
        )
        return result.get("response", "")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response (alternative interface)."""
        return self.__call__(prompt, **kwargs)


class RMNTool(BaseTool):
    """
    Base class for RMN-specific tools that work with CrewAI.
    
    Extends CrewAI's BaseTool with RMN-specific functionality.
    """
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    
    def _run(self, *args, **kwargs) -> Any:
        """Execute the tool (CrewAI interface)."""
        return self.execute(*args, **kwargs)
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the tool (implementation)."""
        pass


class RMNAgent(ABC):
    """
    Base class for RMN agents using CrewAI framework.
    
    Provides:
    - Integration with LoRA Federation
    - CrewAI Agent creation
    - Tool management
    - Task execution
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        federation: LoRAFederation,
        tools: Optional[List[RMNTool]] = None,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None,
        verbose: bool = True,
        allow_delegation: bool = False
    ):
        """Initialize RMN agent.
        
        Args:
            name: Agent name/identifier
            role: Agent role description
            goal: Agent goal
            backstory: Agent backstory for context
            federation: Federation service
            tools: List of tools available to agent
            retailer_id: Retailer context
            brand_id: Brand context
            verbose: Enable verbose logging
            allow_delegation: Allow agent to delegate tasks
        """
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.federation = federation
        self.tools = tools or []
        self.retailer_id = retailer_id
        self.brand_id = brand_id
        self.verbose = verbose
        self.allow_delegation = allow_delegation
        
        # Create federated LLM for this agent
        self.llm = FederatedLLM(
            federation=federation,
            task_name=name,
            retailer_id=retailer_id,
            brand_id=brand_id
        )
        
        # Create CrewAI agent
        self.agent = self._create_agent()
        
        logger.info(f"Initialized RMN Agent: {name}")
    
    def _create_agent(self) -> Agent:
        """Create CrewAI Agent with federation."""
        return Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            llm=self.llm,
            tools=self.tools,
            verbose=self.verbose,
            allow_delegation=self.allow_delegation
        )
    
    def create_task(
        self,
        description: str,
        expected_output: str,
        context: Optional[List[Task]] = None
    ) -> Task:
        """
        Create a task for this agent.
        
        Args:
            description: Task description
            expected_output: Expected output format
            context: Optional list of dependent tasks
            
        Returns:
            CrewAI Task instance
        """
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
            context=context or []
        )
    
    def add_tool(self, tool: RMNTool) -> None:
        """Add a tool to this agent."""
        self.tools.append(tool)
        # Recreate agent with new tools
        self.agent = self._create_agent()
        logger.info(f"Added tool '{tool.name}' to agent '{self.name}'")
    
    def get_active_adapters(self) -> List[str]:
        """Get adapters currently active for this agent."""
        return self.federation.get_active_adapters()


class RMNCrew:
    """
    RMN Crew - orchestrates multiple agents for complex workflows.
    
    Uses CrewAI's Crew functionality with our federated agents.
    """
    
    def __init__(
        self,
        name: str,
        agents: List[RMNAgent],
        tasks: List[Task],
        process: Process = Process.sequential,
        verbose: bool = True
    ):
        """Initialize RMN Crew.
        
        Args:
            name: Crew name
            agents: List of RMN agents
            tasks: List of tasks to execute
            process: Execution process (sequential or hierarchical)
            verbose: Enable verbose logging
        """
        self.name = name
        self.rmn_agents = agents
        self.tasks = tasks
        self.process = process
        self.verbose = verbose
        
        # Create CrewAI Crew
        self.crew = Crew(
            agents=[agent.agent for agent in agents],
            tasks=tasks,
            process=process,
            verbose=verbose
        )
        
        logger.info(f"Initialized RMN Crew: {name} with {len(agents)} agents")
    
    def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the crew workflow.
        
        Args:
            inputs: Optional input data for tasks
            
        Returns:
            Crew execution results
        """
        logger.info(f"Starting crew '{self.name}' execution")
        
        try:
            result = self.crew.kickoff(inputs=inputs)
            
            # Add metadata
            return {
                "result": result,
                "crew": self.name,
                "agents": [agent.name for agent in self.rmn_agents],
                "tasks_completed": len(self.tasks),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Crew execution failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "crew": self.name,
                "status": "failed"
            }
    
    def get_all_adapters_used(self) -> Dict[str, List[str]]:
        """Get all adapters used by agents in this crew."""
        adapters_by_agent = {}
        for agent in self.rmn_agents:
            adapters_by_agent[agent.name] = agent.get_active_adapters()
        return adapters_by_agent


# Pre-built RMN Agent Classes

class HarmonizerAgent(RMNAgent):
    """Agent for data harmonization tasks."""
    
    def __init__(
        self,
        federation: LoRAFederation,
        tools: Optional[List[RMNTool]] = None,
        retailer_id: Optional[str] = None
    ):
        super().__init__(
            name="harmonizer",
            role="Data Harmonization Specialist",
            goal="Transform retailer-specific data formats into the canonical RMIS schema",
            backstory="""You are an expert in retail media data formats and schema mapping.
            You understand the nuances of different retailer data structures and can accurately
            map them to the Retail Media Interop Schema (RMIS) while maintaining data quality.""",
            federation=federation,
            tools=tools,
            retailer_id=retailer_id,
            allow_delegation=False
        )


class PlannerAgent(RMNAgent):
    """Agent for campaign planning and optimization."""
    
    def __init__(
        self,
        federation: LoRAFederation,
        tools: Optional[List[RMNTool]] = None,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None
    ):
        super().__init__(
            name="planner",
            role="Campaign Planning Strategist",
            goal="Create optimal media plans that maximize incremental ROAS within constraints",
            backstory="""You are a retail media planning expert with deep knowledge of
            budget allocation, audience targeting, and incrementality measurement. You use
            data-driven insights to create plans that balance performance and experimentation.""",
            federation=federation,
            tools=tools,
            retailer_id=retailer_id,
            brand_id=brand_id,
            allow_delegation=True
        )


class OptimizerAgent(RMNAgent):
    """Agent for budget optimization."""
    
    def __init__(
        self,
        federation: LoRAFederation,
        tools: Optional[List[RMNTool]] = None,
        brand_id: Optional[str] = None
    ):
        super().__init__(
            name="optimizer",
            role="Budget Optimization Specialist",
            goal="Allocate budget to maximize incremental margin while meeting constraints",
            backstory="""You are an optimization expert skilled in linear programming,
            contextual bandits, and causal inference. You find the optimal allocation
            that balances short-term performance with long-term learning.""",
            federation=federation,
            tools=tools,
            brand_id=brand_id,
            allow_delegation=False
        )


class CreativeAgent(RMNAgent):
    """Agent for creative generation."""
    
    def __init__(
        self,
        federation: LoRAFederation,
        tools: Optional[List[RMNTool]] = None,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None
    ):
        super().__init__(
            name="creative",
            role="Creative Content Generator",
            goal="Generate compelling, policy-compliant ad copy that drives conversions",
            backstory="""You are a creative copywriter specializing in retail media.
            You understand brand voice, retailer policies, and what messaging resonates
            with different audiences. You always ensure compliance while maximizing impact.""",
            federation=federation,
            tools=tools,
            retailer_id=retailer_id,
            brand_id=brand_id,
            allow_delegation=False
        )


class GovernanceAgent(RMNAgent):
    """Agent for policy and compliance checking."""
    
    def __init__(
        self,
        federation: LoRAFederation,
        tools: Optional[List[RMNTool]] = None,
        retailer_id: Optional[str] = None
    ):
        super().__init__(
            name="governance",
            role="Compliance and Policy Officer",
            goal="Ensure all outputs comply with privacy regulations and retailer policies",
            backstory="""You are a compliance expert with deep knowledge of privacy laws
            (GDPR, CCPA), retailer advertising policies, and data governance best practices.
            You protect both the brand and consumers by ensuring all activities are compliant.""",
            federation=federation,
            tools=tools,
            retailer_id=retailer_id,
            allow_delegation=False
        )


class MeasurementAgent(RMNAgent):
    """Agent for experiment design and measurement."""
    
    def __init__(
        self,
        federation: LoRAFederation,
        tools: Optional[List[RMNTool]] = None
    ):
        super().__init__(
            name="measurement",
            role="Measurement and Experimentation Lead",
            goal="Design valid experiments and measure incremental lift accurately",
            backstory="""You are a statistician and experimentation expert. You design
            geo tests, switchback experiments, and synthetic control studies that provide
            reliable causal estimates of campaign impact. You ensure statistical rigor
            and practical validity.""",
            federation=federation,
            tools=tools,
            allow_delegation=False
        )
