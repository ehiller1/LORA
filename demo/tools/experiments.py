"""Experiment design and measurement."""

import pandas as pd
import numpy as np
from typing import Dict, List
from pathlib import Path


class ExperimentDesigner:
    """Design and analyze experiments."""
    
    def __init__(self):
        """Initialize experiment designer."""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.geo_regions = None
        self._load_geo_data()
    
    def _load_geo_data(self):
        """Load geographic regions."""
        geo_path = self.data_dir / "geo_regions.csv"
        if geo_path.exists():
            self.geo_regions = pd.read_csv(geo_path)
    
    def design_experiment(
        self,
        exp_type: str,
        min_cells: int = 2,
        power: float = 0.8,
        mde: float = 0.1
    ) -> Dict:
        """
        Design an experiment.
        
        Args:
            exp_type: Type of experiment
            min_cells: Minimum number of cells
            power: Statistical power target
            mde: Minimum detectable effect
        
        Returns:
            Experiment design dict
        """
        
        if exp_type == "Geo Split Test":
            return self._design_geo_split(min_cells, power, mde)
        elif exp_type == "Audience Holdout":
            return self._design_audience_holdout(min_cells, power, mde)
        elif exp_type == "Budget Pacing Test":
            return self._design_budget_pacing(min_cells, power, mde)
        else:
            return self._design_geo_split(min_cells, power, mde)
    
    def _design_geo_split(self, min_cells: int, power: float, mde: float) -> Dict:
        """Design geographic split test."""
        
        # Calculate sample size needed
        # Simplified formula: n ≈ 16 * (1/mde)^2 for 80% power
        sample_size_per_cell = int(16 / (mde ** 2))
        
        # Select geo regions
        if self.geo_regions is not None:
            # Sort by population and select balanced regions
            regions = self.geo_regions.sort_values('population', ascending=False).head(min_cells * 2)
            
            # Assign to treatment/control
            regions['cell'] = ['Treatment' if i % 2 == 0 else 'Control' 
                              for i in range(len(regions))]
            
            cell_assignment = regions[['dma_code', 'dma_name', 'population', 'cell']]
        else:
            # Fallback
            cell_assignment = pd.DataFrame([
                {'dma_code': 'DMA_001', 'dma_name': 'Market Region 1', 'population': 2500000, 'cell': 'Treatment'},
                {'dma_code': 'DMA_002', 'dma_name': 'Market Region 2', 'population': 2400000, 'cell': 'Control'},
                {'dma_code': 'DMA_003', 'dma_name': 'Market Region 3', 'population': 2300000, 'cell': 'Treatment'},
                {'dma_code': 'DMA_004', 'dma_name': 'Market Region 4', 'population': 2200000, 'cell': 'Control'}
            ])
        
        # Generate SQL for readout
        sql = self._generate_geo_readout_sql(cell_assignment)
        
        return {
            'type': 'Geo Split Test',
            'cells': len(cell_assignment['cell'].unique()),
            'sample_size': sample_size_per_cell,
            'power': power,
            'mde': mde,
            'cell_assignment': cell_assignment,
            'sql': sql,
            'interpretation': f"Run for 14+ days. Compare treatment vs control. MDE: {mde*100:.0f}%"
        }
    
    def _design_audience_holdout(self, min_cells: int, power: float, mde: float) -> Dict:
        """Design audience holdout test."""
        
        sample_size_per_cell = int(16 / (mde ** 2))
        
        cell_assignment = pd.DataFrame([
            {'audience': 'Retargeting', 'segment': 'Treatment', 'size': 400000},
            {'audience': 'Retargeting', 'segment': 'Holdout', 'size': 100000},
            {'audience': 'In-Market', 'segment': 'Treatment', 'size': 800000},
            {'audience': 'In-Market', 'segment': 'Holdout', 'size': 200000}
        ])
        
        sql = """
-- Audience Holdout Readout
SELECT
    audience,
    segment,
    COUNT(DISTINCT user_id) as users,
    SUM(conversions) as total_conversions,
    SUM(revenue) as total_revenue,
    SUM(revenue) / COUNT(DISTINCT user_id) as revenue_per_user
FROM experiment_results
WHERE experiment_id = 'audience_holdout_001'
    AND date BETWEEN '2024-01-01' AND '2024-01-14'
GROUP BY audience, segment
ORDER BY audience, segment;

-- Calculate lift
WITH metrics AS (
    SELECT
        audience,
        MAX(CASE WHEN segment = 'Treatment' THEN revenue_per_user END) as treatment_rpu,
        MAX(CASE WHEN segment = 'Holdout' THEN revenue_per_user END) as holdout_rpu
    FROM (
        SELECT
            audience,
            segment,
            SUM(revenue) / COUNT(DISTINCT user_id) as revenue_per_user
        FROM experiment_results
        WHERE experiment_id = 'audience_holdout_001'
        GROUP BY audience, segment
    )
    GROUP BY audience
)
SELECT
    audience,
    treatment_rpu,
    holdout_rpu,
    (treatment_rpu - holdout_rpu) / holdout_rpu as lift_pct,
    treatment_rpu - holdout_rpu as incremental_rpu
FROM metrics;
"""
        
        return {
            'type': 'Audience Holdout',
            'cells': 2,
            'sample_size': sample_size_per_cell,
            'power': power,
            'mde': mde,
            'cell_assignment': cell_assignment,
            'sql': sql,
            'interpretation': f"Holdout 20% of each audience. Measure incremental lift. MDE: {mde*100:.0f}%"
        }
    
    def _design_budget_pacing(self, min_cells: int, power: float, mde: float) -> Dict:
        """Design budget pacing test."""
        
        sample_size_per_cell = int(16 / (mde ** 2))
        
        cell_assignment = pd.DataFrame([
            {'strategy': 'Even Pacing', 'daily_budget': 10000, 'duration_days': 14},
            {'strategy': 'Front-Loaded', 'daily_budget': 15000, 'duration_days': 10},
            {'strategy': 'Back-Loaded', 'daily_budget': 8000, 'duration_days': 18}
        ])
        
        sql = """
-- Budget Pacing Test Readout
SELECT
    pacing_strategy,
    DATE_TRUNC('day', ts) as date,
    SUM(cost) as daily_spend,
    SUM(conversions) as daily_conversions,
    SUM(revenue) as daily_revenue,
    SUM(revenue) / SUM(cost) as daily_roas
FROM experiment_results
WHERE experiment_id = 'budget_pacing_001'
GROUP BY pacing_strategy, DATE_TRUNC('day', ts)
ORDER BY pacing_strategy, date;

-- Overall performance by strategy
SELECT
    pacing_strategy,
    SUM(cost) as total_spend,
    SUM(conversions) as total_conversions,
    SUM(revenue) as total_revenue,
    SUM(revenue) / SUM(cost) as blended_roas,
    COUNT(DISTINCT DATE_TRUNC('day', ts)) as days_active
FROM experiment_results
WHERE experiment_id = 'budget_pacing_001'
GROUP BY pacing_strategy
ORDER BY blended_roas DESC;
"""
        
        return {
            'type': 'Budget Pacing Test',
            'cells': 3,
            'sample_size': sample_size_per_cell,
            'power': power,
            'mde': mde,
            'cell_assignment': cell_assignment,
            'sql': sql,
            'interpretation': f"Test different pacing strategies. Compare ROAS and efficiency. MDE: {mde*100:.0f}%"
        }
    
    def _generate_geo_readout_sql(self, cell_assignment: pd.DataFrame) -> str:
        """Generate SQL for geo test readout."""
        
        treatment_dmas = cell_assignment[cell_assignment['cell'] == 'Treatment']['dma_code'].tolist()
        control_dmas = cell_assignment[cell_assignment['cell'] == 'Control']['dma_code'].tolist()
        
        treatment_list = "', '".join(treatment_dmas)
        control_list = "', '".join(control_dmas)
        
        sql = f"""
-- Geo Split Test Readout
-- Treatment DMAs: {treatment_list}
-- Control DMAs: {control_list}

WITH daily_metrics AS (
    SELECT
        dma_code,
        CASE 
            WHEN dma_code IN ('{treatment_list}') THEN 'Treatment'
            WHEN dma_code IN ('{control_list}') THEN 'Control'
        END as cell,
        DATE_TRUNC('day', ts) as date,
        SUM(cost) as spend,
        SUM(conversions) as conversions,
        SUM(revenue) as revenue
    FROM rmis_events
    WHERE dma_code IN ('{treatment_list}', '{control_list}')
        AND ts BETWEEN '2024-01-01' AND '2024-01-14'
    GROUP BY dma_code, cell, DATE_TRUNC('day', ts)
)
SELECT
    cell,
    COUNT(DISTINCT dma_code) as num_dmas,
    SUM(spend) as total_spend,
    SUM(conversions) as total_conversions,
    SUM(revenue) as total_revenue,
    SUM(revenue) / SUM(spend) as roas,
    AVG(conversions) as avg_daily_conversions,
    STDDEV(conversions) as stddev_conversions
FROM daily_metrics
GROUP BY cell;

-- Statistical test (t-test approximation)
WITH cell_stats AS (
    SELECT
        cell,
        AVG(conversions) as mean_conversions,
        STDDEV(conversions) as sd_conversions,
        COUNT(*) as n
    FROM daily_metrics
    GROUP BY cell
)
SELECT
    t.mean_conversions as treatment_mean,
    c.mean_conversions as control_mean,
    (t.mean_conversions - c.mean_conversions) / c.mean_conversions as lift_pct,
    -- t-statistic (simplified)
    (t.mean_conversions - c.mean_conversions) / 
        SQRT((t.sd_conversions * t.sd_conversions / t.n) + 
             (c.sd_conversions * c.sd_conversions / c.n)) as t_stat
FROM 
    (SELECT * FROM cell_stats WHERE cell = 'Treatment') t,
    (SELECT * FROM cell_stats WHERE cell = 'Control') c;
"""
        
        return sql
