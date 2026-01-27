"""Database models using SQLAlchemy."""
from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Boolean, 
    DateTime, Text, ForeignKey, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()


class Product(Base):
    """Product information table."""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    material_number = Column(String(50), unique=True)
    description = Column(Text, nullable=False)
    hsn_code = Column(String(10), nullable=False)
    uom = Column(String(20), nullable=False)
    category = Column(String(100))
    gst_rate = Column(Float)
    preferred_brand = Column(String(100))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    price_history = relationship("PriceHistory", back_populates="product")
    gst_info = relationship("GSTInfo", back_populates="product")
    analysis_results = relationship("AnalysisResult", back_populates="product")


class PriceHistory(Base):
    """Price history table."""
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    source = Column(String(50), nullable=False)
    brand = Column(String(100))
    price = Column(Float, nullable=False)
    mrp = Column(Float)
    unit = Column(String(20))
    quantity = Column(Float)
    normalized_price = Column(Float)
    url = Column(Text)
    in_stock = Column(Boolean)
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="price_history")
    
    # Indexes
    __table_args__ = (
        Index('idx_price_product_date', 'product_id', 'date'),
        Index('idx_price_source', 'source'),
    )


class GSTInfo(Base):
    """GST information table."""
    __tablename__ = 'gst_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    hsn_code = Column(String(10))
    gst_rate = Column(Float, nullable=False)
    cess = Column(Float, default=0)
    description = Column(Text)
    source = Column(String(50))
    source_url = Column(Text)
    last_verified = Column(DateTime)
    
    # Relationships
    product = relationship("Product", back_populates="gst_info")
    
    # Indexes
    __table_args__ = (
        Index('idx_product_hsn', 'hsn_code'),
    )


class AnalysisResult(Base):
    """Analysis results table."""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    analysis_date = Column(DateTime, default=datetime.utcnow)
    min_2yr = Column(Float)
    max_2yr = Column(Float)
    avg_2yr = Column(Float)
    median_2yr = Column(Float)
    current_percentile = Column(Float)
    trend_1m = Column(Float)
    trend_3m = Column(Float)
    trend_6m = Column(Float)
    std_dev = Column(Float)
    cheapest_months = Column(String(100))
    expensive_months = Column(String(100))
    forecast_6m = Column(Float)
    forecast_lower = Column(Float)
    forecast_upper = Column(Float)
    negotiation_target = Column(Float)
    potential_savings = Column(Float)
    recommended_action = Column(String(20))
    
    # Relationships
    product = relationship("Product", back_populates="analysis_results")


class ScrapingLog(Base):
    """Scraping logs table."""
    __tablename__ = 'scraping_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer)
    source = Column(String(50))
    status = Column(String(20))
    records_found = Column(Integer)
    error_message = Column(Text)
    execution_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_engine(db_path=None):
    """Create database engine."""
    if db_path is None:
        db_path = os.getenv('DATABASE_PATH', 'data/price_history.db')
    
    # Validate database path to prevent path traversal
    db_path = os.path.abspath(db_path)
    allowed_dir = os.path.abspath('data')
    
    # Ensure the path is within the allowed directory
    if not db_path.startswith(allowed_dir):
        raise ValueError(f"Database path must be within {allowed_dir}")
    
    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    return engine


def create_tables(engine=None):
    """Create all database tables."""
    if engine is None:
        engine = get_engine()
    
    Base.metadata.create_all(engine)
    return engine


def get_session(engine=None):
    """Get database session."""
    if engine is None:
        engine = get_engine()
    
    Session = sessionmaker(bind=engine)
    return Session()
