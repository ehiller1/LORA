"""Database models for RMN system."""

from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, Boolean,
    ForeignKey, Text, Enum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class FeedbackType(enum.Enum):
    """Types of feedback."""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    PREFERENCE = "preference"
    CORRECTION = "correction"
    RATING = "rating"


class Retailer(Base):
    """Retailer entity."""
    __tablename__ = "retailers"
    
    id = Column(Integer, primary_key=True)
    retailer_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    schema_version = Column(String(50))
    mapping_config = Column(JSON)  # YAML mapping config
    api_endpoint = Column(String(500))
    api_key_encrypted = Column(Text)
    clean_room_endpoint = Column(String(500))
    policies = Column(JSON)  # Policy documents
    creative_specs = Column(JSON)  # Creative specifications
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="retailer")
    sku_catalogs = relationship("SKUCatalog", back_populates="retailer")
    
    __table_args__ = (
        Index("idx_retailer_active", "is_active"),
    )


class Brand(Base):
    """Brand/Manufacturer entity."""
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    tenant_id = Column(String(100), unique=True, nullable=False, index=True)
    tone_guidelines = Column(JSON)  # Brand tone/voice
    product_categories = Column(JSON)  # List of categories
    budget_constraints = Column(JSON)  # Default constraints
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = relationship("Campaign", back_populates="brand")
    sku_catalogs = relationship("SKUCatalog", back_populates="brand")
    feedbacks = relationship("Feedback", back_populates="brand")


class Campaign(Base):
    """Campaign data."""
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(String(100), unique=True, nullable=False, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    name = Column(String(255), nullable=False)
    objective = Column(String(100))  # awareness, consideration, conversion
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_budget = Column(Float, nullable=False)
    allocated_budget = Column(JSON)  # Budget allocation by placement/audience
    placement_types = Column(JSON)  # List of placement types
    target_audiences = Column(JSON)  # List of audience segments
    target_skus = Column(JSON)  # List of SKU IDs
    constraints = Column(JSON)  # ROAS, CPA, etc.
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    retailer = relationship("Retailer", back_populates="campaigns")
    brand = relationship("Brand", back_populates="campaigns")
    performance_metrics = relationship("PerformanceMetric", back_populates="campaign")
    
    __table_args__ = (
        Index("idx_campaign_dates", "start_date", "end_date"),
        Index("idx_campaign_status", "status"),
    )


class SKUCatalog(Base):
    """Product SKU catalog."""
    __tablename__ = "sku_catalog"
    
    id = Column(Integer, primary_key=True)
    sku_id = Column(String(100), nullable=False, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    upc = Column(String(50))
    ean = Column(String(50))
    gtin = Column(String(50))
    name = Column(String(500), nullable=False)
    category = Column(String(100))
    subcategory = Column(String(100))
    brand_name = Column(String(255))
    price = Column(Float)
    margin = Column(Float)
    cost = Column(Float)
    attributes = Column(JSON)  # size, color, flavor, etc.
    is_in_stock = Column(Boolean, default=True)
    stock_level = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    retailer = relationship("Retailer", back_populates="sku_catalogs")
    brand = relationship("Brand", back_populates="sku_catalogs")
    
    __table_args__ = (
        Index("idx_sku_retailer", "sku_id", "retailer_id"),
        Index("idx_sku_stock", "is_in_stock"),
    )


class AudienceSegment(Base):
    """Audience segment definitions."""
    __tablename__ = "audience_segments"
    
    id = Column(Integer, primary_key=True)
    segment_id = Column(String(100), unique=True, nullable=False, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    segment_type = Column(String(50))  # demographic, behavioral, lookalike
    criteria = Column(JSON)  # Segment definition criteria
    size_estimate = Column(Integer)
    reach_estimate = Column(Float)
    cpm_estimate = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PerformanceMetric(Base):
    """Campaign performance metrics."""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    placement_type = Column(String(100))
    audience_segment = Column(String(100))
    sku_id = Column(String(100))
    
    # Metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    units_sold = Column(Integer, default=0)
    
    # Derived metrics
    ctr = Column(Float)  # Click-through rate
    cvr = Column(Float)  # Conversion rate
    cpc = Column(Float)  # Cost per click
    cpa = Column(Float)  # Cost per acquisition
    roas = Column(Float)  # Return on ad spend
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="performance_metrics")
    
    __table_args__ = (
        Index("idx_perf_campaign_date", "campaign_id", "date"),
        Index("idx_perf_placement", "placement_type"),
    )


class Feedback(Base):
    """User feedback for RLHF."""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    user_id = Column(String(100), nullable=False)
    
    # Context
    task_type = Column(String(100))  # budgeting, creative, planning, etc.
    prompt = Column(Text, nullable=False)
    model_output = Column(Text, nullable=False)
    
    # Feedback
    feedback_type = Column(Enum(FeedbackType), nullable=False)
    rating = Column(Integer)  # 1-5 for rating type
    preferred_output = Column(Text)  # For preference/correction
    rejected_output = Column(Text)  # For preference pairs
    
    # Metadata
    metadata = Column(JSON)  # Additional context
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    brand = relationship("Brand", back_populates="feedbacks")
    
    __table_args__ = (
        Index("idx_feedback_brand_task", "brand_id", "task_type"),
        Index("idx_feedback_session", "session_id"),
    )


class ReflectionLog(Base):
    """Reflection and decision-making logs."""
    __tablename__ = "reflection_logs"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    task_type = Column(String(100))
    
    # Reflection data
    phase = Column(String(50))  # reflection, decision, execution
    memory_references = Column(JSON)  # List of relevant past scenarios
    alternate_frames = Column(JSON)  # Different perspectives considered
    
    # Risk assessment
    risk_factors = Column(JSON)  # High-risk factors identified
    mitigation_strategies = Column(JSON)  # Risk mitigation plans
    
    # Confidence
    confidence_value = Column(Float)
    confidence_rationale = Column(Text)
    decision_threshold = Column(String(255))
    
    # Bias detection
    bias_checkpoint = Column(Text)  # Identified biases
    
    # Decision
    decision = Column(JSON)  # Final decision made
    decision_rationale = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_reflection_session", "session_id"),
        Index("idx_reflection_task", "task_type"),
    )
