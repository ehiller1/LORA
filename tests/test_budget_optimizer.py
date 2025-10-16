"""Tests for Budget Optimizer Agent."""

import pytest
import numpy as np
from src.agents.budget_optimizer import (
    BudgetOptimizerAgent,
    ContextualBanditOptimizer,
    ConvexOptimizer,
    AllocationCandidate,
)
from src.schemas.tools import (
    AllocateBudgetInput,
    BudgetPrior,
    BudgetConstraints,
)


@pytest.fixture
def sample_priors():
    """Sample budget priors for testing."""
    return [
        BudgetPrior(
            rmn="retailer_A",
            placement_type="sponsored_product",
            expected_incremental_roas=3.2,
            margin_pct=0.25,
            oos_probability=0.05,
            historical_spend=50000
        ),
        BudgetPrior(
            rmn="retailer_B",
            placement_type="onsite_display",
            expected_incremental_roas=3.5,
            margin_pct=0.30,
            oos_probability=0.03,
            historical_spend=30000
        ),
        BudgetPrior(
            rmn="retailer_C",
            placement_type="offsite_display",
            expected_incremental_roas=2.8,
            margin_pct=0.20,
            oos_probability=0.10,
            historical_spend=20000
        ),
    ]


@pytest.fixture
def sample_constraints():
    """Sample budget constraints for testing."""
    return BudgetConstraints(
        min_roas=3.0,
        reserve_for_experiments=0.1,
        oos_prob_threshold=0.15
    )


def test_budget_optimizer_initialization():
    """Test budget optimizer initialization."""
    agent = BudgetOptimizerAgent(method="convex")
    assert agent.method == "convex"
    assert agent.bandit is None
    
    agent_bandit = BudgetOptimizerAgent(method="bandit")
    assert agent_bandit.method == "bandit"
    assert agent_bandit.bandit is not None


def test_budget_allocation_convex(sample_priors, sample_constraints):
    """Test budget allocation using convex optimization."""
    agent = BudgetOptimizerAgent(method="convex")
    
    input_data = AllocateBudgetInput(
        total_budget=2500000,
        hierarchy=["rmn", "placement"],
        priors=sample_priors,
        constraints=sample_constraints,
        objective="maximize_incremental_margin"
    )
    
    output = agent.allocate(input_data)
    
    # Check output structure
    assert output.total_allocated > 0
    assert output.experiment_budget > 0
    assert len(output.allocations) > 0
    assert len(output.rationale) > 0
    
    # Check budget constraint
    total = output.total_allocated + output.experiment_budget
    assert abs(total - input_data.total_budget) < 1.0  # Allow small rounding error
    
    # Check experiment reserve
    expected_experiment = input_data.total_budget * sample_constraints.reserve_for_experiments
    assert abs(output.experiment_budget - expected_experiment) < 1.0


def test_budget_allocation_bandit(sample_priors, sample_constraints):
    """Test budget allocation using contextual bandit."""
    agent = BudgetOptimizerAgent(method="bandit")
    
    input_data = AllocateBudgetInput(
        total_budget=1000000,
        hierarchy=["rmn", "placement"],
        priors=sample_priors,
        constraints=sample_constraints,
        objective="maximize_incremental_margin"
    )
    
    output = agent.allocate(input_data)
    
    # Check output structure
    assert output.total_allocated > 0
    assert len(output.allocations) > 0


def test_constraint_satisfaction(sample_priors):
    """Test constraint satisfaction checking."""
    agent = BudgetOptimizerAgent(method="convex")
    
    constraints = BudgetConstraints(
        min_roas=3.0,
        max_cpa=0.5,
        reserve_for_experiments=0.1
    )
    
    input_data = AllocateBudgetInput(
        total_budget=1000000,
        hierarchy=["rmn", "placement"],
        priors=sample_priors,
        constraints=constraints,
        objective="maximize_incremental_margin"
    )
    
    output = agent.allocate(input_data)
    
    # Check constraints satisfaction
    assert "min_roas" in output.constraints_satisfaction
    assert "reserve_for_experiments" in output.constraints_satisfaction


def test_oos_filtering(sample_priors):
    """Test OOS probability filtering."""
    agent = BudgetOptimizerAgent(method="convex")
    
    # Set strict OOS threshold
    constraints = BudgetConstraints(
        oos_prob_threshold=0.05,  # Will exclude retailer_C (0.10)
        reserve_for_experiments=0.1
    )
    
    input_data = AllocateBudgetInput(
        total_budget=1000000,
        hierarchy=["rmn", "placement"],
        priors=sample_priors,
        constraints=constraints,
        objective="maximize_incremental_margin"
    )
    
    output = agent.allocate(input_data)
    
    # Check that high OOS retailer is excluded or has zero budget
    retailer_c_allocs = [a for a in output.allocations if a.rmn == "retailer_C"]
    if retailer_c_allocs:
        assert all(a.budget < 1.0 for a in retailer_c_allocs)


def test_contextual_bandit_update():
    """Test contextual bandit update mechanism."""
    bandit = ContextualBanditOptimizer()
    
    arm_id = "retailer_A_sponsored_product"
    
    # Initial state
    assert arm_id not in bandit.arm_stats
    
    # Update with success
    bandit.update(arm_id, 0.8)
    assert arm_id in bandit.arm_stats
    assert bandit.arm_stats[arm_id]["alpha"] > 1.0
    
    # Update with failure
    bandit.update(arm_id, 0.2)
    assert bandit.arm_stats[arm_id]["beta"] > 1.0


def test_convex_optimizer_fallback():
    """Test convex optimizer fallback mechanism."""
    candidates = [
        AllocationCandidate(
            rmn="retailer_A",
            placement_type="sponsored_product",
            audience_id=None,
            sku_id=None,
            expected_incremental_roas=3.0,
            margin_pct=0.25,
            oos_probability=0.05,
            historical_spend=10000
        )
    ]
    
    # Test with impossible constraints (should fallback)
    allocations = ConvexOptimizer.optimize(
        candidates,
        total_budget=1000000,
        constraints={"min_roas": 10.0},  # Impossible constraint
        objective="maximize_incremental_margin"
    )
    
    # Should still return allocations via fallback
    assert len(allocations) > 0


def test_rationale_generation(sample_priors, sample_constraints):
    """Test rationale generation."""
    agent = BudgetOptimizerAgent(method="convex")
    
    input_data = AllocateBudgetInput(
        total_budget=1000000,
        hierarchy=["rmn", "placement"],
        priors=sample_priors,
        constraints=sample_constraints,
        objective="maximize_incremental_margin"
    )
    
    output = agent.allocate(input_data)
    
    # Check rationale exists and is meaningful
    assert len(output.rationale) > 0
    assert any("incremental" in r.lower() for r in output.rationale)


def test_zero_budget():
    """Test handling of zero budget."""
    agent = BudgetOptimizerAgent(method="convex")
    
    input_data = AllocateBudgetInput(
        total_budget=0,
        hierarchy=["rmn"],
        priors=[],
        constraints=BudgetConstraints(),
        objective="maximize_incremental_margin"
    )
    
    # Should handle gracefully
    output = agent.allocate(input_data)
    assert output.total_allocated == 0


def test_empty_priors():
    """Test handling of empty priors."""
    agent = BudgetOptimizerAgent(method="convex")
    
    input_data = AllocateBudgetInput(
        total_budget=1000000,
        hierarchy=["rmn"],
        priors=[],
        constraints=BudgetConstraints(),
        objective="maximize_incremental_margin"
    )
    
    output = agent.allocate(input_data)
    
    # Should return empty allocations
    assert len(output.allocations) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
