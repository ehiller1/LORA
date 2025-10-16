"""Data Harmonizer Agent - Maps retailer schemas to RMIS."""

import yaml
import pandas as pd
import polars as pl
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging

from ..schemas.rmis import (
    RMISEvent,
    PlacementType,
    AttributionModel,
    InventoryType,
)

logger = logging.getLogger(__name__)


class MappingEngine:
    """Engine for applying retailer → RMIS mappings."""
    
    def __init__(self, mapping_config: Dict[str, Any]):
        """Initialize mapping engine with configuration.
        
        Args:
            mapping_config: Parsed YAML mapping configuration
        """
        self.config = mapping_config
        self.retailer_id = mapping_config.get("retailer_id")
        self.version = mapping_config.get("version")
        self.sources = mapping_config.get("sources", {})
        self.crosswalks = mapping_config.get("crosswalks", {})
        self.validation_rules = mapping_config.get("validation", {}).get("tests", [])
        
    def map_events(self, df: Union[pd.DataFrame, pl.DataFrame]) -> pl.DataFrame:
        """Map raw retailer events to RMIS format.
        
        Args:
            df: Raw retailer event data
            
        Returns:
            RMIS-normalized event dataframe
        """
        # Convert to polars for efficient processing
        if isinstance(df, pd.DataFrame):
            df = pl.from_pandas(df)
            
        event_mapping = self.sources.get("events", {})
        if not event_mapping:
            raise ValueError("No event mapping found in configuration")
            
        source_table = event_mapping.get("table")
        field_mappings = event_mapping.get("fields", {})
        
        logger.info(f"Mapping {len(df)} events from {source_table} to RMIS")
        
        # Apply field mappings
        mapped_df = self._apply_field_mappings(df, field_mappings)
        
        # Apply tagging normalizer rules
        mapped_df = self._apply_tagging_normalizer(mapped_df)
        
        # Validate
        validation_results = self._validate(mapped_df)
        if not validation_results["passed"]:
            logger.warning(f"Validation issues: {validation_results['issues']}")
            
        return mapped_df
    
    def _apply_field_mappings(
        self,
        df: pl.DataFrame,
        field_mappings: Dict[str, Any]
    ) -> pl.DataFrame:
        """Apply field-level mappings."""
        
        expressions = []
        
        for rmis_field, mapping_spec in field_mappings.items():
            if isinstance(mapping_spec, dict):
                # Complex mapping
                if "from" in mapping_spec:
                    # Direct field mapping
                    source_field = mapping_spec["from"]
                    expr = pl.col(source_field)
                    
                    # Apply transformations
                    if "transform" in mapping_spec:
                        expr = self._apply_transform(expr, mapping_spec["transform"])
                    
                    # Apply normalization
                    if "normalize" in mapping_spec:
                        for norm in mapping_spec["normalize"]:
                            expr = self._apply_normalization(expr, norm)
                    
                    # Apply mapping dictionary
                    if "map" in mapping_spec:
                        mapping_dict = mapping_spec["map"]
                        # Create case-when for mapping
                        case_expr = pl.when(expr == list(mapping_dict.keys())[0]).then(list(mapping_dict.values())[0])
                        for k, v in list(mapping_dict.items())[1:]:
                            case_expr = case_expr.when(expr == k).then(v)
                        expr = case_expr.otherwise(expr)
                    
                    expressions.append(expr.alias(rmis_field))
                    
                elif "const" in mapping_spec:
                    # Constant value
                    expressions.append(pl.lit(mapping_spec["const"]).alias(rmis_field))
                    
                elif "derive" in mapping_spec:
                    # Derived expression (simplified - would need full SQL parser)
                    derive_expr = mapping_spec["derive"].get("expr", "")
                    # For now, just handle simple coalesce
                    if "coalesce" in derive_expr.lower():
                        fields = [f.strip() for f in derive_expr.replace("coalesce(", "").replace(")", "").split(",")]
                        expr = pl.coalesce([pl.col(f) for f in fields if f in df.columns])
                        expressions.append(expr.alias(rmis_field))
                    else:
                        # Default to null for complex expressions
                        expressions.append(pl.lit(None).alias(rmis_field))
                        
                elif "candidates" in mapping_spec:
                    # Multiple candidate fields with fallback
                    candidates = mapping_spec["candidates"]
                    fallback = mapping_spec.get("fallback")
                    
                    # Try first candidate
                    first_candidate = candidates[0]
                    if "from" in first_candidate:
                        expr = pl.col(first_candidate["from"])
                        if "map" in first_candidate:
                            mapping_dict = first_candidate["map"]
                            case_expr = pl.when(expr == list(mapping_dict.keys())[0]).then(list(mapping_dict.values())[0])
                            for k, v in list(mapping_dict.items())[1:]:
                                case_expr = case_expr.when(expr == k).then(v)
                            expr = case_expr.otherwise(pl.lit(fallback) if fallback else expr)
                    else:
                        expr = pl.lit(fallback) if fallback else pl.lit(None)
                    
                    expressions.append(expr.alias(rmis_field))
                    
                elif "default" in mapping_spec:
                    # Default value
                    expressions.append(pl.lit(mapping_spec["default"]).alias(rmis_field))
                    
            else:
                # Simple string mapping (field name)
                if mapping_spec in df.columns:
                    expressions.append(pl.col(mapping_spec).alias(rmis_field))
                else:
                    expressions.append(pl.lit(None).alias(rmis_field))
        
        return df.select(expressions)
    
    def _apply_transform(self, expr: pl.Expr, transform: str) -> pl.Expr:
        """Apply transformation to expression."""
        if transform == "to_utc":
            return expr.cast(pl.Datetime).dt.replace_time_zone("UTC")
        elif transform == "to_fraction":
            return expr / 100.0
        elif transform == "dma_to_region":
            # Simplified - would need actual DMA mapping
            return expr
        return expr
    
    def _apply_normalization(self, expr: pl.Expr, normalization: str) -> pl.Expr:
        """Apply normalization to expression."""
        if normalization == "lower":
            return expr.str.to_lowercase()
        elif normalization == "upper":
            return expr.str.to_uppercase()
        elif normalization == "bool_from_int":
            return expr.cast(pl.Boolean)
        return expr
    
    def _apply_tagging_normalizer(self, df: pl.DataFrame) -> pl.DataFrame:
        """Apply tagging normalization rules."""
        tagging_rules = self.config.get("tagging_normalizer", {}).get("rules", [])
        
        for rule in tagging_rules:
            rule_name = rule.get("name")
            if_condition = rule.get("if", {})
            then_action = rule.get("then", {})
            
            # Simple implementation for placement_type normalization
            if rule_name == "placement_normalization":
                field = if_condition.get("field")
                equals_value = if_condition.get("equals")
                
                if field in df.columns:
                    # Apply the normalization
                    derive_expr = then_action.get("derive", {}).get("expr", "")
                    # Simplified - just set to a default
                    df = df.with_columns(
                        pl.when(pl.col(field) == equals_value)
                        .then(pl.lit("sponsored_product"))
                        .otherwise(pl.col(field))
                        .alias(field)
                    )
        
        return df
    
    def _validate(self, df: pl.DataFrame) -> Dict[str, Any]:
        """Validate mapped data against rules."""
        issues = []
        
        for test in self.validation_rules:
            test_name = test.get("name")
            test_type = test.get("type")
            
            if test_type == "not_null":
                fields = test.get("fields", [])
                for field in fields:
                    if field in df.columns:
                        null_count = df[field].null_count()
                        if null_count > 0:
                            issues.append(f"{test_name}: {field} has {null_count} null values")
            
            elif test_type == "in_set":
                field = test.get("field")
                allowed = test.get("allowed", [])
                if field in df.columns:
                    invalid = df.filter(~pl.col(field).is_in(allowed))
                    if len(invalid) > 0:
                        issues.append(f"{test_name}: {field} has {len(invalid)} invalid values")
            
            elif test_type == "regex":
                field = test.get("field")
                pattern = test.get("pattern")
                if field in df.columns:
                    invalid = df.filter(~pl.col(field).str.contains(pattern))
                    if len(invalid) > 0:
                        issues.append(f"{test_name}: {field} has {len(invalid)} values not matching pattern")
            
            elif test_type == "min_cell":
                threshold = test.get("threshold", 50)
                # Check minimum cell sizes for aggregations
                # Simplified - would need more sophisticated grouping logic
                pass
        
        return {
            "passed": len(issues) == 0,
            "issues": issues,
            "total_tests": len(self.validation_rules)
        }


class DataHarmonizerAgent:
    """Agent for harmonizing retailer data to RMIS."""
    
    def __init__(self, mapping_path: Optional[Path] = None):
        """Initialize Data Harmonizer Agent.
        
        Args:
            mapping_path: Path to retailer mapping YAML file
        """
        self.mapping_path = mapping_path
        self.mapping_engine = None
        
        if mapping_path and mapping_path.exists():
            self.load_mapping(mapping_path)
    
    def load_mapping(self, mapping_path: Path) -> None:
        """Load retailer mapping configuration.
        
        Args:
            mapping_path: Path to mapping YAML file
        """
        logger.info(f"Loading mapping from {mapping_path}")
        with open(mapping_path, 'r') as f:
            mapping_config = yaml.safe_load(f)
        
        self.mapping_engine = MappingEngine(mapping_config)
        logger.info(f"Loaded mapping for retailer: {self.mapping_engine.retailer_id}")
    
    def harmonize(
        self,
        input_path: Path,
        output_path: Path,
        entity_type: str = "events"
    ) -> Dict[str, Any]:
        """Harmonize retailer data to RMIS format.
        
        Args:
            input_path: Path to input data file (parquet, csv)
            output_path: Path to output RMIS data file
            entity_type: Type of entity to harmonize (events, sku, audience)
            
        Returns:
            Harmonization statistics
        """
        if not self.mapping_engine:
            raise ValueError("No mapping loaded. Call load_mapping() first.")
        
        logger.info(f"Harmonizing {entity_type} from {input_path}")
        
        # Read input data
        if input_path.suffix == ".parquet":
            df = pl.read_parquet(input_path)
        elif input_path.suffix == ".csv":
            df = pl.read_csv(input_path)
        else:
            raise ValueError(f"Unsupported file format: {input_path.suffix}")
        
        input_rows = len(df)
        logger.info(f"Read {input_rows} rows from {input_path}")
        
        # Map to RMIS
        if entity_type == "events":
            mapped_df = self.mapping_engine.map_events(df)
        else:
            raise NotImplementedError(f"Entity type {entity_type} not yet implemented")
        
        output_rows = len(mapped_df)
        
        # Write output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        mapped_df.write_parquet(output_path)
        logger.info(f"Wrote {output_rows} rows to {output_path}")
        
        return {
            "input_rows": input_rows,
            "output_rows": output_rows,
            "retailer_id": self.mapping_engine.retailer_id,
            "entity_type": entity_type,
            "output_path": str(output_path),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def detect_anomalies(self, df: pl.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in harmonized data.
        
        Args:
            df: Harmonized RMIS dataframe
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Check for unusual null rates
        for col in df.columns:
            null_rate = df[col].null_count() / len(df)
            if null_rate > 0.5:
                anomalies.append({
                    "type": "high_null_rate",
                    "field": col,
                    "null_rate": null_rate,
                    "severity": "warning"
                })
        
        # Check for unusual distributions
        if "cost" in df.columns:
            cost_stats = df["cost"].describe()
            # Check for negative costs
            negative_costs = df.filter(pl.col("cost") < 0)
            if len(negative_costs) > 0:
                anomalies.append({
                    "type": "negative_cost",
                    "count": len(negative_costs),
                    "severity": "error"
                })
        
        # Check for future dates
        if "ts" in df.columns:
            future_dates = df.filter(pl.col("ts") > datetime.utcnow())
            if len(future_dates) > 0:
                anomalies.append({
                    "type": "future_timestamp",
                    "count": len(future_dates),
                    "severity": "warning"
                })
        
        return anomalies


def main():
    """CLI entry point for Data Harmonizer Agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Harmonizer Agent")
    parser.add_argument("--retailer-mapping", type=Path, required=True, help="Path to retailer mapping YAML")
    parser.add_argument("--input", type=Path, required=True, help="Path to input data file")
    parser.add_argument("--output", type=Path, required=True, help="Path to output RMIS file")
    parser.add_argument("--entity-type", default="events", help="Entity type to harmonize")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Run harmonization
    agent = DataHarmonizerAgent(args.retailer_mapping)
    stats = agent.harmonize(args.input, args.output, args.entity_type)
    
    print("\n=== Harmonization Complete ===")
    print(f"Retailer: {stats['retailer_id']}")
    print(f"Input rows: {stats['input_rows']}")
    print(f"Output rows: {stats['output_rows']}")
    print(f"Output: {stats['output_path']}")


if __name__ == "__main__":
    main()
