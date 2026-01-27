# Deployment Guide

## Overview

This guide covers multiple deployment options for the Procurement Intelligence System. The easiest option for GitHub users is **Streamlit Cloud** (free for public repositories).

---

## Option 1: Streamlit Cloud (Recommended) ⭐

**Free, easy, and specifically designed for Streamlit apps.**

### Prerequisites
- GitHub repository (public or private with Streamlit Cloud Team plan)
- Streamlit Cloud account (free at https://streamlit.io/cloud)

### Steps

#### 1. Prepare Your Repository

Ensure these files exist in your repo (they already do):
- ✅ `web_app/app.py` (main application)
- ✅ `requirements.txt` (dependencies)
- ✅ `.gitignore` (excludes database and logs)

#### 2. Create Streamlit-Specific Files

**a) Create `packages.txt`** (for system dependencies like Playwright):

```bash
# Create in repository root
cat > packages.txt << 'EOF'
chromium
chromium-driver
EOF
```

**b) Update `.streamlit/config.toml`** (optional, for custom settings):

```bash
mkdir -p .streamlit
cat > .streamlit/config.toml << 'EOF'
[server]
headless = true
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
EOF
```

#### 3. Deploy to Streamlit Cloud

1. **Go to:** https://share.streamlit.io/
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure:**
   - Repository: `sarthakbjj-code/Rate-App`
   - Branch: `main` (or your default branch)
   - Main file path: `web_app/app.py`
5. **Advanced settings (optional):**
   - Add secrets (if using API keys)
   - Set Python version: `3.9`
6. **Click "Deploy"**

#### 4. Wait for Deployment

- Initial deployment takes 2-5 minutes
- Streamlit Cloud will install dependencies automatically
- You'll get a URL like: `https://your-app-name.streamlit.app`

#### 5. Access Your App

Your app will be live at: `https://[your-app-name].streamlit.app`

### Managing Secrets on Streamlit Cloud

If you use API keys (e.g., KEEPA_API_KEY, SERPAPI_KEY):

1. Go to your app settings
2. Click "Secrets" section
3. Add secrets in TOML format:

```toml
KEEPA_API_KEY = "your_key_here"
SERPAPI_KEY = "your_key_here"
SCRAPE_DELAY = 3
```

### Updating Your Deployment

Streamlit Cloud auto-deploys when you push to the connected branch:

```bash
git add .
git commit -m "Update feature"
git push origin main
```

The app will automatically redeploy in 1-2 minutes.

---

## Option 2: Heroku

**Good for production deployments with custom domains.**

### Prerequisites
- Heroku account (https://heroku.com)
- Heroku CLI installed

### Steps

#### 1. Create Required Files

**a) Create `Procfile`:**

```bash
cat > Procfile << 'EOF'
web: sh setup.sh && streamlit run web_app/app.py
EOF
```

**b) Create `setup.sh`:**

```bash
cat > setup.sh << 'EOF'
#!/bin/bash
mkdir -p ~/.streamlit/

echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
\n\
" > ~/.streamlit/config.toml

# Setup database
python scripts/setup_database.py

# Populate test data (optional)
# python scripts/populate_test_data.py
EOF
chmod +x setup.sh
```

**c) Create `runtime.txt`:**

```bash
echo "python-3.9.18" > runtime.txt
```

#### 2. Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Set buildpacks (for Playwright support)
heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add --index 2 heroku/python

# Create Aptfile for system dependencies
cat > Aptfile << 'EOF'
chromium-browser
chromium-chromedriver
EOF

# Deploy
git push heroku main

# Open app
heroku open
```

#### 3. Configure Environment Variables

```bash
heroku config:set SCRAPE_DELAY=3
heroku config:set HEADLESS=True
# Add API keys if needed
heroku config:set KEEPA_API_KEY=your_key
```

### Costs
- Free tier: Limited hours/month
- Hobby tier: $7/month
- Professional: $25+/month

---

## Option 3: Docker + GitHub Container Registry

**Best for self-hosting or cloud deployment.**

### Steps

#### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN python -m playwright install chromium

# Copy application
COPY . .

# Setup database
RUN python scripts/setup_database.py

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "web_app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### 2. Create `.dockerignore`

```
.git
.gitignore
__pycache__
*.pyc
*.pyo
*.pyd
.env
venv/
logs/
exports/
data/*.db
*.md
docs/
tests/
```

#### 3. Build and Test Locally

```bash
# Build image
docker build -t procurement-app .

# Run container
docker run -p 8501:8501 procurement-app

# Test at http://localhost:8501
```

#### 4. Deploy to GitHub Container Registry

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Tag image
docker tag procurement-app ghcr.io/sarthakbjj-code/rate-app:latest

# Push to registry
docker push ghcr.io/sarthakbjj-code/rate-app:latest
```

#### 5. Deploy Anywhere

Now you can deploy the container to:
- **AWS ECS/Fargate**
- **Azure Container Instances**
- **Google Cloud Run**
- **DigitalOcean App Platform**
- **Your own server with Docker**

Example for Google Cloud Run:

```bash
gcloud run deploy procurement-app \
  --image ghcr.io/sarthakbjj-code/rate-app:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

---

## Option 4: AWS Elastic Beanstalk

### Steps

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.9 procurement-app

# Create environment
eb create procurement-env

# Deploy
eb deploy

# Open
eb open
```

---

## Recommended Deployment Strategy

### For Quick Demo/Testing:
✅ **Use Streamlit Cloud** - Free, easy, 5-minute setup

### For Production:
1. **Small projects:** Streamlit Cloud (free tier)
2. **Medium projects:** Heroku or Google Cloud Run
3. **Enterprise:** AWS/Azure with Docker containers

---

## Post-Deployment Checklist

After deploying, verify:

- [ ] App loads successfully
- [ ] Database is initialized
- [ ] GST lookup works (check fallback database)
- [ ] Test data is loaded (if applicable)
- [ ] Input validation works
- [ ] Charts render correctly
- [ ] No errors in logs

---

## Troubleshooting Deployment Issues

### Streamlit Cloud Issues

**Issue:** App fails to start

**Solution:**
```bash
# Check logs in Streamlit Cloud dashboard
# Verify requirements.txt has all dependencies
# Ensure Python version is compatible (3.9+)
```

**Issue:** ModuleNotFoundError

**Solution:**
```bash
# Add missing packages to requirements.txt
# Ensure package names match PyPI exactly
```

**Issue:** Database errors

**Solution:**
```bash
# Ensure setup_database.py runs before app starts
# Check that data/ directory exists
# Verify database path is relative, not absolute
```

### Heroku Issues

**Issue:** App crashes on startup

**Solution:**
```bash
# Check Heroku logs
heroku logs --tail

# Verify Procfile is correct
# Check that port is set from $PORT environment variable
```

**Issue:** Playwright browser not found

**Solution:**
```bash
# Add Aptfile with chromium dependencies
# Verify buildpacks are in correct order
```

### Docker Issues

**Issue:** Container fails to start

**Solution:**
```bash
# Check container logs
docker logs [container_id]

# Test build locally first
docker build -t test-app .
docker run -p 8501:8501 test-app
```

---

## Environment Variables for Deployment

Set these in your deployment platform:

```bash
# Required
DATABASE_PATH=data/price_history.db
SCRAPE_DELAY=3
MAX_RETRIES=3
TIMEOUT=30
HEADLESS=True

# Optional (for enhanced features)
KEEPA_API_KEY=your_key
SERPAPI_KEY=your_key
LOG_LEVEL=INFO
```

---

## Performance Optimization for Deployment

### 1. Use SQLite in Memory Mode (for demos)

```python
# In config/settings.py
DATABASE_PATH = ':memory:'  # For read-only demos
```

### 2. Enable Streamlit Caching

Already implemented in the app with `@st.cache_data`

### 3. Reduce Resource Usage

```python
# Limit concurrent scrapers
MAX_CONCURRENT_SCRAPERS = 3

# Reduce forecast period
FORECAST_DAYS = 90  # Instead of 180
```

---

## Monitoring Your Deployment

### Streamlit Cloud
- Built-in analytics in dashboard
- View real-time logs
- Monitor resource usage

### Heroku
```bash
# View logs
heroku logs --tail

# Monitor dynos
heroku ps

# View metrics
heroku addons:create librato
```

### Docker/Cloud Platforms
- Use CloudWatch (AWS), Stackdriver (GCP), or Azure Monitor
- Set up alerts for errors
- Monitor CPU/memory usage

---

## Scaling Considerations

### Single User → Small Team (< 100 users)
- **Streamlit Cloud** free tier is sufficient
- Use SQLite database

### Medium Traffic (100-1000 users)
- **Heroku Professional** or **Cloud Run**
- Consider PostgreSQL instead of SQLite
- Add Redis for caching

### High Traffic (1000+ users)
- **AWS/Azure/GCP** with auto-scaling
- PostgreSQL with read replicas
- CDN for static assets
- Load balancer

---

## Cost Comparison

| Platform | Free Tier | Paid Plans | Best For |
|----------|-----------|------------|----------|
| Streamlit Cloud | ✅ Public repos | $20/mo (Private) | Quick demos, MVPs |
| Heroku | Limited hours | $7-$50+/mo | Small-medium apps |
| Google Cloud Run | 2M requests/mo | Pay per use | Variable traffic |
| AWS ECS/Fargate | Free tier 1yr | $10-$100+/mo | Enterprise |
| DigitalOcean | $0 | $5-$40/mo | Full control |

---

## Next Steps

1. **Choose your deployment platform** (Streamlit Cloud recommended for GitHub)
2. **Follow the specific guide** above
3. **Test thoroughly** after deployment
4. **Set up monitoring** and alerts
5. **Share your app URL** with users!

## Need Help?

- **Streamlit Cloud:** https://docs.streamlit.io/streamlit-community-cloud
- **Heroku:** https://devcenter.heroku.com/categories/deployment
- **Docker:** https://docs.docker.com/
- **GitHub Issues:** Open an issue in the repository

---

**Happy Deploying! 🚀**
