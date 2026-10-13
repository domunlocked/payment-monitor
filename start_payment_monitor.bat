@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"
set "LOCAL_URL=http://127.0.0.1:8765/"
set "LISTENER_ARGS="
if /I "%~1"=="--autostart" set "LISTENER_ARGS=--autostart"

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

"%PYTHON%" -c "import json,urllib.request,sys; r=json.load(urllib.request.urlopen('http://127.0.0.1:8765/healthz',timeout=1)); sys.exit(0 if r.get('service')=='payment-monitor' else 1)" >nul 2>&1
if not errorlevel 1 goto open_dashboard

start "Payment Monitor local API" /min cmd.exe /d /c ""%PYTHON%" "%PROJECT_DIR%listener.py" %LISTENER_ARGS% >> "%PROJECT_DIR%logs\console.log" 2>&1"
if errorlevel 1 goto startup_failed

for /L %%I in (1,1,30) do (
    "%PYTHON%" -c "import json,urllib.request,sys; r=json.load(urllib.request.urlopen('http://127.0.0.1:8765/healthz',timeout=1)); sys.exit(0 if r.get('service')=='payment-monitor' else 1)" >nul 2>&1
    if not errorlevel 1 goto open_dashboard
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

:open_dashboard
start "" "%LOCAL_URL%"
exit /b 0
