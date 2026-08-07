# Skylark Drones BI Agent - Deployment Guide

This guide covers deploying the BI agent to production on various platforms.

## 📋 Pre-Deployment Checklist

- [ ] Monday.com API token obtained and validated
- [ ] OpenAI API key obtained and validated
- [ ] Environment variables configured
- [ ] Both backend and frontend tested locally
- [ ] Health checks passing (`/api/health` returns 200)
- [ ] Decision log reviewed for production considerations
- [ ] Security review completed
- [ ] Monitoring/logging plan in place

---

## 🐳 Docker Deployment (Recommended)

### Local Docker Testing

1. **Build images**
   ```bash
   docker-compose build
   ```

2. **Create .env file**
   ```bash
   cat > .env << EOF
   MONDAY_API_TOKEN=your_monday_api_token
   OPENAI_API_KEY=your_openai_api_key
   EOF
   ```

3. **Run services**
   ```bash
   docker-compose up -d
   ```

4. **View logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

5. **Test endpoints**
   ```bash
   # Backend health
   curl http://localhost:8000/api/health

   # Frontend
   open http://localhost
   ```

6. **Stop services**
   ```bash
   docker-compose down
   ```

---

## 🚀 Render.com Deployment

**Estimated cost**: $12/month for backend + $0 for static frontend

### 1. Prepare Repository

```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit: Skylark BI Agent"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/monday-bi-agent.git
git branch -M main
git push -u origin main
```

### 2. Deploy Backend

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: `skylark-bi-backend`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - **Root Directory**: `backend`
5. Add environment variables:
   - `MONDAY_API_TOKEN`: Your Monday.com API token
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `CACHE_TTL`: 300
6. Click "Create Web Service"

**Result**: Backend deployed at `https://skylark-bi-backend.onrender.com`

### 3. Deploy Frontend

1. Click "New +" → "Static Site"
2. Connect GitHub repository
3. Configure:
   - **Name**: `skylark-bi-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Add environment variable:
   - `VITE_API_URL`: `https://skylark-bi-backend.onrender.com`
5. Click "Create Static Site"

**Result**: Frontend deployed at `https://skylark-bi-frontend.onrender.com`

### 4. Update Frontend Configuration

Edit `frontend/vite.config.js`:

```javascript
export default {
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        rewrite: (path) => path
      }
    }
  }
}
```

Update `frontend/src/App.jsx`:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const response = await fetch(`${API_URL}/api/chat`, {
  // ...
});
```

---

## 🚀 Heroku Deployment

**Estimated cost**: $7-50/month depending on dyno size

### 1. Install Heroku CLI

```bash
# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh

# Windows
# Download from https://cli-assets.heroku.com/heroku-x64.exe
```

### 2. Deploy Backend

```bash
# Login to Heroku
heroku login

# Create app
heroku create skylark-bi-api

# Set environment variables
heroku config:set MONDAY_API_TOKEN=your_token
heroku config:set OPENAI_API_KEY=your_key
heroku config:set CACHE_TTL=300

# Create Procfile in backend/
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile

# Deploy
git subtree push --prefix backend heroku main

# View logs
heroku logs --tail
```

### 3. Deploy Frontend

```bash
# Create app
heroku create skylark-bi-app

# Create Procfile in frontend/
cat > frontend/Procfile << EOF
web: npm run preview
EOF

# Deploy
git subtree push --prefix frontend heroku main
```

---

## 🌩️ AWS Deployment

**Estimated cost**: $30-100/month

### 1. Backend (Elastic Beanstalk)

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 skylark-bi-api -r us-east-1

# Create Procfile
echo "web: uvicorn app.main:app" > Procfile

# Create environment
eb create skylark-bi-env

# Set environment variables
eb setenv MONDAY_API_TOKEN=your_token OPENAI_API_KEY=your_key

# Deploy
eb deploy

# Monitor
eb open  # Opens app in browser
eb logs  # View logs
```

### 2. Frontend (S3 + CloudFront)

```bash
# Build
npm run build

# Create S3 bucket
aws s3 mb s3://skylark-bi-frontend

# Upload files
aws s3 sync dist/ s3://skylark-bi-frontend/ --delete

# Create CloudFront distribution in AWS Console
# - Origin: S3 bucket
# - Viewer protocol: Redirect HTTP to HTTPS
# - Cache policy: Managed-CachingOptimized
```

---

## 🐙 GitHub Actions CI/CD

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Lint
        run: |
          cd backend
          pip install flake8
          flake8 app --max-line-length=120
      
      - name: Test
        run: |
          cd backend
          pytest tests/
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Build frontend
        run: |
          cd frontend
          npm ci
          npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Render
        run: |
          curl https://api.render.com/deploy/srv-${{ secrets.RENDER_SERVICE_ID }}?key=${{ secrets.RENDER_API_KEY }} \
            -X POST
```

---

## 🔒 Production Security Checklist

### Environment
- [ ] HTTPS/TLS enabled (SSL certificate)
- [ ] Secrets stored in environment variables (not code)
- [ ] API keys rotated every 90 days
- [ ] Database backups automated
- [ ] Disaster recovery plan documented

### Application
- [ ] Input validation on all endpoints
- [ ] CORS properly configured (not `*`)
- [ ] Rate limiting enabled
- [ ] SQL injection protection (N/A - using ORM)
- [ ] XSS protection headers set
- [ ] CSRF protection enabled
- [ ] Authentication implemented
- [ ] Authorization checks in place

### Infrastructure
- [ ] DDoS protection enabled
- [ ] WAF (Web Application Firewall) configured
- [ ] VPC with restricted security groups
- [ ] CloudTrail/audit logging enabled
- [ ] Secrets manager integration
- [ ] Regular security updates applied

### Monitoring
- [ ] Error tracking (Sentry/Rollbar)
- [ ] Performance monitoring (New Relic/DataDog)
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Log aggregation (CloudWatch/ELK)
- [ ] Alerting configured
- [ ] Health checks configured

---

## 📊 Monitoring & Logging

### Application Monitoring

**Sentry Integration** (error tracking):

```python
# In backend/app/core/config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=1.0,
)
```

### Log Aggregation

**CloudWatch** (AWS):
```python
# In backend/app/core/logging_config.py
import watchtower

handler = watchtower.CloudWatchLogHandler(
    log_group='skylark-bi-agent',
    stream_name='backend'
)
logger.addHandler(handler)
```

### Uptime Monitoring

Use UptimeRobot or similar:
- Monitor: `https://your-api.com/api/health`
- Check interval: 5 minutes
- Alert if down >5 minutes

---

## 🔄 Updating Deployment

### Render.com
- Automatic redeploy on push to main
- Manual redeploy: Dashboard → Manual Deploy

### Heroku
```bash
# Update code
git add .
git commit -m "Update message"

# Deploy
git push heroku main

# View deployment status
heroku releases
heroku logs --tail
```

### AWS
```bash
# Update and redeploy
eb deploy

# Check status
eb status
```

---

## 🐛 Troubleshooting Deployment

### Issue: Backend returns 502 Bad Gateway

**Check**:
```bash
# View logs
heroku logs --tail
# or
eb logs

# Check health endpoint
curl https://your-api.com/api/health
```

**Fix**:
- Verify environment variables set correctly
- Check API token validity
- Restart dyno/instance
- Check application logs for errors

### Issue: Frontend shows blank page

**Check**:
```bash
# Browser console for errors
# Network tab for failed requests
# Check API_URL configuration
```

**Fix**:
- Verify `VITE_API_URL` environment variable
- Check CORS headers from backend
- Clear browser cache
- Rebuild frontend

### Issue: Slow response times

**Check**:
```bash
# Monday.com API rate limits
# OpenAI API throttling
# Database query performance
# Network latency
```

**Fix**:
- Increase cache TTL
- Optimize queries
- Scale up instance size
- Add CDN for static content

### Issue: Authentication fails

**Check**:
```bash
# Monday.com API token validity
curl -H "Authorization: YOUR_TOKEN" \
  https://api.monday.com/v2 \
  -d '{"query":"{me{id}}"}'

# OpenAI API key validity
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

**Fix**:
- Regenerate API tokens
- Update environment variables
- Restart services

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com)
- [Render.com Guide](https://render.com/docs)
- [Heroku Deployment](https://devcenter.heroku.com)
- [AWS Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Version**: 1.0  
**Last Updated**: August 7, 2026
