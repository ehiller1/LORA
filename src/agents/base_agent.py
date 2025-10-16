"""Base Agent class for unified federation integration."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json

from ..services.llm_federation import LoRAFederation

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all agents in the RMN LoRA system.
    
    Provides unified interface for:
    - Federation integration
    - Tool execution
    - Prompt building
    - Result parsing
    """
    
    def __init__(
        self,
        name: str,
        federation: LoRAFederation,
        tools: Optional[Dict[str, Any]] = None,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None
    ):
        """Initialize base agent.
        
        Args:
            name: Agent name/task identifier
            federation: Federation service instance
            tools: Available tools for this agent
            retailer_id: Retailer context
            brand_id: Brand/manufacturer context
        """
        self.name = name
        self.federation = federation
        self.tools = tools or {}
        self.retailer_id = retailer_id
        self.brand_id = brand_id
        
        logger.info(f"Initialized {self.__class__.__name__} '{name}'")
    
    def execute(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task with federation.
        
        This is the main entry point for agent execution.
        
        Args:
            user_input: User input/request
            
        Returns:
            Agent execution result
        """
        try:
            # Build prompt
            prompt = self.build_prompt(user_input)
            system_prompt = self.get_system_prompt()
            
            # Run inference with federation
            result = self.federation.infer(
                prompt=prompt,
                task=self.name,
                retailer_id=self.retailer_id,
                brand_id=self.brand_id,
                tools=self.tools,
                system_prompt=system_prompt
            )
            
            # Parse result
            parsed_result = self.parse_result(result)
            
            # Execute tool calls if present
            if result.get("tool_calls"):
                tool_results = self._execute_tools(result["tool_calls"])
                parsed_result["tool_results"] = tool_results
            
            # Add metadata
            parsed_result["agent"] = self.name
            parsed_result["adapters_used"] = result.get("adapters_used", [])
            parsed_result["inference_time_ms"] = result.get("inference_time_ms", 0)
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}", exc_info=True)
            return {
                "error": str(e),
                "agent": self.name,
                "status": "failed"
            }
    
    @abstractmethod
    def build_prompt(self, user_input: Dict[str, Any]) -> str:
        """
        Build prompt from user input.
        
        Must be implemented by subclasses.
        
        Args:
            user_input: User input dict
            
        Returns:
            Formatted prompt string
        """
        pass
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get system prompt for this agent.
        
        Must be implemented by subclasses.
        
        Returns:
            System prompt string
        """
        pass
    
    def parse_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse LLM result into structured output.
        
        Default implementation tries to parse JSON.
        Can be overridden by subclasses.
        
        Args:
            result: Raw LLM result
            
        Returns:
            Parsed result dict
        """
        response = result.get("response", "")
        
        # Try to parse JSON
        try:
            # Look for JSON in response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                parsed = json.loads(json_str)
                return parsed
            elif response.strip().startswith("{"):
                parsed = json.loads(response)
                return parsed
            else:
                # Return as-is
                return {"response": response}
        except json.JSONDecodeError:
            logger.debug("Could not parse JSON, returning raw response")
            return {"response": response}
    
    def _execute_tools(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute tool calls.
        
        Args:
            tool_calls: List of tool call specifications
            
        Returns:
            List of tool execution results
        """
        results = []
        
        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            args = tool_call.get("args", {})
            
            if tool_name not in self.tools:
                results.append({
                    "tool": tool_name,
                    "error": f"Tool '{tool_name}' not available"
                })
                continue
            
            try:
                tool_func = self.tools[tool_name]
                result = tool_func(**args)
                results.append({
                    "tool": tool_name,
                    "result": result,
                    "status": "success"
                })
            except Exception as e:
                logger.error(f"Tool execution error for '{tool_name}': {e}")
                results.append({
                    "tool": tool_name,
                    "error": str(e),
                    "status": "failed"
                })
        
        return results
    
    def add_tool(self, name: str, func: callable, description: str = "") -> None:
        """
        Add a tool to this agent.
        
        Args:
            name: Tool name
            func: Tool function
            description: Tool description
        """
        self.tools[name] = {
            "function": func,
            "description": description
        }
        logger.info(f"Added tool '{name}' to agent '{self.name}'")
    
    def remove_tool(self, name: str) -> None:
        """Remove a tool from this agent."""
        if name in self.tools:
            del self.tools[name]
            logger.info(f"Removed tool '{name}' from agent '{self.name}'")


class SimpleAgent(BaseAgent):
    """
    Simple agent implementation for quick prototyping.
    
    Uses provided prompts without complex logic.
    """
    
    def __init__(
        self,
        name: str,
        federation: LoRAFederation,
        system_prompt: str,
        tools: Optional[Dict[str, Any]] = None,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None
    ):
        """Initialize simple agent.
        
        Args:
            name: Agent name
            federation: Federation service
            system_prompt: System prompt to use
            tools: Available tools
            retailer_id: Retailer context
            brand_id: Brand context
        """
        super().__init__(name, federation, tools, retailer_id, brand_id)
        self._system_prompt = system_prompt
    
    def build_prompt(self, user_input: Dict[str, Any]) -> str:
        """Build prompt from user input."""
        if isinstance(user_input, dict):
            # Format dict as JSON
            return json.dumps(user_input, indent=2)
        else:
            return str(user_input)
    
    def get_system_prompt(self) -> str:
        """Get system prompt."""
        return self._system_prompt
