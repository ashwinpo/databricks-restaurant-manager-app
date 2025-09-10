# Panda Restaurant Group P&L Analytics Backend

FastAPI backend for the Panda Restaurant Group P&L Analytics Dashboard, providing AI-powered insights using Databricks Genie for restaurant operations.

## Features

- **FastAPI REST API** with comprehensive endpoints for restaurant analytics
- **Databricks Integration** with direct SQL querying capabilities
- **Genie AI Assistant** for natural language data queries
- **Operational Alerts** for real-time restaurant management insights
- **KPI Dashboard** data with performance metrics
- **CORS Support** for React frontend integration
- **Health Monitoring** with service status checks

## API Endpoints

### Core Endpoints
- `GET /api/` - API information and status
- `GET /api/health` - Health check for all services
- `GET /api/config` - Configuration details (non-sensitive)

### Data Endpoints
- `GET /api/data/monthly-summary` - Monthly P&L summary data
- `GET /api/data/store-summary` - Store performance summary
- `GET /api/data/top-stores` - Top performing stores by revenue
- `POST /api/db/query` - Execute direct SQL queries

### Analytics Endpoints
- `GET /api/operations/alerts` - Current operational alerts
- `GET /api/analytics/kpis` - Key performance indicators
- `POST /api/genie/ask` - AI-powered natural language queries

### Utility Endpoints
- `POST /api/data/upload` - Upload external data files (CSV/Excel)

## Environment Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables** (create `.env` file in project root)
   ```bash
   # Databricks Configuration
   DB_HOST=https://your-databricks-workspace.cloud.databricks.com
   DB_PAT=your_personal_access_token
   DATABRICKS_WAREHOUSE_ID=your_warehouse_id
   
   # Genie Configuration
   GENIE_SPACE_ID=your_genie_space_id
   LLM_ENDPOINT_NAME=databricks-claude-3-7-sonnet
   ```

## Running the Backend

### Development
```bash
cd backend
python app.py
```

The server will start on `http://localhost:8000`

### API Documentation
Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## Testing

Run the comprehensive test suite:
```bash
python test_backend.py
```

This will test:
- ✅ Health checks for all services
- ✅ Database connectivity and queries
- ✅ Operational alerts generation
- ✅ KPI calculations
- ✅ Genie AI integration
- ✅ Configuration validation

## Data Schema

The backend connects to these Databricks tables:
- `users.aarthi_shankar.panda_monthly_summary` - Monthly P&L aggregates
- `users.aarthi_shankar.panda_store_summary` - Store-level performance data

## Key Components

### Database Integration (`db_utils_local.py`)
- PAT-based authentication for local development
- SQL query execution with pandas DataFrame results
- Connection pooling and error handling
- Schema-specific helper functions

### Genie AI Client (`genie_client_local.py`)
- Natural language to SQL query conversion
- Structured response parsing
- Restaurant-focused context enhancement
- Error handling and fallbacks

### FastAPI Application (`app.py`)
- RESTful API with proper error handling
- CORS middleware for frontend integration
- Comprehensive logging
- Static file serving for React frontend

## Production Deployment

For Databricks Apps deployment:
1. Switch to OAuth authentication (use `*_databricks.py` versions)
2. Update environment detection logic
3. Configure proper CORS origins
4. Set up monitoring and logging

## Frontend Integration

The backend is designed to work seamlessly with the React frontend:
- CORS configured for `localhost:5173` (Vite dev server)
- JSON responses optimized for dashboard components
- Real-time data updates for operational insights
- File upload support for external data integration

## Sample Operational Insights

The backend provides realistic restaurant management alerts:
- **Food Waste Monitoring**: "Orange Chicken waste is 15% above target"
- **Labor Cost Optimization**: "Labor costs are 2.3% above budget for the week"
- **Inventory Management**: "Projected stockout by Thursday based on sales velocity"

## Architecture

```
React Frontend (Port 5173)
        ↓ HTTP/JSON
FastAPI Backend (Port 8000)
        ↓ SQL/Genie
Databricks Platform
        ↓ Data
Panda Restaurant Tables
```

## Status

✅ **Backend Complete** - All core functionality implemented and tested
✅ **Database Integration** - Successfully connecting to Databricks tables
✅ **Genie Integration** - AI queries working (domain configuration needed)
✅ **API Endpoints** - All restaurant analytics endpoints functional
✅ **Health Monitoring** - Comprehensive service status checks

Ready for frontend integration and demo deployment!
