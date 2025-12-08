# EC2 Gateway Setup - Quick Guide for GitHub Actions

## Overview
This guide sets up IB Gateway on AWS EC2 so GitHub Actions can run your trading pipeline 24/7 in the cloud.

---

## STEP 1: Create EC2 Security Group (5 min)

### 1.1 Go to AWS Console
- Open https://console.aws.amazon.com
- Sign in to your AWS account

### 1.2 Create Security Group
1. Go to **EC2** → **Security Groups** (left sidebar)
2. Click **Create security group**
3. Fill in:
   - **Name:** `ibkr-tws-gateway`
   - **Description:** `Allow TWS Gateway for GitHub Actions`
   - **VPC:** Default VPC

### 1.3 Add Inbound Rules
Click **Add rule** twice and add:

| Rule 1 | Rule 2 |
|--------|--------|
| Type: Custom TCP | Type: SSH |
| Protocol: TCP | Protocol: TCP |
| Port: 7496 | Port: 22 |
| Source: 0.0.0.0/0 | Source: Your IP* |

*Your IP = Go to https://whatismyipaddress.com to find it, then use `YOUR_IP/32`

4. Click **Create security group**

---

## STEP 2: Launch EC2 Instance (5 min)

### 2.1 Start Instance Wizard
1. Go to **EC2** → **Instances**
2. Click **Launch instances**

### 2.2 Configure Instance
1. **Name:** `ibkr-gateway`
2. **AMI:** Ubuntu Server 22.04 LTS (free tier eligible)
3. **Instance type:** t2.micro (free tier)
4. **Key pair:**
   - Click **Create new key pair**
   - Name: `ibkr-gateway`
   - Type: RSA
   - Format: .pem
   - Click **Create key pair** (saves to Downloads)
5. **Network settings:**
   - Security group: Select `ibkr-tws-gateway`
6. **Storage:** Keep default (30 GB)
7. Click **Launch instance**

### 2.3 Wait for Instance
- Go back to **Instances**
- Your instance should be in **Running** state (takes ~1-2 min)
- **Note the Public IPv4 address** (e.g., `54.123.45.67`) - you'll need this!

---

## STEP 3: Connect to EC2 (2 min)

### 3.1 Open PowerShell
```powershell
# Windows: PowerShell

# Set your EC2 IP
$EC2_IP = "YOUR_PUBLIC_IP_HERE"  # Replace with actual IP from Step 2.3

# Set key path
$KEY_PATH = "$env:USERPROFILE\Downloads\ibkr-gateway.pem"

# Connect to EC2
ssh -i $KEY_PATH ubuntu@$EC2_IP
```

### 3.2 First Connection
When prompted "Are you sure you want to continue connecting?", type **yes**

You should now be connected! You'll see a prompt like:
```
ubuntu@ip-172-31-xxx-xxx:~$
```

---

## STEP 4: Install IB Gateway on EC2 (10 min)

### 4.1 Update System
```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 4.2 Install Java
```bash
sudo apt-get install -y default-jre-headless xvfb
```

### 4.3 Download IB Gateway
```bash
cd /home/ubuntu
wget https://download.interactivebrokers.com/installers/ibgateway/stable-stable/ibgateway-stable-stable.zip
unzip ibgateway-stable-stable.zip
```

### 4.4 Install IB Gateway
```bash
cd ibgateway
chmod +x ibgateway
./ibgateway
```

The installer will start. Follow these steps:
1. Accept license agreement
2. Choose installation path: `/home/ubuntu/IBJts` (press Enter for default)
3. Wait for installation to complete

### 4.5 Create Startup Script
```bash
cat > /home/ubuntu/start_gateway.sh << 'EOF'
#!/bin/bash
export DISPLAY=:1
Xvfb :1 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 2
cd /home/ubuntu/IBJts/gateway
./gateway &
sleep 10
EOF

chmod +x /home/ubuntu/start_gateway.sh
```

### 4.6 Start IB Gateway
```bash
/home/ubuntu/start_gateway.sh
```

You should see output indicating the gateway is starting. It will bind to port 7496.

### 4.7 Verify Gateway is Running
```bash
netstat -an | grep 7496
```

You should see something like:
```
tcp        0      0 0.0.0.0:7496            0.0.0.0:*               LISTEN
```

---

## STEP 5: Test Connection from Local Machine (5 min)

### 5.1 Update test_ibkr_connection.py
On your local machine, edit `test_ibkr_connection.py`:

```python
from ib_insync import IB

def test_ibkr_connection(host, port):
    ib = IB()
    try:
        print(f"Connecting to {host}:{port}...")
        ib.connect(host, port, clientId=1)
        print("✓ Connected successfully!")
        ib.disconnect()
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
    
if __name__ == "__main__":
    host = "YOUR_EC2_IP_HERE"  # Replace with EC2 public IP
    port = 7496
    test_ibkr_connection(host, port)
```

### 5.2 Run Test
```powershell
cd c:\Users\mimx8\Super_Agent_Trader
python test_ibkr_connection.py
```

Expected output:
```
Connecting to 54.123.45.67:7496...
✓ Connected successfully!
```

If successful, move to Step 6!

---

## STEP 6: Update GitHub Secrets (2 min)

### 6.1 Go to GitHub
1. Open https://github.com/mimx85-boop/Super_Agent_Trader
2. Click **Settings** (top right)
3. Click **Secrets and variables** → **Actions** (left sidebar)

### 6.2 Update IBKR_HOST Secret
1. Find `IBKR_HOST` in the secrets list
2. Click the edit icon (pencil)
3. Change value from `127.0.0.1` to your EC2 public IP (e.g., `54.123.45.67`)
4. Click **Update secret**

### 6.3 Verify Other Secrets
Make sure these are set:
- `IBKR_PORT` = `7496`
- `AWS_ACCESS_KEY_ID` = Your AWS key
- `AWS_SECRET_ACCESS_KEY` = Your AWS secret
- `AWS_REGION` = `us-east-1`
- `S3_BUCKET` = Your bucket name

---

## STEP 7: Test GitHub Actions (2 min)

### 7.1 Trigger Workflow
1. Go to https://github.com/mimx85-boop/Super_Agent_Trader
2. Click **Actions** (top menu)
3. Click **Daily Super Agent Trading Pipeline**
4. Click **Run workflow** → **Run workflow**

### 7.2 Monitor Execution
- Watch the job run in real-time
- Should see green checkmarks if successful
- Look for "Connected successfully!" in logs

---

## Troubleshooting

### Issue: "Connection refused" or "Connection timeout"
**Solution:**
1. Verify EC2 instance is running: https://console.aws.amazon.com/ec2
2. Check security group has port 7496 open
3. SSH back into EC2 and restart gateway:
   ```bash
   pkill -f gateway
   /home/ubuntu/start_gateway.sh
   ```

### Issue: IB Gateway crashes
**Solution:**
1. SSH into EC2
2. Check logs:
   ```bash
   cd /home/ubuntu/IBJts/gateway
   tail -f logs/gw.log
   ```
3. Restart:
   ```bash
   pkill -f gateway
   /home/ubuntu/start_gateway.sh
   ```

### Issue: GitHub Actions still fails
**Solution:**
1. Check GitHub Actions logs for exact error
2. Verify IBKR_HOST secret is set to EC2 public IP (not 127.0.0.1)
3. Run local test first to isolate the issue

---

## Next Steps

✅ Once working:
- GitHub Actions will run daily at 8:00 AM UTC
- You can manually trigger from Actions tab
- Logs go to S3 for monitoring
- Pipeline runs even if your PC is off

📝 Optional:
- Set up email notifications for failures
- Monitor EC2 costs
- Create CloudWatch alarms

---

## Cost Summary

| Component | Cost |
|-----------|------|
| t2.micro (free tier) | ~$0-10/month |
| Data transfer (minimal) | ~$0-2/month |
| **Total** | **~$0-15/month** |

Free tier covers first 12 months at no cost!

---

Need help? Check the main `EC2_TWS_SETUP.md` or `GITHUB_ACTIONS_SETUP.md` for more details.
