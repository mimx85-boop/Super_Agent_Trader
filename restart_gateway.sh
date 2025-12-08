#!/bin/bash
# Proper IB Gateway startup script with Xvfb

# Kill any existing processes
pkill -f Xvfb
pkill -f IbcGateway
sleep 2

# Start Xvfb (virtual display)
export DISPLAY=:1
Xvfb :1 -screen 0 1280x1024x24 > /tmp/xvfb.log 2>&1 &
sleep 3

# Start IB Gateway
cd /home/ubuntu/ibc
nohup ./gatewaystart.sh > /tmp/gateway-startup.log 2>&1 &

# Wait for startup
sleep 15

# Check if it's running
echo "Checking gateway status..."
ps aux | grep -i java | grep -v grep && echo "Gateway process running"
netstat -tlnp 2>/dev/null | grep -E '7496|4001' && echo "Gateway ports listening"

# Show last 50 lines of log
echo "Recent gateway log:"
tail -50 /tmp/gateway-startup.log
