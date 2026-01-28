# 🛒 Procurement Intelligence System

AI-powered price intelligence for smart procurement decisions.

## 🚀 **Want to Deploy? FORK FIRST!**

### Step 1: Fork This Repository
Click the button below to create your own copy:

[![Fork Repository](https://img.shields.io/badge/FORK-Repository-blue?style=for-the-badge&logo=github)](https://github.com/sarthakbjj-code/Rate-App/fork)

**Or manually:** Click the "Fork" button at the top of this page.

### Step 2: Deploy to Streamlit Cloud (2-3 minutes)

After forking, follow these guides:

**👉 [QUICK DEPLOY GUIDE](QUICK_DEPLOY.md)** - Fast 3-step deployment  
**🆕 [NEW ACCOUNT? START HERE](NEW_ACCOUNT_DEPLOY.md)** - Complete walkthrough for new users  
**❓ [DEPLOYMENT FAQ](DEPLOYMENT_FAQ.md)** - Common questions answered

⚠️ **Important:** You must fork the repository before you can deploy it to Streamlit Cloud!

---

## Features

✅ **Multi-Source Price Scraping**
- Blinkit, Amazon, Flipkart, JioMart, IndiaMART, BigBasket
- Automatic price + MRP extraction
- Real-time stock availability

✅ **GST Rate Lookup**
- ClearTax integration
- CBIC official portal
- Fallback database with 80+ HSN codes

✅ **Historical Analysis**
- 2-year price trends
- Seasonality detection
- Volatility metrics
- Supplier comparison

✅ **AI Price Forecasting**
- 6-month predictions using ARIMA and ML models
- 95% confidence intervals
- Ensemble model approach

✅ **Procurement Recommendations**
- Negotiation target prices
- Best time to buy
- Potential savings calculation
- Actionable insights

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/sarthakbjj-code/Rate-App.git
cd Rate-App

# Run setup (installs dependencies, sets up database)
python setup.py
```

### 2. Run Application

```bash
streamlit run web_app/app.py
```

Open browser at: http://localhost:8501

### 3. Enter Product Details

1. Enter product name (e.g., "Ashirvaad Atta 5kg")
2. Enter HSN code (e.g., "1101")
3. Optional: Add preferred brand, quantity, current supplier price
4. Click "Analyze Prices"
5. View results in interactive dashboard

## Manual Installation

```bash
# Install Python 3.9+
python --version

# Install dependencies
pip install -r requirements.txt

# Install browser drivers (for web scraping)
python -m playwright install chromium

# Setup database
python scripts/setup_database.py

# Populate test data (optional)
python scripts/populate_test_data.py

# Run app
streamlit run web_app/app.py
```

## Project Structure

```
Rate-App/
├── web_app/          # Streamlit web interface
│   └── app.py        # Main application
├── src/
│   ├── scrapers/     # Web scrapers for different platforms
│   ├── analysis/     # Price analysis & ML forecasting
│   ├── database/     # SQLite models and database
│   ├── data_collection/ # GST lookup and data gathering
│   └── utils/        # Helper functions and validators
├── scripts/          # Automation and setup scripts
├── data/             # Database and configuration files
├── config/           # Application configuration
├── setup.py          # One-click installation script
└── requirements.txt  # Python dependencies
```

## Configuration

Edit `.env` file for optional settings:

```env
# Scraping settings
SCRAPE_DELAY=3
MAX_RETRIES=3
TIMEOUT=30
HEADLESS=True

# Database
DATABASE_PATH=data/price_history.db

# Optional: API keys for enhanced scraping
KEEPA_API_KEY=your_key
SERPAPI_KEY=your_key
```

## Usage Examples

### Web Interface
The easiest way to use the system is through the Streamlit web interface:

1. **Start the app:** `streamlit run web_app/app.py`
2. **Enter product details** in the sidebar
3. **Click "Analyze Prices"**
4. **View results** across four tabs:
   - Current Prices: Real-time market data
   - Historical Analysis: 2-year trends
   - Price Forecast: 6-month predictions
   - Recommendations: Actionable insights

### Programmatic Usage

```python
from src.scrapers import BlinkitScraper, AmazonScraper
from src.analysis.price_analyzer import PriceAnalyzer
from src.analysis.forecasting import PriceForecaster
from src.data_collection.gst_lookup import GSTRateFinder
from src.database import get_session

# Get GST information
gst_finder = GSTRateFinder()
gst_info = gst_finder.get_gst_rate("1101")
print(f"GST Rate: {gst_info['gst_rate']}%")

# Scrape prices (async)
import asyncio

async def get_prices():
    scraper = BlinkitScraper()
    results = await scraper.search_product("Ashirvaad Atta 5kg")
    return results

prices = asyncio.run(get_prices())

# Analyze historical prices
session = get_session()
analyzer = PriceAnalyzer(session)
analysis = analyzer.analyze_historical_prices(product_id=1)
print(f"Average Price: ₹{analysis['avg_price']:.2f}")

# Forecast future prices
forecaster = PriceForecaster()
historical_data = [
    {'date': '2024-01-01', 'price': 295},
    # ... more data
]
forecast = forecaster.forecast_prices(historical_data, periods=180)
```

## Automated Daily Updates

Run background scraper to update prices daily:

```bash
python scripts/daily_scraper.py
```

This will:
- Scrape all active products daily at 6 AM
- Update price database
- Log scraping results
- Handle errors gracefully

Press Ctrl+C to stop the scheduler.

## Deployment

Want to deploy your app online? See the comprehensive [Deployment Guide](docs/DEPLOYMENT.md) for:

- ✅ **Streamlit Cloud** (recommended, free for GitHub repos)
- Heroku deployment
- Docker + Cloud platforms
- AWS/Azure/GCP options

Quick deploy to Streamlit Cloud:
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Select repository: `sarthakbjj-code/Rate-App`
4. **Branch:** `copilot/build-procurement-web-app` (or merge to `main` first)
5. **Main file:** `web_app/app.py`
6. Click "Deploy"

> **Note:** The code is currently on the `copilot/build-procurement-web-app` branch. Either deploy from this branch or merge the PR to `main` first.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## Database Schema

The system uses SQLite with the following main tables:

- **products**: Product catalog (HSN code, description, category)
- **price_history**: Historical price data from all sources
- **gst_info**: GST rates and information
- **analysis_results**: Cached analysis results
- **scraping_logs**: Scraping operation logs

## Troubleshooting

**Browser installation fails:**
```bash
python -m playwright install --force chromium
```

**Scraping returns no results:**
- Check internet connection
- Some sites may block automated access
- Scraper templates need real implementation for production use
- Try different product names

**Database errors:**
```bash
rm data/price_history.db
python scripts/setup_database.py
```

**Import errors:**
```bash
pip install -r requirements.txt --upgrade
```

## Tech Stack

- **Frontend:** Streamlit
- **Scraping:** Playwright, Selenium, BeautifulSoup
- **ML/Forecasting:** ARIMA (statsmodels), Scikit-learn
- **Database:** SQLite + SQLAlchemy
- **Charts:** Plotly
- **Scheduling:** APScheduler

## Development Status

This is a functional MVP (Minimum Viable Product) with:

✅ **Complete:**
- Database schema and models
- GST lookup system with 80+ HSN codes
- Price analysis engine
- Forecasting models (ARIMA + moving average)
- Recommendation engine
- Full Streamlit web interface
- Setup and automation scripts

🚧 **In Progress:**
- Real web scraper implementations (currently templates)
- Excel export functionality
- Email alerts
- Advanced ML models (Prophet, XGBoost)

## Contributing

Contributions are welcome! Areas for improvement:

1. **Scrapers:** Implement real scraping logic for all platforms
2. **ML Models:** Add Prophet and XGBoost for better forecasting
3. **UI:** Enhance Streamlit interface with more features
4. **Testing:** Add comprehensive unit and integration tests
5. **Documentation:** Expand API documentation

## License

MIT License - See LICENSE file for details

## Support

- **Issues:** https://github.com/sarthakbjj-code/Rate-App/issues
- **Documentation:** See `/docs` folder
- **Email:** Create an issue for support

## Acknowledgments

Built with ❤️ for procurement professionals worldwide.

---

**Note:** This system is designed for internal procurement analysis. Ensure compliance with website terms of service when scraping. Some platforms may require API access for production use.