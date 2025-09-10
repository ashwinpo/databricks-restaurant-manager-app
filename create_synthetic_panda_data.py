#!/usr/bin/env python3
"""
Databricks Synthetic Data Generator for Panda Restaurant Group P&L Data
========================================================================

This script creates synthetic versions of Panda Restaurant Group's financial data
for development and demo purposes. It generates realistic P&L data based on the
schema provided in PandaSchemas.

Tables created:
- users.ashwin_pothukuchi.pandapnl: Main P&L data (based on Panda_pandapnl_empty.csv)
- users.ashwin_pothukuchi.dimperiod: Period dimension table
- users.ashwin_pothukuchi.storedim: Store dimension table
- users.ashwin_pothukuchi.orgchart: Organization chart/hierarchy

Run this in a Databricks notebook or as a Python script in Databricks.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def create_period_dimension() -> pd.DataFrame:
    """Create period dimension table with fiscal periods for 2022-2025."""
    periods = []
    
    # Generate periods for 2022-2025 (4 years)
    for year in range(2022, 2026):
        for period in range(1, 14):  # 13 periods per year (4-week cycles)
            period_id = f"{year}{period:02d}"
            
            # Calculate approximate dates (4-week periods)
            start_date = datetime(year, 1, 1) + timedelta(weeks=(period-1)*4)
            end_date = start_date + timedelta(weeks=4, days=-1)
            
            # Quarter mapping
            quarter = min(4, ((period - 1) // 3) + 1)
            
            periods.append({
                'PeriodID': period_id,
                'PeriodIDSeq': len(periods) + 1,
                'FiscalPeriod': period,
                'FiscalPeriodName': f"{year} - P{period}",
                'FiscalPeriodName2': f"P{period} '{str(year)[-2:]}",
                'FiscalPeriodKey': int(f"{year}13{period:02d}"),
                'FiscalPeriodStartDate': start_date.strftime('%Y-%m-%d'),
                'FiscalPeriodEndDate': end_date.strftime('%Y-%m-%d'),
                'QuarterID': f"{year}{quarter:02d}",
                'FiscalQuarter': quarter,
                'FiscalQuarterName': f"{year} - Q{quarter}",
                'FiscalYear': year,
                'FiscalYearStartDate': f"{year}-01-01",
                'FiscalYearEndDate': f"{year}-12-31"
            })
    
    return pd.DataFrame(periods)

def create_store_dimension() -> pd.DataFrame:
    """Create store dimension with realistic Panda Express locations."""
    
    # Realistic store locations and characteristics
    store_data = [
        # California stores
        {'store': 1001, 'name': 'Los Angeles - Downtown', 'state': 'CA', 'region': 'West', 'sq_ft': 2200, 'mall': True},
        {'store': 1002, 'name': 'San Francisco - Union Square', 'state': 'CA', 'region': 'West', 'sq_ft': 1800, 'mall': True},
        {'store': 1003, 'name': 'San Diego - Mission Valley', 'state': 'CA', 'region': 'West', 'sq_ft': 2000, 'mall': True},
        {'store': 1004, 'name': 'Sacramento - Arden Fair', 'state': 'CA', 'region': 'West', 'sq_ft': 2100, 'mall': True},
        {'store': 1005, 'name': 'Orange County - Irvine', 'state': 'CA', 'region': 'West', 'sq_ft': 1900, 'mall': False},
        
        # Texas stores
        {'store': 2001, 'name': 'Houston - Galleria', 'state': 'TX', 'region': 'South', 'sq_ft': 2300, 'mall': True},
        {'store': 2002, 'name': 'Dallas - NorthPark', 'state': 'TX', 'region': 'South', 'sq_ft': 2000, 'mall': True},
        {'store': 2003, 'name': 'Austin - Domain', 'state': 'TX', 'region': 'South', 'sq_ft': 1850, 'mall': False},
        {'store': 2004, 'name': 'San Antonio - River Walk', 'state': 'TX', 'region': 'South', 'sq_ft': 2150, 'mall': False},
        
        # New York stores
        {'store': 3001, 'name': 'New York - Times Square', 'state': 'NY', 'region': 'Northeast', 'sq_ft': 1600, 'mall': False},
        {'store': 3002, 'name': 'New York - Herald Square', 'state': 'NY', 'region': 'Northeast', 'sq_ft': 1700, 'mall': True},
        {'store': 3003, 'name': 'Brooklyn - Atlantic Terminal', 'state': 'NY', 'region': 'Northeast', 'sq_ft': 1900, 'mall': True},
        
        # Florida stores
        {'store': 4001, 'name': 'Miami - Aventura Mall', 'state': 'FL', 'region': 'Southeast', 'sq_ft': 2200, 'mall': True},
        {'store': 4002, 'name': 'Orlando - Disney Springs', 'state': 'FL', 'region': 'Southeast', 'sq_ft': 2400, 'mall': False},
        {'store': 4003, 'name': 'Tampa - International Plaza', 'state': 'FL', 'region': 'Southeast', 'sq_ft': 2000, 'mall': True},
        
        # Illinois stores
        {'store': 5001, 'name': 'Chicago - Magnificent Mile', 'state': 'IL', 'region': 'Midwest', 'sq_ft': 1800, 'mall': False},
        {'store': 5002, 'name': 'Chicago - Woodfield Mall', 'state': 'IL', 'region': 'Midwest', 'sq_ft': 2100, 'mall': True},
        
        # Other states
        {'store': 6001, 'name': 'Las Vegas - Forum Shops', 'state': 'NV', 'region': 'West', 'sq_ft': 2300, 'mall': True},
        {'store': 6002, 'name': 'Phoenix - Scottsdale Fashion', 'state': 'AZ', 'region': 'West', 'sq_ft': 2000, 'mall': True},
        {'store': 6003, 'name': 'Denver - Cherry Creek', 'state': 'CO', 'region': 'West', 'sq_ft': 1950, 'mall': True},
    ]
    
    stores = []
    for store in store_data:
        stores.append({
            'storenumber': store['store'],
            'store_name': store['name'],
            'state': store['state'],
            'region': store['region'],
            'square_feet': store['sq_ft'],
            'store_type': 'Mall' if store['mall'] else 'Standalone',
            'open_date': f"{random.randint(2010, 2020)}-{random.randint(1, 12):02d}-01",
            'active': True
        })
    
    return pd.DataFrame(stores)

def create_line_items() -> List[Dict[str, Any]]:
    """Create realistic P&L line items for Panda Express."""
    
    line_items = [
        # Revenue items
        {'Type': 'Revenue', 'SubType': 'Food Sales', 'LineItem': 'Entree Sales', 'typical_pct': 65.0, 'variance': 5.0},
        {'Type': 'Revenue', 'SubType': 'Food Sales', 'LineItem': 'Side Sales', 'typical_pct': 25.0, 'variance': 3.0},
        {'Type': 'Revenue', 'SubType': 'Beverage Sales', 'LineItem': 'Drink Sales', 'typical_pct': 8.0, 'variance': 2.0},
        {'Type': 'Revenue', 'SubType': 'Other', 'LineItem': 'Catering Sales', 'typical_pct': 2.0, 'variance': 1.0},
        
        # Cost of Goods Sold
        {'Type': 'COGS', 'SubType': 'Food Costs', 'LineItem': 'Protein Costs', 'typical_pct': 18.0, 'variance': 2.0},
        {'Type': 'COGS', 'SubType': 'Food Costs', 'LineItem': 'Vegetable Costs', 'typical_pct': 6.0, 'variance': 1.0},
        {'Type': 'COGS', 'SubType': 'Food Costs', 'LineItem': 'Rice/Noodle Costs', 'typical_pct': 3.0, 'variance': 0.5},
        {'Type': 'COGS', 'SubType': 'Packaging', 'LineItem': 'To-Go Containers', 'typical_pct': 2.5, 'variance': 0.5},
        {'Type': 'COGS', 'SubType': 'Beverage', 'LineItem': 'Drink Costs', 'typical_pct': 1.5, 'variance': 0.3},
        
        # Labor Costs
        {'Type': 'Labor', 'SubType': 'Management', 'LineItem': 'Store Manager Salary', 'typical_pct': 3.5, 'variance': 0.5},
        {'Type': 'Labor', 'SubType': 'Management', 'LineItem': 'Assistant Manager Salary', 'typical_pct': 2.5, 'variance': 0.3},
        {'Type': 'Labor', 'SubType': 'Hourly', 'LineItem': 'Crew Labor', 'typical_pct': 20.0, 'variance': 3.0},
        {'Type': 'Labor', 'SubType': 'Benefits', 'LineItem': 'Payroll Taxes', 'typical_pct': 2.0, 'variance': 0.2},
        {'Type': 'Labor', 'SubType': 'Benefits', 'LineItem': 'Health Insurance', 'typical_pct': 1.8, 'variance': 0.2},
        {'Type': 'Labor', 'SubType': 'Benefits', 'LineItem': 'Workers Comp', 'typical_pct': 0.8, 'variance': 0.2},
        
        # Operating Expenses
        {'Type': 'OpEx', 'SubType': 'Occupancy', 'LineItem': 'Base Rent', 'typical_pct': 6.0, 'variance': 1.0},
        {'Type': 'OpEx', 'SubType': 'Occupancy', 'LineItem': 'CAM Charges', 'typical_pct': 1.5, 'variance': 0.3},
        {'Type': 'OpEx', 'SubType': 'Utilities', 'LineItem': 'Electricity', 'typical_pct': 2.8, 'variance': 0.5},
        {'Type': 'OpEx', 'SubType': 'Utilities', 'LineItem': 'Gas', 'typical_pct': 1.2, 'variance': 0.3},
        {'Type': 'OpEx', 'SubType': 'Utilities', 'LineItem': 'Water/Sewer', 'typical_pct': 0.4, 'variance': 0.1},
        {'Type': 'OpEx', 'SubType': 'Marketing', 'LineItem': 'Local Marketing', 'typical_pct': 1.0, 'variance': 0.3},
        {'Type': 'OpEx', 'SubType': 'Marketing', 'LineItem': 'Digital Marketing', 'typical_pct': 0.8, 'variance': 0.2},
        {'Type': 'OpEx', 'SubType': 'Maintenance', 'LineItem': 'Equipment Repairs', 'typical_pct': 1.2, 'variance': 0.4},
        {'Type': 'OpEx', 'SubType': 'Maintenance', 'LineItem': 'Cleaning Supplies', 'typical_pct': 0.6, 'variance': 0.1},
        {'Type': 'OpEx', 'SubType': 'Other', 'LineItem': 'Credit Card Fees', 'typical_pct': 2.2, 'variance': 0.3},
        {'Type': 'OpEx', 'SubType': 'Other', 'LineItem': 'Insurance', 'typical_pct': 0.9, 'variance': 0.1},
        {'Type': 'OpEx', 'SubType': 'Other', 'LineItem': 'Bank Fees', 'typical_pct': 0.3, 'variance': 0.1},
    ]
    
    return line_items

def generate_synthetic_pnl_data(stores_df: pd.DataFrame, periods_df: pd.DataFrame) -> pd.DataFrame:
    """Generate synthetic P&L data for all stores and periods."""
    
    line_items = create_line_items()
    pnl_data = []
    
    # Base revenue assumptions by store type and location
    base_revenue_by_region = {
        'West': {'high': 450000, 'med': 380000, 'low': 320000},
        'Northeast': {'high': 420000, 'med': 360000, 'low': 300000},
        'Southeast': {'high': 380000, 'med': 320000, 'low': 280000},
        'South': {'high': 360000, 'med': 300000, 'low': 250000},
        'Midwest': {'high': 340000, 'med': 290000, 'low': 240000}
    }
    
    # Get recent periods (last 24 months)
    recent_periods = periods_df[periods_df['FiscalYear'].isin([2024, 2025])].copy()
    
    print(f"Generating P&L data for {len(stores_df)} stores across {len(recent_periods)} periods...")
    
    for _, store in stores_df.iterrows():
        store_number = store['storenumber']
        region = store['region']
        sq_ft = store['square_feet']
        
        # Determine store performance tier based on location and size
        if sq_ft > 2100 and region in ['West', 'Northeast']:
            perf_tier = 'high'
        elif sq_ft > 1900:
            perf_tier = 'med'
        else:
            perf_tier = 'low'
            
        base_monthly_revenue = base_revenue_by_region[region][perf_tier] / 13  # 13 periods per year
        
        for _, period in recent_periods.iterrows():
            period_id = period['PeriodID']
            
            # Add seasonality (higher in Q4, lower in Q1)
            fiscal_period = period['FiscalPeriod']
            if fiscal_period in [11, 12, 13]:  # Q4 - holiday season
                seasonal_multiplier = 1.15
            elif fiscal_period in [1, 2]:  # Q1 - post holiday slowdown
                seasonal_multiplier = 0.90
            elif fiscal_period in [6, 7, 8]:  # Summer
                seasonal_multiplier = 1.05
            else:
                seasonal_multiplier = 1.0
                
            # Random variance for realism
            revenue_variance = np.random.normal(1.0, 0.08)
            period_revenue = base_monthly_revenue * seasonal_multiplier * revenue_variance
            
            # Generate data for each line item
            for item in line_items:
                line_item = item['LineItem']
                item_type = item['Type']
                sub_type = item['SubType']
                typical_pct = item['typical_pct']
                variance = item['variance']
                
                # Calculate actual percentage with variance
                actual_pct = max(0, np.random.normal(typical_pct, variance))
                
                if item_type == 'Revenue':
                    # Revenue items are positive
                    actual_amount = period_revenue * (actual_pct / 100)
                    plan_amount = period_revenue * (typical_pct / 100)
                else:
                    # Cost items are negative (expenses)
                    actual_amount = -period_revenue * (actual_pct / 100)
                    plan_amount = -period_revenue * (typical_pct / 100)
                
                pnl_data.append({
                    'storenumber': store_number,
                    'periodid': period_id,
                    'Type': item_type,
                    'SubType': sub_type,
                    'LineItem': line_item,
                    'Actual': round(actual_amount, 2),
                    'Plan': round(plan_amount, 2),
                    'Group': f"{item_type}_{sub_type}"
                })
    
    print(f"Generated {len(pnl_data)} P&L records")
    return pd.DataFrame(pnl_data)

def create_tables_in_databricks():
    """Create the tables in Databricks using Spark SQL."""
    
    print("Creating synthetic Panda Restaurant Group data...")
    
    # Create the DataFrames
    print("1. Creating period dimension...")
    periods_df = create_period_dimension()
    
    print("2. Creating store dimension...")
    stores_df = create_store_dimension()
    
    print("3. Generating P&L data...")
    pnl_df = generate_synthetic_pnl_data(stores_df, periods_df)
    
    # Convert to Spark DataFrames and save as tables
    try:
        print("4. Creating Spark DataFrames and saving to tables...")
        
        # Create period dimension table
        periods_spark = spark.createDataFrame(periods_df)
        periods_spark.write.mode("overwrite").saveAsTable("users.ashwin_pothukuchi.dimperiod")
        print(f"   ✓ Created dimperiod table with {periods_df.shape[0]} records")
        
        # Create store dimension table  
        stores_spark = spark.createDataFrame(stores_df)
        stores_spark.write.mode("overwrite").saveAsTable("users.ashwin_pothukuchi.storedim")
        print(f"   ✓ Created storedim table with {stores_df.shape[0]} records")
        
        # Create main P&L table
        pnl_spark = spark.createDataFrame(pnl_df)
        pnl_spark.write.mode("overwrite").saveAsTable("users.ashwin_pothukuchi.pandapnl")
        print(f"   ✓ Created pandapnl table with {pnl_df.shape[0]} records")
        
        print("\n5. Creating summary views for analytics...")
        
        # Create monthly summary view
        spark.sql("""
        CREATE OR REPLACE VIEW users.ashwin_pothukuchi.panda_monthly_summary AS
        SELECT 
            p.periodid,
            p.FiscalYear,
            p.FiscalPeriod,
            p.FiscalPeriodName as month_year,
            COUNT(DISTINCT pnl.storenumber) as store_count,
            SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END) as total_revenue_sum,
            SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Plan ELSE 0 END) as total_revenue_plan,
            SUM(CASE WHEN pnl.Type = 'COGS' THEN pnl.Actual ELSE 0 END) as total_cogs_actual,
            SUM(CASE WHEN pnl.Type = 'Labor' THEN pnl.Actual ELSE 0 END) as total_labor_actual,
            SUM(CASE WHEN pnl.Type = 'OpEx' THEN pnl.Actual ELSE 0 END) as total_opex_actual,
            SUM(pnl.Actual) as net_income_actual,
            SUM(pnl.Plan) as net_income_plan,
            -- Calculate margins as percentages
            ROUND(100.0 * ABS(SUM(CASE WHEN pnl.Type = 'COGS' THEN pnl.Actual ELSE 0 END)) / 
                  NULLIF(SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END), 0), 2) as cogs_pct_of_sales,
            ROUND(100.0 * ABS(SUM(CASE WHEN pnl.Type = 'Labor' THEN pnl.Actual ELSE 0 END)) / 
                  NULLIF(SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END), 0), 2) as labor_pct_of_sales,
            ROUND(100.0 * (SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END) + 
                           SUM(CASE WHEN pnl.Type = 'COGS' THEN pnl.Actual ELSE 0 END)) / 
                  NULLIF(SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END), 0), 2) as gross_margin_pct,
            ROUND(100.0 * SUM(pnl.Actual) / 
                  NULLIF(SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END), 0), 2) as ebitda_margin_pct
        FROM users.ashwin_pothukuchi.pandapnl pnl
        JOIN users.ashwin_pothukuchi.dimperiod p ON pnl.periodid = p.PeriodID
        GROUP BY p.periodid, p.FiscalYear, p.FiscalPeriod, p.FiscalPeriodName
        ORDER BY p.FiscalYear, p.FiscalPeriod
        """)
        
        # Create store summary view
        spark.sql("""
        CREATE OR REPLACE VIEW users.ashwin_pothukuchi.panda_store_summary AS
        SELECT 
            s.storenumber,
            s.store_name,
            s.state,
            s.region,
            s.square_feet,
            s.store_type,
            COUNT(DISTINCT pnl.periodid) as periods_count,
            SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END) as total_revenue,
            AVG(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END) as avg_period_revenue,
            SUM(CASE WHEN pnl.Type = 'COGS' THEN pnl.Actual ELSE 0 END) as total_cogs,
            SUM(CASE WHEN pnl.Type = 'Labor' THEN pnl.Actual ELSE 0 END) as total_labor,
            SUM(CASE WHEN pnl.Type = 'OpEx' THEN pnl.Actual ELSE 0 END) as total_opex,
            SUM(pnl.Actual) as net_income,
            -- Performance metrics
            ROUND(100.0 * ABS(SUM(CASE WHEN pnl.Type = 'Labor' THEN pnl.Actual ELSE 0 END)) / 
                  NULLIF(SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END), 0), 2) as labor_pct_of_sales,
            ROUND(100.0 * SUM(pnl.Actual) / 
                  NULLIF(SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END), 0), 2) as ebitda_margin_pct,
            ROUND(SUM(CASE WHEN pnl.Type = 'Revenue' THEN pnl.Actual ELSE 0 END) / s.square_feet, 2) as sales_per_sq_ft
        FROM users.ashwin_pothukuchi.storedim s
        LEFT JOIN users.ashwin_pothukuchi.pandapnl pnl ON s.storenumber = pnl.storenumber
        GROUP BY s.storenumber, s.store_name, s.state, s.region, s.square_feet, s.store_type
        ORDER BY total_revenue DESC
        """)
        
        print("   ✓ Created panda_monthly_summary view")
        print("   ✓ Created panda_store_summary view")
        
        print("\n6. Running data validation...")
        
        # Validate the data
        total_records = spark.sql("SELECT COUNT(*) as cnt FROM users.ashwin_pothukuchi.pandapnl").collect()[0]['cnt']
        total_revenue = spark.sql("SELECT SUM(Actual) as rev FROM users.ashwin_pothukuchi.pandapnl WHERE Type = 'Revenue'").collect()[0]['rev']
        
        print(f"   ✓ Total P&L records: {total_records:,}")
        print(f"   ✓ Total revenue: ${total_revenue:,.2f}")
        
        # Show sample data
        print("\n7. Sample data preview:")
        print("Monthly Summary (last 5 periods):")
        spark.sql("""
        SELECT month_year, store_count, 
               ROUND(total_revenue_sum/1000, 0) as revenue_k,
               ROUND(labor_pct_of_sales, 1) as labor_pct,
               ROUND(ebitda_margin_pct, 1) as ebitda_pct
        FROM users.ashwin_pothukuchi.panda_monthly_summary 
        ORDER BY FiscalYear DESC, FiscalPeriod DESC 
        LIMIT 5
        """).show()
        
        print("\nTop 5 Performing Stores:")
        spark.sql("""
        SELECT store_name, state, 
               ROUND(total_revenue/1000, 0) as revenue_k,
               ROUND(labor_pct_of_sales, 1) as labor_pct,
               ROUND(ebitda_margin_pct, 1) as ebitda_pct,
               ROUND(sales_per_sq_ft, 0) as sales_per_sqft
        FROM users.ashwin_pothukuchi.panda_store_summary 
        ORDER BY total_revenue DESC 
        LIMIT 5
        """).show()
        
        print("\n🎉 SUCCESS: Synthetic Panda Restaurant Group data created successfully!")
        print("\nTables created:")
        print("- users.ashwin_pothukuchi.pandapnl (main P&L data)")
        print("- users.ashwin_pothukuchi.dimperiod (time periods)")
        print("- users.ashwin_pothukuchi.storedim (store information)")
        print("- users.ashwin_pothukuchi.panda_monthly_summary (view)")
        print("- users.ashwin_pothukuchi.panda_store_summary (view)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False

def main():
    """Main function to run the data generation."""
    print("=" * 70)
    print("Panda Restaurant Group - Synthetic Data Generator")
    print("=" * 70)
    
    try:
        success = create_tables_in_databricks()
        if success:
            print("\n✅ Data generation completed successfully!")
            print("\nNext steps:")
            print("1. Test the data with: SELECT * FROM users.ashwin_pothukuchi.panda_monthly_summary LIMIT 10")
            print("2. Update your backend queries to use the new table structure")
            print("3. Configure app.yaml with the new schema settings")
        else:
            print("\n❌ Data generation failed. Check the error messages above.")
            
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
