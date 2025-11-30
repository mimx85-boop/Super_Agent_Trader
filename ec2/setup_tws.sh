#!/usr/bin/env bash
set -euo pipefail

# Hardened TWS Gateway + IBC setup script.
# Usage: sudo bash ec2/setup_tws.sh

TWS_INSTALLER_URL="https://download2.interactivebrokers.com/installers/tws/latest/tws-latest-linux-x64.sh"
IBC_VER="v997.17g"
IBC_ZIP="IBCLinux-997.17g.zip"
IBC_URL="https://github.com/IbcAlpha/IBC/releases/download/${IBC_VER}/${IBC_ZIP}"
IBC_BASE="/home/ubuntu/ibc"
CONFIG_DIR="${IBC_BASE}/config"
CONFIG_FILE="${CONFIG_DIR}/config.ini"
LOG_DIR="/var/log/ibc"

echo "[1/7] Installing base dependencies..."
apt-get update -y
DEBIAN_FRONTEND=noninteractive apt-get install -y default-jre wget unzip lsof screen

echo "[2/7] Creating directories..."
mkdir -p /home/ubuntu/tws-gateway "$IBC_BASE" "$CONFIG_DIR" "$LOG_DIR"
chmod 755 /home/ubuntu/tws-gateway "$IBC_BASE" "$CONFIG_DIR"

echo "[3/7] Downloading TWS installer..."
cd /home/ubuntu/tws-gateway
if ! wget -q -O tws-install.sh "$TWS_INSTALLER_URL"; then
  echo "WARN: Failed to download TWS from $TWS_INSTALLER_URL" >&2
  echo "Please manually download the Linux offline installer from IBKR and place it at /home/ubuntu/tws-gateway/tws-install.sh" >&2
else
  chmod +x tws-install.sh
  echo "Launching installer inside detached screen session 'tws-install'..."
  screen -dmS tws-install bash -lc "./tws-install.sh" || echo "Screen failed; run manually: sudo bash /home/ubuntu/tws-gateway/tws-install.sh"
fi

echo "[4/7] Downloading IBC ${IBC_VER}..."
cd /home/ubuntu
if ! wget -q "$IBC_URL"; then
  echo "ERROR: Failed to download IBC archive $IBC_URL" >&2
  exit 1
fi
unzip -o "$IBC_ZIP" -d "$IBC_BASE"

echo "[5/7] Creating initial IBC config template..."
cat > "$CONFIG_FILE" <<'EOF'
# IBC Config for TWS Gateway
IbLoginId=CHANGE_ME_USERNAME
IbPassword=CHANGE_ME_BASE64_PASSWORD
TradingMode=live
FIXLoginId=CHANGE_ME_USERNAME
FIXPassword=CHANGE_ME_BASE64_PASSWORD
AllowBlindTrading=no
AcceptNonBrokerageAccountWarning=yes
BindAddress=0.0.0.0
IbBindAddress=0.0.0.0
IbBindPort=7496
ConfirmOrderSubmit=no
OverrideTradingMode=NeverOverride
PasswordEncryption=base64
FIXPasswordEncryption=base64
LogComponents=never
PersistentFilePath=/root/Jts
Logpath=/var/log/ibc
FIXLogPath=/var/log/ibc
FIXConnectionType=duplex
FIXAcceptorPort=7497
EOF
chmod 600 "$CONFIG_FILE"
chown root:root "$CONFIG_FILE"

echo "[6/7] Creating systemd service file..."
cat > /etc/systemd/system/tws-gateway.service <<'EOF'
[Unit]
Description=Interactive Brokers TWS Gateway (IBC Managed)
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/Jts
Environment=IBC_CONFIG=/home/ubuntu/ibc/config/config.ini
ExecStart=/home/ubuntu/ibc/IBCLinux/gateway.sh
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable tws-gateway || true

echo "[7/7] Setup complete.";
echo "Next steps:";
echo "  1. Attach to installer if needed: screen -r tws-install (complete TWS install until /root/Jts exists).";
echo "  2. Base64-encode your IBKR password: echo -n 'PASS' | base64";
echo "  3. Edit $CONFIG_FILE replacing username & base64 password.";
echo "  4. Start gateway: sudo systemctl start tws-gateway";
echo "  5. Tail logs: sudo journalctl -u tws-gateway -f";
echo "  6. Verify port: sudo ss -ltnp | grep 7496";
echo "Do NOT start service before updating credentials."
