"""Database models for NDE rater system."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, Boolean,
    ForeignKey, Text, Enum, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
import enum

from src.storage.models import Base


class RatingTaskType(enum.Enum):
    """Types of rating tasks for NDEs."""
    TOOL_CALL_QA = "tool_call_qa"
    SCHEMA_MAPPING = "schema_mapping"
    POLICY_COMPLIANCE = "policy_compliance"
    PLAN_QUALITY = "plan_quality"
    TAGGING_NORMALIZATION = "tagging_normalization"
    EDGE_CASE_RED_TEAM = "edge_case_red_team"


class TaskStatus(enum.Enum):
    """Status of rating tasks."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    EXPERT_REVIEW = "expert_review"
    VALIDATED = "validated"


class JudgmentChoice(enum.Enum):
    """Judgment choices for pairwise comparison."""
    CANDIDATE_A = "candidate_a"
    CANDIDATE_B = "candidate_b"
    TIE = "tie"
    UNSURE = "unsure"


class RaterProfile(Base):
    """Rater profile with reliability tracking."""
    __tablename__ = "rater_profiles"
    
    id = Column(Integer, primary_key=True)
    rater_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255))
    email = Column(String(255))
    
    # Reliability metrics
    total_judgments = Column(Integer, default=0)
    golden_set_accuracy = Column(Float, default=0.0)
    inter_rater_agreement = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)
    avg_time_per_task_seconds = Column(Float, default=0.0)
    
    # Specialization
    preferred_task_types = Column(JSON)  # List of task types
    reliability_by_task_type = Column(JSON)  # Dict of task_type -> reliability score
    
    # Status
    is_active = Column(Boolean, default=True)
    is_calibrated = Column(Boolean, default=False)
    calibration_date = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    judgments = relationship("Judgment", back_populates="rater")
    
    __table_args__ = (
        Index("idx_rater_active_calibrated", "is_active", "is_calibrated"),
    )


class RatingTask(Base):
    """Rating task for NDE raters."""
    __tablename__ = "rating_tasks"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    task_type = Column(Enum(RatingTaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    
    # Context
    retailer_id = Column(String(100), nullable=False, index=True)
    adapter_id = Column(String(100))
    
    # Task data
    context_snippets = Column(JSON)  # Retailer docs, glossary, examples
    candidate_a = Column(JSON, nullable=False)  # First candidate
    candidate_b = Column(JSON, nullable=False)  # Second candidate
    candidate_c = Column(JSON)  # Optional third candidate
    
    # Auto-checks (free shaping signals)
    auto_checks = Column(JSON)  # {check_name: pass/fail, details}
    
    # Rubric
    rubric_checklist = Column(JSON)  # List of objective criteria
    reason_codes = Column(JSON)  # Available reason codes
    
    # Golden set
    is_golden = Column(Boolean, default=False)
    golden_choice = Column(Enum(JudgmentChoice))  # Expert-verified answer
    golden_reasons = Column(JSON)
    
    # Priority
    priority = Column(Integer, default=0)  # Higher = more urgent
    uncertainty_score = Column(Float)  # For active learning
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    assigned_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    judgments = relationship("Judgment", back_populates="task")
    
    __table_args__ = (
        Index("idx_task_status_type", "status", "task_type"),
        Index("idx_task_retailer_type", "retailer_id", "task_type"),
        Index("idx_task_priority", "priority", "status"),
    )


class Judgment(Base):
    """Rater judgment on a task."""
    __tablename__ = "judgments"
    
    id = Column(Integer, primary_key=True)
    judgment_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # References
    task_id = Column(Integer, ForeignKey("rating_tasks.id"), nullable=False)
    rater_id = Column(Integer, ForeignKey("rater_profiles.id"), nullable=False)
    
    # Judgment
    choice = Column(Enum(JudgmentChoice), nullable=False)
    reasons = Column(JSON)  # List of reason codes selected
    free_text_feedback = Column(Text)
    confidence = Column(Float, nullable=False)  # 0-1
    
    # Rubric scores
    rubric_scores = Column(JSON)  # Dict of criterion -> score
    
    # Time tracking
    time_spent_seconds = Column(Float)
    
    # Quality indicators
    is_escalated = Column(Boolean, default=False)
    escalation_reason = Column(Text)
    matches_golden = Column(Boolean)  # If task is golden
    
    # Expert review
    expert_reviewed = Column(Boolean, default=False)
    expert_agrees = Column(Boolean)
    expert_feedback = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    task = relationship("RatingTask", back_populates="judgments")
    rater = relationship("RaterProfile", back_populates="judgments")
    
    __table_args__ = (
        Index("idx_judgment_task_rater", "task_id", "rater_id"),
        Index("idx_judgment_escalated", "is_escalated"),
        UniqueConstraint("task_id", "rater_id", name="uq_task_rater"),
    )


class GoldenSetItem(Base):
    """Golden set items for calibration."""
    __tablename__ = "golden_set_items"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("rating_tasks.id"), unique=True, nullable=False)
    
    # Expert verification
    expert_id = Column(String(100), nullable=False)
    expert_choice = Column(Enum(JudgmentChoice), nullable=False)
    expert_reasons = Column(JSON)
    expert_rationale = Column(Text)
    
    # Usage tracking
    times_used = Column(Integer, default=0)
    rater_accuracy_rate = Column(Float, default=0.0)
    
    # Metadata
    difficulty_level = Column(String(50))  # easy, medium, hard
    edge_case_type = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RewardModel(Base):
    """Reward model trained from NDE judgments."""
    __tablename__ = "reward_models"
    
    id = Column(Integer, primary_key=True)
    model_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Model info
    base_model = Column(String(255), nullable=False)
    retailer_id = Column(String(100), index=True)  # Retailer-specific or shared
    task_type = Column(Enum(RatingTaskType))
    
    # Training data
    training_judgments_count = Column(Integer)
    training_date = Column(DateTime)
    
    # Model artifacts
    model_path = Column(String(500))
    config = Column(JSON)
    
    # Performance metrics
    validation_accuracy = Column(Float)
    inter_rater_agreement = Column(Float)
    auto_check_correlation = Column(Float)
    
    # Deployment
    is_active = Column(Boolean, default=False)
    deployed_at = Column(DateTime)
    
    # Versioning
    version = Column(String(50))
    parent_model_id = Column(String(100))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_rm_retailer_type", "retailer_id", "task_type"),
        Index("idx_rm_active", "is_active"),
    )


class RLHFMetric(Base):
    """Business metrics for RLHF program."""
    __tablename__ = "rlhf_metrics"
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False, index=True)
    retailer_id = Column(String(100), index=True)
    
    # Adapter quality KPIs
    tool_call_exact_match_rate = Column(Float)
    tool_call_compile_pass_rate = Column(Float)
    schema_mapping_f1 = Column(Float)
    policy_pass_rate_first_submit = Column(Float)
    time_to_onboard_days = Column(Float)
    
    # Program health KPIs
    inter_rater_reliability = Column(Float)
    golden_set_accuracy = Column(Float)
    percent_tasks_escalated = Column(Float)
    cost_per_accepted_judgment = Column(Float)
    latency_per_rl_iteration_hours = Column(Float)
    
    # Business impact
    incremental_roas = Column(Float)
    incremental_revenue = Column(Float)
    expert_hours_saved = Column(Float)
    
    # Volume
    total_judgments = Column(Integer)
    active_raters = Column(Integer)
    tasks_completed = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_metrics_date_retailer", "date", "retailer_id"),
    )
