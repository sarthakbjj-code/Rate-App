"""Database package initialization."""
try:
    from .models import (
        Product, PriceHistory, GSTInfo, AnalysisResult, ScrapingLog,
        get_engine, create_tables, get_session, Base
    )
    
    __all__ = [
        'Product', 'PriceHistory', 'GSTInfo', 'AnalysisResult', 'ScrapingLog',
        'get_engine', 'create_tables', 'get_session', 'Base'
    ]
except ImportError:
    # If SQLAlchemy is not available (cloud deployment), provide stubs
    class Product:
        pass
    
    class PriceHistory:
        pass
    
    class GSTInfo:
        pass
    
    class AnalysisResult:
        pass
    
    class ScrapingLog:
        pass
    
    def get_engine():
        raise NotImplementedError("Database not available in cloud deployment")
    
    def create_tables():
        raise NotImplementedError("Database not available in cloud deployment")
    
    def get_session():
        raise NotImplementedError("Database not available in cloud deployment")
    
    Base = None
    
    __all__ = [
        'Product', 'PriceHistory', 'GSTInfo', 'AnalysisResult', 'ScrapingLog',
        'get_engine', 'create_tables', 'get_session', 'Base'
    ]

