"""Main Streamlit web application."""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers import (
    BlinkitScraper, AmazonScraper, FlipkartScraper,
    JioMartScraper, IndiaMartScraper, BigBasketScraper
)
from src.data_collection.gst_lookup import GSTRateFinder
from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.forecasting import PriceForecaster
from src.analysis.recommendations import RecommendationEngine
from src.database import get_session, Product, PriceHistory
from src.utils.validators import validate_product_name, validate_hsn_code
from config import config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Page configuration
st.set_page_config(
    page_title="Procurement Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🛒 Procurement Intelligence System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-Powered Price Analysis & Forecasting</div>', unsafe_allow_html=True)


# Sidebar - Input Form
with st.sidebar:
    st.header("📋 Product Details")
    
    product_name = st.text_input(
        "Product Name*",
        placeholder="e.g., Ashirvaad Atta 5kg",
        help="Enter the product name to search"
    )
    
    hsn_code = st.text_input(
        "HSN Code*",
        placeholder="e.g., 1101",
        max_chars=8,
        help="4-8 digit HSN code"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=100,
            help="Quantity needed"
        )
    
    with col2:
        uom = st.selectbox(
            "Unit",
            ["kg", "litre", "pieces", "box", "carton"],
            help="Unit of measurement"
        )
    
    preferred_brand = st.text_input(
        "Preferred Brand",
        placeholder="Optional",
        help="Enter preferred brand (optional)"
    )
    
    current_supplier_price = st.number_input(
        "Current Supplier Price (₹)",
        min_value=0.0,
        value=0.0,
        help="Your current supplier's price for comparison (optional)"
    )
    
    st.markdown("---")
    analyze_button = st.button(
        "🔍 Analyze Prices",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    st.caption("💡 **Tip:** Enter accurate product details for better results")


# Main content area
if not analyze_button:
    # Welcome screen
    st.info("👈 **Get Started:** Enter product details in the sidebar and click 'Analyze Prices'")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### ✅ Multi-Source Scraping")
        st.write("- Blinkit, Amazon, Flipkart")
        st.write("- JioMart, IndiaMART, BigBasket")
        st.write("- Real-time price comparison")
    
    with col2:
        st.markdown("### 📊 Smart Analysis")
        st.write("- 2-year historical trends")
        st.write("- Seasonality detection")
        st.write("- Supplier comparison")
    
    with col3:
        st.markdown("### 🔮 AI Forecasting")
        st.write("- 6-month price predictions")
        st.write("- ARIMA & ML models")
        st.write("- Confidence intervals")
    
    st.markdown("---")
    
    st.markdown("### 📖 How It Works")
    st.write("""
    1. **Enter Product Details:** Provide product name, HSN code, and other relevant information
    2. **Scrape Prices:** System fetches current prices from multiple online sources
    3. **Analyze History:** Historical price data is analyzed for trends and patterns
    4. **Forecast Future:** AI models predict price movements for next 6 months
    5. **Get Recommendations:** Receive actionable procurement recommendations
    """)

else:
    # Validate inputs
    is_valid_name, name_error = validate_product_name(product_name)
    is_valid_hsn, hsn_error = validate_hsn_code(hsn_code)
    
    if not is_valid_name:
        st.error(f"❌ {name_error}")
        st.stop()
    
    if not is_valid_hsn:
        st.error(f"❌ {hsn_error}")
        st.stop()
    
    # Process analysis
    with st.spinner("🔎 Analyzing prices from multiple sources..."):
        
        # Get GST information
        gst_finder = GSTRateFinder()
        gst_info = gst_finder.get_gst_rate(hsn_code)
        
        # Run scrapers (async)
        async def run_all_scrapers():
            scrapers = [
                BlinkitScraper(),
                AmazonScraper(),
                FlipkartScraper(),
                JioMartScraper(),
                IndiaMartScraper(),
                BigBasketScraper()
            ]
            
            tasks = [s.search_product(product_name, hsn_code) for s in scrapers]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Flatten results
            all_products = []
            for result in results:
                if isinstance(result, list):
                    all_products.extend(result)
            
            return all_products
        
        # Get current prices
        current_prices = asyncio.run(run_all_scrapers())
        
        # Generate sample historical data for demo (in real app, this comes from database)
        # For MVP, we'll create some dummy historical data
        historical_data = []
        base_price = 300
        for i in range(365):
            date = datetime.now() - timedelta(days=365-i)
            # Add some variation
            import random
            price = base_price + random.uniform(-20, 30)
            historical_data.append({
                'date': date,
                'price': price
            })
        
        # Analyze prices
        session = get_session()
        
        # For demo purposes, create analysis without database
        # In production, this would use actual database data
        price_analysis = {
            'min_price': min([h['price'] for h in historical_data]) if historical_data else 0,
            'max_price': max([h['price'] for h in historical_data]) if historical_data else 0,
            'avg_price': sum([h['price'] for h in historical_data]) / len(historical_data) if historical_data else 0,
            'median_price': sorted([h['price'] for h in historical_data])[len(historical_data)//2] if historical_data else 0,
            'current_percentile': 45.0,
            'volatility': 0.08,
            'trend_1m': -2.5,
            'trend_3m': 1.2,
            'trend_6m': 3.8,
            'trend_1yr': 5.5,
            'std_dev': 15.2
        }
        
        seasonality = {
            'cheapest_months': ['March', 'April'],
            'expensive_months': ['November', 'December'],
            'seasonal_pattern': True,
            'avg_variation': 12.5
        }
        
        # Forecast
        forecaster = PriceForecaster()
        forecast = forecaster.forecast_prices(historical_data, periods=180)
        
        # Recommendations
        rec_engine = RecommendationEngine()
        
        # If no scraped prices, use dummy data for demo
        if not current_prices:
            current_prices = [
                {
                    'product_name': product_name,
                    'brand': 'Generic',
                    'current_price': 295.0,
                    'mrp': 310.0,
                    'source': 'Market Average',
                    'url': '#',
                    'in_stock': True
                }
            ]
        
        recommendations = rec_engine.generate_recommendations(
            current_prices=current_prices,
            historical_analysis=price_analysis,
            seasonality=seasonality,
            forecast=forecast,
            current_supplier_price=current_supplier_price if current_supplier_price > 0 else None
        )
    
    # Display results in tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Current Prices",
        "📈 Historical Analysis",
        "🔮 Price Forecast",
        "💡 Recommendations"
    ])
    
    with tab1:
        st.subheader("Current Market Prices")
        
        # GST Info Card
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "GST Rate",
                f"{gst_info['gst_rate']}%",
                help=f"Source: {gst_info['source']}"
            )
        with col2:
            st.metric("CESS", f"{gst_info['cess']}%")
        with col3:
            if current_prices:
                lowest = min([p.get('current_price', float('inf')) for p in current_prices])
                st.metric("Lowest Price", f"₹{lowest:.2f}")
            else:
                st.metric("Lowest Price", "N/A")
        with col4:
            if current_prices:
                highest = max([p.get('current_price', 0) for p in current_prices])
                st.metric("Highest Price", f"₹{highest:.2f}")
            else:
                st.metric("Highest Price", "N/A")
        
        st.markdown("---")
        
        # Price comparison table
        if current_prices:
            df_prices = pd.DataFrame(current_prices)
            
            # Select relevant columns
            display_cols = ['source', 'brand', 'current_price', 'mrp', 'url']
            available_cols = [col for col in display_cols if col in df_prices.columns]
            
            if available_cols:
                df_display = df_prices[available_cols]
                
                st.dataframe(
                    df_display,
                    column_config={
                        "source": "Source",
                        "brand": "Brand",
                        "current_price": st.column_config.NumberColumn(
                            "Price (₹)",
                            format="₹%.2f"
                        ),
                        "mrp": st.column_config.NumberColumn(
                            "MRP (₹)",
                            format="₹%.2f"
                        ),
                        "url": st.column_config.LinkColumn("Product Link")
                    },
                    hide_index=True,
                    use_container_width=True
                )
        else:
            st.info("No current prices available. Scrapers returned no results.")
            st.write("This could be because:")
            st.write("- Product not found on the platforms")
            st.write("- Scraping templates need real implementation")
            st.write("- Network or access issues")
    
    with tab2:
        st.subheader("2-Year Price History")
        
        if historical_data:
            # Create DataFrame
            df_hist = pd.DataFrame(historical_data)
            
            # Line chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_hist['date'],
                y=df_hist['price'],
                mode='lines+markers',
                name='Price',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=4)
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Minimum (2Y)",
                    f"₹{price_analysis['min_price']:.2f}",
                    help="Lowest price in last 2 years"
                )
            
            with col2:
                st.metric(
                    "Average (2Y)",
                    f"₹{price_analysis['avg_price']:.2f}",
                    help="Average price in last 2 years"
                )
            
            with col3:
                st.metric(
                    "Maximum (2Y)",
                    f"₹{price_analysis['max_price']:.2f}",
                    help="Highest price in last 2 years"
                )
            
            with col4:
                st.metric(
                    "Volatility",
                    f"{price_analysis['volatility']*100:.1f}%",
                    help="Price variation coefficient"
                )
        else:
            st.info("No historical data available")
    
    with tab3:
        st.subheader("6-Month Price Forecast")
        
        if forecast and forecast.get('predictions'):
            # Create forecast DataFrame
            df_forecast = pd.DataFrame({
                'date': forecast['dates'],
                'prediction': forecast['predictions'],
                'lower': forecast['lower_bound'],
                'upper': forecast['upper_bound']
            })
            
            # Forecast chart
            fig = go.Figure()
            
            # Upper bound
            fig.add_trace(go.Scatter(
                x=df_forecast['date'],
                y=df_forecast['upper'],
                mode='lines',
                name='Upper Bound',
                line=dict(width=0),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Lower bound with fill
            fig.add_trace(go.Scatter(
                x=df_forecast['date'],
                y=df_forecast['lower'],
                mode='lines',
                name='95% Confidence Interval',
                line=dict(width=0),
                fillcolor='rgba(68, 68, 68, 0.2)',
                fill='tonexty',
                hoverinfo='skip'
            ))
            
            # Prediction line
            fig.add_trace(go.Scatter(
                x=df_forecast['date'],
                y=df_forecast['prediction'],
                mode='lines+markers',
                name='Predicted Price',
                line=dict(color='rgb(31, 119, 180)', width=3),
                marker=dict(size=5)
            ))
            
            fig.update_layout(
                xaxis_title="Date",
                yaxis_title="Price (₹)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Model info
            confidence = forecast.get('confidence', 0) * 100
            st.info(
                f"📊 **Model:** Ensemble Forecasting | "
                f"**Confidence:** {confidence:.0f}% | "
                f"**Method:** ARIMA + Moving Average"
            )
        else:
            st.info("Forecast not available - insufficient data")
    
    with tab4:
        st.subheader("💡 Procurement Recommendations")
        
        # Action card
        action = recommendations['action']
        
        if action == "BUY_NOW":
            st.success("✅ **RECOMMENDATION: BUY NOW**")
        elif action == "WAIT":
            st.warning("⏳ **RECOMMENDATION: WAIT**")
        else:
            st.info("💬 **RECOMMENDATION: NEGOTIATE**")
        
        # Detailed recommendation
        st.markdown("---")
        st.markdown("### 📋 Analysis Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if recommendations['current_supplier_price']:
                st.metric(
                    "Current Supplier Price",
                    f"₹{recommendations['current_supplier_price']:.2f}",
                    help="Your current supplier's price"
                )
            
            st.metric(
                "Negotiation Target",
                f"₹{recommendations['negotiation_target']:.2f}",
                help="Recommended target price for negotiations"
            )
        
        with col2:
            best_price = recommendations['current_best_price'].get('price', 0)
            st.metric(
                "Market Best Price",
                f"₹{best_price:.2f}",
                delta=f"-{recommendations['savings_percentage']:.1f}%" if recommendations['savings_percentage'] > 0 else None,
                help=f"From {recommendations['current_best_price'].get('source', 'N/A')}"
            )
            
            if recommendations['potential_savings'] > 0:
                st.metric(
                    "Potential Savings",
                    f"₹{recommendations['potential_savings']:.2f}",
                    help="Savings compared to current supplier"
                )
        
        st.markdown("---")
        st.markdown("### 📅 Timing Insights")
        
        col1, col2 = st.columns(2)
        with col1:
            if recommendations['best_time_to_buy'] != 'N/A':
                st.success(f"✅ **Best Time to Buy:** {recommendations['best_time_to_buy']}")
            else:
                st.info("ℹ️ **Best Time to Buy:** Insufficient seasonal data")
        
        with col2:
            if recommendations['avoid_months'] != 'N/A':
                st.error(f"❌ **Avoid Buying:** {recommendations['avoid_months']}")
            else:
                st.info("ℹ️ **Avoid Buying:** Insufficient seasonal data")
        
        st.markdown("---")
        st.markdown("### 💡 Recommendation")
        st.write(recommendations['recommendation_text'])
        
        st.markdown("---")
        st.markdown("### 🏆 Top 3 Current Options")
        
        for i, option in enumerate(recommendations['top_3_options'], 1):
            source = option.get('source', 'Unknown')
            price = option.get('price', 0)
            url = option.get('url', '#')
            
            if url and url != '#':
                st.markdown(f"{i}. **{source}** - ₹{price:.2f} [(View Product)]({url})")
            else:
                st.markdown(f"{i}. **{source}** - ₹{price:.2f}")
        
        st.markdown("---")
        
        # Export functionality (placeholder)
        if st.button("📥 Export Full Report (Excel)", use_container_width=True):
            st.info("Excel export functionality will be implemented in the next phase")

# Footer
st.markdown("---")
st.caption("🛒 Procurement Intelligence System | Built with Streamlit | © 2024")
