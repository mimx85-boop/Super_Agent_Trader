# Setup Virtual Environment for Super Agent Trader
# Run this script in PowerShell to create and activate the virtual environment

Write-Host "Creating virtual environment..." -ForegroundColor Green

# Create venv
python -m venv venv

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Green
python -m pip install --upgrade pip setuptools wheel

# Install requirements
Write-Host "Installing requirements..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "`nVirtual environment setup complete!" -ForegroundColor Cyan
Write-Host "To activate in the future, run: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
