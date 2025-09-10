# P&L Insights Configuration Guide

This guide explains how to update the P&L Insights dashboard with AI-generated insights from the Databricks notebook.

## Overview

The P&L Insights dashboard uses a **two-stage AI approach**:
1. **Databricks Genie** extracts quantitative data via text-to-SQL
2. **Claude** identifies key business insights and generates actionable recommendations

The dashboard loads these AI-generated insights dynamically from a JSON configuration file, making it easy to update with fresh insights without modifying code.

## Workflow

### 1. Run the Databricks Notebook

1. Open `panda_pnl_insights_notebook.py` in your Databricks workspace
2. Update the configuration variables:
   ```python
   GENIE_SPACE_ID = "your-genie-space-id"
   LLM_ENDPOINT_NAME = "your-claude-endpoint"
   STORE_NUMBER = "1619"  # or your target store
   PERIOD_ID = "202507"   # or your target period
   ```
3. Run all cells in the notebook
4. The notebook will:
   - Extract quantitative P&L data using Genie
   - Generate a narrative analysis report
   - Use Claude to identify the 5 most important insights
   - Output a JSON configuration - **copy this JSON**

### 2. Update the Frontend Configuration

1. Navigate to `frontend-v2/public/`
2. Replace the contents of `pnl-insights-config.json` with the JSON from the notebook
3. Save the file

### 3. Refresh the Dashboard

The dashboard will automatically load the new insights on the next page refresh or within 30 minutes (auto-refresh interval).

## AI-Driven Insight Generation

### Why This Approach?

**Traditional Method (❌ Problematic):**
- Pre-defined insight categories and templates
- Limited flexibility to adapt to different business scenarios
- Generic recommendations not tailored to specific situations

**Our Method (✅ Optimal):**
- **Stage 1**: Genie extracts reliable quantitative data via SQL
- **Stage 2**: Claude analyzes the data and identifies the most important business insights
- **Result**: Flexible, context-aware insights with actionable recommendations

### Benefits:
- **Dynamic Insight Discovery**: Claude identifies what matters most for each specific situation
- **Natural Language**: Human-friendly titles and recommendations
- **Business Context**: Understands restaurant operations and management priorities  
- **Actionable Focus**: Provides specific actions with timeframes and impact assessments

## Configuration File Structure

The `pnl-insights-config.json` file contains:

```json
{
  "metadata": {
    "store_number": "1619",
    "period": "202507", 
    "generated_at": "2025-09-10T12:00:00.000Z",
    "total_insights": 5,
    "methodology": "Databricks Genie + Claude Analysis"
  },
  "kpi_header": {
    "revenue": {
      "value": "-6.1%",
      "amount": "$320,433"
    },
    "profit": {
      "value": "-6.6%", 
      "amount": "$539,814"
    },
    "critical": {
      "value": "-18.6%",
      "amount": "$15,826",
      "label": "Beverage Sales"
    }
  },
  "insight_cards": [
    {
      "id": 1,
      "type": "critical",
      "priority": "urgent",
      "icon": "TrendingDown",
      "title": "Beverage Revenue Crisis",
      "description": "...",
      "metric": "-18.6%",
      "actualValue": "$15,826",
      "plannedValue": "$19,442", 
      "variance": "-$3,616",
      "recommendation": "...",
      "actions": [...],
      "impact": "Critical - largest revenue gap",
      "timeframe": "Immediate (Week 1)"
    }
    // ... more insight cards
  ]
}
```

## Card Types and Priorities

### Card Types
- `critical`: Red styling, urgent issues
- `alert`: Orange styling, important warnings  
- `opportunity`: Green styling, positive opportunities
- `insight`: Blue styling, general insights
- `performance`: Purple styling, performance metrics

### Priority Levels
- `urgent`: Immediate attention required
- `high`: High priority, address soon
- `medium`: Medium priority, monitor
- `low`: Low priority, informational

### Icons Available
- `TrendingDown`: Declining metrics
- `TrendingUp`: Improving metrics
- `DollarSign`: Financial metrics
- `BarChart3`: Performance charts
- `Target`: Goals and targets
- `AlertCircle`: Alerts and warnings
- `AlertTriangle`: Critical issues

## Error Handling

If the configuration file fails to load:
1. The dashboard displays an error message
2. Falls back to hardcoded demonstration data
3. Logs the error to browser console

## Best Practices

1. **Always validate JSON**: Ensure the notebook output is valid JSON before saving
2. **Test locally**: Refresh the dashboard to verify new insights load correctly
3. **Keep backups**: Save previous configurations before updating
4. **Monitor timing**: Allow 30 minutes for auto-refresh or manually refresh the page
5. **Check console**: Monitor browser console for any loading errors

## Troubleshooting

### Configuration Not Loading
- Verify `pnl-insights-config.json` is in the `public/` directory
- Check JSON syntax with a validator
- Look for browser console errors
- Ensure file permissions allow reading

### Missing Icons
- Verify icon names match the available icons list
- Check for typos in icon names
- Fallback icon (AlertTriangle) will be used for unknown icons

### Styling Issues
- Ensure `type` and `priority` values match expected options
- Check that all required fields are present in each card
- Verify currency formatting includes dollar signs

## Demo Mode

For demonstrations, you can:
1. Use the provided sample configuration
2. Modify values directly in the JSON file
3. Create multiple configuration files for different scenarios
4. Switch configurations by updating the filename in the component

This system provides a clean separation between data generation (notebook) and presentation (React app), making it easy for customers to maintain and update their insights dashboard.
