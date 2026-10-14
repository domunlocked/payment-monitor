@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"
set "TASK_NAME=PaymentMonitorListener"
if not exist "%PROJECT_DIR%logs" mkdir "%PROJECT_DIR%logs"

if not exist "%PYTHON%" (
    echo The project Python environment is missing.
    echo Run install.bat first.
    pause
    exit /b 1
)
if not exist "%PROJECT_DIR%.env" (
    echo The local .env file is missing. Run install.bat and complete setup first.
    pause
    exit /b 1
)

set "PAYMENT_MONITOR_PROJECT_DIR=%PROJECT_DIR%"
"%PYTHON%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/healthz', timeout=1)" >nul 2>&1
if not errorlevel 1 (
    echo Gracefully stopping the existing service so Task Scheduler can own its process...
    "%PYTHON%" "%PROJECT_DIR%listener.py" --shutdown >nul 2>&1
    if errorlevel 1 (
        echo Existing service does not support graceful shutdown; validating its exact process before replacement...
        powershell -NoProfile -ExecutionPolicy Bypass -Command ^
          "$root = $env:PAYMENT_MONITOR_PROJECT_DIR;" ^
          "$connections = @(Get-NetTCPConnection -LocalAddress '127.0.0.1' -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue);" ^
          "if (-not $connections) { exit 0 };" ^
          "foreach ($connection in $connections) {" ^
          "  $process = Get-CimInstance Win32_Process -Filter ('ProcessId = ' + $connection.OwningProcess);" ^
          "  if (-not $process -or $process.Name -ne 'python.exe' -or $process.CommandLine -notlike ('*' + (Join-Path $root 'listener.py') + '*')) { exit 2 };" ^
          "  Stop-Process -Id $process.ProcessId -ErrorAction Stop;" ^
          "}"
        if errorlevel 1 (
            echo Could not verify the process on 127.0.0.1:8765 belongs to this project.
            echo Startup task was not changed; no unrelated process was stopped.
            pause
            exit /b 1
        )
    )
    for /L %%I in (1,1,20) do (
        "%PYTHON%" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/healthz', timeout=1)" >nul 2>&1
        if errorlevel 1 goto existing_service_stopped
        timeout /t 1 /nobreak >nul
    )
    echo The existing service did not stop in time. Startup task was not changed.
    pause
    exit /b 1
)
:existing_service_stopped

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference = 'Stop';" ^
  "$root = $env:PAYMENT_MONITOR_PROJECT_DIR;" ^
  "$launcher = Join-Path $root 'start_payment_monitor.bat';" ^
  "$command = Join-Path $env:SystemRoot 'System32\cmd.exe';" ^
  "$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name;" ^
  "$argument = '/d /c ' + [char]34 + [char]34 + $launcher + [char]34 + ' --task' + [char]34;" ^
  "$action = New-ScheduledTaskAction -Execute $command -Argument $argument -WorkingDirectory $root;" ^
  "$trigger = New-ScheduledTaskTrigger -AtLogOn -User $identity;" ^
  "$trigger.Delay = 'PT30S';" ^
  "$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -MultipleInstances IgnoreNew -StartWhenAvailable;" ^
  "$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited;" ^
  "Register-ScheduledTask -TaskName 'PaymentMonitorListener' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Starts the local Payment Monitor and Telegram listener after this user signs in.' -Force | Out-Null;" ^
  "Start-ScheduledTask -TaskName 'PaymentMonitorListener';"
if errorlevel 1 (
    echo Could not create or start the current-user PaymentMonitorListener task.
    echo No administrator rights should be needed. Check Task Scheduler permissions.
    >>"%PROJECT_DIR%logs\startup.log" echo [%DATE% %TIME%] Failed to register or start PaymentMonitorListener.
    pause
    exit /b 1
)

echo Startup task installed for the current Windows user.
echo Task name: %TASK_NAME%
echo It runs start_payment_monitor.bat after sign-in with a 30-second delay.
echo Task Scheduler retries failures every minute.
echo The local dashboard will open in your default browser after the API starts.
echo Waiting for the local service to become ready...
for /L %%I in (1,1,90) do (
    "%PYTHON%" -c "import json,urllib.request; r=json.load(urllib.request.urlopen('http://127.0.0.1:8765/healthz', timeout=1)); raise SystemExit(0 if r.get('service')=='payment-monitor' else 1)" >nul 2>&1
    if not errorlevel 1 goto service_ready
    timeout /t 1 /nobreak >nul
)
echo The local service did not respond. Check logs\listener.log and logs\startup.log.
pause
exit /b 1

:service_ready
echo Requesting Telegram start in the existing service. This will not create another listener.
"%PYTHON%" "%PROJECT_DIR%listener.py" --start
if errorlevel 1 (
    echo The scheduled task was installed, but the listener could not be started now.
    echo Check the .env settings and logs\listener.log.
    pause
    exit /b 1
)
echo.
echo Use check_listener.bat to check it, or stop_payment_monitor.bat to stop the service.
pause
exit /b 0
