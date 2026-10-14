@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
    echo The project Python environment is missing. Run install.bat first.
    pause
    exit /b 1
)

"%PYTHON%" "%PROJECT_DIR%listener.py" --stop
set "RESULT=%ERRORLEVEL%"
if not "%RESULT%"=="0" (
    echo.
    echo The local service could not confirm a graceful listener stop.
    echo If the dashboard service is already closed, there is no listener to stop.
    pause
    exit /b %RESULT%
)
echo The Telegram listener is stopped. The dashboard and scheduled task stay available.
echo To start Telegram again, use the local dashboard Start Listening button
echo or run setup_startup.bat.
pause
exit /b 0
