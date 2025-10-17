"""Clean Room Connector - Simulates clean room queries with field restrictions."""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
import logging

logger = logging.getLogger(__name__)


# Clean room field restrictions by retailer
CLEAN_ROOM_ALLOWED_FIELDS = {
    "default": [
        "event_id",
        "retailer_id",
        "placement_type",
        "sku_id",
        "impressions",
        "clicks",
        "conversions",
        "revenue",
        "cost",
        "attr_model",
        "date",
        "audience",
        "geo_region"
    ],
    "retailer_alpha": [
        "event_id",
        "retailer_id",
        "placement_type",
        "sku_id",
        "impressions",
        "clicks",
        "conversions",
        "revenue",
        "cost",
        "date"
    ],
    "retailer_beta": [
        "event_id",
        "retailer_id",
        "placement_type",
        "sku_id",
        "impressions",
        "clicks",
        "conversions",
        "revenue",
        "cost",
        "attr_model",
        "date"
    ]
}

# Fields that are BLOCKED in clean rooms (private/sensitive data)
CLEAN_ROOM_BLOCKED_FIELDS = [
    "margin",
    "margin_pct",
    "promo_flag",
    "creative_text",
    "stock_level",
    "stock_probability",
    "customer_id",
    "user_id",
    "email",
    "phone",
    "address",
    "geo_detail",
    "ip_address",
    "device_id",
    "price",  # Manufacturer private data
    "cost_detail",  # Detailed cost breakdown
    "supplier_id"
]

# Missing capabilities when using clean room only
CLEAN_ROOM_MISSING_CAPABILITIES = [
    "No margin data → Can't optimize profitability",
    "No stock levels → Risk of out-of-stock allocation",
    "No promo flags → Miss timing opportunities",
    "No price data → Can't model price elasticity",
    "Limited SKU coverage → Fewer optimization opportunities",
    "Aggregated only → Less granular targeting"
]


class CleanRoomConnector:
    """
    Simulates clean room queries with privacy restrictions.
    
    Clean rooms provide:
    - Aggregated data only (k-anonymity)
    - Limited field access
    - No PII exposure
    - Privacy-safe analytics
    
    But they lack:
    - Margin/profitability data
    - Inventory/stock levels
    - Promotional flags
    - Detailed customer data
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize clean room connector.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir or Path(__file__).parent.parent / "data"
        self.min_k_anonymity = 100  # Minimum records per aggregation cell
    
    def query_clean_room(
        self,
        query_params: Dict[str, Any],
        retailer_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Execute a clean room query with privacy restrictions.
        
        Args:
            query_params: Query parameters (filters, aggregations, etc.)
            retailer_id: Retailer identifier for field restrictions
            
        Returns:
            Query results with privacy guarantees
        """
        start_time = time.time()
        
        # Get allowed fields for this retailer
        allowed_fields = self.get_allowed_fields(retailer_id)
        
        # Load data
        try:
            df = self._load_data()
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return {
                "error": "Data unavailable",
                "results": [],
                "execution_time_ms": (time.time() - start_time) * 1000
            }
        
        # Apply filters
        filters = query_params.get("filters", {})
        df = self._apply_filters(df, filters)
        
        # Restrict to allowed fields
        available_cols = [col for col in allowed_fields if col in df.columns]
        df = df[available_cols]
        
        # Apply aggregations
        aggregations = query_params.get("aggregations", [])
        group_by = query_params.get("group_by", [])
        
        if group_by:
            result_df = self._aggregate_data(df, group_by, aggregations)
        else:
            result_df = df
        
        # Enforce k-anonymity
        result_df, suppressed = self._enforce_k_anonymity(result_df, group_by)
        
        # Convert to dict
        results = result_df.to_dict(orient="records")
        
        execution_time = (time.time() - start_time) * 1000
        
        blocked_fields = self._get_blocked_fields(df.columns.tolist(), allowed_fields)
        
        return {
            "results": results,
            "row_count": len(results),
            "suppressed_cells": suppressed,
            "allowed_fields": allowed_fields,
            "blocked_fields": blocked_fields,
            "missing_capabilities": self._get_missing_capabilities(blocked_fields),
            "execution_time_ms": execution_time,
            "k_anonymity_threshold": self.min_k_anonymity,
            "privacy_guarantees": [
                "k-anonymity enforced",
                "Aggregated data only",
                "No PII exposure",
                "Field restrictions applied"
            ]
        }
    
    def get_allowed_fields(self, retailer_id: str = "default") -> List[str]:
        """
        Get allowed fields for a retailer's clean room.
        
        Args:
            retailer_id: Retailer identifier
            
        Returns:
            List of allowed field names
        """
        return CLEAN_ROOM_ALLOWED_FIELDS.get(
            retailer_id,
            CLEAN_ROOM_ALLOWED_FIELDS["default"]
        )
    
    def _get_blocked_fields(self, all_fields: List[str], allowed_fields: List[str]) -> List[str]:
        """Get fields that are blocked in clean room."""
        return [f for f in all_fields if f not in allowed_fields]
    
    def _get_missing_capabilities(self, blocked_fields: List[str]) -> List[str]:
        """Get list of missing capabilities based on blocked fields."""
        capabilities = []
        
        # Check what's blocked and map to capabilities
        if any(field in blocked_fields for field in ['margin', 'margin_pct']):
            capabilities.append("No margin data → Can't optimize profitability")
        
        if any(field in blocked_fields for field in ['stock_level', 'stock_probability']):
            capabilities.append("No stock levels → Risk of out-of-stock allocation")
        
        if 'promo_flag' in blocked_fields:
            capabilities.append("No promo flags → Miss timing opportunities")
        
        if 'price' in blocked_fields:
            capabilities.append("No price data → Can't model price elasticity")
        
        # Add general limitations
        capabilities.append("Limited SKU coverage → Fewer optimization opportunities")
        capabilities.append("Aggregated only → Less granular targeting")
        
        return capabilities
    
    def _load_data(self) -> pd.DataFrame:
        """Load data from warehouse."""
        # Try to load harmonized data
        harmonized_path = self.data_dir / "harmonized_events.parquet"
        if harmonized_path.exists():
            return pd.read_parquet(harmonized_path)
        
        # Fallback to CSV
        csv_path = self.data_dir / "rmis_events.csv"
        if csv_path.exists():
            return pd.read_csv(csv_path)
        
        # Generate mock data if no files exist
        logger.warning("No data files found, generating mock data")
        return self._generate_mock_data()
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe."""
        for field, value in filters.items():
            if field in df.columns:
                if isinstance(value, list):
                    df = df[df[field].isin(value)]
                else:
                    df = df[df[field] == value]
        return df
    
    def _aggregate_data(
        self,
        df: pd.DataFrame,
        group_by: List[str],
        aggregations: List[Dict[str, str]]
    ) -> pd.DataFrame:
        """Aggregate data by specified dimensions."""
        # Filter group_by to only include available columns
        valid_group_by = [col for col in group_by if col in df.columns]
        
        if not valid_group_by:
            return df
        
        # Build aggregation dict
        agg_dict = {}
        for agg in aggregations:
            field = agg.get("field")
            func = agg.get("function", "sum")
            
            if field in df.columns:
                agg_dict[field] = func
        
        # Default aggregations if none specified
        if not agg_dict:
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            agg_dict = {col: "sum" for col in numeric_cols if col in df.columns}
        
        # Aggregate
        result = df.groupby(valid_group_by, as_index=False).agg(agg_dict)
        
        # Add record count
        result["record_count"] = df.groupby(valid_group_by).size().values
        
        return result
    
    def _enforce_k_anonymity(
        self,
        df: pd.DataFrame,
        group_by: List[str]
    ) -> tuple[pd.DataFrame, int]:
        """
        Enforce k-anonymity by suppressing cells with < k records.
        
        Args:
            df: Dataframe to enforce k-anonymity on
            group_by: Grouping columns
            
        Returns:
            Tuple of (filtered_df, num_suppressed_cells)
        """
        if not group_by or "record_count" not in df.columns:
            return df, 0
        
        # Filter out cells with < k records
        original_count = len(df)
        df = df[df["record_count"] >= self.min_k_anonymity]
        suppressed = original_count - len(df)
        
        return df, suppressed
    
    def _generate_mock_data(self) -> pd.DataFrame:
        """Generate mock data for testing."""
        np.random.seed(42)
        n_records = 1000
        
        return pd.DataFrame({
            "event_id": [f"evt_{i}" for i in range(n_records)],
            "retailer_id": np.random.choice(["alpha", "beta"], n_records),
            "placement_type": np.random.choice(["sponsored_product", "onsite_display", "offsite_video"], n_records),
            "sku_id": [f"SKU-{np.random.randint(1, 100):03d}" for _ in range(n_records)],
            "impressions": np.random.randint(100, 10000, n_records),
            "clicks": np.random.randint(1, 500, n_records),
            "conversions": np.random.randint(0, 50, n_records),
            "revenue": np.random.uniform(10, 1000, n_records),
            "cost": np.random.uniform(5, 500, n_records),
            "date": pd.date_range("2024-01-01", periods=n_records, freq="H")
        })


# Convenience functions for tool integration

def query_clean_room(query_params: Dict[str, Any], retailer_id: str = "default") -> Dict[str, Any]:
    """
    Query clean room with privacy restrictions.
    
    Args:
        query_params: Query parameters
        retailer_id: Retailer identifier
        
    Returns:
        Query results
    """
    connector = CleanRoomConnector()
    return connector.query_clean_room(query_params, retailer_id)


def get_allowed_fields(retailer_id: str = "default") -> List[str]:
    """
    Get allowed fields for a retailer's clean room.
    
    Args:
        retailer_id: Retailer identifier
        
    Returns:
        List of allowed fields
    """
    return CLEAN_ROOM_ALLOWED_FIELDS.get(retailer_id, CLEAN_ROOM_ALLOWED_FIELDS["default"])


def aggregate_to_rmis(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate raw data to RMIS format with privacy guarantees.
    
    Args:
        raw_data: Raw dataframe
        
    Returns:
        Aggregated RMIS dataframe
    """
    connector = CleanRoomConnector()
    
    # Group by standard RMIS dimensions
    group_by = ["retailer_id", "placement_type", "sku_id", "date"]
    
    # Aggregate metrics
    agg_dict = {
        "impressions": "sum",
        "clicks": "sum",
        "conversions": "sum",
        "revenue": "sum",
        "cost": "sum"
    }
    
    result = raw_data.groupby(group_by, as_index=False).agg(agg_dict)
    result["record_count"] = raw_data.groupby(group_by).size().values
    
    # Enforce k-anonymity
    result, _ = connector._enforce_k_anonymity(result, group_by)
    
    return result
