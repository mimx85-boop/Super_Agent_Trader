# Windows Task Scheduler Setup for Daily Trading Pipeline
# Run this in PowerShell as Administrator to schedule daily execution

$taskName = "SuperAgentTrader_DailyPipeline"
$taskPath = "\SuperAgentTrader\"
$scriptPath = "C:\Users\mimx8\Super_Agent_Trader\run_daily_pipeline.py"
$pythonExe = "C:\Users\mimx8\Super_Agent_Trader\venv\Scripts\python.exe"
$workDir = "C:\Users\mimx8\Super_Agent_Trader"

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator" -ForegroundColor Red
    exit 1
}

# Create task trigger for 8:00 AM daily
$trigger = New-ScheduledTaskTrigger -Daily -At "08:00AM"

# Create task action - run Python script
$action = New-ScheduledTaskAction `
    -Execute $pythonExe `
    -Argument $scriptPath `
    -WorkingDirectory $workDir

# Create task settings (run even if logged off, stop after 1 hour, etc.)
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Register the task
try {
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "Removed existing task: $taskName" -ForegroundColor Yellow
    }
    
    Register-ScheduledTask `
        -TaskName $taskName `
        -TaskPath $taskPath `
        -Trigger $trigger `
        -Action $action `
        -Settings $settings `
        -RunLevel Highest `
        -Force `
        -ErrorAction Stop
    
    Write-Host "✓ Task scheduled successfully!" -ForegroundColor Green
    Write-Host "  Task Name: $taskName" -ForegroundColor Cyan
    Write-Host "  Schedule: Daily at 08:00 AM" -ForegroundColor Cyan
    Write-Host "  Script: $scriptPath" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To modify the schedule, use:" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName '$taskName' | Set-ScheduledTask -Trigger (New-ScheduledTaskTrigger -Daily -At '09:00AM')"
    Write-Host ""
    Write-Host "To view task status:" -ForegroundColor Yellow
    Write-Host "  Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo"
    Write-Host ""
    Write-Host "To view task execution history:" -ForegroundColor Yellow
    Write-Host "  Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-TaskScheduler/Operational'; Data='$taskName'} -MaxEvents 10"
}
catch {
    Write-Host "ERROR: Failed to create scheduled task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
