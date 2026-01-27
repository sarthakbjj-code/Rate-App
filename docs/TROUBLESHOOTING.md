# Troubleshooting Guide

## Common Issues and Solutions

### Installation Issues

#### 1. Python Version Error

**Problem:** "Python 3.9+ required"

**Solution:**
```bash
# Check Python version
python --version

# If using Python 3.8 or lower, upgrade:
# On Ubuntu/Debian:
sudo apt update
sudo apt install python3.9

# On macOS (using Homebrew):
brew install python@3.9

# On Windows:
# Download from https://www.python.org/downloads/
```

#### 2. pip Not Found

**Problem:** "pip: command not found"

**Solution:**
```bash
# Install pip
python -m ensurepip --upgrade

# Or use:
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
```

#### 3. Permission Denied During Installation

**Problem:** "Permission denied" when installing packages

**Solution:**
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Or install for user only:
pip install -r requirements.txt --user
```

### Browser Driver Issues

#### 4. Playwright Installation Fails

**Problem:** Browser installation fails

**Solution:**
```bash
# Try manual installation
python -m playwright install chromium

# If still fails, use system browser:
python -m playwright install-deps
python -m playwright install chromium

# On Linux, you might need:
sudo apt-get install libgbm1 libxshmfence1
```

#### 5. Browser Not Found at Runtime

**Problem:** "Browser executable not found"

**Solution:**
```bash
# Reinstall with force
python -m playwright install --force chromium

# Or set environment variable:
export PLAYWRIGHT_BROWSERS_PATH=/home/user/.cache/ms-playwright
```

### Database Issues

#### 6. Database File Not Created

**Problem:** "No such file or directory: data/price_history.db"

**Solution:**
```bash
# Create data directory
mkdir -p data

# Run setup script
python scripts/setup_database.py
```

#### 7. Database Locked

**Problem:** "Database is locked"

**Solution:**
```bash
# Close all connections and restart
# If using daily scraper, stop it first
pkill -f daily_scraper.py

# Then restart the app
streamlit run web_app/app.py
```

#### 8. SQLite Version Error

**Problem:** "SQLite version too old"

**Solution:**
```bash
# Update SQLite
pip install pysqlite3-binary
# Or upgrade system SQLite
```

### Web Scraping Issues

#### 9. No Results from Scrapers

**Problem:** Scrapers return empty lists

**Causes:**
- Product not found on platform
- Scraper template needs implementation
- Website structure changed
- IP blocked by website
- Network issues

**Solutions:**
```bash
# 1. Check internet connection
ping google.com

# 2. Try different product name
# Use exact product name from website

# 3. Check logs
# Look for error messages in console

# 4. Implement real scraping logic
# The current scrapers are templates
# See src/scrapers/ for implementation
```

#### 10. Timeout Errors

**Problem:** "Timeout waiting for page load"

**Solution:**
```bash
# Increase timeout in .env
TIMEOUT=60

# Or reduce concurrent scrapers
# Run scrapers sequentially instead of parallel
```

#### 11. Rate Limiting / IP Blocked

**Problem:** "403 Forbidden" or "Too many requests"

**Solution:**
```bash
# Increase delay between requests in .env
SCRAPE_DELAY=5

# Use different user agents (already configured)
# Consider using proxy rotation
# Reduce scraping frequency
```

### Streamlit Issues

#### 12. Port Already in Use

**Problem:** "Address already in use"

**Solution:**
```bash
# Use different port
streamlit run web_app/app.py --server.port 8502

# Or kill existing process
# On Linux/Mac:
lsof -ti:8501 | xargs kill -9

# On Windows:
netstat -ano | findstr :8501
taskkill /PID <PID> /F
```

#### 13. Streamlit Not Refreshing

**Problem:** Changes not reflected

**Solution:**
```bash
# Clear Streamlit cache
# In the browser, press 'C' then 'Clear cache'

# Or restart the app
# Ctrl+C to stop, then run again
streamlit run web_app/app.py
```

#### 14. Module Not Found Error

**Problem:** "ModuleNotFoundError: No module named 'src'"

**Solution:**
```bash
# Ensure you're running from project root
cd /path/to/Rate-App
streamlit run web_app/app.py

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/Rate-App"
```

### Forecasting Issues

#### 15. ARIMA Model Fails

**Problem:** "ARIMA model fit failed"

**Solution:**
- This is expected with insufficient data
- System falls back to simple moving average
- Load test data: `python scripts/populate_test_data.py`
- Ensure at least 30 data points exist

#### 16. Forecast Returns Zeros

**Problem:** All predictions are 0

**Solution:**
```bash
# Check if historical data exists
# Look at Historical Analysis tab

# Populate test data
python scripts/populate_test_data.py

# Verify data in database
sqlite3 data/price_history.db "SELECT COUNT(*) FROM price_history;"
```

### Performance Issues

#### 17. Slow Page Load

**Problem:** Dashboard takes too long to load

**Solutions:**
- Reduce number of concurrent scrapers
- Implement caching
- Use database queries instead of scraping every time
- Optimize database with indexes (already included)

#### 18. High Memory Usage

**Problem:** Application uses too much RAM

**Solutions:**
```bash
# Reduce forecast period
# Edit config/settings.py
FORECAST_DAYS = 90  # Instead of 180

# Limit historical analysis
HISTORICAL_DAYS = 365  # Instead of 730

# Close other applications
# Restart system if needed
```

### Data Quality Issues

#### 19. Incorrect GST Rate

**Problem:** GST rate seems wrong

**Solution:**
```bash
# Check HSN code is correct (4-8 digits)
# Verify in data/hsn_gst_mapping.json
# Add custom mapping if needed:

# Edit hsn_gst_mapping.json:
{
  "1234": {"rate": 12, "desc": "Your product category"}
}
```

#### 20. Price Anomalies

**Problem:** Unrealistic prices in analysis

**Solution:**
- Check data source quality
- Validate scraped data
- Implement outlier detection
- Manually review and clean data

## Getting Additional Help

If your issue isn't listed here:

1. **Check the logs** - Look for error messages
2. **Search GitHub Issues** - Someone may have had the same problem
3. **Create a new issue** - Provide:
   - Error message
   - Steps to reproduce
   - System information (OS, Python version)
   - Screenshots if applicable

4. **Review documentation:**
   - [README.md](../README.md)
   - [SETUP.md](SETUP.md)

## Reporting Bugs

When reporting bugs, include:

```
**Environment:**
- OS: [e.g., Ubuntu 20.04]
- Python Version: [e.g., 3.9.7]
- Streamlit Version: [run `streamlit version`]

**Description:**
[Clear description of the issue]

**Steps to Reproduce:**
1. [First step]
2. [Second step]
3. [...]

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Error Messages:**
```
[Paste error messages here]
```

**Screenshots:**
[If applicable]
```

## Prevention Tips

- Always use virtual environment
- Keep dependencies updated: `pip install -r requirements.txt --upgrade`
- Backup database before major changes: `cp data/price_history.db data/backup.db`
- Test scrapers individually before running all
- Monitor disk space and memory usage
- Review logs regularly
