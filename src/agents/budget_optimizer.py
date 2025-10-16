"""Budget Optimizer Agent - Allocates budget using contextual bandits and optimization."""

import logging
import numpy as np
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import cvxpy as cp

from ..schemas.tools import (
    AllocateBudgetInput,
    AllocateBudgetOutput,
    BudgetAllocation,
    BudgetPrior,
)

logger = logging.getLogger(__name__)


@dataclass
class AllocationCandidate:
    """Candidate for budget allocation."""
    rmn: str
    placement_type: str
    audience_id: Optional[str]
    sku_id: Optional[str]
    expected_incremental_roas: float
    margin_pct: float
    oos_probability: float
    historical_spend: float = 0.0
    confidence: float = 1.0


class ContextualBanditOptimizer:
    """Contextual bandit for budget allocation with Thompson Sampling."""
    
    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        """Initialize contextual bandit.
        
        Args:
            alpha: Prior alpha for Beta distribution
            beta: Prior beta for Beta distribution
        """
        self.alpha = alpha
        self.beta = beta
        self.arm_stats: Dict[str, Dict[str, float]] = {}
    
    def select_allocation(
        self,
        candidates: List[AllocationCandidate],
        budget: float,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Select budget allocation using Thompson Sampling.
        
        Args:
            candidates: List of allocation candidates
            budget: Total budget to allocate
            constraints: Allocation constraints
            
        Returns:
            List of allocations
        """
        # Sample from posterior for each candidate
        samples = []
        for candidate in candidates:
            arm_id = f"{candidate.rmn}_{candidate.placement_type}"
            
            # Get or initialize arm statistics
            if arm_id not in self.arm_stats:
                self.arm_stats[arm_id] = {
                    "alpha": self.alpha,
                    "beta": self.beta,
                    "pulls": 0
                }
            
            stats = self.arm_stats[arm_id]
            
            # Sample from Beta distribution
            sampled_success_rate = np.random.beta(stats["alpha"], stats["beta"])
            
            # Adjust by expected ROAS and margin
            expected_value = (
                sampled_success_rate *
                candidate.expected_incremental_roas *
                candidate.margin_pct *
                (1 - candidate.oos_probability)
            )
            
            samples.append({
                "candidate": candidate,
                "expected_value": expected_value,
                "arm_id": arm_id
            })
        
        # Sort by expected value
        samples.sort(key=lambda x: x["expected_value"], reverse=True)
        
        # Allocate budget proportionally to expected value
        total_value = sum(s["expected_value"] for s in samples)
        
        allocations = []
        remaining_budget = budget
        
        for sample in samples:
            if remaining_budget <= 0:
                break
            
            candidate = sample["candidate"]
            
            # Proportional allocation
            allocation_pct = sample["expected_value"] / total_value if total_value > 0 else 0
            allocated_budget = min(budget * allocation_pct, remaining_budget)
            
            # Apply minimum budget constraints
            min_budget = constraints.get("min_share_by_rmn", {}).get(candidate.rmn, 0)
            allocated_budget = max(allocated_budget, min_budget)
            
            allocations.append({
                "rmn": candidate.rmn,
                "placement_type": candidate.placement_type,
                "audience_id": candidate.audience_id,
                "sku_id": candidate.sku_id,
                "budget": allocated_budget,
                "expected_incremental_roas": candidate.expected_incremental_roas,
                "expected_incremental_margin": allocated_budget * candidate.expected_incremental_roas * candidate.margin_pct
            })
            
            remaining_budget -= allocated_budget
        
        return allocations
    
    def update(self, arm_id: str, reward: float) -> None:
        """Update arm statistics with observed reward.
        
        Args:
            arm_id: Arm identifier
            reward: Observed reward (0-1)
        """
        if arm_id not in self.arm_stats:
            self.arm_stats[arm_id] = {
                "alpha": self.alpha,
                "beta": self.beta,
                "pulls": 0
            }
        
        stats = self.arm_stats[arm_id]
        
        # Update Beta distribution parameters
        if reward > 0.5:  # Success
            stats["alpha"] += 1
        else:  # Failure
            stats["beta"] += 1
        
        stats["pulls"] += 1


class ConvexOptimizer:
    """Convex optimization for budget allocation with constraints."""
    
    @staticmethod
    def optimize(
        candidates: List[AllocationCandidate],
        total_budget: float,
        constraints: Dict[str, Any],
        objective: str = "maximize_incremental_margin"
    ) -> List[Dict[str, Any]]:
        """Optimize budget allocation using convex optimization.
        
        Args:
            candidates: List of allocation candidates
            total_budget: Total budget to allocate
            constraints: Allocation constraints
            objective: Optimization objective
            
        Returns:
            Optimal allocations
        """
        n = len(candidates)
        
        # Decision variables: budget allocation for each candidate
        x = cp.Variable(n, nonneg=True)
        
        # Objective: maximize incremental margin or revenue
        if objective == "maximize_incremental_margin":
            objective_coeffs = np.array([
                c.expected_incremental_roas * c.margin_pct * (1 - c.oos_probability)
                for c in candidates
            ])
        else:  # maximize_incremental_revenue
            objective_coeffs = np.array([
                c.expected_incremental_roas * (1 - c.oos_probability)
                for c in candidates
            ])
        
        objective_fn = cp.Maximize(objective_coeffs @ x)
        
        # Constraints
        constraint_list = []
        
        # Budget constraint
        constraint_list.append(cp.sum(x) <= total_budget)
        
        # ROAS constraint
        min_roas = constraints.get("min_roas")
        if min_roas:
            roas_coeffs = np.array([c.expected_incremental_roas for c in candidates])
            constraint_list.append(roas_coeffs @ x >= min_roas * cp.sum(x))
        
        # CPA constraint (simplified)
        max_cpa = constraints.get("max_cpa")
        if max_cpa:
            # Inverse ROAS constraint
            min_roas_for_cpa = 1.0 / max_cpa if max_cpa > 0 else 0
            roas_coeffs = np.array([c.expected_incremental_roas for c in candidates])
            constraint_list.append(roas_coeffs @ x >= min_roas_for_cpa * cp.sum(x))
        
        # OOS probability threshold
        oos_threshold = constraints.get("oos_prob_threshold", 0.1)
        for i, candidate in enumerate(candidates):
            if candidate.oos_probability > oos_threshold:
                constraint_list.append(x[i] == 0)
        
        # Exclude SKUs
        exclude_skus = constraints.get("exclude_skus", [])
        for i, candidate in enumerate(candidates):
            if candidate.sku_id in exclude_skus:
                constraint_list.append(x[i] == 0)
        
        # Budget caps
        budget_caps = constraints.get("budget_caps", [])
        for cap in budget_caps:
            scope = cap.get("scope")
            cap_id = cap.get("id")
            max_budget = cap.get("max_budget")
            
            # Find matching candidates
            matching_indices = []
            for i, candidate in enumerate(candidates):
                if scope == "rmn" and candidate.rmn == cap_id:
                    matching_indices.append(i)
                elif scope == "placement" and candidate.placement_type == cap_id:
                    matching_indices.append(i)
            
            if matching_indices:
                constraint_list.append(cp.sum([x[i] for i in matching_indices]) <= max_budget)
        
        # Solve
        problem = cp.Problem(objective_fn, constraint_list)
        
        try:
            problem.solve(solver=cp.ECOS)
            
            if problem.status not in ["optimal", "optimal_inaccurate"]:
                logger.warning(f"Optimization status: {problem.status}")
                # Fallback to simple proportional allocation
                return ConvexOptimizer._fallback_allocation(candidates, total_budget, constraints)
            
            # Build allocations from solution
            allocations = []
            for i, candidate in enumerate(candidates):
                allocated_budget = x.value[i]
                
                if allocated_budget > 1.0:  # Threshold for inclusion
                    allocations.append({
                        "rmn": candidate.rmn,
                        "placement_type": candidate.placement_type,
                        "audience_id": candidate.audience_id,
                        "sku_id": candidate.sku_id,
                        "budget": float(allocated_budget),
                        "expected_incremental_roas": candidate.expected_incremental_roas,
                        "expected_incremental_revenue": float(allocated_budget * candidate.expected_incremental_roas),
                        "expected_incremental_margin": float(
                            allocated_budget * candidate.expected_incremental_roas * candidate.margin_pct
                        )
                    })
            
            return allocations
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            return ConvexOptimizer._fallback_allocation(candidates, total_budget, constraints)
    
    @staticmethod
    def _fallback_allocation(
        candidates: List[AllocationCandidate],
        total_budget: float,
        constraints: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Fallback to simple proportional allocation."""
        # Sort by expected value
        scored_candidates = [
            (c, c.expected_incremental_roas * c.margin_pct * (1 - c.oos_probability))
            for c in candidates
        ]
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Allocate proportionally
        total_score = sum(score for _, score in scored_candidates)
        
        allocations = []
        for candidate, score in scored_candidates:
            allocated_budget = (score / total_score) * total_budget if total_score > 0 else 0
            
            if allocated_budget > 1.0:
                allocations.append({
                    "rmn": candidate.rmn,
                    "placement_type": candidate.placement_type,
                    "audience_id": candidate.audience_id,
                    "sku_id": candidate.sku_id,
                    "budget": allocated_budget,
                    "expected_incremental_roas": candidate.expected_incremental_roas
                })
        
        return allocations


class BudgetOptimizerAgent:
    """Agent for optimizing budget allocation."""
    
    def __init__(self, method: str = "convex"):
        """Initialize Budget Optimizer Agent.
        
        Args:
            method: Optimization method ('convex' or 'bandit')
        """
        self.method = method
        self.bandit = ContextualBanditOptimizer() if method == "bandit" else None
        logger.info(f"Budget Optimizer initialized with method: {method}")
    
    def allocate(self, input_data: AllocateBudgetInput) -> AllocateBudgetOutput:
        """Allocate budget based on input specification.
        
        Args:
            input_data: Budget allocation input
            
        Returns:
            Budget allocation output
        """
        logger.info(f"Allocating budget: ${input_data.total_budget:,.2f}")
        
        # Convert priors to candidates
        candidates = [
            AllocationCandidate(
                rmn=prior.rmn,
                placement_type=prior.placement_type,
                audience_id=prior.audience_id,
                sku_id=prior.sku_id,
                expected_incremental_roas=prior.expected_incremental_roas,
                margin_pct=prior.margin_pct,
                oos_probability=prior.oos_probability,
                historical_spend=prior.historical_spend or 0.0
            )
            for prior in input_data.priors
        ]
        
        # Reserve budget for experiments
        experiment_budget = input_data.total_budget * input_data.constraints.reserve_for_experiments
        allocation_budget = input_data.total_budget - experiment_budget
        
        # Optimize allocation
        if self.method == "convex":
            allocations = ConvexOptimizer.optimize(
                candidates,
                allocation_budget,
                input_data.constraints.model_dump(),
                input_data.objective
            )
        else:  # bandit
            allocations = self.bandit.select_allocation(
                candidates,
                allocation_budget,
                input_data.constraints.model_dump()
            )
        
        # Build output
        budget_allocations = [BudgetAllocation(**alloc) for alloc in allocations]
        
        total_allocated = sum(alloc.budget for alloc in budget_allocations)
        
        # Calculate expected ROAS
        if total_allocated > 0:
            expected_roas = sum(
                alloc.budget * alloc.expected_incremental_roas
                for alloc in budget_allocations
            ) / total_allocated
        else:
            expected_roas = 0.0
        
        # Generate rationale
        rationale = self._generate_rationale(
            budget_allocations,
            input_data.constraints,
            input_data.objective
        )
        
        # Check constraint satisfaction
        constraints_satisfaction = self._check_constraints(
            budget_allocations,
            input_data.constraints
        )
        
        return AllocateBudgetOutput(
            allocations=budget_allocations,
            total_allocated=total_allocated,
            experiment_budget=experiment_budget,
            constraints_satisfaction=constraints_satisfaction,
            rationale=rationale,
            expected_total_incremental_roas=expected_roas,
            monitoring_plan={
                "pacing_checks": "daily",
                "reoptimization_cadence": "weekly",
                "kpis": ["incremental_roas", "spend_pacing", "oos_rate"]
            }
        )
    
    def _generate_rationale(
        self,
        allocations: List[BudgetAllocation],
        constraints: Any,
        objective: str
    ) -> List[str]:
        """Generate human-readable rationale for allocations."""
        rationale = []
        
        # Top allocations
        sorted_allocs = sorted(allocations, key=lambda x: x.budget, reverse=True)
        for i, alloc in enumerate(sorted_allocs[:3]):
            pct = (alloc.budget / sum(a.budget for a in allocations)) * 100
            rationale.append(
                f"Allocated {pct:.1f}% (${alloc.budget:,.0f}) to {alloc.rmn} {alloc.placement_type} "
                f"due to expected incremental ROAS of {alloc.expected_incremental_roas:.2f}"
            )
        
        # Objective
        if objective == "maximize_incremental_margin":
            rationale.append("Optimized for incremental margin considering product margins and stock availability")
        else:
            rationale.append("Optimized for incremental revenue")
        
        # Constraints
        if constraints.reserve_for_experiments > 0:
            rationale.append(f"Reserved {constraints.reserve_for_experiments*100:.0f}% for experimentation")
        
        return rationale
    
    def _check_constraints(
        self,
        allocations: List[BudgetAllocation],
        constraints: Any
    ) -> Dict[str, bool]:
        """Check if allocations satisfy constraints."""
        satisfaction = {}
        
        total_budget = sum(alloc.budget for alloc in allocations)
        
        # ROAS constraint
        if constraints.min_roas:
            avg_roas = sum(
                alloc.budget * alloc.expected_incremental_roas
                for alloc in allocations
            ) / total_budget if total_budget > 0 else 0
            satisfaction["min_roas"] = avg_roas >= constraints.min_roas
        
        # Experiment reserve
        satisfaction["reserve_for_experiments"] = True  # Handled in allocation
        
        return satisfaction


def main():
    """CLI entry point for Budget Optimizer Agent."""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="Budget Optimizer Agent")
    parser.add_argument("--method", choices=["convex", "bandit"], default="convex", help="Optimization method")
    parser.add_argument("--input", type=Path, required=True, help="Input JSON file")
    parser.add_argument("--output", type=Path, help="Output JSON file")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Load input
    with open(args.input, 'r') as f:
        input_dict = json.load(f)
    
    input_data = AllocateBudgetInput(**input_dict)
    
    # Run optimization
    agent = BudgetOptimizerAgent(method=args.method)
    output = agent.allocate(input_data)
    
    # Print results
    print("\n=== Budget Allocation ===")
    print(f"Total Allocated: ${output.total_allocated:,.2f}")
    print(f"Experiment Budget: ${output.experiment_budget:,.2f}")
    print(f"Expected ROAS: {output.expected_total_incremental_roas:.2f}")
    print("\nAllocations:")
    for alloc in output.allocations:
        print(f"  {alloc.rmn} {alloc.placement_type}: ${alloc.budget:,.2f} (ROAS: {alloc.expected_incremental_roas:.2f})")
    
    print("\nRationale:")
    for reason in output.rationale:
        print(f"  - {reason}")
    
    # Save output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output.model_dump(), f, indent=2)
        print(f"\nOutput saved to {args.output}")


if __name__ == "__main__":
    from pathlib import Path
    main()
