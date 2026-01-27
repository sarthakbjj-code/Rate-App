#!/usr/bin/env python3
"""Setup database script."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import create_tables, get_engine
from config import config


def setup_database():
    """Initialize database with all tables."""
    print("🗄️  Setting up database...")
    
    # Create data directory
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)
    
    # Create engine and tables
    engine = get_engine(config.DATABASE_PATH)
    create_tables(engine)
    
    print(f"✅ Database created at: {config.DATABASE_PATH}")
    print("✅ All tables created successfully")
    
    # List tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"\n📋 Created tables: {', '.join(tables)}")


if __name__ == "__main__":
    setup_database()
