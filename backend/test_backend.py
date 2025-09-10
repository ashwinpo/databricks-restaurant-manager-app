#!/usr/bin/env python3
"""
Test script for Panda Restaurant Group P&L Analytics Backend
Demonstrates key functionality and API endpoints.
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Test an API endpoint and return the result."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return {"success": True, "data": response.json(), "status_code": response.status_code}
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e), "status_code": getattr(e.response, 'status_code', 0)}

def main():
    """Run comprehensive backend tests."""
    print("🐼 Panda Restaurant Group P&L Analytics Backend Test")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Health Check")
    result = test_endpoint("/api/health")
    if result["success"]:
        print("✅ Backend is healthy")
        health_data = result["data"]
        for service, status in health_data.items():
            status_icon = "✅" if status["status"] in ["healthy", "configured"] else "⚠️"
            print(f"   {status_icon} {service}: {status['message']}")
    else:
        print(f"❌ Health check failed: {result['error']}")
        return
    
    # Test 2: Basic Info
    print("\n2. API Information")
    result = test_endpoint("/api/")
    if result["success"]:
        info = result["data"]
        print(f"✅ App: {info['app']}")
        print(f"   Version: {info['version']}")
        print(f"   Status: {info['status']}")
    else:
        print(f"❌ API info failed: {result['error']}")
    
    # Test 3: Database Direct Query
    print("\n3. Database Direct Query")
    query_data = {
        "query": "SELECT store_id, store_name, total_revenue FROM users.aarthi_shankar.panda_store_summary ORDER BY total_revenue DESC LIMIT 3"
    }
    result = test_endpoint("/api/db/query", "POST", query_data)
    if result["success"]:
        data = result["data"]["data"]
        print(f"✅ Query successful: {len(data['rows'])} rows returned")
        print("   Top 3 stores by revenue:")
        for row in data["rows"]:
            print(f"   - {row['store_name']}: ${row['total_revenue']:,.2f}")
    else:
        print(f"❌ Database query failed: {result['error']}")
    
    # Test 4: Operational Alerts
    print("\n4. Operational Alerts")
    result = test_endpoint("/api/operations/alerts")
    if result["success"]:
        alerts = result["data"]["alerts"]
        print(f"✅ Retrieved {len(alerts)} operational alerts")
        for alert in alerts[:2]:  # Show first 2 alerts
            print(f"   - {alert['title']} ({alert['severity']})")
            print(f"     Action: {alert['action']}")
    else:
        print(f"❌ Alerts failed: {result['error']}")
    
    # Test 5: KPI Metrics
    print("\n5. KPI Metrics")
    result = test_endpoint("/api/analytics/kpis")
    if result["success"]:
        kpis = result["data"]["kpis"]
        print(f"✅ Retrieved {len(kpis)} KPIs")
        for kpi in kpis:
            change_icon = "📈" if kpi["change"] > 0 else "📉" if kpi["change"] < 0 else "➡️"
            print(f"   {change_icon} {kpi['name']}: {kpi['value']:,.1f} ({kpi['change']:+.1f}% {kpi['period']})")
    else:
        print(f"❌ KPIs failed: {result['error']}")
    
    # Test 6: Genie Query (might fail due to domain mismatch)
    print("\n6. Genie AI Query")
    genie_data = {
        "question": "Show me the top 3 stores by revenue",
        "context": "I'm a restaurant manager reviewing store performance"
    }
    result = test_endpoint("/api/genie/ask", "POST", genie_data)
    if result["success"]:
        genie_result = result["data"]
        print("✅ Genie query successful")
        print(f"   Answer: {genie_result['answer'][:100]}...")
        if genie_result.get("data") and genie_result["data"]["rows"]:
            print(f"   Data returned: {len(genie_result['data']['rows'])} rows")
    else:
        print(f"❌ Genie query failed: {result['error']}")
    
    # Test 7: Configuration
    print("\n7. Configuration Check")
    result = test_endpoint("/api/config")
    if result["success"]:
        config = result["data"]
        print("✅ Configuration loaded")
        print(f"   Genie Space: {config.get('genie_space_id', 'Not configured')}")
        print(f"   LLM Endpoint: {config.get('llm_endpoint', 'Not configured')}")
        print(f"   Auth Method: {config.get('auth_method', 'Unknown')}")
    else:
        print(f"❌ Config check failed: {result['error']}")
    
    print("\n" + "=" * 60)
    print("🎉 Backend test completed!")
    print("\nThe Panda Restaurant Group P&L Analytics backend is ready for:")
    print("• Real-time operational alerts and insights")
    print("• Direct SQL queries to Databricks tables") 
    print("• KPI dashboard data")
    print("• AI-powered analytics via Genie (when configured for restaurant domain)")
    print("• Integration with the React frontend")

if __name__ == "__main__":
    main()
