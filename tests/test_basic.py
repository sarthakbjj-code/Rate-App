"""Basic tests for the procurement intelligence system."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_database_setup():
    """Test database creation."""
    from src.database import get_engine, create_tables
    from sqlalchemy import inspect
    
    engine = get_engine('data/test.db')
    create_tables(engine)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    assert 'products' in tables
    assert 'price_history' in tables
    assert 'gst_info' in tables
    assert 'analysis_results' in tables
    assert 'scraping_logs' in tables
    
    print("✅ Database setup test passed")
    
    # Cleanup
    if os.path.exists('data/test.db'):
        os.remove('data/test.db')


def test_gst_lookup():
    """Test GST rate lookup."""
    from src.data_collection.gst_lookup import GSTRateFinder
    
    finder = GSTRateFinder()
    
    # Test with known HSN code
    result = finder.get_gst_rate('1101')
    
    assert result['hsn_code'] == '1101'
    assert result['gst_rate'] == 5.0
    assert 'Wheat' in result['description'] or 'flour' in result['description'].lower()
    
    print("✅ GST lookup test passed")


def test_price_normalization():
    """Test price normalization."""
    from src.utils.helpers import normalize_price
    
    # Test kg conversion
    price = normalize_price(150, 500, 'g')
    assert abs(price - 300) < 0.01  # 500g @ 150 = 300/kg
    
    # Test litre conversion
    price = normalize_price(200, 2, 'litre')
    assert abs(price - 100) < 0.01  # 2L @ 200 = 100/litre
    
    # Test pieces
    price = normalize_price(120, 6, 'pieces')
    assert abs(price - 20) < 0.01  # 6 pieces @ 120 = 20/piece
    
    print("✅ Price normalization test passed")


def test_validators():
    """Test input validators."""
    from src.utils.validators import validate_hsn_code, validate_product_name
    
    # Valid HSN codes
    valid, _ = validate_hsn_code('1101')
    assert valid == True
    
    valid, _ = validate_hsn_code('11010000')
    assert valid == True
    
    # Invalid HSN codes
    valid, error = validate_hsn_code('abc')
    assert valid == False
    assert error is not None
    
    valid, error = validate_hsn_code('123')
    assert valid == False
    
    # Valid product names
    valid, _ = validate_product_name('Ashirvaad Atta')
    assert valid == True
    
    # Invalid product names
    valid, error = validate_product_name('')
    assert valid == False
    
    valid, error = validate_product_name('ab')
    assert valid == False
    
    print("✅ Validators test passed")


def test_forecasting():
    """Test price forecasting."""
    from src.analysis.forecasting import PriceForecaster
    from datetime import datetime, timedelta
    
    forecaster = PriceForecaster()
    
    # Create sample historical data
    historical_data = []
    for i in range(60):
        historical_data.append({
            'date': datetime.now() - timedelta(days=60-i),
            'price': 300 + (i % 10)
        })
    
    # Test forecast
    forecast = forecaster.forecast_prices(historical_data, periods=30)
    
    assert 'dates' in forecast
    assert 'predictions' in forecast
    assert 'lower_bound' in forecast
    assert 'upper_bound' in forecast
    assert len(forecast['predictions']) == 30
    
    print("✅ Forecasting test passed")


def test_recommendations():
    """Test recommendation engine."""
    from src.analysis.recommendations import RecommendationEngine
    
    engine = RecommendationEngine()
    
    current_prices = [
        {'source': 'Source1', 'brand': 'Brand1', 'current_price': 295, 'url': '#'},
        {'source': 'Source2', 'brand': 'Brand2', 'current_price': 310, 'url': '#'},
    ]
    
    historical_analysis = {
        'min_price': 265,
        'max_price': 395,
        'avg_price': 310,
        'current_percentile': 45
    }
    
    seasonality = {
        'cheapest_months': ['March', 'April'],
        'expensive_months': ['November', 'December']
    }
    
    forecast = {
        'predictions': [300, 305, 310],
        'dates': [],
        'lower_bound': [],
        'upper_bound': []
    }
    
    recommendations = engine.generate_recommendations(
        current_prices=current_prices,
        historical_analysis=historical_analysis,
        seasonality=seasonality,
        forecast=forecast,
        current_supplier_price=350
    )
    
    assert 'action' in recommendations
    assert 'current_best_price' in recommendations
    assert 'negotiation_target' in recommendations
    assert 'recommendation_text' in recommendations
    
    print("✅ Recommendations test passed")


if __name__ == '__main__':
    print("Running tests...\n")
    
    test_database_setup()
    test_gst_lookup()
    test_price_normalization()
    test_validators()
    test_forecasting()
    test_recommendations()
    
    print("\n✅ All tests passed!")
