# Streamlit Cloud Deployment Notes

## Important: Simplified Dependencies

For Streamlit Cloud deployment, we've removed some heavy dependencies that require system-level installations:

### Removed Dependencies:
- **playwright** - Requires browser binaries
- **selenium** - Requires browser drivers  
- **prophet** - Requires additional C++ compilers
- **xgboost** - Can cause installation issues
- **pytest** - Not needed in production

### Impact on Functionality:

The web scrapers that depend on Playwright/Selenium will show placeholder data instead of live scraping. This is acceptable for demonstration purposes on Streamlit Cloud.

**For full functionality with live scraping:**
- Deploy locally: `python setup.py && streamlit run web_app/app.py`
- Or use Docker/Heroku with the full `requirements.txt`

### What Still Works on Streamlit Cloud:

✅ Full UI with all tabs and visualizations
✅ Historical data analysis (using pre-populated database)
✅ Price forecasting with ARIMA and moving averages
✅ Recommendation engine
✅ GST rate lookup
✅ All charts and interactive features
✅ Export functionality

### Local Development:

For local development with full scraping capabilities, use `requirements-full.txt`:

```bash
pip install -r requirements-full.txt
playwright install chromium
```

This file contains all original dependencies including Playwright and Selenium.
