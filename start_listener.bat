@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Dependencies are not installed. Run install.bat first.
    pause
    exit /b 1
)
if not exist ".env" (
    echo The .env file is missing. Run install.bat, then edit .env.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" listener.py
if errorlevel 1 (
    echo.
    echo The listener stopped with an error. Check the message above and logs\listener.log.
    pause
)
