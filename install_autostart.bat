@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "LAUNCHER=%PROJECT_DIR%start_payment_monitor.bat"

if not exist "%LAUNCHER%" (
    echo start_payment_monitor.bat was not found in this project folder.
    pause
    exit /b 1
)

set "PAYMENT_MONITOR_PROJECT_DIR=%PROJECT_DIR%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$root = $env:PAYMENT_MONITOR_PROJECT_DIR; $shortcutPath = Join-Path $env:APPDATA 'Microsoft\Windows\Start Menu\Programs\Startup\Payment Monitor.lnk'; $shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut($shortcutPath); $shortcut.TargetPath = Join-Path $root 'start_payment_monitor.bat'; $shortcut.Arguments = '--autostart'; $shortcut.WorkingDirectory = $root; $shortcut.WindowStyle = 7; $shortcut.Description = 'Start Payment Monitor and Telegram at Windows sign-in'; $shortcut.Save(); if (-not (Test-Path -LiteralPath $shortcutPath)) { exit 1 }"
if errorlevel 1 (
    echo Could not add Payment Monitor to this Windows account's Startup folder.
    pause
    exit /b 1
)
echo Automatic startup is installed for the current Windows account.
echo It runs at sign-in, starts the local API if needed, and opens the dashboard.
echo To remove it later, run remove_autostart.bat.
pause
exit /b 0
