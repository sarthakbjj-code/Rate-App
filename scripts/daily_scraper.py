"""Daily scraper with scheduler for automated price updates."""
import sys
import os
from datetime import datetime
import asyncio
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from apscheduler.schedulers.blocking import BlockingScheduler
from src.database import get_session, Product, PriceHistory, ScrapingLog
from src.scrapers import (
    BlinkitScraper, AmazonScraper, FlipkartScraper,
    JioMartScraper, IndiaMartScraper, BigBasketScraper
)
from config import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_active_products():
    """Get all active products from database."""
    session = get_session()
    products = session.query(Product).filter_by(active=True).all()
    return products


async def scrape_product(product):
    """Scrape a single product from all sources."""
    logger.info(f"Scraping {product.description}...")
    
    scrapers = [
        BlinkitScraper(),
        AmazonScraper(),
        FlipkartScraper(),
        JioMartScraper(),
        IndiaMartScraper(),
        BigBasketScraper()
    ]
    
    tasks = [s.search_product(product.description, product.hsn_code) for s in scrapers]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Flatten results
    all_products = []
    for result in results:
        if isinstance(result, list):
            all_products.extend(result)
    
    return all_products


def save_price_history(product_id, results):
    """Save scraped prices to database."""
    if not results:
        logger.warning(f"No results to save for product {product_id}")
        return 0
    
    session = get_session()
    count = 0
    
    for result in results:
        try:
            price_record = PriceHistory(
                product_id=product_id,
                date=datetime.now(),
                source=result.get('source', 'Unknown'),
                brand=result.get('brand', 'Unknown'),
                price=result.get('current_price', 0),
                mrp=result.get('mrp'),
                unit=result.get('unit'),
                quantity=result.get('quantity'),
                normalized_price=result.get('normalized_price'),
                url=result.get('url'),
                in_stock=result.get('in_stock', False),
                confidence_score=0.8
            )
            
            session.add(price_record)
            count += 1
        except Exception as e:
            logger.error(f"Error saving price record: {e}")
    
    session.commit()
    return count


def log_scraping_result(product_id, source, status, records_found, error_msg, exec_time):
    """Log scraping result."""
    session = get_session()
    
    log_entry = ScrapingLog(
        product_id=product_id,
        source=source,
        status=status,
        records_found=records_found,
        error_message=error_msg,
        execution_time=exec_time
    )
    
    session.add(log_entry)
    session.commit()


def daily_price_update():
    """Scrape all active products daily."""
    logger.info(f"🔄 Starting daily price update at {datetime.now()}")
    
    # Get all active products
    products = get_active_products()
    logger.info(f"Found {len(products)} active products")
    
    if not products:
        logger.warning("No active products found")
        return
    
    total_records = 0
    
    for product in products:
        start_time = datetime.now()
        
        try:
            # Run scrapers
            results = asyncio.run(scrape_product(product))
            
            # Save results
            count = save_price_history(product.id, results)
            total_records += count
            
            exec_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ {product.description}: {count} records saved in {exec_time:.2f}s")
            
            # Log success
            log_scraping_result(
                product.id,
                'all_sources',
                'success',
                count,
                None,
                exec_time
            )
            
        except Exception as e:
            exec_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Error scraping {product.description}: {e}")
            
            # Log error
            log_scraping_result(
                product.id,
                'all_sources',
                'error',
                0,
                str(e),
                exec_time
            )
    
    logger.info(f"✅ Daily update complete! Total records: {total_records}")


def main():
    """Main function to run scheduler."""
    logger.info("🚀 Starting price scraper scheduler...")
    
    # Create scheduler
    scheduler = BlockingScheduler()
    
    # Schedule for 6 AM daily
    scheduler.add_job(
        daily_price_update,
        'cron',
        hour=6,
        minute=0,
        id='daily_price_update'
    )
    
    logger.info("📅 Scheduled daily update at 6:00 AM")
    logger.info("Press Ctrl+C to exit")
    
    try:
        # Run once immediately for testing
        logger.info("Running initial update...")
        daily_price_update()
        
        # Start scheduler
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()
