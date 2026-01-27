#!/usr/bin/env python3
"""Populate test data for development and testing."""
import sys
import os
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import get_session, Product, PriceHistory
from config import config


def populate_test_data():
    """Populate database with sample test data."""
    print("📊 Populating test data...")
    
    session = get_session()
    
    # Sample products
    products = [
        {
            'material_number': 'MAT001',
            'description': 'Ashirvaad Whole Wheat Atta 5kg',
            'hsn_code': '1101',
            'uom': 'kg',
            'category': 'Food & Beverages',
            'gst_rate': 5.0,
            'preferred_brand': 'Ashirvaad'
        },
        {
            'material_number': 'MAT002',
            'description': 'Fortune Sunflower Oil 1L',
            'hsn_code': '1512',
            'uom': 'litre',
            'category': 'Food & Beverages',
            'gst_rate': 5.0,
            'preferred_brand': 'Fortune'
        },
        {
            'material_number': 'MAT003',
            'description': 'Tata Salt 1kg',
            'hsn_code': '2501',
            'uom': 'kg',
            'category': 'Food & Beverages',
            'gst_rate': 5.0,
            'preferred_brand': 'Tata'
        }
    ]
    
    # Add products
    for prod_data in products:
        # Check if exists
        existing = session.query(Product).filter_by(
            material_number=prod_data['material_number']
        ).first()
        
        if not existing:
            product = Product(**prod_data)
            session.add(product)
            print(f"✅ Added product: {prod_data['description']}")
        else:
            print(f"⏭️  Product already exists: {prod_data['description']}")
    
    session.commit()
    
    # Add sample price history (2 years)
    print("\n📈 Adding sample price history...")
    
    products_list = session.query(Product).all()
    sources = ['Blinkit', 'Amazon', 'Flipkart', 'JioMart', 'BigBasket']
    
    for product in products_list:
        # Check if price history exists
        existing_prices = session.query(PriceHistory).filter_by(
            product_id=product.id
        ).count()
        
        if existing_prices > 0:
            print(f"⏭️  Price history exists for: {product.description}")
            continue
        
        print(f"Adding prices for: {product.description}")
        
        # Generate 2 years of weekly prices
        base_price = random.uniform(200, 400)
        
        for days_ago in range(0, 730, 7):  # Weekly data for 2 years
            date = datetime.now() - timedelta(days=days_ago)
            
            for source in sources:
                # Add some variation and seasonality
                seasonal_factor = 1 + 0.1 * random.choice([-1, 1])
                price_variation = random.uniform(0.95, 1.05)
                price = base_price * seasonal_factor * price_variation
                
                price_record = PriceHistory(
                    product_id=product.id,
                    date=date,
                    source=source,
                    brand=product.preferred_brand,
                    price=price,
                    mrp=price * 1.05,
                    unit=product.uom,
                    quantity=1.0,
                    normalized_price=price,
                    in_stock=True,
                    confidence_score=0.9
                )
                
                session.add(price_record)
        
        print(f"✅ Added {len(sources) * 104} price records")
    
    session.commit()
    print("\n✅ Test data population complete!")
    
    # Summary
    total_products = session.query(Product).count()
    total_prices = session.query(PriceHistory).count()
    
    print(f"\n📊 Database Summary:")
    print(f"  - Products: {total_products}")
    print(f"  - Price Records: {total_prices}")


if __name__ == "__main__":
    populate_test_data()
