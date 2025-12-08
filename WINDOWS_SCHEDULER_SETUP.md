# Windows Task Scheduler Setup - Quick Guide

## Overview
This sets up your Super Agent Trader pipeline to run automatically every day at 8:00 AM (configurable).

**Benefits:**
- ✅ Runs daily without manual intervention
- ✅ Your PC stays logged into IBKR naturally
- ✅ No EC2 costs
- ✅ Works even if GitHub is down
- ✅ Logs stored locally for debugging

---

## Step 1: Ensure Your PC Stays Awake

For the task to run, your PC must be powered on at the scheduled time (8:00 AM by default).

### Option A: Keep PC Running 24/7
- Leave your PC on overnight
- Enable "Never sleep" in Power Settings

### Option B: Wake at Scheduled Time
- Configure Windows to wake from sleep at 8:00 AM
- Requires BIOS support (check your PC's BIOS settings)

---

## Step 2: Create the Scheduled Task

### Run as Administrator
1. **Right-click PowerShell** on your taskbar
2. Click **"Run as Administrator"**
3. Accept the UAC prompt

### Run the Setup Script
```powershell
cd C:\Users\mimx8\Super_Agent_Trader
.\create_scheduled_task.ps1
```

### Expected Output
```
==========================================
SUCCESS - Task created!
==========================================
Task: Super Agent Trader Daily Pipeline
Folder: \Super Agent Trader
Schedule: Daily at 8:00
```

---

## Step 3: Verify Task Creation

### Option A: GUI
1. Press `Win + R`
2. Type `taskschd.msc` and press Enter
3. Expand **Task Scheduler Library**
4. Look for folder: **Super Agent Trader**
5. Inside: **Super Agent Trader Daily Pipeline**

### Option B: PowerShell
```powershell
Get-ScheduledTask -TaskName "Super Agent Trader Daily Pipeline" | Format-List
```

---

## Step 4: Test the Task Manually

### Run Now
1. Open Task Scheduler (`taskschd.msc`)
2. Find your task in: **Task Scheduler Library > Super Agent Trader**
3. Right-click the task
4. Click **"Run"**

### Check Results
- Task should execute immediately
- Check logs in: `C:\Users\mimx8\Super_Agent_Trader\logs\scheduled_runs\`
- Look for file: `scheduled_run_YYYYMMDD_HHMMSS.log`

---

## Step 5: Customize Schedule (Optional)

To change the run time, edit `create_scheduled_task.ps1`:

```powershell
[int]$Hour = 8,      # Change to desired hour (0-23)
[int]$Minute = 0,    # Change to desired minute (0-59)
```

Then re-run:
```powershell
.\create_scheduled_task.ps1
```

---

## Logs & Monitoring

### Log Location
`C:\Users\mimx8\Super_Agent_Trader\logs\scheduled_runs\`

### Log Files
Each run creates a file:
- `scheduled_run_20251207_080000.log` - Full execution transcript
- Includes all output from the pipeline

### View Recent Logs
```powershell
Get-ChildItem C:\Users\mimx8\Super_Agent_Trader\logs\scheduled_runs -File | Sort-Object LastWriteTime -Descending | Select-Object Name, LastWriteTime | head -10
```

---

## Troubleshooting

### Task Not Running
**Check:**
1. Is your PC on at scheduled time?
2. Is IBKR (TWS/Gateway) running?
3. Open Task Scheduler and check task history (right-click task → View History)

### Pipeline Fails
**Check:**
1. View the log file in `logs/scheduled_runs/`
2. Look for error messages
3. Run manually to see detailed errors:
   ```powershell
   python C:\Users\mimx8\Super_Agent_Trader\run_daily_pipeline.py
   ```

### Change Run Time
Edit and re-run `create_scheduled_task.ps1` with new time

---

## Disable/Enable Task

### Disable (temporarily pause)
```powershell
Disable-ScheduledTask -TaskName "Super Agent Trader Daily Pipeline" -TaskPath "\Super Agent Trader"
```

### Enable (resume)
```powershell
Enable-ScheduledTask -TaskName "Super Agent Trader Daily Pipeline" -TaskPath "\Super Agent Trader"
```

### Delete Task (permanent)
```powershell
Unregister-ScheduledTask -TaskName "Super Agent Trader Daily Pipeline" -TaskPath "\Super Agent Trader" -Confirm:$false
```

---

## Next Steps

✅ **Run the setup script** (Step 2)
✅ **Test manually** (Step 4)
✅ **Verify logs are created** (Logs section)

Your pipeline will now run automatically every day!
