# ⚡ Quick Reference Card

## 🎯 6 Steps to Automate Your Pipeline

```
┌─────────────────────────────────────────────────────┐
│  STEP 1: Push Code (5 min)                         │
├─────────────────────────────────────────────────────┤
│  git add .                                          │
│  git commit -m "Add GitHub Actions"                 │
│  git push origin main                               │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│  STEP 2: GitHub Secrets (5 min)                    │
├─────────────────────────────────────────────────────┤
│  Settings → Secrets and variables → Actions         │
│  Add: AWS_ACCESS_KEY_ID                             │
│  Add: AWS_SECRET_ACCESS_KEY                         │
│  Add: AWS_REGION (us-east-1)                        │
│  Add: S3_BUCKET (stock-trade-data-2025)             │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│  STEP 3: AWS EC2 Setup (45 min)                    │
├─────────────────────────────────────────────────────┤
│  Read: EC2_TWS_SETUP.md                             │
│  Create security group (port 7496)                  │
│  Launch t2.micro Ubuntu instance                    │
│  Install TWS Gateway & IBC                          │
│  Configure auto-login                               │
│  Note: Your EC2 IP (54.123.45.67)                   │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│  STEP 4: IBKR Secrets (2 min)                      │
├─────────────────────────────────────────────────────┤
│  Add: IBKR_HOST (your EC2 IP)                       │
│  Add: IBKR_PORT (7496)                              │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│  STEP 5: Test Workflow (10 min)                    │
├─────────────────────────────────────────────────────┤
│  GitHub → Actions tab                               │
│  Click "Run workflow"                               │
│  Watch logs in real-time                            │
│  Verify success ✓                                   │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│  STEP 6: Verify Results (5 min)                    │
├─────────────────────────────────────────────────────┤
│  AWS S3 → stock-trade-data-2025                     │
│  Check: raw/AAPL/, raw/MSFT/, raw/TSLA/             │
│  Check: logs/ folder                                │
│  Success! ✓                                         │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│  AUTOMATIC FROM NOW ON                             │
├─────────────────────────────────────────────────────┤
│  Every day at 8:00 AM UTC:                          │
│  • GitHub Actions triggers                          │
│  • EC2 connects to IBKR                             │
│  • Data fetched → Models trained → Results uploaded │
│  • Your computer can be OFF ✓                       │
└─────────────────────────────────────────────────────┘
```

---

## 📝 Commands You'll Need

### Git Commands
```powershell
git add .
git commit -m "Add GitHub Actions"
git push origin main
```

### AWS Security Group
- Protocol: TCP
- Port: 7496
- Source: 0.0.0.0/0

### EC2 Instance
- AMI: Ubuntu 22.04 LTS
- Type: t2.micro
- Region: us-east-1

### EC2 SSH
```bash
ssh -i key.pem ubuntu@54.123.45.67
```

### Test Connection
```powershell
Test-NetConnection -ComputerName 54.123.45.67 -Port 7496
```

---

## 🔐 Secrets Checklist

### GitHub Secrets (6 total)

**AWS Credentials:**
- [ ] AWS_ACCESS_KEY_ID
- [ ] AWS_SECRET_ACCESS_KEY
- [ ] AWS_REGION
- [ ] S3_BUCKET

**IBKR Connection:**
- [ ] IBKR_HOST
- [ ] IBKR_PORT

---

## ⏱️ Timeline

| Step | Duration |
|------|----------|
| 1. Git push | 5 min |
| 2. GitHub secrets | 5 min |
| 3. EC2 setup | 45 min |
| 4. IBKR secrets | 2 min |
| 5. Test | 10 min |
| 6. Verify | 5 min |
| **TOTAL** | **1 hour** |

---

## 🔄 Daily Workflow (Automatic)

```
8:00 AM UTC
    ↓
GitHub Actions Triggered
    ↓
Checkout code
Install dependencies
Create config
    ↓
Connect to EC2:7496
    ↓
Connect to IBKR
    ↓
Fetch: AAPL, MSFT, TSLA (30 days)
    ↓
Train: ML models
    ↓
Generate: Predictions
    ↓
Upload: S3 + Logs
    ↓
Complete ✓
```

---

## 📊 Architecture

```
Your Computer (Can be OFF)
    │
    ├─→ GitHub (stores code)
    │
    └─→ GitHub Actions (trigger at 8:00 AM UTC)
            │
            ├─→ AWS EC2 (runs TWS Gateway)
            │       │
            │       └─→ IBKR (fetches data)
            │
            └─→ AWS S3 (stores results)
```

---

## ✅ Success Indicators

- ✓ GitHub code pushed
- ✓ 6 secrets created
- ✓ EC2 running with TWS
- ✓ First test passed
- ✓ Files in S3
- ✓ Tomorrow's auto-run succeeds

---

## 🆘 Troubleshooting

| Error | Solution |
|-------|----------|
| "Connection refused" | Check EC2 security group port 7496 |
| "Auth failed" | Verify IBKR credentials in EC2 |
| "Timeout" | Increase timeout-minutes in workflow |
| "S3 access denied" | Check AWS IAM permissions |
| "Can't SSH to EC2" | Check key.pem permissions: `chmod 400 key.pem` |

---

## 📁 Files Reference

```
.github/workflows/
└── daily-pipeline.yml ← Main workflow

Root:
├── NEXT_STEPS.md ← Start here
├── SETUP_CHECKLIST.md
├── GITHUB_ACTIONS_SETUP.md
├── EC2_TWS_SETUP.md ← For EC2
├── COMPLETE_SETUP_SUMMARY.md
├── FILES_AND_GUIDES.md
└── README_SETUP_FINAL.md
```

---

## 🎯 Your Next Action

**→ Open `NEXT_STEPS.md` and start Step 1**

---

## 💡 Quick Tips

1. **Time Zone:** 8:00 AM UTC (adjust cron in workflow if needed)
2. **Cost:** Free first year, then ~$10-15/month
3. **Reliability:** 99.9% uptime guarantee from AWS
4. **Monitoring:** Check GitHub Actions dashboard
5. **Scalability:** Can add more symbols/models without issues

---

## 📞 Getting Help

- **GitHub issues?** → GITHUB_ACTIONS_SETUP.md
- **EC2 issues?** → EC2_TWS_SETUP.md
- **General questions?** → COMPLETE_SETUP_SUMMARY.md
- **Workflow logs?** → GitHub.com → Actions tab (real-time)

---

**Status: READY TO GO** 🚀

**Now:** Open NEXT_STEPS.md and begin!
