"""Tool schemas for agent function calling."""

from typing import List, Dict, Any, Optional, Literal
from datetime import date
from pydantic import BaseModel, Field


# ============================================================================
# Query Clean Room Tool
# ============================================================================

class CleanRoomQuery(BaseModel):
    """Single clean room query specification."""
    
    name: str = Field(..., description="Query name/identifier")
    select: List[str] = Field(..., description="Fields to select")
    from_table: str = Field(..., alias="from", description="RMIS logical table")
    joins: List[Dict[str, Any]] = Field(default_factory=list, description="Join specifications")
    filters: List[str] = Field(default_factory=list, description="WHERE clause filters")
    group_by: List[str] = Field(default_factory=list, description="GROUP BY fields")
    metrics: List[str] = Field(..., description="Aggregation metrics")


class QueryConstraints(BaseModel):
    """Privacy and aggregation constraints."""
    
    min_cell_size: int = Field(50, description="Minimum cell size for k-anonymity")
    privacy_threshold_enabled: bool = Field(True, description="Enable privacy thresholding")
    max_rows: Optional[int] = Field(None, description="Maximum rows to return")


class TimeWindow(BaseModel):
    """Time window for queries."""
    
    start_date: date = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: date = Field(..., description="End date (YYYY-MM-DD)")


class QueryCleanRoomInput(BaseModel):
    """Input for query_clean_room tool."""
    
    queries: List[CleanRoomQuery] = Field(..., description="List of queries to execute")
    constraints: QueryConstraints = Field(default_factory=QueryConstraints)
    time_window: TimeWindow = Field(..., description="Time window for data")


class QueryResult(BaseModel):
    """Single query result."""
    
    name: str
    rows: List[Dict[str, Any]]
    row_count: int
    suppressed_cells: int = Field(0, description="Number of cells suppressed for privacy")


class QueryCleanRoomOutput(BaseModel):
    """Output from query_clean_room tool."""
    
    results: List[QueryResult]
    total_rows: int
    execution_time_ms: float


# ============================================================================
# Allocate Budget Tool
# ============================================================================

class BudgetPrior(BaseModel):
    """Prior performance data for budget allocation."""
    
    rmn: str = Field(..., description="Retailer/RMN identifier")
    placement_type: str = Field(..., description="Placement type")
    audience_id: Optional[str] = Field(None, description="Audience identifier")
    sku_id: Optional[str] = Field(None, description="SKU identifier")
    
    # Performance priors
    expected_incremental_roas: float = Field(..., description="Expected incremental ROAS")
    oos_probability: float = Field(0.0, ge=0, le=1, description="Out-of-stock probability")
    margin_pct: float = Field(..., ge=0, le=1, description="Margin percentage")
    
    # Historical data
    historical_spend: Optional[float] = Field(None, description="Historical spend")
    historical_conversions: Optional[int] = Field(None, description="Historical conversions")


class BudgetConstraints(BaseModel):
    """Budget allocation constraints."""
    
    min_roas: Optional[float] = Field(None, description="Minimum ROAS constraint")
    max_cpa: Optional[float] = Field(None, description="Maximum CPA constraint")
    min_share_by_rmn: Optional[List[Dict[str, Any]]] = Field(None, description="Minimum share by RMN")
    reserve_for_experiments: float = Field(0.0, ge=0, le=1, description="% to reserve for experiments")
    exclude_skus: List[str] = Field(default_factory=list, description="SKUs to exclude")
    oos_prob_threshold: float = Field(0.1, ge=0, le=1, description="Max OOS probability threshold")
    budget_caps: Optional[List[Dict[str, Any]]] = Field(None, description="Budget caps by scope")


class AllocateBudgetInput(BaseModel):
    """Input for allocate_budget tool."""
    
    total_budget: float = Field(..., gt=0, description="Total budget to allocate")
    hierarchy: List[str] = Field(..., description="Allocation hierarchy (e.g., ['rmn', 'placement', 'audience', 'sku'])")
    priors: List[BudgetPrior] = Field(..., description="Performance priors")
    constraints: BudgetConstraints = Field(default_factory=BudgetConstraints)
    objective: Literal["maximize_incremental_margin", "maximize_incremental_revenue"] = Field(
        ...,
        description="Optimization objective"
    )


class BudgetAllocation(BaseModel):
    """Single budget allocation."""
    
    rmn: str
    placement_type: str
    audience_id: Optional[str] = None
    sku_id: Optional[str] = None
    budget: float = Field(..., ge=0)
    expected_incremental_roas: float
    expected_incremental_revenue: Optional[float] = None
    expected_incremental_margin: Optional[float] = None
    notes: Optional[str] = None


class AllocateBudgetOutput(BaseModel):
    """Output from allocate_budget tool."""
    
    allocations: List[BudgetAllocation]
    total_allocated: float
    experiment_budget: float
    constraints_satisfaction: Dict[str, bool]
    rationale: List[str] = Field(..., description="Explanation of allocation decisions")
    expected_total_incremental_roas: float
    monitoring_plan: Optional[Dict[str, Any]] = None


# ============================================================================
# Design Experiment Tool
# ============================================================================

class DesignExperimentInput(BaseModel):
    """Input for design_experiment tool."""
    
    goal: Literal["incremental_revenue", "incremental_margin", "ice"] = Field(
        ...,
        description="Experiment goal"
    )
    units: Literal["geo", "store", "region", "time_switchback"] = Field(
        ...,
        description="Experimental units"
    )
    power: float = Field(0.8, ge=0.5, le=0.99, description="Statistical power")
    min_detectable_effect: float = Field(..., description="Minimum detectable effect size")
    duration_weeks: int = Field(..., ge=1, description="Experiment duration in weeks")
    covariates: List[str] = Field(default_factory=list, description="Covariates for adjustment")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Additional constraints")


class ExperimentCell(BaseModel):
    """Experiment cell assignment."""
    
    cell_id: str
    assignment: Literal["control", "treatment"]
    units: List[str] = Field(..., description="Unit identifiers in this cell")
    expected_size: Optional[int] = None


class DesignExperimentOutput(BaseModel):
    """Output from design_experiment tool."""
    
    design: str = Field(..., description="Experiment design type (e.g., 'randomized_geo', 'switchback')")
    sample_size: int = Field(..., description="Total sample size required")
    cells: List[ExperimentCell] = Field(..., description="Experiment cells")
    success_criteria: List[str] = Field(..., description="Success criteria and analysis plan")
    expected_runtime_weeks: int
    power_analysis: Dict[str, Any] = Field(..., description="Power analysis details")


# ============================================================================
# Generate Copy Tool
# ============================================================================

class RetailerSpecs(BaseModel):
    """Retailer creative specifications."""
    
    max_headline_length: Optional[int] = None
    max_body_length: Optional[int] = None
    disallowed_terms: List[str] = Field(default_factory=list)
    required_disclaimers: List[str] = Field(default_factory=list)
    placement_type: str = Field(..., description="Placement type for specs")


class GenerateCopyInput(BaseModel):
    """Input for generate_copy tool."""
    
    sku_id: str
    attributes: Dict[str, Any] = Field(..., description="SKU attributes (size, flavor, benefits, etc.)")
    retailer_specs: RetailerSpecs
    brand_tone: str = Field(..., description="Brand tone/voice guidelines")
    num_variants: int = Field(5, ge=1, le=20, description="Number of variants to generate")
    target_audience: Optional[str] = Field(None, description="Target audience description")


class CopyVariant(BaseModel):
    """Single copy variant."""
    
    headline: str
    body: str
    call_to_action: Optional[str] = None
    reasons_to_believe: List[str] = Field(default_factory=list)
    compliance_score: float = Field(..., ge=0, le=1, description="Compliance score (0-1)")


class GenerateCopyOutput(BaseModel):
    """Output from generate_copy tool."""
    
    variants: List[CopyVariant]
    compliance_checks: List[str] = Field(..., description="Compliance check results")
    all_compliant: bool = Field(..., description="Whether all variants are compliant")
    recommendations: Optional[List[str]] = Field(None, description="Recommendations for improvement")
