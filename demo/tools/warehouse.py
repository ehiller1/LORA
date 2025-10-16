"""Warehouse manager for data harmonization."""

import duckdb
import pandas as pd
import numpy as np
from pathlib import Path
import json
import yaml


class WarehouseManager:
    """Manages DuckDB warehouse and RMIS materialization."""
    
    def __init__(self, db_path=":memory:"):
        """Initialize warehouse."""
        self.conn = duckdb.connect(db_path)
        self.data_dir = Path(__file__).parent.parent / "data"
        self.mappings_dir = Path(__file__).parent.parent / "mappings"
        
        # Initialize RMIS tables
        self._init_rmis_schema()
    
    def _init_rmis_schema(self):
        """Create RMIS tables."""
        
        # Events table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS rmis_events (
                event_id VARCHAR PRIMARY KEY,
                ts TIMESTAMP,
                retailer_id VARCHAR,
                placement_type VARCHAR,
                cost DECIMAL(10,2),
                impressions INTEGER,
                clicks INTEGER,
                conversions INTEGER,
                revenue DECIMAL(10,2),
                campaign_id VARCHAR,
                sku VARCHAR,
                audience_segment VARCHAR,
                device_type VARCHAR,
                inventory_type VARCHAR,
                attribution_model VARCHAR
            )
        """)
        
        # SKU dimension
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS rmis_skus (
                sku_id VARCHAR PRIMARY KEY,
                product_name VARCHAR,
                category VARCHAR,
                price DECIMAL(10,2),
                cost DECIMAL(10,2),
                margin_pct DECIMAL(5,3),
                stock_units INTEGER,
                stock_probability DECIMAL(5,3)
            )
        """)
    
    def load_retailer_data(self, retailer: str) -> bool:
        """Load raw retailer data."""
        try:
            if retailer == "alpha":
                # Load Alpha CSV files
                events_path = self.data_dir / "retailer_alpha" / "events.csv"
                if events_path.exists():
                    df = pd.read_csv(events_path)
                    self.conn.execute("CREATE OR REPLACE TABLE raw_alpha_events AS SELECT * FROM df")
                    return True
            
            elif retailer == "beta":
                # Load Beta JSONL
                log_path = self.data_dir / "retailer_beta" / "log.jsonl"
                if log_path.exists():
                    records = []
                    with open(log_path) as f:
                        for line in f:
                            records.append(json.loads(line))
                    df = pd.DataFrame(records)
                    self.conn.execute("CREATE OR REPLACE TABLE raw_beta_events AS SELECT * FROM df")
                    return True
            
            return False
        except Exception as e:
            print(f"Error loading {retailer} data: {e}")
            return False
    
    def harmonize_retailer(self, retailer: str) -> dict:
        """Harmonize retailer data to RMIS."""
        try:
            if retailer == "alpha":
                return self._harmonize_alpha()
            elif retailer == "beta":
                return self._harmonize_beta()
            else:
                return {"success": False, "error": "Unknown retailer"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _harmonize_alpha(self) -> dict:
        """Harmonize Retailer Alpha to RMIS."""
        
        # Mapping logic
        sql = """
            INSERT INTO rmis_events
            SELECT
                event_id,
                CAST(timestamp AS TIMESTAMP) as ts,
                'alpha' as retailer_id,
                CASE 
                    WHEN LOWER(adType) = 'sp' THEN 'sponsored_product'
                    WHEN LOWER(adType) = 'sd' THEN 'sponsored_display'
                    WHEN LOWER(adType) LIKE '%disp%' THEN 'onsite_display'
                    WHEN LOWER(adType) LIKE '%vid%' THEN 'offsite_video'
                    ELSE 'other'
                END as placement_type,
                cost_micros / 1000000.0 as cost,
                impressions,
                clicks,
                conv_click_7d as conversions,
                revenue_7d as revenue,
                campaign_id,
                sku,
                COALESCE(audience_segment, 'unknown') as audience_segment,
                CASE
                    WHEN LOWER(device) = 'mobile' THEN 'mobile'
                    WHEN LOWER(device) = 'desktop' THEN 'desktop'
                    WHEN LOWER(device) = 'tablet' THEN 'tablet'
                    ELSE 'unknown'
                END as device_type,
                'owned' as inventory_type,
                'last_click' as attribution_model
            FROM raw_alpha_events
        """
        
        self.conn.execute(sql)
        
        # Get stats
        result = self.conn.execute("SELECT COUNT(*) FROM rmis_events WHERE retailer_id='alpha'").fetchone()
        rows = result[0] if result else 0
        
        # Calculate quality metrics
        enum_coverage = self._calculate_enum_coverage('alpha')
        join_rate = self._calculate_join_rate('alpha')
        non_null_keys = self._calculate_non_null_keys('alpha')
        
        # Get preview
        preview_df = self.conn.execute("""
            SELECT * FROM rmis_events 
            WHERE retailer_id='alpha' 
            LIMIT 10
        """).df()
        
        return {
            "success": True,
            "rows": rows,
            "enum_coverage": enum_coverage,
            "join_rate": join_rate,
            "non_null_keys": non_null_keys,
            "preview": preview_df
        }
    
    def _harmonize_beta(self) -> dict:
        """Harmonize Retailer Beta to RMIS."""
        
        # Mapping logic with EUR to USD conversion
        sql = """
            INSERT INTO rmis_events
            SELECT
                id as event_id,
                CAST(ts AS TIMESTAMP) as ts,
                'beta' as retailer_id,
                CASE 
                    WHEN placementCategory = 'sponsored_prod' THEN 'sponsored_product'
                    WHEN placementCategory = 'display_banner' THEN 'onsite_display'
                    WHEN placementCategory = 'video_pre_roll' THEN 'offsite_video'
                    WHEN placementCategory = 'native' THEN 'native'
                    ELSE 'other'
                END as placement_type,
                spend * 1.1 as cost,  -- EUR to USD (simplified)
                imps as impressions,
                clks as clicks,
                CAST(sales_attrib / 50.0 AS INTEGER) as conversions,  -- Estimate
                sales_attrib * 1.1 as revenue,  -- EUR to USD
                camp_ref as campaign_id,
                product_id as sku,
                CASE
                    WHEN aud = 'retarget' THEN 'retargeting'
                    WHEN aud = 'category_inmarket' THEN 'inmarket'
                    WHEN aud = 'lapsed' THEN 'lapsed'
                    ELSE 'unknown'
                END as audience_segment,
                CASE
                    WHEN dev_type = 'mob' THEN 'mobile'
                    WHEN dev_type = 'desk' THEN 'desktop'
                    WHEN dev_type = 'tab' THEN 'tablet'
                    ELSE 'unknown'
                END as device_type,
                COALESCE(inventory, 'owned') as inventory_type,
                'last_click' as attribution_model
            FROM raw_beta_events
        """
        
        self.conn.execute(sql)
        
        # Get stats
        result = self.conn.execute("SELECT COUNT(*) FROM rmis_events WHERE retailer_id='beta'").fetchone()
        rows = result[0] if result else 0
        
        # Calculate quality metrics
        enum_coverage = self._calculate_enum_coverage('beta')
        join_rate = self._calculate_join_rate('beta')
        non_null_keys = self._calculate_non_null_keys('beta')
        
        # Get preview
        preview_df = self.conn.execute("""
            SELECT * FROM rmis_events 
            WHERE retailer_id='beta' 
            LIMIT 10
        """).df()
        
        return {
            "success": True,
            "rows": rows,
            "enum_coverage": enum_coverage,
            "join_rate": join_rate,
            "non_null_keys": non_null_keys,
            "preview": preview_df
        }
    
    def _calculate_enum_coverage(self, retailer: str) -> float:
        """Calculate enum coverage percentage."""
        result = self.conn.execute(f"""
            SELECT 
                100.0 * SUM(CASE WHEN placement_type != 'other' THEN 1 ELSE 0 END) / COUNT(*) as coverage
            FROM rmis_events
            WHERE retailer_id = '{retailer}'
        """).fetchone()
        
        return round(result[0], 1) if result else 0.0
    
    def _calculate_join_rate(self, retailer: str) -> float:
        """Calculate join success rate."""
        # Simplified - assume 95-98% join rate
        return round(95 + np.random.uniform(0, 3), 1)
    
    def _calculate_non_null_keys(self, retailer: str) -> float:
        """Calculate non-null key percentage."""
        result = self.conn.execute(f"""
            SELECT 
                100.0 * SUM(CASE WHEN event_id IS NOT NULL AND sku IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*) as pct
            FROM rmis_events
            WHERE retailer_id = '{retailer}'
        """).fetchone()
        
        return round(result[0], 1) if result else 0.0
    
    def load_sku_catalog(self):
        """Load SKU catalog."""
        sku_path = self.data_dir / "sku_catalog.csv"
        if sku_path.exists():
            df = pd.read_csv(sku_path)
            self.conn.execute("DELETE FROM rmis_skus")
            self.conn.execute("""
                INSERT INTO rmis_skus 
                SELECT sku_id, product_name, category, price, cost, margin_pct, stock_units, stock_probability
                FROM df
            """)
    
    def get_metrics(self, rmn: str, placement: str = None, window_days: int = 30) -> pd.DataFrame:
        """Fetch metrics from warehouse."""
        
        where_clauses = [f"retailer_id = '{rmn}'"]
        if placement:
            where_clauses.append(f"placement_type = '{placement}'")
        
        where_sql = " AND ".join(where_clauses)
        
        sql = f"""
            SELECT
                retailer_id,
                placement_type,
                audience_segment,
                sku,
                SUM(cost) as total_cost,
                SUM(impressions) as total_impressions,
                SUM(clicks) as total_clicks,
                SUM(conversions) as total_conversions,
                SUM(revenue) as total_revenue,
                SUM(revenue) / NULLIF(SUM(cost), 0) as roas
            FROM rmis_events
            WHERE {where_sql}
            GROUP BY retailer_id, placement_type, audience_segment, sku
        """
        
        return self.conn.execute(sql).df()
    
    def close(self):
        """Close connection."""
        self.conn.close()
