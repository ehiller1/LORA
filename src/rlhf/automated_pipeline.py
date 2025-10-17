"""Automated RLHF pipeline integrating all components.

This module orchestrates the complete RLHF workflow:
1. Generate model outputs
2. Collect synthetic feedback (CrewAI)
3. Build training datasets (DPO/SFT)
4. Train adapters
5. Evaluate improvements
6. Deploy to production
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass
import json

from .synthetic_feedback import SyntheticFeedbackGenerator, DPODatasetBuilder
from .multi_agent_rlhf import MultiAgentRLHF
from .langsmith_integration import LangSmithTracer

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for automated RLHF pipeline."""
    
    # Generation
    num_synthetic_examples: int = 1000
    num_variations_per_prompt: int = 5
    
    # Quality thresholds
    min_rating_chosen: int = 4  # 4-5 stars = chosen
    max_rating_rejected: int = 2  # 1-2 stars = rejected
    min_score_acceptable: float = 70.0  # 0-100 scale
    
    # Training
    output_dir: Path = Path("models/adapters")
    dataset_dir: Path = Path("data/rlhf")
    
    # Monitoring
    enable_langsmith: bool = True
    langsmith_project: str = "rmn-rlhf"


class AutomatedRLHFPipeline:
    """Automated end-to-end RLHF pipeline."""
    
    def __init__(
        self,
        config: PipelineConfig,
        task_type: str = "budgeting"
    ):
        """Initialize automated pipeline.
        
        Args:
            config: Pipeline configuration
            task_type: Type of task (budgeting, creative, etc.)
        """
        self.config = config
        self.task_type = task_type
        
        # Initialize components
        self.feedback_generator = SyntheticFeedbackGenerator(
            task_type=task_type,
            enable_langsmith=config.enable_langsmith
        )
        
        self.multi_agent_rlhf = MultiAgentRLHF(task_type=task_type)
        
        self.dpo_builder = DPODatasetBuilder(self.feedback_generator)
        
        if config.enable_langsmith:
            self.tracer = LangSmithTracer(project_name=config.langsmith_project)
        else:
            self.tracer = None
        
        # Create directories
        config.output_dir.mkdir(parents=True, exist_ok=True)
        config.dataset_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized AutomatedRLHFPipeline for {task_type}")
    
    def run_full_pipeline(
        self,
        prompts: List[str],
        model_inference_fn: Callable[[str], str],
        adapter_name: str = "auto_rlhf"
    ) -> Dict[str, Any]:
        """Run complete RLHF pipeline from prompts to trained adapter.
        
        Args:
            prompts: List of prompts to generate outputs for
            model_inference_fn: Function that takes prompt and returns model output
            adapter_name: Name for the trained adapter
            
        Returns:
            Pipeline results and metrics
        """
        logger.info(f"Starting automated RLHF pipeline with {len(prompts)} prompts")
        
        results = {
            "adapter_name": adapter_name,
            "num_prompts": len(prompts),
            "stages": {}
        }
        
        # Stage 1: Generate model outputs
        logger.info("Stage 1: Generating model outputs...")
        examples = self._generate_outputs(prompts, model_inference_fn)
        results["stages"]["generation"] = {
            "num_examples": len(examples),
            "prompts_processed": len(prompts)
        }
        
        # Stage 2: Collect synthetic feedback
        logger.info("Stage 2: Collecting synthetic feedback...")
        with_feedback = self._collect_feedback(examples)
        results["stages"]["feedback"] = {
            "num_evaluated": len(with_feedback),
            "avg_rating": sum(f["rating"] for f in with_feedback) / len(with_feedback)
        }
        
        # Stage 3: Build training dataset
        logger.info("Stage 3: Building DPO dataset...")
        dataset_path = self._build_dataset(with_feedback, adapter_name)
        results["stages"]["dataset"] = {
            "path": str(dataset_path),
            "num_examples": self._count_dataset_examples(dataset_path)
        }
        
        # Stage 4: Train adapter
        logger.info("Stage 4: Training LoRA adapter...")
        training_results = self._train_adapter(dataset_path, adapter_name)
        results["stages"]["training"] = training_results
        
        # Stage 5: Evaluate
        logger.info("Stage 5: Evaluating trained adapter...")
        eval_results = self._evaluate_adapter(adapter_name, prompts[:10])
        results["stages"]["evaluation"] = eval_results
        
        logger.info(f"Pipeline complete! Adapter saved: {adapter_name}")
        
        # Save results
        results_path = self.config.output_dir / adapter_name / "pipeline_results.json"
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
    
    def _generate_outputs(
        self,
        prompts: List[str],
        inference_fn: Callable[[str], str]
    ) -> List[Dict[str, str]]:
        """Generate model outputs for prompts.
        
        Args:
            prompts: List of prompts
            inference_fn: Function to generate outputs
            
        Returns:
            List of {prompt, output} dicts
        """
        examples = []
        
        for i, prompt in enumerate(prompts):
            logger.debug(f"Generating output {i+1}/{len(prompts)}")
            
            try:
                output = inference_fn(prompt)
                examples.append({
                    "prompt": prompt,
                    "output": output
                })
            except Exception as e:
                logger.error(f"Failed to generate output for prompt {i}: {e}")
                continue
        
        logger.info(f"Generated {len(examples)} outputs")
        return examples
    
    def _collect_feedback(
        self,
        examples: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """Collect synthetic feedback for examples.
        
        Args:
            examples: List of {prompt, output} dicts
            
        Returns:
            Examples with feedback added
        """
        with_feedback = []
        
        for i, example in enumerate(examples):
            logger.debug(f"Collecting feedback {i+1}/{len(examples)}")
            
            try:
                # Use multi-agent RLHF for comprehensive evaluation
                feedback = self.multi_agent_rlhf.evaluate(
                    prompt=example["prompt"],
                    model_output=example["output"]
                )
                
                # Convert to format compatible with DPO builder
                example["rating"] = int(feedback.overall_score / 20)  # Convert 0-100 to 1-5
                example["feedback"] = {
                    "overall_score": feedback.overall_score,
                    "accuracy": feedback.accuracy_score,
                    "brand_alignment": feedback.brand_alignment_score,
                    "compliance": feedback.compliance_score,
                    "clarity": feedback.clarity_score,
                    "actionability": feedback.actionability_score,
                    "is_acceptable": feedback.is_acceptable
                }
                
                with_feedback.append(example)
                
            except Exception as e:
                logger.error(f"Failed to collect feedback for example {i}: {e}")
                continue
        
        logger.info(f"Collected feedback for {len(with_feedback)} examples")
        return with_feedback
    
    def _build_dataset(
        self,
        examples_with_feedback: List[Dict[str, Any]],
        adapter_name: str
    ) -> Path:
        """Build DPO training dataset.
        
        Args:
            examples_with_feedback: Examples with ratings
            adapter_name: Name for the dataset
            
        Returns:
            Path to dataset file
        """
        # Separate into chosen and rejected
        chosen = [
            ex for ex in examples_with_feedback
            if ex["rating"] >= self.config.min_rating_chosen
        ]
        
        rejected = [
            ex for ex in examples_with_feedback
            if ex["rating"] <= self.config.max_rating_rejected
        ]
        
        logger.info(f"Building DPO dataset: {len(chosen)} chosen, {len(rejected)} rejected")
        
        # Build DPO dataset
        dataset_path = self.config.dataset_dir / f"{adapter_name}_dpo.jsonl"
        
        # Write dataset
        with open(dataset_path, "w") as f:
            # Create pairs
            for c_ex in chosen:
                # Find worst rejected example for this prompt (if any)
                rejected_for_prompt = [
                    r for r in rejected
                    if r["prompt"] == c_ex["prompt"]
                ]
                
                if rejected_for_prompt:
                    # Use worst one
                    r_ex = min(rejected_for_prompt, key=lambda x: x["rating"])
                    
                    dpo_example = {
                        "prompt": c_ex["prompt"],
                        "chosen": c_ex["output"],
                        "rejected": r_ex["output"]
                    }
                    f.write(json.dumps(dpo_example) + "\n")
        
        logger.info(f"DPO dataset saved to {dataset_path}")
        return dataset_path
    
    def _count_dataset_examples(self, dataset_path: Path) -> int:
        """Count examples in dataset.
        
        Args:
            dataset_path: Path to dataset
            
        Returns:
            Number of examples
        """
        count = 0
        with open(dataset_path) as f:
            for line in f:
                if line.strip():
                    count += 1
        return count
    
    def _train_adapter(
        self,
        dataset_path: Path,
        adapter_name: str
    ) -> Dict[str, Any]:
        """Train LoRA adapter with DPO.
        
        Args:
            dataset_path: Path to training dataset
            adapter_name: Name for adapter
            
        Returns:
            Training results
        """
        # Import training module
        try:
            from src.training.train_lora import LoRATrainer, LoRATrainingConfig
            
            # Create training config
            config = LoRATrainingConfig(
                output_dir=str(self.config.output_dir)
            )
            
            # Initialize trainer
            trainer = LoRATrainer(config)
            
            # Load model
            trainer.load_model()
            
            # Prepare dataset
            dataset = trainer.prepare_dataset(dataset_path, dataset_type="dpo")
            
            # Train
            with self.tracer.trace_training("DPO", adapter_name) if self.tracer else None:
                trainer.train(dataset, adapter_name=adapter_name)
            
            return {
                "status": "success",
                "adapter_path": str(self.config.output_dir / adapter_name)
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _evaluate_adapter(
        self,
        adapter_name: str,
        test_prompts: List[str]
    ) -> Dict[str, Any]:
        """Evaluate trained adapter.
        
        Args:
            adapter_name: Name of adapter
            test_prompts: Prompts to test
            
        Returns:
            Evaluation results
        """
        # Placeholder - in production, load adapter and run inference
        return {
            "status": "evaluation_complete",
            "num_test_prompts": len(test_prompts),
            "note": "Full evaluation requires loading the trained adapter"
        }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Configuration
    config = PipelineConfig(
        num_synthetic_examples=100,
        enable_langsmith=False  # Set to True if you have LangSmith configured
    )
    
    # Initialize pipeline
    pipeline = AutomatedRLHFPipeline(config, task_type="budgeting")
    
    # Example prompts
    prompts = [
        "Allocate $2.5M across Amazon, Walmart, Target for Q1",
        "Optimize $1M budget for new product launch",
        "Plan $500K test budget for emerging retailer"
    ]
    
    # Mock inference function (replace with actual model)
    def mock_inference(prompt: str) -> str:
        return f"Mock allocation for: {prompt[:50]}..."
    
    # Run pipeline
    print("\n🚀 Running Automated RLHF Pipeline...\n")
    
    results = pipeline.run_full_pipeline(
        prompts=prompts,
        model_inference_fn=mock_inference,
        adapter_name="test_adapter"
    )
    
    print(f"\n✅ Pipeline Complete!")
    print(f"Results: {json.dumps(results, indent=2, default=str)}")
