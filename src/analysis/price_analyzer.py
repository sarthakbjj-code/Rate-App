"""Price analysis engine."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from src.database import PriceHistory, Product
import logging

logger = logging.getLogger(__name__)


class PriceAnalyzer:
    """Analyze historical price data."""
    
    def __init__(self, session: Session):
        """
        Initialize price analyzer.
        
        Args:
            session: Database session
        """
        self.session = session
    
    def analyze_historical_prices(self, product_id: int, days: int = 730) -> Dict:
        """
        Analyze historical prices for a product.
        
        Args:
            product_id: Product ID
            days: Number of days to analyze (default: 730 = 2 years)
            
        Returns:
            Dictionary with price statistics
        """
        try:
            # Get price history
            cutoff_date = datetime.now() - timedelta(days=days)
            
            prices = self.session.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.date >= cutoff_date
            ).order_by(PriceHistory.date).all()
            
            if not prices:
                return self._empty_analysis()
            
            # Convert to DataFrame
            df = pd.DataFrame([{
                'date': p.date,
                'price': p.normalized_price or p.price,
                'source': p.source
            } for p in prices])
            
            # Calculate statistics
            price_values = df['price'].values
            
            analysis = {
                'min_price': float(np.min(price_values)),
                'max_price': float(np.max(price_values)),
                'avg_price': float(np.mean(price_values)),
                'median_price': float(np.median(price_values)),
                'std_dev': float(np.std(price_values)),
                'volatility': float(np.std(price_values) / np.mean(price_values)) if np.mean(price_values) > 0 else 0,
            }
            
            # Current price percentile
            if len(prices) > 0:
                current_price = prices[-1].normalized_price or prices[-1].price
                analysis['current_percentile'] = float(
                    (price_values < current_price).sum() / len(price_values) * 100
                )
            else:
                analysis['current_percentile'] = 50.0
            
            # Trends
            analysis.update(self._calculate_trends(df))
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing prices: {e}")
            return self._empty_analysis()
    
    def _calculate_trends(self, df: pd.DataFrame) -> Dict:
        """Calculate price trends for different time periods."""
        trends = {}
        
        try:
            current_date = df['date'].max()
            
            for period, days in [('1m', 30), ('3m', 90), ('6m', 180), ('1yr', 365)]:
                start_date = current_date - timedelta(days=days)
                period_data = df[df['date'] >= start_date]
                
                if len(period_data) >= 2:
                    first_price = period_data.iloc[0]['price']
                    last_price = period_data.iloc[-1]['price']
                    
                    if first_price > 0:
                        trend = ((last_price - first_price) / first_price) * 100
                        trends[f'trend_{period}'] = float(trend)
                    else:
                        trends[f'trend_{period}'] = 0.0
                else:
                    trends[f'trend_{period}'] = 0.0
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            trends = {'trend_1m': 0.0, 'trend_3m': 0.0, 'trend_6m': 0.0, 'trend_1yr': 0.0}
        
        return trends
    
    def detect_seasonality(self, product_id: int) -> Dict:
        """
        Detect seasonal patterns in pricing.
        
        Args:
            product_id: Product ID
            
        Returns:
            Dictionary with seasonality information
        """
        try:
            # Get 2 years of data
            cutoff_date = datetime.now() - timedelta(days=730)
            
            prices = self.session.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.date >= cutoff_date
            ).all()
            
            if len(prices) < 50:  # Not enough data
                return {
                    'cheapest_months': [],
                    'expensive_months': [],
                    'seasonal_pattern': False,
                    'avg_variation': 0.0
                }
            
            # Group by month
            df = pd.DataFrame([{
                'month': p.date.month,
                'price': p.normalized_price or p.price
            } for p in prices])
            
            monthly_avg = df.groupby('month')['price'].mean()
            
            # Find cheapest and most expensive months
            sorted_months = monthly_avg.sort_values()
            
            month_names = [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]
            
            cheapest = [month_names[m-1] for m in sorted_months.head(2).index]
            expensive = [month_names[m-1] for m in sorted_months.tail(2).index]
            
            # Calculate variation
            variation = (monthly_avg.max() - monthly_avg.min()) / monthly_avg.mean() * 100
            
            return {
                'cheapest_months': cheapest,
                'expensive_months': expensive,
                'seasonal_pattern': variation > 10,  # >10% variation
                'avg_variation': float(variation)
            }
            
        except Exception as e:
            logger.error(f"Error detecting seasonality: {e}")
            return {
                'cheapest_months': [],
                'expensive_months': [],
                'seasonal_pattern': False,
                'avg_variation': 0.0
            }
    
    def compare_sources(self, product_id: int) -> pd.DataFrame:
        """
        Compare prices across different sources.
        
        Args:
            product_id: Product ID
            
        Returns:
            DataFrame with source comparison
        """
        try:
            # Get last 30 days of data
            cutoff_date = datetime.now() - timedelta(days=30)
            
            prices = self.session.query(PriceHistory).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.date >= cutoff_date
            ).all()
            
            if not prices:
                return pd.DataFrame()
            
            # Group by source
            df = pd.DataFrame([{
                'source': p.source,
                'price': p.normalized_price or p.price,
                'in_stock': p.in_stock
            } for p in prices])
            
            comparison = df.groupby('source').agg({
                'price': ['mean', 'min', 'count'],
                'in_stock': lambda x: (x == True).sum() / len(x) * 100
            }).round(2)
            
            comparison.columns = ['Avg Price', 'Min Price', 'Data Points', 'Availability %']
            comparison = comparison.sort_values('Avg Price')
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing sources: {e}")
            return pd.DataFrame()
    
    def _empty_analysis(self) -> Dict:
        """Return empty analysis structure."""
        return {
            'min_price': 0.0,
            'max_price': 0.0,
            'avg_price': 0.0,
            'median_price': 0.0,
            'current_percentile': 50.0,
            'volatility': 0.0,
            'trend_1m': 0.0,
            'trend_3m': 0.0,
            'trend_6m': 0.0,
            'trend_1yr': 0.0,
            'std_dev': 0.0
        }
