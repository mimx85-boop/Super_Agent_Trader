# Quick Reference Guide - Super Agent Trader

## 1. DAILY AUTOMATION - How It Works

### Automatically Runs Every Day @ 8:00 AM
**Pipeline Flow:**
```
DataAgent (IBKR) → MLAgent (Train) → PredictAgent (Predict) → Reports
        ↓
   S3 Storage
        ↓
   Analytics & Visualizations
```

### To Run Manually (anytime):
```bash
python run_daily_pipeline.py
```

### To Modify Schedule:
```powershell
# Edit time from 8:00 AM to your preferred time
# Run as Administrator
.\setup_scheduler.ps1
```

### To View Scheduled Tasks:
```powershell
Get-ScheduledTask -TaskName "SuperAgentTrader_DailyPipeline" | Get-ScheduledTaskInfo
```

---

## 2. DATA VISUALIZATION - Simplest S3 Solution

### Dashboard Location:
```
visualizations/index.html
```

### How to Use:
1. **Local:** Open `visualizations/index.html` in your browser
2. **S3:** Upload `visualizations/` to S3, then share the S3 URL
3. **No backend needed** - all charts are static HTML files

### Interactive Charts Available:
- **Candlestick Charts** - AAPL, MSFT, TSLA with volume
- **Returns Comparison** - Bar chart across symbols
- **Volatility Metrics** - Risk comparison
- **Correlation Heatmap** - Price relationships

### Why Plotly?
✅ Lightweight (5MB per chart)
✅ No server needed
✅ S3-compatible (upload .html files)
✅ Interactive (hover, zoom, pan)
✅ Works offline

---

## 3. ANALYTICS REPORTS - Today's Data

### Latest Reports (Nov 28, 2025):

**Performance Summary:**
```
AAPL: +10.53% return, 1.19% volatility, Sharpe: 4.721
MSFT: -4.20% return, 1.36% volatility, Sharpe: -1.622
TSLA: -2.08% return, 3.16% volatility, Sharpe: -0.121
```

**Price Correlations:**
```
AAPL ↔ MSFT: -0.405 (negative)
AAPL ↔ TSLA: -0.200 (weak negative)
MSFT ↔ TSLA: +0.716 (strong positive)
```

### Report Files:
- `logs/analytics_data_*.json` - Complete metrics (programmatic access)
- `logs/analytics_symbols_*.csv` - Symbol analysis (spreadsheet friendly)
- `logs/analytics_report_*.log` - Execution trace (debugging)

### To Generate New Reports:
```bash
python utils/analytics_reporter.py
```

---

## 4. HANDOFF DOCUMENTATION

### Word Document:
```
Super_Agent_Trader_Handoff.docx
```

**Contains 13 Sections:**
1. Executive Summary
2. Project Overview
3. System Architecture
4. Configuration Details
5. Daily Automation Setup
6. Analytics & Reporting
7. Data Visualizations
8. File Structure
9. Current System State
10. Troubleshooting Guide
11. Recommended Next Steps
12. Code References
13. Handoff Information

### For Next Agent:
This document is **production-ready** and explains everything needed to:
- Understand the system
- Run it manually or on schedule
- Troubleshoot issues
- Extend with new features
- Plan next development phases

---

## 5. COMMON TASKS

### View Latest Trading Data:
```python
from utils.s3_client import S3Client

s3 = S3Client()
df = s3.read_parquet('raw/AAPL/[latest].parquet')
print(df.head())
```

### Check S3 Contents:
```bash
python query_s3.py
```

### Generate Visualizations:
```bash
python utils/trading_dashboard.py
```

### Run Full Pipeline Once:
```bash
python run_daily_pipeline.py
```

### Check Scheduled Task Status:
```powershell
Get-ScheduledTask -TaskName "SuperAgentTrader_DailyPipeline" | Format-List
```

---

## 6. KEY METRICS EXPLAINED

| Metric | What It Means | Good Range |
|--------|---------------|-----------|
| **Return** | Total price change over 30 days | +5% to +20% |
| **Volatility** | Daily price fluctuation | <2% is stable, >3% is risky |
| **Sharpe Ratio** | Risk-adjusted return | >1.0 is good, >2.0 is great |
| **Win Rate** | % of up days vs down days | >50% is positive |
| **Correlation** | Price movement relationship | 0.7+ = moves together |

---

## 7. TROUBLESHOOTING

### "IBKR connection failed"
- Ensure TWS Gateway is running on 127.0.0.1:7496
- Check IBKR Workstation is logged in

### "S3 access denied"
- Verify AWS credentials are configured
- Check bucket name in config.yaml (stock-trade-data-2025)
- Verify IAM permissions for S3 access

### "Dashboard won't open"
- Ensure you're opening visualizations/index.html (not double-clicking)
- Try a different browser (Chrome, Edge, Firefox)
- Check that Plotly CDN is accessible

### "Task Scheduler job failed"
- Check Event Viewer > Windows Logs > System
- Verify Python path: `C:\Users\mimx8\Super_Agent_Trader\venv\Scripts\python.exe`
- Check working directory is correct

---

## 8. PROJECT STRUCTURE

```
Super_Agent_Trader/
├── agents/
│   ├── super_agent.py          ← Main orchestrator
│   ├── data_agent.py            ← Fetch data
│   ├── ml_agent.py              ← Train models
│   └── predict_agent.py         ← Generate predictions
├── utils/
│   ├── s3_client.py             ← S3 I/O
│   ├── ibkr_client.py           ← IBKR API
│   ├── analytics_reporter.py    ← Reports
│   ├── trading_dashboard.py     ← Visualizations
│   └── features.py              ← Feature engineering
├── logs/                         ← Daily logs & reports
├── visualizations/              ← Interactive dashboards
├── config.yaml                  ← Configuration
├── run_daily_pipeline.py        ← Daily runner
├── setup_scheduler.ps1          ← Scheduler setup
└── Super_Agent_Trader_Handoff.docx ← Full documentation
```

---

## 9. NEXT STEPS FOR DEVELOPMENT

### Immediate (This Week):
- Monitor daily reports for consistency
- Validate predictions against actual market data
- Fine-tune model parameters

### Short Term (1-2 Weeks):
- Add more technical indicators
- Implement email alerts
- Create performance benchmarks

### Medium Term (1-3 Months):
- Add portfolio-level analysis
- Implement actual trading (paper first)
- Deploy Redshift analytics

---

## 10. USEFUL COMMANDS

```bash
# View latest data
python query_s3.py

# Generate analytics
python utils/analytics_reporter.py

# Create visualizations
python utils/trading_dashboard.py

# Run pipeline manually
python run_daily_pipeline.py

# Run tests
pytest tests/ -v

# View scheduled tasks
Get-ScheduledTask | Where-Object {$_.TaskName -like "*SuperAgent*"}
```

---

**System Status:** ✅ Production Ready
**Last Updated:** November 28, 2025
**All systems operational and fully automated**
