# Procurement Intelligence System

🚀 AI-Powered Price Intelligence for Smart Procurement

## Overview
This system provides real-time price intelligence, GST lookup, and AI-powered price predictions for procurement decisions.

## Features
- ✅ Multi-source price scraping (Blinkit, Amazon, Flipkart, JioMart, IndiaMART)
- ✅ Automated GST rate lookup (ClearTax + CBIC)
- ✅ AI price forecasting (6-month predictions)
- ✅ Historical price analysis
- ✅ Web-based dashboard

## Getting Started
### Local Preview
Open `public/index.html` in a browser to preview the landing page.

### Docker Deployment
Build and run the containerized static site:

```bash
docker build -t rate-app .
docker run --rm -p 8080:80 rate-app
```

Visit `http://localhost:8080` to view the app.
