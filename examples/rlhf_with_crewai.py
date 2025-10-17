#!/usr/bin/env python3
"""Example: Using CrewAI for synthetic RLHF feedback generation.

This example demonstrates how to:
1. Generate synthetic feedback using CrewAI agents
2. Build DPO datasets from synthetic feedback
3. Use multi-agent evaluation for comprehensive quality assessment
"""

import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rlhf import (
    SyntheticFeedbackGenerator,
    DPODatasetBuilder,
    MultiAgentRLHF,
    LangSmithTracer,
    AutomatedRLHFPipeline,
    PipelineConfig
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_1_synthetic_feedback():
    """Example 1: Generate synthetic feedback for a single output."""
    
    print("\n" + "="*70)
    print("EXAMPLE 1: Synthetic Feedback Generation")
    print("="*70 + "\n")
    
    # Create generator
    generator = SyntheticFeedbackGenerator(
        task_type="budgeting",
        enable_langsmith=False  # Set to True if you have LangSmith configured
    )
    
    # Example prompt and output
    prompt = """
Allocate $2.5M quarterly budget across Amazon, Walmart, and Target to maximize
incremental margin with ROAS >= 3.0. Consider Q1 seasonal factors.
    """.strip()
    
    output = """
Budget Allocation Recommendation:

Amazon: $1,200,000 (48%)
- Historical ROAS: 3.8x
- Strong Prime Day performance expected
- 150 active SKUs with proven performance

Walmart: $800,000 (32%)
- Historical ROAS: 3.2x  
- Growing digital presence
- Q1 promotional calendar aligned

Target: $500,000 (20%)
- Historical ROAS: 2.9x (below target but improving)
- Strong brand fit
- Testing new ad formats

Expected Overall ROAS: 3.4x
Projected Incremental Margin: $6.0M
    """.strip()
    
    # Generate feedback
    print("Generating synthetic feedback (this may take a minute)...\n")
    feedback = generator.generate_feedback(prompt, output)
    
    # Display results
    print(f"Overall Rating: {feedback.overall_rating}/5")
    print(f"Is Chosen (for DPO): {'✅ Yes' if feedback.is_chosen else '❌ No'}")
    print(f"\nDimension Ratings:")
    for dim, rating in feedback.dimensions.items():
        print(f"  - {dim}: {rating}/5")
    print(f"\nExplanation (first 300 chars):\n{feedback.explanation[:300]}...")


def example_2_multi_agent_evaluation():
    """Example 2: Multi-agent comprehensive evaluation."""
    
    print("\n" + "="*70)
    print("EXAMPLE 2: Multi-Agent RLHF Evaluation")
    print("="*70 + "\n")
    
    # Create multi-agent system
    rlhf = MultiAgentRLHF(
        task_type="budgeting",
        weights={
            "accuracy": 0.30,
            "brand_alignment": 0.20,
            "compliance": 0.25,
            "clarity": 0.15,
            "actionability": 0.10
        }
    )
    
    # Example evaluation
    prompt = "Allocate $1M for new product launch across 3 retailers"
    output = """
Recommendation:
- Amazon: $600K (60%) - largest reach
- Walmart: $250K (25%) - strong in category
- Target: $150K (15%) - brand alignment

Expected ROAS: 3.2x
    """
    
    context = {
        "brand": "Acme Foods",
        "product": "New Energy Drink",
        "target_audience": "18-35 active lifestyle"
    }
    
    print("Running multi-agent evaluation (this may take a minute)...\n")
    feedback = rlhf.evaluate(prompt, output, context)
    
    # Display results
    print(f"Overall Score: {feedback.overall_score:.1f}/100")
    print(f"Acceptable: {'✅ Yes' if feedback.is_acceptable else '❌ No'}")
    print(f"Confidence: {feedback.confidence:.2f}")
    print(f"\nDimension Scores:")
    print(f"  - Accuracy: {feedback.accuracy_score:.1f}/100")
    print(f"  - Brand Alignment: {feedback.brand_alignment_score:.1f}/100")
    print(f"  - Compliance: {feedback.compliance_score:.1f}/100")
    print(f"  - Clarity: {feedback.clarity_score:.1f}/100")
    print(f"  - Actionability: {feedback.actionability_score:.1f}/100")


def example_3_dpo_dataset_building():
    """Example 3: Build DPO dataset from output variations."""
    
    print("\n" + "="*70)
    print("EXAMPLE 3: DPO Dataset Building")
    print("="*70 + "\n")
    
    # Create generator and DPO builder
    generator = SyntheticFeedbackGenerator(task_type="budgeting")
    dpo_builder = DPODatasetBuilder(generator)
    
    # Example: Multiple outputs for same prompt
    prompt = "Allocate $500K test budget for emerging retailer Instacart"
    
    variations = [
        # Good variation
        """
Instacart Test Allocation: $500K

Strategy: Conservative test with 3-month learning period
- Month 1: $100K (learning phase)
- Month 2: $200K (scale if ROAS > 2.5x)
- Month 3: $200K (optimize top performers)

Focus: High-margin SKUs with proven digital performance
Target ROAS: 2.8x (acceptable for new channel)
        """,
        
        # Bad variation
        """
Put all $500K into Instacart immediately with maximum bids.
        """,
        
        # Medium variation
        """
Instacart: $500K spread evenly over Q1.
Try different products and see what works.
        """
    ]
    
    print("Building DPO example from variations...\n")
    dpo_example = dpo_builder.build_from_variations(prompt, variations)
    
    print(f"Chosen Output (rated {dpo_example['chosen_rating']}/5):")
    print(dpo_example['chosen'][:200] + "...\n")
    
    print(f"Rejected Output (rated {dpo_example['rejected_rating']}/5):")
    print(dpo_example['rejected'][:200] + "...\n")


def example_4_automated_pipeline():
    """Example 4: Run automated RLHF pipeline."""
    
    print("\n" + "="*70)
    print("EXAMPLE 4: Automated RLHF Pipeline")
    print("="*70 + "\n")
    
    # Configuration
    config = PipelineConfig(
        num_synthetic_examples=5,  # Small for demo
        enable_langsmith=False,
        output_dir=Path("models/adapters/demo"),
        dataset_dir=Path("data/rlhf/demo")
    )
    
    # Initialize pipeline
    pipeline = AutomatedRLHFPipeline(config, task_type="budgeting")
    
    # Example prompts
    prompts = [
        "Allocate $2.5M across Amazon, Walmart, Target for Q1",
        "Optimize $1M budget for new product launch",
        "Plan $500K test budget for emerging retailer"
    ]
    
    # Mock inference function (replace with actual model in production)
    def mock_inference(prompt: str) -> str:
        return f"""
Budget Allocation for: {prompt[:50]}...

Amazon: $1.2M (48%)
Walmart: $800K (32%)
Target: $500K (20%)

Expected ROAS: 3.4x
        """
    
    print("Running automated pipeline...\n")
    print("Note: This is a demo with mock inference. In production, use your actual model.\n")
    
    # Run pipeline (this will fail at training step without actual model)
    try:
        results = pipeline.run_full_pipeline(
            prompts=prompts,
            model_inference_fn=mock_inference,
            adapter_name="demo_adapter"
        )
        
        print(f"\n✅ Pipeline Complete!")
        print(f"Adapter: {results['adapter_name']}")
        print(f"Stages completed: {len(results['stages'])}")
        
    except Exception as e:
        print(f"\n⚠️  Pipeline demo stopped at training step (expected without actual model)")
        print(f"Error: {e}")


def example_5_langsmith_integration():
    """Example 5: LangSmith tracing for observability."""
    
    print("\n" + "="*70)
    print("EXAMPLE 5: LangSmith Integration")
    print("="*70 + "\n")
    
    # Initialize tracer
    tracer = LangSmithTracer(project_name="rmn-rlhf-demo")
    
    if tracer.enabled:
        print("✅ LangSmith enabled!")
        
        # Example: Trace feedback collection
        with tracer.trace_feedback_collection(
            user_id="demo_user",
            task_type="budgeting",
            metadata={"brand": "Acme Foods"}
        ):
            print("Collecting feedback (traced to LangSmith)...")
            # Your feedback collection code here
        
        # Get project stats
        stats = tracer.get_project_stats()
        if stats:
            print(f"\nProject Stats:")
            print(f"  Total runs: {stats['total_runs']}")
            print(f"  Tag distribution: {stats['tag_distribution']}")
    else:
        print("⚠️  LangSmith not enabled")
        print("To enable:")
        print("1. Set LANGCHAIN_API_KEY environment variable")
        print("2. pip install langsmith")
        print("3. Re-run this example")


def main():
    """Run all examples."""
    
    print("\n" + "🚀"*35)
    print("CrewAI-Enhanced RLHF Examples")
    print("🚀"*35)
    
    examples = [
        ("1", "Synthetic Feedback Generation", example_1_synthetic_feedback),
        ("2", "Multi-Agent Evaluation", example_2_multi_agent_evaluation),
        ("3", "DPO Dataset Building", example_3_dpo_dataset_building),
        ("4", "Automated Pipeline", example_4_automated_pipeline),
        ("5", "LangSmith Integration", example_5_langsmith_integration)
    ]
    
    print("\nAvailable examples:")
    for num, name, _ in examples:
        print(f"  {num}. {name}")
    print(f"  all. Run all examples")
    print(f"  q. Quit")
    
    choice = input("\nSelect example (1-5, all, or q): ").strip().lower()
    
    if choice == 'q':
        print("Goodbye!")
        return
    
    if choice == 'all':
        for num, name, func in examples:
            try:
                func()
            except KeyboardInterrupt:
                print("\n\nInterrupted by user")
                break
            except Exception as e:
                logger.error(f"Example {num} failed: {e}", exc_info=True)
                continue
    else:
        for num, name, func in examples:
            if choice == num:
                func()
                break
        else:
            print(f"Invalid choice: {choice}")
    
    print("\n" + "="*70)
    print("Examples complete! Check the code in examples/rlhf_with_crewai.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
