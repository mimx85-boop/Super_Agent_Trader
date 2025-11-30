param(
    [string]$Region = "us-east-1",
    [string]$KeyName = "ibkr-tws-gateway",
    [string]$KeySavePath = "$HOME/ibkr-tws-gateway.pem",
    [string]$SecurityGroupName = "ibkr-tws-gateway",
    [string]$InstanceType = "t2.micro",
    [int]$Port = 7496
)

# Ensure AWS CLI is installed and configured
Write-Host "Checking AWS CLI configuration..."
$awsWho = aws sts get-caller-identity 2>$null
if (-not $awsWho) {
    Write-Error "AWS CLI not configured. Run 'aws configure' first."; exit 1
}

# Find latest Ubuntu 22.04 LTS AMI
Write-Host "Fetching latest Ubuntu 22.04 LTS AMI in $Region..."
$ami = aws ec2 describe-images `
  --region $Region `
  --owners 099720109477 `
  --filters Name=name,Values="ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" `
  --query 'Images | sort_by(@, &CreationDate) | [-1].ImageId' `
  --output text
if (-not $ami) { Write-Error "Could not find Ubuntu AMI"; exit 1 }

# Create or reuse key pair
Write-Host "Ensuring key pair '$KeyName' exists..."
$existingKey = aws ec2 describe-key-pairs --region $Region --key-name $KeyName 2>$null
if (-not $existingKey) {
    Write-Host "Creating key pair..."
    $kp = aws ec2 create-key-pair --region $Region --key-name $KeyName --query 'KeyMaterial' --output text
    Set-Content -Path $KeySavePath -Value $kp
    icacls $KeySavePath /inheritance:r | Out-Null
    icacls $KeySavePath /grant:r "$($env:USERNAME):(R)" | Out-Null
    Write-Host "Key saved to $KeySavePath"
} else {
    Write-Host "Key pair exists; ensure you have the .pem file at $KeySavePath"
}

# Create or reuse security group
Write-Host "Ensuring security group '$SecurityGroupName' exists..."
$sgId = aws ec2 describe-security-groups --region $Region --group-names $SecurityGroupName --query 'SecurityGroups[0].GroupId' --output text 2>$null
if ($LASTEXITCODE -ne 0 -or $sgId -eq $null -or $sgId -eq "None") {
    $sgId = aws ec2 create-security-group --region $Region --group-name $SecurityGroupName --description "Allow TWS Gateway access" --query 'GroupId' --output text
    Write-Host "Created SG: $sgId"
    # Allow TWS port
    aws ec2 authorize-security-group-ingress --region $Region --group-id $sgId --protocol tcp --port $Port --cidr 0.0.0.0/0 | Out-Null
    # Allow SSH from current public IP
    $myIP = (Invoke-RestMethod -Uri "https://checkip.amazonaws.com").Trim()
    aws ec2 authorize-security-group-ingress --region $Region --group-id $sgId --protocol tcp --port 22 --cidr "$myIP/32" | Out-Null
} else {
    Write-Host "SG exists: $sgId"
}

# Launch instance
Write-Host "Launching EC2 instance..."
$userdata = @'
#cloud-config
package_update: true
packages:
  - default-jre
  - wget
runcmd:
  - [ bash, -lc, "mkdir -p /home/ubuntu/tws-gateway" ]
'@

$runOut = aws ec2 run-instances `
  --region $Region `
  --image-id $ami `
  --instance-type $InstanceType `
  --key-name $KeyName `
  --security-group-ids $sgId `
  --user-data $userdata `
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=ibkr-tws-gateway}]' `
  --query 'Instances[0].InstanceId' `
  --output text

Write-Host "Instance ID: $runOut"
Write-Host "Waiting for instance to be running..."
aws ec2 wait instance-running --region $Region --instance-ids $runOut

$pubIP = aws ec2 describe-instances --region $Region --instance-ids $runOut --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
Write-Host "Public IP: $pubIP"

Write-Host "Use SSH to connect:" -ForegroundColor Cyan
Write-Host "ssh -i `"$KeySavePath`" ubuntu@$pubIP"

Write-Host "Next: Run 'ec2/setup_tws.sh' on the EC2 host to install TWS Gateway + IBC."