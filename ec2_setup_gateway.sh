#!/bin/bash
# EC2 IB Gateway Setup Script
# This script installs IB Gateway on Ubuntu EC2 instance

set -e  # Exit on any error

echo "=========================================="
echo "IB Gateway EC2 Setup Starting"
echo "=========================================="

# Step 1: Update system
echo "[1/5] Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Step 2: Install dependencies
echo "[2/5] Installing Java and X11 packages..."
sudo apt-get install -y default-jre-headless xvfb wget unzip

# Step 3: Download IB Gateway
echo "[3/5] Downloading IB Gateway..."
cd /home/ubuntu
wget -q https://download.interactivebrokers.com/installers/ibgateway/stable-stable/ibgateway-stable-stable.zip
unzip -q ibgateway-stable-stable.zip
rm ibgateway-stable-stable.zip

# Step 4: Create startup script
echo "[4/5] Creating startup script..."
cat > /home/ubuntu/start_gateway.sh << 'SCRIPT'
#!/bin/bash
export DISPLAY=:1
Xvfb :1 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 2
cd /home/ubuntu/ibgateway
./gateway &
sleep 10
echo "IB Gateway started on port 7496"
SCRIPT

chmod +x /home/ubuntu/start_gateway.sh

# Step 5: Start the gateway
echo "[5/5] Starting IB Gateway..."
/home/ubuntu/start_gateway.sh

# Verify gateway is running
sleep 5
if netstat -an | grep -q 7496; then
    echo "=========================================="
    echo "✓ IB Gateway is running on port 7496"
    echo "=========================================="
else
    echo "⚠ Warning: Gateway may not be running yet"
    echo "Try checking with: netstat -an | grep 7496"
fi

echo "Setup complete!"
