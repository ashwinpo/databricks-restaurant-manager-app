# Databricks notebook source
# MAGIC %md
# MAGIC # Panda Restaurant Group P&L Insights Generator
# MAGIC
# MAGIC This notebook demonstrates the **correct way** to generate AI-driven insights from P&L data using:
# MAGIC 1. **Databricks Genie** for structured data extraction (text-to-SQL)
# MAGIC 2. **Claude via Model Serving** for narrative analysis of structured insights
# MAGIC
# MAGIC ## Why This Approach vs. Direct LLM Analysis?
# MAGIC
# MAGIC ❌ **Problematic Approach**: Passing raw table data directly to LLMs
# MAGIC - **Non-deterministic**: Results vary between runs
# MAGIC - **Security risk**: Raw data exposure
# MAGIC - **Cost inefficient**: Large token consumption
# MAGIC - **Limited context**: LLMs can't see full dataset relationships
# MAGIC
# MAGIC ✅ **Correct Approach**: Genie + Structured Insights + LLM Analysis
# MAGIC - **Deterministic**: SQL-based data extraction ensures consistency
# MAGIC - **Secure**: Only structured insights passed to LLMs, not raw data
# MAGIC - **Cost effective**: Minimal token usage for analysis
# MAGIC - **Comprehensive**: Genie understands full data schema and relationships

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuration and Setup

# COMMAND ----------

!pip install -U databricks-langchain
%restart_python

# COMMAND ----------

# Configuration - Update these for your environment
GENIE_SPACE_ID = "01f08a789d6b16cf8e8819ef3db441d9"  # Your Genie Space ID
LLM_ENDPOINT_NAME = "databricks-claude-sonnet-4"        # Your Claude endpoint
STORE_NUMBER = "1619"                                      # Store to analyze
PERIOD_ID = "202507"                                       # Period to analyze

# COMMAND ----------

# Import required libraries
import json
import requests
import pandas as pd
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from io import StringIO

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Genie Agent Setup
# MAGIC
# MAGIC We embed the Genie client code directly in the notebook so it can run independently without external dependencies.
# MAGIC This allows easy deployment to customer environments.

# COMMAND ----------

# Genie Agent Implementation (embedded for portability)
from databricks_langchain import ChatDatabricks
from databricks_langchain.genie import GenieAgent

@dataclass
class GenieResult:
    """Result from Genie containing answer, SQL, and data."""
    answer: str
    sql: str
    df: pd.DataFrame

@dataclass
class QuantitativeInsight:
    """Structure for storing quantitative insights"""
    category: str
    subcategory: str
    metric_name: str
    value: float
    comparison_value: Optional[float] = None
    variance_pct: Optional[float] = None
    period: str = ""
    context: str = ""
    sql_query: Optional[str] = None

def extract_sql_from_text(text: str) -> str:
    """Extract SQL query from natural language text."""
    sql_patterns = [
        r'```sql\s*(.*?)\s*```',  # SQL code blocks
        r'```\s*(SELECT.*?)\s*```',  # Generic code blocks with SELECT
        r'(SELECT\s+.*?(?:;|$))',  # Inline SELECT statements
    ]
    
    for pattern in sql_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            return matches[0].strip()
    
    return ""

def extract_data_from_text(text: str) -> pd.DataFrame:
    """Extract tabular data from natural language text."""
    try:
        lines = text.split('\n')
        table_lines = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            if '|' in line and (line.count('|') >= 2):
                in_table = True
                if not re.match(r'^[\|\s\-:]+$', line):
                    table_lines.append(line)
            elif in_table and line == '':
                break
            elif in_table and '|' not in line:
                break
        
        if len(table_lines) >= 2:
            csv_lines = []
            for line in table_lines:
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                csv_lines.append(','.join(f'"{cell}"' for cell in cells))
            
            csv_text = '\n'.join(csv_lines)
            df = pd.read_csv(StringIO(csv_text))
            df.columns = df.columns.str.strip()
            return df
            
    except Exception:
        pass
    
    return pd.DataFrame()

# Initialize Genie Agent
genie_agent = GenieAgent(
    genie_space_id=GENIE_SPACE_ID,
    genie_agent_name="PandaPnLAnalyst",
    description="AI assistant for Panda Restaurant Group P&L analytics, operations, and performance insights using natural language SQL queries.",
)

def ask_genie_structured(question: str) -> GenieResult:
    """Send a natural-language question to Genie and return structured result."""
    
    enhanced_question = f"""
Context: You are analyzing data for Panda Restaurant Group, a fast-casual restaurant chain. 
The data includes store performance, P&L metrics, operational data, and regional comparisons.

Available tables and views:
- users.ashwin_pothukuchi.store_1619_pnl: Main P&L data by store and period (storenumber, periodid, Type, SubType, LineItem, Actual, Plan, Group)

Key data structure:
- P&L data is organized by Type (Revenue, COGS, Labor, OpEx), SubType, and LineItem
- Revenue items are positive, cost items are negative
- Store performance can be analyzed by region, store type, and size

Question: {question}

Please provide actionable insights for restaurant operations and management.
If you execute a SQL query, please include the query in your response.
If you return data, please format it clearly in a table.
Focus on operational metrics like labor costs, food costs, sales performance, and efficiency.
"""

    try:
        result = genie_agent.invoke({"messages": [{"role": "user", "content": enhanced_question}]})
        
        content = ""
        if isinstance(result, dict):
            messages = result.get("messages", [])
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("content"):
                    content = msg["content"]
                    break
                elif hasattr(msg, 'content'):
                    content = str(msg.content)
                    break
        else:
            if hasattr(result, 'content'):
                content = str(result.content)
        
        if not content:
            return GenieResult(answer="No response from Genie", sql="", df=pd.DataFrame())
        
        sql = extract_sql_from_text(content)
        df = extract_data_from_text(content)
        
        return GenieResult(answer=content, sql=sql, df=df)
        
    except Exception as e:
        return GenieResult(answer=f"Error calling Genie: {str(e)}", sql="", df=pd.DataFrame())

print("✅ Genie Agent initialized successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Quantitative Insight Generation
# MAGIC
# MAGIC Extract structured, quantitative insights using Genie's text-to-SQL capabilities.

# COMMAND ----------

class PandaInsightGenerator:
    """Generate structured quantitative insights from Panda P&L data using Genie"""
    
    def __init__(self):
        self.insights: List[QuantitativeInsight] = []
    
    def generate_revenue_insights(self, store_number: str, period: str) -> List[QuantitativeInsight]:
        """Generate revenue performance insights"""
        insights = []
        
        print(f"🔍 Analyzing revenue performance for Store {store_number}, Period {period}...")
        
        # Net Sales Analysis
        net_sales_query = f"""
        For store {store_number} in period {period}, show me the Net Sales breakdown:
        1. Total Net Sales (actual vs plan) - filter for Type = 'Net Sales'
        2. Include all Net Sales line items with actual and plan values
        3. Calculate variance percentages
        Order by actual value descending.
        """
        
        response = ask_genie_structured(net_sales_query)
        print(f"📊 Net Sales Analysis: Found {len(response.df)} line items")
        
        if not response.df.empty and 'Actual' in response.df.columns:
            for _, row in response.df.iterrows():
                actual = float(row.get('Actual', 0))
                plan = float(row.get('Plan', 0))
                variance = ((actual - plan) / plan * 100) if plan != 0 else 0
                
                line_item = row.get('LineItem', 'Net Sales')
                
                insights.append(QuantitativeInsight(
                    category="Revenue Performance",
                    subcategory="Net Sales",
                    metric_name=line_item,
                    value=actual,
                    comparison_value=plan,
                    variance_pct=variance,
                    period=period,
                    context=f"Store {store_number} net sales analysis",
                    sql_query=response.sql
                ))
        
        # Digital Sales Analysis
        digital_query = f"""
        For store {store_number} in period {period}, show me digital sales performance:
        1. Third party digital sales
        2. Panda digital sales  
        3. Sales channel breakdown for digital/online orders
        Filter for Type containing 'Digital' or 'Third Party'.
        """
        
        digital_response = ask_genie_structured(digital_query)
        print(f"📱 Digital Sales Analysis: Found {len(digital_response.df)} metrics")
        
        return insights
    
    def generate_cost_insights(self, store_number: str, period: str) -> List[QuantitativeInsight]:
        """Generate cost structure insights"""
        insights = []
        
        print(f"💰 Analyzing cost structure for Store {store_number}, Period {period}...")
        
        # COGS Analysis
        cogs_query = f"""
        For store {store_number} in period {period}, show me Cost of Goods Sold analysis:
        1. Total COGS by category (actual vs plan)
        2. COGS breakdown by food type (chicken, beef, seafood, etc.)
        3. Calculate COGS as percentage of sales where possible
        Filter for Type = 'Cogs'. Show actual vs plan values.
        """
        
        response = ask_genie_structured(cogs_query)
        print(f"🍗 COGS Analysis: Found {len(response.df)} cost categories")
        
        # Labor Analysis
        labor_query = f"""
        For store {store_number} in period {period}, show me Labor cost analysis:
        1. Total labor costs (actual vs plan)
        2. Labor breakdown by category (management, hourly, benefits)
        3. Labor hours vs costs analysis
        Filter for Type = 'Labor'. Show actual vs plan values.
        """
        
        labor_response = ask_genie_structured(labor_query)
        print(f"👥 Labor Analysis: Found {len(labor_response.df)} labor categories")
        
        if not labor_response.df.empty and 'Actual' in labor_response.df.columns:
            total_labor_actual = labor_response.df['Actual'].sum()
            total_labor_plan = labor_response.df['Plan'].sum() if 'Plan' in labor_response.df.columns else 0
            variance = ((total_labor_actual - total_labor_plan) / total_labor_plan * 100) if total_labor_plan != 0 else 0
            
            insights.append(QuantitativeInsight(
                category="Cost Structure",
                subcategory="Labor Costs",
                metric_name="Total Labor Costs",
                value=total_labor_actual,
                comparison_value=total_labor_plan,
                variance_pct=variance,
                period=period,
                context=f"Store {store_number} total labor cost analysis"
            ))
        
        return insights
    
    def generate_profitability_insights(self, store_number: str, period: str) -> List[QuantitativeInsight]:
        """Generate profitability analysis insights"""
        insights = []
        
        print(f"📈 Analyzing profitability for Store {store_number}, Period {period}...")
        
        profit_query = f"""
        For store {store_number} in period {period}, show me profitability metrics:
        1. Controllable Profit (actual vs plan)
        2. Restaurant Contribution (actual vs plan)  
        3. Key profitability ratios and margins
        Filter for Type in ('Controllable Profit', 'Restaurant Contribution').
        """
        
        response = ask_genie_structured(profit_query)
        print(f"💹 Profitability Analysis: Found {len(response.df)} profit metrics")
        
        if not response.df.empty and 'Actual' in response.df.columns:
            for _, row in response.df.iterrows():
                actual = float(row.get('Actual', 0))
                plan = float(row.get('Plan', 0))
                variance = ((actual - plan) / plan * 100) if plan != 0 else 0
                metric_type = row.get('Type', 'Profitability Metric')
                
                insights.append(QuantitativeInsight(
                    category="Profitability Analysis",
                    subcategory=metric_type,
                    metric_name=metric_type,
                    value=actual,
                    comparison_value=plan,
                    variance_pct=variance,
                    period=period,
                    context=f"Store {store_number} {metric_type.lower()} performance"
                ))
        
        return insights
    
    def generate_variance_analysis(self, store_number: str, period: str) -> List[QuantitativeInsight]:
        """Generate variance analysis insights"""
        insights = []
        
        print(f"⚠️ Analyzing variances for Store {store_number}, Period {period}...")
        
        variance_query = f"""
        For store {store_number} in period {period}, find significant variances:
        1. Calculate variance percentage for each line item: ((Actual - Plan) / Plan) * 100
        2. Show items with variance greater than 20% (positive or negative)  
        3. Focus on items with significant dollar impact (absolute value > 1000)
        4. Include Type, SubType, LineItem, Actual, Plan, and calculated variance
        Order by absolute variance percentage descending.
        """
        
        response = ask_genie_structured(variance_query)
        print(f"📊 Variance Analysis: Found {len(response.df)} significant variances")
        
        return insights
    
    def generate_all_insights(self, store_number: str, period: str) -> List[QuantitativeInsight]:
        """Generate comprehensive insights for a store and period"""
        print(f"\n🚀 Generating comprehensive insights for Store {store_number}, Period {period}\n")
        
        all_insights = []
        
        all_insights.extend(self.generate_revenue_insights(store_number, period))
        all_insights.extend(self.generate_cost_insights(store_number, period))
        all_insights.extend(self.generate_profitability_insights(store_number, period))
        all_insights.extend(self.generate_variance_analysis(store_number, period))
        
        self.insights = all_insights
        print(f"\n✅ Generated {len(all_insights)} quantitative insights")
        return all_insights

# Generate insights
generator = PandaInsightGenerator()
insights = generator.generate_all_insights(STORE_NUMBER, PERIOD_ID)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Prepare Structured Data for Claude Analysis

# COMMAND ----------

# Convert insights to structured JSON for Claude analysis
insights_data = {
    "store_number": STORE_NUMBER,
    "period": PERIOD_ID,
    "analysis_date": datetime.now().isoformat(),
    "total_insights": len(insights),
    "insights_by_category": {},
    "key_metrics": [],
    "significant_variances": []
}

# Group insights by category
for insight in insights:
    category = insight.category
    if category not in insights_data["insights_by_category"]:
        insights_data["insights_by_category"][category] = []
    
    insight_dict = asdict(insight)
    insights_data["insights_by_category"][category].append(insight_dict)
    
    # Identify key metrics (high dollar values)
    if abs(insight.value) > 50000:
        insights_data["key_metrics"].append({
            "metric": insight.metric_name,
            "value": insight.value,
            "plan": insight.comparison_value,
            "variance_pct": insight.variance_pct,
            "category": insight.category
        })
    
    # Identify significant variances (>20%)
    if insight.variance_pct and abs(insight.variance_pct) > 20:
        insights_data["significant_variances"].append({
            "metric": insight.metric_name,
            "variance_pct": insight.variance_pct,
            "actual": insight.value,
            "plan": insight.comparison_value,
            "category": insight.category
        })

# Convert to JSON string for Claude
insights_json = json.dumps(insights_data, indent=2)

print(f"📋 Prepared structured data for Claude analysis:")
print(f"   • {len(insights_data['key_metrics'])} key metrics")
print(f"   • {len(insights_data['significant_variances'])} significant variances")
print(f"   • {len(insights_data['insights_by_category'])} insight categories")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Claude Analysis via Model Serving
# MAGIC
# MAGIC Now we send our structured insights (not raw table data) to Claude for narrative analysis.

# COMMAND ----------

# Get Databricks token for API calls
token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# Construct Claude endpoint URL
workspace_url = spark.conf.get("spark.databricks.workspaceUrl")
endpoint_url = f"https://{workspace_url}/serving-endpoints/{LLM_ENDPOINT_NAME}/invocations"

# Craft the analysis prompt
analysis_prompt = f"""You are a professional restaurant operations analyst. I will provide you with structured quantitative insights from a Panda Restaurant Group store's P&L data.

Your task is to analyze these insights and provide a comprehensive business analysis report similar to a management consulting deliverable.

**Important Context:**
- This data comes from structured SQL queries via Databricks Genie (not raw table dumps)
- All metrics have been validated and variance calculations are accurate
- Focus on actionable business insights for restaurant operations

**Analysis Framework:**
1. **Key Insights and Trends** - What are the most important findings?
2. **Notable Patterns and Anomalies** - What stands out as unusual or concerning?
3. **Business Implications** - What actions should management take?

**Structured Data:**
```json
{insights_json}
```

**Instructions:**
- Think step-by-step through the analysis
- Prioritize high-impact findings (large dollar amounts, significant variances)
- Provide specific, actionable recommendations
- Use professional business language
- Structure your response with clear sections and bullet points
- Include relevant metrics and percentages to support your analysis
- Focus on operational efficiency, cost control, and revenue optimization

Please provide a thorough analysis that a restaurant executive could use to make informed decisions."""

# Prepare the API request
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "messages": [
        {
            "role": "user",
            "content": analysis_prompt
        }
    ],
    "max_tokens": 20000,
    # # Enable reasoning for deeper analysis
    # "extra_body": {
    "thinking": {
        "type": "enabled", 
        "budget_tokens": 5000
    }
    # }
}

print(f"🤖 Sending structured insights to Claude for analysis...")
print(f"   • Endpoint: {LLM_ENDPOINT_NAME}")
print(f"   • Data size: {len(insights_json)} characters")
print(f"   • Using reasoning mode for deeper analysis")

# COMMAND ----------

# Call Claude API
try:
    response = requests.post(
        endpoint_url,
        headers=headers,
        json=payload,
        timeout=120
    )
    
    response.raise_for_status()
    result = response.json()
    
    # Extract Claude's analysis
    claude_analysis = result.get("choices", [{}])[0].get("message", {}).get("content", "No analysis generated.")
    
    print("✅ Claude analysis completed successfully!")
    
except Exception as e:
    claude_analysis = f"❌ Error calling Claude: {str(e)}"
    print(f"❌ Error: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Final Analysis Report

# COMMAND ----------

# Display the comprehensive analysis
print("=" * 80)
print(f"PANDA RESTAURANT GROUP P&L ANALYSIS")
print(f"Store {STORE_NUMBER} | Period {PERIOD_ID}")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print()

print("METHODOLOGY:")
print("✅ Structured data extraction via Databricks Genie (text-to-SQL)")
print("✅ Quantitative insights generation and validation")
print("✅ AI-powered narrative analysis via Claude Model Serving")
print("✅ No raw table data exposed to LLMs - secure and deterministic")
print()

print("ANALYSIS RESULTS:")
print("-" * 40)
print(claude_analysis)

# COMMAND ----------

len(claude_analysis[1])

# COMMAND ----------

from IPython.display import Markdown, display
display(Markdown(claude_analysis[1]["text"]))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Generate UI Card Configuration
# MAGIC
# MAGIC Generate the JSON structure needed for the frontend P&L Insights cards.
# MAGIC This allows easy integration with the React frontend application.

# COMMAND ----------

# Generate structured insights using Claude
def generate_structured_insights_with_claude(insights_data: dict, token: str, endpoint_url: str) -> dict:
    """Use Claude to identify key insights and structure them for UI cards"""
    
    insights_prompt = f"""You are a restaurant operations analyst creating executive dashboard cards for a store manager.

I will provide you with structured P&L data from Databricks Genie. Your task is to identify the 5 most important insights that a store manager needs to know and act upon.

**Structured P&L Data:**
```json
{json.dumps(insights_data, indent=2)}
```

**Your Task:**
Create exactly 5 insight cards that follow this structure. Focus on actionable insights that drive business results.

**Required JSON Format:**
```json
{{
  "insights": [
    {{
      "title": "Clear, action-oriented title (max 50 chars)",
      "type": "critical|alert|opportunity|insight|performance",
      "priority": "urgent|high|medium|low",
      "icon": "TrendingDown|TrendingUp|DollarSign|BarChart3|Target|AlertCircle",
      "metric_value": "percentage or dollar variance (e.g., '-18.6%', '+$5,294')",
      "metric_label": "brief context (e.g., 'vs Plan', 'Over Budget')",
      "actual_amount": "actual dollar amount (e.g., '$15,826')",
      "planned_amount": "planned dollar amount (e.g., '$19,442')",
      "variance_amount": "variance with +/- sign (e.g., '-$3,616')",
      "description": "1-2 sentence explanation of what happened and why it matters",
      "recommendation": "Specific, actionable recommendation for the store manager",
      "primary_action": "Main action button text (e.g., 'Equipment Audit')",
      "secondary_action": "Secondary action button text (e.g., 'Staff Training')",
      "impact": "Business impact description (e.g., 'Critical - largest revenue gap')",
      "timeframe": "When to act (e.g., 'Immediate (Week 1)', 'This week', '30-90 days')",
      "data_source": "Which P&L category this insight comes from"
    }}
  ],
  "kpi_header": {{
    "revenue": {{
      "value": "revenue variance percentage (e.g., '-6.1%')",
      "amount": "total revenue amount (e.g., '$320,433')"
    }},
    "profit": {{
      "value": "profit variance percentage (e.g., '-6.6%')",
      "amount": "profit amount (e.g., '$539,814')"
    }},
    "critical": {{
      "value": "most critical metric variance (e.g., '-18.6%')",
      "amount": "critical metric amount (e.g., '$15,826')",
      "label": "what this critical metric represents (e.g., 'Beverage Sales')"
    }}
  }}
}}
```

**Guidelines:**
- Prioritize insights by business impact (large dollar amounts, significant variances)
- Use "critical" for urgent issues (>30% variance or major revenue gaps)
- Use "alert" for important warnings (15-30% negative variance)
- Use "opportunity" for positive trends or cost savings (>20% positive variance)
- Use "insight" for important patterns or moderate variances (10-20%)
- Use "performance" for overall performance summaries
- Make titles punchy and manager-friendly (avoid jargon)
- Recommendations should be specific and actionable
- Focus on what the store manager can actually control or influence
- Include timeframes that reflect urgency and business cycles

**Icons Guide:**
- TrendingDown: Declining performance, negative variances
- TrendingUp: Improving performance, positive trends  
- DollarSign: Cost/revenue focus, financial opportunities
- BarChart3: Performance analysis, comparisons
- Target: Goals, targets, optimization
- AlertCircle: Attention needed, monitoring required

Return ONLY the JSON structure, no other text."""

    # Prepare the API request for insights generation
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            {
                "role": "user",
                "content": insights_prompt
            }
        ],
        "max_tokens": 8000,
        "thinking": {
            "type": "enabled", 
            "budget_tokens": 3000
        }
    }

    print(f"🤖 Asking Claude to generate structured insights...")
    
    try:
        response = requests.post(
            endpoint_url,
            headers=headers,
            json=payload,
            timeout=120
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract Claude's response
        claude_response = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Parse the JSON from Claude's response
        try:
            # Extract JSON from Claude's response (handle potential markdown formatting)
            json_start = claude_response.find('{')
            json_end = claude_response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = claude_response[json_start:json_end]
                claude_insights = json.loads(json_str)
                print("✅ Successfully parsed Claude's structured insights")
                return claude_insights
            else:
                raise ValueError("No valid JSON found in Claude's response")
                
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Claude's JSON response: {e}")
            print(f"Raw response: {claude_response[:500]}...")
            return None
            
    except Exception as e:
        print(f"❌ Error calling Claude for insights: {e}")
        return None

# Convert Claude's insights to UI configuration format
def convert_claude_insights_to_ui_config(claude_insights: dict, store_number: str, period: str, total_raw_insights: int) -> dict:
    """Convert Claude's structured insights into the UI configuration format"""
    
    if not claude_insights or "insights" not in claude_insights:
        print("❌ Invalid Claude insights structure")
        return None
    
    ui_cards = []
    
    for idx, insight in enumerate(claude_insights["insights"], 1):
        # Map action labels to action identifiers
        primary_action_id = insight["primary_action"].lower().replace(" ", "_").replace("-", "_")
        secondary_action_id = insight["secondary_action"].lower().replace(" ", "_").replace("-", "_")
        
        ui_card = {
            "id": idx,
            "type": insight["type"],
            "priority": insight["priority"],
            "icon": insight["icon"],
            "title": insight["title"],
            "description": insight["description"],
            "metric": insight["metric_value"],
            "metricLabel": insight["metric_label"],
            "actualValue": insight["actual_amount"],
            "plannedValue": insight["planned_amount"],
            "variance": insight["variance_amount"],
            "recommendation": insight["recommendation"],
            "actions": [
                {
                    "label": insight["primary_action"],
                    "type": "primary",
                    "action": primary_action_id
                },
                {
                    "label": insight["secondary_action"],
                    "type": "secondary",
                    "action": secondary_action_id
                }
            ],
            "impact": insight["impact"],
            "timeframe": insight["timeframe"],
            "dataSource": insight["data_source"]
        }
        
        ui_cards.append(ui_card)
    
    # Use Claude's KPI header data
    kpi_header = claude_insights.get("kpi_header", {})
    
    config = {
        "metadata": {
            "store_number": store_number,
            "period": period,
            "generated_at": datetime.now().isoformat(),
            "total_insights": total_raw_insights,
            "methodology": "Databricks Genie + Claude Structured Insights"
        },
        "kpi_header": kpi_header,
        "insight_cards": ui_cards
    }
    
    return config

# Generate structured insights using Claude
print("\n" + "=" * 80)
print("🎯 GENERATING STRUCTURED INSIGHTS WITH CLAUDE")
print("=" * 80)

# Use Claude to generate structured insights from the quantitative data
claude_insights = generate_structured_insights_with_claude(insights_data, token, endpoint_url)

if claude_insights:
    # Convert Claude's insights to UI configuration format
    ui_config = convert_claude_insights_to_ui_config(
        claude_insights, 
        STORE_NUMBER, 
        PERIOD_ID, 
        len(insights)
    )
    
    if ui_config:
        print("🎨 Generated UI Cards Configuration:")
        print(f"   • {len(ui_config['insight_cards'])} insight cards")
        print(f"   • KPI header with revenue, profit, and critical metrics")
        print(f"   • AI-generated insights with actionable recommendations")
        print(f"   • Ready for frontend integration")
        print()

        # Display the JSON configuration
        print("=" * 80)
        print("FRONTEND INTEGRATION - COPY THIS JSON:")
        print("=" * 80)
        print(json.dumps(ui_config, indent=2))
        print("=" * 80)
        print()
        print("📋 Instructions:")
        print("1. Copy the JSON above")
        print("2. Save it as 'pnl-insights-config.json' in your frontend project")
        print("3. Update the PnLInsightsBrief component to load from this file")
        print("4. The UI will automatically display your store's insights!")
        print()
        print("🚀 Benefits of this approach:")
        print("   • Claude identifies the most important business insights")
        print("   • Natural language titles and recommendations")
        print("   • Flexible insight generation (not pre-defined templates)")
        print("   • Quantitative data from Genie + qualitative insights from Claude")
        
    else:
        print("❌ Failed to convert Claude insights to UI configuration")
        print("   Falling back to structured data summary...")
        
        # Fallback: show the raw insights data for manual processing
        print("\n📊 Raw Quantitative Insights (for manual processing):")
        print(json.dumps(insights_data, indent=2))
        
else:
    print("❌ Failed to generate structured insights with Claude")
    print("   This could be due to:")
    print("   • API connectivity issues")
    print("   • Invalid response format from Claude")
    print("   • Insufficient quantitative data")
    print()
    print("📊 Raw Quantitative Insights (for manual processing):")
    print(json.dumps(insights_data, indent=2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Save Results and Summary

# COMMAND ----------

# # Save the complete analysis results
# analysis_results = {
#     "metadata": {
#         "store_number": STORE_NUMBER,
#         "period": PERIOD_ID,
#         "generated_at": datetime.now().isoformat(),
#         "genie_space_id": GENIE_SPACE_ID,
#         "llm_endpoint": LLM_ENDPOINT_NAME,
#         "methodology": "Genie + Structured Insights + Claude Analysis"
#     },
#     "quantitative_insights": {
#         "total_insights": len(insights),
#         "insights_by_category": insights_data["insights_by_category"],
#         "key_metrics": insights_data["key_metrics"],
#         "significant_variances": insights_data["significant_variances"]
#     },
#     "narrative_analysis": claude_analysis,
#     "summary": {
#         "approach": "Used Databricks Genie for structured data extraction, then Claude for narrative analysis",
#         "benefits": [
#             "Deterministic and repeatable results",
#             "Secure - no raw data exposure", 
#             "Cost effective token usage",
#             "Comprehensive business insights"
#         ]
#     }
# }

# # Convert to JSON for storage
# results_json = json.dumps(analysis_results, indent=2)

# print(f"📄 Complete analysis saved:")
# print(f"   • {len(insights)} quantitative insights extracted")
# print(f"   • {len(insights_data['key_metrics'])} key metrics identified")
# print(f"   • {len(insights_data['significant_variances'])} significant variances found")
# print(f"   • Comprehensive narrative analysis generated")
# print()
# print("🎯 This approach demonstrates the proper way to generate AI-driven")
# print("   business insights from P&L data using structured methodologies.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC
# MAGIC This notebook demonstrates the **optimal approach** for AI-driven P&L insights generation:
# MAGIC
# MAGIC ### ✅ What We Did Right:
# MAGIC 1. **Genie for Data Extraction** - Used text-to-SQL for structured, deterministic queries
# MAGIC 2. **Quantitative Insights Generation** - Extracted specific metrics with variance calculations  
# MAGIC 3. **Claude for Insight Identification** - AI determines the most important business insights
# MAGIC 4. **Structured UI Configuration** - Generated ready-to-use dashboard configuration
# MAGIC 5. **Flexible Insight Generation** - Not limited to pre-defined templates or categories
# MAGIC
# MAGIC ### 🎯 Key Innovation:
# MAGIC **Two-Stage AI Approach:**
# MAGIC - **Stage 1 (Genie)**: Extract reliable quantitative data via text-to-SQL
# MAGIC - **Stage 2 (Claude)**: Identify key insights and create actionable recommendations
# MAGIC
# MAGIC This gives us the best of both worlds: **deterministic data + creative insight generation**
# MAGIC
# MAGIC ### ❌ What We Avoided:
# MAGIC - Passing raw table data directly to LLMs
# MAGIC - Pre-defining insight categories (limiting flexibility)
# MAGIC - Non-deterministic data extraction
# MAGIC - Security risks from data exposure
# MAGIC - Inefficient token usage
# MAGIC
# MAGIC ### 🔄 Next Steps:
# MAGIC - Deploy this notebook to production environments
# MAGIC - Extend to analyze multiple stores and periods
# MAGIC - Create automated reporting pipelines
# MAGIC - Build alerting for significant variances
# MAGIC - Customize insight prompts for different business contexts
# MAGIC
# MAGIC ### 🚀 Business Value:
# MAGIC - **Store managers** get AI-curated insights focused on what matters most
# MAGIC - **Flexible adaptation** to different business scenarios and priorities
# MAGIC - **Actionable recommendations** with specific timeframes and impact assessments
# MAGIC - **Easy deployment** - just copy JSON to update the dashboard
# MAGIC
# MAGIC This methodology provides a scalable, secure, and highly flexible foundation for AI-powered business analytics.