"""Procurement recommendations engine."""
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generate procurement recommendations."""
    
    def __init__(self):
        """Initialize recommendation engine."""
        pass
    
    def generate_recommendations(
        self,
        current_prices: List[Dict],
        historical_analysis: Dict,
        seasonality: Dict,
        forecast: Dict,
        current_supplier_price: float = None
    ) -> Dict:
        """
        Generate procurement recommendations.
        
        Args:
            current_prices: List of current prices from different sources
            historical_analysis: Historical price analysis
            seasonality: Seasonality information
            forecast: Price forecast
            current_supplier_price: Current supplier price (optional)
            
        Returns:
            Recommendations dictionary
        """
        try:
            # Find best current option
            if not current_prices:
                return self._empty_recommendations()
            
            # Sort by price
            sorted_prices = sorted(current_prices, key=lambda x: x.get('current_price', float('inf')))
            best_option = sorted_prices[0] if sorted_prices else None
            top_3 = sorted_prices[:3]
            
            if not best_option:
                return self._empty_recommendations()
            
            best_price = best_option.get('current_price', 0)
            
            # Calculate negotiation target
            min_historical = historical_analysis.get('min_price', best_price)
            negotiation_target = min_historical * 1.05  # 5% above historical min
            
            # Determine action
            action = self._determine_action(
                best_price,
                historical_analysis,
                forecast
            )
            
            # Calculate savings
            if current_supplier_price:
                potential_savings = current_supplier_price - best_price
                savings_percentage = (potential_savings / current_supplier_price * 100) if current_supplier_price > 0 else 0
            else:
                potential_savings = 0
                savings_percentage = 0
            
            # Determine forecast trend
            if forecast and forecast.get('predictions'):
                predictions = forecast['predictions']
                if len(predictions) > 30:
                    current_avg = best_price
                    future_avg = sum(predictions[:90]) / min(90, len(predictions))
                    
                    if future_avg > current_avg * 1.05:
                        trend = 'increasing'
                    elif future_avg < current_avg * 0.95:
                        trend = 'decreasing'
                    else:
                        trend = 'stable'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # Generate recommendation text
            rec_text = self._generate_recommendation_text(
                action,
                best_price,
                current_supplier_price,
                negotiation_target,
                savings_percentage,
                trend,
                seasonality
            )
            
            return {
                'action': action,
                'confidence': 0.80,
                'current_best_price': {
                    'price': best_price,
                    'source': best_option.get('source', 'Unknown'),
                    'brand': best_option.get('brand', 'Unknown'),
                    'url': best_option.get('url', '')
                },
                'current_supplier_price': current_supplier_price,
                'negotiation_target': round(negotiation_target, 2),
                'potential_savings': round(potential_savings, 2),
                'savings_percentage': round(savings_percentage, 2),
                'best_time_to_buy': ', '.join(seasonality.get('cheapest_months', [])) or 'N/A',
                'avoid_months': ', '.join(seasonality.get('expensive_months', [])) or 'N/A',
                'top_3_options': [
                    {
                        'source': p.get('source', 'Unknown'),
                        'price': p.get('current_price', 0),
                        'url': p.get('url', '')
                    } for p in top_3
                ],
                'forecast_trend': trend,
                'recommendation_text': rec_text
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return self._empty_recommendations()
    
    def _determine_action(
        self,
        current_price: float,
        historical_analysis: Dict,
        forecast: Dict
    ) -> str:
        """
        Determine recommended action.
        
        Returns:
            'BUY_NOW', 'WAIT', or 'NEGOTIATE'
        """
        try:
            current_percentile = historical_analysis.get('current_percentile', 50)
            
            # If price is in bottom 20%, consider buying
            if current_percentile < 20:
                return 'BUY_NOW'
            
            # If price is in top 20%, wait
            if current_percentile > 80:
                return 'WAIT'
            
            # Middle range - negotiate
            return 'NEGOTIATE'
            
        except:
            return 'NEGOTIATE'
    
    def _generate_recommendation_text(
        self,
        action: str,
        best_price: float,
        supplier_price: float,
        negotiation_target: float,
        savings_percentage: float,
        trend: str,
        seasonality: Dict
    ) -> str:
        """Generate human-readable recommendation text."""
        
        lines = []
        
        # Price comparison
        if supplier_price:
            diff_percentage = abs((supplier_price - best_price) / supplier_price * 100) if supplier_price > 0 else 0
            if best_price < supplier_price:
                lines.append(f"Current market price (₹{best_price:.2f}) is {diff_percentage:.1f}% below your supplier.")
            else:
                lines.append(f"Current market price (₹{best_price:.2f}) is {diff_percentage:.1f}% above your supplier.")
        
        # Trend
        if trend == 'increasing':
            lines.append("Prices are expected to rise in the next 3-6 months.")
        elif trend == 'decreasing':
            lines.append("Prices are expected to fall in the next 3-6 months.")
        else:
            lines.append("Prices are expected to remain stable.")
        
        # Seasonality
        if seasonality.get('seasonal_pattern') and seasonality.get('cheapest_months'):
            best_months = ', '.join(seasonality['cheapest_months'])
            lines.append(f"Historically, best time to buy is {best_months}.")
        
        # Action-specific advice
        if action == 'BUY_NOW':
            lines.append("Current prices are at historical lows. Consider buying now.")
        elif action == 'WAIT':
            lines.append("Current prices are high. Consider waiting for better rates.")
        else:
            lines.append(f"Strong negotiation position. Target price: ₹{negotiation_target:.2f}")
        
        return ' '.join(lines)
    
    def _empty_recommendations(self) -> Dict:
        """Return empty recommendations structure."""
        return {
            'action': 'NEGOTIATE',
            'confidence': 0.0,
            'current_best_price': {},
            'current_supplier_price': None,
            'negotiation_target': 0,
            'potential_savings': 0,
            'savings_percentage': 0,
            'best_time_to_buy': 'N/A',
            'avoid_months': 'N/A',
            'top_3_options': [],
            'forecast_trend': 'stable',
            'recommendation_text': 'Insufficient data for recommendations.'
        }
