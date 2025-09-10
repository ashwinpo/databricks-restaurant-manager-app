# Panda Restaurant Group - AI-Driven P&L Analytics Dashboard

A complete AI-powered P&L analytics solution that uses **Databricks Genie** for data extraction and **Claude** for intelligent insights generation, paired with a modern React dashboard for store managers.

## 🎯 What This Does

**Problem**: Store managers need actionable P&L insights but don't have time to dig through complex financial data.

**Solution**: 
1. **Databricks Genie** extracts quantitative data via text-to-SQL
2. **Claude AI** identifies the most important business insights
3. **React Dashboard** presents insights in a manager-friendly interface
4. **Easy Customization** - add new questions or change analysis focus without coding

## 🚀 Complete Setup Guide

Follow these steps to get the full system running:

### Step 1: Import the Notebook to Databricks

1. **Download the notebook**: `panda_pnl_insights_notebook.py`
2. **Open Databricks workspace** → **Workspace** → **Import**
3. **Upload the file** and save it in your workspace
4. **Open the notebook** in Databricks

### Step 2: Configure Your Environment

1. **Find the Configuration Section** (right at the top of the notebook)
2. **Update these settings**:
   ```python
   GENIE_SPACE_ID = "your-genie-space-id"        # ← Your Genie Space ID
   LLM_ENDPOINT_NAME = "your-claude-endpoint"     # ← Your Claude endpoint name
   STORE_NUMBER = "1619"                          # ← Store to analyze
   PERIOD_ID = "202507"                          # ← Period to analyze
   ```

### Step 3: Run the Notebook

1. **Run all cells** in the notebook (Ctrl+Shift+Enter)
2. **Wait for completion** - it will:
   - Extract P&L data using Genie
   - Generate a comprehensive narrative report
   - Use Claude to create 5 key insights for the dashboard
   - Output JSON configuration at the end

3. **Copy the final JSON output** (look for "FRONTEND INTEGRATION - COPY THIS JSON:")

### Step 4: Update the Frontend Configuration

1. **Navigate to**: `frontend/public/pnl-insights-config.json`
2. **Replace the entire contents** with the JSON you copied from the notebook
3. **Save the file**

### Step 5: Set Up the Backend

1. **Create a virtual environment**:
   ```bash
   cd backend
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file** (`.env` in project root):
   ```bash
   DB_HOST=https://your-workspace.cloud.databricks.com
   DB_PAT=your_personal_access_token
   DATABRICKS_WAREHOUSE_ID=your_warehouse_id
   GENIE_SPACE_ID=your_genie_space_id
   LLM_ENDPOINT_NAME=your-claude-endpoint
   ```

4. **Start the backend**:
   ```bash
   python app.py
   ```
   ✅ Backend should be running at `http://localhost:8000`

### Step 6: Set Up the Frontend

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```
   ✅ Frontend should be running at `http://localhost:5173`

### Step 7: Test Locally

1. **Open your browser** to `http://localhost:5173`
2. **Check the P&L Insights tab** - you should see your AI-generated insights
3. **Test the Genie Chat** to make sure backend connectivity works
4. **Verify the insights** match what was generated in the notebook

### Step 8: Deploy to Databricks

Follow the detailed deployment guide in [`databricks_frontend_deployment.md`](databricks_frontend_deployment.md):

1. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Commit the `dist/` folder** to your repository:
   ```bash
   git add frontend/dist -f
   git commit -m "Add production build"
   git push
   ```

3. **Update your FastAPI app** to serve static files (see deployment guide)

4. **Deploy to Databricks Apps**:
   - Push code to Databricks Repo
   - Click **Deploy App** in Databricks
   - Your dashboard will be live!

## 🛠 Customizing the Analysis

### Adding New Genie Questions

Want to add monthly trends analysis? It's super easy:

1. **Open the notebook**
2. **Find the `GENIE_QUESTIONS` section**
3. **Uncomment the example questions** or add your own:
   ```python
   "monthly_trends": {
       "question": f"""For store {"{store_number}"}, show me monthly revenue trends:
   1. Compare current period {"{period}"} with previous 3 months
   2. Show Net Sales by month with growth percentages
   3. Identify seasonal patterns or trends
   Filter for Type = 'Net Sales' and show monthly comparison.""",
       "description": "Monthly revenue trends and seasonality",
       "category": "Trends"
   }
   ```
4. **Run the notebook** - Claude will automatically analyze the new data!

### Customizing Claude Prompts

Want to change the analysis focus? Easy:

1. **Find the `CLAUDE_PROMPTS` section** in the notebook
2. **Modify the prompts** to change tone, focus, or output format
3. **Example**: Change from cost-focus to growth-focus by editing the prompt text

## 📁 Project Structure

```
panda-pnl-app/
├── panda_pnl_insights_notebook.py    # 🧠 Main AI analysis notebook
├── frontend/
│   ├── src/                          # React components
│   ├── public/
│   │   └── pnl-insights-config.json  # 📊 AI-generated insights config
│   └── dist/                         # Built assets (for deployment)
├── backend/
│   ├── app.py                        # FastAPI server
│   ├── genie_client_local.py         # Genie integration
│   └── requirements.txt              # Python dependencies
└── databricks_frontend_deployment.md # 🚀 Deployment guide
```

## 🎨 Key Features

### Two-Stage AI Architecture
- **Stage 1 (Genie)**: Reliable quantitative data extraction via text-to-SQL
- **Stage 2 (Claude)**: Intelligent insight identification and natural language generation

### Manager-Friendly Dashboard
- **Clean UI**: Designed for store managers, not analysts
- **Actionable Insights**: Specific recommendations with timeframes
- **Mobile Ready**: Optimized for iPad usage
- **Panda Branding**: Professional appearance with brand colors

### Easy Customization
- **No Code Changes**: Add questions by editing configuration
- **Automatic Integration**: New questions flow to Claude analysis automatically
- **Flexible Prompts**: Customize analysis focus and tone
- **Example Questions**: Ready-to-use templates for common analyses

## 🔧 Troubleshooting

### Notebook Issues
- **Genie connection fails**: Check your `GENIE_SPACE_ID` and permissions
- **Claude endpoint error**: Verify your `LLM_ENDPOINT_NAME` is correct
- **No insights generated**: Ensure your store/period has data in the P&L table

### Frontend Issues
- **Blank insights**: Make sure you copied the JSON correctly to `pnl-insights-config.json`
- **Config not loading**: Check browser console for errors, verify JSON syntax
- **Old insights showing**: Hard refresh the browser (Cmd+Shift+R)

### Backend Issues
- **Connection errors**: Verify your `.env` file has correct Databricks credentials
- **Import errors**: Make sure virtual environment is activated and dependencies installed
- **CORS errors**: Check that backend is running on port 8000

### Deployment Issues
- **Static files not serving**: Ensure `dist/` folder is committed to repository
- **App not updating**: Click **Restart** in Databricks App UI
- **404 errors**: Check that all API routes are defined before static file mount

## 📞 Support

This system demonstrates the **correct approach** for AI-driven P&L analysis:
- ✅ Deterministic data extraction (Genie)
- ✅ Creative insight generation (Claude)
- ✅ Secure - no raw data exposure to LLMs
- ✅ Flexible and customizable
- ✅ Production-ready deployment

For technical questions, refer to the detailed deployment guide and configuration examples in the notebook.

---

**Ready to transform your P&L analysis with AI?** 🚀

Start with Step 1 above and you'll have intelligent insights running in minutes!