"""CrewAI-powered synthetic feedback generation for RLHF.

This module generates high-quality synthetic feedback using specialized CrewAI agents,
reducing dependency on expensive human labeling while maintaining quality.
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from crewai import Agent, Task, Crew, Process
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)


class FeedbackDimension(Enum):
    """Dimensions for multi-faceted feedback."""
    ACCURACY = "accuracy"
    BRAND_ALIGNMENT = "brand_alignment"
    COMPLIANCE = "compliance"
    CLARITY = "clarity"
    ACTIONABILITY = "actionability"


@dataclass
class SyntheticFeedback:
    """Synthetic feedback from AI evaluators."""
    
    prompt: str
    model_output: str
    overall_rating: int  # 1-5
    dimensions: Dict[str, int]  # Dimension -> rating
    explanation: str
    is_chosen: bool  # For DPO: True if good example
    improvements: Optional[str] = None


class SyntheticFeedbackGenerator:
    """Generate synthetic feedback using CrewAI agents."""
    
    def __init__(
        self,
        task_type: str = "budgeting",
        enable_langsmith: bool = True
    ):
        """Initialize synthetic feedback generator.
        
        Args:
            task_type: Type of task (budgeting, creative, measurement, etc.)
            enable_langsmith: Enable LangSmith tracing
        """
        self.task_type = task_type
        self.enable_langsmith = enable_langsmith
        
        # Create specialized evaluator agents
        self.agents = self._create_evaluator_agents()
        
        logger.info(f"Initialized SyntheticFeedbackGenerator for {task_type}")
    
    def _create_evaluator_agents(self) -> Dict[str, Agent]:
        """Create specialized evaluator agents for different dimensions.
        
        Returns:
            Dictionary of dimension -> Agent
        """
        agents = {}
        
        # Budget Optimization Expert
        if self.task_type == "budgeting":
            agents["budget_expert"] = Agent(
                role="RMN Budget Optimization Expert",
                goal="Evaluate budget allocations for effectiveness, realism, and strategic soundness",
                backstory="""You are a seasoned retail media optimization expert with 15 years 
                of experience. You've managed $500M+ in annual RMN spend across Amazon, Walmart, 
                Target, and other retailers. You understand ROAS optimization, retailer dynamics, 
                seasonal factors, and incremental lift measurement. You can instantly spot 
                unrealistic allocations or missed opportunities.""",
                verbose=True,
                allow_delegation=False
            )
        
        # Creative Copy Expert
        agents["creative_expert"] = Agent(
            role="Creative Copy Specialist",
            goal="Evaluate creative copy for brand alignment, compliance, and effectiveness",
            backstory="""You are a creative director with 12 years in CPG and retail media.
            You've written thousands of compliant, high-performing ad headlines and descriptions.
            You know what makes copy convert while staying on-brand and policy-compliant.
            You can identify tone mismatches, compliance issues, and weak CTAs instantly.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Compliance & Policy Expert
        agents["compliance_expert"] = Agent(
            role="Compliance and Policy Expert",
            goal="Verify adherence to retailer policies, regulations, and brand guidelines",
            backstory="""You are a compliance officer who has reviewed 10,000+ RMN campaigns.
            You know every retailer's advertising policy, FTC guidelines, and common pitfalls.
            You can spot prohibited claims, missing disclosures, and policy violations before
            they become problems.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Data Quality Expert
        agents["data_expert"] = Agent(
            role="Data Quality Analyst",
            goal="Assess data accuracy, completeness, and analytical rigor",
            backstory="""You are a data scientist specializing in retail analytics.
            You've built measurement frameworks for dozens of brands. You know when numbers
            don't add up, when analysis is missing key factors, or when conclusions aren't
            supported by the data.""",
            verbose=True,
            allow_delegation=False
        )
        
        # Strategic Planning Expert
        agents["strategy_expert"] = Agent(
            role="Strategic Planning Expert",
            goal="Evaluate strategic soundness and long-term thinking",
            backstory="""You are a strategy consultant who has advised Fortune 500 CPG brands.
            You think in terms of competitive positioning, market dynamics, and sustainable
            advantage. You can identify short-term thinking, missed strategic opportunities,
            or misalignment with business objectives.""",
            verbose=True,
            allow_delegation=False
        )
        
        return agents
    
    def generate_feedback(
        self,
        prompt: str,
        model_output: str,
        context: Optional[Dict[str, Any]] = None
    ) -> SyntheticFeedback:
        """Generate synthetic feedback for a model output.
        
        Args:
            prompt: Original prompt/query
            model_output: Model's response
            context: Additional context (brand, retailer, etc.)
            
        Returns:
            SyntheticFeedback with multi-dimensional ratings
        """
        logger.info(f"Generating synthetic feedback for prompt: {prompt[:100]}...")
        
        # Select relevant evaluators based on task type
        evaluators = self._select_evaluators()
        
        # Create evaluation tasks
        tasks = []
        for dimension, agent in evaluators.items():
            task = Task(
                description=self._create_evaluation_prompt(
                    dimension, prompt, model_output, context
                ),
                agent=agent,
                expected_output=f"Rating (1-5) and detailed explanation"
            )
            tasks.append(task)
        
        # Create crew and execute
        crew = Crew(
            agents=list(evaluators.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Run evaluation (with LangSmith tracing if enabled)
        if self.enable_langsmith:
            results = self._run_with_tracing(crew)
        else:
            results = crew.kickoff()
        
        # Parse results and aggregate
        feedback = self._aggregate_feedback(
            results, prompt, model_output, evaluators.keys()
        )
        
        logger.info(f"Generated feedback with overall rating: {feedback.overall_rating}/5")
        
        return feedback
    
    def _select_evaluators(self) -> Dict[str, Agent]:
        """Select relevant evaluators for the task type.
        
        Returns:
            Dictionary of dimension -> Agent
        """
        if self.task_type == "budgeting":
            return {
                "budget": self.agents["budget_expert"],
                "data": self.agents["data_expert"],
                "strategy": self.agents["strategy_expert"]
            }
        elif self.task_type == "creative":
            return {
                "creative": self.agents["creative_expert"],
                "compliance": self.agents["compliance_expert"]
            }
        elif self.task_type == "measurement":
            return {
                "data": self.agents["data_expert"],
                "strategy": self.agents["strategy_expert"]
            }
        else:
            # Default: use all available
            return self.agents
    
    def _create_evaluation_prompt(
        self,
        dimension: str,
        prompt: str,
        model_output: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Create evaluation prompt for a specific dimension.
        
        Args:
            dimension: Evaluation dimension
            prompt: Original prompt
            model_output: Model's output
            context: Additional context
            
        Returns:
            Evaluation prompt
        """
        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{self._format_context(context)}"
        
        return f"""
Please evaluate the following model output:

**Original Prompt:**
{prompt}

**Model Output:**
{model_output}
{context_str}

**Your Task:**
Rate this output on a scale of 1-5 for the {dimension} dimension, where:
- 1 = Very poor, major issues
- 2 = Below average, significant problems
- 3 = Acceptable, some issues
- 4 = Good, minor issues
- 5 = Excellent, no issues

Provide:
1. Rating (1-5)
2. Detailed explanation of your rating
3. Specific strengths
4. Specific weaknesses
5. Suggestions for improvement

Be honest and critical. This feedback will be used to train the model.
"""
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for display.
        
        Args:
            context: Context dictionary
            
        Returns:
            Formatted string
        """
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _run_with_tracing(self, crew: Crew) -> str:
        """Run crew with LangSmith tracing enabled.
        
        Args:
            crew: CrewAI crew
            
        Returns:
            Crew results
        """
        try:
            from langsmith import Client
            
            client = Client()
            with client.tracing_context(project_name="rmn-synthetic-feedback"):
                results = crew.kickoff()
            
            logger.info("Execution traced to LangSmith")
            return results
            
        except ImportError:
            logger.warning("LangSmith not available, running without tracing")
            return crew.kickoff()
    
    def _aggregate_feedback(
        self,
        results: str,
        prompt: str,
        model_output: str,
        dimensions: List[str]
    ) -> SyntheticFeedback:
        """Aggregate feedback from multiple evaluators.
        
        Args:
            results: Raw results from crew
            prompt: Original prompt
            model_output: Model output
            dimensions: Evaluated dimensions
            
        Returns:
            SyntheticFeedback
        """
        # Parse results (simplified - in production, use structured output)
        # This is a placeholder for parsing logic
        
        # Extract ratings from results
        dimension_ratings = {}
        overall_rating = 3  # Default
        explanation = str(results)
        
        # Simple heuristic: look for rating patterns
        import re
        rating_matches = re.findall(r'[Rr]ating:?\s*(\d)', str(results))
        if rating_matches:
            ratings = [int(r) for r in rating_matches]
            overall_rating = int(sum(ratings) / len(ratings))
            
            # Assign to dimensions
            for i, dim in enumerate(dimensions):
                if i < len(ratings):
                    dimension_ratings[dim] = ratings[i]
        
        # Determine if this is a "chosen" example (rating >= 4)
        is_chosen = overall_rating >= 4
        
        return SyntheticFeedback(
            prompt=prompt,
            model_output=model_output,
            overall_rating=overall_rating,
            dimensions=dimension_ratings,
            explanation=explanation,
            is_chosen=is_chosen
        )
    
    def generate_batch(
        self,
        examples: List[Dict[str, str]],
        batch_size: int = 10
    ) -> List[SyntheticFeedback]:
        """Generate feedback for a batch of examples.
        
        Args:
            examples: List of {"prompt": ..., "output": ...} dicts
            batch_size: Process in batches of this size
            
        Returns:
            List of SyntheticFeedback
        """
        all_feedback = []
        
        for i in range(0, len(examples), batch_size):
            batch = examples[i:i+batch_size]
            logger.info(f"Processing batch {i//batch_size + 1}/{(len(examples)-1)//batch_size + 1}")
            
            batch_feedback = []
            for example in batch:
                try:
                    feedback = self.generate_feedback(
                        prompt=example["prompt"],
                        model_output=example["output"],
                        context=example.get("context")
                    )
                    batch_feedback.append(feedback)
                except Exception as e:
                    logger.error(f"Failed to generate feedback: {e}")
                    continue
            
            all_feedback.extend(batch_feedback)
        
        logger.info(f"Generated {len(all_feedback)} synthetic feedback examples")
        return all_feedback


class DPODatasetBuilder:
    """Build DPO datasets from synthetic feedback."""
    
    def __init__(self, feedback_generator: SyntheticFeedbackGenerator):
        """Initialize DPO dataset builder.
        
        Args:
            feedback_generator: Synthetic feedback generator
        """
        self.feedback_generator = feedback_generator
    
    def build_from_variations(
        self,
        prompt: str,
        variations: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build DPO example from output variations.
        
        Generate multiple model outputs for the same prompt, evaluate each,
        and create chosen/rejected pairs.
        
        Args:
            prompt: Input prompt
            variations: Different model outputs for the same prompt
            context: Additional context
            
        Returns:
            DPO example with chosen and rejected outputs
        """
        # Evaluate all variations
        feedback_list = []
        for variation in variations:
            feedback = self.feedback_generator.generate_feedback(
                prompt, variation, context
            )
            feedback_list.append(feedback)
        
        # Sort by rating
        feedback_list.sort(key=lambda x: x.overall_rating, reverse=True)
        
        # Best = chosen, worst = rejected
        chosen = feedback_list[0]
        rejected = feedback_list[-1]
        
        return {
            "prompt": prompt,
            "chosen": chosen.model_output,
            "rejected": rejected.model_output,
            "chosen_rating": chosen.overall_rating,
            "rejected_rating": rejected.overall_rating,
            "explanation": f"Chosen (rated {chosen.overall_rating}/5): {chosen.explanation[:200]}... | Rejected (rated {rejected.overall_rating}/5): {rejected.explanation[:200]}..."
        }
    
    def build_dataset(
        self,
        prompts: List[str],
        output_generator,  # Function that generates variations given a prompt
        num_variations: int = 5
    ) -> List[Dict[str, Any]]:
        """Build complete DPO dataset.
        
        Args:
            prompts: List of prompts
            output_generator: Function to generate output variations
            num_variations: Number of variations per prompt
            
        Returns:
            List of DPO examples
        """
        dataset = []
        
        for prompt in prompts:
            logger.info(f"Building DPO example for: {prompt[:100]}...")
            
            # Generate variations
            variations = [
                output_generator(prompt) for _ in range(num_variations)
            ]
            
            # Create DPO example
            dpo_example = self.build_from_variations(prompt, variations)
            dataset.append(dpo_example)
        
        logger.info(f"Built DPO dataset with {len(dataset)} examples")
        return dataset


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create generator
    generator = SyntheticFeedbackGenerator(task_type="budgeting")
    
    # Example prompt and output
    prompt = "Allocate $2.5M quarterly budget across Amazon, Walmart, and Target to maximize incremental margin with ROAS >= 3.0"
    
    output = """
    Budget Allocation Recommendation:
    
    - Amazon: $1,200,000 (48%)
      - Strong historical ROAS of 3.8x
      - Best SKU coverage
      - Prime Day upcoming
    
    - Walmart: $800,000 (32%)
      - Solid ROAS of 3.2x
      - Growing digital presence
      - Q1 promotions planned
    
    - Target: $500,000 (20%)
      - Testing allocation
      - ROAS of 2.9x (below target but improving)
      - Strong brand alignment
    
    Expected Total ROAS: 3.4x
    Projected Incremental Margin: $6.0M
    """
    
    # Generate feedback
    feedback = generator.generate_feedback(prompt, output)
    
    print(f"\n{'='*70}")
    print(f"SYNTHETIC FEEDBACK")
    print(f"{'='*70}")
    print(f"Overall Rating: {feedback.overall_rating}/5")
    print(f"Is Chosen: {feedback.is_chosen}")
    print(f"\nDimensions:")
    for dim, rating in feedback.dimensions.items():
        print(f"  - {dim}: {rating}/5")
    print(f"\nExplanation:\n{feedback.explanation[:500]}...")
