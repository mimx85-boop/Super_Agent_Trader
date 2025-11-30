# GitHub Actions Setup Guide

## What I've Done For You ✅

I've created a GitHub Actions workflow file that will:
- Run your daily pipeline automatically at **8:00 AM UTC** every day
- Work even when your computer is powered off
- Upload logs to S3 for monitoring
- Notify you if anything fails
- Allow manual trigger from GitHub Actions tab

**Workflow Location:** `.github/workflows/daily-pipeline.yml`

## What You Need to Do 🚀

### Step 1: Push Code to GitHub

Make sure your repository is on GitHub. If not:
```powershell
cd c:\Users\mimx8\Super_Agent_Trader
git init
git add .
git commit -m "Initial commit: Super Agent Trader"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Super_Agent_Trader.git
git push -u origin main
```

### Step 2: Add GitHub Secrets

Go to: **GitHub.com** → Your Repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets one by one:

| Secret Name | Value | Example |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | `wJal...` |
| `IBKR_HOST` | IBKR connection host | `127.0.0.1` or your remote IP |
| `IBKR_PORT` | IBKR connection port | `7496` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `S3_BUCKET` | S3 bucket name | `stock-trade-data-2025` |

**⚠️ IMPORTANT:**
- Keep these secrets private
- Never commit them to the repository
- GitHub Actions automatically injects them at runtime

### Step 3: Modify IBKR Connection (If Remote)

**Current issue:** The workflow runs on GitHub's servers (not your computer).

**If you're running IBKR locally on your computer:**
- ❌ GitHub can't reach `127.0.0.1` (localhost)
- ❌ Need to use a VPN or proxy

**Solutions:**

**Option A: Use IBrokers TWS Gateway on a Cloud Server (Recommended)**
1. Set up TWS Gateway on an EC2 instance or similar
2. Update `IBKR_HOST` secret to the server's public IP
3. Add firewall rules to allow port 7496 from GitHub

**Option B: Use a Local Tunnel Service**
```powershell
# Install ngrok: https://ngrok.com/
ngrok tcp 7496
# This exposes your local port to the internet
# Use the ngrok URL in IBKR_HOST secret
```

**Option C: Run on Self-Hosted Runner**
- If you want to run on your local machine instead of GitHub servers
- More complex setup, but avoids IBKR connectivity issues

### Step 4: Test the Workflow

1. Go to: **GitHub.com** → Your Repo → **Actions** tab
2. Click **"Daily Super Agent Trading Pipeline"**
3. Click **"Run workflow"** → **"Run workflow"** button
4. Monitor the execution

Watch the logs in real-time to verify:
- ✅ Dependencies install
- ✅ Config file created
- ✅ IBKR connection established
- ✅ Pipeline completes
- ✅ Logs uploaded to S3

### Step 5: Disable Windows Task Scheduler (Optional)

Once GitHub Actions is working:
```powershell
# Run as Administrator
Disable-ScheduledTask -TaskName "SuperAgentTrader_DailyPipeline"
```

## Timezone Note ⏰

The workflow is set to **8:00 AM UTC**.

**Convert to your timezone:**
- **EST (UTC-5):** 3:00 AM
- **CST (UTC-6):** 2:00 AM
- **PST (UTC-8):** 12:00 AM (Midnight)
- **CET (UTC+1):** 9:00 AM

To change the time, edit `.github/workflows/daily-pipeline.yml`:
```yaml
cron: '30 13 * * *'  # Change to 1:30 PM UTC, etc.
```

## Monitoring & Troubleshooting 🔍

### View Logs
- GitHub.com → Repo → Actions → Latest run → Click step for details

### Common Issues

**❌ "IBKR connection failed"**
- IBKR_HOST is unreachable from GitHub
- Solution: Use VPN, proxy, or cloud-hosted TWS Gateway

**❌ "AWS credentials invalid"**
- Check AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- Verify they have S3 permissions

**❌ "Timeout after 30 minutes"**
- Pipeline taking too long
- Solution: Increase `timeout-minutes` in workflow file

## Next Steps After Setup ✨

1. ✅ Verify first automated run at 8:00 AM tomorrow
2. ✅ Check S3 bucket for logs and data
3. ✅ Monitor Redshift for analytics updates
4. ✅ Review predictions in dashboard

---

**Questions?** Check the GitHub Actions documentation: https://docs.github.com/en/actions
