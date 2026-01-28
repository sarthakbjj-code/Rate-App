"""GST Rate Lookup System."""
import json
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional, Dict
from config import config
import time
import logging

logger = logging.getLogger(__name__)


class GSTRateFinder:
    """Find GST rates for HSN codes."""
    
    def __init__(self):
        """Initialize GST Rate Finder."""
        self.hsn_mapping = self._load_fallback_mapping()
    
    def _load_fallback_mapping(self) -> Dict:
        """Load fallback HSN-to-GST mapping from JSON."""
        try:
            mapping_file = config.HSN_GST_MAPPING_FILE
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load HSN mapping: {e}")
        
        return {}
    
    def get_gst_rate(self, hsn_code: str) -> Dict:
        """
        Get GST rate for HSN code.
        
        Tries multiple sources in order:
        1. ClearTax website
        2. Fallback database
        
        Args:
            hsn_code: HSN code (4-8 digits)
            
        Returns:
            Dictionary with GST information
        """
        # Clean HSN code
        hsn_code = hsn_code.replace(' ', '').replace('-', '')
        
        # Try ClearTax first
        try:
            result = self._scrape_cleartax(hsn_code)
            if result:
                return result
        except Exception as e:
            logger.warning(f"ClearTax scraping failed: {e}")
        
        # Fallback to local database
        return self._get_from_fallback(hsn_code)
    
    def _scrape_cleartax(self, hsn_code: str) -> Optional[Dict]:
        """
        Scrape GST rate from ClearTax.
        
        Args:
            hsn_code: HSN code
            
        Returns:
            GST information or None
        """
        try:
            url = f"https://cleartax.in/s/gst-rates-hsn-code/{hsn_code}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try to find GST rate in the page
                # This is a simplified version - actual implementation may need adjustment
                text = soup.get_text().lower()
                
                # Look for GST rate patterns
                import re
                rate_patterns = [
                    r'gst rate.*?(\d+)%',
                    r'rate.*?(\d+)%',
                    r'(\d+)%\s*gst',
                ]
                
                for pattern in rate_patterns:
                    match = re.search(pattern, text)
                    if match:
                        gst_rate = float(match.group(1))
                        
                        return {
                            'hsn_code': hsn_code,
                            'gst_rate': gst_rate,
                            'cess': 0.0,
                            'description': f'HSN {hsn_code}',
                            'source': 'ClearTax',
                            'source_url': url,
                            'last_verified': datetime.now(),
                            'confidence': 'high'
                        }
            
            time.sleep(1)  # Be polite
            
        except Exception as e:
            logger.error(f"Error scraping ClearTax: {e}")
        
        return None
    
    def _get_from_fallback(self, hsn_code: str) -> Dict:
        """
        Get GST rate from fallback database.
        
        Args:
            hsn_code: HSN code
            
        Returns:
            GST information
        """
        # Try exact match
        if hsn_code in self.hsn_mapping:
            data = self.hsn_mapping[hsn_code]
            return {
                'hsn_code': hsn_code,
                'gst_rate': float(data['rate']),
                'cess': 0.0,
                'description': data['desc'],
                'source': 'Fallback Database',
                'source_url': None,
                'last_verified': datetime.now(),
                'confidence': 'medium'
            }
        
        # Try prefix match (first 4 digits)
        if len(hsn_code) > 4:
            prefix = hsn_code[:4]
            if prefix in self.hsn_mapping:
                data = self.hsn_mapping[prefix]
                return {
                    'hsn_code': hsn_code,
                    'gst_rate': float(data['rate']),
                    'cess': 0.0,
                    'description': data['desc'],
                    'source': 'Fallback Database (Prefix Match)',
                    'source_url': None,
                    'last_verified': datetime.now(),
                    'confidence': 'low'
                }
        
        # Default fallback
        return {
            'hsn_code': hsn_code,
            'gst_rate': 18.0,  # Default GST rate
            'cess': 0.0,
            'description': f'HSN {hsn_code} (Default)',
            'source': 'Default',
            'source_url': None,
            'last_verified': datetime.now(),
            'confidence': 'low'
        }
