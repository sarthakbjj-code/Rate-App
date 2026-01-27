# API Documentation

## Core Modules

### Database (`src/database/models.py`)

#### Classes

**Product**
- Stores product information
- Fields: material_number, description, hsn_code, uom, category, gst_rate, preferred_brand

**PriceHistory**
- Stores historical price data
- Fields: product_id, date, source, brand, price, mrp, unit, quantity, normalized_price, url, in_stock

**GSTInfo**
- Stores GST rate information
- Fields: product_id, hsn_code, gst_rate, cess, description, source

**AnalysisResult**
- Stores cached analysis results
- Fields: product_id, min_2yr, max_2yr, avg_2yr, trend_1m, trend_3m, etc.

#### Functions

```python
get_engine(db_path=None) -> Engine
    """Create database engine."""

create_tables(engine=None) -> Engine
    """Create all database tables."""

get_session(engine=None) -> Session
    """Get database session."""
```

### GST Lookup (`src/data_collection/gst_lookup.py`)

#### GSTRateFinder

```python
get_gst_rate(hsn_code: str) -> Dict
    """
    Get GST rate for HSN code.
    
    Returns:
        {
            'hsn_code': str,
            'gst_rate': float,
            'cess': float,
            'description': str,
            'source': str,
            'source_url': str,
            'last_verified': datetime,
            'confidence': str  # 'high', 'medium', 'low'
        }
    """
```

### Price Analysis (`src/analysis/price_analyzer.py`)

#### PriceAnalyzer

```python
analyze_historical_prices(product_id: int, days: int = 730) -> Dict
    """
    Analyze historical prices.
    
    Returns:
        {
            'min_price': float,
            'max_price': float,
            'avg_price': float,
            'median_price': float,
            'current_percentile': float,
            'volatility': float,
            'trend_1m': float,
            'trend_3m': float,
            'trend_6m': float,
            'trend_1yr': float,
            'std_dev': float
        }
    """

detect_seasonality(product_id: int) -> Dict
    """
    Detect seasonal patterns.
    
    Returns:
        {
            'cheapest_months': List[str],
            'expensive_months': List[str],
            'seasonal_pattern': bool,
            'avg_variation': float
        }
    """

compare_sources(product_id: int) -> pd.DataFrame
    """Compare prices across sources."""
```

### Forecasting (`src/analysis/forecasting.py`)

#### PriceForecaster

```python
forecast_prices(price_history: List[Dict], periods: int = 180) -> Dict
    """
    Forecast prices for N days.
    
    Args:
        price_history: List of {'date': datetime, 'price': float}
        periods: Number of days to forecast
    
    Returns:
        {
            'dates': List[datetime],
            'predictions': List[float],
            'lower_bound': List[float],
            'upper_bound': List[float],
            'confidence': float,
            'model_weights': Dict
        }
    """
```

### Recommendations (`src/analysis/recommendations.py`)

#### RecommendationEngine

```python
generate_recommendations(
    current_prices: List[Dict],
    historical_analysis: Dict,
    seasonality: Dict,
    forecast: Dict,
    current_supplier_price: float = None
) -> Dict
    """
    Generate procurement recommendations.
    
    Returns:
        {
            'action': str,  # 'BUY_NOW', 'WAIT', 'NEGOTIATE'
            'confidence': float,
            'current_best_price': Dict,
            'negotiation_target': float,
            'potential_savings': float,
            'savings_percentage': float,
            'best_time_to_buy': str,
            'avoid_months': str,
            'top_3_options': List[Dict],
            'forecast_trend': str,
            'recommendation_text': str
        }
    """
```

### Web Scrapers (`src/scrapers/`)

#### BaseScraper (Abstract)

```python
async def search_product(product_name: str, hsn_code: str = None) -> List[Dict]
    """
    Search for product and return price information.
    
    Returns:
        List of {
            'product_name': str,
            'brand': str,
            'current_price': float,
            'mrp': float,
            'unit': str,
            'quantity': float,
            'normalized_price': float,
            'url': str,
            'in_stock': bool,
            'rating': float,
            'image_url': str,
            'source': str,
            'scraped_at': datetime
        }
    """
```

#### Implementations
- **BlinkitScraper**: Scrapes blinkit.com
- **AmazonScraper**: Scrapes amazon.in
- **FlipkartScraper**: Scrapes flipkart.com
- **JioMartScraper**: Scrapes jiomart.com
- **IndiaMartScraper**: Scrapes indiamart.com
- **BigBasketScraper**: Scrapes bigbasket.com

### Utilities (`src/utils/`)

#### helpers.py

```python
normalize_price(price: float, quantity: float, unit: str) -> Optional[float]
    """Convert prices to standard units (kg, litre, piece)."""

extract_quantity_from_text(text: str) -> Tuple[Optional[float], Optional[str]]
    """Extract quantity and unit from product text."""

sanitize_input(text: str) -> str
    """Sanitize user input to prevent XSS and SQL injection."""

format_currency(amount: float) -> str
    """Format amount as Indian currency (₹)."""

calculate_savings_percentage(current_price: float, target_price: float) -> float
    """Calculate savings percentage."""
```

#### validators.py

```python
validate_hsn_code(hsn_code: str) -> tuple[bool, Optional[str]]
    """Validate HSN code (4-8 digits)."""

validate_product_name(name: str) -> tuple[bool, Optional[str]]
    """Validate product name."""

validate_quantity(quantity: float) -> tuple[bool, Optional[str]]
    """Validate quantity."""

validate_uom(uom: str) -> tuple[bool, Optional[str]]
    """Validate unit of measurement."""
```

## Usage Examples

### Basic Workflow

```python
import asyncio
from src.database import get_session, Product, PriceHistory
from src.scrapers import BlinkitScraper, AmazonScraper
from src.data_collection.gst_lookup import GSTRateFinder
from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.forecasting import PriceForecaster
from src.analysis.recommendations import RecommendationEngine

# 1. Get GST information
gst_finder = GSTRateFinder()
gst_info = gst_finder.get_gst_rate("1101")
print(f"GST Rate: {gst_info['gst_rate']}%")

# 2. Scrape current prices
async def scrape_prices():
    blinkit = BlinkitScraper()
    amazon = AmazonScraper()
    
    results = await asyncio.gather(
        blinkit.search_product("Ashirvaad Atta 5kg"),
        amazon.search_product("Ashirvaad Atta 5kg")
    )
    
    return [item for sublist in results for item in sublist]

current_prices = asyncio.run(scrape_prices())

# 3. Analyze historical data
session = get_session()
analyzer = PriceAnalyzer(session)
analysis = analyzer.analyze_historical_prices(product_id=1, days=730)

print(f"Min Price (2Y): ₹{analysis['min_price']:.2f}")
print(f"Avg Price (2Y): ₹{analysis['avg_price']:.2f}")
print(f"Max Price (2Y): ₹{analysis['max_price']:.2f}")

# 4. Detect seasonality
seasonality = analyzer.detect_seasonality(product_id=1)
print(f"Best months: {', '.join(seasonality['cheapest_months'])}")

# 5. Forecast future prices
historical_data = [
    {'date': p.date, 'price': p.price}
    for p in session.query(PriceHistory).filter_by(product_id=1).all()
]

forecaster = PriceForecaster()
forecast = forecaster.forecast_prices(historical_data, periods=180)

# 6. Get recommendations
rec_engine = RecommendationEngine()
recommendations = rec_engine.generate_recommendations(
    current_prices=current_prices,
    historical_analysis=analysis,
    seasonality=seasonality,
    forecast=forecast,
    current_supplier_price=350.0
)

print(f"Action: {recommendations['action']}")
print(f"Best Price: ₹{recommendations['current_best_price']['price']:.2f}")
print(f"Negotiation Target: ₹{recommendations['negotiation_target']:.2f}")
print(f"Potential Savings: ₹{recommendations['potential_savings']:.2f}")
```

### Adding Products

```python
from src.database import get_session, Product

session = get_session()

product = Product(
    material_number='MAT001',
    description='Ashirvaad Whole Wheat Atta 5kg',
    hsn_code='1101',
    uom='kg',
    category='Food & Beverages',
    gst_rate=5.0,
    preferred_brand='Ashirvaad'
)

session.add(product)
session.commit()
```

### Saving Price Data

```python
from src.database import get_session, PriceHistory
from datetime import datetime

session = get_session()

price_record = PriceHistory(
    product_id=1,
    date=datetime.now(),
    source='Blinkit',
    brand='Ashirvaad',
    price=295.0,
    mrp=310.0,
    unit='kg',
    quantity=5.0,
    normalized_price=59.0,  # 295/5 = 59 per kg
    url='https://blinkit.com/product/...',
    in_stock=True
)

session.add(price_record)
session.commit()
```

## Configuration

### Environment Variables (.env)

```env
# Scraping
SCRAPE_DELAY=3
MAX_RETRIES=3
TIMEOUT=30
HEADLESS=True

# Database
DATABASE_PATH=data/price_history.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Optional API Keys
KEEPA_API_KEY=your_key
SERPAPI_KEY=your_key
```

### Access via Code

```python
from config import config

print(config.SCRAPE_DELAY)  # 3
print(config.DATABASE_PATH)  # data/price_history.db
```

## Error Handling

All major functions include comprehensive error handling:

```python
try:
    result = analyzer.analyze_historical_prices(product_id=1)
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    # Fallback to default values
    result = analyzer._empty_analysis()
```

Scrapers fail gracefully:
- Individual scraper failures don't stop others
- Errors are logged to database
- Empty results returned instead of exceptions

## Best Practices

1. **Always use async for scrapers**: Use `asyncio.run()` or `await` in async functions
2. **Close database sessions**: Use context managers or explicit `session.close()`
3. **Validate inputs**: Use validators from `src.utils.validators`
4. **Handle missing data**: Check for empty results before processing
5. **Log errors**: Use Python's `logging` module for debugging

## Extending the System

### Adding a New Scraper

```python
from src.scrapers.base_scraper import BaseScraper

class NewSiteScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://newsite.com"
    
    async def search_product(self, product_name: str, hsn_code: str = None):
        # Implementation here
        results = []
        # ... scraping logic ...
        return results
```

### Adding a New Analysis Metric

Extend `PriceAnalyzer` class:

```python
def calculate_custom_metric(self, product_id: int) -> float:
    # Your analysis logic
    return metric_value
```

## Support

For detailed implementation examples, see:
- Test files in `/tests`
- Web app in `/web_app/app.py`
- Scripts in `/scripts`
