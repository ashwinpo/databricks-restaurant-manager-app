"""
Local database utilities for Panda Restaurant Group demo.
Uses PAT authentication for local development.
"""

import os
import pandas as pd
from typing import Dict, Optional
from databricks import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DEFAULT_CATALOG = "users"
DEFAULT_SCHEMA = "ashwin_pothukuchi"  # Updated for your schema

def get_catalog() -> str:
    """Get the catalog name from environment or use default."""
    return os.getenv('DATABRICKS_CATALOG', DEFAULT_CATALOG)

def get_schema() -> str:
    """Get the schema name from environment or use default.""" 
    return os.getenv('DATABRICKS_SCHEMA', DEFAULT_SCHEMA)

def get_full_table_name(table_name: str) -> str:
    """Get the fully qualified table name."""
    return f"{get_catalog()}.{get_schema()}.{table_name}"

def get_panda_table(table_key: str) -> str:
    """Get configurable Panda table name from environment variables."""
    table_mapping = {
        'pnl': 'PANDA_PNL_TABLE',
        'store': 'PANDA_STORE_TABLE', 
        'period': 'PANDA_PERIOD_TABLE',
        'monthly_summary': 'PANDA_MONTHLY_SUMMARY_VIEW',
        'store_summary': 'PANDA_STORE_SUMMARY_VIEW'
    }
    
    env_var = table_mapping.get(table_key)
    if env_var:
        return os.getenv(env_var, get_full_table_name(table_key))
    else:
        return get_full_table_name(table_key)

def get_connection():
    """Get a Databricks SQL connection using environment variables with PAT auth."""
    server_hostname = os.getenv("DB_HOST")
    access_token = os.getenv("DB_PAT")  
    warehouse_id = os.getenv("DATABRICKS_WAREHOUSE_ID")
    
    if not server_hostname:
        raise ValueError("DB_HOST environment variable not set")
    if not access_token:
        raise ValueError("DB_PAT environment variable not set") 
    if not warehouse_id:
        raise ValueError("DATABRICKS_WAREHOUSE_ID environment variable not set")
    
    # Remove https:// prefix if present
    if server_hostname.startswith("https://"):
        server_hostname = server_hostname[8:]
    
    return sql.connect(
        server_hostname=server_hostname,
        http_path=f"/sql/1.0/warehouses/{warehouse_id}",
        access_token=access_token
    )

def sql_query(query: str, params: Optional[Dict] = None) -> pd.DataFrame:
    """Execute a SQL query and return results as pandas DataFrame."""
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Fetch results and convert to pandas
                result = cursor.fetchall_arrow().to_pandas()
                return result
                
    except Exception as e:
        print(f"Database query failed: {str(e)}")
        return pd.DataFrame()

def test_connection() -> bool:
    """Test the database connection with a simple query."""
    try:
        result = sql_query("SELECT 1 as test, current_timestamp() as ts")
        return not result.empty
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False

def get_panda_monthly_summary() -> pd.DataFrame:
    """Get data from panda_monthly_summary table with the new schema."""
    try:
        table_name = get_panda_table('monthly_summary')
        
        query = f"""
        SELECT 
            periodid,
            month_year,
            store_count,
            total_revenue_sum,
            total_revenue_plan,
            total_cogs_actual,
            total_labor_actual,
            total_opex_actual,
            net_income_actual,
            net_income_plan,
            cogs_pct_of_sales,
            labor_pct_of_sales,
            gross_margin_pct,
            ebitda_margin_pct
        FROM {table_name} 
        ORDER BY FiscalYear DESC, FiscalPeriod DESC 
        LIMIT 100
        """
        
        return sql_query(query)
    except Exception as e:
        print(f"Failed to get monthly summary: {str(e)}")
        return pd.DataFrame()

def get_panda_store_summary() -> pd.DataFrame:
    """Get data from panda_store_summary table."""
    try:
        table_name = get_panda_table('store_summary')
        query = f"""
        SELECT 
            storenumber,
            store_name,
            state,
            region,
            square_feet,
            store_type,
            periods_count,
            total_revenue,
            avg_period_revenue,
            total_cogs,
            total_labor,
            total_opex,
            net_income,
            labor_pct_of_sales,
            ebitda_margin_pct,
            sales_per_sq_ft
        FROM {table_name} 
        ORDER BY total_revenue DESC
        LIMIT 100
        """
        return sql_query(query)
    except Exception as e:
        print(f"Failed to get store summary: {str(e)}")
        return pd.DataFrame()

def get_top_performing_stores(limit: int = 10) -> pd.DataFrame:
    """Get top performing stores by revenue."""
    try:
        table_name = get_panda_table('store_summary')
        query = f"""
        SELECT 
            storenumber, 
            store_name, 
            state, 
            region,
            total_revenue, 
            ebitda_margin_pct, 
            labor_pct_of_sales, 
            sales_per_sq_ft
        FROM {table_name}
        ORDER BY total_revenue DESC
        LIMIT {limit}
        """
        return sql_query(query)
    except Exception as e:
        print(f"Failed to get top performing stores: {str(e)}")
        return pd.DataFrame()

def get_monthly_trends() -> pd.DataFrame:
    """Get monthly performance trends with the new schema."""
    try:
        table_name = get_panda_table('monthly_summary')
        
        query = f"""
        SELECT 
            periodid,
            month_year,
            store_count,
            total_revenue_sum,
            total_revenue_plan,
            net_income_actual,
            net_income_plan,
            cogs_pct_of_sales,
            labor_pct_of_sales,
            gross_margin_pct,
            ebitda_margin_pct
        FROM {table_name}
        ORDER BY FiscalYear, FiscalPeriod
        """
        
        return sql_query(query)
    except Exception as e:
        print(f"Failed to get monthly trends: {str(e)}")
        return pd.DataFrame()

def get_restaurant_performance_summary() -> Dict[str, pd.DataFrame]:
    """Get comprehensive restaurant performance data for dashboard."""
    try:
        return {
            'monthly_trends': get_monthly_trends(),
            'store_summary': get_panda_store_summary(),
            'top_stores': get_top_performing_stores(10)
        }
    except Exception as e:
        print(f"Failed to get performance summary: {str(e)}")
        return {
            'monthly_trends': pd.DataFrame(),
            'store_summary': pd.DataFrame(), 
            'top_stores': pd.DataFrame()
        }

def get_table_schema(table_name: str) -> pd.DataFrame:
    """Get schema information for a specific table."""
    try:
        full_table_name = get_full_table_name(table_name)
        query = f"DESCRIBE {full_table_name}"
        return sql_query(query)
    except Exception as e:
        print(f"Failed to get table schema: {str(e)}")
        return pd.DataFrame()

def list_available_schemas() -> pd.DataFrame:
    """List available schemas in the catalog."""
    try:
        catalog = get_catalog()
        query = f"SHOW SCHEMAS IN {catalog}"
        return sql_query(query)
    except Exception as e:
        print(f"Failed to list schemas: {str(e)}")
        return pd.DataFrame()

def list_tables(schema_name: Optional[str] = None) -> pd.DataFrame:
    """List tables in the specified schema."""
    try:
        if schema_name is None:
            schema_name = get_schema()
        catalog = get_catalog() 
        query = f"SHOW TABLES IN {catalog}.{schema_name}"
        return sql_query(query)
    except Exception as e:
        print(f"Failed to list tables: {str(e)}")
        return pd.DataFrame()
