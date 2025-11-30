# GitHub Actions + EC2 Setup Checklist

## Phase 1: GitHub Actions Setup ✅ (Already Done)
- [x] Created `.github/workflows/daily-pipeline.yml`
- [x] Created `GITHUB_ACTIONS_SETUP.md`

## Phase 2: Your Tasks - GitHub (5 min)

- [ ] **Push code to GitHub**
  ```powershell
  cd c:\Users\mimx8\Super_Agent_Trader
  git add .
  git commit -m "Add GitHub Actions workflow"
  git push
  ```

- [ ] **Create GitHub Secrets** (Settings → Secrets and variables → Actions)
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `AWS_REGION` = `us-east-1`
  - [ ] `S3_BUCKET` = `stock-trade-data-2025`

## Phase 3: AWS EC2 Setup (30-45 min)

Follow: `EC2_TWS_SETUP.md`

### Security Group
- [ ] Create security group `ibkr-tws-gateway`
- [ ] Add inbound rule: TCP 7496 from 0.0.0.0/0
- [ ] Add inbound rule: SSH 22 from your IP

### EC2 Instance
- [ ] Launch t2.micro Ubuntu 22.04 LTS
- [ ] Create/download key pair (`.pem` file)
- [ ] **Note EC2 public IP:** `_________________`

### Install TWS Gateway
- [ ] SSH into EC2
- [ ] Install Java: `sudo apt install -y default-jre wget`
- [ ] Download TWS Gateway
- [ ] Download & install IBC

### Configure IBC
- [ ] Create `~/ibc/config/config.ini`
- [ ] Add IBKR credentials (username, password)
- [ ] Create systemd service file
- [ ] Start service: `sudo systemctl start tws-gateway`

### Verify Connection
- [ ] Test from EC2: `netstat -tlnp | grep 7496`
- [ ] Test from Windows: `Test-NetConnection -ComputerName 54.123.45.67 -Port 7496`
- [ ] Test with Python (ib_insync)

## Phase 4: Update GitHub Secrets (2 min)

- [ ] Add secret: `IBKR_HOST` = `54.123.45.67` (your EC2 public IP)
- [ ] Add secret: `IBKR_PORT` = `7496`

## Phase 5: Test & Verify (10 min)

- [ ] Go to GitHub → Actions → Run workflow manually
- [ ] Monitor logs in real-time
- [ ] Verify pipeline completes successfully
- [ ] Check S3 bucket for uploaded logs
- [ ] Verify AAPL/MSFT/TSLA data in S3

## Phase 6: Cleanup (5 min)

- [ ] Disable Windows Task Scheduler (optional)
  ```powershell
  Disable-ScheduledTask -TaskName "SuperAgentTrader_DailyPipeline"
  ```
- [ ] Test next day at 8:00 AM UTC

---

## Time Estimate

| Phase | Time |
|-------|------|
| GitHub Push | 5 min |
| EC2 Setup | 45 min |
| Testing | 10 min |
| **Total** | **1 hour** |

---

## Support Documents

- 📄 `GITHUB_ACTIONS_SETUP.md` - GitHub Actions guide
- 📄 `EC2_TWS_SETUP.md` - EC2 + TWS Gateway setup
- 📄 `QUICK_REFERENCE.md` - Quick project reference

---

## Questions?

- **GitHub Actions issues?** See `GITHUB_ACTIONS_SETUP.md` troubleshooting
- **EC2/TWS issues?** See `EC2_TWS_SETUP.md` troubleshooting
- **Need help?** Check GitHub Actions logs in real-time

---

**Status:** Ready for Phase 2 ✅

Next step: Push code to GitHub and create secrets.
