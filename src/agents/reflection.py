"""Reflection and decision-making framework for agents."""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class Phase(str, Enum):
    """Decision-making phases."""
    REFLECTION = "reflection"
    ANALYSIS = "analysis"
    DECISION = "decision"
    EXECUTION = "execution"
    REVIEW = "review"


class BiasType(str, Enum):
    """Common cognitive biases to check."""
    AVAILABILITY = "availability"  # Overweighting recent/memorable events
    ANCHORING = "anchoring"  # Over-relying on first piece of information
    CONFIRMATION = "confirmation"  # Seeking info that confirms beliefs
    SUNK_COST = "sunk_cost"  # Continuing based on past investment
    RECENCY = "recency"  # Overweighting recent data
    OPTIMISM = "optimism"  # Underestimating risks
    STATUS_QUO = "status_quo"  # Preferring current state


@dataclass
class RiskFactor:
    """Risk factor in decision-making."""
    factor: str
    severity: str  # low, medium, high, critical
    probability: float  # 0-1
    impact: str
    mitigation: Optional[str] = None


@dataclass
class Confidence:
    """Confidence assessment."""
    value: float  # 0-1
    rationale: str
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)


@dataclass
class ReflectionContext:
    """Context for reflection and decision-making."""
    phase: Phase
    task_type: str
    session_id: str
    
    # Memory and context
    memory_references: List[str] = field(default_factory=list)
    alternate_frames: List[str] = field(default_factory=list)
    
    # Risk assessment
    risk_factors: List[RiskFactor] = field(default_factory=list)
    
    # Confidence
    confidence: Optional[Confidence] = None
    decision_threshold: str = "confidence >= 0.8"
    
    # Bias detection
    bias_checkpoints: List[Dict[str, str]] = field(default_factory=list)
    
    # Decision
    decision: Optional[Dict[str, Any]] = None
    decision_rationale: Optional[str] = None
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ReflectionEngine:
    """Engine for reflective decision-making."""
    
    def __init__(
        self,
        default_threshold: float = 0.8,
        enable_bias_detection: bool = True
    ):
        """
        Initialize reflection engine.
        
        Args:
            default_threshold: Default confidence threshold
            enable_bias_detection: Enable bias detection
        """
        self.default_threshold = default_threshold
        self.enable_bias_detection = enable_bias_detection
        self.reflection_history: List[ReflectionContext] = []
    
    def create_context(
        self,
        task_type: str,
        session_id: str,
        phase: Phase = Phase.REFLECTION
    ) -> ReflectionContext:
        """
        Create a new reflection context.
        
        Args:
            task_type: Type of task being performed
            session_id: Unique session identifier
            phase: Current phase
        
        Returns:
            Reflection context
        """
        context = ReflectionContext(
            phase=phase,
            task_type=task_type,
            session_id=session_id
        )
        
        # Load relevant memory references
        context.memory_references = self._load_memory_references(task_type)
        
        return context
    
    def _load_memory_references(self, task_type: str) -> List[str]:
        """
        Load relevant past scenarios from memory.
        
        Args:
            task_type: Type of task
        
        Returns:
            List of memory references
        """
        # In production, this would query a vector database
        # For now, return relevant examples based on task type
        memory_map = {
            "budgeting": [
                "Similar budget allocation for Q3 2024 - achieved 3.2x ROAS",
                "Budget reallocation after OOS spike - prevented 15% waste",
                "Cross-RMN optimization - improved efficiency by 22%"
            ],
            "creative": [
                "Compliance issue with Retailer X - headline too long",
                "High-performing copy variant - emphasized value proposition",
                "Brand tone violation - too promotional"
            ],
            "measurement": [
                "Geo test design for similar product category",
                "Switchback experiment with 85% power",
                "Lift analysis showing 12% incremental sales"
            ]
        }
        
        return memory_map.get(task_type, [])
    
    def add_alternate_frame(
        self,
        context: ReflectionContext,
        frame: str
    ):
        """
        Add an alternate perspective to consider.
        
        Args:
            context: Reflection context
            frame: Alternate framing
        """
        context.alternate_frames.append(frame)
        logger.debug(f"Added alternate frame: {frame}")
    
    def assess_risk(
        self,
        context: ReflectionContext,
        factor: str,
        severity: str,
        probability: float,
        impact: str,
        mitigation: Optional[str] = None
    ):
        """
        Add a risk factor to assessment.
        
        Args:
            context: Reflection context
            factor: Risk factor description
            severity: Severity level
            probability: Probability (0-1)
            impact: Impact description
            mitigation: Mitigation strategy
        """
        risk = RiskFactor(
            factor=factor,
            severity=severity,
            probability=probability,
            impact=impact,
            mitigation=mitigation
        )
        context.risk_factors.append(risk)
        logger.info(f"Risk assessed: {factor} ({severity}, p={probability})")
    
    def set_confidence(
        self,
        context: ReflectionContext,
        value: float,
        rationale: str,
        supporting: Optional[List[str]] = None,
        contradicting: Optional[List[str]] = None
    ):
        """
        Set confidence level for decision.
        
        Args:
            context: Reflection context
            value: Confidence value (0-1)
            rationale: Rationale for confidence level
            supporting: Supporting evidence
            contradicting: Contradicting evidence
        """
        context.confidence = Confidence(
            value=value,
            rationale=rationale,
            supporting_evidence=supporting or [],
            contradicting_evidence=contradicting or []
        )
        logger.info(f"Confidence set: {value:.2f} - {rationale}")
    
    def check_bias(
        self,
        context: ReflectionContext,
        bias_type: BiasType,
        description: str
    ):
        """
        Check for cognitive bias.
        
        Args:
            context: Reflection context
            bias_type: Type of bias
            description: Description of potential bias
        """
        if not self.enable_bias_detection:
            return
        
        checkpoint = {
            "bias_type": bias_type.value,
            "description": description,
            "timestamp": datetime.utcnow().isoformat()
        }
        context.bias_checkpoints.append(checkpoint)
        logger.warning(f"Bias checkpoint: {bias_type.value} - {description}")
    
    def should_proceed(self, context: ReflectionContext) -> bool:
        """
        Determine if decision should proceed based on threshold.
        
        Args:
            context: Reflection context
        
        Returns:
            True if should proceed
        """
        if context.confidence is None:
            logger.warning("No confidence set, cannot determine if should proceed")
            return False
        
        # Evaluate decision threshold
        # Simple threshold check (can be extended with complex logic)
        confidence_met = context.confidence.value >= self.default_threshold
        
        # Check for critical risks
        critical_risks = [
            r for r in context.risk_factors
            if r.severity == "critical" and r.mitigation is None
        ]
        
        if critical_risks:
            logger.warning(f"Critical unmitigated risks present: {len(critical_risks)}")
            return False
        
        return confidence_met
    
    def make_decision(
        self,
        context: ReflectionContext,
        decision: Dict[str, Any],
        rationale: str
    ):
        """
        Record a decision.
        
        Args:
            context: Reflection context
            decision: Decision data
            rationale: Decision rationale
        """
        context.phase = Phase.DECISION
        context.decision = decision
        context.decision_rationale = rationale
        
        # Store in history
        self.reflection_history.append(context)
        
        logger.info(f"Decision made: {rationale}")
    
    def get_summary(self, context: ReflectionContext) -> Dict[str, Any]:
        """
        Get summary of reflection context.
        
        Args:
            context: Reflection context
        
        Returns:
            Summary dictionary
        """
        return {
            "phase": context.phase.value,
            "task_type": context.task_type,
            "session_id": context.session_id,
            "memory_references": context.memory_references,
            "alternate_frames": context.alternate_frames,
            "risk_assessment": {
                "high_risk_factors": [
                    {
                        "factor": r.factor,
                        "severity": r.severity,
                        "probability": r.probability,
                        "mitigation": r.mitigation
                    }
                    for r in context.risk_factors
                    if r.severity in ["high", "critical"]
                ]
            },
            "confidence": {
                "value": context.confidence.value if context.confidence else None,
                "rationale": context.confidence.rationale if context.confidence else None
            } if context.confidence else None,
            "decision_threshold": context.decision_threshold,
            "bias_checkpoints": context.bias_checkpoints,
            "decision": context.decision,
            "decision_rationale": context.decision_rationale,
            "timestamp": context.timestamp.isoformat()
        }
    
    def save_to_database(self, context: ReflectionContext, db_session):
        """
        Save reflection context to database.
        
        Args:
            context: Reflection context
            db_session: Database session
        """
        from src.storage.models import ReflectionLog
        
        log = ReflectionLog(
            session_id=context.session_id,
            task_type=context.task_type,
            phase=context.phase.value,
            memory_references=context.memory_references,
            alternate_frames=context.alternate_frames,
            risk_factors=[
                {
                    "factor": r.factor,
                    "severity": r.severity,
                    "probability": r.probability,
                    "impact": r.impact,
                    "mitigation": r.mitigation
                }
                for r in context.risk_factors
            ],
            mitigation_strategies=[
                r.mitigation for r in context.risk_factors
                if r.mitigation is not None
            ],
            confidence_value=context.confidence.value if context.confidence else None,
            confidence_rationale=context.confidence.rationale if context.confidence else None,
            decision_threshold=context.decision_threshold,
            bias_checkpoint="; ".join([
                f"{b['bias_type']}: {b['description']}"
                for b in context.bias_checkpoints
            ]),
            decision=context.decision,
            decision_rationale=context.decision_rationale
        )
        
        db_session.add(log)
        db_session.commit()
        logger.info(f"Reflection log saved: {context.session_id}")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create reflection engine
    engine = ReflectionEngine()
    
    # Create context for budget allocation task
    context = engine.create_context(
        task_type="budgeting",
        session_id="session_123"
    )
    
    # Add alternate perspectives
    engine.add_alternate_frame(
        context,
        "Looking at the problem from a cost vs. benefit perspective"
    )
    engine.add_alternate_frame(
        context,
        "Considering short-term gains vs. long-term stability"
    )
    
    # Assess risks
    engine.assess_risk(
        context,
        factor="Market volatility in Q4",
        severity="medium",
        probability=0.6,
        impact="Budget efficiency may decrease by 10-15%",
        mitigation="Reserve 15% budget for reallocation"
    )
    
    # Check for biases
    engine.check_bias(
        context,
        BiasType.AVAILABILITY,
        "Anchoring on recent market fluctuations"
    )
    
    # Set confidence
    engine.set_confidence(
        context,
        value=0.75,
        rationale="Market trends align with historical patterns",
        supporting=[
            "Historical Q4 performance data",
            "Current market indicators"
        ],
        contradicting=[
            "Increased competition from new entrants"
        ]
    )
    
    # Check if should proceed
    should_proceed = engine.should_proceed(context)
    print(f"Should proceed: {should_proceed}")
    
    # Get summary
    summary = engine.get_summary(context)
    print("\nReflection Summary:")
    import json
    print(json.dumps(summary, indent=2))
