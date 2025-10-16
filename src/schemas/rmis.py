"""Retail Media Interop Schema (RMIS) - Canonical data models."""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class PlacementType(str, Enum):
    """Standard placement types across RMNs."""
    SPONSORED_PRODUCT = "sponsored_product"
    ONSITE_DISPLAY = "onsite_display"
    OFFSITE_DISPLAY = "offsite_display"
    CTV = "ctv"
    AUDIO = "audio"
    SEARCH = "search"
    UNKNOWN = "unknown"


class AttributionModel(str, Enum):
    """Attribution models used by RMNs."""
    LAST_CLICK = "last_click"
    FIRST_CLICK = "first_click"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    DATA_DRIVEN = "data_driven"
    UNSPECIFIED = "unspecified"


class InventoryType(str, Enum):
    """Inventory types."""
    ONSITE = "onsite"
    OFFSITE = "offsite"
    CTV = "ctv"
    AUDIO = "audio"
    MOBILE_APP = "mobile_app"


class RMISEvent(BaseModel):
    """Canonical event schema for retail media impressions/clicks/conversions."""
    
    # Identity
    event_id: str = Field(..., description="Unique event identifier")
    ts: datetime = Field(..., description="Event timestamp (UTC)")
    retailer_id: str = Field(..., description="Retailer/RMN identifier")
    
    # Campaign hierarchy
    placement_type: PlacementType = Field(..., description="Standardized placement type")
    campaign_id: str = Field(..., description="Campaign identifier")
    ad_group_id: Optional[str] = Field(None, description="Ad group identifier")
    creative_id: Optional[str] = Field(None, description="Creative identifier")
    
    # Audience & context
    audience_id: Optional[str] = Field(None, description="Audience segment identifier")
    device: Optional[str] = Field(None, description="Device type (mobile, desktop, tablet, ctv)")
    geo: Optional[str] = Field(None, description="Geographic region/DMA")
    inventory_type: InventoryType = Field(..., description="Inventory type")
    
    # Product
    sku_id: str = Field(..., description="SKU/product identifier")
    unit_price: Optional[float] = Field(None, description="Product unit price")
    promo_flag: bool = Field(False, description="Whether product is on promotion")
    in_stock_flag: bool = Field(True, description="Whether product is in stock")
    
    # Metrics
    impressions: int = Field(0, ge=0, description="Number of impressions")
    clicks: int = Field(0, ge=0, description="Number of clicks")
    attributed_conversions: int = Field(0, ge=0, description="Attributed conversions")
    attributed_revenue: float = Field(0.0, ge=0, description="Attributed revenue")
    view_through_conversions: int = Field(0, ge=0, description="View-through conversions")
    
    # Attribution metadata
    attr_model: AttributionModel = Field(AttributionModel.UNSPECIFIED, description="Attribution model used")
    lookback_window_days: int = Field(7, ge=0, description="Attribution lookback window in days")
    
    # Cost
    cost: float = Field(0.0, ge=0, description="Media cost")
    currency: str = Field("USD", description="Currency code (ISO 4217)")
    
    # Extended attributes
    extended_attributes: Optional[Dict[str, Any]] = Field(None, description="Additional retailer-specific attributes")
    
    @field_validator('device')
    @classmethod
    def normalize_device(cls, v: Optional[str]) -> Optional[str]:
        """Normalize device to lowercase."""
        return v.lower() if v else None
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code format."""
        if len(v) != 3 or not v.isupper():
            raise ValueError("Currency must be 3-letter ISO 4217 code")
        return v


class RMISSKUDimension(BaseModel):
    """SKU/product dimension."""
    
    sku_id: str = Field(..., description="SKU identifier")
    upc_ean_gtin: Optional[str] = Field(None, description="Universal product code")
    brand: str = Field(..., description="Brand name")
    category: str = Field(..., description="Product category")
    subcategory: Optional[str] = Field(None, description="Product subcategory")
    product_name: str = Field(..., description="Product name")
    
    # Attributes
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Product attributes (size, flavor, etc.)")
    
    # Economics
    margin_pct: Optional[float] = Field(None, ge=0, le=1, description="Margin percentage (0-1)")
    avg_price: Optional[float] = Field(None, ge=0, description="Average price")
    
    # Availability
    availability_score: Optional[float] = Field(None, ge=0, le=1, description="Stock availability score")
    
    @field_validator('margin_pct')
    @classmethod
    def validate_margin(cls, v: Optional[float]) -> Optional[float]:
        """Ensure margin is between 0 and 1."""
        if v is not None and (v < 0 or v > 1):
            raise ValueError("Margin must be between 0 and 1")
        return v


class RMISAudienceDimension(BaseModel):
    """Audience segment dimension."""
    
    audience_id: str = Field(..., description="Audience identifier")
    audience_name: str = Field(..., description="Audience name")
    definition: str = Field(..., description="Audience definition/description")
    seed_source: Optional[str] = Field(None, description="Seed source (1P, 3P, lookalike)")
    
    # Size & reach
    estimated_size: Optional[int] = Field(None, ge=0, description="Estimated audience size")
    reach_pct: Optional[float] = Field(None, ge=0, le=1, description="Reach as % of total population")
    
    # Overlap metrics
    overlap_metrics: Optional[Dict[str, float]] = Field(None, description="Overlap with other audiences")
    
    # Behavioral attributes
    behavioral_attributes: Optional[Dict[str, Any]] = Field(None, description="Behavioral attributes")


class RMISPolicyDimension(BaseModel):
    """Retailer policy and specifications."""
    
    retailer_id: str = Field(..., description="Retailer identifier")
    
    # Creative specifications
    creative_specs: Dict[str, Any] = Field(..., description="Creative specifications by placement type")
    disallowed_terms: list[str] = Field(default_factory=list, description="Disallowed terms/phrases")
    required_disclaimers: list[str] = Field(default_factory=list, description="Required disclaimers")
    
    # Rate limits & constraints
    rate_limits: Optional[Dict[str, Any]] = Field(None, description="API rate limits")
    min_budget_constraints: Optional[Dict[str, float]] = Field(None, description="Minimum budget by placement")
    
    # API endpoints
    api_endpoints: Dict[str, str] = Field(default_factory=dict, description="API endpoints")
    
    # Data policies
    pii_policy: Optional[str] = Field(None, description="PII handling policy")
    data_retention_days: Optional[int] = Field(None, description="Data retention period")
    min_cell_size: int = Field(50, description="Minimum cell size for k-anonymity")
    
    # Attribution
    default_attribution_model: AttributionModel = Field(
        AttributionModel.LAST_CLICK,
        description="Default attribution model"
    )
    default_lookback_days: int = Field(7, description="Default lookback window")


class RMISCrosswalk(BaseModel):
    """Crosswalk mapping between identifier systems."""
    
    retailer_id: str
    source_type: str = Field(..., description="Source identifier type (sku_id, upc, gtin)")
    target_type: str = Field(..., description="Target identifier type")
    mappings: Dict[str, str] = Field(..., description="Source -> Target mappings")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Mapping confidence")
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class RMISRecord(BaseModel):
    """
    Complete RMIS record with all fields including optional private data.
    
    This model includes fields that may not be available in clean room environments.
    """
    
    # Core fields (available in clean rooms)
    event_id: str = Field(..., description="Unique event identifier")
    retailer_id: str = Field(..., description="Retailer identifier")
    placement_type: str = Field(..., description="Placement type")
    sku_id: str = Field(..., description="SKU identifier")
    impressions: int = Field(0, ge=0, description="Impressions")
    clicks: int = Field(0, ge=0, description="Clicks")
    conversions: int = Field(0, ge=0, description="Conversions")
    revenue: float = Field(0.0, ge=0, description="Revenue")
    cost: float = Field(0.0, ge=0, description="Cost")
    attr_model: str = Field("last_click", description="Attribution model")
    date: datetime = Field(..., description="Event date")
    
    # Optional fields (may be restricted in clean rooms)
    audience: Optional[str] = Field(None, description="Audience segment")
    geo_region: Optional[str] = Field(None, description="Geographic region")
    
    # Private fields (NOT available in clean rooms)
    margin: Optional[float] = Field(None, description="Margin amount (manufacturer private)")
    margin_pct: Optional[float] = Field(None, ge=0, le=1, description="Margin percentage")
    promo_flag: Optional[bool] = Field(None, description="Promotional flag")
    stock_level: Optional[int] = Field(None, ge=0, description="Stock level")
    stock_probability: Optional[float] = Field(None, ge=0, le=1, description="Stock availability probability")
    price: Optional[float] = Field(None, ge=0, description="Product price")
    
    # Metadata
    clean_room_compatible: bool = Field(True, description="Whether record is clean room compatible")


class AllocationItem(BaseModel):
    """Single allocation item in a plan."""
    
    retailer: str = Field(..., description="Retailer name")
    placement: str = Field(..., description="Placement type")
    audience: str = Field(..., description="Audience segment")
    sku: str = Field(..., description="SKU identifier")
    spend: float = Field(..., ge=0, description="Allocated spend")
    expected_conversions: float = Field(0.0, ge=0, description="Expected conversions")
    expected_revenue: float = Field(0.0, ge=0, description="Expected revenue")
    expected_roas: float = Field(0.0, ge=0, description="Expected ROAS")
    is_experiment: bool = Field(False, description="Whether this is experimental allocation")


class Plan(BaseModel):
    """
    Campaign plan with budget allocation and optimization details.
    
    Generated by PlannerAgent with federation-enabled optimization.
    """
    
    # Objective
    objective: str = Field(..., description="Campaign objective")
    
    # Budget
    budget_total: float = Field(..., ge=0, description="Total budget")
    budget_allocated: float = Field(0.0, ge=0, description="Budget allocated")
    budget_experiment: float = Field(0.0, ge=0, description="Budget reserved for experiments")
    
    # Constraints
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Optimization constraints")
    
    # Allocation
    allocation: list[AllocationItem] = Field(default_factory=list, description="Budget allocation items")
    
    # Experiments
    experiments: Dict[str, Any] = Field(default_factory=dict, description="Experiment designs")
    
    # Rationale
    rationale: str = Field("", description="Plan rationale and reasoning")
    
    # Metadata
    adapters_used: list[str] = Field(default_factory=list, description="LoRA adapters used in planning")
    clean_room_mode: bool = Field(False, description="Whether plan was generated with clean room restrictions")
    tool_calls: list[Dict[str, Any]] = Field(default_factory=list, description="Tool calls made during planning")
    
    # Metrics
    expected_roas: float = Field(0.0, ge=0, description="Expected blended ROAS")
    expected_revenue: float = Field(0.0, ge=0, description="Expected total revenue")
    expected_margin: Optional[float] = Field(None, ge=0, description="Expected margin (if available)")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Plan creation timestamp")
    
    @field_validator('budget_allocated')
    @classmethod
    def validate_allocation(cls, v: float, info) -> float:
        """Ensure allocated budget doesn't exceed total."""
        budget_total = info.data.get('budget_total', 0)
        if v > budget_total:
            raise ValueError(f"Allocated budget ({v}) cannot exceed total budget ({budget_total})")
        return v


class ComparisonResult(BaseModel):
    """
    Comparison between clean room and full data results.
    
    Shows the performance delta when using federation vs clean-room-only.
    """
    
    # Identifiers
    comparison_id: str = Field(..., description="Comparison identifier")
    plan_id: Optional[str] = Field(None, description="Associated plan ID")
    
    # Clean room results
    clean_room_roas: float = Field(0.0, ge=0, description="ROAS with clean room data only")
    clean_room_revenue: float = Field(0.0, ge=0, description="Revenue with clean room data only")
    clean_room_accuracy: float = Field(0.0, ge=0, le=1, description="Prediction accuracy with clean room")
    clean_room_skus: int = Field(0, ge=0, description="Number of SKUs optimized with clean room")
    
    # Full data results (with federation)
    full_data_roas: float = Field(0.0, ge=0, description="ROAS with full data")
    full_data_revenue: float = Field(0.0, ge=0, description="Revenue with full data")
    full_data_accuracy: float = Field(0.0, ge=0, le=1, description="Prediction accuracy with full data")
    full_data_skus: int = Field(0, ge=0, description="Number of SKUs optimized with full data")
    
    # Deltas
    roas_delta_pct: float = Field(0.0, description="ROAS improvement percentage")
    revenue_delta_pct: float = Field(0.0, description="Revenue improvement percentage")
    accuracy_delta_pct: float = Field(0.0, description="Accuracy improvement percentage")
    sku_delta_pct: float = Field(0.0, description="SKU coverage improvement percentage")
    
    # Missing capabilities in clean room
    missing_capabilities: list[str] = Field(
        default_factory=list,
        description="Capabilities unavailable in clean room mode"
    )
    
    # Blocked fields
    blocked_fields: list[str] = Field(
        default_factory=list,
        description="Fields blocked in clean room"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Comparison timestamp")
    
    def calculate_deltas(self) -> None:
        """Calculate delta percentages."""
        if self.clean_room_roas > 0:
            self.roas_delta_pct = ((self.full_data_roas - self.clean_room_roas) / self.clean_room_roas) * 100
        
        if self.clean_room_revenue > 0:
            self.revenue_delta_pct = ((self.full_data_revenue - self.clean_room_revenue) / self.clean_room_revenue) * 100
        
        if self.clean_room_accuracy > 0:
            self.accuracy_delta_pct = ((self.full_data_accuracy - self.clean_room_accuracy) / self.clean_room_accuracy) * 100
        
        if self.clean_room_skus > 0:
            self.sku_delta_pct = ((self.full_data_skus - self.clean_room_skus) / self.clean_room_skus) * 100
