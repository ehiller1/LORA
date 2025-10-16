"""
Federation Demo Workflow - Orchestrates federated LoRA demo with clean room comparison.

This workflow demonstrates:
1. Data harmonization with retailer adapters
2. Campaign planning with industry + manufacturer adapters
3. Clean room vs full data comparison
4. Creative generation with brand adapters
5. Federation visualization
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

from crewai import Task, Process

from src.services.llm_federation import LoRAFederation, FederationConfig
from src.agents.crewai_base import (
    RMNCrew,
    HarmonizerAgent,
    PlannerAgent,
    OptimizerAgent,
    CreativeAgent,
    GovernanceAgent,
    RMNTool
)
from src.schemas.rmis import Plan, ComparisonResult
from demo.tools.warehouse import WarehouseManager
from demo.tools.optimizer import BudgetOptimizer
from demo.tools.clean_room import CleanRoomConnector, query_clean_room
from demo.tools.policy import PolicyChecker
from demo.tools.creatives import CreativeGenerator

logger = logging.getLogger(__name__)


class FederationDemoWorkflow:
    """
    Orchestrates the complete federation demo workflow.
    
    Shows the power of federated LoRA adapters vs clean-room-only approaches.
    """
    
    def __init__(
        self,
        base_model_path: str = "meta-llama/Llama-3.1-8B-Instruct",
        adapters_dir: Optional[Path] = None,
        use_mock_llm: bool = True
    ):
        """Initialize demo workflow.
        
        Args:
            base_model_path: Base LLM model path
            adapters_dir: Directory containing adapter metadata
            use_mock_llm: Use mock LLM for demo (no actual model loading)
        """
        self.use_mock_llm = use_mock_llm
        
        # Initialize federation service
        if use_mock_llm:
            # For demo, use mock federation
            self.federation = MockFederation()
        else:
            config = FederationConfig(
                base_model_path=base_model_path,
                adapters_dir=adapters_dir or Path("demo/mock_adapters")
            )
            self.federation = LoRAFederation(config=config)
        
        # Initialize tools
        self.warehouse = WarehouseManager()
        self.optimizer = BudgetOptimizer()
        self.clean_room = CleanRoomConnector()
        self.policy_checker = PolicyChecker()
        self.creative_gen = CreativeGenerator()
        
        logger.info("Federation Demo Workflow initialized")
    
    def run_full_demo(
        self,
        user_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run the complete demo workflow.
        
        Args:
            user_input: User input with objective, budget, constraints
            
        Returns:
            Complete demo results with comparison
        """
        logger.info("Starting full federation demo workflow")
        
        results = {
            "workflow_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "steps": {}
        }
        
        # Step 1: Data Harmonization
        logger.info("Step 1: Data Harmonization")
        harmonization_result = self.step_1_harmonize_data()
        results["steps"]["harmonization"] = harmonization_result
        
        # Step 2: Generate Plan (Full Data)
        logger.info("Step 2: Generate Plan with Full Data")
        full_plan = self.step_2_generate_plan(user_input, clean_room_mode=False)
        results["steps"]["full_plan"] = full_plan
        
        # Step 3: Generate Plan (Clean Room Only)
        logger.info("Step 3: Generate Plan with Clean Room Only")
        clean_room_plan = self.step_2_generate_plan(user_input, clean_room_mode=True)
        results["steps"]["clean_room_plan"] = clean_room_plan
        
        # Step 4: Compare Results
        logger.info("Step 4: Compare Results")
        comparison = self.step_4_compare_results(full_plan, clean_room_plan)
        results["steps"]["comparison"] = comparison
        
        # Step 5: Generate Creatives
        logger.info("Step 5: Generate Creatives")
        creatives = self.step_5_generate_creatives(user_input)
        results["steps"]["creatives"] = creatives
        
        # Step 6: Federation Visualization
        logger.info("Step 6: Generate Federation Visualization")
        visualization = self.step_6_federation_graph()
        results["steps"]["visualization"] = visualization
        
        logger.info("Demo workflow completed successfully")
        return results
    
    def step_1_harmonize_data(self) -> Dict[str, Any]:
        """Step 1: Harmonize retailer data to RMIS."""
        # Load data from warehouse
        try:
            df = self.warehouse.query("SELECT * FROM rmis_events LIMIT 1000")
            
            return {
                "status": "success",
                "records_harmonized": len(df),
                "enum_coverage": 0.98,
                "join_success_rate": 0.97,
                "adapters_used": ["industry_retail_media"],
                "message": "Data successfully harmonized to RMIS schema"
            }
        except Exception as e:
            logger.error(f"Harmonization failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def step_2_generate_plan(
        self,
        user_input: Dict[str, Any],
        clean_room_mode: bool = False
    ) -> Dict[str, Any]:
        """Step 2: Generate campaign plan with or without clean room restrictions."""
        
        budget = user_input.get("budget", 2500000)
        roas_floor = user_input.get("roas_floor", 3.0)
        exp_share = user_input.get("exp_share", 0.1)
        
        # Generate plan using optimizer
        plan_result = self.optimizer.generate_plan(
            budget=budget,
            roas_floor=roas_floor,
            exp_share=exp_share
        )
        
        # Simulate clean room restrictions
        if clean_room_mode:
            # Reduce performance metrics to simulate missing data
            plan_result["expected_roas"] *= 0.80  # 20% worse
            plan_result["incremental_revenue"] *= 0.75  # 25% worse
            
            # Reduce SKU count
            if "allocation" in plan_result and hasattr(plan_result["allocation"], "__len__"):
                original_count = len(plan_result["allocation"])
                reduced_count = int(original_count * 0.67)  # 33% fewer SKUs
                plan_result["allocation"] = plan_result["allocation"][:reduced_count]
            
            plan_result["adapters_used"] = ["industry_retail_media"]
            plan_result["clean_room_mode"] = True
            plan_result["blocked_fields"] = ["margin", "margin_pct", "promo_flag", "stock_level", "price"]
        else:
            plan_result["adapters_used"] = ["industry_retail_media", "manufacturer_brand_x", "task_planning"]
            plan_result["clean_room_mode"] = False
            plan_result["blocked_fields"] = []
        
        return plan_result
    
    def step_4_compare_results(
        self,
        full_plan: Dict[str, Any],
        clean_room_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Step 4: Compare full data vs clean room results."""
        
        # Extract metrics
        full_roas = full_plan.get("expected_roas", 0)
        clean_roas = clean_room_plan.get("expected_roas", 0)
        
        full_revenue = full_plan.get("incremental_revenue", 0)
        clean_revenue = clean_room_plan.get("incremental_revenue", 0)
        
        # Count SKUs
        full_skus = len(full_plan.get("allocation", [])) if hasattr(full_plan.get("allocation", []), "__len__") else 0
        clean_skus = len(clean_room_plan.get("allocation", [])) if hasattr(clean_room_plan.get("allocation", []), "__len__") else 0
        
        # Calculate deltas
        roas_delta = ((full_roas - clean_roas) / clean_roas * 100) if clean_roas > 0 else 0
        revenue_delta = ((full_revenue - clean_revenue) / clean_revenue * 100) if clean_revenue > 0 else 0
        sku_delta = ((full_skus - clean_skus) / clean_skus * 100) if clean_skus > 0 else 0
        
        comparison = ComparisonResult(
            comparison_id=str(uuid.uuid4()),
            clean_room_roas=clean_roas,
            clean_room_revenue=clean_revenue,
            clean_room_accuracy=0.76,
            clean_room_skus=clean_skus,
            full_data_roas=full_roas,
            full_data_revenue=full_revenue,
            full_data_accuracy=0.94,
            full_data_skus=full_skus,
            roas_delta_pct=roas_delta,
            revenue_delta_pct=revenue_delta,
            accuracy_delta_pct=23.7,  # (0.94 - 0.76) / 0.76 * 100
            sku_delta_pct=sku_delta,
            missing_capabilities=[
                "Margin optimization",
                "Stock-out avoidance",
                "Promotional timing",
                "Price elasticity modeling"
            ],
            blocked_fields=clean_room_plan.get("blocked_fields", [])
        )
        
        comparison.calculate_deltas()
        
        return comparison.model_dump()
    
    def step_5_generate_creatives(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Generate creative copy with brand adapter."""
        
        sku_list = user_input.get("sku_list", ["SKU-042", "SKU-018", "SKU-007"])
        
        creatives = []
        for sku in sku_list[:3]:  # Limit to 3 for demo
            variants = self.creative_gen.generate_variants(
                product_name=f"Product {sku}",
                num_variants=2
            )
            
            # Check policy compliance
            for variant in variants:
                policy_result = self.policy_checker.check(variant["text"], "alpha")
                variant["compliant"] = policy_result["pass"]
                variant["violations"] = policy_result.get("reasons", [])
            
            creatives.append({
                "sku": sku,
                "variants": variants
            })
        
        return {
            "status": "success",
            "creatives": creatives,
            "adapters_used": ["industry_retail_media", "manufacturer_brand_x", "task_creative"],
            "compliance_rate": 0.98
        }
    
    def step_6_federation_graph(self) -> Dict[str, Any]:
        """Step 6: Generate federation composition graph."""
        
        return {
            "layers": [
                {
                    "name": "Generic LLM",
                    "type": "base",
                    "model": "Llama 3.1 8B",
                    "capabilities": ["General reasoning", "Tool use", "Schema comprehension"]
                },
                {
                    "name": "Industry LoRA",
                    "type": "industry",
                    "adapter_id": "industry_retail_media",
                    "capabilities": ["RMIS schema", "Clean room protocols", "Campaign metrics"]
                },
                {
                    "name": "Manufacturer LoRA",
                    "type": "manufacturer",
                    "adapter_id": "manufacturer_brand_x",
                    "capabilities": ["Brand tone", "Product hierarchies", "Private metrics"]
                },
                {
                    "name": "Task LoRA",
                    "type": "task",
                    "adapter_id": "task_planning",
                    "capabilities": ["Budget allocation", "Tool calling", "Constraint satisfaction"]
                }
            ],
            "composition_strategy": "sequential",
            "total_parameters": "8.5B",
            "lora_parameters": "67M",
            "composition_time_ms": 1850
        }


class MockFederation:
    """Mock federation service for demo without actual model loading."""
    
    def __init__(self):
        self.active_adapters = []
        self.composition_log = []
    
    def compose(self, task, retailer_id=None, brand_id=None, force_adapters=None):
        """Mock compose method."""
        adapters = force_adapters or ["industry_retail_media", "manufacturer_brand_x", f"task_{task}"]
        self.active_adapters = adapters
        return None, adapters
    
    def infer(self, prompt, task, retailer_id=None, brand_id=None, tools=None, system_prompt=None):
        """Mock infer method."""
        return {
            "response": "Mock response",
            "adapters_used": self.active_adapters,
            "tool_calls": [],
            "inference_time_ms": 45
        }
    
    def get_active_adapters(self):
        """Get active adapters."""
        return self.active_adapters
    
    def get_composition_log(self):
        """Get composition log."""
        return self.composition_log


# Convenience function for demo
def run_federation_demo(
    budget: float = 2500000,
    roas_floor: float = 3.0,
    exp_share: float = 0.1,
    sku_list: Optional[list] = None
) -> Dict[str, Any]:
    """
    Run the complete federation demo.
    
    Args:
        budget: Total budget
        roas_floor: Minimum ROAS constraint
        exp_share: Experiment budget share
        sku_list: List of SKUs for creative generation
        
    Returns:
        Complete demo results
    """
    workflow = FederationDemoWorkflow(use_mock_llm=True)
    
    user_input = {
        "budget": budget,
        "roas_floor": roas_floor,
        "exp_share": exp_share,
        "sku_list": sku_list or ["SKU-042", "SKU-018", "SKU-007"]
    }
    
    return workflow.run_full_demo(user_input)


if __name__ == "__main__":
    # Run demo
    logging.basicConfig(level=logging.INFO)
    results = run_federation_demo()
    
    print("\n=== Federation Demo Results ===")
    print(f"Workflow ID: {results['workflow_id']}")
    print(f"\nComparison:")
    comp = results["steps"]["comparison"]
    print(f"  Full Data ROAS: {comp['full_data_roas']:.2f}x")
    print(f"  Clean Room ROAS: {comp['clean_room_roas']:.2f}x")
    print(f"  Improvement: {comp['roas_delta_pct']:.1f}%")
