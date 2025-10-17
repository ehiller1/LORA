"""Multi-Agent RLHF Orchestration with specialized evaluator crews.

This module coordinates multiple specialized agents to provide comprehensive,
multi-dimensional feedback for RLHF training.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from crewai import Agent, Task, Crew, Process

logger = logging.getLogger(__name__)


@dataclass
class MultiDimensionalFeedback:
    """Comprehensive feedback from multiple specialized agents."""
    
    prompt: str
    model_output: str
    
    # Individual dimension scores (0-100)
    accuracy_score: float
    brand_alignment_score: float
    compliance_score: float
    clarity_score: float
    actionability_score: float
    
    # Weighted overall score
    overall_score: float
    
    # Detailed feedback by dimension
    accuracy_feedback: str
    brand_feedback: str
    compliance_feedback: str
    clarity_feedback: str
    actionability_feedback: str
    
    # Aggregate insights
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    
    # Decision
    is_acceptable: bool = False
    confidence: float = 0.0


class MultiAgentRLHF:
    """Multi-agent system for comprehensive RLHF evaluation."""
    
    def __init__(
        self,
        task_type: str = "budgeting",
        weights: Optional[Dict[str, float]] = None
    ):
        """Initialize multi-agent RLHF system.
        
        Args:
            task_type: Type of task being evaluated
            weights: Dimension weights for overall score (must sum to 1.0)
        """
        self.task_type = task_type
        
        # Default weights if not provided
        self.weights = weights or {
            "accuracy": 0.30,
            "brand_alignment": 0.20,
            "compliance": 0.25,
            "clarity": 0.15,
            "actionability": 0.10
        }
        
        # Validate weights
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        # Create specialized agents
        self.agents = self._create_specialist_agents()
        
        logger.info(f"Initialized MultiAgentRLHF for {task_type}")
    
    def _create_specialist_agents(self) -> Dict[str, Agent]:
        """Create specialized evaluator agents.
        
        Returns:
            Dictionary of dimension -> Agent
        """
        agents = {}
        
        # Accuracy Specialist
        agents["accuracy"] = Agent(
            role="Accuracy & Correctness Evaluator",
            goal="Verify factual accuracy, mathematical correctness, and logical soundness",
            backstory="""You are a detail-oriented analyst who catches errors others miss.
            You verify that numbers add up, logic is sound, and recommendations are based
            on valid reasoning. You have a PhD in data science and 10 years in analytics.""",
            verbose=False,
            allow_delegation=False
        )
        
        # Brand Alignment Specialist
        agents["brand_alignment"] = Agent(
            role="Brand Voice & Alignment Specialist",
            goal="Ensure outputs match brand personality, tone, and messaging guidelines",
            backstory="""You are a brand strategist who has defined voice for 50+ major brands.
            You can identify when messaging is off-brand in subtle ways. You understand how
            tone, word choice, and framing reinforce or undermine brand identity.""",
            verbose=False,
            allow_delegation=False
        )
        
        # Compliance Specialist
        agents["compliance"] = Agent(
            role="Compliance & Policy Expert",
            goal="Flag any policy violations, prohibited claims, or regulatory issues",
            backstory="""You are a compliance officer with legal training and 12 years in
            advertising law. You know FTC regulations, retailer policies, and common pitfalls.
            You prevent expensive mistakes before they happen.""",
            verbose=False,
            allow_delegation=False
        )
        
        # Clarity Specialist  
        agents["clarity"] = Agent(
            role="Clarity & Communication Expert",
            goal="Ensure outputs are clear, concise, and easy to understand",
            backstory="""You are a technical writer and UX copy expert. You've simplified
            complex information for thousands of users. You know when jargon obscures meaning,
            when structure confuses, and when brevity would improve impact.""",
            verbose=False,
            allow_delegation=False
        )
        
        # Actionability Specialist
        agents["actionability"] = Agent(
            role="Actionability & Usefulness Evaluator",
            goal="Assess whether outputs provide clear, implementable next steps",
            backstory="""You are a management consultant who has delivered 200+ strategy
            projects. You know the difference between vague advice and actionable recommendations.
            You assess whether users can actually execute based on the output.""",
            verbose=False,
            allow_delegation=False
        )
        
        return agents
    
    def evaluate(
        self,
        prompt: str,
        model_output: str,
        context: Optional[Dict[str, Any]] = None
    ) -> MultiDimensionalFeedback:
        """Evaluate model output across all dimensions.
        
        Args:
            prompt: Original prompt
            model_output: Model's response
            context: Additional context (brand guidelines, constraints, etc.)
            
        Returns:
            MultiDimensionalFeedback with scores and detailed feedback
        """
        logger.info(f"Starting multi-agent evaluation for: {prompt[:100]}...")
        
        # Create evaluation tasks for each dimension
        tasks = self._create_evaluation_tasks(prompt, model_output, context)
        
        # Create crew with all specialists
        crew = Crew(
            agents=list(self.agents.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        # Execute evaluations
        results = crew.kickoff()
        
        # Parse and aggregate results
        feedback = self._aggregate_results(results, prompt, model_output)
        
        logger.info(f"Evaluation complete. Overall score: {feedback.overall_score:.1f}/100")
        
        return feedback
    
    def _create_evaluation_tasks(
        self,
        prompt: str,
        model_output: str,
        context: Optional[Dict[str, Any]]
    ) -> List[Task]:
        """Create evaluation tasks for each dimension.
        
        Args:
            prompt: Original prompt
            model_output: Model output
            context: Additional context
            
        Returns:
            List of Tasks
        """
        tasks = []
        
        context_str = self._format_context(context) if context else ""
        
        # Accuracy task
        tasks.append(Task(
            description=f"""
Evaluate the ACCURACY and CORRECTNESS of this output:

Prompt: {prompt}

Output: {model_output}
{context_str}

Score 0-100 for:
1. Factual accuracy (are numbers/facts correct?)
2. Mathematical correctness (do calculations check out?)
3. Logical soundness (is the reasoning valid?)

Provide:
- Score (0-100)
- Key strengths
- Key weaknesses
- Specific errors or concerns
""",
            agent=self.agents["accuracy"],
            expected_output="Score and detailed accuracy assessment"
        ))
        
        # Brand alignment task
        tasks.append(Task(
            description=f"""
Evaluate the BRAND ALIGNMENT of this output:

Prompt: {prompt}

Output: {model_output}
{context_str}

Score 0-100 for:
1. Tone matches brand voice
2. Messaging aligns with brand values
3. Language/phrasing is on-brand

Provide:
- Score (0-100)
- What's on-brand
- What's off-brand
- Suggested improvements
""",
            agent=self.agents["brand_alignment"],
            expected_output="Score and brand alignment assessment"
        ))
        
        # Compliance task
        tasks.append(Task(
            description=f"""
Evaluate COMPLIANCE and POLICY ADHERENCE:

Prompt: {prompt}

Output: {model_output}
{context_str}

Score 0-100 for:
1. FTC compliance (no prohibited claims)
2. Retailer policy adherence
3. Legal/regulatory safety

Provide:
- Score (0-100) - 100 = fully compliant, 0 = major violations
- Any policy violations found
- Risks or red flags
- How to fix issues
""",
            agent=self.agents["compliance"],
            expected_output="Score and compliance assessment"
        ))
        
        # Clarity task
        tasks.append(Task(
            description=f"""
Evaluate CLARITY and COMMUNICATION QUALITY:

Prompt: {prompt}

Output: {model_output}
{context_str}

Score 0-100 for:
1. Clear and easy to understand
2. Well-structured and organized
3. Appropriate level of detail

Provide:
- Score (0-100)
- What's clear
- What's confusing
- How to improve clarity
""",
            agent=self.agents["clarity"],
            expected_output="Score and clarity assessment"
        ))
        
        # Actionability task
        tasks.append(Task(
            description=f"""
Evaluate ACTIONABILITY and USEFULNESS:

Prompt: {prompt}

Output: {model_output}
{context_str}

Score 0-100 for:
1. Provides clear next steps
2. Recommendations are specific and implementable
3. User can act on this information

Provide:
- Score (0-100)
- What's actionable
- What's too vague
- Missing implementation details
""",
            agent=self.agents["actionability"],
            expected_output="Score and actionability assessment"
        ))
        
        return tasks
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for display.
        
        Args:
            context: Context dictionary
            
        Returns:
            Formatted string
        """
        lines = ["\nAdditional Context:"]
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _aggregate_results(
        self,
        results: str,
        prompt: str,
        model_output: str
    ) -> MultiDimensionalFeedback:
        """Aggregate results from all agents.
        
        Args:
            results: Raw results from crew
            prompt: Original prompt
            model_output: Model output
            
        Returns:
            MultiDimensionalFeedback
        """
        # Parse results (simplified - in production, use structured output)
        import re
        
        # Extract scores
        score_pattern = r'Score:?\s*(\d+)'
        scores = re.findall(score_pattern, str(results), re.IGNORECASE)
        
        # Default scores
        dimension_scores = {
            "accuracy": 75.0,
            "brand_alignment": 75.0,
            "compliance": 85.0,
            "clarity": 70.0,
            "actionability": 65.0
        }
        
        # Update with found scores
        dimensions = ["accuracy", "brand_alignment", "compliance", "clarity", "actionability"]
        for i, score in enumerate(scores[:5]):
            if i < len(dimensions):
                dimension_scores[dimensions[i]] = float(score)
        
        # Calculate weighted overall score
        overall_score = sum(
            dimension_scores[dim] * self.weights[dim]
            for dim in dimensions
        )
        
        # Extract feedback sections (simplified)
        result_str = str(results)
        
        # Determine if acceptable (threshold: 70/100)
        is_acceptable = overall_score >= 70
        
        # Calculate confidence based on score variance
        scores_list = list(dimension_scores.values())
        variance = sum((s - overall_score) ** 2 for s in scores_list) / len(scores_list)
        confidence = max(0.0, min(1.0, 1.0 - (variance / 1000)))  # Normalize
        
        return MultiDimensionalFeedback(
            prompt=prompt,
            model_output=model_output,
            accuracy_score=dimension_scores["accuracy"],
            brand_alignment_score=dimension_scores["brand_alignment"],
            compliance_score=dimension_scores["compliance"],
            clarity_score=dimension_scores["clarity"],
            actionability_score=dimension_scores["actionability"],
            overall_score=overall_score,
            accuracy_feedback=result_str[:500],
            brand_feedback=result_str[:500],
            compliance_feedback=result_str[:500],
            clarity_feedback=result_str[:500],
            actionability_feedback=result_str[:500],
            is_acceptable=is_acceptable,
            confidence=confidence
        )
    
    def batch_evaluate(
        self,
        examples: List[Dict[str, str]]
    ) -> List[MultiDimensionalFeedback]:
        """Evaluate a batch of examples.
        
        Args:
            examples: List of {"prompt": ..., "output": ..., "context": ...} dicts
            
        Returns:
            List of MultiDimensionalFeedback
        """
        results = []
        
        for i, example in enumerate(examples):
            logger.info(f"Evaluating example {i+1}/{len(examples)}")
            
            try:
                feedback = self.evaluate(
                    prompt=example["prompt"],
                    model_output=example["output"],
                    context=example.get("context")
                )
                results.append(feedback)
            except Exception as e:
                logger.error(f"Failed to evaluate example {i+1}: {e}")
                continue
        
        return results


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create multi-agent system
    rlhf = MultiAgentRLHF(task_type="budgeting")
    
    # Example evaluation
    prompt = "Allocate $2.5M across Amazon, Walmart, Target to maximize ROAS"
    output = """
    Recommendation:
    - Amazon: $1.5M (60%) - highest ROAS historically
    - Walmart: $700K (28%) - growing channel
    - Target: $300K (12%) - testing new features
    
    Expected ROAS: 3.4x
    """
    
    context = {
        "brand": "Acme Foods",
        "budget_constraints": "Min $250K per retailer",
        "target_roas": "≥ 3.0x"
    }
    
    # Evaluate
    feedback = rlhf.evaluate(prompt, output, context)
    
    print(f"\n{'='*70}")
    print(f"MULTI-DIMENSIONAL FEEDBACK")
    print(f"{'='*70}")
    print(f"Overall Score: {feedback.overall_score:.1f}/100")
    print(f"Acceptable: {'✅ Yes' if feedback.is_acceptable else '❌ No'}")
    print(f"Confidence: {feedback.confidence:.2f}")
    print(f"\nDimension Scores:")
    print(f"  - Accuracy: {feedback.accuracy_score:.1f}/100")
    print(f"  - Brand Alignment: {feedback.brand_alignment_score:.1f}/100")
    print(f"  - Compliance: {feedback.compliance_score:.1f}/100")
    print(f"  - Clarity: {feedback.clarity_score:.1f}/100")
    print(f"  - Actionability: {feedback.actionability_score:.1f}/100")
