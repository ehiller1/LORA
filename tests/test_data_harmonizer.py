"""Tests for Data Harmonizer Agent."""

import pytest
import polars as pl
from pathlib import Path
import tempfile
import yaml

from src.agents.data_harmonizer import DataHarmonizerAgent, MappingEngine


@pytest.fixture
def sample_mapping_config():
    """Sample mapping configuration."""
    return {
        "retailer_id": "test_retailer",
        "version": "1.0.0",
        "sources": {
            "events": {
                "table": "test_events",
                "fields": {
                    "event_id": {"from": "evt_id"},
                    "ts": {"from": "timestamp"},
                    "retailer_id": {"const": "test_retailer"},
                    "placement_type": {
                        "from": "placement",
                        "map": {
                            "sp": "sponsored_product",
                            "od": "onsite_display"
                        }
                    },
                    "cost": {"from": "spend", "default": 0.0},
                    "impressions": {"from": "imps", "default": 0}
                }
            }
        },
        "validation": {
            "tests": [
                {
                    "name": "required_fields",
                    "type": "not_null",
                    "fields": ["event_id", "ts"]
                }
            ]
        }
    }


@pytest.fixture
def sample_raw_data():
    """Sample raw retailer data."""
    return pl.DataFrame({
        "evt_id": ["evt_001", "evt_002", "evt_003"],
        "timestamp": ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z", "2024-01-01T02:00:00Z"],
        "placement": ["sp", "od", "sp"],
        "spend": [100.0, 150.0, 200.0],
        "imps": [1000, 1500, 2000]
    })


def test_mapping_engine_initialization(sample_mapping_config):
    """Test mapping engine initialization."""
    engine = MappingEngine(sample_mapping_config)
    
    assert engine.retailer_id == "test_retailer"
    assert engine.version == "1.0.0"
    assert "events" in engine.sources


def test_field_mapping(sample_mapping_config, sample_raw_data):
    """Test basic field mapping."""
    engine = MappingEngine(sample_mapping_config)
    
    mapped_df = engine.map_events(sample_raw_data)
    
    # Check mapped fields exist
    assert "event_id" in mapped_df.columns
    assert "ts" in mapped_df.columns
    assert "retailer_id" in mapped_df.columns
    assert "placement_type" in mapped_df.columns
    assert "cost" in mapped_df.columns
    
    # Check values
    assert mapped_df["event_id"][0] == "evt_001"
    assert mapped_df["retailer_id"][0] == "test_retailer"
    assert mapped_df["placement_type"][0] == "sponsored_product"
    assert mapped_df["cost"][0] == 100.0


def test_constant_field_mapping(sample_mapping_config, sample_raw_data):
    """Test constant field mapping."""
    engine = MappingEngine(sample_mapping_config)
    
    mapped_df = engine.map_events(sample_raw_data)
    
    # All rows should have same retailer_id
    assert all(mapped_df["retailer_id"] == "test_retailer")


def test_value_mapping(sample_mapping_config, sample_raw_data):
    """Test value mapping (dictionary lookup)."""
    engine = MappingEngine(sample_mapping_config)
    
    mapped_df = engine.map_events(sample_raw_data)
    
    # Check placement type mapping
    assert mapped_df["placement_type"][0] == "sponsored_product"  # sp -> sponsored_product
    assert mapped_df["placement_type"][1] == "onsite_display"  # od -> onsite_display


def test_default_values(sample_mapping_config):
    """Test default value handling."""
    engine = MappingEngine(sample_mapping_config)
    
    # Data without spend field
    data = pl.DataFrame({
        "evt_id": ["evt_001"],
        "timestamp": ["2024-01-01T00:00:00Z"],
        "placement": ["sp"],
        "imps": [1000]
    })
    
    mapped_df = engine.map_events(data)
    
    # Should use default value for cost
    assert "cost" in mapped_df.columns


def test_validation(sample_mapping_config, sample_raw_data):
    """Test data validation."""
    engine = MappingEngine(sample_mapping_config)
    
    mapped_df = engine.map_events(sample_raw_data)
    
    # Validation should pass for valid data
    validation_result = engine._validate(mapped_df)
    assert validation_result["passed"] == True
    assert len(validation_result["issues"]) == 0


def test_validation_failures(sample_mapping_config):
    """Test validation failure detection."""
    engine = MappingEngine(sample_mapping_config)
    
    # Data with null required field
    data = pl.DataFrame({
        "evt_id": [None, "evt_002"],
        "timestamp": ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"],
        "placement": ["sp", "od"],
        "spend": [100.0, 150.0],
        "imps": [1000, 1500]
    })
    
    mapped_df = engine.map_events(data)
    validation_result = engine._validate(mapped_df)
    
    # Should detect null in required field
    assert validation_result["passed"] == False
    assert len(validation_result["issues"]) > 0


def test_data_harmonizer_agent():
    """Test Data Harmonizer Agent end-to-end."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create mapping file
        mapping_config = {
            "retailer_id": "test_retailer",
            "version": "1.0.0",
            "sources": {
                "events": {
                    "table": "test_events",
                    "fields": {
                        "event_id": {"from": "evt_id"},
                        "ts": {"from": "timestamp"},
                        "retailer_id": {"const": "test_retailer"},
                        "cost": {"from": "spend"}
                    }
                }
            },
            "validation": {"tests": []}
        }
        
        mapping_path = tmpdir / "mapping.yaml"
        with open(mapping_path, 'w') as f:
            yaml.dump(mapping_config, f)
        
        # Create input data
        input_data = pl.DataFrame({
            "evt_id": ["evt_001", "evt_002"],
            "timestamp": ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"],
            "spend": [100.0, 150.0]
        })
        
        input_path = tmpdir / "input.parquet"
        input_data.write_parquet(input_path)
        
        # Initialize agent and harmonize
        agent = DataHarmonizerAgent(mapping_path)
        output_path = tmpdir / "output.parquet"
        
        stats = agent.harmonize(input_path, output_path)
        
        # Check stats
        assert stats["input_rows"] == 2
        assert stats["output_rows"] == 2
        assert stats["retailer_id"] == "test_retailer"
        
        # Check output file exists
        assert output_path.exists()
        
        # Load and verify output
        output_data = pl.read_parquet(output_path)
        assert "event_id" in output_data.columns
        assert "retailer_id" in output_data.columns


def test_anomaly_detection():
    """Test anomaly detection."""
    agent = DataHarmonizerAgent()
    
    # Data with anomalies
    data = pl.DataFrame({
        "event_id": ["evt_001", "evt_002", "evt_003"],
        "cost": [100.0, -50.0, 200.0],  # Negative cost
        "ts": ["2024-01-01T00:00:00Z", "2025-12-31T00:00:00Z", "2024-01-01T02:00:00Z"]  # Future date
    })
    
    anomalies = agent.detect_anomalies(data)
    
    # Should detect negative cost and future date
    assert len(anomalies) > 0
    anomaly_types = [a["type"] for a in anomalies]
    assert "negative_cost" in anomaly_types
    assert "future_timestamp" in anomaly_types


def test_high_null_rate_detection():
    """Test high null rate detection."""
    agent = DataHarmonizerAgent()
    
    # Data with high null rate
    data = pl.DataFrame({
        "event_id": ["evt_001", "evt_002", "evt_003"],
        "optional_field": [None, None, "value"]
    })
    
    anomalies = agent.detect_anomalies(data)
    
    # Should detect high null rate
    high_null_anomalies = [a for a in anomalies if a["type"] == "high_null_rate"]
    assert len(high_null_anomalies) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
