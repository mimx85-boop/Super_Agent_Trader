param(
    [string]$Region = "us-east-1",
    [string]$KeyName = "ibkr-tws-gateway",
    [string]$KeySavePath = "$HOME/ibkr-tws-gateway.pem",
    [string]$SecurityGroupName = "ibkr-tws-gateway",
    [string]$InstanceType = "t2.micro",
    [int]$Port = 7496,
    [switch]$SkipFreeTierCheck
)

# Ensure AWS CLI is installed and configured
Write-Host "Checking AWS CLI configuration..."
$awsWho = aws sts get-caller-identity 2>$null
if (-not $awsWho) {
    Write-Error "AWS CLI not configured. Run 'aws configure' first."; exit 1
}

if (-not $SkipFreeTierCheck) {
    $freeTierFlag = aws ec2 describe-instance-types --instance-types $InstanceType --query 'InstanceTypes[0].FreeTierEligible' --output text 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Could not query instance type metadata; proceeding with '$InstanceType'."
    }
    elseif ($freeTierFlag -eq 'false') {
        Write-Warning "Instance type '$InstanceType' not free-tier eligible (account restriction?). To override pass -SkipFreeTierCheck or specify -InstanceType explicitly. Attempting switch to 't3.micro'."
        $InstanceType = 't3.micro'
        $freeTierFlag2 = aws ec2 describe-instance-types --instance-types $InstanceType --query 'InstanceTypes[0].FreeTierEligible' --output text 2>$null
        if ($freeTierFlag2 -eq 'false') { Write-Warning "'t3.micro' also reported not free-tier; using anyway." }
    }
}
else {
    Write-Host "Skipping free-tier eligibility check by request." -ForegroundColor Yellow
}
Write-Host "Using instance type: $InstanceType"

Write-Host "Fetching latest Ubuntu 22.04 LTS AMI in $Region..."
# Correct filter syntax: each filter is a quoted string Name=...,Values=...
$ami = aws ec2 describe-images `
    --region $Region `
    --owners 099720109477 `
    --filters `
    "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" `
    "Name=architecture,Values=x86_64" `
    "Name=root-device-type,Values=ebs" `
    --query 'Images | sort_by(@, &CreationDate)[-1].ImageId' `
    --output text 2>$null

if (-not $ami -or $ami -eq "None") {
    Write-Warning "Primary AMI lookup failed (permissions or filters). Attempting SSM parameter fallback..."
    $ami = aws ssm get-parameters `
        --names "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp3/ami-id" `
        --region $Region `
        --query 'Parameters[0].Value' `
        --output text 2>$null
}

if (-not $ami -or $ami -eq "None") { Write-Error "Could not find Ubuntu AMI"; exit 1 }
Write-Host "Using Ubuntu AMI: $ami"

Write-Host "Ensuring key pair '$KeyName' exists..."
# Normalize path separators for Windows
$normalizedKeyPath = $KeySavePath -replace '/', '\\'
$existingKey = aws ec2 describe-key-pairs --region $Region --key-name $KeyName 2>$null
if (-not $existingKey) {
    Write-Host "Creating key pair..."
    $kp = aws ec2 create-key-pair --region $Region --key-name $KeyName --query 'KeyMaterial' --output text
    Set-Content -Path $normalizedKeyPath -Value $kp
    icacls $normalizedKeyPath /inheritance:r | Out-Null
    icacls $normalizedKeyPath /grant:r "$($env:USERNAME):(R)" | Out-Null
    Write-Host "Key saved to $normalizedKeyPath"
}
else {
    Write-Host "Key pair exists; expecting private key at $normalizedKeyPath"
    if (-not (Test-Path $normalizedKeyPath)) {
        Write-Error "Private key file missing at $normalizedKeyPath. Cannot SSH existing instances using this key. Delete key pair or choose new key name and re-provision."; exit 1
    }
}

# Create or reuse security group
Write-Host "Ensuring security group '$SecurityGroupName' exists..."
$sgId = aws ec2 describe-security-groups --region $Region --group-names $SecurityGroupName --query 'SecurityGroups[0].GroupId' --output text 2>$null
if ($LASTEXITCODE -ne 0 -or $null -eq $sgId -or $sgId -eq "None") {
    $sgId = aws ec2 create-security-group --region $Region --group-name $SecurityGroupName --description "Allow TWS Gateway access" --query 'GroupId' --output text
    Write-Host "Created SG: $sgId"
    # Allow TWS port
    aws ec2 authorize-security-group-ingress --region $Region --group-id $sgId --protocol tcp --port $Port --cidr 0.0.0.0/0 | Out-Null
    # Allow SSH from current public IP
    $myIP = (Invoke-RestMethod -Uri "https://checkip.amazonaws.com").Trim()
    aws ec2 authorize-security-group-ingress --region $Region --group-id $sgId --protocol tcp --port 22 --cidr "$myIP/32" | Out-Null
}
else {
    Write-Host "SG exists: $sgId"
}

# Launch instance
Write-Host "Launching EC2 instance..."
${userdata} = @"
#cloud-config
package_update: true
packages:
 - default-jre
 - wget
runcmd:
 - mkdir -p /home/ubuntu/tws-gateway
"@

# Write user-data to a temporary file to avoid CLI parsing issues
$udFile = [System.IO.Path]::GetTempFileName()
Set-Content -Path $udFile -Value $userdata -NoNewline
Write-Host "User-data temp file: $udFile"

Write-Host "Executing run-instances (debug enabled)..."
$launchRaw = aws ec2 run-instances `
    --region $Region `
    --image-id $ami `
    --instance-type $InstanceType `
    --key-name $KeyName `
    --security-group-ids $sgId `
    --user-data file://$udFile `
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ibkr-tws-gateway}]' `
    --output json

if ($LASTEXITCODE -ne 0) {
    Write-Error "run-instances failed. Raw output:"; Write-Host $launchRaw; exit 1
}

# Parse InstanceId
try {
    $parsed = $launchRaw | ConvertFrom-Json
    $runOut = $parsed.Instances[0].InstanceId
}
catch {
    Write-Error "Could not parse InstanceId from run-instances output."; Write-Host $launchRaw; exit 1
}

if (-not $runOut) { Write-Error "Instance launch failed (InstanceId missing)."; Write-Host $launchRaw; exit 1 }

Write-Host "Instance ID: $runOut"
Write-Host "Waiting for instance to be running..."
aws ec2 wait instance-running --region $Region --instance-ids $runOut

$pubIP = aws ec2 describe-instances --region $Region --instance-ids $runOut --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
Write-Host "Public IP: $pubIP"

Write-Host "Use SSH to connect:" -ForegroundColor Cyan
Write-Host "ssh -i `"$normalizedKeyPath`" ubuntu@$pubIP"

Write-Host "Next: Run 'ec2/setup_tws.sh' on the EC2 host to install TWS Gateway + IBC."