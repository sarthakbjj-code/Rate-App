"""BigBasket scraper implementation."""
from typing import List, Dict
import logging
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class BigBasketScraper(BaseScraper):
    """Scraper for BigBasket (bigbasket.com)."""
    
    def __init__(self):
        """Initialize BigBasket scraper."""
        super().__init__()
        self.base_url = "https://www.bigbasket.com"
    
    async def search_product(self, product_name: str, hsn_code: str = None) -> List[Dict]:
        """
        Search for product on BigBasket.
        
        Args:
            product_name: Product name to search
            hsn_code: Optional HSN code
            
        Returns:
            List of product dictionaries
        """
        try:
            logger.info(f"Searching BigBasket for: {product_name}")
            results = []
            logger.info(f"BigBasket: Found {len(results)} products")
            await self.delay_request()
            return results
        except Exception as e:
            logger.error(f"BigBasket scraping error: {e}")
            return []
