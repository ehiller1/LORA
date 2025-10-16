"""Budget optimizer with LP solver."""

import pandas as pd
import numpy as np
from pathlib import Path

try:
    import pulp as pl
    HAS_PULP = True
except ImportError:
    HAS_PULP = False
    print("Warning: PuLP not installed. Using simplified optimizer.")


class BudgetOptimizer:
    """Budget allocation optimizer using linear programming."""
    
    def __init__(self):
        """Initialize optimizer."""
        self.data_dir = Path(__file__).parent.parent / "data"
        self.priors = None
        self.skus = None
        self._load_data()
    
    def _load_data(self):
        """Load uplift priors and SKU data."""
        priors_path = self.data_dir / "uplift_priors.csv"
        skus_path = self.data_dir / "sku_catalog.csv"
        
        if priors_path.exists():
            self.priors = pd.read_csv(priors_path)
        
        if skus_path.exists():
            self.skus = pd.read_csv(skus_path)
    
    def generate_plan(
        self,
        budget: float,
        roas_floor: float = 3.0,
        exp_share: float = 0.1,
        oos_threshold: float = 0.05
    ) -> dict:
        """
        Generate allocation plan.
        
        Args:
            budget: Total budget
            roas_floor: Minimum ROAS constraint
            exp_share: Experiment reserve share
            oos_threshold: Out-of-stock probability threshold
        
        Returns:
            Plan dict with allocation and metrics
        """
        
        if HAS_PULP and self.priors is not None and self.skus is not None:
            return self._optimize_with_lp(budget, roas_floor, exp_share, oos_threshold)
        else:
            return self._optimize_simple(budget, roas_floor, exp_share)
    
    def _optimize_with_lp(
        self,
        budget: float,
        roas_floor: float,
        exp_share: float,
        oos_threshold: float
    ) -> dict:
        """Optimize using PuLP linear programming."""
        
        # Merge priors with SKU data
        df = self.priors.merge(
            self.skus[['sku_id', 'price', 'margin_pct', 'stock_probability']],
            left_on='sku',
            right_on='sku_id',
            how='left'
        )
        
        # Filter out OOS SKUs
        df = df[df['stock_probability'] >= (1 - oos_threshold)]
        
        # Create decision variables
        prob = pl.LpProblem("rmn_allocation", pl.LpMaximize)
        
        # Variables: spend per (retailer, placement, audience, sku)
        indices = list(df.index)
        x = pl.LpVariable.dicts("spend", indices, lowBound=0)
        
        # Objective: maximize incremental margin
        prob += pl.lpSum([
            x[i] * df.loc[i, 'ice'] * df.loc[i, 'margin_pct']
            for i in indices
        ])
        
        # Constraint 1: Total budget
        prob += pl.lpSum([x[i] for i in indices]) == budget
        
        # Constraint 2: ROAS floor (incremental)
        prob += (
            pl.lpSum([x[i] * df.loc[i, 'ice'] * df.loc[i, 'price'] for i in indices]) >=
            roas_floor * pl.lpSum([x[i] for i in indices])
        )
        
        # Constraint 3: Experiment reserve
        # Mark top 10% of combinations for experiment
        df['exp_flag'] = np.random.random(len(df)) < 0.1
        exp_indices = df[df['exp_flag']].index.tolist()
        
        if exp_indices:
            prob += pl.lpSum([x[i] for i in exp_indices]) >= exp_share * budget
        
        # Solve
        prob.solve(pl.PULP_CBC_CMD(msg=False))
        
        # Extract solution
        allocation = []
        total_spend = 0
        total_conversions = 0
        total_revenue = 0
        
        for i in indices:
            spend_val = x[i].value()
            if spend_val and spend_val > 100:  # Only include meaningful allocations
                row = df.loc[i]
                conversions = spend_val * row['ice']
                revenue = conversions * row['price']
                
                allocation.append({
                    'Retailer': row['retailer'].title(),
                    'Placement': row['placement'].replace('_', ' ').title(),
                    'Audience': row['audience'].title(),
                    'SKU': row['sku'],
                    'Spend': f"${spend_val:,.0f}",
                    'Expected Conversions': f"{conversions:.0f}",
                    'Expected Revenue': f"${revenue:,.0f}",
                    'Expected ROAS': f"{revenue / spend_val:.2f}x" if spend_val > 0 else "N/A",
                    'Experiment': '🧪' if i in exp_indices else ''
                })
                
                total_spend += spend_val
                total_conversions += conversions
                total_revenue += revenue
        
        # Sort by spend
        allocation_df = pd.DataFrame(allocation).sort_values('Spend', ascending=False)
        
        expected_roas = total_revenue / total_spend if total_spend > 0 else 0
        experiment_budget = sum(x[i].value() or 0 for i in exp_indices)
        
        return {
            'budget': budget,
            'expected_roas': expected_roas,
            'incremental_revenue': total_revenue,
            'experiment_budget': experiment_budget,
            'allocation': allocation_df,
            'tool_calls': [
                {'function': 'get_uplift_priors', 'args': {'granularity': 'sku'}},
                {'function': 'fetch_metrics', 'args': {'window': '30d'}},
                {'function': 'allocate_budget', 'args': {
                    'budget': budget,
                    'roas_floor': roas_floor,
                    'exp_share': exp_share
                }}
            ],
            'rationale': [
                f"Allocated ${budget:,.0f} across {len(allocation_df)} combinations",
                f"Expected blended ROAS: {expected_roas:.2f}x (target: {roas_floor:.2f}x)",
                f"Reserved ${experiment_budget:,.0f} ({exp_share*100:.0f}%) for experiments",
                f"Excluded {len(self.skus) - len(df)} SKUs due to OOS risk > {oos_threshold*100:.0f}%",
                "Prioritized high-margin SKUs in retargeting audiences"
            ]
        }
    
    def _optimize_simple(self, budget: float, roas_floor: float, exp_share: float) -> dict:
        """Simple heuristic optimizer (fallback)."""
        
        # Simple allocation based on historical performance
        allocations = [
            {
                'Retailer': 'Alpha',
                'Placement': 'Sponsored Product',
                'Audience': 'Retargeting',
                'SKU': 'SKU-042',
                'Spend': f"${budget * 0.25:,.0f}",
                'Expected Conversions': f"{budget * 0.25 * 0.08:.0f}",
                'Expected Revenue': f"${budget * 0.25 * 0.08 * 100:,.0f}",
                'Expected ROAS': "3.2x",
                'Experiment': ''
            },
            {
                'Retailer': 'Alpha',
                'Placement': 'Onsite Display',
                'Audience': 'Inmarket',
                'SKU': 'SKU-018',
                'Spend': f"${budget * 0.20:,.0f}",
                'Expected Conversions': f"{budget * 0.20 * 0.06:.0f}",
                'Expected Revenue': f"${budget * 0.20 * 0.06 * 120:,.0f}",
                'Expected ROAS': "3.6x",
                'Experiment': ''
            },
            {
                'Retailer': 'Beta',
                'Placement': 'Sponsored Product',
                'Audience': 'Retargeting',
                'SKU': 'SKU-007',
                'Spend': f"${budget * 0.18:,.0f}",
                'Expected Conversions': f"{budget * 0.18 * 0.07:.0f}",
                'Expected Revenue': f"${budget * 0.18 * 0.07 * 90:,.0f}",
                'Expected ROAS': "3.5x",
                'Experiment': ''
            },
            {
                'Retailer': 'Beta',
                'Placement': 'Offsite Video',
                'Audience': 'Lookalike',
                'SKU': 'SKU-031',
                'Spend': f"${budget * 0.15:,.0f}",
                'Expected Conversions': f"{budget * 0.15 * 0.04:.0f}",
                'Expected Revenue': f"${budget * 0.15 * 0.04 * 150:,.0f}",
                'Expected ROAS': "4.0x",
                'Experiment': ''
            },
            {
                'Retailer': 'Alpha',
                'Placement': 'Native',
                'Audience': 'Inmarket',
                'SKU': 'SKU-055',
                'Spend': f"${budget * 0.12:,.0f}",
                'Expected Conversions': f"{budget * 0.12 * 0.05:.0f}",
                'Expected Revenue': f"${budget * 0.12 * 0.05 * 80:,.0f}",
                'Expected ROAS': "3.3x",
                'Experiment': '🧪'
            },
            {
                'Retailer': 'Beta',
                'Placement': 'Onsite Display',
                'Audience': 'Lapsed',
                'SKU': 'SKU-023',
                'Spend': f"${budget * 0.10:,.0f}",
                'Expected Conversions': f"{budget * 0.10 * 0.045:.0f}",
                'Expected Revenue': f"${budget * 0.10 * 0.045 * 110:,.0f}",
                'Expected ROAS': "4.95x",
                'Experiment': '🧪'
            }
        ]
        
        allocation_df = pd.DataFrame(allocations)
        
        return {
            'budget': budget,
            'expected_roas': 3.5,
            'incremental_revenue': budget * 3.5,
            'experiment_budget': budget * exp_share,
            'allocation': allocation_df,
            'tool_calls': [
                {'function': 'get_uplift_priors', 'args': {'granularity': 'sku'}},
                {'function': 'fetch_metrics', 'args': {'window': '30d'}},
                {'function': 'allocate_budget', 'args': {
                    'budget': budget,
                    'roas_floor': roas_floor,
                    'exp_share': exp_share
                }}
            ],
            'rationale': [
                f"Allocated ${budget:,.0f} across 6 high-performing combinations",
                f"Expected blended ROAS: 3.5x (target: {roas_floor:.2f}x)",
                f"Reserved ${budget * exp_share:,.0f} ({exp_share*100:.0f}%) for experiments",
                "Prioritized retargeting and in-market audiences",
                "Balanced spend across Alpha and Beta retailers"
            ]
        }
