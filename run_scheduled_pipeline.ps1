# Daily Pipeline Runner for Windows Task Scheduler
# This script runs the Super Agent Trader pipeline daily

param(
    [string]$PipelineScript = "C:\Users\mimx8\Super_Agent_Trader\run_daily_pipeline.py",
    [string]$LogDir = "C:\Users\mimx8\Super_Agent_Trader\logs\scheduled_runs"
)

# Ensure log directory exists
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

# Create timestamp
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $LogDir "scheduled_run_$timestamp.log"

# Start logging
Start-Transcript -Path $logFile -Append

Write-Host "=========================================="
Write-Host "Super Agent Trader - Scheduled Run"
Write-Host "=========================================="
Write-Host "Started: $(Get-Date)"
Write-Host "Pipeline Script: $PipelineScript"
Write-Host "Log File: $logFile"
Write-Host ""

try {
    # Check if pipeline script exists
    if (-not (Test-Path $PipelineScript)) {
        throw "Pipeline script not found: $PipelineScript"
    }
    
    Write-Host "Running pipeline..." -ForegroundColor Cyan
    
    # Run the pipeline
    python $PipelineScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "" -ForegroundColor Green
        Write-Host "=========================================="
        Write-Host "SUCCESS - Pipeline completed successfully"
        Write-Host "=========================================" -ForegroundColor Green
    }
    else {
        Write-Host "" -ForegroundColor Red
        Write-Host "=========================================="
        Write-Host "WARNING - Pipeline exited with code: $LASTEXITCODE"
        Write-Host "=========================================" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "" -ForegroundColor Red
    Write-Host "=========================================="
    Write-Host "ERROR - Pipeline execution failed"
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "Error: $_"
}

Write-Host ""
Write-Host "Completed: $(Get-Date)"
Write-Host ""

# Stop logging
Stop-Transcript

# Show last few lines of log
Write-Host "Log saved to: $logFile"
