# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- 500 MB free disk space
- Internet connection

## Installation Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/sarthakbjj-code/Rate-App.git
cd Rate-App
```

### Step 2: One-Click Setup

```bash
python setup.py
```

This script will:
1. Install all Python dependencies
2. Install browser drivers (Playwright/Chromium)
3. Create necessary directories
4. Setup SQLite database
5. Create configuration file

### Step 3: Verify Installation

```bash
# Check database
ls data/price_history.db

# Check if all packages are installed
python -c "import streamlit, pandas, plotly, playwright; print('✅ All packages installed')"
```

### Step 4: Run Application

```bash
streamlit run web_app/app.py
```

The application will open in your default browser at `http://localhost:8501`

## Optional Steps

### Load Sample Data

To populate the database with sample test data:

```bash
python scripts/populate_test_data.py
```

This creates:
- 3 sample products
- 2 years of historical price data
- Multiple sources per product

### Configure Settings

Edit `.env` file to customize:

```env
# Scraping settings
SCRAPE_DELAY=3        # Delay between requests (seconds)
MAX_RETRIES=3         # Retry attempts on failure
TIMEOUT=30            # Request timeout (seconds)
HEADLESS=True         # Run browser in headless mode

# Optional API keys (for enhanced features)
KEEPA_API_KEY=your_key
SERPAPI_KEY=your_key
```

## Troubleshooting

### Issue: Playwright installation fails

**Solution:**
```bash
python -m playwright install chromium --force
```

Or install manually:
```bash
playwright install chromium
```

### Issue: Port 8501 already in use

**Solution:**
```bash
streamlit run web_app/app.py --server.port 8502
```

### Issue: Database error

**Solution:**
```bash
# Delete and recreate database
rm data/price_history.db
python scripts/setup_database.py
```

### Issue: Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Issue: Streamlit not found

**Solution:**
```bash
pip install streamlit
```

## System Requirements

- **OS:** Windows 10+, macOS 10.14+, or Linux
- **RAM:** 2 GB minimum, 4 GB recommended
- **Storage:** 500 MB for application + data
- **Python:** 3.9, 3.10, or 3.11

## Next Steps

After successful installation:

1. **Familiarize yourself** with the web interface
2. **Try sample queries** (e.g., "Ashirvaad Atta", HSN: "1101")
3. **Load test data** for better demo results
4. **Customize scrapers** for your specific needs
5. **Set up automated updates** using the daily scraper

## Getting Help

- Check the main [README.md](../README.md)
- Review [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Open an issue on GitHub
- Check Streamlit documentation: https://docs.streamlit.io
