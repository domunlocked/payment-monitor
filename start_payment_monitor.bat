@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"
set "LOCAL_URL=http://127.0.0.1:8765/"

if not exist "%PROJECT_DIR%logs" mkdir "%PROJECT_DIR%logs"

if not exist "%PYTHON%" (
    echo The project Python environment is missing.
    echo Double-click install.bat, wait for it to finish, then try again.
    >>"%PROJECT_DIR%logs\startup.log" echo [%DATE% %TIME%] Python environment is missing.
    if /I "%~1"=="--autostart" exit /b 1
    pause
    exit /b 1
)
if not exist "%PROJECT_DIR%.env" (
    echo The local .env file is missing. Run install.bat and complete the local setup.
    >>"%PROJECT_DIR%logs\startup.log" echo [%DATE% %TIME%] Local .env file is missing.
    if /I "%~1"=="--autostart" exit /b 1
    pause
    exit /b 1
)

"%PYTHON%" -c "from config import get_settings; import sys; sys.exit(0 if get_settings().remote_api_origin else 1)" >nul 2>&1
if errorlevel 1 goto tunnel_checked
powershell -NoProfile -ExecutionPolicy Bypass -Command "$s = Get-Service -Name 'cloudflared' -ErrorAction SilentlyContinue; if (-not $s) { exit 2 }; if ($s.Status -ne 'Running') { try { Start-Service -Name 'cloudflared' -ErrorAction Stop; Start-Sleep -Seconds 2; $s = Get-Service -Name 'cloudflared' } catch { exit 3 } }; if ($s.Status -eq 'Running') { exit 0 }; exit 4" >nul 2>&1
if errorlevel 1 (
    echo Cloudflare Tunnel service is not running. Local monitoring can still start,
    echo but remote phone access will remain offline until the tunnel service is installed and running.
    >>"%PROJECT_DIR%logs\startup.log" echo [%DATE% %TIME%] Cloudflare Tunnel service is unavailable.
)
:tunnel_checked

if /I "%~1"=="--task" (
    "%PYTHON%" -c "import json,urllib.request,sys; r=json.load(urllib.request.urlopen('http://127.0.0.1:8765/healthz',timeout=1)); sys.exit(0 if r.get('service')=='payment-monitor' else 1)" >nul 2>&1
    if not errorlevel 1 goto existing_task_service
    goto scheduled_task
)

"%PYTHON%" -c "import json,urllib.request,sys; r=json.load(urllib.request.urlopen('http://127.0.0.1:8765/healthz',timeout=1)); sys.exit(0 if r.get('service')=='payment-monitor' else 1)" >nul 2>&1
if not errorlevel 1 goto start_listener

start "Payment Monitor local API" /min cmd.exe /d /c ""%PYTHON%" "%PROJECT_DIR%listener.py" --autostart >> "%PROJECT_DIR%logs\console.log" 2>&1"
if errorlevel 1 goto startup_failed

for /L %%I in (1,1,90) do (
    "%PYTHON%" -c "import json,urllib.request,sys; r=json.load(urllib.request.urlopen('http://127.0.0.1:8765/healthz',timeout=1)); sys.exit(0 if r.get('service')=='payment-monitor' else 1)" >nul 2>&1
    if not errorlevel 1 goto start_listener
    timeout /t 1 /nobreak >nul
)

:startup_failed
echo Payment Monitor did not start at http://127.0.0.1:8765/.
echo Check the safe local logs at:
echo   %PROJECT_DIR%logs\listener.log
echo   %PROJECT_DIR%logs\console.log
>>"%PROJECT_DIR%logs\startup.log" echo [%DATE% %TIME%] API startup timed out; see listener.log and console.log.
if /I "%~1"=="--autostart" exit /b 1
pause
exit /b 1

:start_listener
"%PYTHON%" "%PROJECT_DIR%listener.py" --start
if errorlevel 1 (
    echo The dashboard is up, but the listener could not be started. Check logs\listener.log.
    exit /b 1
)

:open_dashboard
if /I "%~1"=="--task" exit /b 0
start "" "%LOCAL_URL%"
exit /b 0

:scheduled_task
cd /d "%PROJECT_DIR%"
echo [%DATE% %TIME%] Starting Payment Monitor under Task Scheduler.>>"%PROJECT_DIR%logs\startup.log"
"%PYTHON%" "%PROJECT_DIR%listener.py" --autostart --open-dashboard >> "%PROJECT_DIR%logs\console.log" 2>&1
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" >>"%PROJECT_DIR%logs\startup.log" echo [%DATE% %TIME%] Payment Monitor exited with code %RESULT%; Task Scheduler will retry.
exit /b %RESULT%

:existing_task_service
"%PYTHON%" "%PROJECT_DIR%listener.py" --start >nul 2>&1
exit /b %ERRORLEVEL%
