@echo off
REM Create Windows Task Scheduler Task for Super Agent Trader
REM Run this as Administrator

setlocal enabledelayedexpansion

echo ==========================================
echo Windows Task Scheduler Setup
echo ==========================================
echo.

REM Check if running as admin
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must run as Administrator!
    echo Please right-click this file and select "Run as Administrator"
    pause
    exit /b 1
)

echo Running as Administrator (Check)
echo.

REM Create the scheduled task
echo Creating scheduled task...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
    $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -NoLogo -WindowStyle Hidden -ExecutionPolicy Bypass -File \"C:\Users\mimx8\Super_Agent_Trader\run_scheduled_pipeline.ps1\"" -WorkingDirectory "C:\Users\mimx8\Super_Agent_Trader"; ^
    $trigger = New-ScheduledTaskTrigger -Daily -At "08:00"; ^
    $settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable; ^
    Register-ScheduledTask -TaskName "Super Agent Trader Daily Pipeline" -TaskPath "\Super Agent Trader" -Action $action -Trigger $trigger -Settings $settings -User "%USERNAME%" -RunLevel Highest -Force | Out-Null; ^
    Write-Host "Task created successfully!"

if %errorLevel% equ 0 (
    echo.
    echo ==========================================
    echo SUCCESS - Task created!
    echo ==========================================
    echo.
    echo To verify:
    echo 1. Press Win+R and type: taskschd.msc
    echo 2. Look for: Task Scheduler Library \ Super Agent Trader
    echo 3. Find task: "Super Agent Trader Daily Pipeline"
    echo.
    echo Scheduled to run daily at 8:00 AM
    echo.
) else (
    echo.
    echo ==========================================
    echo ERROR - Failed to create task
    echo ==========================================
)

pause
