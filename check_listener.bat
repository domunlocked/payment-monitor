@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo The project Python environment is missing. Run install.bat first.
    pause
    exit /b 1
)

"%PYTHON%" "%PROJECT_DIR%listener.py" --status
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo.
    echo If this is the first start, double-click setup_startup.bat or start_payment_monitor.bat.
    echo Check logs\listener.log and logs\console.log for safe error summaries.
)
pause
exit /b %RESULT%
