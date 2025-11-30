#!/usr/bin/env bash
set -euo pipefail

# This script installs TWS Gateway + IBC headlessly and configures a systemd service.
# Run on EC2: sudo bash ec2/setup_tws.sh

# 1) Install dependencies
apt-get update -y
apt-get install -y default-jre wget unzip lsof

# 2) Create dirs
mkdir -p /home/ubuntu/tws-gateway
mkdir -p /home/ubuntu/ibc/config

# 3) Download TWS Gateway installer (interactive)
cd /home/ubuntu/tws-gateway
wget -O latest-tws.sh https://download2.interactivebrokers.com/downloads/unixmacosx/latest-tws-latest-ubuntu-latest.sh
chmod +x latest-tws.sh

# NOTE: The installer is interactive; if it fails headless, use screen:
apt-get install -y screen
screen -dmS tws-install bash -lc "./latest-tws.sh"
echo "If installer requires interaction, attach via: screen -r tws-install"

# Expect install to /root/Jts (default). Verify:
if [ ! -d "/root/Jts" ]; then
  echo "TWS install directory /root/Jts not found. Complete installer in screen.";
fi

# 4) Download IBC
cd /home/ubuntu
IBC_VER="v997.17g"
wget https://github.com/IbcAlpha/IBC/releases/download/${IBC_VER}/IBCLinux-997.17g.zip
unzip -o IBCLinux-997.17g.zip -d /home/ubuntu/ibc

# 5) Create IBC config (edit credentials later)
cat > /home/ubuntu/ibc/config/config.ini << 'EOF'
# IBC Config for TWS Gateway
IbLoginId=CHANGE_ME_USERNAME
IbPassword=CHANGE_ME_PASSWORD
TradingMode=live
FIXLoginId=CHANGE_ME_USERNAME
FIXPassword=CHANGE_ME_PASSWORD
AcceptIncomingConnectionAccount=
AcceptNonBrokerageAccountWarning=yes
AllowBlindTrading=no
BindAddress=0.0.0.0
ConfirmOrderSubmit=no
FIXAcceptorPort=7497
FIXConnectionType=duplex
FIXLogPath=/var/log/ibc
FIXPasswordEncryption=base64
FIXStorePath=/root/Jts/connection.xml
IbBindAddress=0.0.0.0
IbBindPort=7496
LogComponents=never
OverrideTradingMode=NeverOverride
PasswordEncryption=base64
PersistentFilePath=/root/Jts
Logpath=/var/log/ibc
EOF

# 6) Create systemd service
cat > /etc/systemd/system/tws-gateway.service << 'EOF'
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

systemctl daemon-reload
systemctl enable tws-gateway
# Do not start until credentials updated

echo "Setup complete. Edit /home/ubuntu/ibc/config/config.ini with your IBKR credentials, then run:"
echo "  sudo systemctl start tws-gateway"
echo "Check logs: sudo journalctl -u tws-gateway -f"
