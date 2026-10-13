@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo The project Python environment is missing. Run install.bat first.
    pause
    exit /b 1
)
if not exist ".env" (
    echo The local .env file is missing. Run install.bat, then configure .env.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" listener.py
if errorlevel 1 (
    echo.
    echo Payment Monitor stopped with an error. Review logs\listener.log.
    pause
)
