"""Scrapers package initialization."""
from .base_scraper import BaseScraper
from .blinkit import BlinkitScraper
from .amazon import AmazonScraper
from .flipkart import FlipkartScraper
from .jiomart import JioMartScraper
from .indiamart import IndiaMartScraper
from .bigbasket import BigBasketScraper

__all__ = [
    'BaseScraper',
    'BlinkitScraper',
    'AmazonScraper',
    'FlipkartScraper',
    'JioMartScraper',
    'IndiaMartScraper',
    'BigBasketScraper'
]
