# AWS EC2 Setup Guide for IBKR TWS Gateway

## Overview

This guide walks you through setting up Interactive Brokers' TWS Gateway on an AWS EC2 instance so GitHub Actions can connect to it remotely.

**Architecture:**
```
GitHub Actions (Cloud)
        ↓
    Internet
        ↓
EC2 Instance (us-east-1)
        ↓
TWS Gateway (Port 7496)
        ↓
Interactive Brokers API
```

---

## Step 1: Launch EC2 Instance

### 1a. Create Security Group

1. Go to **AWS Console** → **EC2** → **Security Groups**
2. Click **Create security group**
   - **Name:** `ibkr-tws-gateway`
   - **Description:** "Allow TWS Gateway access for GitHub Actions"
   - **VPC:** Default

3. Add inbound rules:

| Type | Protocol | Port | Source | Reason |
|------|----------|------|--------|--------|
| Custom TCP | TCP | 7496 | 0.0.0.0/0 | GitHub Actions access* |
| SSH | TCP | 22 | Your IP | Your computer access |

**\*Note:** `0.0.0.0/0` allows anyone to connect. For production, use specific IPs.

4. Click **Create security group**

### 1b. Launch Instance

1. Go to **EC2** → **Instances** → **Launch instances**

2. **Choose AMI:**
   - Select **Ubuntu Server 22.04 LTS** (free tier eligible)

3. **Instance Type:**
   - Select **t2.micro** (free tier: 1 vCPU, 1 GB RAM)

4. **Configure:**
   - **Key pair:** Create new → Name: `ibkr-tws-gateway` → Download `.pem` file (save it!)
   - **Security group:** Select `ibkr-tws-gateway`
   - **Storage:** 30 GB (default, sufficient)

5. Click **Launch instance**

6. **Wait 2-3 minutes** for instance to start
   - Note the **Public IPv4 address** (e.g., `54.123.45.67`)

---

## Step 2: Install TWS Gateway on EC2

### 2a. Connect to EC2

**On Windows, use PowerShell:**

```powershell
# Convert .pem to .ppk for PuTTY (optional)
# Or use SSH directly (Windows 10+):

$keyPath = "C:\path\to\ibkr-tws-gateway.pem"
$ec2IP = "YOUR_EC2_PUBLIC_IP"  # e.g., 54.123.45.67

ssh -i $keyPath ubuntu@$ec2IP
```

If SSH connection fails, use **PuTTY**:
1. Download: https://www.putty.org/
2. Convert `.pem` to `.ppk` using PuTTYgen
3. Connect: Host = `ubuntu@54.123.45.67`, Auth → Private key = `.ppk`

### 2b. Update System

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y default-jre wget
```

### 2c. Download & Install TWS Gateway

```bash
# Create directory
mkdir -p ~/tws-gateway
cd ~/tws-gateway

# Download TWS Gateway (latest version)
wget https://download2.interactivebrokers.com/downloads/unixmacosx/latest-tws-latest-ubuntu-latest.sh

# Make executable and run
chmod +x *.sh
./latest-tws-latest-ubuntu-latest.sh
```

**During installation:**
- Accept license terms
- Use default installation path: `/root/Jts`
- Accept IBC defaults

### 2d. Install IBC (IB Controller)

IBC allows TWS to run headless (without GUI) and auto-login:

```bash
cd ~/tws-gateway

# Download IBC
wget https://github.com/IbcAlpha/IBC/releases/download/v997.17g/IBCLinux-997.17g.zip
unzip IBCLinux-997.17g.zip

# Create config directory
mkdir -p ~/ibc/config
```

### 2e. Configure IBC

Create file: `~/ibc/config/config.ini`

```bash
cat > ~/ibc/config/config.ini << 'EOF'
# IBC Config for TWS Gateway

# Your IBKR credentials
IbLoginId=YOUR_ACCOUNT_USERNAME
IbPassword=YOUR_ACCOUNT_PASSWORD
TradingMode=live
FIXLoginId=YOUR_ACCOUNT_USERNAME
FIXPassword=YOUR_ACCOUNT_PASSWORD

# Gateway settings
AcceptIncomingConnectionAccount=
AcceptNonBrokerageAccountWarning=yes
AllowBlindTrading=no
BindAddress=0.0.0.0
ConfirmOrderSubmit=no
FIXAcceptorPort=7497
FIXConnectionType=duplex
FIXLogPath=/var/log/ibc
FIXPasswordEncryption=base64
FIXSSLClientAuthType=
FIXSSLKeyStorePassword=
FIXSSLKeyStorePath=
FIXSSLKeyStoreType=JKS
FIXSSLVersion=
FIXStorePath=/root/Jts/connection.xml
IbBindAddress=127.0.0.1
IbBindPort=7496
LogComponents=never
OverrideTradingMode=NeverOverride
PasswordEncryption=base64
PersistentFilePath=/root/Jts
Logpath=/var/log/ibc

EOF
```

**Replace these values:**
- `YOUR_ACCOUNT_USERNAME` - Your IBKR username
- `YOUR_ACCOUNT_PASSWORD` - Your IBKR password

### 2f. Start TWS Gateway as Service

Create systemd service file:

```bash
sudo tee /etc/systemd/system/tws-gateway.service > /dev/null << 'EOF'
[Unit]
Description=Interactive Brokers TWS Gateway
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Jts
ExecStart=/home/ubuntu/ibc/IBCLinux/gateway.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable tws-gateway
sudo systemctl start tws-gateway

# Check status
sudo systemctl status tws-gateway
sudo journalctl -u tws-gateway -f  # View logs
```

---

## Step 3: Verify TWS Gateway is Running

### 3a. Test from EC2

```bash
# On the EC2 instance, test if gateway is listening
netstat -tlnp | grep 7496

# Should see something like:
# tcp  0  0 0.0.0.0:7496  0.0.0.0:*  LISTEN
```

### 3b. Test from Your Local Machine

```powershell
# From your Windows PowerShell
$ec2IP = "54.123.45.67"  # Your EC2 public IP
$port = 7496

# Test TCP connection
Test-NetConnection -ComputerName $ec2IP -Port $port

# Should show: TcpTestSucceeded : True
```

### 3c. Test with Python

```python
from ib_insync import IB

ib = IB()
ib.connect('54.123.45.67', 7496, clientId=1)
print(ib.isConnected())  # Should be True
ib.disconnect()
```

---

## Step 4: Update GitHub Actions Secrets

Now that you have TWS Gateway running on EC2:

1. Go to **GitHub** → Your Repo → **Settings** → **Secrets and variables** → **Actions**

2. Update/Create these secrets:

| Secret | Value |
|--------|-------|
| `IBKR_HOST` | `54.123.45.67` (your EC2 public IP) |
| `IBKR_PORT` | `7496` |
| `AWS_ACCESS_KEY_ID` | Your AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key |
| `AWS_REGION` | `us-east-1` |
| `S3_BUCKET` | `stock-trade-data-2025` |

---

## Step 5: Test GitHub Actions Workflow

1. Go to **GitHub** → Your Repo → **Actions** tab
2. Select **"Daily Super Agent Trading Pipeline"**
3. Click **"Run workflow"** → **"Run workflow"**
4. Monitor logs in real-time

**Expected output:**
```
✓ Python installed
✓ Dependencies installed
✓ Config created
✓ Connected to IBKR at 54.123.45.67:7496
✓ DataAgent: Fetched AAPL, MSFT, TSLA
✓ MLAgent: Training complete
✓ PredictAgent: Predictions generated
✓ Logs uploaded to S3
```

---

## Troubleshooting

### ❌ Connection Refused from GitHub

**Problem:** `Connection refused` when GitHub tries to connect to IBKR

**Solutions:**
1. Check security group allows port 7496
2. Verify TWS Gateway is running: `sudo systemctl status tws-gateway`
3. Check logs: `sudo journalctl -u tws-gateway -f`

### ❌ "Authentication failed"

**Problem:** TWS login fails

**Solution:**
- Verify credentials in `/home/ubuntu/ibc/config/config.ini`
- Check IBKR account is active and has API access enabled
- Go to IBKR website → Account → User Settings → API → Enable

### ❌ Port Already in Use

**Problem:** `Address already in use`

**Solution:**
```bash
# Find process using port 7496
sudo lsof -i :7496

# Kill it
sudo kill -9 <PID>
```

### ❌ High EC2 Costs

**Problem:** Monthly bill is high

**Solutions:**
- Ensure t2.micro instance (free tier)
- Use auto-scaling rules to stop instance if not needed
- Set up cost alerts in AWS

---

## Monitoring & Maintenance

### View Logs

```bash
# SSH to EC2
ssh -i ibkr-tws-gateway.pem ubuntu@YOUR_EC2_IP

# View TWS Gateway logs
sudo journalctl -u tws-gateway -f
```

### Restart TWS Gateway

```bash
sudo systemctl restart tws-gateway
```

### Backup Configuration

```bash
# Download config from EC2 to local
scp -i ibkr-tws-gateway.pem ubuntu@YOUR_EC2_IP:/home/ubuntu/ibc/config/config.ini ./config.ini.backup
```

---

## Cost Estimate

| Component | Cost/Month |
|-----------|-----------|
| EC2 t2.micro | Free (first 12 months) or ~$9 |
| Data transfer | ~$0-5 (depends on usage) |
| EBS storage | Free (first 12 months) or ~$1 |
| **Total** | **Free - $15/month** |

---

## Next Steps

1. ✅ Launch EC2 instance
2. ✅ Install TWS Gateway + IBC
3. ✅ Test connection locally
4. ✅ Update GitHub secrets with EC2 IP
5. ✅ Test GitHub Actions workflow
6. ✅ Delete Windows Task Scheduler job

**Once verified:** Your pipeline runs automatically at 8:00 AM UTC daily, even when your computer is off! 🚀

---

## Quick Reference Commands

```bash
# SSH to EC2
ssh -i ~/ibkr-tws-gateway.pem ubuntu@54.123.45.67

# Check TWS status
sudo systemctl status tws-gateway

# View logs
sudo journalctl -u tws-gateway -f

# Restart
sudo systemctl restart tws-gateway

# Stop
sudo systemctl stop tws-gateway
```

