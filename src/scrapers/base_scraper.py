"""Base scraper abstract class."""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import asyncio
import time
import logging
from config import config

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    def __init__(self):
        """Initialize base scraper."""
        self.delay = config.SCRAPE_DELAY
        self.max_retries = config.MAX_RETRIES
        self.timeout = config.TIMEOUT
        self.source_name = self.__class__.__name__.replace('Scraper', '').lower()
    
    @abstractmethod
    async def search_product(self, product_name: str, hsn_code: str = None) -> List[Dict]:
        """
        Search for product and return price information.
        
        Args:
            product_name: Product name to search
            hsn_code: Optional HSN code
            
        Returns:
            List of product price dictionaries
        """
        pass
    
    def create_product_dict(
        self,
        product_name: str,
        brand: str,
        current_price: float,
        mrp: float = None,
        unit: str = None,
        quantity: float = None,
        url: str = None,
        in_stock: bool = True,
        rating: float = None,
        image_url: str = None
    ) -> Dict:
        """
        Create standardized product dictionary.
        
        Returns:
            Standardized product dictionary
        """
        from src.utils.helpers import normalize_price
        
        # Calculate normalized price
        normalized_price = None
        if current_price and quantity and unit:
            normalized_price = normalize_price(current_price, quantity, unit)
        
        return {
            'product_name': product_name,
            'brand': brand or 'Unknown',
            'current_price': current_price,
            'mrp': mrp or current_price,
            'unit': unit or 'piece',
            'quantity': quantity or 1.0,
            'normalized_price': normalized_price,
            'url': url,
            'in_stock': in_stock,
            'rating': rating,
            'image_url': image_url,
            'source': self.source_name,
            'scraped_at': datetime.now()
        }
    
    async def retry_on_failure(self, func, *args, **kwargs):
        """
        Retry function on failure with exponential backoff.
        
        Args:
            func: Async function to retry
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or None on failure
        """
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                wait_time = (2 ** attempt) * self.delay
                logger.warning(
                    f"{self.source_name} attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"{self.source_name} failed after {self.max_retries} attempts")
                    return None
    
    async def delay_request(self):
        """Add delay between requests."""
        await asyncio.sleep(self.delay)
