# EC2 Gateway Setup - PowerShell Helper
# This script automates SSH connection and IB Gateway installation

param(
    [string]$EC2_IP = "3.235.175.135",
    [string]$KeyPath = "$env:USERPROFILE\Downloads\ibkr-tws-gateway.pem"
)

Write-Host "==========================================" -ForegroundColor Green
Write-Host "EC2 IB Gateway Setup Helper" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "EC2 IP: $EC2_IP"
Write-Host "Key File: $KeyPath"

# Check if key file exists
if (-not (Test-Path $KeyPath)) {
    Write-Host "ERROR: Key file not found at: $KeyPath" -ForegroundColor Red
    Write-Host "Make sure your ibkr-tws-gateway.pem file is in Downloads" -ForegroundColor Yellow
    exit 1
}

Write-Host "`nStep 1: Testing SSH connection..." -ForegroundColor Cyan
ssh -i $KeyPath -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 ubuntu@$EC2_IP "echo Connection successful" 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK - SSH connection successful" -ForegroundColor Green
}
else {
    Write-Host "ERROR - SSH connection failed" -ForegroundColor Red
    Write-Host "Make sure:" -ForegroundColor Yellow
    Write-Host "  1. EC2 instance is running"
    Write-Host "  2. Security group allows SSH (port 22) from your IP"
    Write-Host "  3. Key file has correct permissions"
    exit 1
}

Write-Host "`nStep 2: Uploading setup script..." -ForegroundColor Cyan
scp -i $KeyPath -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null `
    "c:\Users\mimx8\Super_Agent_Trader\ec2_setup_gateway.sh" `
    ubuntu@${EC2_IP}:/home/ubuntu/setup_gateway.sh
Write-Host "OK - Setup script uploaded" -ForegroundColor Green

Write-Host "`nStep 3: Running setup on EC2..." -ForegroundColor Cyan
Write-Host "This will take 2-3 minutes..." -ForegroundColor Yellow
ssh -i $KeyPath -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null `
    ubuntu@$EC2_IP "chmod +x /home/ubuntu/setup_gateway.sh && /home/ubuntu/setup_gateway.sh"

Write-Host "`nStep 4: Verifying IB Gateway..." -ForegroundColor Cyan
ssh -i $KeyPath -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null `
    ubuntu@$EC2_IP "netstat -an | grep 7496"

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "OK - Setup complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test connection locally with: python test_ibkr_connection.py"
Write-Host "  2. Update GitHub secrets with IP: $EC2_IP"
Write-Host "  3. Trigger GitHub Actions workflow"
