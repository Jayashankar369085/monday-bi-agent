# Testing Guide - Skylark Drones BI Agent

Comprehensive testing procedures for local development, staging, and production deployment.

---

## 🧪 Local Development Testing

### 1. Backend Testing

#### Setup Test Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pip install pytest pytest-cov
```

#### Manual API Testing

**Health Check**:
```bash
curl http://localhost:8000/api/health
# Expected response:
# {"status": "healthy", "monday_com": "connected", "openai": "connected"}
```

**Chat Endpoint**:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How many projects are completed?"}'

# Expected response:
# {"answer": "Your answer here..."}
```

**Leadership Update**:
```bash
curl http://localhost:8000/api/leadership-update

# Expected response:
# {"status": "success", "report": "...executive summary...", "timestamp": "...", "metrics": {...}}
```

#### Unit Tests

Create `backend/tests/test_analytics.py`:

```python
import pytest
import pandas as pd
from app.services.analytics.sales import SalesAnalytics
from app.services.analytics.operations import OperationsAnalytics
from app.services.analytics.finance import FinanceAnalytics

class TestSalesAnalytics:
    def test_pipeline_health_calculation(self):
        # Create test data
        deals = pd.DataFrame({
            'Deal Status': ['Open', 'Open', 'Won', 'Lost'],
            'Masked Deal value': [100, 200, 150, 50],
        })
        
        result = SalesAnalytics.analyze_pipeline_health(deals)
        
        assert result['total_deals'] == 4
        assert result['win_rate_percentage'] == 25.0
        assert result['total_pipeline_value'] == 500

class TestOperationsAnalytics:
    def test_execution_analysis(self):
        work_orders = pd.DataFrame({
            'Execution Status': ['Completed', 'Completed', 'Ongoing'],
            'Amount in Rupees (Excl of GST) (Masked)': [100, 200, 150],
        })
        
        result = OperationsAnalytics.analyze_project_execution(work_orders)
        
        assert result['total_projects'] == 3
        assert result['completion_rate'] == 66.67

class TestFinanceAnalytics:
    def test_revenue_metrics(self):
        work_orders = pd.DataFrame({
            'Billed Value in Rupees (Excl of GST.) (Masked)': [100, 200, 150],
            'Collected Amount in Rupees (Incl of GST.) (Masked)': [100, 150, 150],
            'Amount in Rupees (Excl of GST) (Masked)': [100, 200, 150],
        })
        
        result = FinanceAnalytics.analyze_revenue_metrics(work_orders)
        
        assert result['total_billed'] == 450
        assert result['total_collected'] == 400
```

Run tests:
```bash
pytest backend/tests/ -v --cov=app
```

#### Integration Tests

Create `backend/tests/test_integration.py`:

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestChatAPI:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert 'status' in data
    
    def test_chat_endpoint_requires_question(self):
        response = client.post("/api/chat", json={})
        assert response.status_code == 422  # Validation error
    
    def test_chat_endpoint_basic_query(self):
        response = client.post("/api/chat", json={"question": "What is our total revenue?"})
        assert response.status_code == 200
        data = response.json()
        assert 'answer' in data
```

---

### 2. Frontend Testing

#### Setup

```bash
cd frontend
npm install
npm install --save-dev @testing-library/react @testing-library/jest-dom vitest
```

#### Manual UI Testing

1. **Start frontend dev server**
   ```bash
   npm run dev
   ```

2. **Test in browser**:
   - Open http://localhost:5173
   - Check API status indicator
   - Send test query
   - Verify message display
   - Test example buttons
   - Try leadership update button

#### Automated Tests

Create `frontend/src/App.test.jsx`:

```javascript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  test('renders welcome message', () => {
    render(<App />);
    expect(screen.getByText('Welcome to Skylark BI Agent')).toBeInTheDocument();
  });

  test('displays example queries', () => {
    render(<App />);
    expect(screen.getByText(/Try asking:/i)).toBeInTheDocument();
  });

  test('has send button disabled when input is empty', () => {
    render(<App />);
    const sendButton = screen.getByText('Send');
    expect(sendButton).toBeDisabled();
  });

  test('enables send button with input', async () => {
    render(<App />);
    const input = screen.getByPlaceholderText(/Ask a question/i);
    fireEvent.change(input, { target: { value: 'Test question' } });
    
    const sendButton = screen.getByText('Send');
    await waitFor(() => {
      expect(sendButton).not.toBeDisabled();
    });
  });
});
```

Run tests:
```bash
npm test
```

---

## 🔧 Staging/Pre-Production Testing

### Docker Compose Testing

1. **Build and run services**
   ```bash
   docker-compose up --build
   ```

2. **Verify services**
   ```bash
   # Backend health
   curl http://localhost:8000/api/health

   # Frontend access
   open http://localhost

   # View logs
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

3. **Test end-to-end flow**
   - Navigate to http://localhost
   - Send query
   - Verify response appears
   - Test leadership update

4. **Load testing**
   ```bash
   # Install Apache Bench
   brew install httpd  # macOS
   
   # Load test
   ab -n 100 -c 10 http://localhost:8000/api/health
   ```

### Data Validation Testing

1. **Create test data snapshot**
   ```bash
   # Export small dataset from Monday.com
   # Save to test_data.json
   ```

2. **Verify data cleaning**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Data quality check"
     }'
   ```

3. **Check for errors/warnings**
   - Look for "Update Required" flags
   - Check "Masked" data handling
   - Verify date parsing

---

## 📊 Production Testing

### Pre-Deployment Checklist

**Code Quality**:
- [ ] Linting passes: `npm run lint`, `flake8 backend/app`
- [ ] No console warnings/errors
- [ ] No hardcoded secrets
- [ ] Documentation up to date

**Security**:
- [ ] Input validation on all endpoints
- [ ] No SQL injection vulnerabilities
- [ ] No XSS vulnerabilities
- [ ] CORS properly configured
- [ ] API rate limiting configured

**Performance**:
- [ ] Response time <2 seconds for queries
- [ ] Cache working (repeated queries faster)
- [ ] Database queries optimized
- [ ] No memory leaks in profiling

**Functionality**:
- [ ] All API endpoints working
- [ ] Error handling graceful
- [ ] Fallbacks for API failures
- [ ] Data quality scoring accurate

### Post-Deployment Testing

#### Smoke Tests (Run immediately after deployment)

```bash
#!/bin/bash
set -e

API_URL="https://your-deployed-api.com"
FRONTEND_URL="https://your-deployed-frontend.com"

echo "Testing backend health..."
curl -f "${API_URL}/api/health" || exit 1

echo "Testing chat endpoint..."
curl -f -X POST "${API_URL}/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"question": "Test"}' || exit 1

echo "Testing leadership update..."
curl -f "${API_URL}/api/leadership-update" || exit 1

echo "Testing frontend availability..."
curl -f "${FRONTEND_URL}" | grep -q "Skylark Drones" || exit 1

echo "✅ All smoke tests passed"
```

#### Canary Testing

1. **Deploy to 10% of traffic**
   - Configure load balancer
   - Route 10% to new version
   - Monitor error rates

2. **Monitor metrics**
   ```bash
   # Check error rate
   # Check response time
   # Check resource usage
   ```

3. **Increase to 100%**
   - If all metrics normal, increase traffic gradually
   - Rollback if issues detected

#### User Acceptance Testing (UAT)

1. **Provide test accounts** to key stakeholders
2. **Use cases to validate**:
   - Revenue query works correctly
   - Pipeline analysis accurate
   - Leadership update comprehensive
   - Performance satisfactory
   - UI intuitive

3. **Collect feedback**
   - Document any issues
   - Create follow-up tasks
   - Schedule post-launch review

---

## 🔍 Monitoring & Continuous Testing

### Automated Monitoring

**Uptime Monitoring** (UptimeRobot):
- Monitor `/api/health` every 5 minutes
- Alert if down >5 minutes
- 99.9% uptime SLA

**Performance Monitoring**:
```javascript
// Add to backend routes
import time
import logging

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    if process_time > 5:  # Alert if > 5s
        logger.warning(f"Slow request: {request.url} took {process_time}s")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

**Error Tracking** (Sentry):
```python
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0,
)
```

### Scheduled Tests

**Daily**:
- Health check (automated)
- Error log review
- Performance report

**Weekly**:
- Full regression test
- Data quality audit
- Backup verification

**Monthly**:
- Disaster recovery drill
- Security audit
- User feedback review

---

## 📈 Performance Benchmarks

### Expected Performance Targets

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Health check response | <100ms | >500ms |
| Chat query (cold) | 2-3s | >5s |
| Chat query (cached) | <500ms | >1s |
| Leadership update | 3-5s | >10s |
| 99th percentile response | <5s | >10s |
| Error rate | <0.1% | >1% |

### Load Testing with Locust

Create `load_test.py`:

```python
from locust import HttpUser, task, between

class BiAgentUser(HttpUser):
    wait_time = between(2, 5)

    @task
    def health_check(self):
        self.client.get("/api/health")
    
    @task
    def ask_query(self):
        self.client.post("/api/chat", 
            json={"question": "What is our total revenue?"})
    
    @task
    def get_update(self):
        self.client.get("/api/leadership-update")
```

Run load test:
```bash
pip install locust
locust -f load_test.py --host=http://localhost:8000 --users=100 --spawn-rate=10
```

---

## 🆘 Debugging Guide

### Enable Debug Logging

**Backend**:
```python
# In app/core/logging_config.py
logging.basicConfig(level=logging.DEBUG)
```

**Frontend**:
```javascript
// In App.jsx
console.log('Query:', query);
console.log('Response:', response);
```

### Common Issues & Fixes

| Issue | Check | Fix |
|-------|-------|-----|
| 502 Bad Gateway | Backend logs | Restart backend, check API keys |
| Blank page | Browser console | Check API_URL, clear cache |
| Slow response | Network tab | Check API limits, increase cache |
| Auth fails | API token | Regenerate and update .env |
| 404 on queries | Routes registered | Verify routes.py includes router |

---

## 📝 Test Report Template

```markdown
# Test Report - [Date]

## Summary
- Total tests run: X
- Passed: Y
- Failed: Z
- Coverage: A%

## Smoke Tests
- [x] Health check
- [x] Chat endpoint
- [x] Leadership update
- [x] Frontend loads

## Regression Tests
- [x] Revenue queries
- [x] Pipeline analysis
- [x] Sectoral performance
- [x] Data cleaning

## Performance
- Average response time: Xms
- P99 response time: Yms
- Error rate: Z%

## Issues Found
- [ ] None
- [ ] See attached issues list

## Recommendations
- [Bullet points]

## Sign-off
- QA: [Name] Date: [Date]
- Approved: [Name] Date: [Date]
```

---

**Version**: 1.0  
**Last Updated**: August 7, 2026
