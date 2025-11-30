param(
    [string]$Region = "us-east-1",
    [string]$Repo = "mimx85-boop/Super_Agent_Trader",
    [string]$InstanceNameTag = "ibkr-tws-gateway",
    [int]$Port = 7496
)

# Ensure AWS CLI and GH CLI are available
Write-Host "Checking AWS CLI..."
$awsOk = aws sts get-caller-identity 2>$null
if (-not $awsOk) { Write-Error "AWS CLI not configured. Run 'aws configure'."; exit 1 }

Write-Host "Checking GitHub CLI (gh)..."
$ghVer = gh --version 2>$null
if (-not $ghVer) {
    Write-Error "GitHub CLI not found. Install via: winget install GitHub.cli"; exit 1
}

# Ensure gh is authenticated
$ghAuth = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Authenticating gh CLI..."
    gh auth login
}

# Find running instance public IP by Name tag
Write-Host "Fetching EC2 public IP for instance tagged '$InstanceNameTag' in $Region..."
$publicIp = aws ec2 describe-instances `
    --region $Region `
    --filters Name=tag:Name, Values=$InstanceNameTag Name=instance-state-name, Values=running `
    --query 'Reservations[].Instances[].PublicIpAddress' `
    --output text

if (-not $publicIp -or $publicIp -eq "None") {
    Write-Error "No running instance with tag Name=$InstanceNameTag found or no public IP."; exit 1
}

Write-Host "EC2 Public IP: $publicIp"

# Update secrets IBKR_HOST and IBKR_PORT
Write-Host "Updating GitHub secrets in $Repo..."
& gh secret set IBKR_HOST -R $Repo -b $publicIp
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to set IBKR_HOST secret."; exit 1 }

& gh secret set IBKR_PORT -R $Repo -b $Port
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to set IBKR_PORT secret."; exit 1 }

Write-Host "Secrets updated successfully."

# Optionally trigger workflow run
$workflowName = "Daily Super Agent Trading Pipeline"
Write-Host "Triggering workflow: $workflowName"
# Try by name; fallback to listing IDs if needed
$runOk = gh workflow run "$workflowName" -R $Repo 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Could not trigger by name. Listing workflows..."
    $wf = gh workflow list -R $Repo --limit 10
    Write-Host $wf
    Write-Host "You can trigger manually from GitHub Actions tab."
}
else {
    Write-Host "Workflow triggered. Check Actions tab for progress.";
}
