#!/usr/bin/env python3
"""
Deployment Diagnostic Script for Panda Restaurant Group P&L Analytics
Helps troubleshoot issues in deployed Databricks Apps environment.
"""

import os
import sys
import json
import traceback
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def safe_get_env(key, default="Not Set"):
    """Safely get environment variable with fallback."""
    try:
        value = os.getenv(key, default)
        return value if value != default else default
    except Exception as e:
        return f"Error: {e}"

def test_imports():
    """Test if required modules can be imported."""
    print_section("MODULE IMPORTS")
    
    modules_to_test = [
        "fastapi",
        "uvicorn", 
        "pandas",
        "databricks_langchain",
        "databricks.sql",
        "databricks.sdk"
    ]
    
    results = {}
    for module in modules_to_test:
        try:
            __import__(module)
            results[module] = "✅ OK"
        except ImportError as e:
            results[module] = f"❌ FAILED: {e}"
        except Exception as e:
            results[module] = f"⚠️  ERROR: {e}"
    
    for module, status in results.items():
        print(f"{module:25} {status}")
    
    return all("OK" in status for status in results.values())

def test_environment():
    """Test environment variables and configuration."""
    print_section("ENVIRONMENT CONFIGURATION")
    
    env_vars = [
        "GENIE_SPACE_ID",
        "LLM_ENDPOINT_NAME", 
        "DATABRICKS_WAREHOUSE_ID",
        "DATABRICKS_CATALOG",
        "DATABRICKS_SCHEMA",
        "DB_HOST",
        "DB_PAT",
        "DATABRICKS_CLIENT_ID",
        "DATABRICKS_TOKEN"
    ]
    
    for var in env_vars:
        value = safe_get_env(var)
        # Mask sensitive values
        if var in ["DB_PAT", "DATABRICKS_TOKEN"] and value != "Not Set":
            display_value = value[:8] + "..." if len(value) > 8 else "***"
        else:
            display_value = value
        
        status = "✅" if value != "Not Set" else "⚠️"
        print(f"{status} {var:25} {display_value}")

def test_databricks_auth():
    """Test Databricks authentication methods."""
    print_section("DATABRICKS AUTHENTICATION")
    
    try:
        from databricks.sdk.core import Config
        
        # Test if we can create a config
        cfg = Config()
        print(f"✅ Config created successfully")
        print(f"   Host: {getattr(cfg, 'host', 'Not available')}")
        print(f"   Auth type: {getattr(cfg, 'auth_type', 'Not available')}")
        
        # Check available auth methods
        has_pat = bool(os.getenv("DB_PAT") or os.getenv("DATABRICKS_TOKEN"))
        has_oauth = bool(os.getenv("DATABRICKS_CLIENT_ID"))
        
        print(f"   PAT available: {'✅' if has_pat else '❌'}")
        print(f"   OAuth available: {'✅' if has_oauth else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Databricks config failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_genie_connection():
    """Test Genie connectivity."""
    print_section("GENIE CONNECTION TEST")
    
    try:
        # Import based on environment
        is_databricks_apps = (
            os.getenv("DATABRICKS_CLIENT_ID") or 
            not (os.getenv("DB_PAT") or os.getenv("DATABRICKS_TOKEN"))
        )
        
        print(f"Environment detected: {'Databricks Apps' if is_databricks_apps else 'Local Development'}")
        
        if is_databricks_apps:
            from genie_client_databricks import get_genie_health_status, ask_genie_structured
        else:
            from genie_client_local import get_genie_health_status, ask_genie_structured
        
        # Test health status
        print("Testing Genie health...")
        health = get_genie_health_status()
        print(f"Health status: {health}")
        
        # Test simple query
        print("Testing simple Genie query...")
        result = ask_genie_structured("Hello")
        print(f"✅ Query successful")
        print(f"   Answer length: {len(result.answer)}")
        print(f"   Has SQL: {bool(result.sql)}")
        print(f"   Has data: {not result.df.empty}")
        print(f"   Answer preview: {result.answer[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Genie test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_database_connection():
    """Test database connectivity."""
    print_section("DATABASE CONNECTION TEST")
    
    try:
        # Import based on environment
        is_databricks_apps = (
            os.getenv("DATABRICKS_CLIENT_ID") or 
            not (os.getenv("DB_PAT") or os.getenv("DATABRICKS_TOKEN"))
        )
        
        if is_databricks_apps:
            from db_utils_databricks import test_connection, sql_query
        else:
            from db_utils_local import test_connection, sql_query
        
        # Test basic connection
        print("Testing database connection...")
        if test_connection():
            print("✅ Database connection successful")
            
            # Test simple query
            print("Testing simple SQL query...")
            result = sql_query("SELECT 1 as test, current_timestamp() as ts")
            if not result.empty:
                print(f"✅ SQL query successful: {result.shape[0]} rows returned")
            else:
                print("⚠️  SQL query returned no results")
            
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def generate_report():
    """Generate comprehensive diagnostic report."""
    print_section("PANDA RESTAURANT GROUP - DEPLOYMENT DIAGNOSTICS")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Run all tests
    results = {
        "imports": test_imports(),
        "environment": True,  # Environment test doesn't return boolean
        "auth": test_databricks_auth(),
        "genie": test_genie_connection(),
        "database": test_database_connection()
    }
    
    test_environment()  # This prints but doesn't return boolean
    
    print_section("DIAGNOSTIC SUMMARY")
    
    all_passed = True
    for test_name, passed in results.items():
        if test_name == "environment":
            continue  # Skip environment as it's informational
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.upper():15} {status}")
        if not passed:
            all_passed = False
    
    print(f"\nOverall Status: {'✅ ALL SYSTEMS GO' if all_passed else '❌ ISSUES DETECTED'}")
    
    if not all_passed:
        print("\n🔧 TROUBLESHOOTING TIPS:")
        if not results.get("imports"):
            print("- Install missing Python packages: pip install -r requirements.txt")
        if not results.get("auth"):
            print("- Check Databricks authentication configuration")
            print("- Verify DATABRICKS_WAREHOUSE_ID is set correctly")
        if not results.get("genie"):
            print("- Check GENIE_SPACE_ID and LLM_ENDPOINT_NAME configuration")
            print("- Verify Genie space permissions and accessibility")
        if not results.get("database"):
            print("- Check SQL warehouse status and permissions")
            print("- Verify network connectivity to Databricks")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = generate_report()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ DIAGNOSTIC SCRIPT FAILED: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(2)
