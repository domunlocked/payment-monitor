@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo The project Python environment is missing.
    if not defined PAYMENT_MONITOR_NO_PAUSE pause
    exit /b 1
)

"%PYTHON%" -c "import json,urllib.request; r=json.load(urllib.request.urlopen('http://127.0.0.1:8765/healthz', timeout=2)); raise SystemExit(0 if r.get('service')=='payment-monitor' else 1)" >nul 2>&1
if errorlevel 1 (
    echo The Payment Monitor API is not running.
    echo The Telegram listener may already be stopped.
    if not defined PAYMENT_MONITOR_NO_PAUSE pause
    exit /b 0
)

"%PYTHON%" "%PROJECT_DIR%listener.py" --shutdown
if errorlevel 1 (
    echo The service did not confirm a graceful shutdown.
    echo No process was force-terminated. Check logs\listener.log and logs\console.log.
    if not defined PAYMENT_MONITOR_NO_PAUSE pause
    exit /b 1
)

for /L %%I in (1,1,30) do (
    "%PYTHON%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/healthz', timeout=1)" >nul 2>&1
    if errorlevel 1 goto stopped
    timeout /t 1 /nobreak >nul
)

echo The shutdown request was accepted, but the API is still responding.
echo Check logs\listener.log before retrying. No process was force-terminated.
if not defined PAYMENT_MONITOR_NO_PAUSE pause
exit /b 1

:stopped
echo Payment Monitor API and Telegram listener stopped gracefully.
echo The scheduled task remains installed and runs again at your next Windows sign-in.
if not defined PAYMENT_MONITOR_NO_PAUSE pause
exit /b 0
