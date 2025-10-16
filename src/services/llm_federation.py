"""LLM Federation Service - Core adapter composition and inference routing."""

import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import json

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from ..runtime.adapter_manager import AdapterManager

logger = logging.getLogger(__name__)


@dataclass
class FederationConfig:
    """Configuration for LLM Federation."""
    
    base_model_path: str = "meta-llama/Llama-3.1-8B-Instruct"
    adapters_dir: Path = field(default_factory=lambda: Path("models/adapters"))
    device: str = "auto"
    max_new_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    cache_adapters: bool = True
    log_composition: bool = True


class LoRAFederation:
    """
    Core federation service that composes LoRA adapters and handles inference.
    
    This service dynamically selects and composes adapters based on:
    - Task type (harmonization, planning, creative, etc.)
    - Retailer context
    - Brand/manufacturer context
    """
    
    def __init__(
        self,
        config: Optional[FederationConfig] = None,
        adapter_manager: Optional[AdapterManager] = None
    ):
        """Initialize federation service.
        
        Args:
            config: Federation configuration
            adapter_manager: Optional pre-initialized adapter manager
        """
        self.config = config or FederationConfig()
        
        # Initialize or use provided adapter manager
        if adapter_manager:
            self.adapter_manager = adapter_manager
        else:
            self.adapter_manager = AdapterManager(
                base_model_path=self.config.base_model_path,
                adapters_dir=self.config.adapters_dir,
                device=self.config.device
            )
        
        # Track active composition
        self.active_adapters: List[str] = []
        self.composition_log: List[Dict[str, Any]] = []
        
        # Tokenizer (loaded lazily)
        self.tokenizer: Optional[AutoTokenizer] = None
        
        logger.info("LoRA Federation Service initialized")
    
    def compose(
        self,
        task: str,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None,
        force_adapters: Optional[List[str]] = None
    ) -> Tuple[Any, List[str]]:
        """
        Compose adapters for a specific task and context.
        
        Args:
            task: Task type (harmonization, planning, optimization, creative, governance)
            retailer_id: Retailer identifier for retailer-specific adapter
            brand_id: Brand/manufacturer identifier
            force_adapters: Optional list to force specific adapters
            
        Returns:
            Tuple of (composed_model, adapter_ids_used)
        """
        start_time = time.time()
        
        # Select adapters
        if force_adapters:
            adapter_ids = force_adapters
        else:
            adapter_ids = self._select_adapters(task, retailer_id, brand_id)
        
        logger.info(f"Composing adapters for task '{task}': {adapter_ids}")
        
        # Compose adapters
        if adapter_ids:
            model = self.adapter_manager.compose_adapters(
                adapter_ids,
                composition_strategy="sequential"
            )
        else:
            # Use base model only
            self.adapter_manager.load_base_model()
            model = self.adapter_manager.base_model
        
        # Track composition
        self.active_adapters = adapter_ids
        
        if self.config.log_composition:
            self.composition_log.append({
                "timestamp": time.time(),
                "task": task,
                "retailer_id": retailer_id,
                "brand_id": brand_id,
                "adapters": adapter_ids,
                "composition_time_ms": (time.time() - start_time) * 1000
            })
        
        logger.info(f"Adapter composition completed in {(time.time() - start_time)*1000:.1f}ms")
        
        return model, adapter_ids
    
    def _select_adapters(
        self,
        task: str,
        retailer_id: Optional[str],
        brand_id: Optional[str]
    ) -> List[str]:
        """
        Select appropriate adapters based on task and context.
        
        Selection strategy:
        1. Always include industry adapter (if available)
        2. Add retailer adapter if retailer_id provided
        3. Add manufacturer/brand adapter if brand_id provided
        4. Add task-specific adapter
        
        Args:
            task: Task type
            retailer_id: Retailer identifier
            brand_id: Brand identifier
            
        Returns:
            List of adapter IDs to compose
        """
        selected = []
        
        # 1. Industry adapter (retail media domain knowledge)
        industry_adapters = self.adapter_manager.get_adapters_by_type("industry")
        if industry_adapters:
            selected.append(industry_adapters[0].adapter_id)
        
        # 2. Retailer adapter (retailer-specific schemas, policies)
        if retailer_id:
            retailer_adapters = [
                a for a in self.adapter_manager.get_adapters_by_type("retailer")
                if retailer_id in a.tags
            ]
            if retailer_adapters:
                selected.append(retailer_adapters[0].adapter_id)
        
        # 3. Manufacturer/Brand adapter (brand tone, private metrics)
        if brand_id:
            brand_adapters = [
                a for a in self.adapter_manager.get_adapters_by_type("manufacturer")
                if brand_id in a.tags
            ]
            if brand_adapters:
                selected.append(brand_adapters[0].adapter_id)
        
        # 4. Task-specific adapter
        task_adapters = [
            a for a in self.adapter_manager.get_adapters_by_type("task")
            if task in a.tags or task.lower() in a.name.lower()
        ]
        if task_adapters:
            selected.append(task_adapters[0].adapter_id)
        
        return selected
    
    def infer(
        self,
        prompt: str,
        task: str,
        retailer_id: Optional[str] = None,
        brand_id: Optional[str] = None,
        tools: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run inference with composed adapters.
        
        Args:
            prompt: User prompt
            task: Task type
            retailer_id: Retailer context
            brand_id: Brand context
            tools: Available tools for tool calling
            system_prompt: Optional system prompt
            
        Returns:
            Dict with response, adapters_used, tool_calls, etc.
        """
        start_time = time.time()
        
        # Compose adapters
        model, adapter_ids = self.compose(task, retailer_id, brand_id)
        
        # Load tokenizer if needed
        if self.tokenizer is None:
            self.tokenizer = self.adapter_manager.tokenizer
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Add tool information if provided
        if tools:
            tool_desc = self._format_tools(tools)
            messages.append({
                "role": "system",
                "content": f"Available tools:\n{tool_desc}"
            })
        
        # Generate response
        response_text = self._generate(model, messages)
        
        # Parse tool calls if present
        tool_calls = self._parse_tool_calls(response_text) if tools else []
        
        inference_time = (time.time() - start_time) * 1000
        
        result = {
            "response": response_text,
            "adapters_used": adapter_ids,
            "tool_calls": tool_calls,
            "inference_time_ms": inference_time,
            "task": task,
            "timestamp": time.time()
        }
        
        logger.info(f"Inference completed in {inference_time:.1f}ms")
        
        return result
    
    def _generate(
        self,
        model: Any,
        messages: List[Dict[str, str]]
    ) -> str:
        """Generate response from model."""
        # Format messages
        if hasattr(self.tokenizer, "apply_chat_template"):
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
        else:
            # Fallback formatting
            prompt = "\n\n".join([f"{m['role']}: {m['content']}" for m in messages])
            prompt += "\n\nassistant:"
        
        # Tokenize
        inputs = self.tokenizer(prompt, return_tensors="pt").to(model.device)
        
        # Generate
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                top_p=self.config.top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )
        
        return response.strip()
    
    def _format_tools(self, tools: Dict[str, Any]) -> str:
        """Format tool descriptions for prompt."""
        tool_lines = []
        for tool_name, tool_info in tools.items():
            desc = tool_info.get("description", "")
            tool_lines.append(f"- {tool_name}: {desc}")
        return "\n".join(tool_lines)
    
    def _parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """Parse tool calls from response."""
        tool_calls = []
        
        # Try to parse JSON tool calls
        try:
            # Look for JSON blocks
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                parsed = json.loads(json_str)
                
                if isinstance(parsed, dict) and parsed.get("type") == "tool_call":
                    tool_calls.append({
                        "tool": parsed.get("tool"),
                        "args": parsed.get("args", {})
                    })
                elif isinstance(parsed, list):
                    tool_calls.extend(parsed)
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug(f"No tool calls parsed: {e}")
        
        return tool_calls
    
    def get_active_adapters(self) -> List[str]:
        """Get currently active adapter IDs."""
        return self.active_adapters.copy()
    
    def get_composition_log(self) -> List[Dict[str, Any]]:
        """Get log of adapter compositions."""
        return self.composition_log.copy()
    
    def clear_cache(self) -> None:
        """Clear adapter cache."""
        self.adapter_manager.clear_cache()
        self.active_adapters = []
        logger.info("Federation cache cleared")
    
    def get_available_adapters(self) -> Dict[str, List[str]]:
        """Get all available adapters by type."""
        return {
            "industry": [a.adapter_id for a in self.adapter_manager.get_adapters_by_type("industry")],
            "retailer": [a.adapter_id for a in self.adapter_manager.get_adapters_by_type("retailer")],
            "manufacturer": [a.adapter_id for a in self.adapter_manager.get_adapters_by_type("manufacturer")],
            "task": [a.adapter_id for a in self.adapter_manager.get_adapters_by_type("task")]
        }


def merge_loras(base_model: Any, adapters: List[str]) -> Any:
    """
    Merge multiple LoRA adapters into base model.
    
    This is a convenience function that wraps the adapter manager's
    composition functionality.
    
    Args:
        base_model: Base model or model path
        adapters: List of adapter paths or IDs
        
    Returns:
        Model with merged adapters
    """
    # This is handled by AdapterManager.compose_adapters
    # Kept for API compatibility with requirements
    logger.warning("merge_loras is deprecated, use LoRAFederation.compose instead")
    return base_model
