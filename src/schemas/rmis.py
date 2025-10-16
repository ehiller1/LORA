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
