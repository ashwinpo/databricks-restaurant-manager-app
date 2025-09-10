"""
Local Databricks Genie client for Panda Restaurant Group demo.
Uses PAT authentication for local development.
"""

import os
import json
import re
import pandas as pd
from typing import Optional
from dataclasses import dataclass
from io import StringIO

from dotenv import load_dotenv

# These third-party libraries are required for Genie
try:
    from databricks_langchain import ChatDatabricks
    from databricks_langchain.genie import GenieAgent
except ImportError as e:
    raise ImportError(
        "databricks-langchain is not installed. Add it to requirements.txt "
        "and run `pip install -r requirements.txt`."
    ) from e

# Load environment variables from .env
load_dotenv()

# ---------------------------------------------------------------------------
# Environment variable mapping & validation
# ---------------------------------------------------------------------------

# Required values
GENIE_SPACE_ID = os.getenv("GENIE_SPACE_ID")
LLM_ENDPOINT_NAME = os.getenv("LLM_ENDPOINT_NAME")

# For local development with PAT auth
DATABRICKS_HOST = os.getenv("DB_HOST")
DATABRICKS_TOKEN = os.getenv("DB_PAT")  # Map DB_PAT to DATABRICKS_TOKEN

# Set DATABRICKS_HOST and DATABRICKS_TOKEN for the SDK
if DATABRICKS_HOST and DATABRICKS_TOKEN:
    os.environ["DATABRICKS_HOST"] = DATABRICKS_HOST
    os.environ["DATABRICKS_TOKEN"] = DATABRICKS_TOKEN

has_pat_auth = DATABRICKS_HOST and DATABRICKS_TOKEN

if not has_pat_auth:
    raise EnvironmentError(
        "Missing authentication credentials. For local development, "
        "provide DB_HOST and DB_PAT environment variables."
    )

# Always require these regardless of auth method
_missing = [
    name for name, val in {
        "GENIE_SPACE_ID": GENIE_SPACE_ID,
        "LLM_ENDPOINT_NAME": LLM_ENDPOINT_NAME,
    }.items() if not val
]

if _missing:
    raise EnvironmentError(
        "Missing required environment variables for Genie client: "
        + ", ".join(_missing)
    )

# ---------------------------------------------------------------------------
# Initialize LLM & Genie agent
# ---------------------------------------------------------------------------

_llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME, streaming=False)

_genie = GenieAgent(
    genie_space_id=GENIE_SPACE_ID,
    genie_agent_name="PandaGenie",
    description=os.getenv(
        "GENIE_AGENT_DESCRIPTION",
        "This Genie agent can answer questions about Panda Restaurant Group P&L data, operations, and performance metrics using natural language SQL queries.",
    ),
)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class GenieResult:
    """Result from Genie containing answer, SQL, and data."""
    answer: str
    sql: str
    df: pd.DataFrame

# ---------------------------------------------------------------------------
# Helper functions  
# ---------------------------------------------------------------------------

def extract_sql_from_text(text: str) -> str:
    """Extract SQL query from natural language text."""
    # Look for SQL patterns in the text
    sql_patterns = [
        r'```sql\s*(.*?)\s*```',  # SQL code blocks
        r'```\s*(SELECT.*?)\s*```',  # Generic code blocks with SELECT
        r'(SELECT\s+.*?(?:;|$))',  # Inline SELECT statements
        r'(INSERT\s+.*?(?:;|$))',  # Inline INSERT statements
        r'(UPDATE\s+.*?(?:;|$))',  # Inline UPDATE statements
        r'(DELETE\s+.*?(?:;|$))',  # Inline DELETE statements
    ]
    
    for pattern in sql_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            return matches[0].strip()
    
    return ""

def extract_data_from_text(text: str) -> pd.DataFrame:
    """Extract tabular data from natural language text."""
    try:
        # Look for markdown tables
        lines = text.split('\n')
        table_lines = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            if '|' in line and (line.count('|') >= 2):
                in_table = True
                # Skip separator lines (like |---|---|)
                if not re.match(r'^[\|\s\-:]+$', line):
                    table_lines.append(line)
            elif in_table and line == '':
                break
            elif in_table and '|' not in line:
                break
        
        if len(table_lines) >= 2:  # At least header and one data row
            # Convert to CSV format
            csv_lines = []
            for line in table_lines:
                # Remove leading/trailing |, split by |, and clean up
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                csv_lines.append(','.join(f'"{cell}"' for cell in cells))
            
            csv_text = '\n'.join(csv_lines)
            df = pd.read_csv(StringIO(csv_text))
            
            # Clean up column names and data
            df.columns = df.columns.str.strip()
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.strip()
            
            return df
            
    except Exception as e:
        # If parsing fails, return empty DataFrame
        pass
    
    return pd.DataFrame()

# ---------------------------------------------------------------------------
# Public helper functions
# ---------------------------------------------------------------------------

def ask_genie_structured(question: str, *, _agent: Optional[GenieAgent] = None) -> GenieResult:
    """Send a natural-language question to Genie and return structured result.

    Parameters
    ----------
    question:
        User's question in natural language.
    _agent:
        For testing you can inject a pre-configured GenieAgent. Defaults to the
        module-level one.

    Returns
    -------
    GenieResult
        Structured result with answer, SQL, and DataFrame.
    """

    agent = _agent or _genie

    # Enhance questions with Panda Restaurant context
    enhanced_question = f"""
Context: You are analyzing data for Panda Restaurant Group, a fast-casual restaurant chain. 
The data includes store performance, P&L metrics, operational data, and regional comparisons.

Question: {question}

If you execute a SQL query, please include the query in your response.
If you return data, please format it clearly.
Focus on actionable insights for restaurant operations and management.
"""

    try:
        result = agent.invoke({"messages": [{"role": "user", "content": enhanced_question}]})

        # Extract content from result
        content = ""
        if isinstance(result, dict):
            messages = result.get("messages", [])
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("content"):
                    content = msg["content"]
                    break
                elif hasattr(msg, 'content'):  # Handle AIMessage objects
                    content = str(msg.content)
                    break
        else:
            # Handle direct AIMessage or similar objects
            if hasattr(result, 'content'):
                content = str(result.content)
        
        if not content:
            return GenieResult(
                answer="No response from Genie",
                sql="",
                df=pd.DataFrame()
            )
        
        # Try to extract SQL and data from natural language response
        sql = extract_sql_from_text(content)
        df = extract_data_from_text(content)
        
        return GenieResult(
            answer=content,
            sql=sql,
            df=df
        )
        
    except Exception as e:
        return GenieResult(
            answer=f"Error calling Genie: {str(e)}",
            sql="",
            df=pd.DataFrame()
        )

def ask_genie(question: str, *, _agent: Optional[GenieAgent] = None) -> str:
    """Backward-compatible function that returns just the answer text."""
    result = ask_genie_structured(question, _agent=_agent)
    return result.answer

def get_genie_health_status() -> str:
    """
    Check if Genie is accessible and working.
    
    Returns:
        Status string: "healthy", "error: <message>", or "unknown"
    """
    try:
        # Simple test query to check if Genie is responsive
        test_result = ask_genie("Hello, can you help me with Panda Restaurant data?")
        if test_result and len(test_result.strip()) > 0:
            return "healthy"
        else:
            return "error: No response from Genie"
    except Exception as e:
        return f"error: {str(e)}"
