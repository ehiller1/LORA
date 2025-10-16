"""Planner Agent - Orchestrates planning and tool calls."""

import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import torch

from ..schemas.tools import (
    QueryCleanRoomInput,
    AllocateBudgetInput,
    DesignExperimentInput,
    GenerateCopyInput,
)

logger = logging.getLogger(__name__)


PLANNER_SYSTEM_PROMPT = """You are the Planner Agent in a Retail Media optimization stack. Your role is to:
- Translate user objectives into a structured plan and precise tool calls.
- Always prefer incremental outcomes (uplift, incremental ROAS/margin) over last-click.
- Enforce brand and retailer policies. Never produce PII. Never request raw user-level data outside clean rooms.
- Use the canonical Retail Media Interop Schema (RMIS) for data semantics.
- Call tools for data access and optimization; do not perform optimization internally.
- When constraints conflict, ask a clarifying question instead of guessing.
- Output ONLY JSON that conforms to the specified schema for each action, no prose.

Definitions:
- Incremental ROAS = incremental revenue / spend.
- ICE (Incremental Cost-Effectiveness) = incremental sales or margin per incremental dollar.
- Experiments must be designed for measurement validity (geo/switchback), with minimum cell sizes and lift confidence thresholds.

Available Tools:
1. query_clean_room: Fetch aggregated, privacy-safe metrics from clean rooms
2. allocate_budget: Call solver/bandit to allocate budget with constraints
3. design_experiment: Propose valid experiment design for lift measurement
4. generate_copy: Create compliant creative copy variants

Guardrails:
- No PII in outputs. Aggregated results only with minimum thresholds.
- Respect retailer creative specs and disallowed terms.
- For data joins, only use clean-room endpoints via query_clean_room().

Output Format:
Return JSON with one of:
- {"type": "ask_clarification", "question": "..."}
- {"type": "tool_call", "tool": "tool_name", "args": {...}}
- {"type": "plan", "steps": [...], "rationale": "..."}
- {"type": "result", "summary": "...", "details": {...}}
"""


class PlannerAgent:
    """Agent for orchestrating planning and tool calls."""
    
    def __init__(
        self,
        base_model_path: str,
        adapter_paths: Optional[List[Path]] = None,
        device: str = "auto"
    ):
        """Initialize Planner Agent.
        
        Args:
            base_model_path: Path or HF model ID for base model
            adapter_paths: List of LoRA adapter paths to load
            device: Device to run on (auto, cuda, cpu)
        """
        self.base_model_path = base_model_path
        self.adapter_paths = adapter_paths or []
        self.device = device
        
        logger.info(f"Loading base model: {base_model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map=device,
            trust_remote_code=True
        )
        
        # Load adapters
        for adapter_path in self.adapter_paths:
            if adapter_path.exists():
                logger.info(f"Loading adapter: {adapter_path}")
                self.model = PeftModel.from_pretrained(
                    self.model,
                    str(adapter_path),
                    is_trainable=False
                )
        
        self.model.eval()
        logger.info("Planner Agent initialized")
    
    def plan(
        self,
        objective: str,
        context: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a plan for the given objective.
        
        Args:
            objective: User objective/goal
            context: Additional context (historical data, current state)
            constraints: Constraints to enforce
            
        Returns:
            Plan with tool calls and rationale
        """
        # Build prompt
        messages = [
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": self._build_user_prompt(objective, context, constraints)}
        ]
        
        # Generate response
        response = self._generate(messages)
        
        # Parse response
        try:
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse plan JSON: {e}")
            return {
                "type": "error",
                "message": "Failed to generate valid plan",
                "raw_response": response
            }
    
    def _build_user_prompt(
        self,
        objective: str,
        context: Optional[Dict[str, Any]],
        constraints: Optional[Dict[str, Any]]
    ) -> str:
        """Build user prompt from objective, context, and constraints."""
        prompt_parts = [f"Objective: {objective}"]
        
        if context:
            prompt_parts.append(f"\nContext: {json.dumps(context, indent=2)}")
        
        if constraints:
            prompt_parts.append(f"\nConstraints: {json.dumps(constraints, indent=2)}")
        
        prompt_parts.append("\nGenerate a plan with tool calls to achieve this objective.")
        
        return "\n".join(prompt_parts)
    
    def _generate(self, messages: List[Dict[str, str]], max_new_tokens: int = 2048) -> str:
        """Generate response from model.
        
        Args:
            messages: List of message dicts with role and content
            max_new_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        # Format messages using tokenizer's chat template
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
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )
        
        return response.strip()
    
    def _execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call by routing to actual agent implementations.
        
        Args:
            tool_call: Tool call specification
            
        Returns:
            Tool execution result
        """
        tool_name = tool_call.get("tool")
        args = tool_call.get("args", {})
        
        logger.info(f"Executing tool: {tool_name}")
        
        try:
            if tool_name == "query_clean_room":
                return self._execute_query_clean_room(args)
            elif tool_name == "allocate_budget":
                return self._execute_allocate_budget(args)
            elif tool_name == "design_experiment":
                return self._execute_design_experiment(args)
            elif tool_name == "generate_copy":
                return self._execute_generate_copy(args)
            else:
                return {
                    "error": f"Unknown tool: {tool_name}"
                }
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                "error": str(e),
                "tool": tool_name
            }
    
    def _execute_query_clean_room(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute clean room query using actual API or database."""
        import httpx
        
        # Get clean room endpoint from config or args
        endpoint = args.get("endpoint") or self.config.get("clean_room_endpoint")
        
        if not endpoint:
            logger.warning("No clean room endpoint configured, using mock data")
            return self._mock_query_clean_room(args)
        
        # Make actual API call
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{endpoint}/query",
                    json={
                        "query": args.get("query"),
                        "filters": args.get("filters", {}),
                        "aggregations": args.get("aggregations", [])
                    },
                    headers={"Authorization": f"Bearer {self.config.get('clean_room_api_key')}"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Clean room query failed: {e}")
            return {"error": str(e)}
    
    def _execute_allocate_budget(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute budget allocation using BudgetOptimizerAgent."""
        from src.agents.budget_optimizer import BudgetOptimizerAgent
        
        # Initialize budget optimizer
        optimizer = BudgetOptimizerAgent(
            method=args.get("method", "convex")
        )
        
        # Prepare priors from args
        priors = args.get("priors", [])
        
        # Allocate budget
        result = optimizer.allocate(
            total_budget=args["total_budget"],
            priors=priors,
            constraints=args.get("constraints", {})
        )
        
        return result
    
    def _execute_design_experiment(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute experiment design using MeasurementAgent."""
        from src.agents.measurement import MeasurementAgent, ExperimentDesigner
        
        # Initialize measurement agent
        agent = MeasurementAgent()
        designer = ExperimentDesigner()
        
        # Design experiment
        design = designer.design_experiment(
            experiment_type=args.get("experiment_type", "geo"),
            treatment_effect=args.get("min_detectable_effect", 0.1),
            power=args.get("power", 0.8),
            alpha=args.get("alpha", 0.05),
            units=args.get("units", [])
        )
        
        return design
    
    def _execute_generate_copy(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute creative copy generation using CreativeAgent."""
        from src.agents.creative import CreativeAgent
        
        # Initialize creative agent
        agent = CreativeAgent(
            model_name=self.model_name,
            retailer_id=args.get("retailer_id")
        )
        
        # Generate copy variants
        result = agent.generate_copy(
            product_name=args["product_name"],
            key_features=args.get("key_features", []),
            target_audience=args.get("target_audience"),
            num_variants=args.get("num_variants", 5),
            tone=args.get("tone", "professional")
        )
        
        return result
    
    def _mock_query_clean_room(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback mock for clean room queries."""
        return {
            "results": [
                {
                    "name": "performance_by_placement",
                    "rows": [
                        {
                            "rmn": "retailer_A",
                            "placement_type": "sponsored_product",
                            "cost": 50000,
                            "attributed_revenue": 175000,
                            "incremental_roas": 3.2
                        },
                        {
                            "rmn": "retailer_B",
                            "placement_type": "onsite_display",
                            "cost": 30000,
                            "attributed_revenue": 105000,
                            "incremental_roas": 3.5
                        }
                    ],
                    "row_count": 2,
                    "suppressed_cells": 0
                }
            ],
            "total_rows": 2,
            "execution_time_ms": 234.5,
            "note": "Mock data - configure clean_room_endpoint for real queries"
        }


def main():
    """CLI entry point for Planner Agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Planner Agent")
    parser.add_argument("--base-model", default="meta-llama/Llama-3.1-8B-Instruct", help="Base model path")
    parser.add_argument("--adapters", nargs="*", help="Adapter paths to load")
    parser.add_argument("--objective", required=True, help="Planning objective")
    parser.add_argument("--context", type=json.loads, help="Context as JSON")
    parser.add_argument("--constraints", type=json.loads, help="Constraints as JSON")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Initialize agent
    adapter_paths = [Path(p) for p in args.adapters] if args.adapters else []
    agent = PlannerAgent(args.base_model, adapter_paths)
    
    # Generate plan
    plan = agent.plan(args.objective, args.context, args.constraints)
    
    print("\n=== Generated Plan ===")
    print(json.dumps(plan, indent=2))
    
    # If plan includes tool calls, execute them
    if plan.get("type") == "tool_call":
        result = agent.execute_tool_call(plan)
        print("\n=== Tool Execution Result ===")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
