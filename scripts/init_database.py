#!/usr/bin/env python
"""Initialize database with sample data."""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage.database import init_db
from src.storage.models import Brand, Retailer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_sample_data(db):
    """Create sample brands and retailers."""
    
    with db.get_session() as session:
        # Create sample retailers
        retailers = [
            Retailer(
                retailer_id="amazon",
                name="Amazon",
                schema_version="1.0.0",
                api_endpoint="https://api.amazon.com/ads",
                clean_room_endpoint="https://api.amazon.com/clean-room",
                policies={
                    "max_headline_length": 80,
                    "max_body_length": 200,
                    "disallowed_terms": ["guaranteed", "miracle", "cure"]
                },
                creative_specs={
                    "sponsored_product": {
                        "headline_max": 80,
                        "image_sizes": ["1200x628", "1080x1080"]
                    }
                },
                is_active=True
            ),
            Retailer(
                retailer_id="walmart",
                name="Walmart",
                schema_version="1.0.0",
                api_endpoint="https://api.walmart.com/ads",
                clean_room_endpoint="https://api.walmart.com/clean-room",
                policies={
                    "max_headline_length": 100,
                    "max_body_length": 250,
                    "disallowed_terms": ["best", "number one"]
                },
                creative_specs={
                    "display": {
                        "headline_max": 100,
                        "image_sizes": ["1200x600", "600x600"]
                    }
                },
                is_active=True
            ),
            Retailer(
                retailer_id="target",
                name="Target",
                schema_version="1.0.0",
                api_endpoint="https://api.target.com/ads",
                clean_room_endpoint="https://api.target.com/clean-room",
                policies={
                    "max_headline_length": 90,
                    "max_body_length": 220,
                    "disallowed_terms": ["cheapest", "lowest price"]
                },
                creative_specs={
                    "roundel": {
                        "headline_max": 90,
                        "image_sizes": ["1200x628"]
                    }
                },
                is_active=True
            )
        ]
        
        for retailer in retailers:
            session.add(retailer)
        
        # Create sample brands
        brands = [
            Brand(
                brand_id="acme_corp",
                name="ACME Corporation",
                tenant_id="tenant_acme",
                tone_guidelines={
                    "tone": "professional",
                    "voice": "authoritative",
                    "avoid": ["slang", "emojis"]
                },
                product_categories=["electronics", "home_goods"],
                budget_constraints={
                    "min_roas": 2.5,
                    "max_cpa": 50.0
                },
                is_active=True
            ),
            Brand(
                brand_id="globex_inc",
                name="Globex Inc",
                tenant_id="tenant_globex",
                tone_guidelines={
                    "tone": "friendly",
                    "voice": "conversational",
                    "avoid": ["technical jargon"]
                },
                product_categories=["food", "beverages"],
                budget_constraints={
                    "min_roas": 3.0,
                    "max_cpa": 30.0
                },
                is_active=True
            ),
            Brand(
                brand_id="initech",
                name="Initech",
                tenant_id="tenant_initech",
                tone_guidelines={
                    "tone": "innovative",
                    "voice": "inspiring",
                    "avoid": ["negative language"]
                },
                product_categories=["software", "services"],
                budget_constraints={
                    "min_roas": 4.0,
                    "max_cpa": 100.0
                },
                is_active=True
            )
        ]
        
        for brand in brands:
            session.add(brand)
        
        session.commit()
        
        logger.info(f"Created {len(retailers)} retailers and {len(brands)} brands")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Initialize RMN database")
    parser.add_argument(
        "--database-url",
        default="sqlite:///rmn_system.db",
        help="Database URL (default: sqlite:///rmn_system.db)"
    )
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Create sample data"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Initializing database: {args.database_url}")
    
    # Initialize database
    db = init_db(args.database_url)
    
    logger.info("Database tables created successfully")
    
    # Create sample data if requested
    if args.sample_data:
        logger.info("Creating sample data...")
        create_sample_data(db)
        logger.info("Sample data created successfully")
    
    logger.info("Database initialization complete!")
    
    # Print summary
    with db.get_session() as session:
        from src.storage.models import Brand, Retailer
        
        brand_count = session.query(Brand).count()
        retailer_count = session.query(Retailer).count()
        
        print("\n" + "="*50)
        print("Database Summary")
        print("="*50)
        print(f"Brands: {brand_count}")
        print(f"Retailers: {retailer_count}")
        print("="*50)
        
        if brand_count > 0:
            print("\nBrands:")
            brands = session.query(Brand).all()
            for brand in brands:
                print(f"  - {brand.name} ({brand.brand_id})")
        
        if retailer_count > 0:
            print("\nRetailers:")
            retailers = session.query(Retailer).all()
            for retailer in retailers:
                print(f"  - {retailer.name} ({retailer.retailer_id})")
        
        print("\n")


if __name__ == "__main__":
    main()
