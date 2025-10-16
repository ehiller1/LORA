"""Generate synthetic retailer data for demo."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from pathlib import Path

# Set seed for reproducibility
np.random.seed(42)

# Create data directory
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)

# Retailer Alpha directory
alpha_dir = data_dir / "retailer_alpha"
alpha_dir.mkdir(exist_ok=True)

# Retailer Beta directory
beta_dir = data_dir / "retailer_beta"
beta_dir.mkdir(exist_ok=True)


def generate_retailer_alpha_data():
    """Generate Retailer Alpha data (CSV format, US-centric)."""
    
    # Events data
    n_events = 10000
    start_date = datetime(2024, 1, 1)
    
    events = []
    for i in range(n_events):
        event = {
            'event_id': f'evt_alpha_{i:06d}',
            'timestamp': (start_date + timedelta(days=np.random.randint(0, 90), 
                                                 hours=np.random.randint(0, 24))).strftime('%Y-%m-%d %H:%M:%S CST'),
            'adType': np.random.choice(['sp', 'SD', 'onsite_disp', 'offsite_vid']),  # Mixed case
            'cost_micros': np.random.randint(100000, 5000000),  # Micros (USD)
            'impressions': np.random.randint(100, 10000),
            'clicks': np.random.randint(0, 500),
            'conv_click_7d': np.random.randint(0, 50),
            'revenue_7d': np.random.randint(0, 5000),
            'campaign_id': f'camp_alpha_{np.random.randint(1, 20):03d}',
            'sku': f'SKU-{np.random.randint(1, 100):03d}',
            'audience_segment': np.random.choice(['retargeting', 'inmarket', 'lookalike', None]),
            'device': np.random.choice(['mobile', 'desktop', 'tablet', 'UNKNOWN']),
            'currency': 'USD',
            'timezone': 'CST'
        }
        events.append(event)
    
    df_events = pd.DataFrame(events)
    df_events.to_csv(alpha_dir / "events.csv", index=False)
    print(f"✅ Generated {len(df_events)} Retailer Alpha events")
    
    # Conversions data
    conversions = []
    for i in range(2000):
        conv = {
            'conversion_id': f'conv_alpha_{i:06d}',
            'event_id': f'evt_alpha_{np.random.randint(0, n_events):06d}',
            'conversion_timestamp': (start_date + timedelta(days=np.random.randint(0, 90))).strftime('%Y-%m-%d %H:%M:%S CST'),
            'conversion_value': np.random.randint(10, 500),
            'attribution_model': np.random.choice(['last_click', 'first_click', 'linear']),
            'sku': f'SKU-{np.random.randint(1, 100):03d}',
            'quantity': np.random.randint(1, 5)
        }
        conversions.append(conv)
    
    df_conversions = pd.DataFrame(conversions)
    df_conversions.to_csv(alpha_dir / "conversions.csv", index=False)
    print(f"✅ Generated {len(df_conversions)} Retailer Alpha conversions")
    
    # Campaigns data
    campaigns = []
    for i in range(1, 21):
        camp = {
            'campaign_id': f'camp_alpha_{i:03d}',
            'campaign_name': f'Alpha Campaign {i}',
            'status': np.random.choice(['ACTIVE', 'PAUSED', 'ENDED']),
            'daily_budget': np.random.randint(1000, 10000),
            'start_date': (start_date + timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d'),
            'objective': np.random.choice(['AWARENESS', 'CONSIDERATION', 'CONVERSION'])
        }
        campaigns.append(camp)
    
    df_campaigns = pd.DataFrame(campaigns)
    df_campaigns.to_csv(alpha_dir / "campaigns.csv", index=False)
    print(f"✅ Generated {len(df_campaigns)} Retailer Alpha campaigns")


def generate_retailer_beta_data():
    """Generate Retailer Beta data (JSONL format, EU-centric)."""
    
    # Events data (JSONL)
    n_events = 8000
    start_date = datetime(2024, 1, 1)
    
    events = []
    for i in range(n_events):
        event = {
            'id': f'beta-evt-{i:06d}',
            'ts': (start_date + timedelta(days=np.random.randint(0, 90), 
                                         hours=np.random.randint(0, 24))).strftime('%Y-%m-%d %H:%M:%S PST'),
            'placementCategory': np.random.choice(['sponsored_prod', 'display_banner', 'video_pre_roll', 'native']),
            'spend': round(np.random.uniform(1.0, 50.0), 2),  # EUR
            'imps': np.random.randint(50, 5000),
            'clks': np.random.randint(0, 200),
            'sales_attrib': round(np.random.uniform(0, 500.0), 2),
            'camp_ref': f'beta_c_{np.random.randint(1, 15):02d}',
            'product_id': f'PROD-{np.random.randint(1, 80):03d}',
            'aud': np.random.choice(['retarget', 'category_inmarket', 'lapsed', None]),
            'dev_type': np.random.choice(['mob', 'desk', 'tab', 'unk']),
            'curr': 'EUR',
            'tz': 'PST',
            'inventory': np.random.choice(['owned', 'partner', None])
        }
        events.append(event)
    
    with open(beta_dir / "log.jsonl", 'w') as f:
        for event in events:
            f.write(json.dumps(event) + '\n')
    
    print(f"✅ Generated {len(events)} Retailer Beta events (JSONL)")


def generate_sku_catalog():
    """Generate SKU catalog with pricing and inventory."""
    
    skus = []
    for i in range(1, 101):
        sku = {
            'sku_id': f'SKU-{i:03d}',
            'product_name': f'Product {i}',
            'category': np.random.choice(['Electronics', 'Home', 'Beauty', 'Food', 'Apparel']),
            'price': round(np.random.uniform(10, 500), 2),
            'cost': round(np.random.uniform(5, 250), 2),
            'margin_pct': round(np.random.uniform(0.2, 0.6), 3),
            'stock_units': np.random.randint(0, 1000),
            'stock_probability': round(np.random.uniform(0.7, 1.0), 3),  # Probability in stock
            'upc': f'{np.random.randint(100000000000, 999999999999)}',
            'brand': np.random.choice(['BrandA', 'BrandB', 'BrandC', 'BrandD'])
        }
        # Calculate margin
        sku['margin_pct'] = round((sku['price'] - sku['cost']) / sku['price'], 3)
        skus.append(sku)
    
    df_skus = pd.DataFrame(skus)
    df_skus.to_csv(data_dir / "sku_catalog.csv", index=False)
    print(f"✅ Generated {len(df_skus)} SKUs")


def generate_uplift_priors():
    """Generate uplift priors (ICE - Incremental Conversions per Euro/Dollar)."""
    
    retailers = ['alpha', 'beta']
    placements = ['sponsored_product', 'onsite_display', 'offsite_video', 'native']
    audiences = ['retargeting', 'inmarket', 'lookalike', 'lapsed']
    
    priors = []
    for retailer in retailers:
        for placement in placements:
            for audience in audiences:
                # Generate 10 SKUs per combination
                for _ in range(10):
                    sku = f'SKU-{np.random.randint(1, 100):03d}'
                    
                    # ICE varies by placement and audience
                    base_ice = {
                        'sponsored_product': 0.08,
                        'onsite_display': 0.05,
                        'offsite_video': 0.03,
                        'native': 0.04
                    }[placement]
                    
                    audience_multiplier = {
                        'retargeting': 1.5,
                        'inmarket': 1.2,
                        'lookalike': 1.0,
                        'lapsed': 0.8
                    }[audience]
                    
                    ice = base_ice * audience_multiplier * np.random.uniform(0.8, 1.2)
                    
                    prior = {
                        'retailer': retailer,
                        'placement': placement,
                        'audience': audience,
                        'sku': sku,
                        'ice': round(ice, 4),  # Incremental conversions per dollar
                        'baseline_cvr': round(np.random.uniform(0.01, 0.05), 4),
                        'cpa': round(1.0 / ice if ice > 0 else 999, 2),
                        'confidence': round(np.random.uniform(0.6, 0.95), 2)
                    }
                    priors.append(prior)
    
    df_priors = pd.DataFrame(priors)
    df_priors.to_csv(data_dir / "uplift_priors.csv", index=False)
    print(f"✅ Generated {len(df_priors)} uplift priors")


def generate_audience_segments():
    """Generate audience segment definitions."""
    
    segments = [
        {
            'segment_id': 'retargeting',
            'name': 'Retargeting - Site Visitors',
            'description': 'Users who visited product pages in last 30 days',
            'reach_estimate': 500000,
            'cpm_premium': 1.5
        },
        {
            'segment_id': 'inmarket',
            'name': 'In-Market Shoppers',
            'description': 'Users actively searching for category',
            'reach_estimate': 1000000,
            'cpm_premium': 1.3
        },
        {
            'segment_id': 'lookalike',
            'name': 'Lookalike Audience',
            'description': 'Similar to past converters',
            'reach_estimate': 2000000,
            'cpm_premium': 1.0
        },
        {
            'segment_id': 'lapsed',
            'name': 'Lapsed Customers',
            'description': 'Purchased 90+ days ago',
            'reach_estimate': 300000,
            'cpm_premium': 1.2
        }
    ]
    
    df_segments = pd.DataFrame(segments)
    df_segments.to_csv(data_dir / "audience_segments.csv", index=False)
    print(f"✅ Generated {len(df_segments)} audience segments")


def generate_geo_regions():
    """Generate geographic regions for testing."""
    
    regions = []
    for i in range(1, 21):
        region = {
            'dma_code': f'DMA_{i:03d}',
            'dma_name': f'Market Region {i}',
            'population': np.random.randint(500000, 5000000),
            'baseline_sales': np.random.randint(100000, 1000000),
            'seasonality_index': round(np.random.uniform(0.8, 1.2), 2)
        }
        regions.append(region)
    
    df_regions = pd.DataFrame(regions)
    df_regions.to_csv(data_dir / "geo_regions.csv", index=False)
    print(f"✅ Generated {len(df_regions)} geo regions")


if __name__ == "__main__":
    print("🚀 Generating synthetic data for RMN demo...\n")
    
    generate_retailer_alpha_data()
    generate_retailer_beta_data()
    generate_sku_catalog()
    generate_uplift_priors()
    generate_audience_segments()
    generate_geo_regions()
    
    print("\n✅ All synthetic data generated successfully!")
    print(f"📁 Data location: {data_dir.absolute()}")
