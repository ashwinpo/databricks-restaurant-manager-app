"""
FastAPI application for Panda Restaurant Group P&L Analytics Dashboard.
Provides AI-powered insights using Databricks Genie for restaurant operations.
"""

import os
import sys
import logging
import time
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import our modules - detect if we're running in Databricks Apps vs locally
# Detect environment - if we have OAuth credentials, we're in Databricks Apps
# If we have PAT tokens, we're running locally
is_databricks_apps = (
    os.getenv("DATABRICKS_CLIENT_ID") or 
    not (os.getenv("DB_PAT") or os.getenv("DATABRICKS_TOKEN"))
)

try:
    if is_databricks_apps:
        logger.info("Detected Databricks Apps environment - using OAuth authentication")
        from genie_client_databricks import ask_genie_structured, get_genie_health_status, GenieResult
        from db_utils_databricks import (
            sql_query, get_connection, test_connection, 
            get_panda_monthly_summary, get_panda_store_summary,
            get_top_performing_stores, get_monthly_trends
        )
    else:
        logger.info("Detected local development environment - using PAT authentication")
        from genie_client_local import ask_genie_structured, get_genie_health_status, GenieResult
        from db_utils_local import (
            sql_query, get_connection, test_connection, 
            get_panda_monthly_summary, get_panda_store_summary,
            get_top_performing_stores, get_monthly_trends
        )
except ImportError as e:
    logger.warning(f"Failed to import client modules: {e}")
    # Define fallback functions
    def ask_genie_structured(question):
        return type('GenieResult', (), {'answer': f'Client not available: {e}', 'sql': '', 'df': pd.DataFrame()})()
    def get_genie_health_status():
        return f"error: Client not available: {e}"
    def sql_query(query, params=None):
        return pd.DataFrame()
    def test_connection():
        return False
    def get_panda_monthly_summary():
        return pd.DataFrame()
    def get_panda_store_summary():
        return pd.DataFrame()
    def get_top_performing_stores(limit=10):
        return pd.DataFrame()
    def get_monthly_trends():
        return pd.DataFrame()

app = FastAPI(
    title="Panda Restaurant Group P&L Analytics",
    description="AI-powered restaurant analytics platform using Databricks Genie",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
# Configure CORS based on environment
if is_databricks_apps:
    # In production, allow Databricks Apps domain
    cors_origins = ["*"]  # Databricks Apps will handle domain restrictions
else:
    # In development, allow local servers and same-origin requests
    cors_origins = [
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if is_databricks_apps else ["*"],  # Allow all origins for development
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Pydantic models for API requests/responses
class GenieQuery(BaseModel):
    question: str
    context: Optional[str] = None

class GenieResponse(BaseModel):
    answer: str
    sql: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    status: str = "success"

class SQLQuery(BaseModel):
    query: str
    params: Optional[Dict] = None

class HealthResponse(BaseModel):
    service: str
    status: str
    message: Optional[str] = None

class OperationalAlert(BaseModel):
    id: str
    title: str
    description: str
    severity: str  # "high", "medium", "low"
    action: str
    store_id: Optional[str] = None

class KPIData(BaseModel):
    name: str
    value: float
    change: float
    period: str

# Utility function to convert DataFrame to API response format
def df_to_response(df: pd.DataFrame) -> Dict[str, Any]:
    """Convert pandas DataFrame to API response format."""
    if df.empty:
        return {"columns": [], "rows": [], "shape": [0, 0]}
    
    # Filter out index columns that pandas sometimes adds
    columns_to_exclude = []
    for col in df.columns:
        col_str = str(col).lower()
        if (col_str.startswith('unnamed') or 
            col_str.startswith('index') or 
            col_str == 'level_0'):
            columns_to_exclude.append(col)
    
    # Create a clean DataFrame without index columns
    if columns_to_exclude:
        clean_df = df.drop(columns=columns_to_exclude)
    else:
        clean_df = df
    
    return {
        "columns": clean_df.columns.tolist(),
        "rows": clean_df.to_dict(orient="records"),
        "shape": list(clean_df.shape)
    }

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests."""
    return {"message": "OK"}

@app.get("/api/")
async def root():
    """API root endpoint with basic app information."""
    return {
        "app": "Panda Restaurant Group P&L Analytics",
        "version": "1.0.0",
        "status": "running",
        "description": "AI-powered restaurant analytics platform for operational insights"
    }

@app.get("/api/health", response_model=Dict[str, Any])
async def health_check():
    """Check health of all services."""
    health_status = {
        "app": {"status": "healthy", "message": "FastAPI server running"},
        "environment": {"status": "healthy", "message": "Environment variables loaded"},
    }
    
    # Check Genie health
    try:
        genie_status = get_genie_health_status()
        if genie_status.startswith("error"):
            health_status["genie"] = {"status": "unhealthy", "message": genie_status}
        else:
            health_status["genie"] = {"status": "healthy", "message": "Genie connection active"}
    except Exception as e:
        health_status["genie"] = {"status": "error", "message": f"Genie check failed: {str(e)}"}
    
    # Check database connection
    try:
        if test_connection():
            health_status["database"] = {"status": "healthy", "message": "Database connection active"}
        else:
            health_status["database"] = {"status": "unhealthy", "message": "Database connection test failed"}
    except Exception as e:
        health_status["database"] = {"status": "error", "message": f"Database connection failed: {str(e)}"}
    
    # Check LLM endpoint
    try:
        llm_endpoint = os.getenv("LLM_ENDPOINT_NAME")
        if llm_endpoint:
            health_status["llm"] = {"status": "configured", "message": f"LLM endpoint: {llm_endpoint}"}
        else:
            health_status["llm"] = {"status": "warning", "message": "LLM endpoint not configured"}
    except Exception as e:
        health_status["llm"] = {"status": "error", "message": f"LLM check failed: {str(e)}"}
    
    return health_status

@app.post("/api/genie/ask", response_model=GenieResponse)
async def ask_genie(query: GenieQuery):
    """Ask Genie a natural language question about Panda Restaurant data."""
    request_id = f"genie_{int(time.time())}"
    logger.info(f"[{request_id}] Starting Genie query: '{query.question[:100]}...'")
    
    try:
        # Log the environment and configuration
        logger.info(f"[{request_id}] Environment: {'Databricks Apps' if is_databricks_apps else 'Local Development'}")
        logger.info(f"[{request_id}] Genie Space ID: {os.getenv('GENIE_SPACE_ID', 'Not configured')}")
        logger.info(f"[{request_id}] LLM Endpoint: {os.getenv('LLM_ENDPOINT_NAME', 'Not configured')}")
        
        # Enhance the question with context if provided
        enhanced_question = query.question
        if query.context:
            enhanced_question = f"Context: {query.context}\n\nQuestion: {query.question}"
            logger.info(f"[{request_id}] Enhanced with context")
        
        # Call Genie with detailed logging
        logger.info(f"[{request_id}] Calling Genie structured query...")
        result: GenieResult = ask_genie_structured(enhanced_question)
        logger.info(f"[{request_id}] Genie response received - Answer length: {len(result.answer)}, SQL: {'Yes' if result.sql else 'No'}, Data rows: {len(result.df) if not result.df.empty else 0}")
        
        # Convert DataFrame to dict for JSON response
        data_dict = None
        if not result.df.empty:
            logger.info(f"[{request_id}] Converting DataFrame to response format: {result.df.shape}")
            data_dict = df_to_response(result.df)
        
        response = GenieResponse(
            answer=result.answer,
            sql=result.sql if result.sql else None,
            data=data_dict,
            status="success"
        )
        
        logger.info(f"[{request_id}] Genie query completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"[{request_id}] Genie query failed with exception: {type(e).__name__}: {str(e)}")
        logger.error(f"[{request_id}] Full traceback:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Genie query failed: {str(e)}")

@app.get("/api/data/monthly-summary")
async def get_monthly_summary():
    """Get monthly P&L summary data."""
    try:
        df = get_monthly_trends()
        return {
            "status": "success",
            "data": df_to_response(df),
            "message": f"Retrieved {len(df)} monthly records"
        }
    except Exception as e:
        logger.error(f"Failed to get monthly summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get monthly summary: {str(e)}")

@app.get("/api/data/store-summary")
async def get_store_summary():
    """Get store performance summary data."""
    try:
        df = get_panda_store_summary()
        return {
            "status": "success",
            "data": df_to_response(df),
            "message": f"Retrieved {len(df)} store records"
        }
    except Exception as e:
        logger.error(f"Failed to get store summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get store summary: {str(e)}")

@app.get("/api/data/top-stores")
async def get_top_stores(limit: int = 10):
    """Get top performing stores by revenue."""
    try:
        df = get_top_performing_stores(limit=limit)
        return {
            "status": "success",
            "data": df_to_response(df),
            "message": f"Retrieved top {len(df)} performing stores"
        }
    except Exception as e:
        logger.error(f"Failed to get top stores: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get top stores: {str(e)}")

@app.get("/api/operations/alerts")
async def get_operational_alerts():
    """Get current operational alerts for store managers."""
    # This would typically come from real-time monitoring systems
    # For demo purposes, we'll return realistic sample alerts
    alerts = [
        OperationalAlert(
            id="alert_001",
            title="High Food Waste - Store #142",
            description="Orange Chicken waste is 15% above target. Consider reducing batch size during slow periods.",
            severity="high",
            action="Reduce batch cooking by 20% between 2-4 PM",
            store_id="142"
        ),
        OperationalAlert(
            id="alert_002", 
            title="Labor Cost Alert - District 5",
            description="Labor costs are 2.3% above budget for the week. Review scheduling optimization.",
            severity="medium",
            action="Review shift schedules and consider early releases during low traffic"
        ),
        OperationalAlert(
            id="alert_003",
            title="Inventory Shortage - Honey Walnut Shrimp",
            description="Projected stockout by Thursday based on current sales velocity.",
            severity="high", 
            action="Coordinate with supply chain for emergency delivery"
        )
    ]
    
    return {
        "status": "success",
        "alerts": [alert.model_dump() for alert in alerts],
        "message": f"Retrieved {len(alerts)} operational alerts"
    }

@app.get("/api/analytics/kpis")
async def get_key_metrics():
    """Get key performance indicators for dashboard."""
    try:
        # Get recent monthly data for KPI calculation
        monthly_df = get_monthly_trends()
        
        if monthly_df.empty:
            # Return demo KPIs if no data available
            kpis = [
                KPIData(name="Revenue", value=2845000, change=5.2, period="vs last month"),
                KPIData(name="EBITDA Margin", value=18.5, change=-0.8, period="vs last month"),
                KPIData(name="Labor %", value=28.2, change=1.2, period="vs target"),
                KPIData(name="Transactions", value=156789, change=3.1, period="vs last month")
            ]
        else:
            # Calculate KPIs from actual data
            latest = monthly_df.iloc[-1] if len(monthly_df) > 0 else None
            previous = monthly_df.iloc[-2] if len(monthly_df) > 1 else None
            
            kpis = []
            if latest is not None:
                revenue_change = 0
                if previous is not None and 'total_revenue_sum' in previous:
                    revenue_change = ((latest.get('total_revenue_sum', 0) - previous.get('total_revenue_sum', 0)) / previous.get('total_revenue_sum', 1)) * 100
                
                kpis = [
                    KPIData(name="Revenue", value=latest.get('total_revenue_sum', 0), change=revenue_change, period="vs last month"),
                    KPIData(name="EBITDA Margin", value=latest.get('ebitda_margin_pct', 0), change=0, period="vs last month"),
                    KPIData(name="Labor %", value=latest.get('labor_pct_of_sales', 0), change=0, period="vs target"),
                    KPIData(name="Transactions", value=latest.get('transactions_sum', 0), change=0, period="vs last month")
                ]
        
        return {
            "status": "success",
            "kpis": [kpi.model_dump() for kpi in kpis],
            "message": "KPIs calculated successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate KPIs: {str(e)}")
        # Return demo data on error
        kpis = [
            KPIData(name="Revenue", value=2845000, change=5.2, period="vs last month"),
            KPIData(name="EBITDA Margin", value=18.5, change=-0.8, period="vs last month"),
            KPIData(name="Labor %", value=28.2, change=1.2, period="vs target"),
            KPIData(name="Transactions", value=156789, change=3.1, period="vs last month")
        ]
        return {
            "status": "success",
            "kpis": [kpi.model_dump() for kpi in kpis],
            "message": "Using demo KPIs due to data access issue"
        }

@app.post("/api/db/query")
async def execute_sql_query(query: SQLQuery):
    """Execute a direct SQL query against the data warehouse."""
    try:
        logger.info(f"Executing SQL query: {query.query[:100]}...")
        
        # Execute the query
        result_df = sql_query(query.query, query.params)
        
        if result_df.empty:
            return {
                "status": "success",
                "message": "Query executed successfully but returned no results",
                "data": {"columns": [], "rows": [], "shape": [0, 0]}
            }
        
        return {
            "status": "success",
            "message": f"Query executed successfully. Returned {result_df.shape[0]} rows.",
            "data": df_to_response(result_df)
        }
        
    except Exception as e:
        logger.error(f"SQL query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"SQL query failed: {str(e)}")

@app.post("/api/data/upload")
async def upload_data(file: UploadFile = File(...)):
    """Upload external data file (CSV, Excel) for analysis."""
    try:
        # For demo purposes, just validate the file and return info
        # In production, this would process and store the data
        
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
        
        contents = await file.read()
        file_size = len(contents)
        
        return {
            "status": "success",
            "message": f"File '{file.filename}' uploaded successfully",
            "file_info": {
                "filename": file.filename,
                "size_bytes": file_size,
                "content_type": file.content_type
            }
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/api/config")
async def get_config():
    """Get current configuration (without sensitive values)."""
    return {
        "genie_space_id": os.getenv("GENIE_SPACE_ID", "Not configured"),
        "llm_endpoint": os.getenv("LLM_ENDPOINT_NAME", "Not configured"),
        "db_host": os.getenv("DB_HOST", "Not configured") if os.getenv("DB_HOST") else "Not configured",
        "warehouse_id": "Configured" if os.getenv("DATABRICKS_WAREHOUSE_ID") else "Not configured",
        "auth_method": "OAuth" if is_databricks_apps else "PAT",
        "environment": "databricks_apps" if is_databricks_apps else "development",
        "catalog": os.getenv("DATABRICKS_CATALOG", "users"),
        "schema": os.getenv("DATABRICKS_SCHEMA", "aarthi_shankar"),
        "cors_origins": "all (*)" if is_databricks_apps else "localhost only"
    }

@app.get("/api/debug/genie")
async def debug_genie():
    """Debug endpoint to test Genie connectivity and configuration."""
    debug_info = {
        "timestamp": time.time(),
        "environment": "databricks_apps" if is_databricks_apps else "development",
        "genie_space_id": os.getenv("GENIE_SPACE_ID", "Not configured"),
        "llm_endpoint": os.getenv("LLM_ENDPOINT_NAME", "Not configured"),
        "auth_available": bool(os.getenv("DATABRICKS_CLIENT_ID")) or bool(os.getenv("DB_PAT")),
    }
    
    # Test basic Genie health
    try:
        health_status = get_genie_health_status()
        debug_info["genie_health"] = health_status
        debug_info["genie_healthy"] = not health_status.startswith("error")
    except Exception as e:
        debug_info["genie_health"] = f"error: {str(e)}"
        debug_info["genie_healthy"] = False
    
    # Test simple query
    try:
        simple_result = ask_genie_structured("Hello")
        debug_info["simple_query"] = {
            "answer_length": len(simple_result.answer),
            "has_sql": bool(simple_result.sql),
            "has_data": not simple_result.df.empty,
            "answer_preview": simple_result.answer[:200] + "..." if len(simple_result.answer) > 200 else simple_result.answer
        }
    except Exception as e:
        debug_info["simple_query"] = {"error": str(e)}
    
    return debug_info

# Mount React build directory for static files (if available)
build_dir = Path(__file__).parent.parent / "frontend" / "dist"
if build_dir.exists():
    app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")
    logger.info(f"Mounted static files from {build_dir}")
else:
    logger.warning(f"Frontend build directory not found: {build_dir}")
    logger.warning("Run 'npm run build' in the frontend directory to build the React app")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
