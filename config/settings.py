"""Application configuration settings."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration."""
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/price_history.db')
    
    # Scraping settings
    SCRAPE_DELAY = int(os.getenv('SCRAPE_DELAY', 3))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
    TIMEOUT = int(os.getenv('TIMEOUT', 30))
    HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    
    # API Keys (optional)
    KEEPA_API_KEY = os.getenv('KEEPA_API_KEY', '')
    SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')
    
    # User agents for scraping
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    ]
    
    # HSN-GST mapping file
    HSN_GST_MAPPING_FILE = 'data/hsn_gst_mapping.json'
    
    # Forecast settings
    FORECAST_DAYS = 180  # 6 months
    HISTORICAL_DAYS = 730  # 2 years
    
    # Price analysis
    PRICE_TOLERANCE = 0.05  # 5% tolerance for price changes


config = Config()
