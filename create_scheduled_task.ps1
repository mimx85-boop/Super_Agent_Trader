# Create Windows Task Scheduler Task for Daily Pipeline
# Run this with Administrator privileges

param(
    [string]$TaskName = "Super Agent Trader Daily Pipeline",
    [string]$TaskFolder = "\Super Agent Trader",
    [int]$Hour = 8,
    [int]$Minute = 0,
    [string]$PowerShellScript = "C:\Users\mimx8\Super_Agent_Trader\run_scheduled_pipeline.ps1",
    [string]$WorkingDir = "C:\Users\mimx8\Super_Agent_Trader"
)

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Windows Task Scheduler Setup" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Task Name: $TaskName"
Write-Host "Folder: $TaskFolder"
Write-Host "Schedule: Daily at $($Hour):$($Minute.ToString('00'))"
Write-Host "Script: $PowerShellScript"
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

Write-Host "Running as Administrator (Check)" -ForegroundColor Green
Write-Host ""

# Check if script exists
if (-not (Test-Path $PowerShellScript)) {
    Write-Host "ERROR: PowerShell script not found: $PowerShellScript" -ForegroundColor Red
    exit 1
}

Write-Host "Script found (Check)" -ForegroundColor Green
Write-Host ""

# Create the task action
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-NoProfile -NoLogo -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$PowerShellScript`"" `
    -WorkingDirectory $WorkingDir

Write-Host "Task action created (Check)" -ForegroundColor Green

# Create the task trigger (daily at specified time)
$trigger = New-ScheduledTaskTrigger `
    -Daily `
    -At "$($Hour):$($Minute.ToString('00'))"

Write-Host "Task trigger created (Check)" -ForegroundColor Green

# Create task settings
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -RunOnlyIfIdle:$false

Write-Host "Task settings created (Check)" -ForegroundColor Green

# Get current user
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name

# Register the task
Write-Host ""
Write-Host "Registering task..."
$task = Register-ScheduledTask `
    -TaskName $TaskName `
    -TaskPath $TaskFolder `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -User $user `
    -RunLevel Highest `
    -Force

if ($task) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "SUCCESS - Task created!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Green
    Write-Host "Task: $TaskName"
    Write-Host "Folder: $TaskFolder"
    Write-Host "Schedule: Daily at $($Hour):$($Minute.ToString('00'))"
    Write-Host ""
    Write-Host "Next run: $($task.Triggers[0].StartBoundary)"
    Write-Host ""
    Write-Host "To manage this task:"
    Write-Host "  1. Open Task Scheduler (taskschd.msc)"
    Write-Host "  2. Navigate to: Task Scheduler Library$TaskFolder"
    Write-Host "  3. Right-click '$TaskName' for options"
    Write-Host ""
}
else {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "ERROR - Failed to create task" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    exit 1
}
