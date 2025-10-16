"""Example workflow demonstrating the RMN LoRA system."""

import logging
from pathlib import Path
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def example_data_harmonization():
    """Example: Harmonize retailer data to RMIS."""
    from src.agents.data_harmonizer import DataHarmonizerAgent
    
    logger.info("=== Example: Data Harmonization ===")
    
    # Initialize agent with retailer mapping
    mapping_path = Path("config/mappings/retailer_ABC.yaml")
    agent = DataHarmonizerAgent(mapping_path)
    
    # Note: In a real scenario, you would have actual data files
    # For this example, we'll just show the structure
    
    logger.info("Agent initialized with retailer_ABC mapping")
    logger.info("To harmonize data, run:")
    logger.info("  python -m src.agents.data_harmonizer \\")
    logger.info("    --retailer-mapping config/mappings/retailer_ABC.yaml \\")
    logger.info("    --input data/raw/retailer_ABC_export.parquet \\")
    logger.info("    --output data/harmonized/rmis_events.parquet")


def example_budget_optimization():
    """Example: Optimize budget allocation."""
    from src.agents.budget_optimizer import BudgetOptimizerAgent
    from src.schemas.tools import (
        AllocateBudgetInput,
        BudgetPrior,
        BudgetConstraints,
    )
    
    logger.info("\n=== Example: Budget Optimization ===")
    
    # Create sample priors
    priors = [
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
    
    # Create constraints
    constraints = BudgetConstraints(
        min_roas=3.0,
        reserve_for_experiments=0.1,
        oos_prob_threshold=0.15
    )
    
    # Create input
    input_data = AllocateBudgetInput(
        total_budget=2500000,
        hierarchy=["rmn", "placement"],
        priors=priors,
        constraints=constraints,
        objective="maximize_incremental_margin"
    )
    
    # Run optimization
    agent = BudgetOptimizerAgent(method="convex")
    output = agent.allocate(input_data)
    
    logger.info(f"Total Allocated: ${output.total_allocated:,.2f}")
    logger.info(f"Experiment Budget: ${output.experiment_budget:,.2f}")
    logger.info(f"Expected ROAS: {output.expected_total_incremental_roas:.2f}")
    
    logger.info("\nAllocations:")
    for alloc in output.allocations:
        logger.info(
            f"  {alloc.rmn} {alloc.placement_type}: "
            f"${alloc.budget:,.2f} (ROAS: {alloc.expected_incremental_roas:.2f})"
        )
    
    logger.info("\nRationale:")
    for reason in output.rationale:
        logger.info(f"  - {reason}")


def example_experiment_design():
    """Example: Design a lift experiment."""
    from src.agents.measurement import MeasurementAgent
    from src.schemas.tools import DesignExperimentInput
    
    logger.info("\n=== Example: Experiment Design ===")
    
    # Create experiment specification
    input_data = DesignExperimentInput(
        goal="incremental_revenue",
        units="geo",
        power=0.8,
        min_detectable_effect=0.10,  # 10% lift
        duration_weeks=4,
        covariates=["store_size", "historical_sales"]
    )
    
    # Design experiment
    agent = MeasurementAgent()
    output = agent.design_experiment(input_data)
    
    logger.info(f"Design: {output.design}")
    logger.info(f"Sample Size: {output.sample_size}")
    logger.info(f"Duration: {output.expected_runtime_weeks} weeks")
    
    logger.info("\nCells:")
    for cell in output.cells:
        logger.info(f"  {cell.assignment}: {len(cell.units)} units")
    
    logger.info("\nSuccess Criteria:")
    for criterion in output.success_criteria:
        logger.info(f"  - {criterion}")


def example_creative_generation():
    """Example: Generate creative copy."""
    from src.agents.creative import CreativeAgent
    from src.schemas.tools import GenerateCopyInput, RetailerSpecs
    
    logger.info("\n=== Example: Creative Generation ===")
    
    # Create retailer specs
    retailer_specs = RetailerSpecs(
        max_headline_length=50,
        max_body_length=200,
        disallowed_terms=["guaranteed", "miracle"],
        required_disclaimers=["*Terms apply"],
        placement_type="sponsored_product"
    )
    
    # Create input
    input_data = GenerateCopyInput(
        sku_id="SKU12345",
        attributes={
            "name": "Premium Organic Coffee",
            "size": "12 oz",
            "benefits": ["100% Organic", "Fair Trade", "Rich Flavor"],
            "price": 14.99
        },
        retailer_specs=retailer_specs,
        brand_tone="Premium, authentic, environmentally conscious",
        num_variants=3
    )
    
    # Generate copy (without LLM, using templates)
    agent = CreativeAgent()  # No model path = template mode
    output = agent.generate_copy(input_data)
    
    logger.info(f"Generated {len(output.variants)} variants")
    logger.info(f"All Compliant: {output.all_compliant}")
    
    for i, variant in enumerate(output.variants, 1):
        logger.info(f"\nVariant {i} (Compliance: {variant.compliance_score:.2f}):")
        logger.info(f"  Headline: {variant.headline}")
        logger.info(f"  Body: {variant.body}")
        logger.info(f"  CTA: {variant.call_to_action}")


def example_governance_checks():
    """Example: Run governance and PII checks."""
    from src.agents.governance import GovernanceAgent
    
    logger.info("\n=== Example: Governance Checks ===")
    
    agent = GovernanceAgent(min_cell_size=50)
    
    # Check text for PII
    test_text = "Contact us at john.doe@example.com or call 555-123-4567"
    result = agent.check_text(test_text)
    
    logger.info(f"Text Safe: {result['text_safe']}")
    logger.info(f"PII Detected: {result['pii_detected']}")
    
    if result['pii_detected']:
        logger.info(f"PII Types: {', '.join(result['pii_types'])}")
        logger.info(f"Redacted: {result['redacted_text']}")
    
    # Check creative compliance
    creative_text = "Premium Coffee - Best Quality! *Terms apply"
    creative_result = agent.check_creative(
        creative_text,
        disallowed_terms=["guaranteed", "miracle"],
        required_disclaimers=["*Terms apply"],
        placement_type="sponsored_product"
    )
    
    logger.info(f"\nCreative Approved: {creative_result['approved']}")


def example_training_dataset():
    """Example: Build training dataset."""
    from src.training.dataset_builder import DatasetBuilder
    
    logger.info("\n=== Example: Training Dataset Creation ===")
    
    # Create synthetic examples
    examples = DatasetBuilder.create_synthetic_examples(
        example_type="budgeting",
        num_examples=10
    )
    
    logger.info(f"Created {len(examples)} synthetic examples")
    logger.info(f"Example: {json.dumps(examples[0], indent=2)}")
    
    # Save to file
    output_path = Path("data/training/synthetic_budgeting.jsonl")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert to training format
    training_examples = []
    for ex in examples:
        messages = [
            {"role": "system", "content": "You are a budget optimization expert."},
            {"role": "user", "content": ex['objective']},
            {"role": "assistant", "content": json.dumps(ex['tool_call'])}
        ]
        training_examples.append({"messages": messages})
    
    with open(output_path, 'w') as f:
        for ex in training_examples:
            f.write(json.dumps(ex) + '\n')
    
    logger.info(f"Saved training dataset to {output_path}")


def example_planner_workflow():
    """Example: Full planning workflow."""
    logger.info("\n=== Example: Planning Workflow ===")
    
    objective = "Allocate $2.5M across retailers A, B, C to maximize incremental margin with ROAS >= 3.0"
    
    logger.info(f"Objective: {objective}")
    logger.info("\nWorkflow steps:")
    logger.info("1. Planner Agent receives objective")
    logger.info("2. Calls query_clean_room() to fetch performance data")
    logger.info("3. Calls allocate_budget() with constraints")
    logger.info("4. Returns allocation plan with rationale")
    logger.info("5. Optionally calls design_experiment() for holdout testing")
    
    logger.info("\nTo run with actual LLM:")
    logger.info("  python -m src.agents.planner \\")
    logger.info("    --base-model meta-llama/Llama-3.1-8B-Instruct \\")
    logger.info("    --objective 'Allocate $2.5M...' \\")
    logger.info("    --adapters models/adapters/retailer_ABC models/adapters/task_budgeting")


def main():
    """Run all examples."""
    logger.info("=" * 80)
    logger.info("RMN LoRA System - Example Workflows")
    logger.info("=" * 80)
    
    # Run examples
    example_data_harmonization()
    example_budget_optimization()
    example_experiment_design()
    example_creative_generation()
    example_governance_checks()
    example_training_dataset()
    example_planner_workflow()
    
    logger.info("\n" + "=" * 80)
    logger.info("Examples complete!")
    logger.info("=" * 80)
    
    logger.info("\nNext steps:")
    logger.info("1. Prepare your retailer data and create mapping files")
    logger.info("2. Build training datasets for your adapters")
    logger.info("3. Train LoRA adapters using src/training/train_lora.py")
    logger.info("4. Deploy multi-tenant runtime using src/runtime/multi_tenant.py")
    logger.info("5. Integrate with your optimization and measurement services")


if __name__ == "__main__":
    main()
