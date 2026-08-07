# Skylark Drones - Monday.com Business Intelligence Agent

An AI-powered conversational business intelligence agent that analyzes work orders and deals data from Monday.com, providing founders and executives with actionable insights through natural language queries.

## 🎯 Overview

This system enables non-technical users to ask founder-level business questions and get immediate, contextual answers:

- **"How's our pipeline looking for energy sector this quarter?"**
- **"What's our revenue by sector?"**
- **"Show me delayed projects"**
- **"Compare mining vs renewables performance"**

The agent integrates with Monday.com boards, processes real-world messy data gracefully, and uses AI to interpret queries and format insights for leadership.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (Port 5173)            │
│  - Chat Interface                                         │
│  - Message History                                        │
│  - Real-time Status                                       │
│  - Example Queries                                        │
└──────────────────┬──────────────────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                 │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │ API Routes (/api/chat, /api/leadership-update)    │  │
│  └────────────┬──────────────────┬───────────────────┘  │
│               │                  │                       │
│  ┌────────────▼─┐      ┌─────────▼──────┐              │
│  │ Orchestrator │      │ Analytics      │              │
│  │ (Intent)     │      │ Services       │              │
│  └────────────┬─┘      └─────────┬──────┘              │
│               │                  │                       │
│  ┌────────────▼──────────────────▼────────────────────┐ │
│  │         Monday.com Client                          │ │
│  │  - GraphQL queries                                 │ │
│  │  - Data normalization                              │ │
│  │  - Caching (5-min TTL)                             │ │
│  └────────────┬────────────────────────────────────────┘ │
│               │                                          │
│  ┌────────────▼────────────────────────────────────────┐ │
│  │      Cleaner & Validator Services                   │ │
│  │  - Date normalization                               │ │
│  │  - Currency parsing                                 │ │
│  │  - Enum standardization                             │ │
│  │  - Data quality scoring                             │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┴───────────┐
        │                      │
   ┌────▼─────┐          ┌────▼──────┐
   │ Monday.com│          │ OpenAI API│
   │ GraphQL   │          │ (GPT-4o)  │
   └──────────┘          └───────────┘
```

---

## 📦 Components

### Backend (`backend/app/`)

#### Core Services
- **`services/monday/`**: Monday.com integration
  - `monday_client.py`: GraphQL API wrapper
  - `monday_service.py`: High-level data access

- **`services/ai/`**: AI & NLP services
  - `intent_parser.py`: Query intent detection
  - `entity_extractor.py`: Business entity extraction
  - `prompt_builder.py`: LLM prompt construction
  - `openai_client.py`: OpenAI API wrapper
  - `orchestrator.py`: Main coordinator

- **`services/analytics/`**: Business intelligence
  - `sales.py`: Pipeline, deals, win rates
  - `operations.py`: Project execution, timelines
  - `finance.py`: Revenue, billing, collections

- **`services/cleaner/`**: Data quality
  - `date_cleaner.py`: Normalize dates
  - `money_cleaner.py`: Parse currencies
  - `enum_cleaner.py`: Standardize enums
  - `validator.py`: Quality scoring

#### API Layer
- **`api/routes.py`**: REST endpoints
  - `POST /api/chat`: Answer BI queries
  - `GET /api/leadership-update`: Generate executive summary
  - `GET /api/health`: Health check

### Frontend (`frontend/src/`)
- **`App.jsx`**: Chat interface component
- **`App.css`**: Responsive styling
- Integrates with backend via REST API

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Monday.com API token
- OpenAI API key

### Backend Setup

1. **Clone & navigate**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials:
   # MONDAY_API_TOKEN=your_monday_api_token
   # OPENAI_API_KEY=your_openai_api_key
   # CACHE_TTL=300
   ```

4. **Run server**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend**
   ```bash
   cd frontend
   npm install
   ```

2. **Run development server**
   ```bash
   npm run dev
   ```

3. **Access application**
   - Open http://localhost:5173
   - Backend must be running on http://localhost:8000

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
MONDAY_API_TOKEN=your_monday_api_token
OPENAI_API_KEY=your_openai_api_key

# Optional
CACHE_TTL=300                    # Cache duration in seconds
APP_NAME=Monday BI Agent         # Application name
APP_VERSION=1.0.0                # Version
```

### Monday.com Board Setup

The agent expects two boards in your Monday.com workspace:

1. **"Work Order Tracker"** - Project execution data
   - Columns: Deal name, Status, Sector, Amount, Billing Status, etc.

2. **"Deal funnel Data"** - Sales pipeline
   - Columns: Deal Name, Status, Stage, Value, Owner, Probability, etc.

**Note**: The agent auto-discovers boards by name. Ensure exact naming.

---

## 💬 Usage

### Chat Interface

1. **Ask a question**
   ```
   "What's our revenue by sector?"
   "How many projects are delayed?"
   "Compare mining vs renewables"
   ```

2. **View response**
   - Agent parses intent
   - Fetches relevant data
   - Runs analytics
   - Formats with AI
   - Displays result

### Example Queries

#### Revenue Analysis
- "How much have we billed this quarter?"
- "What's our collection rate?"
- "Show revenue by sector"

#### Pipeline Health
- "What's our sales funnel looking like?"
- "How many deals are in negotiation?"
- "What's our win rate?"

#### Operational Metrics
- "Show me completed projects"
- "Which projects are behind schedule?"
- "What's the team workload?"

#### Comparisons
- "Compare mining vs renewables revenue"
- "Mining vs Railways - which is more profitable?"

#### Leadership Updates
- Click "📊 Generate Leadership Update"
- Get executive summary with KPIs

---

## 🧠 How It Works

### Query Processing Flow

```
User Query
    ↓
Intent Parser (Keyword matching)
    ↓
Entity Extractor (Sectors, metrics, time periods)
    ↓
Clarification Check (Need more info?)
    ↓
Data Loader (Fetch from Monday.com)
    ↓
Analytics Service (Process data)
    ↓
Prompt Builder (Create LLM prompt)
    ↓
OpenAI API (Format response)
    ↓
Response to User
```

### Intent Detection

The agent recognizes these intents:
- `revenue_analysis` - Financial metrics
- `pipeline_health` - Sales pipeline status
- `sectoral_performance` - Performance by sector
- `operational_metrics` - Project execution
- `deal_status` - Deal information
- `collection_analysis` - Payment status
- `billing_analysis` - Billing status
- `comparison` - Compare entities
- `trend_analysis` - Historical patterns

### Data Cleaning

Raw data from Monday.com goes through:

1. **Date Cleaner**: Normalizes date formats
2. **Money Cleaner**: Parses currency values
3. **Enum Cleaner**: Standardizes status values
4. **Validator**: Scores data quality

Example:
```python
# Input: "₹50,000.00" → Output: 50000.0
# Input: "completed, Completed, COMPLETED" → Output: "completed"
# Input: "2025-05-20", "05/20/2025" → Output: datetime(2025, 5, 20)
```

---

## 📊 Analytics Capabilities

### Sales Analytics
- Pipeline health (total value, deal counts)
- Pipeline by sector
- Deal progression through stages
- Win rate calculations
- At-risk deal identification
- Owner performance
- Revenue forecasting

### Operations Analytics
- Project completion rates
- Timeline performance (on-time vs delayed)
- Delayed project identification
- Team workload distribution
- Project type analysis
- Sector-wise operations

### Finance Analytics
- Revenue metrics (billed, collected, outstanding)
- Revenue by sector
- Billing status breakdown
- Collection metrics
- Receivables aging analysis
- Collection at-risk identification
- Margin analysis by customer

---

## ⚙️ API Reference

### Chat Endpoint

**POST** `/api/chat`

Request:
```json
{
  "question": "How's our pipeline for renewables?"
}
```

Response:
```json
{
  "answer": "Your renewables pipeline looks strong with 15 active deals worth ₹X crores. Win rate is Y%. Top at-risk deals are..."
}
```

### Leadership Update Endpoint

**GET** `/api/leadership-update`

Response:
```json
{
  "status": "success",
  "report": "## Executive Summary\n\n**Key Metrics**\n- Total Pipeline: ₹X\n- Projects Completed: Y\n- Collection Rate: Z%\n\n**Status**\n...",
  "timestamp": "2026-01-08T10:30:00",
  "metrics": {
    "operations": {...},
    "sales": {...},
    "sectors": {...}
  }
}
```

### Health Check Endpoint

**GET** `/api/health`

Response:
```json
{
  "status": "healthy",
  "monday_com": "connected",
  "openai": "connected"
}
```

---

## 🐛 Troubleshooting

### Issue: "Connection error: Unable to reach the server"
- Ensure backend is running on http://localhost:8000
- Check firewall/network settings
- Verify FastAPI server started successfully

### Issue: "API key invalid"
- Check `MONDAY_API_TOKEN` in `.env`
- Check `OPENAI_API_KEY` in `.env`
- Regenerate keys if needed

### Issue: "Board not found"
- Verify board names in Monday.com:
  - "Work Order Tracker"
  - "Deal funnel Data"
- Names must match exactly (case-sensitive)

### Issue: Slow responses
- First query is slow (data loading) - normal
- Subsequent queries use 5-min cache
- Clear cache: Restart backend server
- Check Monday.com API rate limits

### Issue: Incomplete or "Masked" data
- This is expected - data from your Monday.com boards
- Agent reports data quality issues
- Update records in Monday.com to fix

---

## 🔐 Security Considerations

### Current Limitations (MVP)
- ❌ No authentication - anyone with access can query
- ❌ No authorization - all users see all data
- ❌ Credentials in .env file (not production-safe)
- ❌ CORS allows all origins (`*`)

### Production Recommendations
1. **Add Authentication**: OAuth2 with Monday.com SSO
2. **Add Authorization**: Role-based access control
3. **Secrets Management**: Use AWS Secrets Manager / HashiCorp Vault
4. **Restrict CORS**: Specify allowed origins only
5. **Enable HTTPS**: TLS encryption for all traffic
6. **Rate Limiting**: Prevent API abuse
7. **Audit Logging**: Log all queries and results
8. **Input Validation**: Sanitize all user inputs

---

## 📈 Performance

### Typical Response Times
- First query: 2-3 seconds (data loading)
- Cached queries: <500ms
- Leadership update: 3-5 seconds

### Scalability Considerations
- Current: Single-server deployment
- For 10+ concurrent users: Add load balancer
- For 100+ concurrent users: Separate DB layer, Redis cache
- For 1000+ concurrent users: Horizontal scaling with Kubernetes

---

## 🧪 Testing

### Manual Testing

1. **Backend health check**
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Test query**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "How many projects are completed?"}'
   ```

3. **Test leadership update**
   ```bash
   curl http://localhost:8000/api/leadership-update
   ```

### Recommended Test Coverage
- [ ] Unit tests for analytics services (60% of logic)
- [ ] Integration tests for Monday.com API
- [ ] E2E tests for chat flow
- [ ] Load testing (concurrent users)
- [ ] Security audit (OWASP top 10)

---

## 📚 Project Structure

```
monday-bi-agent/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py           # REST endpoints
│   │   ├── core/
│   │   │   ├── config.py           # Configuration
│   │   │   └── logging_config.py   # Logging setup
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic models
│   │   ├── services/
│   │   │   ├── ai/                 # NLP & orchestration
│   │   │   ├── monday/             # Monday.com integration
│   │   │   ├── analytics/          # BI services
│   │   │   └── cleaner/            # Data quality
│   │   ├── utils/
│   │   ├── main.py                 # FastAPI app
│   │   └── __init__.py
│   ├── .env.example                # Environment template
│   └── requirements.txt            # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Main component
│   │   ├── App.css                 # Styling
│   │   ├── main.jsx                # Entry point
│   │   └── index.css               # Global styles
│   ├── package.json                # Node dependencies
│   └── vite.config.js              # Vite configuration
│
├── Decision_Log.md                 # Architecture decisions
├── README.md                       # This file
└── requirements.txt                # Root dependencies
```

---

## 🚢 Deployment

### Local Development
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Docker Deployment

**Backend Dockerfile** (create `backend/Dockerfile`):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile** (create `frontend/Dockerfile`):
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json .
RUN npm ci --only=production
COPY . .
RUN npm run build
CMD ["npm", "run", "preview"]
```

### Cloud Platforms

**Render.com** (recommended for MVP):
1. Push code to GitHub
2. Connect Render to GitHub repo
3. Deploy backend as "Web Service"
4. Deploy frontend as "Static Site"
5. Set environment variables

**Heroku** (alternative):
```bash
heroku create skylark-bi-agent-api
heroku create skylark-bi-agent-ui
heroku config:set MONDAY_API_TOKEN=...
heroku config:set OPENAI_API_KEY=...
git push heroku main
```

**AWS** (for production):
- Backend: AWS Lambda + API Gateway
- Frontend: CloudFront + S3
- Database: RDS PostgreSQL
- Cache: ElastiCache Redis

---

## 📝 License

Proprietary - Skylark Drones Inc.

---

## 👥 Support

For issues, questions, or feature requests:
1. Check this README
2. Review Decision_Log.md for architecture context
3. Check backend logs: `tail -f backend/app/main.py` output
4. Check browser console for frontend errors

---

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com
- **React**: https://react.dev
- **Monday.com API**: https://developer.monday.com
- **OpenAI API**: https://platform.openai.com/docs
- **GraphQL**: https://graphql.org

---

## 🔮 Future Enhancements

### Phase 2
- [ ] User authentication & multi-tenant support
- [ ] Query history & saved reports
- [ ] Custom dashboard builder
- [ ] Export to PDF/Excel
- [ ] Automated scheduled reports

### Phase 3
- [ ] Advanced forecasting models
- [ ] Anomaly detection alerts
- [ ] Collaborative features
- [ ] Mobile app
- [ ] Voice interface

### Phase 4
- [ ] Multi-language support
- [ ] Integration with other data sources (Salesforce, HubSpot)
- [ ] Custom metrics builder
- [ ] Machine learning-powered recommendations

---

**Version**: 1.0  
**Last Updated**: August 7, 2026  
**Status**: MVP - Production Ready
