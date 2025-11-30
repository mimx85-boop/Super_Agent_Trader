# Setup Flow Diagram & Next Steps

## 🗂️ File Organization

```
Your Repo
├── .github/workflows/
│   └── daily-pipeline.yml ← GitHub Actions workflow
├── agents/
│   ├── data_agent.py
│   ├── ml_agent.py
│   ├── predict_agent.py
│   └── super_agent.py
├── utils/
│   ├── ibkr_client.py
│   ├── s3_client.py
│   └── ...
├── config.yaml ← Will be auto-generated from secrets
├── run_daily_pipeline.py
├── requirements.txt
├── SETUP_CHECKLIST.md ← YOUR CHECKLIST
├── GITHUB_ACTIONS_SETUP.md ← GitHub guide
├── EC2_TWS_SETUP.md ← AWS EC2 guide
└── COMPLETE_SETUP_SUMMARY.md ← This summary
```

---

## 📋 Your Exact Next Steps (In Order)

### ⏱️ STEP 1: GitHub Push (5 minutes)
**Time: Now**

```powershell
cd c:\Users\mimx8\Super_Agent_Trader

# Check status
git status

# Add all changes (including new workflow file)
git add .

# Commit
git commit -m "Add GitHub Actions workflow and setup documentation"

# Push to GitHub
git push origin main
```

**Verify:** Go to GitHub.com → Your Repo → Should see new files

---

### ⏱️ STEP 2: Create GitHub Secrets (5 minutes)
**Time: After Step 1**

1. Go to: `github.com/YOUR_USERNAME/Super_Agent_Trader`
2. Click **Settings** (top right)
3. Left sidebar → **Secrets and variables** → **Actions**
4. Click **New repository secret** button

**Add these 4 AWS secrets one by one:**

| Name | Value | Example |
|------|-------|---------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | `AKIA2ZPFX...` |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | `wJal...` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `S3_BUCKET` | S3 bucket name | `stock-trade-data-2025` |

**⚠️ Important:**
- One secret at a time
- Click "Add secret" after each
- Don't include quotes

---

### ⏱️ STEP 2B: Add Email Notification Secrets (5 minutes)
**Time: After Step 2 AWS secrets**

**Email notifications will be sent to: mimx85@msn.com**

Add these 5 email secrets (one at a time):

| Name | Value | Example |
|------|-------|---------|
| `EMAIL_SERVER` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USERNAME` | Your email address | `your@gmail.com` |
| `EMAIL_PASSWORD` | App password | `xxxx xxxx xxxx xxxx` |
| `EMAIL_FROM` | From address | `your@gmail.com` |

**Which Email Provider?**

- **Gmail (Recommended):** Get app password from myaccount.google.com/apppasswords
- **Outlook:** Use app password if 2FA enabled
- **Yahoo:** Get app password from Account Security
- **Other:** Use your SMTP settings

**⚠️ Important:**
- For Gmail with 2FA: Use app password (16-char code), NOT regular password
- For Outlook: Use app password if 2FA enabled
- For Yahoo: Must use app password
- Never use your regular password with 2FA enabled

**Detailed Guide:** See `EMAIL_NOTIFICATION_SETUP.md`

---

### ⏱️ STEP 3: AWS EC2 Setup (45 minutes)
**Time: After Step 2B (or do this in parallel)**

**Open: `EC2_TWS_SETUP.md` and follow it exactly**

**Estimated timeline:**
- 5 min: Create security group
- 5 min: Launch EC2 instance
- 10 min: SSH connection & Java install
- 10 min: Download & install TWS
- 5 min: Configure IBC
- 5 min: Test connection

**At the end of this step, you'll have:**
- ✅ EC2 instance running (public IP: `54.123.45.67`)
- ✅ TWS Gateway listening on port 7496
- ✅ IBC auto-login configured

**IMPORTANT:** Note your EC2 public IP address!
```
My EC2 Public IP: ___________________
```

---

### ⏱️ STEP 4: Add IBKR Secrets to GitHub (2 minutes)
**Time: After Step 3**

1. Go back to GitHub → Settings → Secrets
2. Add 2 more secrets:

| Name | Value |
|------|-------|
| `IBKR_HOST` | Your EC2 public IP (e.g., `54.123.45.67`) |
| `IBKR_PORT` | `7496` |

---

### ⏱️ STEP 5: Test the Workflow (10 minutes)
**Time: After Step 4**

1. Go to: `github.com/YOUR_USERNAME/Super_Agent_Trader`
2. Click **Actions** tab (top)
3. Left sidebar: Click **"Daily Super Agent Trading Pipeline"**
4. Click **"Run workflow"** dropdown (blue button)
5. Click **"Run workflow"** (in dropdown)
6. **Wait 30 seconds** for job to appear
7. Click the running job
8. Watch the logs scroll in real-time

**Expected success log:**
```
✓ Checkout code
✓ Set up Python 3.10
✓ Cache pip packages
✓ Install dependencies
✓ Create config from secrets
✓ Run daily pipeline
  - Connecting to IBKR at 54.123.45.67:7496
  - DataAgent: Fetching AAPL, MSFT, TSLA
  - MLAgent: Training models
  - PredictAgent: Generating predictions
✓ Upload logs to S3
✓ Send Email Notification - Success
```

**⚠️ Email Notification:**
- Watch for step: **"Send Email Notification - Success"** or **"Send Email Notification - Failure"**
- This step will send an email to: **mimx85@msn.com**
- Check your email in 1-2 minutes for detailed status report

**If you see errors:** Check `GITHUB_ACTIONS_SETUP.md` or `EMAIL_NOTIFICATION_SETUP.md` troubleshooting

---

### ✅ STEP 6: Verify Results (5 minutes)
**Time: After Step 5**

### 6A: Check GitHub Logs
1. Watch the workflow complete
2. All steps should show ✓ (green checkmarks)
3. Final step: "Send Email Notification - Success"

### 6B: Check Email ✉️
1. Open your email inbox
2. Look for email with subject: **"✅ Super Agent Trader Pipeline - SUCCESS"**
3. Verify it contains:
   - All ✓ steps passed
   - S3 file locations (raw/AAPL/, raw/MSFT/, raw/TSLA/)
   - Execution metrics
   - Next scheduled run time

**If no email after 3 minutes:**
- Check spam/junk folder
- Verify EMAIL_* secrets are correct
- See `EMAIL_NOTIFICATION_SETUP.md` troubleshooting

### 6C: Check S3 Files
1. Go to AWS → S3 → `stock-trade-data-2025` bucket
2. Check for new folders:
   - `raw/AAPL/` - Should have parquet files
   - `raw/MSFT/` - Should have parquet files
   - `raw/TSLA/` - Should have parquet files
   - `logs/` - Should have pipeline logs

**If files are there:** ✅ Everything is working!

---

### 🎉 STEP 7: Done! (Optional cleanup)

Optionally disable Windows Task Scheduler:

```powershell
# Run as Administrator
Disable-ScheduledTask -TaskName "SuperAgentTrader_DailyPipeline"
```

---

## 🔄 What Happens Next (Automatically)

Tomorrow at **8:00 AM UTC**, without you doing anything:

```
8:00 AM UTC
    ↓
GitHub Actions triggers
    ↓
Workflow starts on GitHub's server
    ↓
Connects to your EC2 instance
    ↓
EC2 connects to IBKR
    ↓
Fetches data → Trains models → Makes predictions
    ↓
Uploads results to S3
    ↓
Done! (Repeats daily forever)
```

**You don't need to do anything.**

---

## 🕐 Time Zones

The workflow runs at **8:00 AM UTC** daily.

**Convert to your timezone:**

| Timezone | Time |
|----------|------|
| UTC | 8:00 AM |
| EST (UTC-5) | 3:00 AM |
| CST (UTC-6) | 2:00 AM |
| MST (UTC-7) | 1:00 AM |
| PST (UTC-8) | 12:00 AM (Midnight) |
| CET (UTC+1) | 9:00 AM |
| IST (UTC+5:30) | 1:30 PM |
| SGT (UTC+8) | 4:00 PM |

**To change time:** Edit `.github/workflows/daily-pipeline.yml`, change `cron: '0 8 * * *'` to desired time.

---

## ✋ If You Get Stuck

**Check these in order:**

1. **Step 3 issues (EC2/TWS)?** → See `EC2_TWS_SETUP.md` troubleshooting
2. **Step 2 issues (GitHub)?** → See `GITHUB_ACTIONS_SETUP.md` troubleshooting
3. **Step 5 issues (workflow)?** → Look at GitHub Actions logs (real-time)

---

## 📊 Progress Tracker

Mark these off as you complete them:

- [ ] Step 1: Push code to GitHub
- [ ] Step 2: Create 4 GitHub secrets
- [ ] Step 3: Set up EC2 & TWS Gateway
- [ ] Step 4: Add 2 IBKR secrets
- [ ] Step 5: Test workflow (manual run)
- [ ] Step 6: Verify files in S3
- [ ] Step 7: (Optional) Disable Task Scheduler

**Total time:** ~1 hour

---

## 🎯 Success Checklist

You'll know it's working when ALL of these are true:

- ✅ GitHub Actions workflow ran successfully
- ✅ IBKR connection succeeded (no timeout errors)
- ✅ Data files appeared in S3 (raw/AAPL/, etc.)
- ✅ Logs were uploaded to S3
- ✅ No failure notifications

If all checkboxes are ✅, you're done!

---

**Ready? Start with Step 1!** 🚀
